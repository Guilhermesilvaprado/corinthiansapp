# app/schemas/licenca.py
from typing import Optional, Literal
from datetime import date, datetime
from pydantic import BaseModel, Field, ConfigDict


# Status de pagamento
StatusPagamento = Literal["PENDENTE", "PAGO", "ATRASADO"]


class LicencaBase(BaseModel):
    """Schema base para Licença"""
    codemp: int = Field(..., description="Código da empresa licenciada")
    codfil: int = Field(..., description="Código da filial licenciada")
    nomlic: str = Field(..., min_length=1, max_length=200, description="Nome da empresa/filial")
    cnplic: str = Field(..., max_length=18, description="CNPJ da empresa")
    datini: date = Field(..., description="Data de início da licença")
    datfim: date = Field(..., description="Data de encerramento da licença")
    statpag: StatusPagamento = Field(default="PENDENTE", description="Status de pagamento")
    ativo: bool = Field(default=True, description="Licença ativa/inativa")
    obslic: Optional[str] = Field(None, max_length=1000, description="Observações")
    
    model_config = ConfigDict(from_attributes=True)


class LicencaCreate(LicencaBase):
    """Schema para criar Licença"""
    pass


class LicencaUpdate(BaseModel):
    """Schema para atualizar Licença"""
    nomlic: Optional[str] = Field(None, min_length=1, max_length=200)
    cnplic: Optional[str] = Field(None, max_length=18)
    datini: Optional[date] = None
    datfim: Optional[date] = None
    statpag: Optional[StatusPagamento] = None
    ativo: Optional[bool] = None
    obslic: Optional[str] = Field(None, max_length=1000)


class LicencaResponse(LicencaBase):
    """Schema de resposta para Licença"""
    codlic: int
    chavlic: str
    datcri: datetime
    usucri: int
    datalt: Optional[datetime] = None
    usualt: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


class LicencaDashboard(BaseModel):
    """Schema para dashboard de licenças"""
    total_licencas: int
    licencas_ativas: int
    licencas_inativas: int
    licencas_vencidas: int
    licencas_a_vencer_30_dias: int
    licencas_pendentes_pagamento: int
    
    model_config = ConfigDict(from_attributes=True)
