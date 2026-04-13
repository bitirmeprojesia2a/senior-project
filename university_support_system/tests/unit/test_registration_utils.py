"""Registration utility tests."""

from src.agents.student.registration_utils import (
    pick_preferred_registration_result,
    should_reject_registration_source_only_result,
)


def test_pick_preferred_registration_result_prefers_expected_cap_topic_over_conflicting_staj():
    results = [
        {
            "source": "staj_formlari.pdf",
            "content": "Zorunlu staj formu, mustahaklik ve provizyon belgesi gereklidir.",
            "score": 0.94,
            "metadata": {},
        },
        {
            "source": "cap_yonergesi.pdf",
            "content": "CAP basvurusu icin gerekli belgeler ogrenci isleri tarafindan ilan edilir.",
            "score": 0.82,
            "metadata": {},
        },
    ]

    preferred = pick_preferred_registration_result(
        "CAP basvurusu icin hangi belge gerekli?",
        results,
    )

    assert preferred is not None
    assert preferred["source"] == "cap_yonergesi.pdf"


def test_pick_preferred_registration_result_prefers_document_match_within_same_topic():
    results = [
        {
            "source": "cap_genel_kosullar.pdf",
            "content": "CAP basvurusunda genel not ortalamasi ve basari sirasi kosullari aranir.",
            "score": 0.94,
            "metadata": {},
        },
        {
            "source": "cap_basvuru_belgeleri.pdf",
            "content": "CAP basvurusu icin gerekli belgeler basvuru formu ve transkript olarak ilan edilir.",
            "score": 0.81,
            "metadata": {},
        },
    ]

    preferred = pick_preferred_registration_result(
        "CAP basvurusu icin hangi belge gerekli?",
        results,
    )

    assert preferred is not None
    assert preferred["source"] == "cap_basvuru_belgeleri.pdf"


def test_pick_preferred_registration_result_penalizes_fee_faq_for_timing_query():
    results = [
        {
            "source": "sss_kayit_dondurma.pdf",
            "content": "II. Ogretim ogrencisiyim. Kayit dondurmak istedigimde harc ucreti yatirmak zorunda miyim?",
            "score": 0.95,
            "metadata": {},
        },
        {
            "source": "yonetmelik_kayit_dondurma.pdf",
            "content": "Kayit dondurma basvurulari akademik takvimde ilan edilen tarihlerde yapilir.",
            "score": 0.72,
            "metadata": {},
        },
    ]

    preferred = pick_preferred_registration_result(
        "Kayit dondurma ne zaman yapilir?",
        results,
    )

    assert preferred is not None
    assert preferred["source"] == "yonetmelik_kayit_dondurma.pdf"


def test_should_reject_registration_source_only_result_for_wrong_faq_micro_scenario():
    item = {
        "source": "kayit_dondurma_bilgi_notu.pdf",
        "content": "II. Ogretim ogrencisiyim. Kayit dondurmak istedigimde harc ucreti yatirmak zorunda miyim?",
        "score": 0.95,
        "metadata": {},
    }

    assert should_reject_registration_source_only_result(
        "Kayit dondurma ne zaman yapilir?",
        item,
    ) is True


def test_should_reject_registration_source_only_result_when_aspect_does_not_match():
    item = {
        "source": "kayit_dondurma_genel_bilgi.pdf",
        "content": "Kayıt işlemi bittikten sonra sistem çıktı alarak saklamam gerekir mi? Böyle bir zorunluluk yoktur.",
        "score": 0.91,
        "metadata": {},
    }

    assert should_reject_registration_source_only_result(
        "Kayit dondurma ne zaman yapilir?",
        item,
    ) is True
