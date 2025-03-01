"""create_some_tables

Revision ID: d216258a1d81
Revises: a411c3f250ff
Create Date: 2025-02-27 06:55:27.934973

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd216258a1d81'
down_revision: Union[str, None] = 'a411c3f250ff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('products',
                    sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
                    sa.Column('name', sa.String(100), nullable=False),
                    sa.Column('description', sa.String(255)),
                    sa.Column('quantity_in_stock', sa.Integer(), server_default='0', nullable=False),
                    sa.Column('old_price', sa.Numeric(10, 2)),
                    sa.Column('price', sa.Numeric(10, 2), nullable=False),
                    sa.Column('size', sa.Enum('S', 'M', 'L', 'XL', 'XXL', name='size_enum')),
                    sa.Column('category_id', sa.Integer(), nullable=False),
                    sa.Column('image', sa.String(255)),

                    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], name='products_category_id_fk', ondelete='CASCADE')
                    )

    op.create_table('orders',
                    sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
                    sa.Column('user_id', sa.Integer(), nullable=False),
                    sa.Column('status', sa.String(50), nullable=False),
                    sa.Column('description', sa.String(255)),
                    sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),

                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='orders_user_id_fk', ondelete='CASCADE')
                    )

    op.create_table('order_details',
                    sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
                    sa.Column('order_id', sa.Integer(), nullable=False),
                    sa.Column('product_id', sa.Integer(), nullable=False),
                    sa.Column('quantity', sa.Integer(), nullable=False),
                    sa.Column('priceEach', sa.Numeric(10, 2), nullable=False),

                    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], name='orderdetails_order_id_fk', ondelete='CASCADE'),
                    sa.ForeignKeyConstraint(['product_id'], ['products.id'], name='orderdetails_product_id_fk', ondelete='CASCADE')
                    )

    op.create_table('reviews',
                    sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
                    sa.Column('product_id', sa.Integer(), nullable=False),
                    sa.Column('user_id', sa.Integer(), nullable=False),
                    sa.Column('rating', sa.Enum('1', '2', '3', '4', '5', name='rating_enum'), nullable=False),
                    sa.Column('comment', sa.String(255)),
                    sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),

                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='reviews_user_id_fk', ondelete='CASCADE'),
                    sa.ForeignKeyConstraint(['product_id'], ['products.id'], name='reviews_product_id_fk', ondelete='CASCADE')
                    )

def downgrade() -> None:
    op.drop_constraint('products_category_id_fk', 'products', type_='foreignkey')
    op.drop_constraint('orders_user_id_fk', 'orders', type_='foreignkey')
    op.drop_constraint('orderdetails_order_id_fk', 'order_details', type_='foreignkey')
    op.drop_constraint('orderdetails_product_id_fk', 'order_details', type_='foreignkey')
    op.drop_constraint('reviews_user_id_fk', 'reviews', type_='foreignkey')
    op.drop_constraint('reviews_product_id_fk', 'reviews', type_='foreignkey')

    op.drop_table('products')
    op.drop_table('orders')
    op.drop_table('order_details')
    op.drop_table('reviews')

