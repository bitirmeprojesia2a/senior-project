from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from src.db.curriculum_seed import (
    SHARED_SOCIAL_ELECTIVE_DEPARTMENT,
    load_curriculum_payload,
    seed_curriculum_records,
)
from src.db.model_base import Base
from src.db.student_models import Course, CoursePrerequisite, Student, StudentCourse


def _make_session() -> Session:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(
        engine,
        tables=[
            Student.__table__,
            Course.__table__,
            CoursePrerequisite.__table__,
            StudentCourse.__table__,
        ],
    )
    return Session(engine)


def test_load_curriculum_payload_defaults_department_and_normalizes_codes():
    payload_path = (
        Path(__file__).resolve().parents[1]
        / "fixtures"
        / "curriculum_seed_sample.json"
    )

    payload = load_curriculum_payload(payload_path)

    assert payload["courses"][0]["course_code"] == "TST101"
    assert payload["courses"][0]["department"] == "Test Bolum"
    assert payload["prerequisites"][0]["course_code"] == "TST201"
    assert payload["prerequisites"][0]["prerequisites"][0]["course_code"] == "TST101"


def test_load_curriculum_payload_normalizes_turkish_course_code_letters():
    payload = load_curriculum_payload(
        Path(__file__).resolve().parents[1]
        / "fixtures"
        / "curriculum_seed_sample.json"
    )
    payload["courses"][0]["course_code"] = "BİL101"
    session = _make_session()

    result = seed_curriculum_records(
        session,
        courses=[payload["courses"][0]],
        prerequisites=[],
        managed_prerequisite_course_codes=[],
    )
    course_codes = session.scalars(select(Course.course_code)).all()

    assert result.processed_courses == 1
    assert course_codes == ["BIL101"]


def test_seed_curriculum_records_only_cleans_managed_course_prerequisites():
    session = _make_session()

    other_a = Course(course_code="OTH101", course_name="Other A", department="Other", credits=3)
    other_b = Course(course_code="OTH201", course_name="Other B", department="Other", credits=3)
    session.add_all([other_a, other_b])
    session.flush()
    session.add(
        CoursePrerequisite(
            course_id=other_b.id,
            prerequisite_id=other_a.id,
            prerequisite_group=1,
        )
    )
    session.commit()

    result = seed_curriculum_records(
        session,
        courses=[
            {
                "course_code": "TST101",
                "course_name": "Temel Ders",
                "department": "Test Bolum",
                "theory_hours": 3,
                "practice_hours": 0,
                "lab_hours": 0,
                "credits": 3,
                "akts": 5,
                "curriculum_semester": 1,
                "course_type": "zorunlu",
                "elective_group": None,
            },
            {
                "course_code": "TST201",
                "course_name": "Ileri Ders",
                "department": "Test Bolum",
                "theory_hours": 3,
                "practice_hours": 0,
                "lab_hours": 0,
                "credits": 3,
                "akts": 5,
                "curriculum_semester": 2,
                "course_type": "zorunlu",
                "elective_group": None,
            },
        ],
        prerequisites=[
            {
                "course_code": "TST201",
                "prerequisites": [{"course_code": "TST101", "group": 1}],
            }
        ],
    )
    session.commit()

    prereq_pairs = session.execute(
        select(CoursePrerequisite.course_id, CoursePrerequisite.prerequisite_id)
    ).all()
    course_codes = {
        course_id: course_code
        for course_id, course_code in session.execute(
            select(Course.id, Course.course_code)
        ).all()
    }
    resolved_pairs = {(course_codes[cid], course_codes[pid]) for cid, pid in prereq_pairs}

    assert result.processed_courses == 2
    assert result.inserted_prerequisites == 1
    assert ("OTH201", "OTH101") in resolved_pairs
    assert ("TST201", "TST101") in resolved_pairs


