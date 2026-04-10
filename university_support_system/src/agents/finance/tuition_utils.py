"""Utility helpers for tuition and fee-related finance queries."""

from __future__ import annotations

import re
from typing import Sequence

from src.core.text_normalization import collapse_whitespace, normalize_text

PERSONAL_KEYWORDS = ("borc", "borcum", "odeme", "taksit", "dekont", "gecmisim", "odemem", "harcim", "borclu")
STRUCTURED_FEE_QUERY_KEYWORDS = (
    "ucret",
    "harc",
    "katki payi",
    "ogrenim ucreti",
    "kayit yenileme",
    "ne kadar",
    "tutar",
)
PROCEDURAL_SOURCE_ONLY_KEYWORDS = (
    "ucret",
    "harc",
    "odeme",
    "taksit",
    "dekont",
    "kayit yenileme",
    "ne kadar",
    "ne zaman",
    "nasil odenir",
    "nereye yatirilir",
)
INTERNATIONAL_QUERY_MARKERS = (
    "uluslararasi",
    "international",
    "yabanci",
    "foreign",
    "erasmus",
    "exchange",
    "mevlana",
    "farabi",
    "degisim",
)
INTERNATIONAL_SOURCE_MARKERS = (
    "uluslararasi",
    "international",
    "yabanci",
    "foreign",
    "erasmus",
)
DOMESTIC_QUERY_MARKERS = (
    "turk",
    "turk ogrenci",
    "yerli",
    "domestic",
    "tc vatandasi",
)
FEE_AMOUNT_KEYWORDS = (
    "ucret",
    "harc",
    "ne kadar",
    "katki payi",
    "ogrenim ucreti",
    "kayit yenileme",
    "tutar",
    "toplam ucret",
)
TUITION_TABLE_SOURCE_MARKERS = (
    "ogrenim_ucret",
    "ogrenim ucret",
    "katki_payi",
    "katki payi",
    "ucretleri",
    "tuition",
    "fee",
    "harc_tablosu",
)
UNIT_QUERY_PATTERN = re.compile(
    r"([a-z ]+?(?:fakultesi|yuksekokulu|meslek yuksekokulu|meslekyuksekokulu|enstitusu|konservatuvari))",
    re.IGNORECASE,
)


def is_personal_query(query_text: str) -> bool:
    """Return whether the query asks for personal tuition state."""
    lowered = normalize_finance_text(query_text)
    return any(keyword in lowered for keyword in PERSONAL_KEYWORDS)


_FEE_POLICY_SIGNALS = (
    "asarsam", "astiginda", "asinca", "uzarsa", "uzatirsa",
    "program suresi", "normal sure", "ek sure",
    "azami sure", "sinir", "donarsa", "dondurursam",
    "odenmezse", "odemezse", "yatirmazsam",
    "iade", "muafiyet", "indirim", "afet", "burs",
)
_FEE_PROCEDURAL_SIGNALS = (
    "nereye", "nasil odenir", "nasil yatirilir", "hangi banka",
    "hangi hesap", "odeme yontemi", "odeme sekli",
    "ne zaman odenir", "son odeme", "taksitlendirme",
)


def is_structured_fee_query(query_text: str) -> bool:
    """Return whether the query should prefer structured fee lookup."""
    lowered = normalize_finance_text(query_text)
    if any(signal in lowered for signal in _FEE_POLICY_SIGNALS):
        return False
    return any(keyword in lowered for keyword in STRUCTURED_FEE_QUERY_KEYWORDS)


def normalize_student_type(value: object) -> str | None:
    """Normalize student type into domestic/international labels."""
    if not value:
        return None
    lowered = normalize_finance_text(str(value))
    if any(marker in lowered for marker in ("uluslararasi", "international", "yabanci", "foreign")):
        return "international"
    if any(marker in lowered for marker in ("turk", "domestic", "yerli", "turkiye")):
        return "domestic"
    return None


def infer_requested_student_type(query_text: str) -> str | None:
    """Infer requested student type from the query text."""
    lowered = normalize_finance_text(query_text)
    if any(marker in lowered for marker in INTERNATIONAL_QUERY_MARKERS):
        return "international"
    if any(marker in lowered for marker in DOMESTIC_QUERY_MARKERS):
        return "domestic"
    return None


def infer_source_student_type(item: dict) -> str | None:
    """Infer student type from a retrieved result item."""
    source = normalize_finance_text(item.get("source", ""))
    content = normalize_finance_text(item.get("content", "")[:1200])
    if any(marker in source or marker in content for marker in INTERNATIONAL_SOURCE_MARKERS):
        return "international"
    if any(marker in source or marker in content for marker in ("turk ogrenci", "katki payi", "domestic")):
        return "domestic"
    return None


