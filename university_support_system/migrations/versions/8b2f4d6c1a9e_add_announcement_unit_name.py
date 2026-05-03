"""add announcement unit name

Revision ID: 8b2f4d6c1a9e
Revises: 7c4e2d9a1b3f
Create Date: 2026-04-17 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8b2f4d6c1a9e"
down_revision: Union[str, None] = "7c4e2d9a1b3f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("announcement_sources", sa.Column("unit_name", sa.String(length=120), nullable=True))
    op.create_index(
        "ix_announcement_sources_unit_name",
        "announcement_sources",
        ["unit_name"],
        unique=False,
    )

    op.add_column("announcements", sa.Column("unit_name", sa.String(length=120), nullable=True))
    op.create_index(
        "ix_announcements_unit_name",
        "announcements",
        ["unit_name"],
        unique=False,
    )
    op.execute(
        """
        UPDATE announcement_sources
        SET unit_name = 'Bilgisayar Muhendisligi'
        WHERE list_url = 'https://bil-muhendislik.omu.edu.tr/tr/haberler'
          AND unit_name IS NULL
        """
    )
    op.execute(
        """
        UPDATE announcements AS a
        SET unit_name = s.unit_name
        FROM announcement_sources AS s
        WHERE a.source_id = s.id
          AND a.unit_name IS NULL
          AND s.unit_name IS NOT NULL
        """
    )


def downgrade() -> None:
    op.drop_index("ix_announcements_unit_name", table_name="announcements")
    op.drop_column("announcements", "unit_name")

    op.drop_index("ix_announcement_sources_unit_name", table_name="announcement_sources")
    op.drop_column("announcement_sources", "unit_name")
