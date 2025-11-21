from sqlalchemy import Column, Integer, String, Numeric, Date, SmallInteger, Index
from sqlalchemy.sql import func
from app.database import Base

class Pessoa(Base):
    __tablename__ = "rfe010pes"

    codpes = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    tippes = Column(String(8))
    codtre = Column(Integer)
    nompes = Column(String(100), nullable=False)
    pagcom = Column(String(1), default='S')
    fanpes = Column(String(100))
    endpes = Column(String(100))
    numpes = Column(String(10))
    baipes = Column(String(50))
    cplpes = Column(String(50))
    ceppes = Column(String(9))
    tespes = Column(String(15))
    faxpes = Column(String(15))
    celpes = Column(String(16))
    recpes = Column(String(15))
    obspes = Column(String(1000))
    cpfpes = Column(String(18))
    cnppes = Column(String(14))
    nrgpes = Column(String(18))
    iespes = Column(String(16))
    estpes = Column(String(2))
    cidpes = Column(String(100))
    codibg = Column(String(10))
    sitpes = Column(String(1))
    civpes = Column(String(15))
    sexpes = Column(String(1))
    logocl = Column(String(400))
    endcob = Column(String(100))
    numcob = Column(String(10))
    baicob = Column(String(50))
    cepcob = Column(String(50))
    ufcpes = Column(String(2))
    cdcpes = Column(String(100))
    cplcob = Column(String(30))
    tipseg = Column(Integer)
    codtbp = Column(Integer)
    limcre = Column(Numeric(15, 2))
    limtit = Column(Numeric(15, 2))
    dtacad = Column(Date, server_default=func.current_date())
    dtaalt = Column(Date, onupdate=func.current_date())
    em1pes = Column(String(500))
    em2pes = Column(String(500))
    codemp = Column(Integer, nullable=False, index=True)  # 🔒 Obrigatório para multi-tenant
    codfil = Column(Integer, nullable=False, index=True)  # 🔒 Obrigatório para multi-tenant
    aliicm = Column(Numeric(15, 2))
    aliipi = Column(Numeric(15, 2))
    triicm = Column(String(1), default='S', nullable=False)
    triipi = Column(String(1))
    tripis = Column(String(1))
    tricof = Column(SmallInteger)
    codrtb = Column(Integer, default=0)
    peracr = Column(Numeric(15, 2))
    perdes = Column(Numeric(15, 2))
    perds1 = Column(Numeric(15, 2))
    perds2 = Column(Numeric(15, 2))
    perds3 = Column(Numeric(15, 2))
    codven = Column(Integer, default=0)
    percsv = Column(Numeric(15, 2))
    percpd = Column(Numeric(15, 2))
    codcpg = Column(Integer, default=0)
    codtra = Column(Integer, default=0)
    ctato1 = Column(String(40))
    ctato2 = Column(String(40))
    codusu = Column(Integer, default=0)
    usualt = Column(Integer)
    cadcel = Column(String(1), default='N', nullable=False)
    diaven = Column(Integer)
    vlrmes = Column(Numeric(15, 2))
    perate = Column(Integer, default=0)
    txtctr = Column(String(2000))
    imppes = Column(String(1))
    iniseg = Column(Date)
    finseg = Column(Date)
    pascli = Column(String(70))
    confin = Column(Integer, default=1)

    # Índices otimizados para multi-tenant
    __table_args__ = (
        # Índice composto principal para queries por tenant (NOVO - ESSENCIAL)
        Index('idx_rfe010pes_tenant', 'codemp', 'codfil'),
        
        # Índice composto para busca por PK + tenant (NOVO - ESSENCIAL)
        Index('idx_rfe010pes_pk_tenant', 'codpes', 'codemp', 'codfil'),
        
        # Índice para busca por nome dentro do tenant (NOVO - PERFORMANCE)
        Index('idx_rfe010pes_nome_tenant', 'codemp', 'codfil', 'nompes'),
        
        # Índice para busca por situação dentro do tenant (NOVO - PERFORMANCE)
        Index('idx_rfe010pes_sit_tenant', 'codemp', 'codfil', 'sitpes'),
        
        # Índices originais mantidos
        Index('i010pes_codtre', 'codtre'),
        Index('i010pes_cpfpes', 'tippes', 'codtre', 'cpfpes', 'cnppes', 'codemp', 'codfil', 'nompes', unique=True),
    )