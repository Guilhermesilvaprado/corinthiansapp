// src/pages/ContasPagarPage.tsx
import React, { useState, useCallback, useEffect } from "react";
import api from "../api";

// ========== TYPES ==========
type ContaPagar = {
  codcap: number;
  codfor: number;
  nomfor?: string; // Nome do fornecedor
  vlrcap: string;
  datven: string;
  datpag: string | null;
  statcap: "A_PAGAR" | "PAGO" | "VENCIDO" | "CANCELADO";
  catcap: string | null;
  forpag: string | null;
  numpar: number;
  totpar: number;
  codgrp: number;
  obscap: string | null;
  numdoc: string | null;
  codemp: number;
  codfil: number;
};

type Fornecedor = {
  codcad: number;
  nomcad: string;
  doccad: string | null;
  statcad: string;
};

type ParcelamentoForm = {
  vlrtotal: string;
  quantidade: number;
  datven_primeira: string;
  catcap: string;
  forpag: string;
  obscap: string;
  numdoc: string;
};

type EditParcelaForm = {
  vlrcap: string;
  datven: string;
  datpag: string;
};

// ========== HELPER FUNCTIONS ==========
const formatCurrency = (value: string | number): string => {
  const num = typeof value === "string" ? parseFloat(value) : value;
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(num);
};

const formatDate = (dateStr: string | null): string => {
  if (!dateStr) return "-";
  const date = new Date(dateStr);
  return date.toLocaleDateString("pt-BR");
};

const getStatusColor = (status: string): string => {
  const colors: Record<string, string> = {
    A_PAGAR: "bg-yellow-100 text-yellow-800 border-yellow-300",
    PAGO: "bg-green-100 text-green-800 border-green-300",
    VENCIDO: "bg-red-100 text-red-800 border-red-300",
    CANCELADO: "bg-gray-100 text-gray-800 border-gray-300",
  };
  return colors[status] || "bg-gray-100 text-gray-800";
};

const getStatusLabel = (status: string): string => {
  const labels: Record<string, string> = {
    A_PAGAR: "A Pagar",
    PAGO: "Pago",
    VENCIDO: "Vencido",
    CANCELADO: "Cancelado",
  };
  return labels[status] || status;
};

const getErrMsg = (e: any): string => {
  const d = e?.response?.data;
  if (!d) return e?.message || "Erro desconhecido";
  if (typeof d === "string") return d;
  const det = d.detail;
  if (!det) return JSON.stringify(d);
  if (typeof det === "string") return det;
  if (Array.isArray(det)) {
    return det.map((it: any) => it?.msg || JSON.stringify(it)).join("; ");
  }
  if (typeof det === "object" && det?.msg) return det.msg;
  try {
    return JSON.stringify(det);
  } catch {
    return "Erro de validação";
  }
};

