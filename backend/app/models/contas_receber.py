# app/models/contas_receber.py
from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, Index, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from app.database import Base


class ContaReceber(Base):
    """Modelo para Contas a Receber"""
    __tablename__ = "rfe021car"

    # Campos principais
    codcar = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    codcli = Column(Integer, ForeignKey("rfe010pes.codpes"), nullable=False, index=True, comment="Cliente")
    vlrcar = Column(Numeric(15, 2), nullable=False, comment="Valor da conta")
    datven = Column(Date, nullable=False, comment="Data de vencimento")
    datrec = Column(Date, nullable=True, comment="Data de recebimento")
    statcar = Column(
        String(10), 
        nullable=False, 
        default="A_RECEBER", 
        comment="Status: A_RECEBER, RECEBIDO, VENCIDO, CANCELADO"
    )
    
    # Categoria e forma de recebimento
    catcar = Column(String(100), nullable=True, comment="Categoria da receita")
    forrec = Column(String(50), nullable=True, comment="Forma de recebimento: DINHEIRO, CARTAO, PIX, BOLETO, TRANSFERENCIA")
    
    # Parcelamento
    numpar = Column(Integer, nullable=True, default=1, comment="Número da parcela atual")
    totpar = Column(Integer, nullable=True, default=1, comment="Total de parcelas")
    codgrp = Column(String(50), nullable=True, index=True, comment="Código do grupo de parcelamento (UUID)")
    codpai = Column(Integer, nullable=True, comment="Código da conta pai (se for parcela)")
    
    # Observações e documentos
    obscar = Column(String(1000), nullable=True, comment="Observações")
    numdoc = Column(String(50), nullable=True, comment="Número do documento/nota fiscal")
    
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
            "statcar IN ('A_RECEBER', 'RECEBIDO', 'VENCIDO', 'CANCELADO')",
            name="ck_rfe021car_statcar"
        ),
        CheckConstraint("vlrcar > 0", name="ck_rfe021car_vlrcar"),
        CheckConstraint("numpar > 0", name="ck_rfe021car_numpar"),
        CheckConstraint("totpar > 0", name="ck_rfe021car_totpar"),
        CheckConstraint("numpar <= totpar", name="ck_rfe021car_numpar_totpar"),
        
        # Índices compostos para multi-tenant
        Index("idx_rfe021car_tenant", "codemp", "codfil"),
        Index("idx_rfe021car_pk_tenant", "codcar", "codemp", "codfil"),
        Index("idx_rfe021car_cliente_tenant", "codemp", "codfil", "codcli"),
        Index("idx_rfe021car_status_tenant", "codemp", "codfil", "statcar"),
        Index("idx_rfe021car_vencimento", "codemp", "codfil", "datven"),
        Index("idx_rfe021car_categoria", "codemp", "codfil", "catcar"),
        Index("idx_rfe021car_grupo_parcela", "codemp", "codfil", "codgrp"),
    )
