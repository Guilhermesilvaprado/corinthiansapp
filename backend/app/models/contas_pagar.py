# app/models/contas_pagar.py
from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, Index, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from app.database import Base


class ContaPagar(Base):
    """Modelo para Contas a Pagar"""
    __tablename__ = "rfe020cap"

    # Campos principais
    codcap = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    codfor = Column(Integer, ForeignKey("rfe010pes.codpes"), nullable=False, index=True, comment="Fornecedor")
    vlrcap = Column(Numeric(15, 2), nullable=False, comment="Valor da conta")
    datven = Column(Date, nullable=False, comment="Data de vencimento")
    datpag = Column(Date, nullable=True, comment="Data de pagamento")
    statcap = Column(
        String(10), 
        nullable=False, 
        default="A_PAGAR", 
        comment="Status: A_PAGAR, PAGO, VENCIDO, CANCELADO"
    )
    
    # Categoria e forma de pagamento
    catcap = Column(String(100), nullable=True, comment="Categoria da despesa")
    forpag = Column(String(50), nullable=True, comment="Forma de pagamento: DINHEIRO, CARTAO, PIX, BOLETO, TRANSFERENCIA")
    
    # Parcelamento
    numpar = Column(Integer, nullable=True, default=1, comment="Número da parcela atual")
    totpar = Column(Integer, nullable=True, default=1, comment="Total de parcelas")
    codgrp = Column(String(50), nullable=True, index=True, comment="Código do grupo de parcelamento (UUID)")
    codpai = Column(Integer, nullable=True, comment="Código da conta pai (se for parcela)")
    
    # Observações e documentos
    obscap = Column(String(1000), nullable=True, comment="Observações")
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
            "statcap IN ('A_PAGAR', 'PAGO', 'VENCIDO', 'CANCELADO')",
            name="ck_rfe020cap_statcap"
        ),
        CheckConstraint("vlrcap > 0", name="ck_rfe020cap_vlrcap"),
        CheckConstraint("numpar > 0", name="ck_rfe020cap_numpar"),
        CheckConstraint("totpar > 0", name="ck_rfe020cap_totpar"),
        CheckConstraint("numpar <= totpar", name="ck_rfe020cap_numpar_totpar"),
        
        # Índices compostos para multi-tenant
        Index("idx_rfe020cap_tenant", "codemp", "codfil"),
        Index("idx_rfe020cap_pk_tenant", "codcap", "codemp", "codfil"),
        Index("idx_rfe020cap_fornecedor_tenant", "codemp", "codfil", "codfor"),
        Index("idx_rfe020cap_status_tenant", "codemp", "codfil", "statcap"),
        Index("idx_rfe020cap_vencimento", "codemp", "codfil", "datven"),
        Index("idx_rfe020cap_categoria", "codemp", "codfil", "catcap"),
        Index("idx_rfe020cap_grupo_parcela", "codemp", "codfil", "codgrp"),
    )
