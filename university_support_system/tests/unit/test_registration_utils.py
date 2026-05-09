"""Registration utility tests."""

from src.agents.student.registration_utils import (
    build_general_exam_calendar_answer,
    detect_registration_query_profile,
    filter_registration_answer_results,
    is_course_registration_process_query,
    is_registration_timing_query,
    pick_preferred_registration_result,
    preferred_registration_search_top_k,
    rank_registration_results,
    rank_course_registration_process_results,
    should_force_registration_llm_synthesis,
    should_reject_registration_source_only_result,
)
from src.core.text_normalization import normalize_text


def test_build_general_calendar_answer_handles_course_end_date_for_spring_term():
    result = build_general_exam_calendar_answer(
        "Bilgisayar muhendisligi icin bahar donemi derslerin bitimi ne zaman?"
    )

    assert result is not None
    answer, metadata = result
    normalized_answer = normalize_text(answer)
    assert "bahar doneminde derslerin bitimi 22 mayis 2026" in normalized_answer
    assert metadata["label"] == "Derslerin Bitimi"
    assert normalize_text(metadata["spring"]) == "22 mayis 2026"


def test_build_general_calendar_answer_handles_course_start_date_for_fall_term():
    result = build_general_exam_calendar_answer("Guz donemi derslerin baslamasi ne zaman?")

    assert result is not None
    answer, metadata = result
    normalized_answer = normalize_text(answer)
    assert "guz doneminde derslerin baslamasi 22 eylul 2025" in normalized_answer
    assert metadata["label"] == "Derslerin Baslamasi"
    assert normalize_text(metadata["fall"]) == "22 eylul 2025"


def test_build_general_calendar_answer_handles_course_end_confirmation():
    result = build_general_exam_calendar_answer(
        "Lisans programlarinda derslerin bitimi 22 Mayis 2026 mi?"
    )

    assert result is not None
    answer, metadata = result
    normalized_answer = normalize_text(answer)
    assert "bahar donemi icin 22 mayis 2026" in normalized_answer
    assert metadata["label"] == "Derslerin Bitimi"


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


def test_pick_preferred_registration_result_penalizes_student_community_membership_for_withdrawal():
    results = [
        {
            "source": "ogrenci_topluluklari_yonergesi.pdf",
            "content": (
                "Ogrencinin mezuniyet ve benzeri nedenlerle Universitemiz ile ilisiginin "
                "kesilmesi gibi surecler disinda, uyeligi Yonetim Kurulu karari ile sonlandirilir. "
                "Uyeligi sona eren ogrenci SKSDB'ye itiraz edebilir."
            ),
            "score": 0.96,
            "metadata": {},
        },
        {
            "source": "yonetmelik_onlisans_lisans_egitim_ogretim.pdf",
            "content": (
                "Kendi istegi ile kaydini sildiren ogrencilerin Universite ile ilisigi kesilir. "
                "Kayit sildirme islemi ilgili birime basvuru ile yurutulur."
            ),
            "score": 0.72,
            "metadata": {},
        },
    ]

    preferred = pick_preferred_registration_result(
        "Universiteyi birakip ayrilmak istiyorum, tum islemleri anlatir misin?",
        results,
    )

    assert preferred is not None
    assert preferred["source"] == "yonetmelik_onlisans_lisans_egitim_ogretim.pdf"


def test_should_reject_registration_source_only_result_for_student_community_membership():
    item = {
        "source": "ogrenci_topluluklari_yonergesi.pdf",
        "content": (
            "Uyeligi sonlandirilan ogrenci teblig tarihinden itibaren SKSDB'ye itiraz edebilir."
        ),
        "score": 0.91,
        "metadata": {},
    }

    assert should_reject_registration_source_only_result(
        "Okulu birakmak ve ayrilmak istiyorum, ne yapmaliyim?",
        item,
    ) is True


def test_filter_registration_answer_results_removes_student_community_membership_context():
    results = [
        {
            "source": "ogrenci_topluluklari_yonergesi.pdf",
            "content": "Uyeligi sonlandirilan ogrenci SKSDB'ye itiraz edebilir.",
            "score": 0.95,
            "metadata": {},
        },
        {
            "source": "yonetmelik_onlisans_lisans_egitim_ogretim.pdf",
            "content": "Kendi istegi ile kaydini sildiren ogrencilerin Universite ile ilisigi kesilir.",
            "score": 0.72,
            "metadata": {},
        },
    ]

    filtered = filter_registration_answer_results(
        "Universiteyi birakip ayrilmak istiyorum, tum islemleri anlatir misin?",
        results,
    )

    assert [item["source"] for item in filtered] == [
        "yonetmelik_onlisans_lisans_egitim_ogretim.pdf"
    ]


