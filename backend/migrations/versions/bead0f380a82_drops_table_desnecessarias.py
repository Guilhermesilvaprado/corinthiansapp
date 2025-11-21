"""Drop legacy tables: companies, user_companies, nota_fiscal

Revision ID: drop_legacy_tables
Revises: [sua_ultima_revisao]
Create Date: 2025-01-27 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = 'drop_legacy_tables'
down_revision = 'ecc95a680360'  # ⚠️ AJUSTE para sua última revisão aplicada
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    insp = Inspector.from_engine(bind)

    print("🧹 Limpando tabelas legadas...")

    # 1) Drop tabela de associação primeiro
    if insp.has_table("user_companies"):
        op.drop_table("user_companies")
        print("✅ Dropped table: user_companies")

    # 2) Drop tabelas de notas que dependem de companies
    # 2a) notas_fiscais (plural)
    if insp.has_table("notas_fiscais"):
        # Se quiser garantir remoção do FK explicitamente (não é necessário ao dropar a tabela):
        # op.drop_constraint("notas_fiscais_empresa_id_fkey", "notas_fiscais", type_="foreignkey")
        op.drop_table("notas_fiscais")
        print("✅ Dropped table: notas_fiscais")

    # 2b) nota_fiscal (singular) — caso exista em algum ambiente
    if insp.has_table("nota_fiscal"):
        op.drop_table("nota_fiscal")
        print("✅ Dropped table: nota_fiscal")

    # 3) Agora pode dropar companies
    if insp.has_table("companies"):
        op.drop_table("companies")
        print("✅ Dropped table: companies")

    print("🎉 Limpeza concluída! Agora usando arquitetura multi-tenant com codemp/codfil")


def downgrade():
    """Recria estruturas mínimas caso precise reverter (opcional)"""
    print("⚠️ Revertendo para estruturas legadas...")

    # Recriar companies
    op.create_table(
        'companies',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('cnpj', sa.String(length=18), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.func.now()),
        sa.UniqueConstraint('cnpj', name='uq_companies_cnpj')
    )

    # Recriar user_companies (associação)
    op.create_table(
        'user_companies',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(
            ['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'company_id')
    )

    # Recriar nota_fiscal (estrutura básica)
    op.create_table(
        'nota_fiscal',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('numero', sa.String(length=20), nullable=False),
        sa.Column('serie', sa.String(length=10), nullable=False),
        sa.Column('valor_total', sa.Numeric(
            precision=15, scale=2), nullable=False),
        sa.Column('empresa_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ['empresa_id'], ['companies.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('numero', 'serie', 'empresa_id',
                            name='uq_nota_numero_serie_empresa')
    )

    print("✅ Estruturas legadas recriadas")
