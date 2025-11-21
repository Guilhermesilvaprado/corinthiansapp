from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreateSuper(BaseModel):
    nomusu: str
    logusu: str
    emausu: EmailStr
    senha: str
    situsu: str = "ATIVO"
    codemp: int
    codfil: int
    isadmin: bool = False

class UserRead(BaseModel):
    codusu: int
    nomusu: str
    logusu: str
    emausu: EmailStr
    situsu: str
    codemp: int
    codfil: int
    issuper: bool

    class Config:
        from_attributes = True
