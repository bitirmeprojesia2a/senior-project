"""Compatibility re-export module for ORM models."""

from src.db.auth_models import OTPCode, SlackStudentMapping, UserProfileContext, VerificationSession
from src.db.conversation_models import ConversationState, ConversationTurn
from src.db.finance_models import Installment, Payment, Tuition, TuitionFeeCatalog
from src.db.model_base import Base, TimestampMixin, utcnow
from src.db.scholarship_models import (
    AvailableScholarship,
    Scholarship,
    ScholarshipApplication,
)
from src.db.student_models import (
    Course,
    CoursePrerequisite,
    CourseRegistrationPeriod,
    CourseScheduleSlot,
    Student,
    StudentCourse,
)
from src.db.support_models import (
    AgentRegistry,
    AgentTask,
    Announcement,
    OfficeContact,
    QueryLog,
)

__all__ = [
    "AgentRegistry",
    "AgentTask",
    "Announcement",
    "AvailableScholarship",
    "Base",
    "ConversationState",
    "ConversationTurn",
    "Course",
    "CoursePrerequisite",
    "CourseRegistrationPeriod",
    "CourseScheduleSlot",
    "Installment",
    "OfficeContact",
    "OTPCode",
    "Payment",
    "QueryLog",
    "Scholarship",
    "ScholarshipApplication",
    "SlackStudentMapping",
    "Student",
    "StudentCourse",
    "TimestampMixin",
    "Tuition",
    "TuitionFeeCatalog",
    "UserProfileContext",
    "VerificationSession",
    "utcnow",
]
