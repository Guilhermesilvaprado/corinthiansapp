"""create contas pagar e receber tables

Revision ID: 001_contas_pagar_receber
Revises: ecc95a680360
Create Date: 2025-10-20 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_contas_pagar_receber'
down_revision: Union[str, None] = 'ecc95a680360'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ========== TABELA: CONTAS A PAGAR (rfe020cap) ==========
    op.create_table(
        'rfe020cap',
        sa.Column('codcap', sa.Integer(), nullable=False, autoincrement=True, comment='ID da conta a pagar'),
        sa.Column('codfor', sa.Integer(), nullable=False, comment='Fornecedor'),
        sa.Column('vlrcap', sa.Numeric(precision=15, scale=2), nullable=False, comment='Valor da conta'),
        sa.Column('datven', sa.Date(), nullable=False, comment='Data de vencimento'),
        sa.Column('datpag', sa.Date(), nullable=True, comment='Data de pagamento'),
        sa.Column('statcap', sa.String(length=10), nullable=False, server_default='A_PAGAR', comment='Status'),
        sa.Column('catcap', sa.String(length=100), nullable=True, comment='Categoria da despesa'),
        sa.Column('forpag', sa.String(length=50), nullable=True, comment='Forma de pagamento'),
        sa.Column('numpar', sa.Integer(), nullable=True, server_default='1', comment='Número da parcela atual'),
        sa.Column('totpar', sa.Integer(), nullable=True, server_default='1', comment='Total de parcelas'),
        sa.Column('obscap', sa.String(length=1000), nullable=True, comment='Observações'),
        sa.Column('numdoc', sa.String(length=50), nullable=True, comment='Número do documento/NF'),
        sa.Column('codemp', sa.Integer(), nullable=False, comment='Código da empresa'),
        sa.Column('codfil', sa.Integer(), nullable=False, comment='Código da filial'),
        sa.Column('datcri', sa.DateTime(), nullable=False, server_default=sa.text('now()'), comment='Data de criação'),
        sa.Column('usucri', sa.Integer(), nullable=False, comment='Usuário que criou'),
        sa.Column('datalt', sa.DateTime(), nullable=True, comment='Data da última alteração'),
        sa.Column('usualt', sa.Integer(), nullable=True, comment='Usuário que alterou'),
        
        # Primary Key
        sa.PrimaryKeyConstraint('codcap'),
        
        # Foreign Keys
        sa.ForeignKeyConstraint(['codfor'], ['rfe010pes.codpes'], ),
        
        # Check Constraints
        sa.CheckConstraint("statcap IN ('A_PAGAR', 'PAGO', 'VENCIDO', 'CANCELADO')", name='ck_rfe020cap_statcap'),
        sa.CheckConstraint('vlrcap > 0', name='ck_rfe020cap_vlrcap'),
        sa.CheckConstraint('numpar > 0', name='ck_rfe020cap_numpar'),
        sa.CheckConstraint('totpar > 0', name='ck_rfe020cap_totpar'),
        sa.CheckConstraint('numpar <= totpar', name='ck_rfe020cap_numpar_totpar'),
    )
    
    # Índices para Contas a Pagar
    op.create_index('idx_rfe020cap_tenant', 'rfe020cap', ['codemp', 'codfil'])
    op.create_index('idx_rfe020cap_pk_tenant', 'rfe020cap', ['codcap', 'codemp', 'codfil'])
    op.create_index('idx_rfe020cap_fornecedor', 'rfe020cap', ['codfor'])
    op.create_index('idx_rfe020cap_fornecedor_tenant', 'rfe020cap', ['codemp', 'codfil', 'codfor'])
    op.create_index('idx_rfe020cap_status_tenant', 'rfe020cap', ['codemp', 'codfil', 'statcap'])
    op.create_index('idx_rfe020cap_vencimento', 'rfe020cap', ['codemp', 'codfil', 'datven'])
    op.create_index('idx_rfe020cap_categoria', 'rfe020cap', ['codemp', 'codfil', 'catcap'])
    
    # ========== TABELA: CONTAS A RECEBER (rfe021car) ==========
    op.create_table(
        'rfe021car',
        sa.Column('codcar', sa.Integer(), nullable=False, autoincrement=True, comment='ID da conta a receber'),
        sa.Column('codcli', sa.Integer(), nullable=False, comment='Cliente'),
        sa.Column('vlrcar', sa.Numeric(precision=15, scale=2), nullable=False, comment='Valor da conta'),
        sa.Column('datven', sa.Date(), nullable=False, comment='Data de vencimento'),
        sa.Column('datrec', sa.Date(), nullable=True, comment='Data de recebimento'),
        sa.Column('statcar', sa.String(length=10), nullable=False, server_default='A_RECEBER', comment='Status'),
        sa.Column('catcar', sa.String(length=100), nullable=True, comment='Categoria da receita'),
        sa.Column('forrec', sa.String(length=50), nullable=True, comment='Forma de recebimento'),
        sa.Column('numpar', sa.Integer(), nullable=True, server_default='1', comment='Número da parcela atual'),
        sa.Column('totpar', sa.Integer(), nullable=True, server_default='1', comment='Total de parcelas'),
        sa.Column('obscar', sa.String(length=1000), nullable=True, comment='Observações'),
        sa.Column('numdoc', sa.String(length=50), nullable=True, comment='Número do documento/NF'),
        sa.Column('codemp', sa.Integer(), nullable=False, comment='Código da empresa'),
        sa.Column('codfil', sa.Integer(), nullable=False, comment='Código da filial'),
        sa.Column('datcri', sa.DateTime(), nullable=False, server_default=sa.text('now()'), comment='Data de criação'),
        sa.Column('usucri', sa.Integer(), nullable=False, comment='Usuário que criou'),
        sa.Column('datalt', sa.DateTime(), nullable=True, comment='Data da última alteração'),
        sa.Column('usualt', sa.Integer(), nullable=True, comment='Usuário que alterou'),
        
        # Primary Key
        sa.PrimaryKeyConstraint('codcar'),
        
        # Foreign Keys
        sa.ForeignKeyConstraint(['codcli'], ['rfe010pes.codpes'], ),
        
        # Check Constraints
        sa.CheckConstraint("statcar IN ('A_RECEBER', 'RECEBIDO', 'VENCIDO', 'CANCELADO')", name='ck_rfe021car_statcar'),
        sa.CheckConstraint('vlrcar > 0', name='ck_rfe021car_vlrcar'),
        sa.CheckConstraint('numpar > 0', name='ck_rfe021car_numpar'),
        sa.CheckConstraint('totpar > 0', name='ck_rfe021car_totpar'),
        sa.CheckConstraint('numpar <= totpar', name='ck_rfe021car_numpar_totpar'),
    )
    
    # Índices para Contas a Receber
    op.create_index('idx_rfe021car_tenant', 'rfe021car', ['codemp', 'codfil'])
    op.create_index('idx_rfe021car_pk_tenant', 'rfe021car', ['codcar', 'codemp', 'codfil'])
    op.create_index('idx_rfe021car_cliente', 'rfe021car', ['codcli'])
    op.create_index('idx_rfe021car_cliente_tenant', 'rfe021car', ['codemp', 'codfil', 'codcli'])
    op.create_index('idx_rfe021car_status_tenant', 'rfe021car', ['codemp', 'codfil', 'statcar'])
    op.create_index('idx_rfe021car_vencimento', 'rfe021car', ['codemp', 'codfil', 'datven'])
    op.create_index('idx_rfe021car_categoria', 'rfe021car', ['codemp', 'codfil', 'catcar'])


def downgrade() -> None:
    # Drop Contas a Receber
    op.drop_index('idx_rfe021car_categoria', table_name='rfe021car')
    op.drop_index('idx_rfe021car_vencimento', table_name='rfe021car')
    op.drop_index('idx_rfe021car_status_tenant', table_name='rfe021car')
    op.drop_index('idx_rfe021car_cliente_tenant', table_name='rfe021car')
    op.drop_index('idx_rfe021car_cliente', table_name='rfe021car')
    op.drop_index('idx_rfe021car_pk_tenant', table_name='rfe021car')
    op.drop_index('idx_rfe021car_tenant', table_name='rfe021car')
    op.drop_table('rfe021car')
    
    # Drop Contas a Pagar
    op.drop_index('idx_rfe020cap_categoria', table_name='rfe020cap')
    op.drop_index('idx_rfe020cap_vencimento', table_name='rfe020cap')
    op.drop_index('idx_rfe020cap_status_tenant', table_name='rfe020cap')
    op.drop_index('idx_rfe020cap_fornecedor_tenant', table_name='rfe020cap')
    op.drop_index('idx_rfe020cap_fornecedor', table_name='rfe020cap')
    op.drop_index('idx_rfe020cap_pk_tenant', table_name='rfe020cap')
    op.drop_index('idx_rfe020cap_tenant', table_name='rfe020cap')
    op.drop_table('rfe020cap')
