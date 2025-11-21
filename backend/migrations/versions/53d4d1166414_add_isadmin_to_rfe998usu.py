"""add isadmin to rfe998usu

Revision ID: 53d4d1166414
Revises: c964aeeb268a
Create Date: 2025-10-07 21:55:31.290139

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '53d4d1166414'
down_revision: Union[str, None] = 'c964aeeb268a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        'rfe998usu',
        sa.Column('isadmin', sa.Boolean(), nullable=False, server_default=sa.text('false'))
    )
    # remove o server_default para novas linhas herdarem do modelo
    op.alter_column('rfe998usu', 'isadmin', server_default=None)

def downgrade():
    op.drop_column('rfe998usu', 'isadmin')
