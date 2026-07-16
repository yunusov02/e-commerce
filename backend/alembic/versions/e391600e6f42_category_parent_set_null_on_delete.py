"""category parent set null on delete

Revision ID: e391600e6f42
Revises: 36cf8176ad23
Create Date: 2026-07-16 10:44:09.070106

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e391600e6f42'
down_revision: Union[str, Sequence[str], None] = '36cf8176ad23'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


naming_convention = {
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
}


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('category', naming_convention=naming_convention) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_category_parent_id_category'), type_='foreignkey')
        batch_op.create_foreign_key(
            batch_op.f('fk_category_parent_id_category'),
            'category', ['parent_id'], ['id'], ondelete='SET NULL',
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('category', naming_convention=naming_convention) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_category_parent_id_category'), type_='foreignkey')
        batch_op.create_foreign_key(
            batch_op.f('fk_category_parent_id_category'),
            'category', ['parent_id'], ['id'],
        )
