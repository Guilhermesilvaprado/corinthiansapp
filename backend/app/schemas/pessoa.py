from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from decimal import Decimal

# Campos básicos
class PessoaBase(BaseModel):
    tippes: Optional[str] = Field(None, max_length=8, description="Tipo de pessoa (F/J)")
    codtre: Optional[int] = None
    nompes: str = Field(..., max_length=100, description="Nome da Pessoa")
    fanpes: Optional[str] = Field(None, max_length=100, description="Nome Fantasia")
    cpfpes: Optional[str] = Field(None, max_length=18, description="CPF")
    cnppes: Optional[str] = Field(None, max_length=14, description="CNPJ")
    endpes: Optional[str] = None
    numpes: Optional[str] = None
    baipes: Optional[str] = None
    cidpes: Optional[str] = None
    estpes: Optional[str] = None
    ceppes: Optional[str] = None
    em1pes: Optional[str] = None
    em2pes: Optional[str] = None
    celpes: Optional[str] = None
    sexpes: Optional[str] = None
    sitpes: Optional[str] = None


# Para criação
class PessoaCreate(PessoaBase):
    pass


# Para atualização (aceita todos opcionais)
class PessoaUpdate(PessoaBase):
    nompes: Optional[str] = None


# Para resposta da API
class PessoaResponse(PessoaBase):
    codpes: int
    dtacad: Optional[date] = None
    dtaalt: Optional[date] = None
    pascli: Optional[str] = None

    class Config:
        from_attributes = True  # permite converter de SQLAlchemy → Pydantic