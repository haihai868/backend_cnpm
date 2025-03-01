"""first create

Revision ID: 2a49f32bb764
Revises: 
Create Date: 2025-02-17 22:55:11.392841

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2a49f32bb764'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('users',
                    sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
                    sa.Column('email', sa.String(255), nullable=False, unique=True),
                    sa.Column('password', sa.String(100), nullable=False),
                    sa.Column('fullname', sa.String(100), nullable=False)
                    )

    op.create_table('notifications',
                    sa.Column('id', sa.Integer(), primary_key=True),
                    sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
                    sa.Column('title', sa.String(255), nullable=False),
                    sa.Column('message', sa.String(255), nullable=False),
                    sa.Column('is_read', sa.Boolean(), server_default=sa.false()),
                    sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
                    )

def downgrade() -> None:
    op.drop_table('users')
    op.drop_table('notifications')
