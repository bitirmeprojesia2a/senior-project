"""Scholarship agent policy tests."""

from src.agents.finance.scholarship_agent import ScholarshipAgent


def test_international_scholarship_query_filters_unrelated_finance_sources():
    agent = ScholarshipAgent()
    results = [
        {
            "source": "kismi_zamanli_ogrenci_calistirma_yonergesi.pdf",
            "content": "Kismi zamanli calismak isteyen ogrenciler portal uzerinden basvuru yapar.",
            "score": 0.7,
        },
        {
            "source": "erasmus_hibe_sozlesmesi.pdf",
            "content": "Erasmus hareketlilik hibe odemeleri Ulusal Ajans kurallarina gore yapilir.",
            "score": 0.6,
        },
    ]

    filtered = agent._filter_results_for_answer(
        "Erasmus hibe miktari ve burs basvurusu nasil yapilir?",
        results,
    )

    assert [item["source"] for item in filtered] == ["erasmus_hibe_sozlesmesi.pdf"]


def test_regular_scholarship_query_keeps_regular_finance_sources():
    agent = ScholarshipAgent()
    results = [
        {
            "source": "kismi_zamanli_ogrenci_calistirma_yonergesi.pdf",
            "content": "Kismi zamanli calismak isteyen ogrenciler portal uzerinden basvuru yapar.",
            "score": 0.7,
        }
    ]

    filtered = agent._filter_results_for_answer("Burs basvurusu nasil yapilir?", results)

    assert filtered == results


def test_scholarship_transfer_policy_question_is_not_personal_snapshot_query():
    agent = ScholarshipAgent()

    assert agent._is_personal_query(
        "Burslu ogrenciyim ve yatay gecis yapmak istiyorum. Bursum kesilir mi?"
    ) is False