def test_filter_registration_answer_results_keeps_student_community_when_query_is_about_membership():
    results = [
        {
            "source": "ogrenci_topluluklari_yonergesi.pdf",
            "content": "Topluluga uye olan ogrencinin uyeligi belirli durumlarda sona erer.",
            "score": 0.95,
            "metadata": {},
        },
        {
            "source": "yonetmelik_onlisans_lisans_egitim_ogretim.pdf",
            "content": "Kayit sildiren ogrencilerin Universite ile ilisigi kesilir.",
            "score": 0.72,
            "metadata": {},
        },
    ]

    filtered = filter_registration_answer_results(
        "Ogrenci toplulugundan ayrilirsam uyeligim nasil sonlanir?",
        results,
    )

    assert filtered[0]["source"] == "ogrenci_topluluklari_yonergesi.pdf"


def test_should_force_registration_llm_synthesis_for_multi_step_withdrawal_process():
    assert should_force_registration_llm_synthesis(
        "Universiteyi birakip ayrilmak istiyorum, tum islemleri ve dikkat etmem gerekenleri anlatir misin?",
        [
            {
                "source": "yonetmelik_onlisans_lisans_egitim_ogretim.pdf",
                "content": "Kayit sildirme islemi ilgili birime basvuru ile yurutulur.",
                "score": 0.72,
                "metadata": {},
            }
        ],
    ) is True


def test_should_force_registration_llm_synthesis_for_muafiyet_timing_and_attendance_question():
    assert should_force_registration_llm_synthesis(
        "Yatay gecisle geldim, muafiyet basvurusunu ne zaman yapmaliyim ve karar cikana kadar derslere devam etmeli miyim?",
        [
            {
                "source": "sik_sorulan_sorular.txt",
                "content": "Muafiyet komisyonu tarafindan karar verilir.",
                "score": 0.66,
                "metadata": {},
            }
        ],
    ) is True


def test_should_force_registration_llm_synthesis_for_course_registration_process():
    assert should_force_registration_llm_synthesis(
        "Ders kaydi nasil yapilir ve danisman onayi nasil isler?",
        [
            {
                "source": "sik_sorulan_sorular.txt",
                "content": "Ders kaydi ubys.omu.edu.tr adresinden yapilir.",
                "score": 0.72,
                "metadata": {},
            }
        ],
    ) is True


def test_detect_registration_query_profile_finds_muafiyet_queries():
    assert detect_registration_query_profile(
        "Yatay gecisle geldim, muafiyet basvurusunu ne zaman yapmaliyim?"
    ) == "muafiyet"


def test_preferred_registration_search_top_k_expands_for_admin_profiles():
    assert preferred_registration_search_top_k(
        "Hocam benim ders notlarimi sisteme girmemis, ne yapabilirim?"
    ) == 10
    assert preferred_registration_search_top_k(
        "Sinavda kopya cekilmesinin cezasi nedir ve disiplin sureci nasil isler?"
    ) == 10
    assert preferred_registration_search_top_k(
        "Yatay gecisle geldim, muafiyet basvurusunu ne zaman yapmaliyim ve karar cikana kadar derslere devam etmeli miyim?"
    ) == 12


def test_preferred_registration_search_top_k_uses_moderate_value_for_course_process_queries():
    assert preferred_registration_search_top_k(
        "Ilk kez universite kaydi yaptiran bir ogrenci olarak ders kaydindan danisman onayina kadar tum sureci anlatir misin?"
    ) == 6


def test_rank_registration_results_prefers_withdrawal_form_over_generic_faq():
    results = [
        {
            "source": "sik_sorulan_sorular.txt",
            "content": "Kayit sildirme islemi ile ilgili genel bilgi ogrenci islerinde verilir.",
            "score": 0.78,
            "metadata": {},
        },
        {
            "source": "kayit_sildirme_formu_lisans_onlisans.pdf",
            "content": "Kayit sildirme formu ve dilekce ile ilgili birime basvurulur.",
            "score": 0.71,
            "metadata": {},
        },
    ]

    ranked = rank_registration_results(
        results,
        query_text="Universiteyi birakip ayrilmak istiyorum, tum islemleri anlatir misin?",
    )

    assert ranked[0]["source"] == "kayit_sildirme_formu_lisans_onlisans.pdf"