// ========== COMPONENT ==========
export default function ContasPagarPage() {
  const [contas, setContas] = useState<ContaPagar[]>([]);
  const [fornecedores, setFornecedores] = useState<Fornecedor[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [showParcelamentoModal, setShowParcelamentoModal] = useState(false);
  const [showBaixaModal, setShowBaixaModal] = useState(false);
  const [showEditParcelaModal, setShowEditParcelaModal] = useState(false);
  const [selectedConta, setSelectedConta] = useState<ContaPagar | null>(null);
  const [expandedGroups, setExpandedGroups] = useState<Set<number>>(new Set());
  const [parcelasDoGrupo, setParcelasDoGrupo] = useState<ContaPagar[]>([]);

  // Filtros
  const [filterStatus, setFilterStatus] = useState<string>("");
  const [selectedFornecedor, setSelectedFornecedor] = useState<number>(0);

  // Form de parcelamento
  const [parcelamentoForm, setParcelamentoForm] = useState<ParcelamentoForm>({
    vlrtotal: "",
    quantidade: 1,
    datven_primeira: "",
    catcap: "",
    forpag: "DINHEIRO",
    obscap: "",
    numdoc: "",
  });

  // Form de edição de parcela
  const [editParcelaForm, setEditParcelaForm] = useState<EditParcelaForm>({
    vlrcap: "",
    datven: "",
    datpag: "",
  });

  // Form de baixa
  const [baixaForm, setBaixaForm] = useState({
    datpag: new Date().toISOString().split("T")[0],
    forpag: "DINHEIRO",
    obscap: "",
  });

  const ENDPOINT = "/contas-pagar";
  const CADASTROS_ENDPOINT = "/cadastros-gerais";

  // ========== LOAD FORNECEDORES ==========
  const loadFornecedores = useCallback(async () => {
    try {
      const res = await api.get<Fornecedor[]>(CADASTROS_ENDPOINT, {
        params: { tipocad: "FORNECEDOR", statcad: "ATIVO" },
      });
      setFornecedores(res.data || []);
    } catch (e: any) {
      console.error("Erro ao carregar fornecedores:", e);
    }
  }, []);

  // ========== LOAD CONTAS ==========
  const loadContas = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params: any = {};
      if (filterStatus) params.statcap = filterStatus;

      const res = await api.get<ContaPagar[]>(ENDPOINT, { params });
      setContas(res.data || []);
    } catch (e: any) {
      console.error(e);
      setError(getErrMsg(e));
    } finally {
      setLoading(false);
    }
  }, [filterStatus]);

  useEffect(() => {
    loadContas();
    loadFornecedores();
  }, [loadContas, loadFornecedores]);

  // ========== LOAD PARCELAS DO GRUPO ==========
  const loadParcelasDoGrupo = async (codgrp: number) => {
    try {
      const res = await api.get<ContaPagar[]>(`${ENDPOINT}/grupo/${codgrp}`);
      setParcelasDoGrupo(res.data || []);
    } catch (e: any) {
      console.error("Erro ao carregar parcelas:", e);
      setError(getErrMsg(e));
    }
  };

  // ========== TOGGLE GROUP ==========
  const toggleGroup = async (codgrp: number) => {
    const newExpanded = new Set(expandedGroups);
    if (newExpanded.has(codgrp)) {
      newExpanded.delete(codgrp);
      setParcelasDoGrupo([]);
    } else {
      newExpanded.add(codgrp);
      await loadParcelasDoGrupo(codgrp);
    }
    setExpandedGroups(newExpanded);
  };

  // ========== CREATE PARCELAMENTO ==========
  const handleCreateParcelamento = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (!selectedFornecedor || selectedFornecedor <= 0) {
      setError("Selecione um fornecedor válido");
      return;
    }

    if (!parcelamentoForm.vlrtotal || parseFloat(parcelamentoForm.vlrtotal) <= 0) {
      setError("Informe um valor total válido");
      return;
    }

    if (parcelamentoForm.quantidade < 1) {
      setError("A quantidade de parcelas deve ser no mínimo 1");
      return;
    }

    if (!parcelamentoForm.datven_primeira) {
      setError("Informe a data de vencimento da primeira parcela");
      return;
    }

    try {
      await api.post(`${ENDPOINT}/parcelar/${selectedFornecedor}`, {
        vlrtotal: parseFloat(parcelamentoForm.vlrtotal),
        quantidade: parcelamentoForm.quantidade,
        datven_primeira: parcelamentoForm.datven_primeira,
        catcap: parcelamentoForm.catcap || null,
        forpag: parcelamentoForm.forpag || null,
        obscap: parcelamentoForm.obscap || null,
        numdoc: parcelamentoForm.numdoc || null,
      });

      setSuccess(
        `Parcelamento criado com sucesso! ${parcelamentoForm.quantidade} parcelas geradas.`
      );
      setShowParcelamentoModal(false);
      resetParcelamentoForm();
      setSelectedFornecedor(0);
      await loadContas();
    } catch (e: any) {
      console.error(e);
      setError(getErrMsg(e));
    }
  };

  // ========== EDIT PARCELA ==========
  const handleEditParcela = async () => {
    if (!selectedConta) return;

    setError(null);
    setSuccess(null);

    try {
      await api.put(`${ENDPOINT}/${selectedConta.codcap}`, {
        vlrcap: parseFloat(editParcelaForm.vlrcap),
        datven: editParcelaForm.datven,
        datpag: editParcelaForm.datpag || null,
      });

      setSuccess("Parcela atualizada com sucesso!");
      setShowEditParcelaModal(false);
      setSelectedConta(null);
      
      // Recarregar grupo se estiver expandido
      if (selectedConta.codgrp && expandedGroups.has(selectedConta.codgrp)) {
        await loadParcelasDoGrupo(selectedConta.codgrp);
      }
      
      await loadContas();
    } catch (e: any) {
      console.error(e);
      setError(getErrMsg(e));
    }
  };

  // ========== BAIXAR CONTA ==========
  const handleBaixa = async () => {
    if (!selectedConta) return;

    setError(null);
    setSuccess(null);

    try {
      await api.post(`${ENDPOINT}/${selectedConta.codcap}/baixar`, {
        datpag: baixaForm.datpag,
        forpag: baixaForm.forpag || null,
        obscap: baixaForm.obscap || null,
      });

      setSuccess("Conta baixada com sucesso!");
      setShowBaixaModal(false);
      setSelectedConta(null);
      
      // Recarregar grupo se estiver expandido
      if (selectedConta.codgrp && expandedGroups.has(selectedConta.codgrp)) {
        await loadParcelasDoGrupo(selectedConta.codgrp);
      }
      
      await loadContas();
    } catch (e: any) {
      console.error(e);
      setError(getErrMsg(e));
    }
  };

  // ========== BAIXA ANTECIPADA ==========
  const handleBaixaAntecipada = async (conta: ContaPagar) => {
    if (!confirm("Deseja dar baixa antecipada nesta parcela?")) return;

    setError(null);
    setSuccess(null);

    try {
      await api.post(`${ENDPOINT}/${conta.codcap}/baixar`, {
        datpag: new Date().toISOString().split("T")[0],
        forpag: conta.forpag || "DINHEIRO",
        obscap: "Baixa antecipada",
      });

      setSuccess("Baixa antecipada realizada com sucesso!");
      
      // Recarregar grupo se estiver expandido
      if (conta.codgrp && expandedGroups.has(conta.codgrp)) {
        await loadParcelasDoGrupo(conta.codgrp);
      }
      
      await loadContas();
    } catch (e: any) {
      console.error(e);
      setError(getErrMsg(e));
    }
  };

  // ========== CANCELAR CONTA ==========
  const handleCancelar = async (conta: ContaPagar) => {
    if (!confirm(`Deseja realmente cancelar esta conta?`)) return;

    setError(null);
    setSuccess(null);

    const motivo = prompt("Motivo do cancelamento:");
    if (!motivo) return;

    try {
      await api.post(`${ENDPOINT}/${conta.codcap}/cancelar`, { motivo });
      setSuccess("Conta cancelada com sucesso!");
      
      // Recarregar grupo se estiver expandido
      if (conta.codgrp && expandedGroups.has(conta.codgrp)) {
        await loadParcelasDoGrupo(conta.codgrp);
      }
      
      await loadContas();
    } catch (e: any) {
      console.error(e);
      setError(getErrMsg(e));
    }
  };

  // ========== DELETE ==========
  const handleDelete = async (codcap: number) => {
    if (!confirm("Deseja realmente excluir esta conta?")) return;

    setError(null);
    setSuccess(null);

    try {
      await api.delete(`${ENDPOINT}/${codcap}`);
      setSuccess("Conta excluída com sucesso!");
      await loadContas();
    } catch (e: any) {
      console.error(e);
      setError(getErrMsg(e));
    }
  };

  // ========== RESET FORMS ==========
  const resetParcelamentoForm = () => {
    setParcelamentoForm({
      vlrtotal: "",
      quantidade: 1,
      datven_primeira: "",
      catcap: "",
      forpag: "DINHEIRO",
      obscap: "",
      numdoc: "",
    });
  };

  // ========== OPEN PARCELAMENTO MODAL ==========
  const openParcelamentoModal = () => {
    resetParcelamentoForm();
    setSelectedFornecedor(0);
    setShowParcelamentoModal(true);
  };

  // ========== OPEN EDIT PARCELA MODAL ==========
  const openEditParcelaModal = (conta: ContaPagar) => {
    setEditParcelaForm({
      vlrcap: conta.vlrcap,
      datven: conta.datven.split("T")[0],
      datpag: conta.datpag ? conta.datpag.split("T")[0] : "",
    });
    setSelectedConta(conta);
    setShowEditParcelaModal(true);
  };

  // ========== GET PARCELAS PAGAS NO GRUPO ==========
  const getParcelasPagasNoGrupo = (codgrp: number): { pagas: number; total: number } => {
    const parcelas = contas.filter((c) => c.codgrp === codgrp);
    const pagas = parcelas.filter((c) => c.statcap === "PAGO").length;
    return { pagas, total: parcelas.length };
  };

  // ========== GROUP CONTAS BY CODGRP ==========
  const groupedContas: { [key: number]: ContaPagar[] } = {};
  contas.forEach((conta) => {
    if (!groupedContas[conta.codgrp]) {
      groupedContas[conta.codgrp] = [];
    }
    groupedContas[conta.codgrp].push(conta);
  });

  // ========== GET REPRESENTATIVE CONTA FOR GROUP ==========
  const getRepresentativeConta = (group: ContaPagar[]): ContaPagar => {
    // Retorna a primeira parcela do grupo
    return group.sort((a, b) => a.numpar - b.numpar)[0];
  };

  // ========== RENDER ==========
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-slate-800 mb-2">
            💰 Contas a Pagar
          </h1>
          <p className="text-slate-600">Gerencie suas despesas e fornecedores</p>
        </div>

        {/* Alerts */}
        {error && (
          <div className="mb-6 bg-red-50 border-l-4 border-red-500 p-4 rounded-r-lg shadow-sm">
            <div className="flex items-center">
              <span className="text-red-700 font-medium">⚠️ {error}</span>
              <button
                onClick={() => setError(null)}
                className="ml-auto text-red-500 hover:text-red-700"
              >
                ✕
              </button>
            </div>
          </div>
        )}

        {success && (
          <div className="mb-6 bg-green-50 border-l-4 border-green-500 p-4 rounded-r-lg shadow-sm">
            <div className="flex items-center">
              <span className="text-green-700 font-medium">✓ {success}</span>
              <button
                onClick={() => setSuccess(null)}
                className="ml-auto text-green-500 hover:text-green-700"
              >
                ✕
              </button>
            </div>
          </div>
        )}

        {/* Actions Bar */}
        <div className="bg-white rounded-xl shadow-md p-6 mb-6">
          <div className="flex flex-wrap gap-4 items-center justify-between">
            <div className="flex gap-3 flex-wrap">
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Todos os Status</option>
                <option value="A_PAGAR">A Pagar</option>
                <option value="VENCIDO">Vencido</option>
                <option value="PAGO">Pago</option>
                <option value="CANCELADO">Cancelado</option>
              </select>

              <button
                onClick={loadContas}
                className="px-4 py-2 bg-slate-600 text-white rounded-lg hover:bg-slate-700 transition-colors flex items-center gap-2"
              >
                🔄 Atualizar
              </button>
            </div>

            <button
              onClick={openParcelamentoModal}
              className="px-6 py-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all shadow-md flex items-center gap-2"
            >
              ➕ Nova Conta / Parcelamento
            </button>
          </div>
        </div>

        {/* Table */}
        <div className="bg-white rounded-xl shadow-md overflow-hidden">
          {loading ? (
            <div className="p-12 text-center text-slate-500">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              <p className="mt-4">Carregando...</p>
            </div>
          ) : Object.keys(groupedContas).length === 0 ? (
            <div className="p-12 text-center text-slate-500">
              <p className="text-lg">📭 Nenhuma conta encontrada</p>
              <p className="text-sm mt-2">Crie sua primeira conta a pagar</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-50 border-b-2 border-slate-200">
                  <tr>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                      Grupo
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                      Fornecedor
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                      Valor Total
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                      Parcelas
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                      Progresso
                    </th>
                    <th className="px-6 py-4 text-center text-xs font-semibold text-slate-600 uppercase tracking-wider">
                      Ações
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {Object.entries(groupedContas).map(([codgrp, group]) => {
                    const representative = getRepresentativeConta(group);
                    const { pagas, total } = getParcelasPagasNoGrupo(
                      parseInt(codgrp)
                    );
                    const valorTotal = group.reduce(
                      (sum, c) => sum + parseFloat(c.vlrcap),
                      0
                    );
                    const isExpanded = expandedGroups.has(parseInt(codgrp));

                    return (
                      <React.Fragment key={codgrp}>
                        {/* Linha do Grupo */}
                        <tr className="hover:bg-slate-50 transition-colors">
                          <td className="px-6 py-4 text-sm text-slate-900">
                            <button
                              onClick={() => toggleGroup(parseInt(codgrp))}
                              className="flex items-center gap-2 text-blue-600 hover:text-blue-800"
                            >
                              {isExpanded ? "▼" : "▶"} Grupo #{codgrp}
                            </button>
                          </td>
                          <td className="px-6 py-4 text-sm text-slate-900">
                            {representative.nomfor || `ID: ${representative.codfor}`}
                          </td>
                          <td className="px-6 py-4 text-sm font-semibold text-slate-900">
                            {formatCurrency(valorTotal)}
                          </td>
                          <td className="px-6 py-4 text-sm text-slate-600">
                            {total} parcela{total > 1 ? "s" : ""}
                          </td>
                          <td className="px-6 py-4">
                            <div className="flex items-center gap-2">
                              <div className="flex-1 bg-slate-200 rounded-full h-2">
                                <div
                                  className="bg-green-500 h-2 rounded-full transition-all"
                                  style={{
                                    width: `${(pagas / total) * 100}%`,
                                  }}
                                />
                              </div>
                              <span className="text-xs text-slate-600 whitespace-nowrap">
                                {pagas}/{total}
                              </span>
                            </div>
                          </td>
                          <td className="px-6 py-4 text-center">
                            <button
                              onClick={() => toggleGroup(parseInt(codgrp))}
                              className="px-3 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors text-sm"
                            >
                              {isExpanded ? "Recolher" : "Expandir"}
                            </button>
                          </td>
                        </tr>

                        {/* Linhas das Parcelas (se expandido) */}
                        {isExpanded && (
                          <>
                            {parcelasDoGrupo.map((parcela) => (
                              <tr
                                key={parcela.codcap}
                                className="bg-slate-50 hover:bg-slate-100 transition-colors"
                              >
                                <td className="px-6 py-4 text-sm text-slate-600 pl-12">
                                  Parcela #{parcela.numpar}/{parcela.totpar}
                                </td>
                                <td className="px-6 py-4 text-sm text-slate-600">
                                  {formatCurrency(parcela.vlrcap)}
                                </td>
                                <td className="px-6 py-4 text-sm text-slate-600">
                                  Venc: {formatDate(parcela.datven)}
                                </td>
                                <td className="px-6 py-4">
                                  <span
                                    className={`inline-flex px-3 py-1 text-xs font-medium rounded-full border ${getStatusColor(
                                      parcela.statcap
                                    )}`}
                                  >
                                    {getStatusLabel(parcela.statcap)}
                                  </span>
                                </td>
                                <td className="px-6 py-4 text-sm text-slate-600">
                                  {parcela.datpag
                                    ? `Pago: ${formatDate(parcela.datpag)}`
                                    : "-"}
                                </td>
                                <td className="px-6 py-4">
                                  <div className="flex gap-2 justify-center flex-wrap">
                                    <button
                                      onClick={() => openEditParcelaModal(parcela)}
                                      className="px-2 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors text-xs"
                                      title="Editar Parcela"
                                    >
                                      ✏️
                                    </button>

                                    {parcela.statcap === "A_PAGAR" && (
                                      <>
                                        <button
                                          onClick={() => {
                                            setSelectedConta(parcela);
                                            setShowBaixaModal(true);
                                          }}
                                          className="px-2 py-1 bg-green-100 text-green-700 rounded hover:bg-green-200 transition-colors text-xs"
                                          title="Dar Baixa"
                                        >
                                          ✓
                                        </button>
                                        <button
                                          onClick={() =>
                                            handleBaixaAntecipada(parcela)
                                          }
                                          className="px-2 py-1 bg-teal-100 text-teal-700 rounded hover:bg-teal-200 transition-colors text-xs"
                                          title="Baixa Antecipada"
                                        >
                                          ⚡
                                        </button>
                                      </>
                                    )}

                                    {parcela.statcap !== "PAGO" &&
                                      parcela.statcap !== "CANCELADO" && (
                                        <button
                                          onClick={() => handleCancelar(parcela)}
                                          className="px-2 py-1 bg-orange-100 text-orange-700 rounded hover:bg-orange-200 transition-colors text-xs"
                                          title="Cancelar"
                                        >
                                          ✕
                                        </button>
                                      )}

                                    {parcela.statcap !== "PAGO" && (
                                      <button
                                        onClick={() =>
                                          handleDelete(parcela.codcap)
                                        }
                                        className="px-2 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors text-xs"
                                        title="Excluir"
                                      >
                                        🗑️
                                      </button>
                                    )}
                                  </div>
                                </td>
                              </tr>
                            ))}
                          </>
                        )}
                      </React.Fragment>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Modal de Parcelamento */}
      {showParcelamentoModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50 overflow-y-auto">
          <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full my-8">
            <div className="sticky top-0 bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-4 flex justify-between items-center rounded-t-xl">
              <h2 className="text-2xl font-bold">Nova Conta / Parcelamento</h2>
              <button
                onClick={() => {
                  setShowParcelamentoModal(false);
                  resetParcelamentoForm();
                  setSelectedFornecedor(0);
                }}
                className="text-white hover:text-slate-200 text-2xl"
              >
                ×
              </button>
            </div>

            <form onSubmit={handleCreateParcelamento} className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Fornecedor *
                  </label>
                  <select
                    required
                    value={selectedFornecedor}
                    onChange={(e) =>
                      setSelectedFornecedor(parseInt(e.target.value))
                    }
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value={0}>Selecione um fornecedor</option>
                    {fornecedores.map((f) => (
                      <option key={f.codcad} value={f.codcad}>
                        {f.nomcad} {f.doccad ? `- ${f.doccad}` : ""}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Valor Total *
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    required
                    value={parcelamentoForm.vlrtotal}
                    onChange={(e) =>
                      setParcelamentoForm({
                        ...parcelamentoForm,
                        vlrtotal: e.target.value,
                      })
                    }
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="0.00"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Quantidade de Parcelas *
                  </label>
                  <input
                    type="number"
                    min="1"
                    required
                    value={parcelamentoForm.quantidade}
                    onChange={(e) =>
                      setParcelamentoForm({
                        ...parcelamentoForm,
                        quantidade: parseInt(e.target.value) || 1,
                      })
                    }
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Vencimento da 1ª Parcela *
                  </label>
                  <input
                    type="date"
                    required
                    value={parcelamentoForm.datven_primeira}
                    onChange={(e) =>
                      setParcelamentoForm({
                        ...parcelamentoForm,
                        datven_primeira: e.target.value,
                      })
                    }
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Forma de Pagamento
                  </label>
                  <select
                    value={parcelamentoForm.forpag}
                    onChange={(e) =>
                      setParcelamentoForm({
                        ...parcelamentoForm,
                        forpag: e.target.value,
                      })
                    }
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="DINHEIRO">Dinheiro</option>
                    <option value="CARTAO">Cartão</option>
                    <option value="PIX">PIX</option>
                    <option value="BOLETO">Boleto</option>
                    <option value="TRANSFERENCIA">Transferência</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Categoria
                  </label>
                  <input
                    type="text"
                    value={parcelamentoForm.catcap}
                    onChange={(e) =>
                      setParcelamentoForm({
                        ...parcelamentoForm,
                        catcap: e.target.value,
                      })
                    }
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Ex: Fornecedores"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Número do Documento
                  </label>
                  <input
                    type="text"
                    value={parcelamentoForm.numdoc}
                    onChange={(e) =>
                      setParcelamentoForm({
                        ...parcelamentoForm,
                        numdoc: e.target.value,
                      })
                    }
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="NF, Boleto, etc."
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Observações
                  </label>
                  <textarea
                    value={parcelamentoForm.obscap}
                    onChange={(e) =>
                      setParcelamentoForm({
                        ...parcelamentoForm,
                        obscap: e.target.value,
                      })
                    }
                    rows={3}
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Observações adicionais..."
                  />
                </div>

                {parcelamentoForm.vlrtotal &&
                  parcelamentoForm.quantidade > 0 && (
                    <div className="md:col-span-2 p-4 bg-blue-50 rounded-lg">
                      <p className="text-sm text-slate-700">
                        <strong>Valor por parcela:</strong>{" "}
                        {formatCurrency(
                          parseFloat(parcelamentoForm.vlrtotal) /
                            parcelamentoForm.quantidade
                        )}
                      </p>
                    </div>
                  )}
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  type="submit"
                  className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all font-medium"
                >
                  ✓ Criar Parcelamento
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowParcelamentoModal(false);
                    resetParcelamentoForm();
                    setSelectedFornecedor(0);
                  }}
                  className="px-6 py-3 bg-slate-200 text-slate-700 rounded-lg hover:bg-slate-300 transition-colors font-medium"
                >
                  Cancelar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal de Edição de Parcela */}
      {showEditParcelaModal && selectedConta && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-2xl max-w-md w-full">
            <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-4 flex justify-between items-center rounded-t-xl">
              <h2 className="text-xl font-bold">Editar Parcela</h2>
              <button
                onClick={() => {
                  setShowEditParcelaModal(false);
                  setSelectedConta(null);
                }}
                className="text-white hover:text-slate-200 text-2xl"
              >
                ×
              </button>
            </div>

            <div className="p-6">
              <div className="mb-4 p-4 bg-slate-50 rounded-lg">
                <p className="text-sm text-slate-600">
                  Parcela #{selectedConta.numpar}/{selectedConta.totpar}
                </p>
                <p className="text-sm text-slate-600">
                  Grupo #{selectedConta.codgrp}
                </p>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Valor
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={editParcelaForm.vlrcap}
                    onChange={(e) =>
                      setEditParcelaForm({
                        ...editParcelaForm,
                        vlrcap: e.target.value,
                      })
                    }
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Data de Vencimento
                  </label>
                  <input
                    type="date"
                    value={editParcelaForm.datven}
                    onChange={(e) =>
                      setEditParcelaForm({
                        ...editParcelaForm,
                        datven: e.target.value,
                      })
                    }
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Data de Pagamento
                  </label>
                  <input
                    type="date"
                    value={editParcelaForm.datpag}
                    onChange={(e) =>
                      setEditParcelaForm({
                        ...editParcelaForm,
                        datpag: e.target.value,
                      })
                    }
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  onClick={handleEditParcela}
                  className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all font-medium"
                >
                  💾 Salvar Alterações
                </button>
                <button
                  onClick={() => {
                    setShowEditParcelaModal(false);
                    setSelectedConta(null);
                  }}
                  className="px-6 py-3 bg-slate-200 text-slate-700 rounded-lg hover:bg-slate-300 transition-colors font-medium"
                >
                  Cancelar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Baixa */}
      {showBaixaModal && selectedConta && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-2xl max-w-md w-full">
            <div className="bg-gradient-to-r from-green-600 to-green-700 text-white px-6 py-4 flex justify-between items-center rounded-t-xl">
              <h2 className="text-xl font-bold">Dar Baixa na Conta</h2>
              <button
                onClick={() => {
                  setShowBaixaModal(false);
                  setSelectedConta(null);
                }}
                className="text-white hover:text-slate-200 text-2xl"
              >
                ×
              </button>
            </div>

            <div className="p-6">
              <div className="mb-4 p-4 bg-slate-50 rounded-lg">
                <p className="text-sm text-slate-600">
                  Parcela #{selectedConta.numpar}/{selectedConta.totpar}
                </p>
                <p className="text-lg font-bold text-slate-900">
                  {formatCurrency(selectedConta.vlrcap)}
                </p>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Data de Pagamento *
                  </label>
                  <input
                    type="date"
                    required
                    value={baixaForm.datpag}
                    onChange={(e) =>
                      setBaixaForm({ ...baixaForm, datpag: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Forma de Pagamento
                  </label>
                  <select
                    value={baixaForm.forpag}
                    onChange={(e) =>
                      setBaixaForm({ ...baixaForm, forpag: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  >
                    <option value="DINHEIRO">Dinheiro</option>
                    <option value="CARTAO">Cartão</option>
                    <option value="PIX">PIX</option>
                    <option value="BOLETO">Boleto</option>
                    <option value="TRANSFERENCIA">Transferência</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Observações
                  </label>
                  <textarea
                    value={baixaForm.obscap}
                    onChange={(e) =>
                      setBaixaForm({ ...baixaForm, obscap: e.target.value })
                    }
                    rows={3}
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    placeholder="Observações sobre o pagamento..."
                  />
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  onClick={handleBaixa}
                  className="flex-1 px-6 py-3 bg-gradient-to-r from-green-600 to-green-700 text-white rounded-lg hover:from-green-700 hover:to-green-800 transition-all font-medium"
                >
                  ✓ Confirmar Baixa
                </button>
                <button
                  onClick={() => {
                    setShowBaixaModal(false);
                    setSelectedConta(null);
                  }}
                  className="px-6 py-3 bg-slate-200 text-slate-700 rounded-lg hover:bg-slate-300 transition-colors font-medium"
                >
                  Cancelar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
