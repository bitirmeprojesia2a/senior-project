from __future__ import annotations

from src.core.constants import Department
from src.core.policy_facets import resolve_policy_facet
from src.db.schemas import DepartmentResponse, RAGSource
from src.quality.evidence_answer_validator import should_enforce_validation, validate_evidence_answer


def _cap_response() -> DepartmentResponse:
    claim = (
        "Ogrencinin CAP'a basvurabilmesi icin basvurusu sirasindaki ana dal "
        "not ortalamasinin 4,00 uzerinden en az 3,00 olmasi ve ana dal diploma "
        "programinin ilgili sinifinda basari siralamasi itibari ile en az ilk "
        "% 20'sinde bulunmasi gerekir."
    )
    return DepartmentResponse(
        department=Department.STUDENT_AFFAIRS,
        answer="Kaynak bilgisi final cevap icin hazirlandi.",
        sources=[
            RAGSource(
                content=claim,
                score=0.91,
                metadata={"source": "yonerge_cift_anadal_yandal.pdf"},
            )
        ],
        metadata={
            "evidence_packet": {
                "specialist_response_mode": "evidence_packet",
                "final_answer_owner": "main_orchestrator",
                "facts": [
                    {
                        "claim": claim,
                        "source": "yonerge_cift_anadal_yandal.pdf",
                    }
                ],
                "selected_sources": [
                    {
                        "snippet": claim,
                        "source": "yonerge_cift_anadal_yandal.pdf",
                    }
                ],
            }
        },
    )


def test_validator_passes_when_required_gpa_value_is_preserved():
    result = validate_evidence_answer(
        query="CAP basvurusu icin not ortalamasi kac olmali?",
        answer="CAP basvurusu icin ana dal not ortalamasinin en az 3,00 olmasi gerekir.",
        responses=[_cap_response()],
    )

    assert result.status == "pass"
    assert result.requires_judge is False
    assert "3,00" not in result.missing_values


def test_validator_fails_when_answer_denies_available_gpa_value():
    result = validate_evidence_answer(
        query="CAP basvurusu icin not ortalamasi kac olmali?",
        answer=(
            "Kaynakta basari siralamasi icin ilk %20 kosulu var, ancak not "
            "ortalamasinin tam olarak kac olacagi net degil."
        ),
        responses=[_cap_response()],
    )

    assert result.status == "fail"
    assert result.requires_judge is True
    assert result.reason == "answer_denies_available_evidence"
    assert "3,00" in result.missing_values
    assert result.mode == "shadow"
    assert should_enforce_validation(result) is False


def test_validator_fails_when_answer_uses_conflicting_numeric_value():
    result = validate_evidence_answer(
        query="CAP basvurusu icin not ortalamasi kac olmali?",
        answer="CAP basvurusu icin not ortalamasinin en az 2,75 olmasi gerekir.",
        responses=[_cap_response()],
    )

    assert result.status == "fail"
    assert result.requires_judge is True
    assert result.reason == "answer_conflicts_with_evidence_values"
    assert "3,00" in result.missing_values
    assert "2,75" in result.conflicting_values


def test_validator_ignores_values_from_policy_alignment_conflict():
    cap_claim = (
        "Ogrencinin CAP'a basvurabilmesi icin ana dal not ortalamasinin "
        "4,00 uzerinden en az 3,00 olmasi gerekir."
    )
    minor_claim = (
        "Yan dal programina basvurabilmek icin not ortalamasinin "
        "4,00 uzerinden en az 2,00 olmasi sarttir."
    )
    response = DepartmentResponse(
        department=Department.STUDENT_AFFAIRS,
        answer="Kaynak bilgisi final cevap icin hazirlandi.",
        sources=[],
        metadata={
            "evidence_packet": {
                "facts": [
                    {
                        "claim": cap_claim,
                        "source": "yonerge_cift_anadal_yandal.pdf",
                        "policy_alignment": {
                            "status": "match",
                            "query_target_program": "double_major",
                            "matched_programs": ["double_major"],
                        },
                    },
                    {
                        "claim": minor_claim,
                        "source": "yonerge_cift_anadal_yandal.pdf",
                        "policy_alignment": {
                            "status": "conflict",
                            "query_target_program": "double_major",
                            "conflict_programs": ["minor"],
                        },
                    },
                ],
            }
        },
    )

    result = validate_evidence_answer(
        query="CAP basvurusu icin not ortalamasi kac olmali?",
        answer="CAP basvurusu icin not ortalamasinin en az 3,00 olmasi gerekir.",
        responses=[response],
    )

    assert result.status == "pass"
    assert [claim.required_values[0].raw for claim in result.required_claims] == ["3,00"]


