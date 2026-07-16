"""product category not null

Revision ID: 8c348cba0ed0
Revises: edf8ca9504fd
Create Date: 2026-07-16 11:12:56.988865

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8c348cba0ed0'
down_revision: Union[str, Sequence[str], None] = 'edf8ca9504fd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('product') as batch_op:
        batch_op.drop_constraint('fk_product_category_id_category', type_='foreignkey')
        batch_op.alter_column('category_id', existing_type=sa.Integer(), nullable=False)
        batch_op.create_foreign_key(
            'fk_product_category_id_category', 'category', ['category_id'], ['id']
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('product') as batch_op:
        batch_op.drop_constraint('fk_product_category_id_category', type_='foreignkey')
        batch_op.alter_column('category_id', existing_type=sa.Integer(), nullable=True)
        batch_op.create_foreign_key(
            'fk_product_category_id_category', 'category', ['category_id'], ['id'], ondelete='SET NULL'
        )
