"""Helpers for regulation and international academic agents."""

from __future__ import annotations

from src.core.text_normalization import iter_alias_matches_longest_first, normalize_text

REGULATION_TOPIC_MARKERS: dict[str, tuple[str, ...]] = {
    "cap": ("cap", "cift anadal", "cift ana dal", "ikinci lisans"),
    "yandal": ("yandal", "yan dal"),
    "erasmus": ("erasmus", "degisim programi", "degisim", "mevlana", "farabi"),
    "devam zorunlulugu": ("devam zorunlulugu", "devam", "devamsizlik", "yoklama"),
    "uluslararasi": ("denklik", "ikamet", "tomer", "yos", "yabanci", "uluslararasi"),
    "azami sure": ("azami sure", "azami ogrenim suresi", "maksimum sure"),
    "not sistemi": ("not sistemi", "bagil degerlendirme", "harf notu", "gecme notu"),
}

REGULATION_PROCESS_MARKERS: tuple[str, ...] = (
    "basvuru",
    "kabul",
    "kayit",
    "tarih",
    "takvim",
    "surec",
    "adim",
    "prosedur",
    "islem",
    "nasil yapilir",
)
EXCHANGE_GRANT_QUERY_MARKERS: tuple[str, ...] = (
    "hibe",
    "burs",
    "miktar",
    "ne kadar",
    "odeme",
    "taksit",
)
EXCHANGE_GRANT_STRONG_CONTENT_MARKERS: tuple[str, ...] = (
    "ulusal ajans",
    "odeme usulu",
    "odeme usul",
    "iki taksitte",
    "%80",
    "% 80",
    "ilk odeme",
    "ikinci taksit",
    "hibe sozlesmesi",
)
EXCHANGE_GRANT_WEAK_CONTENT_MARKERS: tuple[str, ...] = (
    "hibe miktari",
    "hibe",
    "burs",
)
EXCHANGE_GRANT_PERSONNEL_MARKERS: tuple[str, ...] = (
    "personel",
    "ders verme",
    "egitim alma",
    "ogretim elemani",
)

INCOMING_EXCHANGE_QUERY_MARKERS: tuple[str, ...] = (
    "gelen ogrenci",
    "gelen erasmus",
    "gelen degisim",
    "yeni geldi",
    "universiteye geldi",
    "omuye geldi",
    "omu ye geldi",
    "incoming",
)

INCOMING_EXCHANGE_CONTENT_MARKERS: tuple[str, ...] = (
    "gelen ogrenci",
    "gelen erasmus",
    "gelen degisim",
    "gelecek degisim ogrencileri",
    "gelen degisim ogrencilerinin",
    "degisim programlari kapsaminda gelen",
    "universiteye gelen ogrenci",
    "universitesinde egitim gormek uzere gelecek",
)

INCOMING_EXCHANGE_PROCEDURE_MARKERS: tuple[str, ...] = (
    "gelen degisim ogrencilerinin kayitlari",
    "kayitlari ilgili bolum",
    "kayitlari ilgili bolum tarafindan",
    "ogrenci isleri otomasyon",
    "ogrenci numarasi verilir",
    "ogrenci kimlik karti verilir",
    "ogrenci kimlik karti cikarilir",
)

OUTGOING_EXCHANGE_CONTENT_MARKERS: tuple[str, ...] = (
    "yurt disina gidecek",
    "gidecegi universite",
    "karsi universite",
    "ogrenim anlasmasi",
    "intibak formu",
    "hibe sozlesmesi",
)

INTL_TUITION_KEYWORDS: tuple[str, ...] = (
    "harc",
    "harç",
    "ucret",
    "ücret",
    "odeme",
    "ödeme",
    "taksit",
    "katki payi",
    "ogrenim ucreti",
)


def build_regulation_intro(query_text: str) -> str:
    lowered = normalize_text(query_text)
    if "cap" in lowered or "cift anadal" in lowered:
        return "CAP mevzuatinda one cikan kosullar soyledir:"
    if "yandal" in lowered or "yan dal" in lowered:
        return "Yandal mevzuatinda one cikan kosullar soyledir:"
    if wants_incoming_exchange_info(query_text):
        return "Gelen degisim ogrencileri icin kaynakta one cikan bilgi soyledir:"
    if wants_exchange_grant_info(query_text):
        return "Erasmus hibe ve odeme kurallarinda one cikan bilgi soyledir:"
    if "erasmus" in lowered or "degisim programi" in lowered:
        return "Degisim programi kurallarinda one cikan bilgi soyledir:"
    return "Akademik mevzuatta en ilgili bilgi su sekildedir:"