def test_validator_arbitrates_cap_threshold_over_minor_threshold_from_support_context():
    cap_claim = (
        "Ana dal not ortalamasinin 4,00 uzerinden en az 3,00 olmasi ve "
        "basari siralamasi itibari ile en az ilk %20'sinde bulunmasi gerekir."
    )
    minor_claim = "Not ortalamasinin 4,00 uzerinden en az 2,00 olmasi sarttir."
    policy_facet = resolve_policy_facet(
        query="CAP basvurusu icin not ortalamasi kac olmali?",
        params={"query": "CAP basvurusu icin not ortalamasi kac olmali?"},
    )
    response = DepartmentResponse(
        department=Department.STUDENT_AFFAIRS,
        answer="Kaynak bilgisi final cevap icin hazirlandi.",
        sources=[],
        metadata={
            "evidence_packet": {
                "policy_facet": policy_facet,
                "facts": [
                    {
                        "claim": cap_claim,
                        "support": "CAP'a basvurabilmesi icin " + cap_claim,
                        "source": "yonerge_cift_anadal_yandal.pdf",
                    },
                    {
                        "claim": minor_claim,
                        "support": "Yan dal programina basvurabilmek icin " + minor_claim,
                        "source": "yonerge_cift_anadal_yandal.pdf",
                    },
                ],
            }
        },
    )

    result = validate_evidence_answer(
        query="CAP basvurusu icin not ortalamasi kac olmali?",
        answer=(
            "CAP basvurusu icin ana dal not ortalamasi 4,00 uzerinden en az "
            "3,00 olmalidir; ayrica ilk %20 sarti aranir."
        ),
        responses=[response],
    )

    assert result.status == "pass"
    assert [claim.required_values[0].raw for claim in result.required_claims] == ["3,00"]
    assert result.value_arbitration["primary_values"] == ["3,00"]
    assert result.value_arbitration["conflicting_values"] == ["2,00"]


def test_validator_arbitrates_minor_threshold_when_query_targets_minor():
    cap_claim = "CAP icin ana dal not ortalamasinin 4,00 uzerinden en az 3,00 olmasi gerekir."
    minor_claim = "Yan dal programina basvurabilmek icin not ortalamasinin 4,00 uzerinden en az 2,00 olmasi sarttir."
    policy_facet = resolve_policy_facet(
        query="Yandal icin not ortalamasi kac olmali?",
        params={"query": "Yandal icin not ortalamasi kac olmali?"},
    )
    response = DepartmentResponse(
        department=Department.STUDENT_AFFAIRS,
        answer="Kaynak bilgisi final cevap icin hazirlandi.",
        sources=[],
        metadata={
            "evidence_packet": {
                "policy_facet": policy_facet,
                "facts": [
                    {"claim": cap_claim, "support": cap_claim, "source": "yonerge_cift_anadal_yandal.pdf"},
                    {"claim": minor_claim, "support": minor_claim, "source": "yonerge_cift_anadal_yandal.pdf"},
                ],
            }
        },
    )

    result = validate_evidence_answer(
        query="Yandal icin not ortalamasi kac olmali?",
        answer="Yandal icin not ortalamasinin 4,00 uzerinden en az 2,00 olmasi gerekir.",
        responses=[response],
    )

    assert result.status == "pass"
    assert [claim.required_values[0].raw for claim in result.required_claims] == ["2,00"]
    assert result.value_arbitration["primary_values"] == ["2,00"]
    assert result.value_arbitration["conflicting_values"] == ["3,00"]


