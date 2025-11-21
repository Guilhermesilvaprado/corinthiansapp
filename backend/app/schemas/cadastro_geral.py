# app/schemas/cadastro_geral.py
from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator


# Tipos possíveis para Cadastro Geral
TipoCadastro = Literal["FORNECEDOR", "CLIENTE", "USUARIO", "OUTROS"]
StatusCadastro = Literal["ATIVO", "INATIVO"]


class CadastroGeralBase(BaseModel):
    """Schema base para Cadastro Geral"""
    nomcad: str = Field(..., min_length=1, max_length=100, description="Nome do cadastro")
    tipcad: TipoCadastro = Field(..., description="Tipo do cadastro")
    doccad: Optional[str] = Field(None, max_length=18, description="CPF ou CNPJ")
    endcad: Optional[str] = Field(None, max_length=200, description="Endereço")
    cidcad: Optional[str] = Field(None, max_length=100, description="Cidade")
    ufcad: Optional[str] = Field(None, max_length=2, description="UF")
    cepcad: Optional[str] = Field(None, max_length=9, description="CEP")
    telcad: Optional[str] = Field(None, max_length=20, description="Telefone")
    celcad: Optional[str] = Field(None, max_length=20, description="Celular")
    emacad: Optional[str] = Field(None, max_length=200, description="E-mail")
    statcad: StatusCadastro = Field(default="ATIVO", description="Status do cadastro")
    obscad: Optional[str] = Field(None, max_length=1000, description="Observações")
    
    model_config = ConfigDict(from_attributes=True)


class CadastroGeralCreate(CadastroGeralBase):
    """Schema para criar Cadastro Geral"""
    pass


class CadastroGeralUpdate(BaseModel):
    """Schema para atualizar Cadastro Geral"""
    nomcad: Optional[str] = Field(None, min_length=1, max_length=100)
    tipcad: Optional[TipoCadastro] = None
    doccad: Optional[str] = Field(None, max_length=18)
    endcad: Optional[str] = Field(None, max_length=200)
    cidcad: Optional[str] = Field(None, max_length=100)
    ufcad: Optional[str] = Field(None, max_length=2)
    cepcad: Optional[str] = Field(None, max_length=9)
    telcad: Optional[str] = Field(None, max_length=20)
    celcad: Optional[str] = Field(None, max_length=20)
    emacad: Optional[str] = Field(None, max_length=200)
    statcad: Optional[StatusCadastro] = None
    obscad: Optional[str] = Field(None, max_length=1000)


class CadastroGeralResponse(CadastroGeralBase):
    """Schema de resposta para Cadastro Geral"""
    codcad: int
    codemp: int
    codfil: int
    datcri: datetime
    usucri: int
    datalt: Optional[datetime] = None
    usualt: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


class CadastroGeralListItem(BaseModel):
    """Schema simplificado para listagem de Cadastros Gerais"""
    codcad: int
    nomcad: str
    tipcad: TipoCadastro
    doccad: Optional[str] = None
    telcad: Optional[str] = None
    emacad: Optional[str] = None
    statcad: StatusCadastro
    
    model_config = ConfigDict(from_attributes=True)
