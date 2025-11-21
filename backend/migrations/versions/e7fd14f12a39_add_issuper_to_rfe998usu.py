"""add issuper to rfe998usu

Revision ID: e7fd14f12a39
Revises: drop_legacy_tables
Create Date: 2025-10-07 19:11:30.395181

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7fd14f12a39'
down_revision: Union[str, None] = 'drop_legacy_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'e7fd14f12a39'
down_revision: Union[str, None] = 'drop_legacy_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    # Adiciona a coluna com default False e NOT NULL
    op.add_column('rfe998usu', sa.Column('issuper', sa.Boolean(), nullable=False, server_default=sa.false()))
    # Opcional: remover o server_default após popular a coluna para ficar só como default do ORM
    op.alter_column('rfe998usu', 'issuper', server_default=None)

def downgrade():
    op.drop_column('rfe998usu', 'issuper')