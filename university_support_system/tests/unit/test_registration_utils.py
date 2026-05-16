from src.agents.student.registration_utils import (
    build_payment_debt_course_registration_answer,
    build_general_exam_calendar_answer,
    filter_registration_answer_results,
    is_payment_debt_course_registration_query,
)


def test_payment_debt_course_registration_typo_is_normalized():
    query = "Harc borcum bar ders kaydi yapabilir miyim?"

    assert is_payment_debt_course_registration_query(query) is True
    answer = build_payment_debt_course_registration_answer(query)

    assert answer is not None
    assert answer.startswith("Hayir.")
    assert "ders kaydi" in answer
    assert "yaptiramaz" in answer
    assert "Turk ogrenci misiniz" not in answer


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
