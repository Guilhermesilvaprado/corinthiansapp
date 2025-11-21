# app/schemas/contas_pagar.py
from typing import Optional, Literal
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict, field_validator


# Status possíveis para Conta a Pagar
StatusContaPagar = Literal["A_PAGAR", "PAGO", "VENCIDO", "CANCELADO"]


class ContaPagarBase(BaseModel):
    """Schema base para Conta a Pagar"""
    codfor: int = Field(..., description="Código do fornecedor")
    vlrcap: Decimal = Field(..., gt=0, description="Valor da conta")
    datven: date = Field(..., description="Data de vencimento")
    datpag: Optional[date] = Field(None, description="Data de pagamento")
    statcap: StatusContaPagar = Field(default="A_PAGAR", description="Status da conta")
    catcap: Optional[str] = Field(None, max_length=100, description="Categoria da despesa")
    forpag: Optional[str] = Field(None, max_length=50, description="Forma de pagamento")
    numpar: int = Field(default=1, gt=0, description="Número da parcela atual")
    totpar: int = Field(default=1, gt=0, description="Total de parcelas")
    codgrp: Optional[str] = Field(None, max_length=50, description="Código do grupo de parcelamento")
    codpai: Optional[int] = Field(None, description="Código da conta pai")
    obscap: Optional[str] = Field(None, max_length=1000, description="Observações")
    numdoc: Optional[str] = Field(None, max_length=50, description="Número do documento/NF")
    
    model_config = ConfigDict(from_attributes=True)
    
    @field_validator("numpar", "totpar")
    @classmethod
    def validate_parcelas(cls, v):
        if v < 1:
            raise ValueError("Número de parcelas deve ser maior que zero")
        return v


class ContaPagarCreate(ContaPagarBase):
    """Schema para criar Conta a Pagar"""
    pass


class ContaPagarUpdate(BaseModel):
    """Schema para atualizar Conta a Pagar"""
    codfor: Optional[int] = None
    vlrcap: Optional[Decimal] = Field(None, gt=0)
    datven: Optional[date] = None
    datpag: Optional[date] = None
    statcap: Optional[StatusContaPagar] = None
    catcap: Optional[str] = Field(None, max_length=100)
    forpag: Optional[str] = Field(None, max_length=50)
    numpar: Optional[int] = Field(None, gt=0)
    totpar: Optional[int] = Field(None, gt=0)
    codgrp: Optional[str] = Field(None, max_length=50)
    codpai: Optional[int] = None
    obscap: Optional[str] = Field(None, max_length=1000)
    numdoc: Optional[str] = Field(None, max_length=50)


class ContaPagarResponse(ContaPagarBase):
    """Schema de resposta para Conta a Pagar"""
    codcap: int
    codemp: int
    codfil: int
    datcri: datetime
    usucri: int
    datalt: Optional[datetime] = None
    usualt: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


class ContaPagarResponseComNome(ContaPagarResponse):
    """Schema de resposta para Conta a Pagar com nome do fornecedor"""
    nomfor: Optional[str] = Field(None, description="Nome do fornecedor")
    
    model_config = ConfigDict(from_attributes=True)


class ContaPagarBaixa(BaseModel):
    """Schema para baixa de Conta a Pagar"""
    datpag: date = Field(..., description="Data do pagamento")
    forpag: Optional[str] = Field(None, max_length=50, description="Forma de pagamento")
    obscap: Optional[str] = Field(None, max_length=1000, description="Observações")


class ContaPagarParcelamento(BaseModel):
    """Schema para parcelamento de Conta a Pagar"""
    totpar: int = Field(..., gt=1, description="Total de parcelas (mínimo 2)")
    vlrcap: Decimal = Field(..., gt=0, description="Valor total a parcelar")
    datven_primeira: date = Field(..., description="Data de vencimento da primeira parcela")
    intervalo_dias: int = Field(default=30, gt=0, description="Intervalo em dias entre parcelas")
    catcap: Optional[str] = Field(None, max_length=100)
    forpag: Optional[str] = Field(None, max_length=50)
    obscap: Optional[str] = Field(None, max_length=1000)
    numdoc: Optional[str] = Field(None, max_length=50)


class ContaPagarReparcelamento(BaseModel):
    """Schema para reparcelamento de Conta a Pagar"""
    totpar_novo: int = Field(..., gt=1, description="Novo total de parcelas")
    datven_primeira: date = Field(..., description="Data de vencimento da primeira nova parcela")
    intervalo_dias: int = Field(default=30, gt=0, description="Intervalo em dias entre parcelas")
    obscap: Optional[str] = Field(None, max_length=1000)


class ContaPagarCancelamento(BaseModel):
    """Schema para cancelamento de Conta a Pagar"""
    motivo: str = Field(..., max_length=1000, description="Motivo do cancelamento")
