from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserCreate, UserUpdate
from app.routers.auth import get_current_user, get_tenant  # importa as dependências

router = APIRouter(prefix="/users", tags=["Users"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# GET /users (agora com auth + tenant automático)
@router.get("/", response_model=list[UserResponse])
async def get_users(
    db: AsyncSession = Depends(get_db),
    tenant: tuple[int, int] = Depends(get_tenant),  # pega do token
):
    codemp, codfil = tenant
    result = await db.execute(
        select(User).where(User.codemp == codemp, User.codfil == codfil)
    )
    return result.scalars().all()


# GET /users/{codusu}
@router.get("/{codusu}", response_model=UserResponse)
async def get_user(
    codusu: int = Path(..., gt=0),
    db: AsyncSession = Depends(get_db),
    tenant: tuple[int, int] = Depends(get_tenant),
):
    codemp, codfil = tenant
    result = await db.execute(
        select(User).where(
            User.codusu == codusu,
            User.codemp == codemp,
            User.codfil == codfil,
        )
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user


# POST /users
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
    # só usuário autenticado pode criar
    current_user: User = Depends(get_current_user),
):
    # Força o mesmo tenant do usuário logado (segurança)
    payload.codemp = current_user.codemp
    payload.codfil = current_user.codfil

    # Verifica duplicidade de login no mesmo tenant
    dup_check = await db.execute(
        select(User).where(
            User.logusu == payload.logusu,
            User.codemp == payload.codemp,
            User.codfil == payload.codfil,
        )
    )
    if dup_check.scalar_one_or_none():
        raise HTTPException(
            status_code=400, detail="Login já existe neste tenant")

    hashed_password = get_password_hash(payload.senha)
    new_user = User(
        nomusu=payload.nomusu,
        logusu=payload.logusu,
        emausu=payload.emausu,
        situsu=payload.situsu,
        pwdusu=hashed_password,
        codemp=payload.codemp,
        codfil=payload.codfil,
        codpes=0,
        setusu=None,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


# PUT /users/{codusu}
@router.put("/{codusu}", response_model=UserResponse)
async def update_user(
    codusu: int,
    updates: UserUpdate,
    db: AsyncSession = Depends(get_db),
    tenant: tuple[int, int] = Depends(get_tenant),
):
    codemp, codfil = tenant
    result = await db.execute(
        select(User).where(
            User.codusu == codusu,
            User.codemp == codemp,
            User.codfil == codfil,
        )
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if updates.nomusu is not None:
        user.nomusu = updates.nomusu
    if updates.emausu is not None:
        user.emausu = updates.emausu
    if updates.situsu is not None:
        user.situsu = updates.situsu
    if updates.senha:
        user.pwdusu = get_password_hash(updates.senha)

    await db.commit()
    await db.refresh(user)
    return user


# DELETE /users/{codusu}
@router.delete("/{codusu}")
async def delete_user(
    codusu: int,
    db: AsyncSession = Depends(get_db),
    tenant: tuple[int, int] = Depends(get_tenant),
):
    codemp, codfil = tenant
    result = await db.execute(
        select(User).where(
            User.codusu == codusu,
            User.codemp == codemp,
            User.codfil == codfil,
        )
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    await db.delete(user)
    await db.commit()
    return {"message": "Usuário removido com sucesso"}
