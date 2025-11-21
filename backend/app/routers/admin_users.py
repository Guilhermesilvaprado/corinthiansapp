# app/routers/admin_users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreateSuper, UserRead, UserUpdate
from app.routers.auth import get_current_user

router = APIRouter(prefix="/admin", tags=["Admin"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


class SetAdminRequest(BaseModel):
    isadmin: bool


class ResetPasswordRequest(BaseModel):
    nova_senha: str


def assert_admin_of_tenant(user: User):
    """Permite se for admin do tenant ou superadmin."""
    if not (user.isadmin or user.issuper):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: somente admin do tenant"
        )


def assert_same_tenant(actor: User, target: User):
    """Garante que o 'actor' e o 'target' estão no mesmo tenant (codemp/codfil),
    a menos que actor seja superadmin."""
    if actor.issuper:
        return
    if actor.codemp != target.codemp or actor.codfil != target.codfil:
        raise HTTPException(status_code=403, detail="Acesso negado a outro tenant")

@router.delete("/users/{codusu}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_of_my_tenant(
    codusu: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Precisa ser admin do tenant (ou superadmin)
    assert_admin_of_tenant(current_user)

    result = await db.execute(select(User).where(User.codusu == codusu))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    # Mesmo tenant (ou superadmin)
    assert_same_tenant(current_user, user)

    # Não permitir deletar superadmin (a menos que current_user seja superadmin)
    if user.issuper and not current_user.issuper:
        raise HTTPException(status_code=400, detail="Não é possível deletar um superadmin")

    await db.delete(user)
    await db.commit()
    return

@router.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user_as_tenant_admin(
    payload: UserCreateSuper,  # reaproveitamos o schema (vamos ignorar codemp/codfil do payload)
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Precisa ser admin do tenant (ou superadmin)
    assert_admin_of_tenant(current_user)

    # Forçamos a criação no tenant do usuário logado (empresa/filial)
    codemp = current_user.codemp
    codfil = current_user.codfil

    # Valida duplicidade de login dentro do mesmo tenant
    q = select(User).where(
        User.logusu == payload.logusu,
        User.codemp == codemp,
        User.codfil == codfil,
    )
    exists = (await db.execute(q)).scalar_one_or_none()
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe usuário com esse login nesse tenant"
        )

    new_user = User(
        nomusu=payload.nomusu,
        logusu=payload.logusu,
        emausu=payload.emausu,
        situsu=payload.situsu,  # "ATIVO"/"INATIVO"
        pwdusu=get_password_hash(payload.senha),
        codemp=codemp,
        codfil=codfil,
        codpes=0,
        setusu=None,
        issuper=False,
        isadmin=payload.isadmin,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.get("/users", response_model=list[UserRead])
async def list_users_of_my_tenant(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Lista somente do próprio tenant (se superadmin, também pode listar o próprio tenant atual dele)
    q = select(User).where(
        User.codemp == current_user.codemp,
        User.codfil == current_user.codfil
    ).order_by(User.nomusu)
    res = await db.execute(q)
    return res.scalars().all()


@router.get("/users/{codusu}", response_model=UserRead)
async def get_user_of_my_tenant(
    codusu: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(User).where(User.codusu == codusu))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    # Acesso somente ao mesmo tenant (ou superadmin)
    assert_same_tenant(current_user, user)
    return user


@router.patch("/users/{codusu}", response_model=UserRead)
async def patch_user_of_my_tenant(
    codusu: int,
    payload: UserUpdate,  # aceita { "situsu": "ATIVO" | "INATIVO", ... }
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Precisa ser admin do tenant (ou superadmin)
    assert_admin_of_tenant(current_user)

    result = await db.execute(select(User).where(User.codusu == codusu))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    # Mesmo tenant (ou superadmin)
    assert_same_tenant(current_user, user)

    # Não permitir alterar superadmin
    if user.issuper and not current_user.issuper:
        raise HTTPException(status_code=400, detail="Não é possível alterar um superadmin")

    # Atualizações parciais
    if payload.nomusu is not None:
        user.nomusu = payload.nomusu
    if payload.emausu is not None:
        user.emausu = payload.emausu
    if payload.situsu is not None:
        # Schemas já normalizam; salva "ATIVO"/"INATIVO"
        user.situsu = payload.situsu
    if payload.senha is not None and payload.senha != "":
        user.pwdusu = get_password_hash(payload.senha)

    # Nunca permitir trocar codemp/codfil por aqui
    await db.commit()
    await db.refresh(user)
    return user


@router.patch("/users/{codusu}/set-admin", response_model=UserRead)
async def set_admin_status(
    codusu: int,
    payload: SetAdminRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Precisa ser admin do tenant (ou superadmin)
    assert_admin_of_tenant(current_user)

    result = await db.execute(select(User).where(User.codusu == codusu))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    # Mesmo tenant (ou superadmin)
    assert_same_tenant(current_user, user)

    # Não permitir alterar superadmin
    if user.issuper and not current_user.issuper:
        raise HTTPException(status_code=400, detail="Não é possível alterar isadmin de um superadmin")

    user.isadmin = payload.isadmin
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/users/{codusu}/reset-password", response_model=UserRead)
async def reset_password(
    codusu: int,
    payload: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Precisa ser admin do tenant (ou superadmin)
    assert_admin_of_tenant(current_user)

    result = await db.execute(select(User).where(User.codusu == codusu))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    # Mesmo tenant (ou superadmin)
    assert_same_tenant(current_user, user)

    # Validação simples da nova senha
    if not payload.nova_senha or payload.nova_senha.strip() == "":
        raise HTTPException(status_code=400, detail="Nova senha inválida")

    user.pwdusu = get_password_hash(payload.nova_senha)
    await db.commit()
    await db.refresh(user)
    return user