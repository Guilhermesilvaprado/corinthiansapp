from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.routers.auth import get_tenant
from app.models.pessoa import Pessoa
from app.schemas.pessoa import PessoaCreate, PessoaUpdate, PessoaResponse

router = APIRouter(prefix="/pessoas", tags=["Pessoas"])


@router.post("/", response_model=PessoaResponse, status_code=status.HTTP_201_CREATED)
async def create_pessoa(
    payload: PessoaCreate,
    db: AsyncSession = Depends(get_db),
    tenant: tuple[int, int] = Depends(get_tenant),
):
    """Cria uma nova pessoa no tenant do usuário autenticado"""
    codemp, codfil = tenant

    # Força tenant no servidor (ignora qualquer valor enviado pelo cliente)
    nova = Pessoa(
        tippes=payload.tippes,
        codtre=payload.codtre,
        nompes=payload.nompes,
        fanpes=payload.fanpes,
        cpfpes=payload.cpfpes,
        cnppes=payload.cnppes,
        endpes=payload.endpes,
        numpes=payload.numpes,
        baipes=payload.baipes,
        cidpes=payload.cidpes,
        estpes=payload.estpes,
        ceppes=payload.ceppes,
        em1pes=payload.em1pes,
        em2pes=payload.em2pes,
        celpes=payload.celpes,
        sexpes=payload.sexpes,
        sitpes=payload.sitpes,
        codemp=codemp,  # 🔒 Força tenant do token
        codfil=codfil,  # 🔒 Força tenant do token
    )
    db.add(nova)
    await db.commit()
    await db.refresh(nova)
    return nova


@router.get("/", response_model=list[PessoaResponse])
async def list_pessoas(
    db: AsyncSession = Depends(get_db),
    tenant: tuple[int, int] = Depends(get_tenant),
):
    """Lista todas as pessoas do tenant do usuário autenticado"""
    codemp, codfil = tenant
    
    result = await db.execute(
        select(Pessoa).where(
            Pessoa.codemp == codemp,
            Pessoa.codfil == codfil,
        ).order_by(Pessoa.nompes)
    )
    return result.scalars().all()


@router.get("/{codpes}", response_model=PessoaResponse)
async def get_pessoa(
    codpes: int,
    db: AsyncSession = Depends(get_db),
    tenant: tuple[int, int] = Depends(get_tenant),
):
    """Busca uma pessoa específica no tenant do usuário autenticado"""
    codemp, codfil = tenant
    
    result = await db.execute(
        select(Pessoa).where(
            Pessoa.codpes == codpes,
            Pessoa.codemp == codemp,
            Pessoa.codfil == codfil,
        )
    )
    pessoa = result.scalar_one_or_none()
    
    if not pessoa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pessoa não encontrada"
        )
    
    return pessoa


@router.put("/{codpes}", response_model=PessoaResponse)
async def update_pessoa(
    codpes: int,
    payload: PessoaUpdate,
    db: AsyncSession = Depends(get_db),
    tenant: tuple[int, int] = Depends(get_tenant),
):
    """Atualiza uma pessoa no tenant do usuário autenticado"""
    codemp, codfil = tenant

    # Busca garantindo isolamento por tenant
    result = await db.execute(
        select(Pessoa).where(
            Pessoa.codpes == codpes,
            Pessoa.codemp == codemp,
            Pessoa.codfil == codfil,
        )
    )
    pessoa = result.scalar_one_or_none()
    
    if not pessoa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pessoa não encontrada"
        )

    # Atualiza apenas campos enviados (não mexe em codemp/codfil/codpes)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(pessoa, field, value)

    await db.commit()
    await db.refresh(pessoa)
    return pessoa


@router.delete("/{codpes}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pessoa(
    codpes: int,
    db: AsyncSession = Depends(get_db),
    tenant: tuple[int, int] = Depends(get_tenant),
):
    """Deleta uma pessoa no tenant do usuário autenticado"""
    codemp, codfil = tenant
    
    result = await db.execute(
        select(Pessoa).where(
            Pessoa.codpes == codpes,
            Pessoa.codemp == codemp,
            Pessoa.codfil == codfil,
        )
    )
    pessoa = result.scalar_one_or_none()
    
    if not pessoa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pessoa não encontrada"
        )

    await db.delete(pessoa)
    await db.commit()
    return