from src.core.constants import Department, collection_name_for_department
from src.rag.search_planner import (
    CAP_OFF_TOPIC_PENALTY,
    _apply_query_profile_source_bias,
    _apply_source_relevance,
    _detect_student_affairs_query_profile,
    _detect_query_topic,
    _plan_search_departments,
)
from src.rag.query_preprocessor import QueryPreprocessor
from src.rag.retriever import HybridRetriever
from src.rag.retriever import _select_reranker_query


def test_detect_query_topic_normalizes_ascii_turkish_variants():
    assert _detect_query_topic("CAP basvurusu nasil yapilir?") == "çap"
    assert _detect_query_topic("Yatay gecis sartlari nelerdir?") == "yatay geçiş"


def test_detect_query_topic_finds_relative_and_absolute_grading_terms():
    assert _detect_query_topic(
        "Bagil degerlendirme ile mutlak degerlendirme farki nedir?"
    ) in {"bagil degerlendirme", "mutlak degerlendirme"}


def test_query_preprocessor_expands_relative_and_absolute_grading_terms():
    expanded = QueryPreprocessor().preprocess(
        "Bagil degerlendirme ile mutlak degerlendirme hangi ogrenci sayisinda uygulanir?"
    )

    assert "bağıl değerlendirme yönergesi" in expanded.lower()
    assert "mutlak not sistemi" in expanded.lower()


def test_apply_source_relevance_prefers_bagil_degerlendirme_yonergesi():
    results = [
        {
            "source": "yonerge_dis_hekimligi_lisans_egitim_ogretim.pdf",
            "score": 0.72,
            "content": "Ders basari notu ve degerlendirme hukumleri.",
        },
        {
            "source": "lisansustu_egitim_ve_ogretim_yonetmeligi.pdf",
            "score": 0.7,
            "content": "Lisansustu derslerde not sistemi.",
        },
        {
            "source": "yonerge_bagil_degerlendirme.pdf",
            "score": 0.66,
            "content": "Bagil ve mutlak degerlendirme ogrenci sayisina gore uygulanir.",
        },
    ]

    adjusted = _apply_source_relevance(
        results,
        "Bagil degerlendirme sistemi ile mutlak degerlendirme arasindaki fark nedir?",
    )

    assert adjusted[0]["source"] == "yonerge_bagil_degerlendirme.pdf"
    assert adjusted[0]["score"] == 0.66


def test_apply_source_relevance_uses_normalized_query_terms():
    results = [
        {"source": "yonerge_cift_anadal_yandal.pdf", "score": 0.9, "content": "test"},
        {"source": "yonerge_yatay_gecis.pdf", "score": 0.8, "content": "test"},
    ]

    adjusted = _apply_source_relevance(results, "CAP basvurusu nasil yapilir?")

    assert adjusted[0]["score"] == 0.9
    assert adjusted[1]["score"] == round(0.8 * CAP_OFF_TOPIC_PENALTY, 4)


def test_apply_source_relevance_penalizes_only_clear_noise_for_exam_discipline_queries():
    results = [
        {"source": "disiplin_yonetmeligi.pdf", "score": 0.72, "content": "test"},
        {"source": "staj_ilkeleri.pdf", "score": 0.85, "content": "test"},
        {
            "source": "muhendislik_fakultesi_sinav_uygulama_kurallari.pdf",
            "score": 0.81,
            "content": "test",
        },
    ]

    adjusted = _apply_source_relevance(results, "Sinavda kopya cekmenin cezasi ve disiplin sureci nedir?")

    assert adjusted[0]["source"] == "disiplin_yonetmeligi.pdf"
    assert adjusted[0]["score"] == 0.72
    assert adjusted[1]["score"] == 0.85
    assert adjusted[2]["score"] == 0.81


def test_apply_source_relevance_boosts_relation_cutting_sources_for_leave_queries():
    results = [
        {"source": "staj_sozlesmesi.pdf", "score": 0.84, "content": "test"},
        {"source": "ogrenci_isleri_ilisik_kesme.pdf", "score": 0.7, "content": "test"},
    ]

    adjusted = _apply_source_relevance(results, "Universiteyi birakip ayrilmak istiyorum, ilisik kesme nasil yapilir?")

    assert adjusted[0]["source"] == "staj_sozlesmesi.pdf"
    assert adjusted[1]["source"] == "ogrenci_isleri_ilisik_kesme.pdf"


def test_plan_search_departments_uses_conservative_defaults_when_no_signal():
    primary, fallback = _plan_search_departments("Merhaba yardim istiyorum")

    assert primary == [Department.STUDENT_AFFAIRS]
    assert fallback == [Department.ACADEMIC_PROGRAMS, Department.FINANCE]


def test_plan_search_departments_prefers_academic_programs_for_cap_queries():
    primary, fallback = _plan_search_departments("Cift ana dal programina basvuru sartlari")

    assert primary == [Department.ACADEMIC_PROGRAMS, Department.STUDENT_AFFAIRS]
    assert fallback == [Department.FINANCE]


