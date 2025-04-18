"""fix metadata import

Revision ID: 807141ae837c
Revises: 4ad253adeaa6
Create Date: 2025-03-12 20:51:15.129119

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '807141ae837c'
down_revision: Union[str, None] = '4ad253adeaa6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bitrix_apartment',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('apartment_id', sa.String(length=255), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('contact', sa.String(length=255), nullable=True),
    sa.Column('apartment_balance', sa.Float(), nullable=True),
    sa.Column('tariff', sa.String(length=255), nullable=True),
    sa.Column('accrual', sa.String(length=255), nullable=True),
    sa.Column('privilege', sa.String(length=255), nullable=True),
    sa.Column('was_accrual_performed', sa.String(length=255), nullable=True),
    sa.Column('microdistrict', sa.String(length=255), nullable=False),
    sa.Column('house', sa.String(length=255), nullable=False),
    sa.Column('apartment', sa.String(length=255), nullable=False),
    sa.Column('personal_account', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('apartment_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('bitrix_apartment')
    # ### end Alembic commands ###
