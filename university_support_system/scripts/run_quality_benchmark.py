"""Reranker Kalite Benchmark Scripti.

ms-marco-MiniLM-L-6-v2 reranker'inin zaman kazancinin kalite kaybina
yol acip acmadigini olcmek icin tasarlanmis 25 soruluk LLM-sentez-odakli
benchmark seti.

Kullanim:
  cd university_support_system
  python scripts/run_quality_benchmark.py                          # Tum sorular
  python scripts/run_quality_benchmark.py --category A             # Tek kategori
  python scripts/run_quality_benchmark.py --question Q5             # Tek soru
  python scripts/run_quality_benchmark.py --question Q8 Q13 Q16    # Birden fazla soru
  python scripts/run_quality_benchmark.py --cold-start             # Cold-start (model yeniden yukle)
  python scripts/run_quality_benchmark.py --use-api                # API uzerinden
  python scripts/run_quality_benchmark.py --use-api --api-base-url http://localhost:8000
  python scripts/run_quality_benchmark.py -v                       # Verbose mod
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from statistics import mean, median

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from src.core.console import configure_utf8_stdio

configure_utf8_stdio()

_verbose_argv = any(a in ("-v", "--verbose") for a in sys.argv)
os.environ["SERVER_DEBUG"] = "true" if _verbose_argv else "false"

from src.db.conversation_context import ConversationContextService
from src.db.connection import init_engine
from src.evaluation.key_fact_matching import check_key_facts
from src.orchestrators.main import MainOrchestrator
from src.core.profiling import QueryProfiler, activate_profiler
from src.api.main import app as api_app
from src.orchestrators.response_utils import (
    LOW_CONFIDENCE_RERANKER_SCORE_THRESHOLD,
    LOW_CONFIDENCE_RETRIEVAL_SCORE_THRESHOLD,
)
from httpx import ASGITransport, AsyncClient

BENCHMARK_FILE = Path(__file__).resolve().with_name("reranker_quality_benchmark.json")
REPORT_DIR = _ROOT / "docs" / "archive" / "benchmarks"
RESULTS_DIR = _ROOT / "tests" / "archive" / "benchmarks"
DEFAULT_BENCHMARK_PROFILE = {
    "full_name": "Benchmark Ogrenci",
    "student_number": "22000001",
    "student_department": "Bilgisayar Muhendisligi",
    "student_faculty": "Muhendislik Fakultesi",
    "student_type": "Turk ogrenci",
}

BOLD = "\033[1m"
DIM = "\033[2m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
RESET = "\033[0m"
SEP = "\u2500" * 70

_SUSPICIOUS_QUALITY_PATTERNS = (
    "bilmedigim icin", "bilemedigim icin", "genellikle",
    "genel olarak bilinen", "genel bilgiler verilebilir",
    "genel bilgi birikimime", "genel bilgi birikimimden",
    "tahminim", "tahminimce", "tahminen",
    "internette arastirdiginizda", "genelde boyle bilinir",
)
_FOREIGN_LANGUAGE_PATTERNS = (
    "however", "therefore", "furthermore", "moreover",
    "please note", "in addition", "regarding",
)
_ROLE_RECITATION_PATTERNS = (
    "harc ve odeme uzmani olarak", "kayit uzmani olarak",
    "mevzuat uzmani olarak", "uzman asistan olarak",
)
_A2A_TRANSPORT_FALLBACK_PATTERNS = (
    "agent servisi zamaninda yanit veremedi",
    "agent servisine su anda ulasilamadi",
    "agent servisi gecici olarak korumaya alindi",
    "a2a circuit breaker aktif",
)
_LLM_ROLE_PRIORITY = {
    "routing": 0,
    "conversation": 1,
    "final_refinement": 2,
    "specialist_synthesis": 2,
    "global_synthesis": 3,
    "default": 4,
}

_SMOKE_WARMUP_QUERIES: tuple[str, ...] = (
    "Test sorgusu",
)

_FULL_WARMUP_QUERIES: tuple[str, ...] = (
    "Yatay gecis sonrasi muafiyet basvurusu ne zaman yapilir ve karar cikana kadar derslere devam gerekir mi?",
    "Kayit yenilemede harc odendikten sonra ders kaydi ve danisman onayi nasil ilerler?",
    "Pedagojik formasyon dersleri transkripte ve mezuniyet ortalamasina nasil yansir?",
    "Uluslararasi ogrenci kaydinda ogrenim ucreti ve ikamet izni belgeleri nelerdir?",
    "Sinav notuna itiraz suresi, dilekce ve bolum baskanligi sureci nasildir?",
    "Ders notu sisteme girilmediyse danisman, bolum baskanligi ve oidb kanali nasil izlenir?",
    "Mezuniyet icin ders, staj, ilisik kesme ve diploma sureci nasil tamamlanir?",
    "Sinavda kopya cekilirse disiplin sureci ve resmi dayanak nasil isler?",
    "Burslu ogrenci yatay gecis yaparsa burs ve harc durumu nasil etkilenir?",
    "Kismi zamanli calisma ve yemek bursu basvuru sartlari nelerdir?",
)

_FULL_API_WARMUP_QUERIES: tuple[str, ...] = (
    "Bagil degerlendirme sistemi ile mutlak degerlendirme arasindaki fark nedir ve hangi ogrenci sayisinda hangisi uygulanir?",
    "Muafiyet ve intibak basvurusu hangi belgelerle ve hangi surede yapilir?",
    "Kayit yenilemede harc odendikten sonra ders kaydi ve danisman onayi nasil ilerler?",
    "Sinav notuna itiraz suresi, dilekce ve bolum baskanligi sureci nasildir?",
    "Uluslararasi ogrenci kaydinda ogrenim ucreti ve ikamet izni belgeleri nelerdir?",
    "Universiteden ayrilmak istiyorum; ilisik kesme sureci ve form teslimi nasil ilerler?",
)

_WARMUP_MODE_ALIASES = {
    "off": "off",
    "none": "off",
    "smoke": "smoke",
    "full": "full",
    "selected": "selected",
}


def _configure_logging(*, verbose: bool) -> None:
    if verbose:
        logging.basicConfig(level=logging.DEBUG, force=True)
        logging.getLogger("sqlalchemy").setLevel(logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING, force=True)
        logging.getLogger("sqlalchemy").setLevel(logging.ERROR)
        try:
            import structlog
            structlog.configure(
                wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
            )
        except Exception:
            pass


def _load_benchmark() -> dict:
    if not BENCHMARK_FILE.exists():
        raise FileNotFoundError(f"Benchmark dosyasi bulunamadi: {BENCHMARK_FILE}")
    return json.loads(BENCHMARK_FILE.read_text(encoding="utf-8"))


def _extract_generation_mode(answer: str, generation_modes: list[str] | None = None) -> str:
    """Yapisal generation mode varsa onu, yoksa cevap metnini kullanir."""
    if generation_modes:
        lowered_modes = " ".join(generation_modes).lower()
        for token in ("llm", "vt", "rag", "kural"):
            if token in lowered_modes:
                return token

    match = re.search(r"Uretim Turu:\s*\n(.*?)(?:\n\n|$)", answer, re.DOTALL)
    if not match:
        return "unknown"
    block = match.group(1).strip().lower()
    modes = set()
    for token in ("vt", "rag", "llm", "kural"):
        if token in block:
            modes.add(token)
    if not modes:
        return "unknown"
    priority = ["llm", "vt", "rag", "kural"]
    for m in priority:
        if m in modes:
            return m
    return "unknown"


def _extract_departments(answer: str, response_depts: list[str]) -> list[str]:
    """Yanit metninden veya response'dan departman listesini cikarir."""
    if response_depts:
        return response_depts
    return []