def source_type_mismatch_penalty(item: dict, requested_type: str | None) -> int:
    """Return a sort penalty when result type mismatches requested type."""
    if requested_type is None:
        return 0
    source_type = infer_source_student_type(item)
    return 1 if source_type is not None and source_type != requested_type else 0


def looks_like_fee_result(item: dict) -> bool:
    """Return whether the item looks like a tuition/fee result."""
    text = normalize_finance_text(f"{item.get('source', '')} {item.get('content', '')}")
    return any(marker in text for marker in ("tl", "ucret", "harc", "fee", "semester fee", "katki payi"))


def looks_like_tuition_table_source(item: dict) -> bool:
    """Return whether the source filename likely belongs to a tuition table."""
    source = normalize_finance_text(item.get("source", ""))
    return any(marker in source for marker in TUITION_TABLE_SOURCE_MARKERS)


def normalize_finance_text(text: str) -> str:
    """Normalized text comparison helper."""
    return normalize_text(text)


def compact_source_content(content: str, *, max_len: int | None = 260) -> str:
    """Collapse whitespace and shorten long source content."""
    collapsed = re.sub(r"\s+", " ", content).strip()
    if max_len is not None and len(collapsed) > max_len:
        return f"{collapsed[: max_len - 3].rstrip()}..."
    return collapsed


def extract_requested_unit(query_text: str) -> str | None:
    """Extract requested faculty/school unit from the query."""
    normalized_query = normalize_finance_text(query_text)
    match = UNIT_QUERY_PATTERN.search(normalized_query)
    if match is None:
        return None
    return collapse_whitespace(match.group(1))


def display_unit_name(unit: str) -> str:
    """Format a normalized unit name for display."""
    return " ".join(part.capitalize() for part in unit.split())


def extract_unit_fee_line(content: str, requested_unit: str) -> str | None:
    """Extract the fee table row for the requested unit."""
    if not content:
        return None

    for raw_line in content.splitlines():
        compact_line = collapse_whitespace(raw_line)
        normalized_line = normalize_finance_text(compact_line)
        if requested_unit in normalized_line and re.search(r"\d[\d\.,]*", compact_line):
            return compact_line

    normalized_content = collapse_whitespace(normalize_finance_text(content))
    match = re.search(
        rf"({re.escape(requested_unit)}(?:\s+[a-z]+){{0,6}}(?:\s+\d[\d\.,]*){{1,4}})",
        normalized_content,
        re.IGNORECASE,
    )
    if match is None:
        return None
    return match.group(1).strip()


def needs_fee_context_clarification(
    query_text: str,
    student_type: str | None,
    requested_unit: str | None = None,
) -> bool:
    """Return whether the system needs student type/unit clarification."""
    lowered = normalize_finance_text(query_text)
    if not any(keyword in lowered for keyword in FEE_AMOUNT_KEYWORDS):
        return False
    if any(signal in lowered for signal in _FEE_POLICY_SIGNALS):
        return False
    if any(signal in lowered for signal in _FEE_PROCEDURAL_SIGNALS):
        return False
    if student_type not in {"domestic", "international"}:
        if any(marker in lowered for marker in INTERNATIONAL_QUERY_MARKERS):
            student_type = "international"
        elif any(marker in lowered for marker in DOMESTIC_QUERY_MARKERS):
            student_type = "domestic"
    if student_type not in {"domestic", "international"}:
        return True
    return not requested_unit


def pick_preferred_result(query_text: str, results: Sequence[dict]) -> dict | None:
    """Pick the most useful fee-related retrieval result."""
    if not results:
        return None

    requested_type = infer_requested_student_type(query_text)
    requested_unit = extract_requested_unit(query_text)
    ranked = sorted(
        results,
        key=lambda item: (
            source_type_mismatch_penalty(item, requested_type),
            0 if looks_like_tuition_table_source(item) else 1,
            0 if requested_unit and extract_unit_fee_line(item.get("content", ""), requested_unit) else 1,
            0 if looks_like_fee_result(item) else 1,
            -float(item.get("score", 0.0)),
        ),
    )
    return dict(ranked[0])


