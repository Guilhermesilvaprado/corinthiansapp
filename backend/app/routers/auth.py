from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

from app.database import get_db
from app.models.user import User
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Auth"])

# Config JWT
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def verify_password(plain_password, hashed_password):
    """Verifica se a senha em texto puro corresponde ao hash bcrypt"""
    if not hashed_password:
        return False
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# 🔑 Função para obter usuário atual com tenant
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        codusu = payload.get("codusu")
        codemp = payload.get("codemp") 
        codfil = payload.get("codfil")
        
        if codusu is None or codemp is None or codfil is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception

    # Busca usuário com filtro de tenant
    result = await db.execute(
        select(User).where(
            User.codusu == codusu,
            User.codemp == codemp,
            User.codfil == codfil,
        )
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception

    return user


# 🔑 Função para extrair tenant do usuário atual
def get_tenant(current_user: User = Depends(get_current_user)) -> tuple[int, int]:
    """Retorna (codemp, codfil) do usuário autenticado"""
    return current_user.codemp, current_user.codfil


# POST /auth/login
@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    # Busca por logusu (não email)
    result = await db.execute(select(User).where(User.logusu == form_data.username))
    user = result.scalar_one_or_none()

    # Debug: log do usuário encontrado (remover em produção)
    if user:
        print(f"🔍 Usuário encontrado: {user.logusu}, situsu: {user.situsu}")
        print(f"🔍 Hash no banco: {user.pwdusu[:20]}...")
    else:
        print(f"❌ Usuário '{form_data.username}' não encontrado")

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Verifica se usuário está ativo
    if user.situsu != "ATIVO":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário inativo"
        )

    # Verifica senha
    if not user.pwdusu or not verify_password(form_data.password, user.pwdusu):
        print(f"❌ Senha inválida para usuário {user.logusu}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "codusu": user.codusu,
            "codemp": user.codemp, 
            "codfil": user.codfil,
            "issuper": user.issuper,
            "isadmin": user.isadmin
        }, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# GET /auth/me (rota autenticada)
@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {
        "codusu": current_user.codusu,
        "nomusu": current_user.nomusu,
        "logusu": current_user.logusu,
        "emausu": current_user.emausu,
        "situsu": current_user.situsu,
        "codemp": current_user.codemp,
        "codfil": current_user.codfil,
        "issuper": current_user.issuper,
        "isadmin": current_user.isadmin
    }


# 🔑 Função para validar se o usuário é SuperAdmin
async def require_superadmin(current_user: User = Depends(get_current_user)) -> User:
    """Valida se o usuário é SuperAdmin"""
    if not current_user.issuper:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: apenas SuperAdmin pode realizar esta ação"
        )
    return current_user