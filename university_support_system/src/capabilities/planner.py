"""LLM-backed capability planner with strict JSON output."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from pydantic import ValidationError

from src.capabilities.models import CapabilityAction
from src.capabilities.registry import (
    format_capabilities_for_prompt,
    get_capabilities_for_departments,
    validate_capability_action,
)
from src.core.config import settings

logger = logging.getLogger(__name__)


PLANNER_SYSTEM_PROMPT = """\
Universite destek botunda deterministic veritabani yetenegi secen planlayicisin.

Kurallar:
1. Sadece listelenen capability adlarindan birini sec.
2. SQL, kod veya sorgu yazma; yalnizca JSON dondur.
3. Parametreleri kullanici sorusundan ve aktif baglamdan cikar.
4. Kullanici "bu ders", "peki", "onun", "kac AKTS" gibi takip sorulari sorarsa aktif baglamdaki course/program bilgisini kullan.
5. Program/bolum degisimi varsa yeni programi kullan, eski programla birlestirme.
6. Emin degilsen veya uygun capability yoksa capability="none", fallback="rag" dondur.
7. Eksik zorunlu parametre varsa missing_params listesini doldur.
8. Ders programi/haftalik saat sorularinda schedule.weekly_program; mufredat/yariyil ders listesi sorularinda curriculum.semester_courses sec.
9. Ders var mi/yok mu sorularinda course.exists_in_program; onkosul sorularinda course.prerequisites; AKTS/kredi/ders detayinda course.detail sec.
10. Akademik takvimde derslerin baslamasi/bitimi, final, butunleme veya not giris tarihi sorularinda calendar.academic_date sec.
11. Ogrenim ucreti/katki payi/harc UCRET TUTARI sorularinda finance.tuition_fee sec; harc borcu, odeme yontemi, basvuru uygunlugu veya politika/prosedur sorularinda finance capability secme.
12. Duyuru/haber/ilan arama sorularinda announcement.search; etkinlik/seminer/konferans arama sorularinda event.search sec.
13. Tek ders, yaz okulu, okul uzamasi, ek AKTS/GANO, mezuniyet kosullari, CAP/YAP, genel kayit, mazeret, ders alma, harc borcu uygunlugu, ogrenci toplulugu/kulup kurma, topluluk uyeligi, topluluk kapatilmasi veya topluluk danismani gibi belge/policy sorularinda student_affairs.policy_lookup sec.
    Uluslararasi/yabanci/foreign ogrenci kayit, basvuru, kabul, ikamet veya belge/evrak sorularinda international.policy_lookup sec; program/fakulte zorunlu degilse eksik slot isteme.
14. Her non-none capability icin kisa bir intent yaz. Cevapta mutlaka ele alinmasi gereken alt basliklari answer_contract.must_answer listesine, beklenen kaynak turlerini evidence_contract.preferred_sources listesine koy.

