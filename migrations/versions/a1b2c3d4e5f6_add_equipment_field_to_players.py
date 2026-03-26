"""add_equipment_field_to_players

Revision ID: a1b2c3d4e5f6
Revises: 25f1dbe05a59
Create Date: 2026-03-26 18:08:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "25f1dbe05a59"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "players",
        sa.Column("equipment", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb"))
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("players", "equipment")
