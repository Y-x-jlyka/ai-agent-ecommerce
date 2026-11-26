"""add message role index

Revision ID: 50ea5de30cfb
Revises: 8a3ca872f907
Create Date: 2026-10-13 20:35:02.362066

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '50ea5de30cfb'
down_revision: Union[str, Sequence[str], None] = '8a3ca872f907'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(
        "ix_messages_role",
    "message",
    ["role"],
    upgrade=False)



def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "ix_messages_role",
        table_name="messages"
    )
