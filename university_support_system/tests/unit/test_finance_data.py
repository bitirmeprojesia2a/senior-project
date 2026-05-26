"""Finance data fallback tests."""

from __future__ import annotations

from src.db.finance_data import _load_tuition_catalog_fallback


def test_tuition_catalog_fallback_finds_dis_hekimligi_in_metadata():
    entry = _load_tuition_catalog_fallback(
        normalized_type="international",
        normalized_unit="dis hekimligi fakultesi",
    )

    assert entry is not None
    assert entry["student_type"] == "international"
    assert entry["normalized_unit_name"] == "dis hekimligi fakultesi"
    assert entry["annual_amount"] == 203000.0

