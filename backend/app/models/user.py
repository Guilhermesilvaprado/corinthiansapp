from sqlalchemy import Column, Integer, String, Boolean, CheckConstraint
from app.database import Base


class User(Base):
    __tablename__ = "rfe998usu"

    codusu = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nomusu = Column(String(100), nullable=False)
    logusu = Column(String(100), unique=True, index=True)
    pwdusu = Column(String(255), nullable=True)
    emausu = Column(String(200), nullable=True)
    situsu = Column(String(8), nullable=True, server_default="ATIVO")  # default explícito
    setusu = Column(Integer, nullable=True)

    codemp = Column(Integer, nullable=False)
    codfil = Column(Integer, nullable=False)
    codpes = Column(Integer, nullable=False, default=0)
    issuper = Column(Boolean, nullable=False, default=False)
    isadmin = Column(Boolean, nullable=False, default=False)

    __table_args__ = (
        CheckConstraint("situsu IN ('ATIVO', 'INATIVO')", name="ck_rfe998usu_situsu"),
    )