def test_filter_registration_answer_results_keeps_exam_rule_sources_for_discipline_queries():
    results = [
        {
            "source": "muhendislik_fakultesi_sinav_uygulama_kurallari.pdf",
            "content": "Cep telefonu ile ilgilenen ogrenciye kopya muamelesi yapilir.",
            "score": 0.76,
            "metadata": {},
        },
        {
            "source": "staj_ilkeleri.pdf",
            "content": "Staj surecinde disiplin ihlalleri ayrica degerlendirilir.",
            "score": 0.81,
            "metadata": {},
        },
    ]

    filtered = filter_registration_answer_results(
        "Sinavda kopya cekilmesinin cezasi nedir ve disiplin sureci nasil isler?",
        results,
    )

    assert [item["source"] for item in filtered] == [
        "muhendislik_fakultesi_sinav_uygulama_kurallari.pdf"
    ]


def test_filter_registration_answer_results_keeps_muafiyet_guideline_even_for_timing_query():
    results = [
        {
            "source": "ders_yeterlik_muafiyet_ve_intibak_yonergesi.pdf",
            "content": "Muafiyet komisyonu ve intibak islemleri ilgili birim tarafindan yurutilur.",
            "score": 0.78,
            "metadata": {},
        },
        {
            "source": "yatay_gecis_ilan.pdf",
            "content": "Yatay gecis kayit tarihleri 26.01.2026 - 01.02.2026 arasindadir.",
            "score": 0.83,
            "metadata": {},
        },
    ]

    filtered = filter_registration_answer_results(
        "Yatay gecisle geldim, muafiyet basvurusunu ne zaman yapmaliyim ve karar cikana kadar derslere devam etmeli miyim?",
        results,
    )

    assert any("muafiyet_ve_intibak" in item["source"] for item in filtered)


def test_is_registration_timing_query_accepts_mixed_fee_and_timing_question():
    assert is_registration_timing_query(
        "Kayit yenileme ucreti ne kadar ve ne zaman yapilir?"
    ) is True


def test_is_registration_timing_query_rejects_payment_then_course_registration_process():
    assert is_registration_timing_query(
        "Kayit yenileme doneminde harc ucretimi yatirdiktan sonra ders kaydini nasil yapacagim, danisman onay sureci nasil isliyor?"
    ) is False


def test_is_registration_timing_query_rejects_freeze_fee_policy_question():
    assert is_registration_timing_query(
        "Ikinci ogretim ogrencisiyim ve bir donem kayit dondurmak istiyorum. Bu donem harc ucretimi yatirmak zorunda miyim?"
    ) is False


def test_is_course_registration_process_query_accepts_inflected_course_registration():
    assert is_course_registration_process_query(
        "Ilk kez kayit yaptiran ogrenci olarak ders kaydindan danisman onayina kadar sureci anlatir misin?"
    ) is True


def test_rank_course_registration_process_results_prefers_faq_process_chunks():
    results = [
        {
            "source": "document.pdf",
            "content": "Staj belgesi guvenli elektronik imza ile onaylanir.",
            "score": 0.9,
            "metadata": {},
        },
        {
            "source": "yonetmelik_onlisans_lisans.pdf",
            "content": "Ders kaydi akademik takvimde belirtilen surede ogrenci bilgi sistemi uzerinden yapilir.",
            "score": 0.8,
            "metadata": {},
        },
        {
            "source": "sik_sorulan_sorular.txt",
            "content": (
                "Ders kaydini nerede yapabilirim? ubys.omu.edu.tr adresinden yapabilirsiniz. "
                "Danisman onayi tamamlandiktan sonra sinif yoklama listesini kontrol ediniz."
            ),
            "score": 0.2,
            "metadata": {},
        },
    ]

    ranked = rank_course_registration_process_results(results)

    assert ranked[0]["source"] == "sik_sorulan_sorular.txt"
    assert ranked[-1]["source"] == "document.pdf"


def test_rank_course_registration_process_results_boosts_leave_return_context():
    results = [
        {
            "source": "sik_sorulan_sorular.txt",
            "content": "Ders kaydi ogrenci bilgi sistemi uzerinden yapilir.",
            "score": 0.9,
            "metadata": {},
        },
        {
            "source": "yonetmelik_onlisans_lisans_egitim_ogretim.pdf",
            "content": (
                "Kayit dondurma suresinin bitiminde ogrenci ayrildigi donemin "
                "basindan baslamak kosuluyla ogrenimine kaldigi yerden devam eder. "
                "Ders kaydi akademik takvimde belirtilen surede yapilir."
            ),
            "score": 0.5,
            "metadata": {},
        },
    ]

    ranked = rank_course_registration_process_results(
        results,
        query_text="Okulumu dondurup 1 yil ara verdikten sonra donuste ders secimini nasil yapacagim?",
    )

    assert ranked[0]["source"] == "yonetmelik_onlisans_lisans_egitim_ogretim.pdf"


