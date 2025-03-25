"""Add ip address

Revision ID: 259bd0080f97
Revises: a0a0f426ec2c
Create Date: 2025-03-24 20:04:06.130164

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '259bd0080f97'
down_revision: Union[str, None] = 'a0a0f426ec2c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
