"""create favourite and add age_gender column


Revision ID: 79b8f6f82f1d
Revises: d216258a1d81
Create Date: 2025-03-09 23:00:42.728130

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '79b8f6f82f1d'
down_revision: Union[str, None] = 'd216258a1d81'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('favourites',
                    sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
                    sa.Column('user_id', sa.Integer(), nullable=False),
                    sa.Column('product_id', sa.Integer(), nullable=False),

                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='favourites_user_id_fk', ondelete='CASCADE'),
                    sa.ForeignKeyConstraint(['product_id'], ['products.id'], name='favourites_product_id_fk', ondelete='CASCADE')
                    )

    op.add_column('products', sa.Column('age_gender', sa.Enum('Man', 'Women', 'Kids', 'Baby', name='age_gender_enum')))


def downgrade() -> None:
    op.drop_constraint('favourites_product_id_fk', 'favourites', type_='foreignkey')
    op.drop_constraint('favourites_user_id_fk', 'favourites', type_='foreignkey')
    op.drop_table('favourites')
    op.drop_column('products', 'age_gender')