def pick_preferred_regulation_result(
    query_text: str,
    results: list[dict] | tuple[dict, ...],
) -> dict | None:
    ranked = rank_regulation_results(query_text, results)
    if not ranked:
        return None
    return dict(ranked[0])


def rank_regulation_results(
    query_text: str,
    results: list[dict] | tuple[dict, ...],
) -> list[dict]:
    if not results:
        return []

    lowered = normalize_text(query_text)
    expected_markers: tuple[str, ...] = ()
    topic_aliases = {
        topic_key: (*topic_markers, topic_key)
        for topic_key, topic_markers in REGULATION_TOPIC_MARKERS.items()
    }
    for topic_key, marker in iter_alias_matches_longest_first(topic_aliases.items()):
        if marker in lowered:
            expected_markers = REGULATION_TOPIC_MARKERS[topic_key]
            break
    wants_process = any(marker in lowered for marker in REGULATION_PROCESS_MARKERS)
    wants_incoming = wants_incoming_exchange_info(query_text)
    wants_grant = wants_exchange_grant_info(query_text)

    return sorted(
        results,
        key=lambda item: (
            0 if matches_regulation_topic(item, expected_markers) else 1,
            incoming_exchange_context_rank(item, wants_incoming),
            exchange_grant_context_rank(item, wants_grant),
            0 if matches_regulation_process(item, wants_process) else 1,
            -float(item.get("score", 0.0)),
        ),
    )


def matches_regulation_topic(item: dict, expected_markers: tuple[str, ...]) -> bool:
    if not expected_markers:
        return True
    source = normalize_text(item.get("source", ""))
    content = normalize_text(item.get("content", "")[:600])
    return any(marker in source or marker in content for marker in expected_markers)


def matches_regulation_process(item: dict, wants_process: bool) -> bool:
    if not wants_process:
        return True
    content = normalize_text(item.get("content", "")[:900])
    return any(marker in content for marker in REGULATION_PROCESS_MARKERS)


def wants_exchange_grant_info(query_text: str) -> bool:
    lowered = normalize_text(query_text)
    if not any(marker in lowered for marker in ("erasmus", "degisim", "exchange")):
        return False
    return any(marker in lowered for marker in EXCHANGE_GRANT_QUERY_MARKERS)


def exchange_grant_context_rank(item: dict, wants_grant: bool) -> int:
    if not wants_grant:
        return 0
    content = normalize_text(item.get("content", "")[:1400])
    source = normalize_text(item.get("source", ""))
    haystack = f"{source} {content}"
    if any(marker in haystack for marker in EXCHANGE_GRANT_STRONG_CONTENT_MARKERS):
        if any(marker in haystack for marker in EXCHANGE_GRANT_PERSONNEL_MARKERS):
            return 1
        return 0
    if any(marker in haystack for marker in EXCHANGE_GRANT_WEAK_CONTENT_MARKERS):
        return 2
    return 3


def wants_incoming_exchange_info(query_text: str) -> bool:
    lowered = normalize_text(query_text)
    if not any(marker in lowered for marker in ("erasmus", "degisim", "exchange")):
        return False
    return any(marker in lowered for marker in INCOMING_EXCHANGE_QUERY_MARKERS)


def matches_incoming_exchange_context(item: dict, wants_incoming: bool) -> bool:
    return incoming_exchange_context_rank(item, wants_incoming) == 0


def incoming_exchange_context_rank(item: dict, wants_incoming: bool) -> int:
    if not wants_incoming:
        return 0
    source = normalize_text(item.get("source", ""))
    content = normalize_text(item.get("content", ""))
    metadata = item.get("metadata") or {}
    metadata_text = normalize_text(
        " ".join(
            str(metadata.get(key, ""))
            for key in ("bolum", "bolum_adi", "category", "subcategory", "source", "file_name")
        )
    )
    haystack = f"{source} {metadata_text} {content}"
    if any(marker in haystack for marker in INCOMING_EXCHANGE_PROCEDURE_MARKERS):
        return 0
    if any(marker in haystack for marker in INCOMING_EXCHANGE_CONTENT_MARKERS):
        return 1
    if any(marker in haystack for marker in OUTGOING_EXCHANGE_CONTENT_MARKERS):
        return 3
    return 2


def needs_international_finance_reference(query_text: str) -> bool:
    lowered = normalize_text(query_text)
    has_intl = any(
        kw in lowered for kw in ("uluslararasi", "uluslararası", "yabanci", "yabancı", "erasmus")
    )
    has_finance = any(kw in lowered for kw in INTL_TUITION_KEYWORDS)
    return has_intl and has_finance
