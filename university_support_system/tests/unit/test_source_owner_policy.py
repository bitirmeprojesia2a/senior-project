from src.core.source_owner_policy import apply_source_owner_policy


def test_source_owner_policy_advisory_boosts_compatible_evidence_without_blocking():
    result = apply_source_owner_policy(
        [
            {
                "content": "Akademik takvimde derslerin bitimi 22 Mayis 2026 olarak yer alir.",
                "source": "2025_2026_genel_akademik_takvim.pdf",
                "score": 0.50,
                "metadata": {"source": "2025_2026_genel_akademik_takvim.pdf"},
            },
            {
                "content": "Fakulte etkinlik duyurusu",
                "source": "haberler",
                "score": 0.60,
                "metadata": {"record_type": "event", "title": "Etkinlik"},
            },
        ],
        {"primary": "academic_calendar"},
        mode="advisory",
    )

    assert result.should_block is False
    assert result.diagnostics["status"] == "applied"
    assert result.diagnostics["compatible_count"] == 1
    assert result.results[0]["metadata"]["source_owner_compatible"] is True
    assert result.results[0]["score"] > 0.50


def test_source_owner_policy_balanced_blocks_structured_owner_without_compatible_evidence():
    result = apply_source_owner_policy(
        [
            {
                "content": "Genel bir haber icerigi.",
                "source": "haberler",
                "score": 0.80,
                "metadata": {"record_type": "announcement", "title": "Haber"},
            }
        ],
        {"primary": "tuition_fee_catalog"},
        mode="balanced",
        min_compatible_score=0.30,
    )

    assert result.should_block is True
    assert result.diagnostics["status"] == "blocked"
    assert result.fallback_answer


def test_source_owner_policy_advisory_does_not_block_structured_owner_without_compatible_evidence():
    result = apply_source_owner_policy(
        [
            {
                "content": "Genel bir haber icerigi.",
                "source": "haberler",
                "score": 0.80,
                "metadata": {"record_type": "announcement", "title": "Haber"},
            }
        ],
        {"primary": "tuition_fee_catalog"},
        mode="advisory",
        min_compatible_score=0.30,
    )

    assert result.should_block is False
    assert result.diagnostics["status"] == "applied"
    assert result.diagnostics["compatible_count"] == 0
