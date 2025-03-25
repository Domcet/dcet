"""Add ip address

Revision ID: 8bb15801edc1
Revises: 259bd0080f97
Create Date: 2025-03-24 20:07:06.824064

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8bb15801edc1'
down_revision: Union[str, None] = '259bd0080f97'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('user_check_request', sa.Column('ip_address', sa.String(length=512), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    pass
