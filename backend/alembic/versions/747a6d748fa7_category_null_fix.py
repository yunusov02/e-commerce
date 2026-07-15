"""category null fix

Revision ID: 747a6d748fa7
Revises: af8d17bd8cd3
Create Date: 2026-07-15 15:35:51.249051

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '747a6d748fa7'
down_revision: Union[str, Sequence[str], None] = 'af8d17bd8cd3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
