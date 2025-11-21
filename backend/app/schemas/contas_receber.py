# app/schemas/contas_receber.py
from typing import Optional, Literal
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict, field_validator


# Status possíveis para Conta a Receber
StatusContaReceber = Literal["A_RECEBER", "RECEBIDO", "VENCIDO", "CANCELADO"]


class ContaReceberBase(BaseModel):
    """Schema base para Conta a Receber"""
    codcli: int = Field(..., description="Código do cliente")
    vlrcar: Decimal = Field(..., gt=0, description="Valor da conta")
    datven: date = Field(..., description="Data de vencimento")
    datrec: Optional[date] = Field(None, description="Data de recebimento")
    statcar: StatusContaReceber = Field(default="A_RECEBER", description="Status da conta")
    catcar: Optional[str] = Field(None, max_length=100, description="Categoria da receita")
    forrec: Optional[str] = Field(None, max_length=50, description="Forma de recebimento")
    numpar: int = Field(default=1, gt=0, description="Número da parcela atual")
    totpar: int = Field(default=1, gt=0, description="Total de parcelas")
    codgrp: Optional[str] = Field(None, max_length=50, description="Código do grupo de parcelamento")
    codpai: Optional[int] = Field(None, description="Código da conta pai")
    obscar: Optional[str] = Field(None, max_length=1000, description="Observações")
    numdoc: Optional[str] = Field(None, max_length=50, description="Número do documento/NF")
    
    model_config = ConfigDict(from_attributes=True)
    
    @field_validator("numpar", "totpar")
    @classmethod
    def validate_parcelas(cls, v):
        if v < 1:
            raise ValueError("Número de parcelas deve ser maior que zero")
        return v


class ContaReceberCreate(ContaReceberBase):
    """Schema para criar Conta a Receber"""
    pass


class ContaReceberUpdate(BaseModel):
    """Schema para atualizar Conta a Receber"""
    codcli: Optional[int] = None
    vlrcar: Optional[Decimal] = Field(None, gt=0)
    datven: Optional[date] = None
    datrec: Optional[date] = None
    statcar: Optional[StatusContaReceber] = None
    catcar: Optional[str] = Field(None, max_length=100)
    forrec: Optional[str] = Field(None, max_length=50)
    numpar: Optional[int] = Field(None, gt=0)
    totpar: Optional[int] = Field(None, gt=0)
    codgrp: Optional[str] = Field(None, max_length=50)
    codpai: Optional[int] = None
    obscar: Optional[str] = Field(None, max_length=1000)
    numdoc: Optional[str] = Field(None, max_length=50)


class ContaReceberResponse(ContaReceberBase):
    """Schema de resposta para Conta a Receber"""
    codcar: int
    codemp: int
    codfil: int
    datcri: datetime
    usucri: int
    datalt: Optional[datetime] = None
    usualt: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


class ContaReceberResponseComNome(ContaReceberResponse):
    """Schema de resposta para Conta a Receber com nome do cliente"""
    nomcli: Optional[str] = Field(None, description="Nome do cliente")
    
    model_config = ConfigDict(from_attributes=True)


class ContaReceberBaixa(BaseModel):
    """Schema para baixa de Conta a Receber"""
    datrec: date = Field(..., description="Data do recebimento")
    forrec: Optional[str] = Field(None, max_length=50, description="Forma de recebimento")
    obscar: Optional[str] = Field(None, max_length=1000, description="Observações")


class ContaReceberParcelamento(BaseModel):
    """Schema para parcelamento de Conta a Receber"""
    totpar: int = Field(..., gt=1, description="Total de parcelas (mínimo 2)")
    vlrcar: Decimal = Field(..., gt=0, description="Valor total a parcelar")
    datven_primeira: date = Field(..., description="Data de vencimento da primeira parcela")
    intervalo_dias: int = Field(default=30, gt=0, description="Intervalo em dias entre parcelas")
    catcar: Optional[str] = Field(None, max_length=100)
    forrec: Optional[str] = Field(None, max_length=50)
    obscar: Optional[str] = Field(None, max_length=1000)
    numdoc: Optional[str] = Field(None, max_length=50)


class ContaReceberReparcelamento(BaseModel):
    """Schema para reparcelamento de Conta a Receber"""
    totpar_novo: int = Field(..., gt=1, description="Novo total de parcelas")
    datven_primeira: date = Field(..., description="Data de vencimento da primeira nova parcela")
    intervalo_dias: int = Field(default=30, gt=0, description="Intervalo em dias entre parcelas")
    obscar: Optional[str] = Field(None, max_length=1000)


class ContaReceberCancelamento(BaseModel):
    """Schema para cancelamento de Conta a Receber"""
    motivo: str = Field(..., max_length=1000, description="Motivo do cancelamento")