def test_load_curriculum_payload_canonicalizes_shared_social_electives():
    payload_path = (
        Path(__file__).resolve().parents[1]
        / "fixtures"
        / "curriculum_social_seed_sample.json"
    )
    payload = load_curriculum_payload(payload_path)

    assert payload["courses"][0]["course_type"] == "sosyal_secmeli"
    assert payload["courses"][0]["department"] == SHARED_SOCIAL_ELECTIVE_DEPARTMENT
    assert payload["courses"][0]["curriculum_semester"] is None
    assert payload["courses"][1]["course_code"] == "EEM-SOS-1"
    assert payload["courses"][1]["course_type"] == "secmeli_grup"
    assert payload["courses"][1]["department"] == "Elektrik-Elektronik Muhendisligi"


def test_seed_curriculum_records_keeps_shared_social_electives_canonical():
    session = _make_session()

    first_result = seed_curriculum_records(
        session,
        courses=[
            {
                "course_code": "SOS101",
                "course_name": "Toplumsal Duyarlilik",
                "department": "Elektrik-Elektronik Muhendisligi",
                "credits": 2,
                "akts": 3,
                "curriculum_semester": 3,
                "course_type": "universite_secmeli",
            }
        ],
        prerequisites=[],
    )
    second_result = seed_curriculum_records(
        session,
        courses=[
            {
                "course_code": "SOS101",
                "course_name": "Toplumsal Duyarlilik",
                "department": "Fizik",
                "credits": 2,
                "akts": 3,
                "curriculum_semester": 5,
                "course_type": "sosyal_secmeli",
            }
        ],
        prerequisites=[],
    )
    session.commit()

    rows = session.execute(
        select(Course.course_code, Course.department, Course.course_type)
        .where(Course.course_code == "SOS101")
    ).all()

    assert first_result.processed_courses == 1
    assert second_result.processed_courses == 1
    assert rows == [("SOS101", SHARED_SOCIAL_ELECTIVE_DEPARTMENT, "sosyal_secmeli")]


def test_seed_curriculum_records_supports_department_specific_program_slots():
    session = _make_session()

    result = seed_curriculum_records(
        session,
        courses=load_curriculum_payload(
            Path(__file__).resolve().parents[1]
            / "fixtures"
            / "curriculum_social_seed_sample.json"
        )["courses"],
        prerequisites=[],
    )
    session.commit()

    rows = session.execute(
        select(
            Course.course_code,
            Course.department,
            Course.course_type,
            Course.curriculum_semester,
            Course.elective_group,
        ).order_by(Course.course_code)
    ).all()

    assert result.processed_courses == 2
    assert rows == [
        ("EEM-SOS-1", "Elektrik-Elektronik Muhendisligi", "secmeli_grup", 5, "SOSYAL-SEC"),
        ("SOS101", SHARED_SOCIAL_ELECTIVE_DEPARTMENT, "sosyal_secmeli", None, None),
    ]


def test_seed_curriculum_records_can_refresh_prerequisites_for_subset_only():
    session = _make_session()

    base = seed_curriculum_records(
        session,
        courses=[
            {
                "course_code": "AAA101",
                "course_name": "A",
                "department": "Test",
                "credits": 3,
                "akts": 5,
                "curriculum_semester": 1,
                "course_type": "zorunlu",
            },
            {
                "course_code": "AAA201",
                "course_name": "B",
                "department": "Test",
                "credits": 3,
                "akts": 5,
                "curriculum_semester": 2,
                "course_type": "zorunlu",
            },
            {
                "course_code": "AAA301",
                "course_name": "C",
                "department": "Test",
                "credits": 3,
                "akts": 5,
                "curriculum_semester": 3,
                "course_type": "zorunlu",
            },
        ],
        prerequisites=[
            {"course_code": "AAA201", "prerequisites": [{"course_code": "AAA101", "group": 1}]},
            {"course_code": "AAA301", "prerequisites": [{"course_code": "AAA201", "group": 1}]},
        ],
    )
    assert base.inserted_prerequisites == 2

    subset = seed_curriculum_records(
        session,
        courses=[
            {
                "course_code": "AAA101",
                "course_name": "A",
                "department": "Test",
                "credits": 3,
                "akts": 5,
                "curriculum_semester": 1,
                "course_type": "zorunlu",
            },
            {
                "course_code": "AAA201",
                "course_name": "B",
                "department": "Test",
                "credits": 3,
                "akts": 5,
                "curriculum_semester": 2,
                "course_type": "zorunlu",
            },
        ],
        prerequisites=[
            {"course_code": "AAA201", "prerequisites": [{"course_code": "AAA101", "group": 1}]},
        ],
        managed_prerequisite_course_codes=["AAA201"],
    )
    session.commit()

    rows = session.execute(
        select(CoursePrerequisite.course_id, CoursePrerequisite.prerequisite_id)
    ).all()
    course_codes = {
        course_id: course_code
        for course_id, course_code in session.execute(
            select(Course.id, Course.course_code)
        ).all()
    }
    resolved_pairs = {(course_codes[cid], course_codes[pid]) for cid, pid in rows}

    assert subset.deleted_prerequisites == 1
    assert ("AAA201", "AAA101") in resolved_pairs
    assert ("AAA301", "AAA201") in resolved_pairs


