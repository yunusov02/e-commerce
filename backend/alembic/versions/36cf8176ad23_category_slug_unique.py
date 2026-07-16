"""category slug unique

Revision ID: 36cf8176ad23
Revises: 747a6d748fa7
Create Date: 2026-07-16 09:07:00.549490

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '36cf8176ad23'
down_revision: Union[str, Sequence[str], None] = '747a6d748fa7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('category') as batch_op:
        batch_op.create_unique_constraint('uq_category_slug', ['slug'])


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('category') as batch_op:
        batch_op.drop_constraint('uq_category_slug', type_='unique')
