"""Office contact access helpers."""

from __future__ import annotations

from dataclasses import dataclass
from time import monotonic
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import OperationalError, ProgrammingError

from src.core.constants import Department
from src.db.connection import get_session
from src.db.support_models import OfficeContact
import logging


logger = logging.getLogger(__name__)

_OFFICE_CONTACTS_MISSING_RECHECK_SECONDS = 300.0
_office_contacts_table_available: bool | None = None
_office_contacts_last_check_at: float = 0.0


@dataclass(frozen=True)
class OfficeContactRecord:
    """Agentlar icin sunulabilecek ofis iletisim kaydi."""

    unit_name: str
    department: str
    person_name: str | None
    title: str | None
    phone_ext: str | None
    email: str | None
    related_agents: list[str]


async def fetch_office_contacts(
    *,
    department: Department | str | None = None,
    agent_id: str | None = None,
    active_only: bool = True,
    include_generic: bool = True,
) -> list[OfficeContactRecord]:
    """Departman veya ajan bazli ofis iletisim kayitlarini getirir."""
    global _office_contacts_table_available, _office_contacts_last_check_at

    now = monotonic()
    if (
        _office_contacts_table_available is False
        and (now - _office_contacts_last_check_at) < _OFFICE_CONTACTS_MISSING_RECHECK_SECONDS
    ):
        return []

    try:
        async with get_session() as session:
            query = select(OfficeContact)
            if active_only:
                query = query.where(OfficeContact.is_active.is_(True))
            if department is not None:
                department_value = department.value if isinstance(department, Department) else department
                query = query.where(OfficeContact.department == department_value)

            result = await session.execute(query.order_by(OfficeContact.unit_name.asc(), OfficeContact.id.asc()))
            records = result.scalars().all()
            _office_contacts_table_available = True
            _office_contacts_last_check_at = now
    except (ProgrammingError, OperationalError):
        should_log = _office_contacts_table_available is not False
        _office_contacts_table_available = False
        _office_contacts_last_check_at = now
        if should_log:
            logger.warning(
                "office_contacts_table_missing_or_unavailable; contact suggestions disabled until schema is available"
            )
        return []

    filtered: list[OfficeContactRecord] = []
    for record in records:
        related_agents = list(record.related_agents or [])
        if agent_id and related_agents and agent_id not in related_agents:
            continue
        if agent_id and not related_agents and not include_generic:
            continue
        filtered.append(
            OfficeContactRecord(
                unit_name=record.unit_name,
                department=record.department,
                person_name=record.person_name,
                title=record.title,
                phone_ext=record.phone_ext,
                email=record.email,
                related_agents=related_agents,
            )
        )
    return filtered


def format_office_contact(contact: OfficeContactRecord) -> dict[str, Any]:
    """UI veya API katmani icin iletisim kaydini duzlestirir."""

    return {
        "unit_name": contact.unit_name,
        "department": contact.department,
        "person_name": contact.person_name,
        "title": contact.title,
        "phone_ext": contact.phone_ext,
        "email": contact.email,
        "related_agents": contact.related_agents,
    }
