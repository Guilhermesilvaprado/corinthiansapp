# app/routers/relatorios.py
from typing import List, Optional
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from pydantic import BaseModel, Field
from decimal import Decimal

from app.database import get_db
from app.models.user import User
from app.models.contas_pagar import ContaPagar
from app.models.contas_receber import ContaReceber
from app.models.pessoa import Pessoa
from app.routers.auth import get_current_user

router = APIRouter(prefix="/relatorios", tags=["Relatórios"])


# ========== SCHEMAS DE RELATÓRIOS ==========

class FluxoCaixaItem(BaseModel):
    """Item do fluxo de caixa"""
    data: date
    descricao: str
    tipo: str  # "ENTRADA" ou "SAIDA"
    categoria: Optional[str] = None
    valor: Decimal
    status: str
    origem: str  # "CONTAS_RECEBER" ou "CONTAS_PAGAR"
    cod_origem: int  # codcar ou codcap
    nome_pessoa: Optional[str] = None  # Nome do cliente/fornecedor


class FluxoCaixaResumo(BaseModel):
    """Resumo do fluxo de caixa"""
    periodo_inicio: date
    periodo_fim: date
    total_entradas: Decimal = Decimal("0.00")
    total_saidas: Decimal = Decimal("0.00")
    saldo: Decimal = Decimal("0.00")
    total_entradas_previstas: Decimal = Decimal("0.00")
    total_saidas_previstas: Decimal = Decimal("0.00")
    saldo_previsto: Decimal = Decimal("0.00")


class FluxoCaixaResponse(BaseModel):
    """Resposta completa do fluxo de caixa"""
    resumo: FluxoCaixaResumo
    items: List[FluxoCaixaItem]


class ContaVencidaItem(BaseModel):
    """Item de conta vencida"""
    tipo: str  # "PAGAR" ou "RECEBER"
    cod: int
    pessoa: str  # Nome do fornecedor/cliente
    valor: Decimal
    data_vencimento: date
    dias_vencido: int
    categoria: Optional[str] = None
    forma_pagamento: Optional[str] = None
    num_parcela: int
    tot_parcelas: int
    observacoes: Optional[str] = None


class ContasVencidasResponse(BaseModel):
    """Resposta de contas vencidas"""
    total_a_pagar: Decimal = Decimal("0.00")
    total_a_receber: Decimal = Decimal("0.00")
    count_a_pagar: int = 0
    count_a_receber: int = 0
    items: List[ContaVencidaItem]


# ========== ENDPOINT: FLUXO DE CAIXA ==========