def test_plan_search_departments_adds_student_affairs_sources_for_bagil_academic_query():
    primary, fallback = _plan_search_departments(
        "Bagil degerlendirme ile mutlak degerlendirme farki nedir?",
        explicit_department=Department.ACADEMIC_PROGRAMS,
    )

    assert primary == [Department.ACADEMIC_PROGRAMS, Department.STUDENT_AFFAIRS]
    assert fallback == []


def test_detect_student_affairs_query_profile_finds_grade_entry_queries():
    assert _detect_student_affairs_query_profile(
        "Hocam benim ders notlarimi sisteme girmemis, ne yapabilirim?"
    ) == "grade_entry"


def test_detect_student_affairs_query_profile_finds_grade_visibility_queries():
    assert _detect_student_affairs_query_profile(
        "Sinav notlarimi nereden gorebilirim?"
    ) == "grade_visibility"


def test_detect_student_affairs_query_profile_finds_grade_objection_with_intervening_words():
    assert _detect_student_affairs_query_profile(
        "Sinav notuma nasil itiraz ederim?"
    ) == "grade_objection"


def test_apply_query_profile_source_bias_boosts_grade_entry_faq_guidance():
    results = [
        {
            "source": "ogrenci_isleri_birimi.txt",
            "score": 0.31,
            "content": "OIDB teknik destek ve bolum baskanina basvuru bilgisi.",
            "metadata": {"department": Department.STUDENT_AFFAIRS.value},
        },
        {
            "source": "2025_2026_bahar_yatay_gecis_ilan_metni.pdf",
            "score": 0.48,
            "content": "Yatay gecis kayit tarihleri ve evrak listesi.",
            "metadata": {"department": Department.STUDENT_AFFAIRS.value},
        },
    ]

    adjusted = _apply_query_profile_source_bias(
        results,
        "Hocam benim ders notlarimi sisteme girmemis bu durumda ne yapabilirim?",
        "student_affairs",
    )

    assert adjusted[0]["source"] == "ogrenci_isleri_birimi.txt"
    assert adjusted[0]["score"] > adjusted[1]["score"]


def test_apply_query_profile_source_bias_demotes_staj_for_grade_visibility():
    results = [
        {
            "source": "staj_esaslar.pdf",
            "score": 0.62,
            "content": "Ogrenci Staj Degerlendirme Formu ve staj raporu.",
            "metadata": {"department": Department.STUDENT_AFFAIRS.value},
        },
        {
            "source": "yonetmelik_onlisans_lisans_egitim_ogretim.pdf",
            "score": 0.51,
            "content": (
                "Ogrenciler sinav sonuclarini Universite tarafindan "
                "hazirlanmis sistem uzerinden gorebilir."
            ),
            "metadata": {"department": Department.STUDENT_AFFAIRS.value},
        },
    ]

    adjusted = _apply_query_profile_source_bias(
        results,
        "Sinav notlarimi nereden gorebilirim?",
        "student_affairs",
    )

    assert adjusted[0]["source"] == "yonetmelik_onlisans_lisans_egitim_ogretim.pdf"
    assert adjusted[0]["score"] > adjusted[1]["score"]


def test_apply_query_profile_source_bias_can_rescue_zero_score_grade_entry_faq():
    results = [
        {
            "source": "sik_sorulan_sorular.txt",
            "score": 0.0,
            "content": "Bolum baskanina ulasamazsaniz oidb@omu.edu.tr adresine yazabilirsiniz.",
            "metadata": {"department": Department.STUDENT_AFFAIRS.value},
        },
        {
            "source": "staj_yonergesi.pdf",
            "score": 0.18,
            "content": "Staj raporu teslim sureci.",
            "metadata": {"department": Department.STUDENT_AFFAIRS.value},
        },
    ]

    adjusted = _apply_query_profile_source_bias(
        results,
        "Hocam benim ders notlarimi sisteme girmemis bu durumda ne yapabilirim?",
        "student_affairs",
    )

    assert adjusted[0]["source"] == "sik_sorulan_sorular.txt"
    assert adjusted[0]["score"] >= 0.30


def test_apply_query_profile_source_bias_does_not_false_penalize_grade_objection_faq_for_status_word():
    results = [
        {
            "source": "sik_sorulan_sorular.txt",
            "score": 0.0,
            "content": (
                "Muafiyet talep ettigim dersin notu en az ne olmalidir? "
                "Fakat sartli gecer statusundeki dersler icin de istisna olabilir. "
                "Sinav sonuclarina nasil itiraz edebilirim? Bes is gunu icinde ilgili birime dilekce verilir."
            ),
            "metadata": {"department": Department.STUDENT_AFFAIRS.value},
        },
    ]

    adjusted = _apply_query_profile_source_bias(
        results,
        "Sinav notuma itiraz etmek istiyorum.",
        "student_affairs",
    )

    assert adjusted[0]["score"] >= 0.30


