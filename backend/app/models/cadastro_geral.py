# app/models/cadastro_geral.py
from sqlalchemy import Column, Integer, String, Date, DateTime, Index, CheckConstraint
from sqlalchemy.sql import func
from app.database import Base


class CadastroGeral(Base):
    """Modelo para Cadastros Gerais (Fornecedores, Clientes, Usuários, Outros)"""
    __tablename__ = "rfe022cad"

    # Campos principais
    codcad = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    nomcad = Column(String(100), nullable=False, comment="Nome do cadastro")
    tipcad = Column(
        String(20), 
        nullable=False, 
        comment="Tipo: FORNECEDOR, CLIENTE, USUARIO, OUTROS"
    )
    
    # Documento (CPF ou CNPJ)
    doccad = Column(String(18), nullable=True, comment="CPF ou CNPJ")
    
    # Endereço
    endcad = Column(String(200), nullable=True, comment="Endereço completo")
    cidcad = Column(String(100), nullable=True, comment="Cidade")
    ufcad = Column(String(2), nullable=True, comment="UF")
    cepcad = Column(String(9), nullable=True, comment="CEP")
    
    # Contato
    telcad = Column(String(20), nullable=True, comment="Telefone")
    celcad = Column(String(20), nullable=True, comment="Celular")
    emacad = Column(String(200), nullable=True, comment="E-mail")
    
    # Status
    statcad = Column(
        String(10), 
        nullable=False, 
        default="ATIVO", 
        comment="Status: ATIVO, INATIVO"
    )
    
    # Observações
    obscad = Column(String(1000), nullable=True, comment="Observações gerais")
    
    # Multi-tenant (empresa/filial)
    codemp = Column(Integer, nullable=False, index=True, comment="Código da empresa")
    codfil = Column(Integer, nullable=False, index=True, comment="Código da filial")
    
    # Campos de auditoria
    datcri = Column(DateTime, nullable=False, server_default=func.now(), comment="Data de criação")
    usucri = Column(Integer, nullable=False, comment="Usuário que criou")
    datalt = Column(DateTime, nullable=True, onupdate=func.now(), comment="Data da última alteração")
    usualt = Column(Integer, nullable=True, comment="Usuário que alterou")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "tipcad IN ('FORNECEDOR', 'CLIENTE', 'USUARIO', 'OUTROS')",
            name="ck_rfe022cad_tipcad"
        ),
        CheckConstraint(
            "statcad IN ('ATIVO', 'INATIVO')",
            name="ck_rfe022cad_statcad"
        ),
        
        # Índices compostos para multi-tenant
        Index("idx_rfe022cad_tenant", "codemp", "codfil"),
        Index("idx_rfe022cad_pk_tenant", "codcad", "codemp", "codfil"),
        Index("idx_rfe022cad_nome_tenant", "codemp", "codfil", "nomcad"),
        Index("idx_rfe022cad_tipo_tenant", "codemp", "codfil", "tipcad"),
        Index("idx_rfe022cad_status_tenant", "codemp", "codfil", "statcad"),
        Index("idx_rfe022cad_documento", "codemp", "codfil", "doccad"),
    )
