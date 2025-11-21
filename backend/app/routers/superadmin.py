from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreateSuper, UserRead
from app.routers.auth import get_current_user

router = APIRouter(prefix="/superadmin", tags=["SuperAdmin"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# Schema para promoção/demoção
class SetAdminRequest(BaseModel):
    isadmin: bool


@router.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user_as_superadmin(
    payload: UserCreateSuper,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.issuper:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado: somente superadmin")

    q = select(User).where(
        User.logusu == payload.logusu,
        User.codemp == payload.codemp,
        User.codfil == payload.codfil,
    )
    exists = (await db.execute(q)).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Já existe usuário com esse login nesse tenant")

    new_user = User(
        nomusu=payload.nomusu,
        logusu=payload.logusu,
        emausu=payload.emausu,
        situsu=payload.situsu,
        pwdusu=get_password_hash(payload.senha),
        codemp=payload.codemp,
        codfil=payload.codfil,
        codpes=0,
        setusu=None,
        issuper=False,
        isadmin=payload.isadmin,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.patch("/users/{codusu}/set-admin", response_model=UserRead)
async def set_admin_status(
    codusu: int,
    payload: SetAdminRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Promove/demove um usuário a admin do tenant (somente superadmin)"""
    if not current_user.issuper:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado: somente superadmin")

    # Busca o usuário pela PK composta
    result = await db.execute(
        select(User).where(User.codusu == codusu)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    
    # Não permite alterar isadmin de um superadmin
    if user.issuper:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível alterar isadmin de um superadmin"
        )
    
    # Atualiza o status
    user.isadmin = payload.isadmin
    await db.commit()
    await db.refresh(user)
    return user


@router.get("/users", response_model=list[UserRead])
async def list_all_users(
    codemp: int = None,
    codfil: int = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista todos os usuários (com filtros opcionais por tenant) - somente superadmin"""
    if not current_user.issuper:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado: somente superadmin")
    
    query = select(User)
    
    # Filtros opcionais
    if codemp is not None:
        query = query.where(User.codemp == codemp)
    if codfil is not None:
        query = query.where(User.codfil == codfil)
    
    query = query.order_by(User.codemp, User.codfil, User.nomusu)
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/users/{codusu}", response_model=UserRead)
async def get_user_by_id(
    codusu: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Busca um usuário específico por ID - somente superadmin"""
    if not current_user.issuper:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado: somente superadmin")
    
    result = await db.execute(
        select(User).where(User.codusu == codusu)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    
    return user