def test_seed_curriculum_records_can_skip_prerequisite_cleanup_with_empty_scope():
    session = _make_session()

    base = seed_curriculum_records(
        session,
        courses=[
            {
                "course_code": "AAA101",
                "course_name": "A",
                "department": "Test",
                "credits": 3,
                "akts": 5,
                "curriculum_semester": 1,
                "course_type": "zorunlu",
            },
            {
                "course_code": "AAA201",
                "course_name": "B",
                "department": "Test",
                "credits": 3,
                "akts": 5,
                "curriculum_semester": 2,
                "course_type": "zorunlu",
            },
        ],
        prerequisites=[
            {"course_code": "AAA201", "prerequisites": [{"course_code": "AAA101", "group": 1}]},
        ],
    )
    assert base.inserted_prerequisites == 1

    courses_only = seed_curriculum_records(
        session,
        courses=[
            {
                "course_code": "AAA201",
                "course_name": "B Updated",
                "department": "Test",
                "credits": 4,
                "akts": 6,
                "curriculum_semester": 2,
                "course_type": "zorunlu",
            }
        ],
        prerequisites=[],
        managed_prerequisite_course_codes=[],
    )
    session.commit()

    prereq_count = session.scalar(select(func.count()).select_from(CoursePrerequisite))
    updated = session.scalar(select(Course).where(Course.course_code == "AAA201"))

    assert courses_only.deleted_prerequisites == 0
    assert courses_only.inserted_prerequisites == 0
    assert prereq_count == 1
    assert updated is not None
    assert updated.course_name == "B Updated"
    assert updated.akts == 6


def test_seed_curriculum_records_can_match_missing_prerequisite_by_name():
    session = _make_session()

    result = seed_curriculum_records(
        session,
        courses=[
            {
                "course_code": "EEM217",
                "course_name": "Devre Kuramı",
                "department": "EEM",
                "credits": 4,
                "akts": 6,
                "curriculum_semester": 3,
                "course_type": "zorunlu",
            },
            {
                "course_code": "EEM214",
                "course_name": "Elektronik II",
                "department": "EEM",
                "credits": 4,
                "akts": 6,
                "curriculum_semester": 4,
                "course_type": "zorunlu",
            },
        ],
        prerequisites=[
            {
                "course_code": "EEM214",
                "prerequisites": [
                    {"course_code": "EEM212", "course_name": "Devre Kuramı", "group": 1}
                ],
            }
        ],
    )
    session.commit()

    rows = session.execute(
        select(CoursePrerequisite.course_id, CoursePrerequisite.prerequisite_id)
    ).all()
    course_codes = {
        course_id: course_code
        for course_id, course_code in session.execute(
            select(Course.id, Course.course_code)
        ).all()
    }
    resolved_pairs = {(course_codes[cid], course_codes[pid]) for cid, pid in rows}

    assert result.inserted_prerequisites == 1
    assert not result.missing_prerequisites
    assert ("EEM214", "EEM217") in resolved_pairs