def _source_metadata(source) -> dict:
    if isinstance(source, dict):
        return dict(source.get("metadata") or {})
    return dict(getattr(source, "metadata", {}) or {})


def _source_score(source) -> float:
    if isinstance(source, dict):
        return float(source.get("score", 0.0) or 0.0)
    return float(getattr(source, "score", 0.0) or 0.0)


def _source_low_confidence_threshold(source) -> float:
    metadata = _source_metadata(source)
    score_type = str(metadata.get("score_type", "retrieval")).strip().lower()
    if score_type == "reranker":
        return LOW_CONFIDENCE_RERANKER_SCORE_THRESHOLD
    return LOW_CONFIDENCE_RETRIEVAL_SCORE_THRESHOLD


def _all_sources_low_confidence(sources: list) -> bool:
    if not sources:
        return False
    try:
        return all(
            _source_score(source) < _source_low_confidence_threshold(source)
            for source in sources
        )
    except Exception:
        return False


def _quality_warnings(answer: str, *, sources: list | None = None) -> list[str]:
    warnings: list[str] = []
    lowered = answer.casefold()
    if any(p in lowered for p in _SUSPICIOUS_QUALITY_PATTERNS):
        warnings.append("uydurma_riski")
    if any(p in lowered for p in _FOREIGN_LANGUAGE_PATTERNS):
        warnings.append("yabanci_dil")
    if any(p in lowered for p in _ROLE_RECITATION_PATTERNS):
        warnings.append("rol_tekrari")
    if any(p in lowered for p in _A2A_TRANSPORT_FALLBACK_PATTERNS):
        warnings.append("a2a_transport_fallback")
    if _all_sources_low_confidence(sources or []):
        warnings.append("zayif_kaynak_destegi")
    if len(answer.strip()) < 30:
        warnings.append("cok_kisa_yanit")
    return warnings


def _response_diagnostics_payload(response) -> dict[str, Any]:
    diagnostics = getattr(response, "diagnostics", None)
    if diagnostics is None:
        return {}
    if hasattr(diagnostics, "model_dump"):
        payload = diagnostics.model_dump()
        return payload if isinstance(payload, dict) else {}
    if isinstance(diagnostics, dict):
        return diagnostics
    return {}


def _extract_llm_usage_from_response(response) -> list[dict[str, Any]]:
    diagnostics = _response_diagnostics_payload(response)
    llm_usage = diagnostics.get("llm_usage") or []
    if not isinstance(llm_usage, list):
        return []
    return [dict(item) for item in llm_usage if isinstance(item, dict)]


def _extract_remote_profiles_from_response(response) -> list[dict[str, Any]]:
    diagnostics = _response_diagnostics_payload(response)
    remote_profiles = diagnostics.get("remote_profiles") or []
    if not isinstance(remote_profiles, list):
        return []
    return [dict(item) for item in remote_profiles if isinstance(item, dict)]


def _extract_local_profile_from_response(response) -> dict[str, Any] | None:
    diagnostics = _response_diagnostics_payload(response)
    local_profile = diagnostics.get("local_profile")
    return dict(local_profile) if isinstance(local_profile, dict) else None


def _extract_routing_attributes(
    profile_snapshot: dict[str, Any],
    local_profile: dict[str, Any] | None,
) -> dict[str, Any]:
    """Use API-side routing diagnostics when the benchmark calls an external API."""
    local_attrs = (local_profile or {}).get("attributes") or {}
    local_routing = local_attrs.get("routing")
    if isinstance(local_routing, dict):
        return local_routing

    snapshot_routing = profile_snapshot.get("attributes", {}).get("routing", {})
    return snapshot_routing if isinstance(snapshot_routing, dict) else {}