def test_validator_demotes_off_topic_policy_dates_for_exemption_timing_question():
    policy_facet = resolve_policy_facet(
        query="Yatay gecisle gelen ogrenci muafiyet basvurusunu ne zaman yapmali?",
        params={"query": "Yatay gecisle gelen ogrenci muafiyet basvurusunu ne zaman yapmali?"},
    )
    response = DepartmentResponse(
        department=Department.STUDENT_AFFAIRS,
        answer="Kaynak bilgisi final cevap icin hazirlandi.",
        sources=[],
        metadata={
            "evidence_packet": {
                "policy_facet": policy_facet,
                "facts": [
                    {
                        "claim": "22.12.2023",
                        "support": (
                            "Mezunlar icin pedagojik formasyon egitimi basvuru takvimi "
                            "22.12.2023 tarihinde ilan edilmistir."
                        ),
                        "source": "mezunlar_icin_pedagojik_formasyon_egitimi.pdf",
                        "policy_alignment": {
                            "status": "match",
                            "query_target_program": "exemption_adjustment",
                            "matched_programs": ["single_exam", "exemption_adjustment", "summer_school"],
                        },
                    },
                    {
                        "claim": "12 hafta",
                        "support": "Muafiyet ve basvuru islemleri bolumunde pedagojik formasyon egitimi 12 hafta surer.",
                        "source": "mezunlar_icin_pedagojik_formasyon_egitimi.pdf",
                        "policy_alignment": {
                            "status": "match",
                            "query_target_program": "exemption_adjustment",
                            "matched_programs": ["single_exam", "exemption_adjustment", "summer_school"],
                        },
                    },
                ],
            }
        },
    )

    result = validate_evidence_answer(
        query="Yatay gecisle gelen ogrenci muafiyet basvurusunu ne zaman yapmali?",
        answer="Egitim ogretimin basladigi tarihten itibaren uc hafta icinde basvuru yapilmalidir.",
        responses=[response],
    )

    assert result.status == "pass"
    assert result.reason == "no_query_relevant_required_values"
    assert result.missing_values == ()
    assert result.value_arbitration["secondary_values"] == ["22.12", "2023", "12"]


def test_validator_demotes_horizontal_transfer_deadline_for_exemption_timing_question():
    policy_facet = resolve_policy_facet(
        query="Yatay gecisle gelen ogrenci muafiyet basvurusunu ne zaman yapmali?",
        params={"query": "Yatay gecisle gelen ogrenci muafiyet basvurusunu ne zaman yapmali?"},
    )
    primary_claim = (
        "Muafiyet ve intibak talebinde bulunan ogrenci, kayit yaptirdigi "
        "ogretim yilinin en gec 3. haftasinda basvuru yapar."
    )
    transfer_deadline = (
        "Yatay gecis basvurulari, akademik takvimde derslere baslama tarihi "
        "olarak tespit edilen tarihten en az 10 gun once bitecek sekilde belirlenir."
    )
    response = DepartmentResponse(
        department=Department.STUDENT_AFFAIRS,
        answer="Kaynak bilgisi final cevap icin hazirlandi.",
        sources=[],
        metadata={
            "evidence_packet": {
                "policy_facet": policy_facet,
                "facts": [
                    {
                        "claim": primary_claim,
                        "support": primary_claim,
                        "source": "yonerge_ders_yeterlik_muafiyet_intibak.pdf",
                    },
                    {
                        "claim": transfer_deadline,
                        "support": transfer_deadline,
                        "source": "onlisans_lisans_programlari_arasi_gecis_yonergesi.pdf",
                    },
                ],
            }
        },
    )

    result = validate_evidence_answer(
        query="Yatay gecisle gelen ogrenci muafiyet basvurusunu ne zaman yapmali?",
        answer="Kayit yaptirdigi ogretim yilinin en gec 3. haftasinda basvuru yapmalidir.",
        responses=[response],
    )

    assert result.status == "pass"
    assert [claim.required_values[0].raw for claim in result.required_claims] == ["3"]
    assert result.value_arbitration["primary_values"] == ["3"]
    assert "10" in result.value_arbitration["secondary_values"]


def test_validator_demotes_bare_international_durations_for_local_policy_question():
    response = DepartmentResponse(
        department=Department.ACADEMIC_PROGRAMS,
        answer="Kaynak bilgisi final cevap icin hazirlandi.",
        sources=[],
        metadata={
            "evidence_packet": {
                "facts": [
                    {
                        "claim": "12 ay",
                        "support": (
                            "Uluslararasi isbirlikleri protokolleri kapsaminda "
                            "muafiyet talebi olan degisim ogrencisinin en fazla 12 ay "
                            "bulunmasi esastir."
                        ),
                        "source": "uluslararasi_isbirlikleri_protokoller_kapsamindaki_ogrenci_ve_personel_degisim.pdf",
                        "policy_alignment": {
                            "status": "match",
                            "query_target_program": "exemption_adjustment",
                            "matched_programs": ["exemption_adjustment", "internship"],
                        },
                    },
                    {
                        "claim": "15 gun",
                        "support": (
                            "Uluslararasi degisim surecinde muafiyet belgeleri 15 gun "
                            "icinde teslim edilir."
                        ),
                        "source": "uluslararasi_isbirlikleri_protokoller_kapsamindaki_ogrenci_ve_personel_degisim.pdf",
                        "policy_alignment": {
                            "status": "match",
                            "query_target_program": "exemption_adjustment",
                            "matched_programs": ["exemption_adjustment", "internship"],
                        },
                    },
                ],
            }
        },
    )

    result = validate_evidence_answer(
        query="Yatay gecisle gelen ogrenci muafiyet basvurusunu ne zaman yapmali?",
        answer="Egitim ogretimin basladigi tarihten itibaren uc hafta icinde basvuru yapilmalidir.",
        responses=[response],
    )

    assert result.status == "pass"
    assert result.reason == "no_query_relevant_required_values"
    assert result.missing_values == ()
    assert result.value_arbitration["secondary_values"] == ["12", "15"]