Ornekler:
- "Bilgisayar muhendisligi icin bahar donemi son ders tarihi nedir?" -> {"capability":"calendar.academic_date","params":{"query":"Bilgisayar muhendisligi icin bahar donemi son ders tarihi nedir?"},"confidence":0.9}
- "Lisans programlarinda DERSLERIN BITIMI 22 Mayis 2026 mi?" -> {"capability":"calendar.academic_date","params":{"query":"Lisans programlarinda DERSLERIN BITIMI 22 Mayis 2026 mi?"},"confidence":0.9}
- "Hic almadigim bir dersten tek derse girebilir miyim?" -> {"capability":"student_affairs.policy_lookup","intent":"single_exam_eligibility","params":{"query":"Hic almadigim bir dersten tek derse girebilir miyim?","topic":"tek ders","question_type":"eligibility","must_answer":["hic alinmamis ders","devam sarti","mezuniyet icin tek ders kalma kosulu"]},"answer_contract":{"must_answer":["hic alinmamis dersten tek ders sinavina girilip girilemeyecegi","gerekli kosullar","basvuru zamani/proseduru kaynakta varsa"]},"evidence_contract":{"preferred_sources":["sik_sorulan_sorular","on_lisans_ve_lisans_yonetmeligi","tek ders yonergesi/duyurusu degil genel kural"]},"confidence":0.9}
- "Yaz okulu uzerinden cozum var mi?" -> {"capability":"student_affairs.policy_lookup","intent":"summer_school_solution","params":{"query":"Yaz okulu uzerinden okulun uzamasini engellemek icin cozum var mi?","topic":"yaz okulu","question_type":"practical_guidance","must_answer":["ders alma imkani","ders acilma kosulu","kredi/ders siniri","baska universiteden alma varsa"]},"answer_contract":{"must_answer":["yaz okulunun nasil cozum olabilecegi","kosullar ve sinirlar","kesin olmayan kisimlari belirtme"]},"evidence_contract":{"preferred_sources":["yaz okulu yonergesi","on_lisans_lisans yonetmeligi"]},"confidence":0.85}
- "Toplulugun kapatilmasi hangi durumda olur?" -> {"capability":"student_affairs.policy_lookup","intent":"student_community_closure","params":{"query":"Ogrenci toplulugunun kapatilmasi hangi durumlarda olur?","topic":"ogrenci topluluklari","question_type":"conditions","must_answer":["toplulugun kapatilma nedenleri","etkinlik kurulu karari","uyelik sonlandirma ile karistirmama"],"preferred_sources":["ogrenci topluluklari yonergesi","topluluk kapatilmasi","etkinlik kurulu"],"avoid_sources":["uyelik sonlandirma","ogrencinin mezuniyet nedeniyle uyeliginin sona ermesi","staj","akademik danismanlik yonergesi"]},"answer_contract":{"must_answer":["toplulugun kapatilma durumlari","varsa yeter sayi ve etkinlik yapmama kosullari","uyelik sonlandirma nedenlerini ayri tutma"]},"evidence_contract":{"preferred_sources":["ogrenci topluluklari yonergesi","topluluk kapatilmasi","etkinlik kurulu"],"avoid_sources":["uyelik sonlandirma","staj","akademik danismanlik yonergesi","ic denetim","guvenlik"]},"confidence":0.88}
- "Ogrenci toplulugu icin danisman sart mi?" -> {"capability":"student_affairs.policy_lookup","intent":"student_community_advisor_requirement","params":{"query":"Ogrenci toplulugu kurulusu veya isleyisi icin akademik danisman sart mi?","topic":"ogrenci topluluklari","question_type":"condition","must_answer":["akademik danisman atanmasi","danismanin topluluk isleyisindeki rolu","uyelik sarti ile karistirmama"],"preferred_sources":["ogrenci topluluklari yonergesi","akademik danisman","topluluk kurulusu"],"avoid_sources":["on lisans akademik danismanlik","lisansustu ogrenci danismanligi","uyelik sartlari tek basina"]},"answer_contract":{"must_answer":["topluluk icin akademik danisman gerekip gerekmedigi","atanma/oneri sureci kaynakta varsa","uyelik sarti olmadigini ayri ifade etme"]},"evidence_contract":{"preferred_sources":["ogrenci topluluklari yonergesi","akademik danisman","topluluk kurulusu"],"avoid_sources":["on lisans akademik danismanlik","lisansustu ogrenci danismanligi","dis hekimligi","pedagojik formasyon"]},"confidence":0.86}
- "Uluslararasi ogrenci olarak kayit icin hangi belgeler gerekir?" -> {"capability":"international.policy_lookup","intent":"international_registration_documents","params":{"query":"Uluslararasi ogrenci olarak kayit icin hangi belgeler gerekir?","topic":"uluslararasi kayit","question_type":"required_documents","must_answer":["gerekli belgeler","basvuru/kesin kayit ayrimi","ikamet/evrak teslim siniri varsa","kaynakta yoksa eksik oldugunu belirtme"],"preferred_sources":["uluslararasi ogrenci kayit","evrak teslim","uluslararasi ogrenci yonergesi","uluslararasi ogrenci basvuru","uluslararasi ogrenci kabul"],"avoid_sources":["konukevi","ozel ogrenci","yemek bursu","pedagojik formasyon"]},"answer_contract":{"must_answer":["kayit icin gerekli belgeler","basvuru/kesin kayit ayrimi","varsa asil/onayli belge sartlari","eksik bilgi varsa net sinir"]},"evidence_contract":{"preferred_sources":["uluslararasi ogrenci kayit","evrak teslim","uluslararasi ogrenci yonergesi","uluslararasi ogrenci basvuru","uluslararasi ogrenci kabul"],"avoid_sources":["konukevi","ozel ogrenci","yemek bursu","pedagojik formasyon","konu disi fakulte yonergeleri"]},"confidence":0.9}

Cikti bicimi:
{"capability":"...","intent":"...","params":{...},"missing_params":[],"answer_contract":{},"evidence_contract":{},"fallback_route":null,"confidence":0.0,"fallback":null,"reasoning":"..."}
"""


async def plan_capability_action(
    *,
    query: str,
    departments: list[object],
    llm_service: Any,
    context: dict[str, Any] | None = None,
    timeout_seconds: float | None = None,
) -> CapabilityAction | None:
    specs = get_capabilities_for_departments(departments)
    if not specs:
        return None

    prompt = build_planner_prompt(query=query, context=context or {}, capabilities=specs)
    timeout = timeout_seconds or settings.capability_planner.timeout_seconds
    try:
        response = await asyncio.wait_for(
            llm_service.generate(
                prompt,
                system=PLANNER_SYSTEM_PROMPT,
                json_mode=True,
                model_role="routing",
                llm_profile="fast",
            ),
            timeout=timeout,
        )
    except Exception as exc:  # pragma: no cover - timeout/provider safety
        logger.warning("Capability planner failed; legacy path will continue: %s", exc)
        return None

    action = parse_planner_response(response)
    if action is None:
        return None

    validation = validate_capability_action(action)
    if not validation.valid:
        action.missing_params = list(validation.missing_params)
    return action


def build_planner_prompt(
    *,
    query: str,
    context: dict[str, Any],
    capabilities: list[Any],
) -> str:
    safe_context = {
        key: value
        for key, value in context.items()
        if value not in (None, "", [], {})
    }
    return "\n".join(
        [
            f"Kullanici sorusu: {query}",
            "",
            "Aktif baglam JSON:",
            json.dumps(safe_context, ensure_ascii=False, default=str),
            "",
            "Kullanilabilir capability'ler:",
            format_capabilities_for_prompt(capabilities),
            "",
            "Yalnizca JSON dondur.",
        ]
    )


def parse_planner_response(response: Any) -> CapabilityAction | None:
    if isinstance(response, CapabilityAction):
        return response
    if isinstance(response, dict):
        payload = response
    else:
        text = str(response or "").strip()
        if not text:
            return None
        payload = _load_json_from_text(text)
    if not isinstance(payload, dict):
        return None
    try:
        action = CapabilityAction.model_validate(payload)
    except ValidationError:
        return None
    if action.departments:
        action = action.model_copy(
            update={
                "departments": [
                    str(department).strip().lower()
                    for department in action.departments
                    if str(department).strip()
                ]
            }
        )
    return action


def _load_json_from_text(text: str) -> Any:
    if text.startswith("```"):
        stripped = text.strip("`").strip()
        if stripped.lower().startswith("json"):
            stripped = stripped[4:].strip()
        text = stripped
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            return None