def test_detect_registration_query_profile_for_new_admin_workflows():
    assert (
        detect_registration_query_profile("sinav notuma itiraz etmek istiyorum")
        == "grade_objection"
    )
    assert (
        detect_registration_query_profile("hocam ders notlarimi sisteme girmemis")
        == "grade_entry"
    )
    assert (
        detect_registration_query_profile("universiteyi birakip ayrilmak istiyorum")
        == "withdrawal"
    )
    assert (
        detect_registration_query_profile("sinavda kopya cekilirse disiplin sureci nasil isler")
        == "discipline"
    )
    assert (
        detect_registration_query_profile(
            "Matematik dersi yuzunden okulum uzuyor nasil cozum bulabilirim?"
        )
        == "course_delay"
    )


def test_filter_registration_answer_results_prefers_faq_for_course_delay_advice():
    results = [
        {
            "source": "yks_taban_puan_tablosu.pdf",
            "content": "YKS taban puanlari ve kontenjanlar listelenir.",
            "score": 0.91,
            "metadata": {},
        },
        {
            "source": "sik_sorulan_sorular.txt",
            "content": (
                "Eksik ders alarak donem uzatmamak icin her donem basinda "
                "mufredat durum kontrolu yapilmalidir. Oncelikle basarisiz "
                "oldugunuz ve hic almadigi alt donem dersleri alinmalidir."
            ),
            "score": 0.62,
            "metadata": {},
        },
    ]

    filtered = filter_registration_answer_results(
        "Matematik dersi yuzunden okulum uzuyor nasil cozum bulabilirim?",
        results,
    )

    assert [item["source"] for item in filtered] == ["sik_sorulan_sorular.txt"]


def test_should_force_registration_llm_synthesis_for_focused_profiles():
    sample_results = [
        {
            "source": "sik_sorulan_sorular.txt",
            "content": "Yaz okulunda derslere devam zorunludur.",
            "score": 0.7,
            "metadata": {},
        }
    ]

    assert should_force_registration_llm_synthesis(
        "Yaz okulu uzerinden cozum var mi?",
        sample_results,
    ) is True
    assert should_force_registration_llm_synthesis(
        "Hic almadigim bir dersten tek derse girebilir miyim?",
        sample_results,
    ) is True


def test_rank_registration_results_prefers_faq_for_grade_objection():
    results = [
        {
            "source": "ders_yeterlilik_sinavi_uygulama_yonergesi.pdf",
            "content": "Sinav notuna itiraz icin on bes is gunu uygulanir.",
            "score": 0.9,
            "metadata": {},
        },
        {
            "source": "sik_sorulan_sorular.txt",
            "content": (
                "Sinav sonuclarina nasil itiraz edebilirim? "
                "Bes is gunu icinde Bolum Baskanligina dilekce ile itiraz edebilirsiniz."
            ),
            "score": 0.6,
            "metadata": {},
        },
    ]

    ranked = rank_registration_results(
        results,
        query_text="Sinav notuma itiraz etmek istiyorum.",
    )

    assert ranked[0]["source"] == "sik_sorulan_sorular.txt"


def test_filter_registration_answer_results_drops_unrelated_grade_objection_sources():
    results = [
        {
            "source": "ogrenci_konukevi_uygulama_yonergesi.pdf",
            "content": "Konukevi yonetim kuruluna yedi gun icinde itiraz edilir.",
            "score": 0.88,
            "metadata": {},
        },
        {
            "source": "sik_sorulan_sorular.txt",
            "content": (
                "Sinav sonuclarina nasil itiraz edebilirim? "
                "Bes is gunu icinde ilgili birime dilekce ile itiraz edebilirsiniz."
            ),
            "score": 0.61,
            "metadata": {},
        },
    ]

    filtered = filter_registration_answer_results(
        "Sinav notuma itiraz etmek istiyorum.",
        results,
    )

    assert [item["source"] for item in filtered] == ["sik_sorulan_sorular.txt"]