@router.get("/fluxo-caixa", response_model=FluxoCaixaResponse)
async def relatorio_fluxo_caixa(
    data_inicio: date = Query(..., description="Data inicial do período"),
    data_fim: date = Query(..., description="Data final do período"),
    incluir_canceladas: bool = Query(False, description="Incluir contas canceladas"),
    apenas_realizadas: bool = Query(False, description="Apenas contas pagas/recebidas"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Relatório de Fluxo de Caixa
    
    Consolida entradas (contas a receber) e saídas (contas a pagar) 
    em um período específico.
    """
    
    if data_inicio > data_fim:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data inicial não pode ser maior que data final"
        )
    
    items = []
    
    # ===== BUSCAR CONTAS A RECEBER =====
    query_receber = select(ContaReceber, Pessoa.nompes).outerjoin(
        Pessoa, ContaReceber.codcli == Pessoa.codpes
    ).where(
        and_(
            ContaReceber.datven >= data_inicio,
            ContaReceber.datven <= data_fim
        )
    )
    
    # Filtro de tenant
    if not current_user.issuper:
        query_receber = query_receber.where(
            and_(
                ContaReceber.codemp == current_user.codemp,
                ContaReceber.codfil == current_user.codfil
            )
        )
    
    # Filtro de status
    if not incluir_canceladas:
        query_receber = query_receber.where(ContaReceber.statcar != "CANCELADO")
    
    if apenas_realizadas:
        query_receber = query_receber.where(ContaReceber.statcar == "RECEBIDO")
    
    result_receber = await db.execute(query_receber)
    contas_receber = result_receber.all()
    
    for conta, nome_pessoa in contas_receber:
        items.append(FluxoCaixaItem(
            data=conta.datven,
            descricao=f"Recebimento - {nome_pessoa or 'Cliente'}",
            tipo="ENTRADA",
            categoria=conta.catcar,
            valor=conta.vlrcar,
            status=conta.statcar,
            origem="CONTAS_RECEBER",
            cod_origem=conta.codcar,
            nome_pessoa=nome_pessoa,
        ))
    
    # ===== BUSCAR CONTAS A PAGAR =====
    query_pagar = select(ContaPagar, Pessoa.nompes).outerjoin(
        Pessoa, ContaPagar.codfor == Pessoa.codpes
    ).where(
        and_(
            ContaPagar.datven >= data_inicio,
            ContaPagar.datven <= data_fim
        )
    )
    
    # Filtro de tenant
    if not current_user.issuper:
        query_pagar = query_pagar.where(
            and_(
                ContaPagar.codemp == current_user.codemp,
                ContaPagar.codfil == current_user.codfil
            )
        )
    
    # Filtro de status
    if not incluir_canceladas:
        query_pagar = query_pagar.where(ContaPagar.statcap != "CANCELADO")
    
    if apenas_realizadas:
        query_pagar = query_pagar.where(ContaPagar.statcap == "PAGO")
    
    result_pagar = await db.execute(query_pagar)
    contas_pagar = result_pagar.all()
    
    for conta, nome_pessoa in contas_pagar:
        items.append(FluxoCaixaItem(
            data=conta.datven,
            descricao=f"Pagamento - {nome_pessoa or 'Fornecedor'}",
            tipo="SAIDA",
            categoria=conta.catcap,
            valor=conta.vlrcap,
            status=conta.statcap,
            origem="CONTAS_PAGAR",
            cod_origem=conta.codcap,
            nome_pessoa=nome_pessoa,
        ))
    
    # Ordenar por data
    items.sort(key=lambda x: x.data)
    
    # ===== CALCULAR RESUMO =====
    total_entradas = sum(
        item.valor for item in items 
        if item.tipo == "ENTRADA" and item.status == "RECEBIDO"
    )
    
    total_saidas = sum(
        item.valor for item in items 
        if item.tipo == "SAIDA" and item.status == "PAGO"
    )
    
    total_entradas_previstas = sum(
        item.valor for item in items 
        if item.tipo == "ENTRADA" and item.status in ["A_RECEBER", "VENCIDO"]
    )
    
    total_saidas_previstas = sum(
        item.valor for item in items 
        if item.tipo == "SAIDA" and item.status in ["A_PAGAR", "VENCIDO"]
    )
    
    resumo = FluxoCaixaResumo(
        periodo_inicio=data_inicio,
        periodo_fim=data_fim,
        total_entradas=total_entradas,
        total_saidas=total_saidas,
        saldo=total_entradas - total_saidas,
        total_entradas_previstas=total_entradas_previstas,
        total_saidas_previstas=total_saidas_previstas,
        saldo_previsto=(total_entradas + total_entradas_previstas) - (total_saidas + total_saidas_previstas),
    )
    
    return FluxoCaixaResponse(resumo=resumo, items=items)


# ========== ENDPOINT: CONTAS VENCIDAS ==========

@router.get("/contas-vencidas", response_model=ContasVencidasResponse)
async def relatorio_contas_vencidas(
    limite_dias: int = Query(None, ge=0, description="Limite de dias vencidos (None = sem limite)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Relatório de Contas Vencidas
    
    Lista todas as contas vencidas (a pagar e a receber) que ainda não foram baixadas.
    """
    
    hoje = date.today()
    items = []
    
    # ===== CONTAS A PAGAR VENCIDAS =====
    query_pagar = select(ContaPagar, Pessoa.nompes).outerjoin(
        Pessoa, ContaPagar.codfor == Pessoa.codpes
    ).where(
        and_(
            ContaPagar.statcap.in_(["A_PAGAR", "VENCIDO"]),
            ContaPagar.datven < hoje
        )
    )
    
    # Filtro de tenant
    if not current_user.issuper:
        query_pagar = query_pagar.where(
            and_(
                ContaPagar.codemp == current_user.codemp,
                ContaPagar.codfil == current_user.codfil
            )
        )
    
    # Limite de dias
    if limite_dias is not None:
        data_limite = hoje - timedelta(days=limite_dias)
        query_pagar = query_pagar.where(ContaPagar.datven >= data_limite)
    
    result_pagar = await db.execute(query_pagar)
    contas_pagar = result_pagar.all()
    
    total_a_pagar = Decimal("0.00")
    count_a_pagar = 0
    
    for conta, nome_pessoa in contas_pagar:
        dias_vencido = (hoje - conta.datven).days
        items.append(ContaVencidaItem(
            tipo="PAGAR",
            cod=conta.codcap,
            pessoa=nome_pessoa or "Fornecedor",
            valor=conta.vlrcap,
            data_vencimento=conta.datven,
            dias_vencido=dias_vencido,
            categoria=conta.catcap,
            forma_pagamento=conta.forpag,
            num_parcela=conta.numpar,
            tot_parcelas=conta.totpar,
            observacoes=conta.obscap,
        ))
        total_a_pagar += conta.vlrcap
        count_a_pagar += 1
    
    # ===== CONTAS A RECEBER VENCIDAS =====
    query_receber = select(ContaReceber, Pessoa.nompes).outerjoin(
        Pessoa, ContaReceber.codcli == Pessoa.codpes
    ).where(
        and_(
            ContaReceber.statcar.in_(["A_RECEBER", "VENCIDO"]),
            ContaReceber.datven < hoje
        )
    )
    
    # Filtro de tenant
    if not current_user.issuper:
        query_receber = query_receber.where(
            and_(
                ContaReceber.codemp == current_user.codemp,
                ContaReceber.codfil == current_user.codfil
            )
        )
    
    # Limite de dias
    if limite_dias is not None:
        data_limite = hoje - timedelta(days=limite_dias)
        query_receber = query_receber.where(ContaReceber.datven >= data_limite)
    
    result_receber = await db.execute(query_receber)
    contas_receber = result_receber.all()
    
    total_a_receber = Decimal("0.00")
    count_a_receber = 0
    
    for conta, nome_pessoa in contas_receber:
        dias_vencido = (hoje - conta.datven).days
        items.append(ContaVencidaItem(
            tipo="RECEBER",
            cod=conta.codcar,
            pessoa=nome_pessoa or "Cliente",
            valor=conta.vlrcar,
            data_vencimento=conta.datven,
            dias_vencido=dias_vencido,
            categoria=conta.catcar,
            forma_pagamento=conta.forrec,
            num_parcela=conta.numpar,
            tot_parcelas=conta.totpar,
            observacoes=conta.obscar,
        ))
        total_a_receber += conta.vlrcar
        count_a_receber += 1
    
    # Ordenar por dias vencidos (maior para menor)
    items.sort(key=lambda x: x.dias_vencido, reverse=True)
    
    return ContasVencidasResponse(
        total_a_pagar=total_a_pagar,
        total_a_receber=total_a_receber,
        count_a_pagar=count_a_pagar,
        count_a_receber=count_a_receber,
        items=items,
    )


# ========== ENDPOINT: RESUMO DASHBOARD ==========

class DashboardResumo(BaseModel):
    """Resumo para dashboard"""
    contas_pagar_abertas: int = 0
    contas_pagar_vencidas: int = 0
    total_pagar_aberto: Decimal = Decimal("0.00")
    total_pagar_vencido: Decimal = Decimal("0.00")
    
    contas_receber_abertas: int = 0
    contas_receber_vencidas: int = 0
    total_receber_aberto: Decimal = Decimal("0.00")
    total_receber_vencido: Decimal = Decimal("0.00")
    
    saldo_previsto_mes: Decimal = Decimal("0.00")


@router.get("/dashboard", response_model=DashboardResumo)
async def relatorio_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Resumo para Dashboard
    
    Retorna estatísticas gerais de contas a pagar e receber.
    """
    
    hoje = date.today()
    fim_mes = date(hoje.year, hoje.month + 1 if hoje.month < 12 else 1, 1) if hoje.month < 12 else date(hoje.year + 1, 1, 1)
    
    # ===== CONTAS A PAGAR =====
    query_pagar = select(ContaPagar)
    if not current_user.issuper:
        query_pagar = query_pagar.where(
            and_(
                ContaPagar.codemp == current_user.codemp,
                ContaPagar.codfil == current_user.codfil
            )
        )
    
    # Abertas
    query_pagar_abertas = query_pagar.where(ContaPagar.statcap == "A_PAGAR")
    result_pagar_abertas = await db.execute(query_pagar_abertas)
    contas_pagar_abertas = result_pagar_abertas.scalars().all()
    
    # Vencidas
    query_pagar_vencidas = query_pagar.where(
        and_(
            ContaPagar.statcap.in_(["A_PAGAR", "VENCIDO"]),
            ContaPagar.datven < hoje
        )
    )
    result_pagar_vencidas = await db.execute(query_pagar_vencidas)
    contas_pagar_vencidas = result_pagar_vencidas.scalars().all()
    
    # ===== CONTAS A RECEBER =====
    query_receber = select(ContaReceber)
    if not current_user.issuper:
        query_receber = query_receber.where(
            and_(
                ContaReceber.codemp == current_user.codemp,
                ContaReceber.codfil == current_user.codfil
            )
        )
    
    # Abertas
    query_receber_abertas = query_receber.where(ContaReceber.statcar == "A_RECEBER")
    result_receber_abertas = await db.execute(query_receber_abertas)
    contas_receber_abertas = result_receber_abertas.scalars().all()
    
    # Vencidas
    query_receber_vencidas = query_receber.where(
        and_(
            ContaReceber.statcar.in_(["A_RECEBER", "VENCIDO"]),
            ContaReceber.datven < hoje
        )
    )
    result_receber_vencidas = await db.execute(query_receber_vencidas)
    contas_receber_vencidas = result_receber_vencidas.scalars().all()
    
    # ===== CÁLCULOS =====
    total_pagar_aberto = sum(c.vlrcap for c in contas_pagar_abertas)
    total_pagar_vencido = sum(c.vlrcap for c in contas_pagar_vencidas)
    
    total_receber_aberto = sum(c.vlrcar for c in contas_receber_abertas)
    total_receber_vencido = sum(c.vlrcar for c in contas_receber_vencidas)
    
    saldo_previsto_mes = total_receber_aberto - total_pagar_aberto
    
    return DashboardResumo(
        contas_pagar_abertas=len(contas_pagar_abertas),
        contas_pagar_vencidas=len(contas_pagar_vencidas),
        total_pagar_aberto=total_pagar_aberto,
        total_pagar_vencido=total_pagar_vencido,
        contas_receber_abertas=len(contas_receber_abertas),
        contas_receber_vencidas=len(contas_receber_vencidas),
        total_receber_aberto=total_receber_aberto,
        total_receber_vencido=total_receber_vencido,
        saldo_previsto_mes=saldo_previsto_mes,
    )
