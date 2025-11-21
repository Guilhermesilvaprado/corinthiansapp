"""Add cadastros gerais, licencas e parcelamento

Revision ID: 002_add_cadastros_gerais_licencas_parcelamento
Revises: 001_create_contas_pagar_receber_tables
Create Date: 2025-11-19 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_add_cadastros_gerais_licencas_parcelamento'
down_revision = '001_create_contas_pagar_receber_tables'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Criar tabela rfe022cad (Cadastros Gerais)
    op.create_table(
        'rfe022cad',
        sa.Column('codcad', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('nomcad', sa.String(length=100), nullable=False, comment='Nome do cadastro'),
        sa.Column('tipcad', sa.String(length=20), nullable=False, comment='Tipo: FORNECEDOR, CLIENTE, USUARIO, OUTROS'),
        sa.Column('doccad', sa.String(length=18), nullable=True, comment='CPF ou CNPJ'),
        sa.Column('endcad', sa.String(length=200), nullable=True, comment='Endereço completo'),
        sa.Column('cidcad', sa.String(length=100), nullable=True, comment='Cidade'),
        sa.Column('ufcad', sa.String(length=2), nullable=True, comment='UF'),
        sa.Column('cepcad', sa.String(length=9), nullable=True, comment='CEP'),
        sa.Column('telcad', sa.String(length=20), nullable=True, comment='Telefone'),
        sa.Column('celcad', sa.String(length=20), nullable=True, comment='Celular'),
        sa.Column('emacad', sa.String(length=200), nullable=True, comment='E-mail'),
        sa.Column('statcad', sa.String(length=10), nullable=False, server_default='ATIVO', comment='Status: ATIVO, INATIVO'),
        sa.Column('obscad', sa.String(length=1000), nullable=True, comment='Observações gerais'),
        sa.Column('codemp', sa.Integer(), nullable=False, comment='Código da empresa'),
        sa.Column('codfil', sa.Integer(), nullable=False, comment='Código da filial'),
        sa.Column('datcri', sa.DateTime(), nullable=False, server_default=sa.text('now()'), comment='Data de criação'),
        sa.Column('usucri', sa.Integer(), nullable=False, comment='Usuário que criou'),
        sa.Column('datalt', sa.DateTime(), nullable=True, comment='Data da última alteração'),
        sa.Column('usualt', sa.Integer(), nullable=True, comment='Usuário que alterou'),
        sa.PrimaryKeyConstraint('codcad'),
        sa.CheckConstraint("tipcad IN ('FORNECEDOR', 'CLIENTE', 'USUARIO', 'OUTROS')", name='ck_rfe022cad_tipcad'),
        sa.CheckConstraint("statcad IN ('ATIVO', 'INATIVO')", name='ck_rfe022cad_statcad'),
    )
    
    # Índices para Cadastros Gerais
    op.create_index('idx_rfe022cad_tenant', 'rfe022cad', ['codemp', 'codfil'])
    op.create_index('idx_rfe022cad_pk_tenant', 'rfe022cad', ['codcad', 'codemp', 'codfil'])
    op.create_index('idx_rfe022cad_nome_tenant', 'rfe022cad', ['codemp', 'codfil', 'nomcad'])
    op.create_index('idx_rfe022cad_tipo_tenant', 'rfe022cad', ['codemp', 'codfil', 'tipcad'])
    op.create_index('idx_rfe022cad_status_tenant', 'rfe022cad', ['codemp', 'codfil', 'statcad'])
    op.create_index('idx_rfe022cad_documento', 'rfe022cad', ['codemp', 'codfil', 'doccad'])
    
    # 2. Criar tabela rfe023lic (Licenças)
    op.create_table(
        'rfe023lic',
        sa.Column('codlic', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('codemp', sa.Integer(), nullable=False, comment='Código da empresa licenciada'),
        sa.Column('codfil', sa.Integer(), nullable=False, comment='Código da filial licenciada'),
        sa.Column('nomlic', sa.String(length=200), nullable=False, comment='Nome da empresa/filial'),
        sa.Column('cnplic', sa.String(length=18), nullable=False, comment='CNPJ da empresa'),
        sa.Column('chavlic', sa.String(length=255), nullable=False, comment='Chave da licença'),
        sa.Column('datini', sa.Date(), nullable=False, comment='Data de início da licença'),
        sa.Column('datfim', sa.Date(), nullable=False, comment='Data de encerramento da licença'),
        sa.Column('statpag', sa.String(length=15), nullable=False, server_default='PENDENTE', comment='Status de pagamento: PENDENTE, PAGO, ATRASADO'),
        sa.Column('ativo', sa.Boolean(), nullable=False, server_default='true', comment='Licença ativa/inativa'),
        sa.Column('obslic', sa.String(length=1000), nullable=True, comment='Observações sobre a licença'),
        sa.Column('datcri', sa.DateTime(), nullable=False, server_default=sa.text('now()'), comment='Data de criação'),
        sa.Column('usucri', sa.Integer(), nullable=False, comment='Usuário que criou'),
        sa.Column('datalt', sa.DateTime(), nullable=True, comment='Data da última alteração'),
        sa.Column('usualt', sa.Integer(), nullable=True, comment='Usuário que alterou'),
        sa.PrimaryKeyConstraint('codlic'),
        sa.CheckConstraint("statpag IN ('PENDENTE', 'PAGO', 'ATRASADO')", name='ck_rfe023lic_statpag'),
    )
    
    # Índices para Licenças
    op.create_index('idx_rfe023lic_empresa', 'rfe023lic', ['codemp', 'codfil'])
    op.create_index('idx_rfe023lic_vigencia', 'rfe023lic', ['datini', 'datfim'])
    op.create_index('idx_rfe023lic_status', 'rfe023lic', ['statpag', 'ativo'])
    op.create_index('idx_rfe023lic_chave', 'rfe023lic', ['chavlic'], unique=True)
    
    # 3. Adicionar campos de parcelamento em rfe020cap (Contas a Pagar)
    op.add_column('rfe020cap', sa.Column('codgrp', sa.String(length=50), nullable=True, comment='Código do grupo de parcelamento (UUID)'))
    op.add_column('rfe020cap', sa.Column('codpai', sa.Integer(), nullable=True, comment='Código da conta pai (se for parcela)'))
    op.create_index('idx_rfe020cap_grupo_parcela', 'rfe020cap', ['codemp', 'codfil', 'codgrp'])
    
    # 4. Adicionar campos de parcelamento em rfe021car (Contas a Receber)
    op.add_column('rfe021car', sa.Column('codgrp', sa.String(length=50), nullable=True, comment='Código do grupo de parcelamento (UUID)'))
    op.add_column('rfe021car', sa.Column('codpai', sa.Integer(), nullable=True, comment='Código da conta pai (se for parcela)'))
    op.create_index('idx_rfe021car_grupo_parcela', 'rfe021car', ['codemp', 'codfil', 'codgrp'])


def downgrade():
    # Remover campos de parcelamento de Contas a Receber
    op.drop_index('idx_rfe021car_grupo_parcela', table_name='rfe021car')
    op.drop_column('rfe021car', 'codpai')
    op.drop_column('rfe021car', 'codgrp')
    
    # Remover campos de parcelamento de Contas a Pagar
    op.drop_index('idx_rfe020cap_grupo_parcela', table_name='rfe020cap')
    op.drop_column('rfe020cap', 'codpai')
    op.drop_column('rfe020cap', 'codgrp')
    
    # Remover tabela de Licenças
    op.drop_index('idx_rfe023lic_chave', table_name='rfe023lic')
    op.drop_index('idx_rfe023lic_status', table_name='rfe023lic')
    op.drop_index('idx_rfe023lic_vigencia', table_name='rfe023lic')
    op.drop_index('idx_rfe023lic_empresa', table_name='rfe023lic')
    op.drop_table('rfe023lic')
    
    # Remover tabela de Cadastros Gerais
    op.drop_index('idx_rfe022cad_documento', table_name='rfe022cad')
    op.drop_index('idx_rfe022cad_status_tenant', table_name='rfe022cad')
    op.drop_index('idx_rfe022cad_tipo_tenant', table_name='rfe022cad')
    op.drop_index('idx_rfe022cad_nome_tenant', table_name='rfe022cad')
    op.drop_index('idx_rfe022cad_pk_tenant', table_name='rfe022cad')
    op.drop_index('idx_rfe022cad_tenant', table_name='rfe022cad')
    op.drop_table('rfe022cad')