def build_structured_fee_answer(
    query_text: str,
    preferred: dict,
    *,
    db_context: str | None = None,
) -> str | None:
    """Build a structured fee answer from a retrieved tuition table row."""
    requested_type = infer_requested_student_type(query_text)
    requested_unit = extract_requested_unit(query_text)
    if requested_type is None or requested_unit is None:
        return None

    fee_line = extract_unit_fee_line(preferred.get("content", ""), requested_unit)
    if fee_line is None:
        return None

    source = preferred.get("source", "bilinmiyor")
    student_type_label = "Turk ogrenci" if requested_type == "domestic" else "uluslararasi ogrenci"
    prefix = f"{db_context}\n\n" if db_context else ""
    normalized_query = normalize_finance_text(query_text)
    question_label = "Kayit yenileme ucreti" if "kayit yenileme" in normalized_query else "Ogrenim ucreti"
    intro = (
        f"{question_label} icin {student_type_label} / {display_unit_name(requested_unit)} "
        "baglaminda ilgili ucret tablosunda su satir yer aliyor:"
    )
    return f"{prefix}{intro}\n{fee_line}\n\n(Kaynak: {source})"


def build_catalog_fee_answer(query_text: str, catalog_entry: dict) -> str:
    """Build an answer from the structured tuition fee catalog."""
    normalized_query = normalize_finance_text(query_text)
    student_type_label = (
        "Turk ogrenci" if catalog_entry["student_type"] == "domestic" else "uluslararasi ogrenci"
    )
    question_label = "Kayit yenileme ucreti" if "kayit yenileme" in normalized_query else "Ogrenim ucreti"
    semester_amount = catalog_entry.get("semester_amount")
    annual_amount = catalog_entry.get("annual_amount")
    source = catalog_entry.get("source_document", "veritabani")
    annual_text = format_currency_tr(annual_amount)

    if semester_amount is not None:
        semester_text = format_currency_tr(semester_amount)
        return (
            f"{question_label} icin {student_type_label} / {catalog_entry['unit_name']} bilgisi veritabaninda kayitli. "
            f"Yillik ucret: {annual_text}. Donemlik ucret: {semester_text}."
            f"\n\n(Kaynak: {source})"
        )

    return (
        f"{question_label} icin {student_type_label} / {catalog_entry['unit_name']} bilgisi veritabaninda kayitli. "
        f"Yillik ucret: {annual_text}."
        f"\n\n(Kaynak: {source})"
    )


def format_currency_tr(amount: float | int | None) -> str:
    """Format a numeric amount in Turkish-style currency display."""
    if amount is None:
        return "bilinmiyor"
    formatted = f"{float(amount):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{formatted} TL"


def build_honest_fee_fallback(
    query_text: str,
    preferred: dict,
    *,
    db_context: str | None = None,
) -> str | None:
    """Build an honest fallback when a tuition row cannot be extracted reliably."""
    requested_type = infer_requested_student_type(query_text)
    requested_unit = extract_requested_unit(query_text)
    if requested_type is None or requested_unit is None:
        return None

    source = preferred.get("source", "bilinmiyor")
    student_type_label = "Turk ogrenci" if requested_type == "domestic" else "uluslararasi ogrenci"
    prefix = f"{db_context}\n\n" if db_context else ""
    return (
        f"{prefix}{student_type_label} / {display_unit_name(requested_unit)} icin "
        "ilgili ucret tablosunda net ucret satirini guvenilir bicimde ayiklayamadim. "
        "Bu birim icin dogrudan teyit edebildigim tutar su anda yok.\n\n"
        f"(Kaynak: {source})"
    )


def format_tuition_snapshot(snapshot: dict) -> str:
    """Format the authenticated student's tuition status snapshot."""
    tuition = snapshot.get("tuition")
    if tuition is None:
        return f"{snapshot['student_name']} icin kayitli harc verisi bulunamadi."

    debt_amount = float(tuition["debt_amount"] or 0.0)
    paid_amount = float(tuition["paid_amount"] or 0.0)
    total_amount = float(tuition["total_amount"] or 0.0)
    due_date = tuition.get("due_date") or "belirtilmemis"

    if debt_amount > 0:
        return (
            f"{snapshot['student_name']} icin {tuition['semester']} doneminde toplam "
            f"{total_amount:.2f} TL harc kaydi var. Su ana kadar {paid_amount:.2f} TL odeme alinmis "
            f"ve {debt_amount:.2f} TL borc gorunuyor. Son odeme tarihi: {due_date}."
        )

    return (
        f"{snapshot['student_name']} icin {tuition['semester']} donemine ait "
        f"{total_amount:.2f} TL tutarindaki harc kaydi odemeyle kapanmis gorunuyor. "
        f"Son odeme tarihi: {due_date}."
    )