def _extract_llm_usage_from_profile(profile_snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    attributes = profile_snapshot.get("attributes") or {}
    llm_usage = attributes.get("llm_usage") or []
    if not isinstance(llm_usage, list):
        return []
    return [dict(item) for item in llm_usage if isinstance(item, dict)]


def _format_llm_usage_label(entry: dict[str, Any]) -> str:
    provider = (
        str(entry.get("provider_label") or "").strip()
        or str(entry.get("display_name") or "").strip()
        or str(entry.get("provider") or "").strip()
    )
    model = str(entry.get("model") or "").strip()
    if not provider:
        return ""
    label = f"{provider}/{model}" if model else provider
    path = str(entry.get("path") or "").strip()
    if path and path != "primary":
        label = f"{label} [{path}]"
    return label


def _summarize_llm_usage(llm_usage: list[dict[str, Any]]) -> dict[str, list[str]]:
    successful = [entry for entry in llm_usage if str(entry.get("status")) == "success"]
    candidates = successful or llm_usage
    grouped: dict[str, list[str]] = {}
    for entry in candidates:
        role = str(entry.get("model_role") or "default").strip() or "default"
        label = _format_llm_usage_label(entry)
        if not label:
            continue
        grouped.setdefault(role, [])
        if label not in grouped[role]:
            grouped[role].append(label)
    ordered_roles = sorted(grouped, key=lambda role: (_LLM_ROLE_PRIORITY.get(role, 999), role))
    return {role: grouped[role] for role in ordered_roles}


def _format_llm_usage_summary(summary: dict[str, list[str]]) -> str:
    if not summary:
        return ""
    parts = []
    for role, labels in summary.items():
        if not labels:
            continue
        parts.append(f"{role}={', '.join(labels)}")
    return "; ".join(parts)


def _format_remote_profile_summary(remote_profiles: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for item in remote_profiles:
        agent_id = str(item.get("agent_id") or "?")
        profile = item.get("profile") or {}
        if not isinstance(profile, dict):
            continue
        total_ms = profile.get("total_ms")
        try:
            total_label = f"{float(total_ms):.0f}ms"
        except Exception:
            total_label = "?ms"
        parts.append(f"{agent_id}={total_label}")
    return "; ".join(parts)


def _event_duration(profile: dict[str, Any], name: str) -> float | None:
    candidates = [
        event
        for event in profile.get("events", []) or []
        if isinstance(event, dict) and event.get("name") == name
    ]
    if not candidates:
        return None
    try:
        return max(float(event.get("duration_ms") or 0.0) for event in candidates)
    except Exception:
        return None


def _format_local_profile_summary(profile: dict[str, Any] | None) -> str:
    if not profile:
        return ""
    parts: list[str] = []
    try:
        parts.append(f"api_total={float(profile.get('total_ms') or 0.0):.0f}ms")
    except Exception:
        pass
    for name, label in (
        ("main.dispatch_departments", "dispatch"),
        ("main.final_llm_synthesis", "final_llm"),
        ("main.global_llm_synthesis", "global_llm"),
        ("main.compose_response", "compose"),
        ("main.telemetry.finalize_success", "telemetry"),
    ):
        duration = _event_duration(profile, name)
        if duration is not None:
            parts.append(f"{label}={duration:.0f}ms")
    return "; ".join(parts)


def _dept_match(actual: list[str], expected: list[str]) -> bool:
    return set(expected) <= set(actual)


def _generation_mode_match(actual: str, expected: str) -> bool:
    if expected == "kural":
        return actual == "kural"
    if expected == "llm":
        return actual in ("llm",)
    return actual == expected


def _create_api_client(
    api_base_url: str | None = None,
    *,
    timeout_seconds: float = 120.0,
) -> AsyncClient:
    if api_base_url:
        return AsyncClient(base_url=api_base_url.rstrip("/"), timeout=timeout_seconds)
    transport = ASGITransport(app=api_app)
    return AsyncClient(transport=transport, base_url="http://testserver", timeout=timeout_seconds)


async def _verify_api_ready(api_client: AsyncClient) -> dict:
    """Fail fast before producing a misleading all-error benchmark report."""
    response = await api_client.get("/health")
    response.raise_for_status()
    body = response.json()
    if str(body.get("status") or "").lower() not in {"healthy", "ok"}:
        raise RuntimeError(f"API health status uygun degil: {body.get('status')}")
    return body


async def _fetch_a2a_diagnostics(api_client: AsyncClient) -> dict | None:
    """Best-effort diagnostics snapshot for API-backed benchmark runs."""
    try:
        response = await api_client.get("/a2a/diagnostics")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        body = response.json()
        if isinstance(body, dict):
            return body
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}
    return None


def _overview_counts(diagnostics: dict | None) -> dict[str, int]:
    overview = (diagnostics or {}).get("overview") or {}
    keys = (
        "query_count",
        "query_failure_count",
        "agent_task_count",
        "agent_task_failure_count",
    )
    counts: dict[str, int] = {}
    for key in keys:
        try:
            counts[key] = int(overview.get(key) or 0)
        except Exception:
            counts[key] = 0
    return counts


def _diagnostics_delta(before: dict | None, after: dict | None) -> dict | None:
    if not after:
        return None
    if after.get("error"):
        return {"error": after.get("error")}

    before_counts = _overview_counts(before)
    after_counts = _overview_counts(after)
    overview_delta = {
        key: max(after_counts.get(key, 0) - before_counts.get(key, 0), 0)
        for key in after_counts
    }

    before_agents = {
        str(agent.get("agent_id")): agent
        for agent in (before or {}).get("agents", []) or []
        if agent.get("agent_id")
    }
    agent_deltas = []
    for agent in (after.get("agents") or []):
        agent_id = str(agent.get("agent_id") or "")
        if not agent_id:
            continue
        previous = before_agents.get(agent_id, {})
        task_delta = max(
            int(agent.get("total_tasks") or 0) - int(previous.get("total_tasks") or 0),
            0,
        )
        failed_delta = max(
            int(agent.get("failed_tasks") or 0) - int(previous.get("failed_tasks") or 0),
            0,
        )
        if task_delta or failed_delta:
            agent_deltas.append(
                {
                    "agent_id": agent_id,
                    "department": agent.get("department"),
                    "role": agent.get("role"),
                    "task_delta": task_delta,
                    "failed_delta": failed_delta,
                    "last_error": agent.get("last_error"),
                    "avg_latency_ms": agent.get("avg_latency_ms"),
                    "max_latency_ms": agent.get("max_latency_ms"),
                }
            )

    before_failure_ids = {
        str(item.get("task_id"))
        for item in (before or {}).get("recent_failures", []) or []
        if item.get("task_id")
    }
    new_recent_failures = [
        item
        for item in (after.get("recent_failures") or [])
        if str(item.get("task_id")) not in before_failure_ids
    ][:10]

    return {
        "overview_before": before_counts,
        "overview_after": after_counts,
        "overview_delta": overview_delta,
        "agent_deltas": agent_deltas,
        "new_recent_failures": new_recent_failures,
    }


def _profile_from_args(args: argparse.Namespace) -> dict[str, str]:
    """Return benchmark profile metadata used to avoid onboarding short-circuit."""
    return {
        "full_name": args.full_name or DEFAULT_BENCHMARK_PROFILE["full_name"],
        "student_number": args.student_number or DEFAULT_BENCHMARK_PROFILE["student_number"],
        "student_department": args.student_department or DEFAULT_BENCHMARK_PROFILE["student_department"],
        "student_faculty": args.student_faculty or DEFAULT_BENCHMARK_PROFILE["student_faculty"],
        "student_type": args.student_type or DEFAULT_BENCHMARK_PROFILE["student_type"],
    }


def _strip_benchmark_name_prefix(answer: str, profile: dict[str, str] | None) -> str:
    """Remove synthetic benchmark personalization without changing API behavior."""
    full_name = str((profile or {}).get("full_name") or "").strip()
    if not full_name:
        return answer
    first_name = (full_name.split() or [full_name])[0].strip()
    if not first_name:
        return answer
    prefix = f"{first_name}, "
    if answer.startswith(prefix):
        return answer[len(prefix):]
    return answer


async def run_single_question(
    orchestrator: MainOrchestrator,
    q: dict,
    *,
    api_client: AsyncClient | None = None,
    llm_profile: str | None = None,
    profile: dict[str, str] | None = None,
    disable_cache: bool = True,
) -> dict:
    qid = q["id"]
    question = q["question"]
    expected_depts = q["expected_departments"]
    expected_mode = q["expected_generation_mode"]
    expected_facts = q.get("expected_key_facts", [])
    category = q["category"]
    difficulty = q.get("difficulty", "medium")

    context_id = f"qbench-{qid}-{datetime.now().strftime('%H%M%S')}"

    print(f"\n  {CYAN}[{qid}]{RESET} {question}")
    print(f"  Kategori: {category} | Zorluk: {difficulty}")

    start = time.perf_counter()
    profiler = QueryProfiler(label=f"qbench_{qid}")
    profile_payload = dict(DEFAULT_BENCHMARK_PROFILE)
    profile_payload.update({key: value for key, value in (profile or {}).items() if value})
    try:
        with activate_profiler(profiler):
            if api_client is None:
                response = await orchestrator.handle_query(
                    question,
                    context_id=context_id,
                    llm_profile=llm_profile,
                    is_authenticated=False,
                    student_id=None,
                    student_number=profile_payload.get("student_number"),
                    student_full_name=profile_payload.get("full_name"),
                    student_department=profile_payload.get("student_department"),
                    student_faculty=profile_payload.get("student_faculty"),
                    student_type=profile_payload.get("student_type"),
                    disable_cache=disable_cache,
                )
            else:
                api_response = await api_client.post(
                    "/query",
                    json={
                        "query": question,
                        "context_id": context_id,
                        "llm_profile": llm_profile,
                        "disable_cache": disable_cache,
                        **profile_payload,
                    },
                )
                api_response.raise_for_status()
                body = api_response.json()
                from types import SimpleNamespace
                response = SimpleNamespace(
                    answer=body.get("answer", ""),
                    departments_involved=body.get("departments_involved", []),
                    generation_modes=body.get("generation_modes", []),
                    sources=body.get("sources", []),
                    response_time_ms=body.get("response_time_ms", 0.0),
                    query_id=body.get("query_id", context_id),
                    diagnostics=body.get("diagnostics"),
                )

        elapsed_ms = round((time.perf_counter() - start) * 1000, 1)
        profile_snapshot = profiler.snapshot()

        answer_text = _strip_benchmark_name_prefix(response.answer, profile_payload)
        actual_depts = list(response.departments_involved)
        actual_mode = _extract_generation_mode(
            answer_text,
            getattr(response, "generation_modes", []),
        )
        fact_check = check_key_facts(answer_text, expected_facts)
        facts_found = sum(1 for v in fact_check.values() if v)
        facts_total = len(expected_facts)
        warnings = _quality_warnings(answer_text, sources=list(response.sources))
        llm_usage = _extract_llm_usage_from_response(response)
        if not llm_usage:
            llm_usage = _extract_llm_usage_from_profile(profile_snapshot)
        llm_usage_summary = _summarize_llm_usage(llm_usage)
        llm_usage_line = _format_llm_usage_summary(llm_usage_summary)
        remote_profiles = _extract_remote_profiles_from_response(response)
        remote_profile_line = _format_remote_profile_summary(remote_profiles)
        local_profile = _extract_local_profile_from_response(response)
        local_profile_line = _format_local_profile_summary(local_profile)
        reported_response_time_ms = float(getattr(response, "response_time_ms", 0.0) or 0.0)

        dept_ok = _dept_match(actual_depts, expected_depts)
        mode_ok = _generation_mode_match(actual_mode, expected_mode)

        routing_attrs = _extract_routing_attributes(profile_snapshot, local_profile)
        intent_data = routing_attrs.get("intent")

        dept_color = GREEN if dept_ok else RED
        mode_color = GREEN if mode_ok else RED
        facts_color = GREEN if facts_found == facts_total else (YELLOW if facts_found > 0 else RED)
        warn_color = GREEN if not warnings else MAGENTA

        print(f"  {BOLD}Departman:{RESET}  {dept_color}{actual_depts}{RESET}  (beklenen: {expected_depts})  {'OK' if dept_ok else 'YANLIS'}")
        print(f"  {BOLD}Uretim:{RESET}     {mode_color}{actual_mode}{RESET}  (beklenen: {expected_mode})  {'OK' if mode_ok else 'YANLIS'}")
        if intent_data:
            print(
                f"  {BOLD}Intent:{RESET}     "
                f"complexity={intent_data.get('complexity', '?')} "
                f"force_llm={intent_data.get('force_llm_synthesis', '?')} "
                f"is_personal={intent_data.get('is_personal', '?')} "
                f"query_type={intent_data.get('query_type', '?')}"
            )
        if llm_usage_line:
            print(f"  {BOLD}LLM:{RESET}        {llm_usage_line}")
        if remote_profile_line:
            print(f"  {BOLD}Ajan Sure:{RESET}  {remote_profile_line}")
        if local_profile_line:
            print(f"  {BOLD}API Sure:{RESET}   {local_profile_line}")
        print(f"  {BOLD}Key Facts:{RESET}  {facts_color}{facts_found}/{facts_total}{RESET}")
        if expected_facts:
            for fact, found in fact_check.items():
                mark = f"{GREEN}+{RESET}" if found else f"{RED}-{RESET}"
                print(f"    {mark} {fact}")
        print(f"  {BOLD}Sure:{RESET}       {elapsed_ms} ms")
        print(f"  {BOLD}Kaynak:{RESET}     {len(response.sources)} adet")
        print(f"  {BOLD}Kalite:{RESET}     {warn_color}{'OK' if not warnings else ', '.join(warnings)}{RESET}")
        print(f"  {BOLD}Yanit:{RESET}")
        for line in answer_text.splitlines()[:15]:
            print(f"    {line}")
        if len(answer_text.splitlines()) > 15:
            print(f"    ... ({len(answer_text.splitlines()) - 15} satir daha)")

        return {
            "id": qid,
            "category": category,
            "question": question,
            "difficulty": difficulty,
            "expected_departments": expected_depts,
            "actual_departments": actual_depts,
            "dept_match": dept_ok,
            "expected_generation_mode": expected_mode,
            "actual_generation_mode": actual_mode,
            "mode_match": mode_ok,
            "expected_key_facts": expected_facts,
            "key_fact_results": fact_check,
            "key_facts_found": facts_found,
            "key_facts_total": facts_total,
            "elapsed_ms": elapsed_ms,
            "reported_response_time_ms": round(reported_response_time_ms, 1),
            "source_count": len(response.sources),
            "quality_warnings": warnings,
            "intent_analysis": intent_data,
            "llm_usage": llm_usage,
            "llm_usage_summary": llm_usage_summary,
            "answer": answer_text,
            "profiling": {
                "total_ms": round(profile_snapshot["total_ms"], 3),
                "events": profile_snapshot.get("events", []),
                "llm_usage": llm_usage,
                "local_profile": local_profile,
                "remote_profiles": remote_profiles,
            },
            "error": None,
        }
    except Exception as e:
        elapsed_ms = round((time.perf_counter() - start) * 1000, 1)
        error_text = f"{type(e).__name__}: {e}"
        print(f"  {RED}HATA:{RESET} {error_text}")
        return {
            "id": qid,
            "category": category,
            "question": question,
            "difficulty": difficulty,
            "expected_departments": expected_depts,
            "actual_departments": [],
            "dept_match": False,
            "expected_generation_mode": expected_mode,
            "actual_generation_mode": "error",
            "mode_match": False,
            "expected_key_facts": expected_facts,
            "key_fact_results": {},
            "key_facts_found": 0,
            "key_facts_total": len(expected_facts),
            "elapsed_ms": elapsed_ms,
            "source_count": 0,
            "quality_warnings": ["exception"],
            "llm_usage": [],
            "llm_usage_summary": {},
            "answer": "",
            "profiling": {},
            "error": error_text,
        }


async def _run_warmup_query(
    *,
    orchestrator: MainOrchestrator,
    api_client: AsyncClient | None,
    query: str,
    context_id: str,
    llm_profile: str | None,
    profile: dict[str, str],
    disable_cache: bool,
    timeout_seconds: float | None = None,
) -> None:
    """Run a warm-up query through the same execution path as measured requests."""
    if api_client is None:
        await orchestrator.handle_query(
            query,
            context_id=context_id,
            llm_profile=llm_profile,
            is_authenticated=False,
            student_number=profile.get("student_number"),
            student_full_name=profile.get("full_name"),
            student_department=profile.get("student_department"),
            student_faculty=profile.get("student_faculty"),
            student_type=profile.get("student_type"),
            disable_cache=disable_cache,
        )
        return

    response = await api_client.post(
        "/query",
        json={
            "query": query,
            "context_id": context_id,
            "llm_profile": llm_profile,
            "disable_cache": disable_cache,
            **profile,
        },
        timeout=timeout_seconds,
    )
    response.raise_for_status()


async def _run_warmup(
    *,
    orchestrator: MainOrchestrator,
    api_client: AsyncClient | None,
    questions: list[dict],
    llm_profile: str | None,
    profile: dict[str, str],
    disable_cache: bool,
    warmup_mode: str,
    warmup_timeout_seconds: float | None,
) -> tuple[int, str, str | None]:
    """Warm up either a smoke path, a representative full path set, or selected questions."""
    mode = _WARMUP_MODE_ALIASES.get((warmup_mode or "").strip().lower(), "full")
    if mode == "off":
        return 0, "off", None

    if mode == "selected":
        warmup_queries = [question["question"] for question in questions]
        effective_mode = "selected"
    elif mode == "smoke":
        warmup_queries = list(_SMOKE_WARMUP_QUERIES)
        effective_mode = "smoke"
    else:
        if api_client is not None:
            warmup_queries = list(_FULL_API_WARMUP_QUERIES)
            effective_mode = "full-api"
        else:
            warmup_queries = list(_FULL_WARMUP_QUERIES)
            effective_mode = "full"

    completed = 0
    warnings: list[str] = []
    for index, query in enumerate(warmup_queries, start=1):
        try:
            await _run_warmup_query(
                orchestrator=orchestrator,
                api_client=api_client,
                query=query,
                context_id=f"warmup-benchmark-{effective_mode}-{index}",
                llm_profile=llm_profile,
                profile=profile,
                disable_cache=disable_cache,
                timeout_seconds=warmup_timeout_seconds if api_client is not None else None,
            )
            completed += 1
        except Exception as exc:
            warnings.append(
                f"warm-up durdu ({index}/{len(warmup_queries)}): "
                f"{type(exc).__name__}: {exc}"
            )
            continue

    if warnings:
        warning_text = " | ".join(warnings[:3])
        if len(warnings) > 3:
            warning_text += f" | ... +{len(warnings) - 3} hata daha"
        if completed == 0:
            return 0, f"{effective_mode}-failed", warning_text
        return completed, f"{effective_mode}-partial", warning_text
    return completed, effective_mode, None


def print_summary(results: list[dict], categories: dict) -> None:
    print(f"\n{'=' * 70}")
    print(f"{BOLD}KALITE BENCHMARK OZETI{RESET}")
    print(f"{'=' * 70}")

    by_cat: dict[str, list[dict]] = {}
    for r in results:
        by_cat.setdefault(r["category"], []).append(r)

    total_dept_ok = 0
    total_mode_ok = 0
    total_facts_found = 0
    total_facts_total = 0
    total_quality_ok = 0
    all_times: list[float] = []
    total = len(results)
    errors = sum(1 for r in results if r["error"])

    for cat_key in sorted(by_cat.keys()):
        cat_results = by_cat[cat_key]
        cat_display = categories.get(cat_key, {}).get("display_name", cat_key)
        cat_dept = sum(1 for r in cat_results if r["dept_match"])
        cat_mode = sum(1 for r in cat_results if r["mode_match"])
        cat_ff = sum(r["key_facts_found"] for r in cat_results)
        cat_ft = sum(r["key_facts_total"] for r in cat_results)
        cat_qok = sum(1 for r in cat_results if not r["quality_warnings"])
        cat_times = [r["elapsed_ms"] for r in cat_results]

        total_dept_ok += cat_dept
        total_mode_ok += cat_mode
        total_facts_found += cat_ff
        total_facts_total += cat_ft
        total_quality_ok += cat_qok
        all_times.extend(cat_times)

        n = len(cat_results)
        fact_pct = round(cat_ff / cat_ft * 100) if cat_ft > 0 else 100

        dept_c = GREEN if cat_dept == n else (YELLOW if cat_dept > 0 else RED)
        mode_c = GREEN if cat_mode == n else (YELLOW if cat_mode > 0 else RED)
        fact_c = GREEN if fact_pct >= 80 else (YELLOW if fact_pct >= 50 else RED)

        print(
            f"\n  {BOLD}{cat_display}{RESET} ({n} soru)"
        )
        print(
            f"    Dept: {dept_c}{cat_dept}/{n}{RESET}"
            f"  |  Mod: {mode_c}{cat_mode}/{n}{RESET}"
            f"  |  Facts: {fact_c}{cat_ff}/{cat_ft} ({fact_pct}%){RESET}"
            f"  |  Kalite: {cat_qok}/{n}"
            f"  |  Ort: {round(mean(cat_times))}ms"
        )

    fact_total_pct = round(total_facts_found / total_facts_total * 100) if total_facts_total > 0 else 100

    intent_used = sum(1 for r in results if r.get("intent_analysis"))
    force_llm_count = sum(
        1 for r in results
        if (r.get("intent_analysis") or {}).get("force_llm_synthesis")
    )

    print(f"\n{'=' * 70}")
    print(f"  {BOLD}TOPLAM ({total} soru):{RESET}")
    print(f"    Departman Dogrulugu:   {total_dept_ok}/{total} ({round(total_dept_ok/total*100)}%)")
    print(f"    Uretim Modu Dogrulugu: {total_mode_ok}/{total} ({round(total_mode_ok/total*100)}%)")
    print(f"    Anahtar Bilgi Kapsami: {total_facts_found}/{total_facts_total} ({fact_total_pct}%)")
    print(f"    Temiz Kalite:          {total_quality_ok}/{total} ({round(total_quality_ok/total*100)}%)")
    print(f"    Intent Analizi:        {intent_used}/{total} soru icin aktif")
    print(f"    Force LLM Sentez:      {force_llm_count}/{total} soruda zorlanmis")
    print(f"    Hatalar:               {errors}")
    print(f"    Ortalama Sure:         {round(mean(all_times))} ms")
    print(f"    Medyan Sure:           {round(median(all_times))} ms")
    print(f"    Min / Max Sure:        {round(min(all_times))} / {round(max(all_times))} ms")


def save_results(
    results: list[dict],
    benchmark_meta: dict,
    *,
    diagnostics_delta: dict | None = None,
) -> tuple[Path, Path]:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    json_path = RESULTS_DIR / f"quality_benchmark_{timestamp}.json"
    payload = {
        "benchmark_version": benchmark_meta.get("version", "?"),
        "reranker_model": benchmark_meta.get("reranker_model", "?"),
        "run_timestamp": timestamp,
        "total_questions": len(results),
        "summary": {
            "dept_accuracy": round(
                sum(1 for r in results if r["dept_match"]) / len(results) * 100, 1
            ),
            "mode_accuracy": round(
                sum(1 for r in results if r["mode_match"]) / len(results) * 100, 1
            ),
            "key_fact_coverage": round(
                sum(r["key_facts_found"] for r in results)
                / max(sum(r["key_facts_total"] for r in results), 1)
                * 100,
                1,
            ),
            "clean_quality_pct": round(
                sum(1 for r in results if not r["quality_warnings"]) / len(results) * 100, 1
            ),
            "avg_time_ms": round(mean(r["elapsed_ms"] for r in results), 1),
            "median_time_ms": round(median(r["elapsed_ms"] for r in results), 1),
        },
        "results": results,
    }
    if diagnostics_delta:
        payload["diagnostics"] = diagnostics_delta

    intent_used = sum(1 for r in results if r.get("intent_analysis"))
    force_llm_count = sum(
        1 for r in results
        if (r.get("intent_analysis") or {}).get("force_llm_synthesis")
    )
    payload["summary"]["intent_analysis_active"] = intent_used
    payload["summary"]["force_llm_synthesis_count"] = force_llm_count
    if diagnostics_delta and diagnostics_delta.get("overview_delta"):
        overview_delta = diagnostics_delta["overview_delta"]
        payload["summary"]["a2a_query_failure_delta"] = int(
            overview_delta.get("query_failure_count") or 0
        )
        payload["summary"]["a2a_agent_task_failure_delta"] = int(
            overview_delta.get("agent_task_failure_count") or 0
        )
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    md_path = REPORT_DIR / f"quality_benchmark_report_{timestamp}.md"
    md_lines = _generate_markdown_report(
        results,
        benchmark_meta,
        payload["summary"],
        diagnostics_delta=diagnostics_delta,
    )
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    print(f"\n  JSON sonuclari: {json_path}")
    print(f"  Markdown rapor: {md_path}")
    return json_path, md_path


def _generate_markdown_report(
    results: list[dict],
    meta: dict,
    summary: dict,
    *,
    diagnostics_delta: dict | None = None,
) -> list[str]:
    lines = [
        "# Reranker Kalite Benchmark Raporu",
        "",
        f"- **Tarih**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- **Reranker Modeli**: {meta.get('reranker_model', '?')}",
        f"- **Toplam Soru**: {len(results)}",
        "",
        "## Ozet Metrikler",
        "",
        "| Metrik | Deger |",
        "|--------|-------|",
        f"| Departman Dogrulugu | {summary['dept_accuracy']}% |",
        f"| Uretim Modu Dogrulugu | {summary['mode_accuracy']}% |",
        f"| Anahtar Bilgi Kapsami | {summary['key_fact_coverage']}% |",
        f"| Temiz Kalite Orani | {summary['clean_quality_pct']}% |",
        f"| Ortalama Sure | {summary['avg_time_ms']} ms |",
        f"| Medyan Sure | {summary['median_time_ms']} ms |",
        f"| Intent Analizi Aktif | {summary.get('intent_analysis_active', 0)}/{len(results)} |",
        f"| Force LLM Sentez | {summary.get('force_llm_synthesis_count', 0)}/{len(results)} |",
        f"| A2A Query Failure Delta | {summary.get('a2a_query_failure_delta', 0)} |",
        f"| A2A Agent Task Failure Delta | {summary.get('a2a_agent_task_failure_delta', 0)} |",
        "",
    ]

    if diagnostics_delta:
        lines.extend(["## A2A Diagnostics Delta", ""])
        if diagnostics_delta.get("error"):
            lines.append(f"- Diagnostics okunamadi: `{diagnostics_delta['error']}`")
            lines.append("")
        else:
            overview_delta = diagnostics_delta.get("overview_delta") or {}
            lines.append(
                "- Overview delta: "
                f"queries={overview_delta.get('query_count', 0)}, "
                f"query_failures={overview_delta.get('query_failure_count', 0)}, "
                f"agent_tasks={overview_delta.get('agent_task_count', 0)}, "
                f"agent_task_failures={overview_delta.get('agent_task_failure_count', 0)}"
            )
            agent_deltas = [
                agent
                for agent in diagnostics_delta.get("agent_deltas", [])
                if agent.get("failed_delta")
            ]
            if agent_deltas:
                lines.append("")
                lines.append("| Agent | Role | Task Delta | Failed Delta | Last Error |")
                lines.append("|-------|------|------------|--------------|------------|")
                for agent in agent_deltas:
                    lines.append(
                        f"| {agent.get('agent_id')} | {agent.get('role')} | "
                        f"{agent.get('task_delta')} | {agent.get('failed_delta')} | "
                        f"{agent.get('last_error') or '-'} |"
                    )
            new_failures = diagnostics_delta.get("new_recent_failures") or []
            if new_failures:
                lines.append("")
                lines.append("Recent failure samples:")
                for failure in new_failures[:5]:
                    lines.append(
                        f"- `{failure.get('receiver_agent_id')}`: "
                        f"{failure.get('error')} - {failure.get('query_preview')}"
                    )
            lines.append("")

    by_cat: dict[str, list[dict]] = {}
    for r in results:
        by_cat.setdefault(r["category"], []).append(r)

    for cat_key in sorted(by_cat.keys()):
        cat_results = by_cat[cat_key]
        cat_name = meta.get("categories", {}).get(cat_key, {}).get("display_name", cat_key)
        lines.append(f"## {cat_name}")
        lines.append("")
        lines.append("| ID | Soru | Dept | Mod | Facts | Sure (ms) | Uyarilar |")
        lines.append("|---|------|------|-----|-------|-----------|----------|")

        for r in cat_results:
            dept_mark = "OK" if r["dept_match"] else "YANLIS"
            mode_mark = "OK" if r["mode_match"] else f"YANLIS ({r['actual_generation_mode']})"
            facts_mark = f"{r['key_facts_found']}/{r['key_facts_total']}"
            warns = ", ".join(r["quality_warnings"]) if r["quality_warnings"] else "-"
            q_short = r["question"][:60] + ("..." if len(r["question"]) > 60 else "")
            lines.append(
                f"| {r['id']} | {q_short} | {dept_mark} | {mode_mark} | {facts_mark} | {r['elapsed_ms']} | {warns} |"
            )
        lines.append("")

    lines.append("## Soru Detaylari")
    lines.append("")
    for r in results:
        lines.append(f"### {r['id']}: {r['question']}")
        lines.append("")
        lines.append(f"- **Kategori**: {r['category']}")
        lines.append(f"- **Zorluk**: {r['difficulty']}")
        lines.append(f"- **Departman**: {r['actual_departments']} (beklenen: {r['expected_departments']}) - {'OK' if r['dept_match'] else 'YANLIS'}")
        lines.append(f"- **Uretim Modu**: {r['actual_generation_mode']} (beklenen: {r['expected_generation_mode']}) - {'OK' if r['mode_match'] else 'YANLIS'}")
        lines.append(f"- **Key Facts**: {r['key_facts_found']}/{r['key_facts_total']}")
        if r["expected_key_facts"]:
            for fact, found in r["key_fact_results"].items():
                lines.append(f"  - {'[x]' if found else '[ ]'} {fact}")
        intent = r.get("intent_analysis")
        if intent:
            lines.append(
                f"- **Intent Analizi**: complexity={intent.get('complexity', '?')}, "
                f"force_llm={intent.get('force_llm_synthesis', '?')}, "
                f"is_personal={intent.get('is_personal', '?')}, "
                f"query_type={intent.get('query_type', '?')}"
            )
        llm_usage_line = _format_llm_usage_summary(r.get("llm_usage_summary") or {})
        if llm_usage_line:
            lines.append(f"- **LLM Kullanimi**: {llm_usage_line}")
        remote_profile_line = _format_remote_profile_summary(
            (r.get("profiling") or {}).get("remote_profiles") or []
        )
        if remote_profile_line:
            lines.append(f"- **Ajan Sureleri**: {remote_profile_line}")
        local_profile_line = _format_local_profile_summary(
            (r.get("profiling") or {}).get("local_profile")
        )
        if local_profile_line:
            lines.append(f"- **API Sureleri**: {local_profile_line}")
        lines.append(f"- **Sure**: {r['elapsed_ms']} ms")
        if r.get("reported_response_time_ms"):
            lines.append(f"- **API Response Time**: {r['reported_response_time_ms']} ms")
        lines.append(f"- **Kaynak Sayisi**: {r['source_count']}")
        if r["quality_warnings"]:
            lines.append(f"- **Uyarilar**: {', '.join(r['quality_warnings'])}")
        if r["error"]:
            lines.append(f"- **Hata**: {r['error']}")
        lines.append("")
        lines.append("**Yanit:**")
        lines.append("```")
        lines.append(r["answer"][:2000])
        if len(r["answer"]) > 2000:
            lines.append(f"... ({len(r['answer']) - 2000} karakter daha)")
        lines.append("```")
        lines.append("")

    return lines


async def main():
    parser = argparse.ArgumentParser(description="Reranker Kalite Benchmark")
    parser.add_argument("--category", type=str, default="",
                        help="Sadece belirli kategoriyi calistir (or. A, B_cross)")
    parser.add_argument("--question", type=str, nargs="+", default=[],
                        help="Bir veya birden fazla soruyu calistir (or. Q5 veya Q8 Q13 Q16)")
    parser.add_argument("--cold-start", action="store_true",
                        help="Cold-start testi (varsayilan: warm)")
    parser.add_argument("--use-api", action="store_true",
                        help="Sorgulari /query API uzerinden kos")
    parser.add_argument("--api-base-url", type=str, default="",
                        help="Gercek HTTP API taban URL'si")
    parser.add_argument("--api-timeout", type=float, default=120.0,
                        help="API benchmark istek timeout'u, saniye")
    parser.add_argument("--warmup-timeout", type=float, default=90.0,
                        help="Warm-up sorgulari icin query-bazli timeout, saniye")
    parser.add_argument("--skip-api-healthcheck", action="store_true",
                        help="API /health preflight kontrolunu atla")
    parser.add_argument("--allow-cache", action="store_true",
                        help="Benchmark sirasinda question cache lookup/storage'a izin ver")
    parser.add_argument("--warmup-mode", type=str, default="full",
                        choices=["off", "smoke", "full", "selected"],
                        help="Warm-up modu: off | smoke | full | selected (varsayilan: full)")
    parser.add_argument("--warmup-selected-questions", action="store_true",
                        help="Geriye donuk uyumluluk: warmup-mode=selected ile ayni davranis")
    parser.add_argument("--llm-profile", type=str, default="",
                        help="LLM profil tercihi: fast | balanced | quality")
    parser.add_argument("--full-name", type=str, default="",
                        help="Benchmark profil ad soyad bilgisi")
    parser.add_argument("--student-number", type=str, default="",
                        help="Benchmark profil ogrenci numarasi")
    parser.add_argument("--student-department", type=str, default="",
                        help="Benchmark profil bolum/program bilgisi")
    parser.add_argument("--student-faculty", type=str, default="",
                        help="Benchmark profil fakulte bilgisi")
    parser.add_argument("--student-type", type=str, default="",
                        help="Benchmark profil ogrenci tipi/uyruk bilgisi")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Verbose mod")
    args = parser.parse_args()

    _configure_logging(verbose=args.verbose)
    init_engine(echo=args.verbose)

    benchmark = _load_benchmark()
    questions = benchmark["questions"]
    categories = benchmark.get("categories", {})
    profile = _profile_from_args(args)

    if args.question:
        q_ids = {qid.upper() for qid in args.question}
        questions = [q for q in questions if q["id"].upper() in q_ids]
        if not questions:
            print(f"{RED}Soru bulunamadi: {', '.join(args.question)}{RESET}")
            return

    if args.category:
        cat_filter = args.category.upper()
        questions = [
            q for q in questions
            if q["category"].upper().startswith(cat_filter)
        ]
        if not questions:
            print(f"{RED}Kategori bulunamadi: {args.category}{RESET}")
            return

    print(f"{BOLD}Reranker Kalite Benchmark{RESET}")
    print(f"Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Model: {benchmark.get('reranker_model', '?')}")
    print(f"Soru Sayisi: {len(questions)}")
    if args.cold_start:
        print(f"{YELLOW}Cold-start modu aktif{RESET}")
    if not args.allow_cache:
        print(f"{YELLOW}Question cache benchmark icin bypass edilecek{RESET}")
    print(SEP)

    print("Orchestrator baslatiliyor...")
    orchestrator = MainOrchestrator(
        conversation_service=ConversationContextService(),
    )
    print("Hazir.")

    results: list[dict] = []
    api_client: AsyncClient | None = None
    diagnostics_before: dict | None = None
    diagnostics_delta: dict | None = None

    if args.use_api:
        api_client = _create_api_client(
            args.api_base_url or None,
            timeout_seconds=args.api_timeout,
        )
        if not args.skip_api_healthcheck:
            print("API health preflight kontrol ediliyor...")
            try:
                health = await _verify_api_ready(api_client)
                app_info = health.get("app") or {}
                build = app_info.get("build") if isinstance(app_info, dict) else {}
                print(
                    "API hazir."
                    f" status={health.get('status')}"
                    f" build_id={(build or {}).get('build_id')}"
                    f" a2a_mode={app_info.get('a2a_mode') if isinstance(app_info, dict) else None}"
                    f" protocol={app_info.get('a2a_transport_protocol') if isinstance(app_info, dict) else None}"
                )
            except Exception as exc:
                print(
                    f"{RED}API preflight basarisiz:{RESET} {type(exc).__name__}: {exc}"
                )
                print("Benchmark raporu uretilmedi; once API/Docker stack'i ayaga kaldirin.")
                await api_client.aclose()
                return

    warmup_mode = "selected" if args.warmup_selected_questions else args.warmup_mode

    if not args.cold_start and warmup_mode != "off":
        print("Warm-up sorgusu gonderiliyor...")
        warmup_start = time.perf_counter()
        warmup_warning: str | None = None
        try:
            warmup_count, effective_warmup_mode, warmup_warning = await _run_warmup(
                orchestrator=orchestrator,
                api_client=api_client,
                questions=questions,
                llm_profile=args.llm_profile or None,
                profile=profile,
                disable_cache=not args.allow_cache,
                warmup_mode=warmup_mode,
                warmup_timeout_seconds=min(args.api_timeout, args.warmup_timeout),
            )
        except Exception as exc:
            warmup_count = 0
            effective_warmup_mode = warmup_mode
            print(f"{YELLOW}Warm-up atlandi:{RESET} {type(exc).__name__}: {exc}")
        warmup_ms = round((time.perf_counter() - warmup_start) * 1000)
        print(
            f"Warm-up tamamlandi "
            f"(mod={effective_warmup_mode}, ic_sorgu={warmup_count}, {warmup_ms} ms)."
        )
        if warmup_warning:
            print(f"{YELLOW}Warm-up notu:{RESET} {warmup_warning}")

    if api_client is not None:
        diagnostics_before = await _fetch_a2a_diagnostics(api_client)
        if diagnostics_before and diagnostics_before.get("error"):
            print(
                f"{YELLOW}A2A diagnostics baslangic snapshot alinamadi:{RESET} "
                f"{diagnostics_before['error']}"
            )

    try:
        for i, q in enumerate(questions, 1):
            cat_display = categories.get(q["category"], {}).get("display_name", q["category"])
            if i == 1 or (i > 1 and questions[i - 2]["category"] != q["category"]):
                print(f"\n{SEP}")
                print(f"{BOLD}{cat_display}{RESET}")
                print(SEP)

            result = await run_single_question(
                orchestrator,
                q,
                api_client=api_client,
                llm_profile=args.llm_profile or None,
                profile=profile,
                disable_cache=not args.allow_cache,
            )
            results.append(result)

            if i < len(questions):
                wait_s = 5
                print(f"\n  {DIM}Rate-limit bekleme: {wait_s}s ...{RESET}", end="", flush=True)
                await asyncio.sleep(wait_s)
                print(f"\r  {DIM}Rate-limit bekleme: {wait_s}s ... tamam{RESET}")
        if api_client is not None:
            diagnostics_after = await _fetch_a2a_diagnostics(api_client)
            diagnostics_delta = _diagnostics_delta(diagnostics_before, diagnostics_after)
            if diagnostics_delta:
                if diagnostics_delta.get("error"):
                    print(
                        f"\n  {YELLOW}A2A diagnostics final snapshot alinamadi:{RESET} "
                        f"{diagnostics_delta['error']}"
                    )
                else:
                    overview_delta = diagnostics_delta.get("overview_delta") or {}
                    failures = int(overview_delta.get("agent_task_failure_count") or 0)
                    if failures:
                        print(
                            f"\n  {YELLOW}A2A diagnostics uyarisi:{RESET} "
                            f"benchmark sirasinda {failures} agent task failure kaydedildi."
                        )
    finally:
        if api_client is not None:
            await api_client.aclose()

    print_summary(results, categories)
    save_results(results, benchmark, diagnostics_delta=diagnostics_delta)


if __name__ == "__main__":
    asyncio.run(main())
