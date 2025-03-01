"""create category table

Revision ID: a411c3f250ff
Revises: 2a49f32bb764
Create Date: 2025-02-18 21:39:25.954110

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a411c3f250ff'
down_revision: Union[str, None] = '2a49f32bb764'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('categories',
                    sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
                    sa.Column('name', sa.String(100), nullable=False),
                    sa.Column('description', sa.String(255))
                    )


def downgrade() -> None:
    op.drop_table('categories')
