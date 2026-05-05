"""Main orchestrator query-policy tests."""

from src.orchestrators.query_policy import (
    looks_like_contact_query,
    looks_like_announcement_query,
    should_block_announcement_primary_flow,
    should_fetch_related_announcements,
)


def test_plain_course_schedule_query_is_not_announcement_short_circuit():
    assert not looks_like_announcement_query("Elektrik elektronik muhendisligi ders programi var mi?")
    assert not looks_like_announcement_query("Fizik ders programi")


def test_explicit_course_schedule_announcement_query_stays_announcement():
    assert looks_like_announcement_query("Elektrik elektronik muhendisligi ders programi duyurusu var mi?")
    assert looks_like_announcement_query("Ders programi linki olan duyuru var mi?")


def test_exam_program_query_stays_announcement_lookup():
    assert looks_like_announcement_query("Bahar donemi final sinavi programi")


def test_procedural_muafiyet_application_does_not_become_announcement_primary():
    query = "Yatay gecisle geldim, muafiyet basvurusu ne zaman yapilir?"

    assert should_block_announcement_primary_flow(query)
    assert not looks_like_announcement_query(query)
    assert not should_fetch_related_announcements(query)


def test_complaint_procedure_does_not_become_announcement_primary():
    query = "Hocami sikayet etmek istiyorum nasil yapabilirim?"

    assert should_block_announcement_primary_flow(query)
    assert not looks_like_announcement_query(query)


def test_explicit_muafiyet_announcement_query_stays_announcement_lookup():
    query = "Yatay gecis muafiyet duyurusu var mi?"

    assert not should_block_announcement_primary_flow(query)
    assert looks_like_announcement_query(query)
    assert should_fetch_related_announcements(query)


def test_incidental_announcement_context_does_not_hide_procedure_intent():
    query = "Duyurulara baktim ama CAP basvurusu nasil yapilir bulamadim, anlatir misin?"

    assert should_block_announcement_primary_flow(query)
    assert not looks_like_announcement_query(query)
    assert not should_fetch_related_announcements(query)


def test_direct_cap_announcement_lookup_stays_announcement():
    query = "CAP basvuru duyurusu var mi?"

    assert not should_block_announcement_primary_flow(query)
    assert looks_like_announcement_query(query)


def test_contact_query_tolerates_small_typo():
    assert looks_like_contact_query("Ogrenci isleri iletiism bilgisi nedir?")
