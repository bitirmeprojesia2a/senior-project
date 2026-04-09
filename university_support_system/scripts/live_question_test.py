"""Canli Soru Testi - Sisteme gercek sorular sorarak test eder.

Kullanim:
  cd university_support_system
  python scripts/live_question_test.py                    # Tum kategoriler
  python scripts/live_question_test.py --benchmark core   # Profil benchmark seti
  python scripts/live_question_test.py --benchmark onboarding_prompt --use-api
  python scripts/live_question_test.py --benchmark profile_context --use-api --interactive-profile
  python scripts/live_question_test.py --kategori 1       # Sadece Ogrenci Isleri
  python scripts/live_question_test.py --kategori 2       # Sadece Finans
  python scripts/live_question_test.py --kategori 3       # Sadece Akademik
  python scripts/live_question_test.py --kategori 4       # Sadece Duyuru / Genel
  python scripts/live_question_test.py --kategori 5       # Coklu Departman
  python scripts/live_question_test.py --kategori 6       # Belirsiz / Clarification
  python scripts/live_question_test.py --kategori 7       # Kisisel Veri (Auth)
  python scripts/live_question_test.py -v                 # SQL echo + DEBUG (RAG dahil)
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from statistics import mean
from types import SimpleNamespace

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from src.core.console import configure_utf8_stdio

configure_utf8_stdio()

# create_async_engine(echo=settings.server.debug) — import oncesi ayarla; yoksa SQL stdout'a doker.
_verbose_argv = any(a in ("-v", "--verbose") for a in sys.argv)
os.environ["SERVER_DEBUG"] = "true" if _verbose_argv else "false"

from src.db.conversation_context import ConversationContextService
from src.db.connection import init_engine
from src.orchestrators.main import MainOrchestrator
from src.core.profiling import QueryProfiler, activate_profiler
from src.api.main import app as api_app
from httpx import ASGITransport, AsyncClient

BENCHMARK_FILE = Path(__file__).resolve().with_name("profile_benchmarks.json")


def _configure_test_logging(*, verbose: bool) -> None:
    """Varsayilan: RAG/structlog INFO kalir; SQLAlchemy satirlari ve echo kapali (-v ile acilir)."""
    if verbose:
        root_level = logging.DEBUG
        sql_level = logging.DEBUG
        slog_level = logging.DEBUG
    else:
        root_level = logging.WARNING
        sql_level = logging.ERROR
        slog_level = logging.INFO

    logging.basicConfig(level=root_level, force=True)
    logging.getLogger("sqlalchemy").setLevel(sql_level)
    logging.getLogger("sqlalchemy.engine").setLevel(sql_level)

    try:
        import structlog

        structlog.configure(
            wrapper_class=structlog.make_filtering_bound_logger(slog_level),
        )
    except Exception:
        pass

# ══════════════════════════════════════════════════════════
# SORU KATALOGU
# ══════════════════════════════════════════════════════════

QUESTIONS: dict[str, list[dict]] = {
    "1 - Ogrenci Isleri (Tek Departman)": [
        {"soru": "Ders kaydı ne zaman başlıyor?", "beklenen_dept": "student_affairs"},
        {"soru": "Kayıt yenileme nasıl yapılır?", "beklenen_dept": "student_affairs"},
        {"soru": "Ders ekleme çıkarma süreci nasıl işliyor?", "beklenen_dept": "student_affairs"},
        {"soru": "Transkript nasıl alınır?", "beklenen_dept": "student_affairs"},
        {"soru": "Mezuniyet şartları nelerdir?", "beklenen_dept": "student_affairs"},
        {"soru": "Staj başvurusu nasıl yapılır?", "beklenen_dept": "student_affairs"},
        {"soru": "Staj süresi kaç gün?", "beklenen_dept": "student_affairs"},
        {"soru": "Bitirme projesi nasıl seçilir?", "beklenen_dept": "student_affairs"},
        {"soru": "MUP programına nasıl başvurulur?", "beklenen_dept": "student_affairs"},
        {"soru": "Sanayi uygulaması nedir, nasıl yapılır?", "beklenen_dept": "student_affairs"},
        {"soru": "Sınav itirazı nasıl yapılır?", "beklenen_dept": "student_affairs"},
        {"soru": "Yatay geçiş şartları nelerdir?", "beklenen_dept": "student_affairs"},
    ],
    "2 - Finans (Tek Departman)": [
        {"soru": "Harç ücreti ne kadar?", "beklenen_dept": "finance"},
        {"soru": "Harç taksitlendirme yapılabiliyor mu?", "beklenen_dept": "finance"},
        {"soru": "Burs başvurusu nasıl yapılır?", "beklenen_dept": "finance"},
        {"soru": "Hangi burs türleri mevcut?", "beklenen_dept": "finance"},
        {"soru": "İkinci öğretim ücreti ne kadar?", "beklenen_dept": "finance"},
        {"soru": "Ödeme planı nasıl oluşturulur?", "beklenen_dept": "finance"},
    ],
    "3 - Akademik Programlar (Tek Departman)": [
        {"soru": "BİL104 dersinin ön koşulu nedir?", "beklenen_dept": "academic_programs"},
        {"soru": "TBMAT112 ön koşulu nedir?", "beklenen_dept": "academic_programs"},
        {"soru": "1. yarıyıl dersleri nelerdir?", "beklenen_dept": "clarification"},
        {"soru": "Teknik seçmeli dersler hangileri?", "beklenen_dept": "clarification"},
        {"soru": "Toplam kaç AKTS gerekli?", "beklenen_dept": "clarification"},
        {"soru": "Müfredat programı hakkında bilgi verir misin?", "beklenen_dept": "clarification"},
        {"soru": "Devam zorunluluğu var mı?", "beklenen_dept": "academic_programs"},
        {"soru": "Not sistemi nasıl işliyor?", "beklenen_dept": "academic_programs"},
        {"soru": "Azami öğrenim süresi kaç yıl?", "beklenen_dept": "academic_programs"},
        {"soru": "Bütünleme sınavına kimler girebilir?", "beklenen_dept": "academic_programs"},
        {"soru": "Erasmus programına nasıl başvururum?", "beklenen_dept": "academic_programs"},
    ],
    "4 - Duyuru / Genel Sorular": [
        {"soru": "Güncel duyurular nelerdir?", "beklenen_dept": "announcement"},
        {"soru": "Son açıklanan haberler neler?", "beklenen_dept": "announcement"},
        {"soru": "Üniversitenin web sitesi nedir?", "beklenen_dept": "clarification"},
    ],
    "5 - Coklu Departman (Paralel)": [
        {"soru": "Kayıt yenileme ücreti ne kadar ve ne zaman yapılır?", "beklenen_dept": "student_affairs,finance"},
        {"soru": "Erasmus bursu ne kadar ve nasıl başvurulur?", "beklenen_dept": "academic_programs,finance"},
        {"soru": "Mezuniyet harç borcu kaldı mı?", "beklenen_dept": "student_affairs,finance"},
        {"soru": "Staj yapacağım dönemde harç ödemem gerekiyor mu?", "beklenen_dept": "student_affairs,finance"},
    ],
    "6 - Belirsiz / Clarification Beklenen": [
        {"soru": "Merhaba", "beklenen_dept": "clarification"},
        {"soru": "Bilgi almak istiyorum", "beklenen_dept": "clarification"},
        {"soru": "Yardım eder misin?", "beklenen_dept": "clarification"},
        {"soru": "Teşekkürler", "beklenen_dept": "clarification"},
    ],
    "7 - Kisisel Veri Gerektiren (Auth)": [
        {"soru": "Not ortalamam kaç?", "beklenen_dept": "student_affairs", "auth": True},
        {"soru": "Harç borcum ne kadar?", "beklenen_dept": "finance", "auth": True},
        {"soru": "Burs alıyor muyum?", "beklenen_dept": "finance", "auth": True},
        {"soru": "Mezuniyetime kaç dersim kaldı?", "beklenen_dept": "student_affairs", "auth": True},
        {"soru": "Kaç AKTS tamamladım?", "beklenen_dept": "student_affairs", "auth": True},
    ],
}

# ══════════════════════════════════════════════════════════
# TEST MOTORU
# ══════════════════════════════════════════════════════════

SEPARATOR = "─" * 70
BOLD = "\033[1m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"
MAGENTA = "\033[95m"

_AUTH_SIGNALS = ("kimlik", "dogrulama", "otp", "tek kullanimlik kod", "giris yap", "oturum")
_SUSPICIOUS_QUALITY_PATTERNS = (
    "bilmedigim icin",
    "bilemedigim icin",
    "genellikle",
    "genel olarak bilinen",
    "genel bilgiler verilebilir",
    "pek dogru olmaz",
    "yardimci olur",
    "not defteri",
    "lakin",
    "genel bilgi birikimime",
    "genel bilgi birikimimden",
    "tahminim",
    "tahminimce",
    "tahminen",
    "internette arastirdiginizda",
    "genelde boyle bilinir",
    "bildigim kadariyla genel",
)
_PROMPT_LEAK_PATTERNS = (
    "sen ondokuz mayis universitesi",
    "sen ondokuz mayıs universitesi",
    "uzun zamandir bu konularla",
    "acik bir bilgi kaynagi bulamadim, ancak",
    "açık bir bilgi kaynağı bulamadım, ancak",
    "sayin ogrenci",
)

_ROLE_RECITATION_PATTERNS = (
    "harc ve odeme uzmani olarak",
    "harc ve ödeme uzmanı olarak",
    "kayit uzmani olarak",
    "mevzuat uzmani olarak",
    "uzman asistan olarak",
    "akademik programlar uzmani olarak",
)


def _dept_match(actual_depts: list[str], expected: str, *, answer: str, source_count: int) -> bool:
    if expected == "announcement":
        lowered = answer.casefold()
        return (
            set(actual_depts) == {"announcement"}
            or "aktif duyuru bulunmuyor" in lowered
            or source_count > 0
        )
    if expected == "herhangi":
        return bool(actual_depts)
    if expected == "clarification":
        return len(actual_depts) == 0
    expected_set = set(expected.split(","))
    actual_set = set(actual_depts)
    return expected_set == actual_set


_FOREIGN_LANGUAGE_PATTERNS = (
    "necesario", "however", "therefore", "furthermore", "moreover",
    "please note", "in addition", "regarding", "nevertheless",
    "por favor", "important to note that", "semestre", "financial kaynaklar",
)


def _quality_warnings(*, answer: str, needs_auth: bool, source_count: int) -> list[str]:
    warnings: list[str] = []
    lowered = answer.casefold()
    is_rule_answer = "uretim turu:" in lowered and "- kural" in lowered
    is_no_announcement_message = "aktif duyuru bulunmuyor" in lowered

    if needs_auth and not any(signal in lowered for signal in _AUTH_SIGNALS):
        warnings.append("auth_mesaji_zayif")

    if any(pattern in lowered for pattern in _SUSPICIOUS_QUALITY_PATTERNS):
        warnings.append("uydurma_riski_ifadesi")

    if any(pattern in lowered for pattern in _PROMPT_LEAK_PATTERNS):
        warnings.append("prompt_sizintisi")

    if any(pattern in lowered for pattern in _FOREIGN_LANGUAGE_PATTERNS):
        warnings.append("yabanci_dil_karisimi")

    if any(pattern in lowered for pattern in _ROLE_RECITATION_PATTERNS):
        warnings.append("rol_tekrari")

    if (
        source_count == 0
        and "kaynak ozeti:" not in lowered
        and "veritabani kaydi:" not in lowered
        and not is_rule_answer
        and not is_no_announcement_message
    ):
        warnings.append("kaynak_seffafligi_yok")

    return warnings


def _summarize_profile(snapshot: dict) -> list[dict]:
    events = snapshot.get("events", [])
    grouped: dict[str, list[float]] = {}
    for event in events:
        grouped.setdefault(event["name"], []).append(float(event.get("duration_ms", 0.0)))

    summary = []
    for name, durations in grouped.items():
        summary.append(
            {
                "stage": name,
                "calls": len(durations),
                "total_ms": round(sum(durations), 3),
                "avg_ms": round(mean(durations), 3),
                "max_ms": round(max(durations), 3),
            }
        )
    summary.sort(key=lambda item: item["total_ms"], reverse=True)
    return summary


def _load_benchmark(name: str) -> tuple[str, list[dict], bool]:
    if not BENCHMARK_FILE.exists():
        raise FileNotFoundError(f"Benchmark dosyasi bulunamadi: {BENCHMARK_FILE}")

    payload = json.loads(BENCHMARK_FILE.read_text(encoding="utf-8"))
    benchmark = payload.get(name)
    if not benchmark:
        available = ", ".join(sorted(payload.keys()))
        raise KeyError(
            f"Gecersiz benchmark: {name}. Kullanilabilir benchmarklar: {available}"
        )

    display_name = benchmark.get("display_name") or f"Benchmark - {name}"
    questions = benchmark.get("questions") or []
    shared_context = bool(benchmark.get("shared_context", False))
    return display_name, questions, shared_context


def _collect_profile_args(args) -> dict[str, str] | None:
    profile = {
        "full_name": (args.full_name or "").strip(),
        "student_number": (args.student_number or "").strip(),
        "student_department": (args.student_department or "").strip(),
        "student_faculty": (args.student_faculty or "").strip(),
        "student_type": (args.student_type or "").strip(),
    }
    if not any(profile.values()):
        return None
    return profile


def _prompt_profile_interactively(existing: dict[str, str] | None = None) -> dict[str, str]:
    profile = dict(existing or {})
    prompts = (
        ("full_name", "Ad Soyad"),
        ("student_number", "Ogrenci Numarasi"),
        ("student_department", "Bolum / Program"),
        ("student_faculty", "Fakulte"),
        ("student_type", "Ogrenci Tipi / Uyruk"),
    )
    print(f"\n{BOLD}Profil Bilgisi{RESET}")
    print("Onboarding akisini test etmek icin bilgileri girin. Bilinmeyen alanlari bos birakabilirsiniz.")
    for key, label in prompts:
        current = profile.get(key, "")
        suffix = f" [{current}]" if current else ""
        value = input(f"{label}{suffix}: ").strip()
        if value:
            profile[key] = value
    return profile


def _build_profile_submission(profile: dict[str, str]) -> str:
    lines = [
        f"Ad Soyad: {profile.get('full_name', '')}",
        f"Ogrenci Numarasi: {profile.get('student_number', '')}",
        f"Bolum: {profile.get('student_department', '')}",
        f"Fakulte: {profile.get('student_faculty', '')}",
    ]
    student_type = profile.get("student_type", "").strip()
    if student_type:
        lines.append(f"Uyruk: {student_type}")
    return "\n".join(lines)


async def _prime_profile_context(
    client: AsyncClient,
    *,
    context_id: str,
    profile: dict[str, str],
    llm_profile: str | None = None,
    announce: bool = True,
) -> None:
    payload = {
        "query": _build_profile_submission(profile),
        "context_id": context_id,
        "full_name": profile.get("full_name") or None,
        "student_number": profile.get("student_number") or None,
        "student_department": profile.get("student_department") or None,
        "student_faculty": profile.get("student_faculty") or None,
        "student_type": profile.get("student_type") or None,
        "llm_profile": llm_profile or None,
    }
    response = await client.post("/query", json=payload)
    response.raise_for_status()
    body = response.json()
    if announce:
        print(f"\n{BOLD}Profil Kaydedildi{RESET}")
        for line in str(body.get("answer", "")).splitlines():
            print(f"  {line}")


def _create_api_client(api_base_url: str | None = None) -> AsyncClient:
    """In-process test client veya gercek HTTP client olusturur."""
    if api_base_url:
        return AsyncClient(base_url=api_base_url.rstrip("/"))

    transport = ASGITransport(app=api_app)
    return AsyncClient(transport=transport, base_url="http://testserver")


async def run_single_question(
    orchestrator: MainOrchestrator,
    question: dict,
    index: int,
    *,
    api_client: AsyncClient | None = None,
    context_id: str | None = None,
    llm_profile: str | None = None,
    profile: dict[str, str] | None = None,
    prime_profile: bool = False,
) -> dict:
    soru = question["soru"]
    beklenen = question["beklenen_dept"]
    needs_auth = question.get("auth", False)

    print(f"\n  {CYAN}Soru {index}:{RESET} {soru}")
    if needs_auth:
        print(
            f"  {YELLOW}[K7: oturum yok — beklenen: kimlik dogrulama mesaji]{RESET}"
        )

    start = time.perf_counter()
    profiler = QueryProfiler(label=f"soru_{index}")
    resolved_context_id = context_id or f"live-test-{datetime.now().strftime('%H%M%S')}-q{index}"
    try:
        with activate_profiler(profiler):
            if api_client is None:
                response = await orchestrator.handle_query(
                    soru,
                    context_id=resolved_context_id,
                    llm_profile=llm_profile,
                    is_authenticated=False,
                    student_id=None,
                    student_department=(profile or {}).get("student_department") or None,
                    student_faculty=(profile or {}).get("student_faculty") or None,
                    student_type=(profile or {}).get("student_type") or None,
                    student_full_name=(profile or {}).get("full_name") or None,
                )
            else:
                if prime_profile and profile:
                    await _prime_profile_context(
                        api_client,
                        context_id=resolved_context_id,
                        profile=profile,
                        llm_profile=llm_profile,
                        announce=False,
                    )
                api_response = await api_client.post(
                    "/query",
                    json={
                        "query": soru,
                        "context_id": resolved_context_id,
                        "llm_profile": llm_profile,
                    },
                )
                api_response.raise_for_status()
                body = api_response.json()
                response = SimpleNamespace(
                    answer=body.get("answer", ""),
                    departments_involved=body.get("departments_involved", []),
                    sources=body.get("sources", []),
                    response_time_ms=body.get("response_time_ms", 0.0),
                    query_id=body.get("query_id", resolved_context_id),
                )
        elapsed = round((time.perf_counter() - start) * 1000, 1)
        profile_snapshot = profiler.snapshot()
        profile_summary = _summarize_profile(profile_snapshot)

        depts = response.departments_involved
        dept_match = _dept_match(
            depts,
            beklenen,
            answer=response.answer,
            source_count=len(response.sources),
        )
        answer_text = response.answer
        kalite_uyarilari = _quality_warnings(
            answer=answer_text,
            needs_auth=needs_auth,
            source_count=len(response.sources),
        )
        kalite_dogru = len(kalite_uyarilari) == 0

        status = f"{GREEN}OK{RESET}" if dept_match else f"{RED}YANLIS DEPT{RESET}"
        kalite_status = f"{GREEN}OK{RESET}" if kalite_dogru else f"{MAGENTA}UYARI{RESET}"

        print(f"  {BOLD}Durum:{RESET}     {status}")
        print(f"  {BOLD}Departman:{RESET} {depts if depts else '[yok - clarification]'}  (beklenen: {beklenen})")
        print(f"  {BOLD}Sure:{RESET}      {elapsed} ms")
        print(f"  {BOLD}Kaynak:{RESET}    {len(response.sources)} adet")
        print(f"  {BOLD}Kalite:{RESET}    {kalite_status}")
        if kalite_uyarilari:
            print(f"  {BOLD}Uyarilar:{RESET}  {', '.join(kalite_uyarilari)}")
        print(f"  {BOLD}Yanit:{RESET}")
        for line in answer_text.splitlines() or [""]:
            print(f"    {line}")
        if profile_summary:
            top_stage = profile_summary[0]
            print(
                f"  {BOLD}Darbogaz:{RESET}  {top_stage['stage']} "
                f"({top_stage['total_ms']} ms, {top_stage['calls']} cagri)"
            )

        return {
            "soru": soru,
            "beklenen_dept": beklenen,
            "gercek_dept": depts,
            "dept_dogru": dept_match,
            "sure_ms": elapsed,
            "yanit_uzunluk": len(response.answer),
            "kaynak_sayisi": len(response.sources),
            "kalite_dogru": kalite_dogru,
            "kalite_uyarilari": kalite_uyarilari,
            "yanit": answer_text,
            "yanit_onizleme": answer_text,
            "profil_toplam_ms": round(profile_snapshot["total_ms"], 3),
            "profil_ozet": profile_summary,
            "profil_ham": profile_snapshot,
            "hata": None,
        }
    except Exception as e:
        elapsed = round((time.perf_counter() - start) * 1000, 1)
        profile_snapshot = profiler.snapshot()
        profile_summary = _summarize_profile(profile_snapshot)
        print(f"  {RED}HATA:{RESET} {e}")
        return {
            "soru": soru,
            "beklenen_dept": beklenen,
            "gercek_dept": [],
            "dept_dogru": False,
            "sure_ms": elapsed,
            "yanit_uzunluk": 0,
            "kaynak_sayisi": 0,
            "kalite_dogru": False,
            "kalite_uyarilari": ["exception"],
            "yanit": "",
            "yanit_onizleme": "",
            "profil_toplam_ms": round(profile_snapshot["total_ms"], 3),
            "profil_ozet": profile_summary,
            "profil_ham": profile_snapshot,
            "hata": str(e),
        }


async def run_category(
    orchestrator: MainOrchestrator,
    category_name: str,
    questions: list[dict],
    *,
    limit: int | None = None,
    question_index: int | None = None,
    api_client: AsyncClient | None = None,
    shared_context_id: str | None = None,
    context_prefix: str | None = None,
    llm_profile: str | None = None,
    profile: dict[str, str] | None = None,
    prime_profile_each_question: bool = False,
) -> list[dict]:
    print(f"\n{SEPARATOR}")
    print(f"{BOLD}{category_name}{RESET}")
    print(SEPARATOR)

    results = []
    if question_index is not None:
        selected_questions = [questions[question_index - 1]] if 0 < question_index <= len(questions) else []
    else:
        selected_questions = questions[:limit] if limit else questions
    for i, q in enumerate(selected_questions, 1):
        question_context_id = shared_context_id
        if question_context_id is None:
            question_context_id = f"{context_prefix or 'live-test'}-q{i}"
        result = await run_single_question(
            orchestrator,
            q,
            i,
            api_client=api_client,
            context_id=question_context_id if api_client is not None else None,
            llm_profile=llm_profile,
            profile=profile,
            prime_profile=prime_profile_each_question,
        )
        results.append(result)
    return results


def print_summary(all_results: dict[str, list[dict]]):
    print(f"\n{'═' * 70}")
    print(f"{BOLD}GENEL OZET{RESET}")
    print(f"{'═' * 70}")

    total = 0
    correct = 0
    quality_correct = 0
    errors = 0
    total_time = 0.0

    for cat, results in all_results.items():
        cat_total = len(results)
        cat_correct = sum(1 for r in results if r["dept_dogru"])
        cat_quality = sum(1 for r in results if r.get("kalite_dogru"))
        cat_errors = sum(1 for r in results if r["hata"])
        cat_time = sum(r["sure_ms"] for r in results)

        total += cat_total
        correct += cat_correct
        quality_correct += cat_quality
        errors += cat_errors
        total_time += cat_time

        pct = round(cat_correct / cat_total * 100) if cat_total else 0
        quality_pct = round(cat_quality / cat_total * 100) if cat_total else 0
        color = GREEN if pct >= 80 else YELLOW if pct >= 50 else RED
        quality_color = GREEN if quality_pct >= 80 else YELLOW if quality_pct >= 50 else RED
        print(
            f"  {cat}: {color}{cat_correct}/{cat_total} ({pct}%){RESET} yonlendirme"
            f"  |  {quality_color}{cat_quality}/{cat_total} ({quality_pct}%){RESET} kalite"
            f"  |  {round(cat_time)}ms"
        )

    pct_total = round(correct / total * 100) if total else 0
    pct_quality_total = round(quality_correct / total * 100) if total else 0
    print(f"\n  {BOLD}TOPLAM: {correct}/{total} ({pct_total}%) dogru yonlendirme{RESET}")
    print(f"  {BOLD}KALITE: {quality_correct}/{total} ({pct_quality_total}%) temiz cevap{RESET}")
    print(f"  {BOLD}HATA:   {errors} adet{RESET}")
    print(f"  {BOLD}SURE:   {round(total_time)}ms toplam, {round(total_time/total)}ms ortalama{RESET}")


def save_results(all_results: dict[str, list[dict]]):
    out_dir = Path(__file__).resolve().parent.parent / "tests"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = out_dir / f"live_test_results_{timestamp}.json"
    profile_file = out_dir / f"live_test_profile_{timestamp}.json"
    flat = []
    profile_payload = {"generated_at": timestamp, "questions": [], "stage_summary": []}
    stage_groups: dict[str, list[float]] = {}
    for cat, results in all_results.items():
        for r in results:
            r["kategori"] = cat
            flat.append(r)
            profile_payload["questions"].append(
                {
                    "kategori": cat,
                    "soru": r["soru"],
                    "sure_ms": r["sure_ms"],
                    "profil_toplam_ms": r.get("profil_toplam_ms"),
                    "darbogaz": (r.get("profil_ozet") or [None])[0],
                    "profil_ozet": r.get("profil_ozet", []),
                    "profil_ham": r.get("profil_ham", {}),
                }
            )
            for item in r.get("profil_ozet", []):
                stage_groups.setdefault(item["stage"], []).append(float(item["total_ms"]))
    out_file.write_text(json.dumps(flat, ensure_ascii=False, indent=2), encoding="utf-8")
    for stage, totals in stage_groups.items():
        profile_payload["stage_summary"].append(
            {
                "stage": stage,
                "runs": len(totals),
                "total_ms": round(sum(totals), 3),
                "avg_ms": round(mean(totals), 3),
                "max_ms": round(max(totals), 3),
            }
        )
    profile_payload["stage_summary"].sort(key=lambda item: item["total_ms"], reverse=True)
    profile_file.write_text(json.dumps(profile_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n  Sonuclar kaydedildi: {out_file}")
    print(f"  Profil kaydi kaydedildi: {profile_file}")


# ══════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════

async def main():
    parser = argparse.ArgumentParser(description="Canli soru testi")
    parser.add_argument("--benchmark", type=str, default="",
                        help="Profil benchmark seti adi (or. core). Verilirse kategori secimini override eder")
    parser.add_argument("--kategori", type=int, default=0,
                        help="Kategori numarasi (1-7), 0=hepsi")
    parser.add_argument("--limit", type=int, default=0,
                        help="Her kategoride en fazla kac soru kosulsun")
    parser.add_argument("--soru-index", type=int, default=0,
                        help="Secili kategoride sadece verilen soru index'ini kos")
    parser.add_argument("--use-api", action="store_true",
                        help="Sorgulari dogrudan orchestrator yerine /query API uzerinden kos")
    parser.add_argument("--api-base-url", type=str, default="",
                        help="Gercek HTTP API taban URL'si (or. http://localhost:8000). Verilmezse in-process ASGI kullanilir")
    parser.add_argument("--interactive-profile", action="store_true",
                        help="API modunda onboarding akisini test etmek icin terminalden profil bilgisi iste")
    parser.add_argument("--full-name", type=str, default="",
                        help="API modunda profil icin ad soyad")
    parser.add_argument("--student-number", type=str, default="",
                        help="API modunda profil icin ogrenci numarasi")
    parser.add_argument("--student-department", type=str, default="",
                        help="API modunda profil icin bolum/program")
    parser.add_argument("--student-faculty", type=str, default="",
                        help="API modunda profil icin fakulte")
    parser.add_argument("--student-type", type=str, default="",
                        help="API modunda profil icin ogrenci tipi / uyruk")
    parser.add_argument("--llm-profile", type=str, default="",
                        help="LLM profil tercihi: fast | balanced | quality")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="SQL echo + tum structlog DEBUG (varsayilan: RAG INFO, SQL kapali)")
    args = parser.parse_args()

    if args.interactive_profile and not args.use_api:
        print(f"{RED}--interactive-profile yalnizca --use-api ile birlikte kullanilabilir.{RESET}")
        return

    if not args.use_api and _collect_profile_args(args):
        print(f"{YELLOW}Profil argumanlari direct modda orchestrator.handle_query'ye aktarilacak.{RESET}")

    _configure_test_logging(verbose=args.verbose)
    init_engine(echo=args.verbose)

    print(f"{BOLD}University Support System - Canli Soru Testi{RESET}")
    print(f"Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'═' * 70}")

    print("Orchestrator baslatiliyor...")
    orchestrator = MainOrchestrator(
        conversation_service=ConversationContextService(),
    )
    print("Hazir.\n")

    profile = _collect_profile_args(args)
    if args.interactive_profile:
        profile = _prompt_profile_interactively(profile)

    if args.benchmark:
        try:
            categories = [_load_benchmark(args.benchmark)]
        except Exception as exc:
            print(f"{RED}{exc}{RESET}")
            return
    else:
        categories = [(name, questions, False) for name, questions in QUESTIONS.items()]

        if args.kategori > 0:
            if args.kategori <= len(categories):
                categories = [categories[args.kategori - 1]]
            else:
                print(f"{RED}Gecersiz kategori: {args.kategori}{RESET}")
                return

    all_results: dict[str, list[dict]] = {}
    if args.use_api:
        async with _create_api_client(args.api_base_url or None) as api_client:
            run_context_prefix = f"live-test-{datetime.now().strftime('%H%M%S')}"

            for cat_index, (cat_name, cat_questions, share_context) in enumerate(categories, 1):
                category_context_prefix = f"{run_context_prefix}-cat{cat_index}"
                shared_context_id = f"{category_context_prefix}-shared" if share_context else None
                if shared_context_id is not None and profile:
                    await _prime_profile_context(
                        api_client,
                        context_id=shared_context_id,
                        profile=profile,
                        llm_profile=args.llm_profile or None,
                        announce=(cat_index == 1),
                    )
                results = await run_category(
                    orchestrator,
                    cat_name,
                    cat_questions,
                    limit=args.limit or None,
                    question_index=args.soru_index or None,
                    api_client=api_client,
                    shared_context_id=shared_context_id,
                    context_prefix=category_context_prefix,
                    llm_profile=args.llm_profile or None,
                    profile=profile,
                    prime_profile_each_question=bool(profile and shared_context_id is None),
                )
                all_results[cat_name] = results
    else:
        for cat_name, cat_questions, _ in categories:
            results = await run_category(
                orchestrator,
                cat_name,
                cat_questions,
                limit=args.limit or None,
                question_index=args.soru_index or None,
                llm_profile=args.llm_profile or None,
                profile=profile,
            )
            all_results[cat_name] = results

    print_summary(all_results)
    save_results(all_results)


if __name__ == "__main__":
    asyncio.run(main())
