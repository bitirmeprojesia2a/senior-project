from src.rag.search_planner import OFF_TOPIC_PENALTY, _apply_source_relevance, _detect_query_topic


def test_detect_query_topic_normalizes_ascii_turkish_variants():
    assert _detect_query_topic("CAP basvurusu nasil yapilir?") == "çap"
    assert _detect_query_topic("Yatay gecis sartlari nelerdir?") == "yatay geçiş"


def test_apply_source_relevance_uses_normalized_query_terms():
    results = [
        {"source": "yonerge_cift_anadal_yandal.pdf", "score": 0.9, "content": "test"},
        {"source": "yonerge_yatay_gecis.pdf", "score": 0.8, "content": "test"},
    ]

    adjusted = _apply_source_relevance(results, "CAP basvurusu nasil yapilir?")

    assert adjusted[0]["score"] == 0.9
    assert adjusted[1]["score"] == round(0.8 * OFF_TOPIC_PENALTY, 4)
