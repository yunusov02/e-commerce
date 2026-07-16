"""product category set null on delete

Revision ID: edf8ca9504fd
Revises: e391600e6f42
Create Date: 2026-07-16 10:51:12.463207

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'edf8ca9504fd'
down_revision: Union[str, Sequence[str], None] = 'e391600e6f42'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


naming_convention = {
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
}


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('product', naming_convention=naming_convention) as batch_op:
        batch_op.alter_column('category_id', existing_type=sa.Integer(), nullable=True)
        batch_op.drop_constraint(batch_op.f('fk_product_category_id_category'), type_='foreignkey')
        batch_op.create_foreign_key(
            batch_op.f('fk_product_category_id_category'),
            'category', ['category_id'], ['id'], ondelete='SET NULL',
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('product', naming_convention=naming_convention) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_product_category_id_category'), type_='foreignkey')
        batch_op.create_foreign_key(
            batch_op.f('fk_product_category_id_category'),
            'category', ['category_id'], ['id'],
        )
        batch_op.alter_column('category_id', existing_type=sa.Integer(), nullable=False)
