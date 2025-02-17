"""init

Revision ID: 7e79e1a06798
Revises: 
Create Date: 2025-02-17 14:42:51.936069

"""
from typing import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '7e79e1a06798'
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('balance',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('event', sa.DateTime(), nullable=False),
    sa.Column('balance', sa.Numeric(), nullable=False),
    sa.Column('percentage_drop', sa.Numeric(), nullable=False),
    sa.Column('action_taken', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    schema='smart_trade_ai'
    )
    op.create_table('market',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('currency', sa.String(length=20), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('kind', sa.String(), nullable=False),
    sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    schema='smart_trade_ai'
    )
    op.create_table('trade',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('currency', sa.String(length=20), nullable=False),
    sa.Column('opened', sa.DateTime(), nullable=False),
    sa.Column('side', sa.String(length=4), nullable=False),
    sa.Column('quantity', sa.Numeric(), nullable=False),
    sa.Column('entry_price', sa.Numeric(), nullable=False),
    sa.Column('leverage', sa.Numeric(), nullable=False),
    sa.Column('stop_loss', sa.Numeric(), nullable=False),
    sa.Column('take_profit', sa.Numeric(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('exit_price', sa.Numeric(), nullable=False),
    sa.Column('pnl', sa.Numeric(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    schema='smart_trade_ai'
    )
    op.create_table('trade_recommendation',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('currency', sa.String(length=20), nullable=False),
    sa.Column('recommended', sa.DateTime(), nullable=False),
    sa.Column('recommended_action', sa.String(), nullable=False),
    sa.Column('confidence', sa.Numeric(), nullable=False),
    sa.Column('data', sa.JSON(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    schema='smart_trade_ai'
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('trade_recommendation', schema='smart_trade_ai')
    op.drop_table('trade', schema='smart_trade_ai')
    op.drop_table('market', schema='smart_trade_ai')
    op.drop_table('balance', schema='smart_trade_ai')
    # ### end Alembic commands ###
