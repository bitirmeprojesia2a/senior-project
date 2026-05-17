from src.agents.student.registration_utils import (
    build_payment_debt_course_registration_answer,
    build_general_exam_calendar_answer,
    filter_registration_answer_results,
    is_payment_debt_course_registration_query,
)
from src.core.text_normalization import normalize_text


def test_payment_debt_course_registration_typo_is_normalized():
    query = "Harc borcum bar ders kaydi yapabilir miyim?"

    assert is_payment_debt_course_registration_query(query) is True
    answer = build_payment_debt_course_registration_answer(query)

    assert answer is not None
    normalized_answer = normalize_text(answer)
    assert normalized_answer.startswith("hayir.")
    assert "ders kaydi" in normalized_answer
    assert "yaptiramaz" in normalized_answer
    assert "turk ogrenci misiniz" not in normalized_answer


def test_payment_debt_rule_does_not_catch_after_payment_process_query():
    query = (
        "Kayit yenileme doneminde harc ucretimi yatirdiktan sonra "
        "ders kaydini nasil yapacagim, danisman onay sureci nasil isliyor?"
    )

    assert is_payment_debt_course_registration_query(query) is False
    assert build_payment_debt_course_registration_answer(query) is None


def test_payment_debt_rule_handles_unpaid_fee_without_borc_word():
    query = "Katki payini odemeden ders kaydi yapabilir miyim?"

    assert is_payment_debt_course_registration_query(query) is True


def test_summer_school_filter_drops_unrelated_dental_sources_when_policy_source_exists():
    results = [
        {
            "source": "dis_hekimligi_fakultesi_lisans_egitim_ogretim_yonergesi.pdf",
            "content": "Dis hekimligi egitim ogretim kosullari ve yaz donemi ifadeleri.",
            "score": 0.9,
            "metadata": {},
        },
        {
            "source": "yaz_okulu_egitim_ogretim_yonergesi.pdf",
            "content": "Yaz okulunda ders alabilir. Dersin acilabilmesi ve yaz okulu sonu sinavi kosullari.",
            "score": 0.7,
            "metadata": {},
        },
    ]

    filtered = filter_registration_answer_results("Yaz okulu sartlari nelerdir?", results)

    assert len(filtered) == 1
    assert filtered[0]["source"] == "yaz_okulu_egitim_ogretim_yonergesi.pdf"


def test_cap_application_dates_use_general_academic_calendar():
    result = build_general_exam_calendar_answer("CAP basvuru tarihleri ne zaman?")

    assert result is not None
    answer, metadata = result
    assert "01-05 Eylül 2025" in answer
    assert "08-10 Eylül 2025" in answer
    assert metadata["label"] == "Cift Anadal ve Yandal Basvurulari"


def test_horizontal_transfer_application_dates_use_official_transfer_calendars():
    result = build_general_exam_calendar_answer("Yatay gecis basvuru tarihleri ne zaman?")

    assert result is not None
    answer, metadata = result
    normalized = normalize_text(answer)
    assert "01.08.2025" in normalized
    assert "15.08.2025" in normalized
    assert "26.01.2026" in normalized
    assert "01.02.2026" in normalized
    assert metadata["label"] == "horizontal_transfer_application_dates"


def test_horizontal_transfer_term_specific_application_dates_use_matching_calendar():
    fall = build_general_exam_calendar_answer("Guz yatay gecis basvuru tarihleri ne zaman?")
    spring = build_general_exam_calendar_answer("Bahar on lisans yatay gecis basvuru tarihleri ne zaman?")

    assert fall is not None
    assert "01.08.2025" in normalize_text(fall[0])
    assert "26.01.2026" not in normalize_text(fall[0])
    assert spring is not None
    assert "26.01.2026" in normalize_text(spring[0])
    assert "01.08.2025" not in normalize_text(spring[0])


def test_horizontal_transfer_registration_dates_are_calendar_backed():
    result = build_general_exam_calendar_answer("Yatay gecis kesin kayit tarihleri ne zaman?")

    assert result is not None
    answer, metadata = result
    normalized = normalize_text(answer)
    assert "18.08.2025" in normalized
    assert "29.08.2025" in normalized
    assert "09.02.2026" in normalized
    assert metadata["label"] == "horizontal_transfer_registration_dates"


def test_course_registration_dates_use_general_academic_calendar():
    result = build_general_exam_calendar_answer("Ders kayitlari ne zaman?")

    assert result is not None
    answer, metadata = result
    assert "08-24 Eylül 2025" in answer
    assert "02-15 Şubat 2026" in answer
    assert metadata["label"] == "Ders Kayitlari ve Katki Payi"


def test_advisor_approval_dates_use_general_academic_calendar():
    result = build_general_exam_calendar_answer("Danisman onay islemleri ne zaman?")

    assert result is not None
    answer, _metadata = result
    assert "08-26 Eylül 2025" in answer
    assert "02-18 Şubat 2026" in answer


def test_midterm_week_does_not_absorb_next_calendar_row():
    result = build_general_exam_calendar_answer("Ara sinav haftasi ne zaman?")

    assert result is not None
    answer, metadata = result
    assert "15-23 Kasım 2025" in answer
    assert "11-19 Nisan 2026" in answer
    assert "02 Ocak 2026" not in answer
    assert metadata["dates"] == ["15-23 Kasım 2025", "11-19 Nisan 2026"]


def test_makeup_extra_and_single_course_exam_dates_use_calendar_registry():
    makeup = build_general_exam_calendar_answer("Butunleme sinavlari ne zaman?")
    extra = build_general_exam_calendar_answer("Ek sinav tarihleri ne zaman?")
    single = build_general_exam_calendar_answer("Tek ders sinavlari ne zaman?")

    assert makeup is not None and "26 Ocak-01 Şubat 2026" in makeup[0]
    assert extra is not None and "14-25 Eylül 2026" in extra[0]
    assert single is not None and "07-09 Ekim 2026" in single[0]