def test_apply_query_profile_source_bias_keeps_exam_rule_sources_for_discipline_queries():
    results = [
        {
            "source": "muhendislik_fakultesi_sinav_uygulama_kurallari.pdf",
            "score": 0.74,
            "content": "Cep telefonu ile ilgilenen ogrenciye kopya muamelesi yapilir.",
            "metadata": {"department": Department.STUDENT_AFFAIRS.value},
        },
        {
            "source": "staj_ilkeleri.pdf",
            "score": 0.68,
            "content": "Staj surecinde disiplin ihlalleri ayrica degerlendirilir.",
            "metadata": {"department": Department.STUDENT_AFFAIRS.value},
        },
    ]

    adjusted = _apply_query_profile_source_bias(
        results,
        "Sinavda kopya cekilmesinin cezasi nedir ve disiplin sureci nasil isler?",
        "student_affairs",
    )

    assert adjusted[0]["source"] == "muhendislik_fakultesi_sinav_uygulama_kurallari.pdf"
    assert adjusted[-1]["source"] == "staj_ilkeleri.pdf"


def test_apply_query_profile_source_bias_demotes_discipline_admin_duties_for_withdrawal():
    results = [
        {
            "source": "ogrenci_isleri_birimi.txt",
            "score": 0.58,
            "content": "Disiplin cezalarini islemek, ilisik kesme cezasi alan ogrencileri YOK'e bildirmek.",
            "metadata": {"department": Department.STUDENT_AFFAIRS.value},
        },
        {
            "source": "sik_sorulan_sorular.txt",
            "score": 0.42,
            "content": "Kaydimi sildirmek icin UBYS uzerinden ilisik kesme sureci baslatilir.",
            "metadata": {"department": Department.STUDENT_AFFAIRS.value},
        },
    ]

    adjusted = _apply_query_profile_source_bias(
        results,
        "Mezuniyet icin gerekli kosullar ve ilisik kesme sureci nedir?",
        "student_affairs",
    )

    assert adjusted[0]["source"] == "sik_sorulan_sorular.txt"
    assert adjusted[0]["score"] > adjusted[1]["score"]


def test_apply_source_relevance_does_not_override_muafiyet_profile_with_generic_transfer_topic():
    results = [
        {
            "source": "ders_yeterlik_muafiyet_ve_intibak_yonergesi.pdf",
            "score": 0.64,
            "content": "Muafiyet komisyonu ve uc hafta icinde dilekce ile basvuru yapilir.",
        },
        {
            "source": "2025_2026_bahar_yatay_gecis_ilan_metni.pdf",
            "score": 0.66,
            "content": "Yatay gecis kayit tarihleri ve evrak listesi.",
        },
    ]

    adjusted = _apply_source_relevance(
        results,
        "Yatay gecisle geldim, muafiyet basvurusunu ne zaman yapmaliyim ve karar cikana kadar derslere devam etmeli miyim?",
    )

    assert adjusted[0]["score"] == 0.64
    assert adjusted[1]["score"] == 0.66


def test_reranker_candidate_limit_expands_for_student_affairs_procedure_profiles():
    retriever = object.__new__(HybridRetriever)
    collection_name = collection_name_for_department(Department.STUDENT_AFFAIRS)

    limit = HybridRetriever._reranker_candidate_limit(
        retriever,
        collection_name,
        "procedural",
        5,
        query="Universiteyi birakip ayrilmak istiyorum, tum islemleri anlatir misin?",
    )

    assert limit >= 6


def test_select_reranker_query_uses_expanded_text_for_withdrawal_profile():
    selected = _select_reranker_query(
        "Universiteyi birakip ayrilmak istiyorum, tum islemleri anlatir misin?",
        "Universiteyi birakip ayrilmak istiyorum, tum islemleri anlatir misin? kayit sildirme ilisik kesme",
    )

    assert selected.endswith("kayit sildirme ilisik kesme")


def test_query_preprocessor_does_not_turn_cap_debt_eligibility_into_fee_lookup():
    expanded = QueryPreprocessor().preprocess(
        "Harc borcum olsaydi CAP'a basvurabilir miydim?"
    )
    normalized = expanded.lower()

    assert "cift ana dal" in normalized or "çift ana dal" in normalized
    assert "ogrenim ucreti" not in normalized
    assert "öğrenim ücreti" not in normalized
    assert "katki payi" not in normalized
    assert "katkı payı" not in normalized
    assert "harç ücreti" not in normalized


def test_query_preprocessor_keeps_fee_expansion_for_explicit_payment_question():
    expanded = QueryPreprocessor().preprocess(
        "CAP basvurusu icin harc borcumu nasil odeyebilirim?"
    )
    normalized = expanded.lower()

    assert "ogrenim ucreti" in normalized or "öğrenim ücreti" in normalized


def test_select_reranker_query_uses_clean_cap_debt_eligibility_query():
    selected = _select_reranker_query(
        "Harc borcum olsaydi CAP'a basvurabilir miydim?",
        "Harc borcum olsaydi CAP'a basvurabilir miydim? cift ana dal harc ucreti ogrenim ucreti",
    )

    assert selected == "Harc borcum olsaydi CAP'a basvurabilir miydim?"
