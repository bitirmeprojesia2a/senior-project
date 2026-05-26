"""Geriye donuk uyumluluk icin veri sorgu facade'i."""

from src.db.curriculum_data import (
    COURSE_CODE_ALIASES,
    fetch_course_prerequisites,
    fetch_courses_by_curriculum_semester,
    fetch_courses_by_elective_group,
    fetch_courses_by_semester,
    resolve_course_code,
)
from src.db.finance_data import (
    fetch_eligible_scholarships,
    fetch_student_scholarship_snapshot,
    fetch_student_tuition_snapshot,
    fetch_tuition_fee_catalog_entry,
)
from src.db.registration_data import (
    RegistrationPeriodInfo,
    fetch_active_registration_period,
    fetch_preferred_registration_period,
)
from src.db.student_academic_data import fetch_student_academic_snapshot

__all__ = [
    "COURSE_CODE_ALIASES",
    "RegistrationPeriodInfo",
    "fetch_active_registration_period",
    "fetch_course_prerequisites",
    "fetch_courses_by_curriculum_semester",
    "fetch_courses_by_elective_group",
    "fetch_courses_by_semester",
    "fetch_eligible_scholarships",
    "fetch_preferred_registration_period",
    "fetch_student_academic_snapshot",
    "fetch_student_scholarship_snapshot",
    "fetch_student_tuition_snapshot",
    "fetch_tuition_fee_catalog_entry",
    "resolve_course_code",
]
