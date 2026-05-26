"""Tests for centralized query concept extraction."""

from src.routing.query_concepts import (
    CAPABILITY_ANNOUNCEMENT,
    CONCEPT_AKTS,
    CONCEPT_APPLICATION,
    CONCEPT_ANNOUNCEMENT,
    CONCEPT_COMPLAINT,
    CONCEPT_EXEMPTION,
    CONCEPT_GRADUATION,
    CONCEPT_HORIZONTAL_TRANSFER,
    CONCEPT_INTERNSHIP,
    CONCEPT_SINGLE_EXAM,
    CONCEPT_STUDENT_DOCUMENT,
    DOMAIN_STUDENT_AFFAIRS_ADMIN,
    extract_query_concepts,
)


def test_horizontal_transfer_exemption_application_blocks_primary_announcement():
    profile = extract_query_concepts("Yatay geçişle geldim, muafiyet başvurusu ne zaman yapılır?")

    assert profile.has(CONCEPT_HORIZONTAL_TRANSFER)
    assert profile.has(CONCEPT_EXEMPTION)
    assert profile.has(CONCEPT_APPLICATION)
    assert CAPABILITY_ANNOUNCEMENT in profile.blocked_primary_capabilities


def test_explicit_announcement_is_not_blocked():
    profile = extract_query_concepts("Güncel duyurular neler?")

    assert profile.has(CONCEPT_ANNOUNCEMENT)
    assert CAPABILITY_ANNOUNCEMENT in profile.explicit_capabilities
    assert CAPABILITY_ANNOUNCEMENT not in profile.blocked_primary_capabilities


def test_complaint_sets_student_affairs_admin_guard():
    profile = extract_query_concepts("Hocamı şikayet etmek istiyorum nasıl yapabilirim?")

    assert profile.has(CONCEPT_COMPLAINT)
    assert profile.domain_guard == DOMAIN_STUDENT_AFFAIRS_ADMIN
    assert CAPABILITY_ANNOUNCEMENT in profile.blocked_primary_capabilities


def test_akts_and_exam_markers_stay_narrow():
    akts_profile = extract_query_concepts("AKTS hesaplamasi nasil yapilir?")
    assert akts_profile.has(CONCEPT_AKTS)
    assert not akts_profile.has(CONCEPT_GRADUATION)

    assert not extract_query_concepts("Sinava giremezsem ne yaparim?").has(CONCEPT_SINGLE_EXAM)


def test_student_identity_loss_and_internship_variants_are_detected():
    assert extract_query_concepts("öğrenci kimlik kartım kayıp").has(CONCEPT_STUDENT_DOCUMENT)
    assert extract_query_concepts("zorunlu staj formunu nereden alırım").has(CONCEPT_INTERNSHIP)
