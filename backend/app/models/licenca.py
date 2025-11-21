# app/models/licenca.py
from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, Index, CheckConstraint
from sqlalchemy.sql import func
from app.database import Base
import secrets
import hashlib


class Licenca(Base):
    """Modelo para Gestão de Licenças (SuperAdmin only)"""
    __tablename__ = "rfe023lic"

    # Campos principais
    codlic = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    
    # Identificação da empresa/filial licenciada
    codemp = Column(Integer, nullable=False, index=True, comment="Código da empresa licenciada")
    codfil = Column(Integer, nullable=False, index=True, comment="Código da filial licenciada")
    nomlic = Column(String(200), nullable=False, comment="Nome da empresa/filial")
    cnplic = Column(String(18), nullable=False, comment="CNPJ da empresa")
    
    # Chave de licença (hash único e seguro)
    chavlic = Column(String(255), nullable=False, unique=True, index=True, comment="Chave da licença")
    
    # Período de vigência
    datini = Column(Date, nullable=False, comment="Data de início da licença")
    datfim = Column(Date, nullable=False, comment="Data de encerramento da licença")
    
    # Status de pagamento e ativação
    statpag = Column(
        String(15), 
        nullable=False, 
        default="PENDENTE", 
        comment="Status de pagamento: PENDENTE, PAGO, ATRASADO"
    )
    ativo = Column(Boolean, nullable=False, default=True, comment="Licença ativa/inativa")
    
    # Observações
    obslic = Column(String(1000), nullable=True, comment="Observações sobre a licença")
    
    # Campos de auditoria
    datcri = Column(DateTime, nullable=False, server_default=func.now(), comment="Data de criação")
    usucri = Column(Integer, nullable=False, comment="Usuário que criou")
    datalt = Column(DateTime, nullable=True, onupdate=func.now(), comment="Data da última alteração")
    usualt = Column(Integer, nullable=True, comment="Usuário que alterou")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "statpag IN ('PENDENTE', 'PAGO', 'ATRASADO')",
            name="ck_rfe023lic_statpag"
        ),
        
        # Índices
        Index("idx_rfe023lic_empresa", "codemp", "codfil"),
        Index("idx_rfe023lic_vigencia", "datini", "datfim"),
        Index("idx_rfe023lic_status", "statpag", "ativo"),
    )
    
    @staticmethod
    def gerar_chave_licenca(codemp: int, codfil: int, cnpj: str) -> str:
        """
        Gera uma chave de licença única e segura
        Formato: HASH-SHA256 baseado em empresa, filial, CNPJ e token aleatório
        """
        # Gera token aleatório de 16 bytes
        token_aleatorio = secrets.token_hex(16)
        
        # Combina dados da empresa com token aleatório
        dados = f"{codemp}-{codfil}-{cnpj}-{token_aleatorio}"
        
        # Gera hash SHA256
        hash_obj = hashlib.sha256(dados.encode())
        chave = hash_obj.hexdigest()
        
        # Formata a chave em blocos de 8 caracteres para melhor legibilidade
        # Exemplo: ABCD1234-5678EFGH-IJKL9012-MNOP3456
        chave_formatada = "-".join([chave[i:i+8].upper() for i in range(0, 32, 8)])
        
        return chave_formatada