def test_rank_registration_results_prefers_faq_for_grade_entry_issue():
    results = [
        {
            "source": "on_lisans_ve_lisans_egitim_ogretim_yonetmeligi.pdf",
            "content": "Notlar ogretim elemani tarafindan sisteme girilir.",
            "score": 0.82,
            "metadata": {},
        },
        {
            "source": "sik_sorulan_sorular.txt",
            "content": (
                "Bolum baskanina ulasamazsaniz oidb@omu.edu.tr adresine sistemle ilgili "
                "sorununuzu e-posta ile iletebilirsiniz."
            ),
            "score": 0.51,
            "metadata": {},
        },
    ]

    ranked = rank_registration_results(
        results,
        query_text="Hocam benim ders notlarimi sisteme girmemis, ne yapabilirim?",
    )

    assert ranked[0]["source"] == "sik_sorulan_sorular.txt"


def test_filter_registration_answer_results_drops_unrelated_grade_entry_sources():
    results = [
        {
            "source": "staj_ilkeleri.pdf",
            "content": "Staj komisyonu gerekli duzeltmeleri ister.",
            "score": 0.85,
            "metadata": {},
        },
        {
            "source": "sik_sorulan_sorular.txt",
            "content": (
                "Bolum baskanina ulasamazsaniz oidb@omu.edu.tr adresine "
                "sistemle ilgili sorununuzu iletebilirsiniz."
            ),
            "score": 0.52,
            "metadata": {},
        },
    ]

    filtered = filter_registration_answer_results(
        "Hocam benim ders notlarimi sisteme girmemis, ne yapabilirim?",
        results,
    )

    assert [item["source"] for item in filtered] == ["sik_sorulan_sorular.txt"]


def test_filter_registration_answer_results_drops_discipline_negative_sources():
    results = [
        {
            "source": "staj_ilkeleri.pdf",
            "content": "Isyeri staj disiplin sureci",
            "score": 0.88,
            "metadata": {},
        },
        {
            "source": "muhendislik_fakultesi_sinav_uygulama_kurallari.pdf",
            "content": "Cep telefonu ile ilgilenene kopya muamelesi yapilir.",
            "score": 0.81,
            "metadata": {},
        },
        {
            "source": "ogrenci_disiplin_yonetmeligi.pdf",
            "content": "Kopya cekmek disiplin sucudur.",
            "score": 0.55,
            "metadata": {},
        },
    ]

    filtered = filter_registration_answer_results(
        "Sinavda kopya cekilmesinin cezasi nedir ve disiplin sureci nasil isler?",
        results,
    )

    assert [item["source"] for item in filtered] == [
        "muhendislik_fakultesi_sinav_uygulama_kurallari.pdf",
        "ogrenci_disiplin_yonetmeligi.pdf",
    ]


def test_filter_registration_answer_results_drops_withdrawal_negative_sources():
    results = [
        {
            "source": "kimlik_karti_yonergesi.pdf",
            "content": "Kimlik kartini iade etmeyen ogrencilerin islemleri tamamlanmaz.",
            "score": 0.91,
            "metadata": {},
        },
        {
            "source": "ogrenci_isleri_birimi.txt",
            "content": "UBYS uzerinden ilisik kesme sureci baslatilir.",
            "score": 0.52,
            "metadata": {},
        },
    ]

    filtered = filter_registration_answer_results(
        "Universiteyi birakip ayrilmak istiyorum, tum islemleri anlatir misin?",
        results,
    )

    assert [item["source"] for item in filtered] == ["ogrenci_isleri_birimi.txt"]


def test_should_force_registration_llm_synthesis_forces_discipline_queries():
    results = [
        {
            "source": "muhendislik_fakultesi_sinav_uygulama_kurallari.pdf",
            "content": "Kopya muamelesi yapilir.",
            "score": 0.91,
            "metadata": {},
        },
        {
            "source": "ogrenci_disiplin_yonetmeligi.pdf",
            "content": "Kopya cekmek disiplin sucudur.",
            "score": 0.88,
            "metadata": {},
        },
        {
            "source": "ogrenci_isleri_yonergesi.pdf",
            "content": "Disiplin sureci ilgili yonetmelige gore yurutulur.",
            "score": 0.85,
            "metadata": {},
        },
    ]

    assert should_force_registration_llm_synthesis(
        "Sinavda kopya cekilmesinin cezasi nedir ve disiplin sureci nasil isler?",
        results,
    ) is True


def test_should_reject_registration_source_only_result_does_not_drop_non_negative_discipline_source():
    item = {
        "source": "ogrenci_disiplin_yonetmeligi.pdf",
        "content": "Kopya cekmek disiplin sucudur ve ogrenci disiplin yonetmeligine tabidir.",
        "score": 0.55,
        "metadata": {},
    }

    assert should_reject_registration_source_only_result(
        "Sinavda kopya cekilmesinin cezasi nedir ve disiplin sureci nasil isler?",
        item,
    ) is False
