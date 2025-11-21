# app/routers/licencas.py
from typing import List, Optional
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func

from app.database import get_db
from app.models.user import User
from app.models.licenca import Licenca
from app.routers.auth import get_current_user, require_superadmin
from app.schemas.licenca import (
    LicencaCreate,
    LicencaUpdate,
    LicencaResponse,
    LicencaDashboard,
)

router = APIRouter(prefix="/licencas", tags=["Licenças (SuperAdmin)"])


async def get_licenca_or_404(
    codlic: int,
    db: AsyncSession,
) -> Licenca:
    """Busca licença ou retorna 404"""
    query = select(Licenca).where(Licenca.codlic == codlic)
    result = await db.execute(query)
    licenca = result.scalar_one_or_none()
    
    if not licenca:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Licença não encontrada"
        )
    
    return licenca


# ========== CRUD (SUPERADMIN ONLY) ==========

@router.post("", response_model=LicencaResponse, status_code=status.HTTP_201_CREATED)
async def create_licenca(
    payload: LicencaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    """Criar nova licença (SuperAdmin only)"""
    
    # Valida se já existe licença ativa para esta empresa/filial
    query = select(Licenca).where(
        and_(
            Licenca.codemp == payload.codemp,
            Licenca.codfil == payload.codfil,
            Licenca.ativo == True,
            Licenca.datfim >= date.today()
        )
    )
    result = await db.execute(query)
    licenca_existente = result.scalar_one_or_none()
    
    if licenca_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Já existe uma licença ativa para esta empresa/filial (Licença #{licenca_existente.codlic})"
        )
    
    # Gera chave de licença
    chave_licenca = Licenca.gerar_chave_licenca(
        payload.codemp,
        payload.codfil,
        payload.cnplic
    )
    
    # Cria a nova licença
    nova_licenca = Licenca(
        codemp=payload.codemp,
        codfil=payload.codfil,
        nomlic=payload.nomlic,
        cnplic=payload.cnplic,
        chavlic=chave_licenca,
        datini=payload.datini,
        datfim=payload.datfim,
        statpag=payload.statpag,
        ativo=payload.ativo,
        obslic=payload.obslic,
        usucri=current_user.codusu,
    )
    
    db.add(nova_licenca)
    await db.commit()
    await db.refresh(nova_licenca)
    
    return nova_licenca


@router.get("", response_model=List[LicencaResponse])
async def list_licencas(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin),
    ativo: Optional[bool] = Query(None, description="Filtrar por status ativo/inativo"),
    statpag: Optional[str] = Query(None, description="Filtrar por status de pagamento"),
    vencidas: Optional[bool] = Query(None, description="Filtrar licenças vencidas"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    """Listar todas as licenças (SuperAdmin only)"""
    
    # Base query
    query = select(Licenca)
    
    # Filtros opcionais
    if ativo is not None:
        query = query.where(Licenca.ativo == ativo)
    
    if statpag:
        query = query.where(Licenca.statpag == statpag)
    
    if vencidas is not None:
        hoje = date.today()
        if vencidas:
            query = query.where(Licenca.datfim < hoje)
        else:
            query = query.where(Licenca.datfim >= hoje)
    
    # Ordenação e paginação
    query = query.order_by(Licenca.datfim.desc())
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    licencas = result.scalars().all()
    
    return licencas


@router.get("/dashboard", response_model=LicencaDashboard)
async def get_licencas_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    """Obter dashboard de licenças (SuperAdmin only)"""
    
    hoje = date.today()
    daqui_30_dias = hoje + timedelta(days=30)
    
    # Total de licenças
    query_total = select(func.count(Licenca.codlic))
    result = await db.execute(query_total)
    total_licencas = result.scalar()
    
    # Licenças ativas
    query_ativas = select(func.count(Licenca.codlic)).where(Licenca.ativo == True)
    result = await db.execute(query_ativas)
    licencas_ativas = result.scalar()
    
    # Licenças inativas
    licencas_inativas = total_licencas - licencas_ativas
    
    # Licenças vencidas
    query_vencidas = select(func.count(Licenca.codlic)).where(
        and_(
            Licenca.ativo == True,
            Licenca.datfim < hoje
        )
    )
    result = await db.execute(query_vencidas)
    licencas_vencidas = result.scalar()
    
    # Licenças a vencer em 30 dias
    query_a_vencer = select(func.count(Licenca.codlic)).where(
        and_(
            Licenca.ativo == True,
            Licenca.datfim >= hoje,
            Licenca.datfim <= daqui_30_dias
        )
    )
    result = await db.execute(query_a_vencer)
    licencas_a_vencer_30_dias = result.scalar()
    
    # Licenças pendentes de pagamento
    query_pendentes = select(func.count(Licenca.codlic)).where(
        and_(
            Licenca.ativo == True,
            Licenca.statpag.in_(["PENDENTE", "ATRASADO"])
        )
    )
    result = await db.execute(query_pendentes)
    licencas_pendentes_pagamento = result.scalar()
    
    return LicencaDashboard(
        total_licencas=total_licencas,
        licencas_ativas=licencas_ativas,
        licencas_inativas=licencas_inativas,
        licencas_vencidas=licencas_vencidas,
        licencas_a_vencer_30_dias=licencas_a_vencer_30_dias,
        licencas_pendentes_pagamento=licencas_pendentes_pagamento,
    )


@router.get("/{codlic}", response_model=LicencaResponse)
async def get_licenca(
    codlic: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    """Buscar licença por ID (SuperAdmin only)"""
    licenca = await get_licenca_or_404(codlic, db)
    return licenca


@router.put("/{codlic}", response_model=LicencaResponse)
async def update_licenca(
    codlic: int,
    payload: LicencaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    """Atualizar licença (SuperAdmin only)"""
    licenca = await get_licenca_or_404(codlic, db)
    
    # Atualiza apenas os campos fornecidos
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(licenca, field, value)
    
    # Atualiza informações de auditoria
    licenca.usualt = current_user.codusu
    
    await db.commit()
    await db.refresh(licenca)
    
    return licenca


@router.delete("/{codlic}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_licenca(
    codlic: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    """Excluir licença (SuperAdmin only)"""
    licenca = await get_licenca_or_404(codlic, db)
    
    # Remove a licença do banco
    await db.delete(licenca)
    await db.commit()
    
    return None


@router.post("/{codlic}/renovar", response_model=LicencaResponse)
async def renovar_licenca(
    codlic: int,
    nova_data_fim: date = Query(..., description="Nova data de encerramento"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    """Renovar licença (SuperAdmin only)"""
    licenca = await get_licenca_or_404(codlic, db)
    
    # Valida se a nova data é posterior à data atual de fim
    if nova_data_fim <= licenca.datfim:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A nova data de encerramento deve ser posterior à data atual"
        )
    
    # Atualiza a data de fim
    licenca.datfim = nova_data_fim
    licenca.ativo = True
    licenca.usualt = current_user.codusu
    
    await db.commit()
    await db.refresh(licenca)
    
    return licenca


@router.post("/{codlic}/ativar", response_model=LicencaResponse)
async def ativar_licenca(
    codlic: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    """Ativar licença (SuperAdmin only)"""
    licenca = await get_licenca_or_404(codlic, db)
    
    licenca.ativo = True
    licenca.usualt = current_user.codusu
    
    await db.commit()
    await db.refresh(licenca)
    
    return licenca


@router.post("/{codlic}/desativar", response_model=LicencaResponse)
async def desativar_licenca(
    codlic: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    """Desativar licença (SuperAdmin only)"""
    licenca = await get_licenca_or_404(codlic, db)
    
    licenca.ativo = False
    licenca.usualt = current_user.codusu
    
    await db.commit()
    await db.refresh(licenca)
    
    return licenca