def test_validator_arbitrates_cap_application_gpa_over_retention_gpa():
    retention_claim = (
        "Not ortalamasinin 4,00 uzerinden en az 2,00 olmasi sarttir; "
        "saglayamayan ogrencinin cift ana dal kaydi silinir."
    )
    application_claim = (
        "Ana dal not ortalamasinin 4,00 uzerinden en az 3,00 olmasi ve ana dal "
        "diploma programinin ilgili sinifinda basari siralamasi itibari ile en az ilk "
        "% 20'sinde bulunmasi gerekir."
    )
    response = DepartmentResponse(
        department=Department.STUDENT_AFFAIRS,
        answer="Kaynak bilgisi final cevap icin hazirlandi.",
        sources=[],
        metadata={
            "evidence_packet": {
                "facts": [
                    {
                        "claim": retention_claim,
                        "source": "yonerge_cift_anadal_yandal.pdf",
                        "policy_alignment": {
                            "status": "match",
                            "matched_programs": ["double_major"],
                        },
                    },
                    {
                        "claim": application_claim,
                        "source": "yonerge_cift_anadal_yandal.pdf",
                        "policy_alignment": {
                            "status": "match",
                            "matched_programs": ["double_major"],
                        },
                    },
                ],
            }
        },
    )

    result = validate_evidence_answer(
        query="Peki not ortalamasi kac olmali?",
        answer="CAP basvurusu icin not ortalamasi 4,00 uzerinden en az 3,00 olmalidir.",
        responses=[response],
    )

    assert result.status == "pass"
    assert result.value_arbitration["primary_values"] == ["3,00"]
    assert result.value_arbitration["secondary_values"] == ["2,00"]


def test_validator_does_not_require_fee_values_for_payment_process_question():
    response = DepartmentResponse(
        department=Department.STUDENT_AFFAIRS,
        answer="Kaynak bilgisi final cevap icin hazirlandi.",
        sources=[],
        metadata={
            "evidence_packet": {
                "facts": [
                    {
                        "claim": (
                            "CAP'tan mezun olabilmek icin onlisans 120 AKTS, "
                            "lisans 240 AKTS tamamlanir."
                        ),
                        "source": "cift_ana_dal_yonergesi.pdf",
                    },
                    {
                        "claim": (
                            "Alinan derslere iliskin ucretler Kanunun 46 nci "
                            "maddesine gore belirlenir."
                        ),
                        "source": "yonetmelik_onlisans_lisans_egitim_ogretim.pdf",
                    },
                ],
            }
        },
    )

    result = validate_evidence_answer(
        query="CAP basvuru sartlari neler ve harc borcumu nasil odeyebilirim?",
        answer=(
            "CAP basvurusunda harc borcunun dogrudan engel olduguna dair acik "
            "bir hukum bulamadim; odeme sureci ders kaydi/kayit yenileme "
            "kapsamindan ayrica degerlendirilmelidir."
        ),
        responses=[response],
    )

    assert result.status == "pass"
    assert result.reason == "no_query_relevant_required_values"
    assert result.missing_values == ()


def test_validator_still_requires_calendar_date_values():
    response = DepartmentResponse(
        department=Department.STUDENT_AFFAIRS,
        answer="Kaynak bilgisi final cevap icin hazirlandi.",
        sources=[
            RAGSource(
                content="Final sinavlari 03 Ocak 2026 tarihinde baslar.",
                score=0.91,
                metadata={"source": "academic_calendar"},
            )
        ],
        metadata={},
    )

    result = validate_evidence_answer(
        query="Final sinavlari ne zaman basliyor?",
        answer="Final sinavlari 03 Ocak 2026 tarihinde baslar.",
        responses=[response],
    )

    assert result.status == "pass"
    assert result.reason == "required_values_preserved"


