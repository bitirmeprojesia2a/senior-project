"""Office contact access helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import select

from src.core.constants import Department
from src.db.connection import get_session
from src.db.support_models import OfficeContact


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
) -> list[OfficeContactRecord]:
    """Departman veya ajan bazli ofis iletisim kayitlarini getirir."""

    async with get_session() as session:
        query = select(OfficeContact)
        if active_only:
            query = query.where(OfficeContact.is_active.is_(True))
        if department is not None:
            department_value = department.value if isinstance(department, Department) else department
            query = query.where(OfficeContact.department == department_value)

        result = await session.execute(query.order_by(OfficeContact.unit_name.asc(), OfficeContact.id.asc()))
        records = result.scalars().all()

    filtered: list[OfficeContactRecord] = []
    for record in records:
        related_agents = list(record.related_agents or [])
        if agent_id and related_agents and agent_id not in related_agents:
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
