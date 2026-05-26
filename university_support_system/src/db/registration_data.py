"""Kayit donemi odakli veri sorgulari."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import desc, select

from src.db.connection import get_session
from src.db.student_models import CourseRegistrationPeriod


@dataclass(frozen=True)
class RegistrationPeriodInfo:
    """Aktif veya tercih edilen kayit donemi bilgisi."""

    semester: str
    start_date: datetime
    end_date: datetime
    is_active: bool
    timing_status: str


def _to_registration_period_info(period: CourseRegistrationPeriod) -> RegistrationPeriodInfo:
    """ORM modelini zaman durumuyla birlikte tasinabilir dataclass'e cevirir."""
    tz = period.start_date.tzinfo or timezone.utc
    now = datetime.now(tz)
    if period.start_date <= now <= period.end_date:
        timing_status = "active"
    elif now < period.start_date:
        timing_status = "upcoming"
    else:
        timing_status = "past"

    return RegistrationPeriodInfo(
        semester=period.semester,
        start_date=period.start_date,
        end_date=period.end_date,
        is_active=bool(period.is_active),
        timing_status=timing_status,
    )


async def fetch_active_registration_period() -> RegistrationPeriodInfo | None:
    """Aktif kayit donemini getirir. Yoksa None doner."""
    async with get_session() as session:
        stmt = (
            select(CourseRegistrationPeriod)
            .where(CourseRegistrationPeriod.is_active.is_(True))
            .order_by(desc(CourseRegistrationPeriod.id))
            .limit(1)
        )
        period = (await session.execute(stmt)).scalar_one_or_none()
        if period is None:
            return None

        return _to_registration_period_info(period)


async def fetch_preferred_registration_period() -> RegistrationPeriodInfo | None:
    """Cevaplarda kullanilacak en uygun kayit donemini getirir."""
    async with get_session() as session:
        now = datetime.now(timezone.utc)

        current_stmt = (
            select(CourseRegistrationPeriod)
            .where(
                CourseRegistrationPeriod.start_date <= now,
                CourseRegistrationPeriod.end_date >= now,
            )
            .order_by(desc(CourseRegistrationPeriod.start_date))
            .limit(1)
        )
        period = (await session.execute(current_stmt)).scalar_one_or_none()
        if period is not None:
            return _to_registration_period_info(period)

        upcoming_stmt = (
            select(CourseRegistrationPeriod)
            .where(CourseRegistrationPeriod.start_date >= now)
            .order_by(CourseRegistrationPeriod.start_date.asc())
            .limit(1)
        )
        period = (await session.execute(upcoming_stmt)).scalar_one_or_none()
        if period is not None:
            return _to_registration_period_info(period)

        active_stmt = (
            select(CourseRegistrationPeriod)
            .where(CourseRegistrationPeriod.is_active.is_(True))
            .order_by(desc(CourseRegistrationPeriod.id))
            .limit(1)
        )
        period = (await session.execute(active_stmt)).scalar_one_or_none()
        if period is not None:
            return _to_registration_period_info(period)

        latest_stmt = (
            select(CourseRegistrationPeriod)
            .order_by(desc(CourseRegistrationPeriod.start_date), desc(CourseRegistrationPeriod.id))
            .limit(1)
        )
        period = (await session.execute(latest_stmt)).scalar_one_or_none()
        if period is None:
            return None

        return _to_registration_period_info(period)