def test_validator_contract_enforce_requires_contract_signal():
    shadow_result = validate_evidence_answer(
        query="CAP basvurusu icin not ortalamasi kac olmali?",
        answer="Kaynakta not ortalamasinin tam olarak kac olacagi net degil.",
        responses=[_cap_response()],
        mode="contract_enforce",
    )

    assert shadow_result.status == "fail"
    assert shadow_result.enforceable_by_contract is False
    assert should_enforce_validation(shadow_result) is False

    response = _cap_response()
    response.metadata["evidence_packet"]["answer_contract"] = {
        "must_answer": ["not ortalamasi kosulu"]
    }
    enforced_result = validate_evidence_answer(
        query="CAP basvurusu icin not ortalamasi kac olmali?",
        answer="Kaynakta not ortalamasinin tam olarak kac olacagi net degil.",
        responses=[response],
        mode="contract_enforce",
    )

    assert enforced_result.status == "fail"
    assert enforced_result.enforceable_by_contract is True
    assert should_enforce_validation(enforced_result) is True


def test_validator_treats_thousand_separator_equivalent():
    response = DepartmentResponse(
        department=Department.FINANCE,
        answer="Kaynak bilgisi final cevap icin hazirlandi.",
        sources=[
            RAGSource(
                content="Harc ucreti 5000 TL olarak uygulanir.",
                score=0.91,
                metadata={"source": "tuition_catalog"},
            )
        ],
        metadata={},
    )

    result = validate_evidence_answer(
        query="Harc ucreti ne kadar?",
        answer="Harc ucreti 5.000 TL.",
        responses=[response],
    )

    assert result.status == "pass"


def test_validator_does_not_require_credit_when_query_asks_akts_only():
    response = DepartmentResponse(
        department=Department.ACADEMIC_PROGRAMS,
        answer="Kaynak bilgisi final cevap icin hazirlandi.",
        sources=[
            RAGSource(
                content="BIL203 Veri Yapilari dersi 6 AKTS 4 kredi.",
                score=0.91,
                metadata={"source": "curriculum_catalog"},
            )
        ],
        metadata={},
    )

    result = validate_evidence_answer(
        query="BIL203 kac AKTS?",
        answer="BIL203 dersi 6 AKTS.",
        responses=[response],
    )

    assert result.status == "pass"


def test_validator_skips_ambiguous_multi_date_calendar_rows():
    response = DepartmentResponse(
        department=Department.STUDENT_AFFAIRS,
        answer="Kaynak bilgisi final cevap icin hazirlandi.",
        sources=[
            RAGSource(
                content="DERSLERIN BITIMI 02 Ocak 2026 22 Mayis 2026",
                score=0.91,
                metadata={"source": "academic_calendar"},
            )
        ],
        metadata={},
    )

    result = validate_evidence_answer(
        query="Bahar donemi derslerin bitimi ne zaman?",
        answer="Bahar doneminde derslerin bitimi 22 Mayis 2026.",
        responses=[response],
    )

    assert result.status == "pass"
    assert result.reason == "no_query_relevant_required_values"


def test_validator_skips_non_value_questions():
    result = validate_evidence_answer(
        query="CAP basvurusu nasil yapilir?",
        answer="CAP basvurusu akademik takvimde ilan edilen surecte yapilir.",
        responses=[_cap_response()],
    )

    assert result.status == "pass"
    assert result.reason == "query_does_not_require_value_check"


def test_validator_ignores_article_and_clause_numbers_for_gpa_question():
    claim = (
        "MADDE 3 - (1) Bu Yonergede gecen; c) CAP: Cift ana dal programini ifade eder. "
        "MADDE 5 - Ogrencinin CAP'a basvurabilmesi icin ana dal not ortalamasinin "
        "4,00 uzerinden en az 3,00 olmasi gerekir."
    )
    response = DepartmentResponse(
        department=Department.STUDENT_AFFAIRS,
        answer="Kaynak bilgisi final cevap icin hazirlandi.",
        sources=[
            RAGSource(
                content=claim,
                score=0.91,
                metadata={"source": "yonerge_cift_anadal_yandal.pdf"},
            )
        ],
        metadata={},
    )

    result = validate_evidence_answer(
        query="CAP basvurusu icin not ortalamasi kac olmali?",
        answer="CAP basvurusu icin ana dal not ortalamasinin en az 3,00 olmasi gerekir.",
        responses=[response],
    )

    missing_or_required = {
        value
        for claim_item in result.required_claims
        for value in (item.raw for item in claim_item.required_values)
    } | set(result.missing_values)
    assert result.status == "pass"
    assert "3" not in missing_or_required
    assert "1" not in missing_or_required
    assert "5" not in missing_or_required
