from alembic import op
import sqlalchemy as sa

# Ajuste estes valores padrão se necessário
DEFAULT_TENANT_EMP = 1
DEFAULT_TENANT_FIL = 1

revision = 'c964aeeb268a'
down_revision = 'e7fd14f12a39'
branch_labels = None
depends_on = None


def upgrade():
    # 1) Backfill: definir codemp/codfil onde estão NULL antes de tornar NOT NULL
    op.execute(f"""
        UPDATE rfe010pes
        SET codemp = COALESCE(codemp, {DEFAULT_TENANT_EMP}),
            codfil = COALESCE(codfil, {DEFAULT_TENANT_FIL})
        WHERE codemp IS NULL OR codfil IS NULL;
    """)

    # 2) Tornar NOT NULL (agora não haverá mais NULLs)
    op.alter_column('rfe010pes', 'codemp',
                    existing_type=sa.Integer(),
                    nullable=False)
    op.alter_column('rfe010pes', 'codfil',
                    existing_type=sa.Integer(),
                    nullable=False)

    # 3) Criar índices compostos para multi-tenant
    op.create_index(
        'idx_rfe010pes_tenant',
        'rfe010pes',
        ['codemp', 'codfil'],
        unique=False
    )
    op.create_index(
        'idx_rfe010pes_pk_tenant',
        'rfe010pes',
        ['codpes', 'codemp', 'codfil'],
        unique=False
    )
    op.create_index(
        'idx_rfe010pes_nome_tenant',
        'rfe010pes',
        ['codemp', 'codfil', 'nompes'],
        unique=False
    )
    op.create_index(
        'idx_rfe010pes_sit_tenant',
        'rfe010pes',
        ['codemp', 'codfil', 'sitpes'],
        unique=False
    )


def downgrade():
    op.drop_index('idx_rfe010pes_sit_tenant', table_name='rfe010pes')
    op.drop_index('idx_rfe010pes_nome_tenant', table_name='rfe010pes')
    op.drop_index('idx_rfe010pes_pk_tenant', table_name='rfe010pes')
    op.drop_index('idx_rfe010pes_tenant', table_name='rfe010pes')

    # Reverter para nullable (se desejar voltar)
    op.alter_column('rfe010pes', 'codfil',
                    existing_type=sa.Integer(),
                    nullable=True)
    op.alter_column('rfe010pes', 'codemp',
                    existing_type=sa.Integer(),
                    nullable=True)