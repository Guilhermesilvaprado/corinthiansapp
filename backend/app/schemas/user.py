# app/schemas/user.py
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator

def to_ui_sit(v: Optional[str]) -> Literal["ATIVO", "INATIVO"]:
    v_up = (v or "").upper().strip()
    if v_up in {"ATIVO", "A"}:
        return "ATIVO"
    if v_up in {"INATIVO", "I"}:
        return "INATIVO"
    return "INATIVO"

class UserBase(BaseModel):
    nomusu: str
    logusu: str
    emausu: Optional[EmailStr] = None
    situsu: Literal["ATIVO", "INATIVO"] = Field(default="ATIVO")
    codemp: int
    codfil: int

    model_config = ConfigDict(from_attributes=True)

    @field_validator("situsu", mode="before")
    @classmethod
    def normalize_situsu_base(cls, v):
        return to_ui_sit(v)

class UserCreate(UserBase):
    senha: str

class UserUpdate(BaseModel):
    nomusu: Optional[str] = None
    emausu: Optional[EmailStr] = None
    situsu: Optional[Literal["ATIVO", "INATIVO"]] = None
    senha: Optional[str] = None

    @field_validator("situsu", mode="before")
    @classmethod
    def normalize_situsu_update(cls, v):
        if v is None:
            return v
        return to_ui_sit(v)

class UserResponse(BaseModel):
    codusu: int
    nomusu: str
    logusu: str
    emausu: Optional[EmailStr] = None
    situsu: Literal["ATIVO", "INATIVO"]
    codemp: int
    codfil: int
    issuper: bool = False
    isadmin: bool = False

    model_config = ConfigDict(from_attributes=True)

    @field_validator("situsu", mode="before")
    @classmethod
    def normalize_situsu_resp(cls, v):
        return to_ui_sit(v)

# ========== SuperAdmin ==========

class UserCreateSuper(BaseModel):
    nomusu: str
    logusu: str
    emausu: EmailStr
    senha: str
    situsu: Literal["ATIVO", "INATIVO"] = Field(default="ATIVO")
    codemp: Optional[int] = None  # Tornar opcional
    codfil: Optional[int] = None  # Tornar opcional
    isadmin: bool = False

    @field_validator("situsu", mode="before")
    @classmethod
    def normalize_situsu_super(cls, v):
        return to_ui_sit(v)

class UserRead(BaseModel):
    codusu: int
    nomusu: str
    logusu: str
    emausu: Optional[EmailStr] = None
    situsu: Literal["ATIVO", "INATIVO"]
    codemp: int
    codfil: int
    issuper: bool
    isadmin: bool

    model_config = ConfigDict(from_attributes=True)

    @field_validator("situsu", mode="before")
    @classmethod
    def normalize_situsu_read(cls, v):
        return to_ui_sit(v)