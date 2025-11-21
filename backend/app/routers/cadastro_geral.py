# app/routers/cadastro_geral.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func

from app.database import get_db
from app.models.user import User
from app.models.cadastro_geral import CadastroGeral
from app.routers.auth import get_current_user
from app.schemas.cadastro_geral import (
    CadastroGeralCreate,
    CadastroGeralUpdate,
    CadastroGeralResponse,
    CadastroGeralListItem,
)

router = APIRouter(prefix="/cadastros-gerais", tags=["Cadastros Gerais"])


def assert_same_tenant_cadastro(user: User, cadastro: CadastroGeral):
    """Valida se o usuário pertence ao mesmo tenant do cadastro"""
    if user.issuper:
        return
    if user.codemp != cadastro.codemp or user.codfil != cadastro.codfil:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: cadastro pertence a outro tenant"
        )


async def get_cadastro_or_404(
    codcad: int,
    db: AsyncSession,
    current_user: User
) -> CadastroGeral:
    """Busca cadastro geral ou retorna 404"""
    query = select(CadastroGeral).where(CadastroGeral.codcad == codcad)
    
    # Se não for superadmin, filtra por tenant
    if not current_user.issuper:
        query = query.where(
            and_(
                CadastroGeral.codemp == current_user.codemp,
                CadastroGeral.codfil == current_user.codfil
            )
        )
    
    result = await db.execute(query)
    cadastro = result.scalar_one_or_none()
    
    if not cadastro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cadastro não encontrado"
        )
    
    return cadastro


# ========== CRUD ==========

@router.post("", response_model=CadastroGeralResponse, status_code=status.HTTP_201_CREATED)
async def create_cadastro_geral(
    payload: CadastroGeralCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Criar novo cadastro geral"""
    
    # Cria o novo cadastro
    novo_cadastro = CadastroGeral(
        nomcad=payload.nomcad,
        tipcad=payload.tipcad,
        doccad=payload.doccad,
        endcad=payload.endcad,
        cidcad=payload.cidcad,
        ufcad=payload.ufcad,
        cepcad=payload.cepcad,
        telcad=payload.telcad,
        celcad=payload.celcad,
        emacad=payload.emacad,
        statcad=payload.statcad,
        obscad=payload.obscad,
        codemp=current_user.codemp,
        codfil=current_user.codfil,
        usucri=current_user.codusu,
    )
    
    db.add(novo_cadastro)
    await db.commit()
    await db.refresh(novo_cadastro)
    
    return novo_cadastro


@router.get("", response_model=List[CadastroGeralListItem])
async def list_cadastros_gerais(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tipo: Optional[str] = Query(None, description="Filtrar por tipo (FORNECEDOR, CLIENTE, USUARIO, OUTROS)"),
    status: Optional[str] = Query(None, description="Filtrar por status (ATIVO, INATIVO)"),
    busca: Optional[str] = Query(None, description="Buscar por nome ou documento"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    """Listar cadastros gerais com filtros"""
    
    # Base query
    query = select(CadastroGeral)
    
    # Filtro por tenant
    if not current_user.issuper:
        query = query.where(
            and_(
                CadastroGeral.codemp == current_user.codemp,
                CadastroGeral.codfil == current_user.codfil
            )
        )
    
    # Filtros opcionais
    if tipo:
        query = query.where(CadastroGeral.tipcad == tipo)
    
    if status:
        query = query.where(CadastroGeral.statcad == status)
    
    if busca:
        query = query.where(
            or_(
                CadastroGeral.nomcad.ilike(f"%{busca}%"),
                CadastroGeral.doccad.ilike(f"%{busca}%")
            )
        )
    
    # Ordenação e paginação
    query = query.order_by(CadastroGeral.nomcad)
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    cadastros = result.scalars().all()
    
    return cadastros


@router.get("/{codcad}", response_model=CadastroGeralResponse)
async def get_cadastro_geral(
    codcad: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Buscar cadastro geral por ID"""
    cadastro = await get_cadastro_or_404(codcad, db, current_user)
    return cadastro


@router.put("/{codcad}", response_model=CadastroGeralResponse)
async def update_cadastro_geral(
    codcad: int,
    payload: CadastroGeralUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Atualizar cadastro geral"""
    cadastro = await get_cadastro_or_404(codcad, db, current_user)
    
    # Atualiza apenas os campos fornecidos
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(cadastro, field, value)
    
    # Atualiza informações de auditoria
    cadastro.usualt = current_user.codusu
    
    await db.commit()
    await db.refresh(cadastro)
    
    return cadastro


@router.delete("/{codcad}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cadastro_geral(
    codcad: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Excluir cadastro geral (inativar)"""
    cadastro = await get_cadastro_or_404(codcad, db, current_user)
    
    # Em vez de deletar, apenas inativa
    cadastro.statcad = "INATIVO"
    cadastro.usualt = current_user.codusu
    
    await db.commit()
    
    return None


@router.get("/tipos/counts", response_model=dict)
async def get_cadastros_counts_by_tipo(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obter contadores de cadastros por tipo"""
    
    # Base query
    query = select(
        CadastroGeral.tipcad,
        func.count(CadastroGeral.codcad).label("total")
    )
    
    # Filtro por tenant
    if not current_user.issuper:
        query = query.where(
            and_(
                CadastroGeral.codemp == current_user.codemp,
                CadastroGeral.codfil == current_user.codfil
            )
        )
    
    # Agrupa por tipo
    query = query.where(CadastroGeral.statcad == "ATIVO")
    query = query.group_by(CadastroGeral.tipcad)
    
    result = await db.execute(query)
    counts = result.all()
    
    # Converte para dicionário
    counts_dict = {row.tipcad: row.total for row in counts}
    
    # Garante que todos os tipos estejam presentes
    for tipo in ["FORNECEDOR", "CLIENTE", "USUARIO", "OUTROS"]:
        if tipo not in counts_dict:
            counts_dict[tipo] = 0
    
    return counts_dict
