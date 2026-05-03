from src.rag.search_planner import _apply_source_relevance


def test_academic_calendar_date_query_prefers_calendar_source_over_faq():
    results = [
        {
            "source": "sık_sorulan_sorular.txt",
            "category": "uygulama",
            "score": 0.76,
            "metadata": {"file_name": "sık_sorulan_sorular.txt"},
            "content": "Sınav sonuçlarına itiraz süresi beş iş günüdür.",
        },
        {
            "source": "2025_2026_genel_akademik_takvim.pdf",
            "category": "takvimler",
            "score": 0.74,
            "metadata": {
                "file_name": "2025_2026_genel_akademik_takvim.pdf",
                "subcategory": "takvimler",
            },
            "content": "Yarıyıl Sonu Sınav Sonuçlarının İnternetten Girilmesinin Son Günü.",
        },
    ]

    ranked = _apply_source_relevance(
        results,
        "Final sınavlarının sisteme girilmesinin son günü ne zaman?",
    )

    assert ranked[0]["source"] == "2025_2026_genel_akademik_takvim.pdf"
    assert ranked[0]["score"] > ranked[1]["score"]


def test_non_calendar_query_does_not_penalize_faq_source():
    results = [
        {
            "source": "sık_sorulan_sorular.txt",
            "category": "uygulama",
            "score": 0.76,
            "metadata": {"file_name": "sık_sorulan_sorular.txt"},
            "content": "Sınav sonuçlarına itiraz süresi beş iş günüdür.",
        },
        {
            "source": "2025_2026_genel_akademik_takvim.pdf",
            "category": "takvimler",
            "score": 0.74,
            "metadata": {"file_name": "2025_2026_genel_akademik_takvim.pdf"},
            "content": "Yarıyıl Sonu Sınavları.",
        },
    ]

    ranked = _apply_source_relevance(results, "Sınav notuma nasıl itiraz ederim?")

    assert ranked[0]["source"] == "sık_sorulan_sorular.txt"
    assert ranked[0]["score"] == 0.76
