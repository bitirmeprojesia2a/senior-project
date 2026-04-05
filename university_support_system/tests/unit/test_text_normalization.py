"""Metin normalizasyonu regresyon testleri."""

from src.core.text_normalization import collapse_whitespace, contains_any_normalized, normalize_text


def test_normalize_text_reduces_turkish_characters_to_ascii_like_form():
    normalized = normalize_text("ÇAP başvurusu, kayıt ücreti ve öğrenci işleri")

    assert normalized == "cap basvurusu, kayit ucreti ve ogrenci isleri"


def test_contains_any_normalized_matches_ascii_and_turkish_variants():
    assert contains_any_normalized("Kayit yenileme ucreti ne kadar?", ["kayıt yenileme ücreti"])
    assert contains_any_normalized("ÇAP başvurusu nasıl yapılır?", ["cap basvurusu"])


def test_collapse_whitespace_compacts_multiline_input():
    compact = collapse_whitespace("  Mühendislik   \n Fakültesi \t ücret  ")

    assert compact == "Mühendislik Fakültesi ücret"
