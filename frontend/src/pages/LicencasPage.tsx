// src/pages/LicencasPage.tsx
import React, { useState, useCallback, useEffect } from "react";
import api from "../api";

// ========== TYPES ==========
type Licenca = {
  codlic: number;
  nomlic: string;
  cnplic: string | null;
  chavelic: string;
  datini: string;
  datenc: string;
  statlic: "ATIVA" | "INATIVA" | "VENCIDA";
  statpag: "PAGO" | "PENDENTE";
  created_at: string;
  updated_at: string;
};

type DashboardStats = {
  total: number;
  ativas: number;
  vencidas: number;
  a_vencer: number;
  inadimplentes: number;
};

type CreateForm = {
  nomlic: string;
  cnplic: string;
  datini: string;
  datenc: string;
  statpag: string;
};

// ========== HELPER FUNCTIONS ==========
const formatDate = (dateStr: string): string => {
  const date = new Date(dateStr);
  return date.toLocaleDateString("pt-BR");
};

const getStatusColor = (status: string): string => {
  const colors: Record<string, string> = {
    ATIVA: "bg-green-100 text-green-800 border-green-300",
    INATIVA: "bg-gray-100 text-gray-800 border-gray-300",
    VENCIDA: "bg-red-100 text-red-800 border-red-300",
  };
  return colors[status] || "bg-gray-100 text-gray-800";
};

const getStatusLabel = (status: string): string => {
  const labels: Record<string, string> = {
    ATIVA: "Ativa",
    INATIVA: "Inativa",
    VENCIDA: "Vencida",
  };
  return labels[status] || status;
};

const getPagamentoColor = (status: string): string => {
  const colors: Record<string, string> = {
    PAGO: "bg-green-100 text-green-800 border-green-300",
    PENDENTE: "bg-orange-100 text-orange-800 border-orange-300",
  };
  return colors[status] || "bg-gray-100 text-gray-800";
};

const getPagamentoLabel = (status: string): string => {
  const labels: Record<string, string> = {
    PAGO: "Pago",
    PENDENTE: "Pendente",
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

const calcularDiasParaVencer = (datenc: string): number => {
  const hoje = new Date();
  const vencimento = new Date(datenc);
  const diff = vencimento.getTime() - hoje.getTime();
  return Math.ceil(diff / (1000 * 60 * 60 * 24));
};

// ========== COMPONENT ==========
export default function LicencasPage() {
  const [licencas, setLicencas] = useState<Licenca[]>([]);
  const [dashboard, setDashboard] = useState<DashboardStats>({
    total: 0,
    ativas: 0,
    vencidas: 0,
    a_vencer: 0,
    inadimplentes: 0,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [selectedLicenca, setSelectedLicenca] = useState<Licenca | null>(null);
  const [copiedChave, setCopiedChave] = useState<string | null>(null);

  // Filtros
  const [filterStatus, setFilterStatus] = useState<string>("");
  const [filterPagamento, setFilterPagamento] = useState<string>("");
  const [searchTerm, setSearchTerm] = useState<string>("");

  // Form de criação/edição
  const [form, setForm] = useState<CreateForm>({
    nomlic: "",
    cnplic: "",
    datini: "",
    datenc: "",
    statpag: "PAGO",
  });

  const ENDPOINT = "/licencas";

  // ========== LOAD LICENCAS ==========
  const loadLicencas = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params: any = {};
      if (filterStatus) params.statlic = filterStatus;
      if (filterPagamento) params.statpag = filterPagamento;

      const res = await api.get<Licenca[]>(ENDPOINT, { params });
      setLicencas(res.data || []);
    } catch (e: any) {
      console.error(e);
      setError(getErrMsg(e));
    } finally {
      setLoading(false);
    }
  }, [filterStatus, filterPagamento]);

  // ========== LOAD DASHBOARD ==========
  const loadDashboard = useCallback(async () => {
    try {
      const res = await api.get<DashboardStats>(`${ENDPOINT}/dashboard`);
      setDashboard(res.data);
    } catch (e: any) {
      console.error("Erro ao carregar dashboard:", e);
    }
  }, []);

  useEffect(() => {
    loadLicencas();
    loadDashboard();
  }, [loadLicencas, loadDashboard]);

  // ========== FILTERED LICENCAS ==========
  const filteredLicencas = licencas.filter((lic) => {
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      return (
        lic.nomlic.toLowerCase().includes(term) ||
        (lic.cnplic && lic.cnplic.toLowerCase().includes(term)) ||
        lic.chavelic.toLowerCase().includes(term)
      );
    }
    return true;
  });

  // ========== CREATE ==========
  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (!form.nomlic.trim()) {
      setError("Nome da empresa/filial é obrigatório");
      return;
    }

    if (!form.datini || !form.datenc) {
      setError("Informe as datas de início e encerramento");
      return;
    }

    try {
      const res = await api.post<Licenca>(ENDPOINT, {
        nomlic: form.nomlic.trim(),
        cnplic: form.cnplic.trim() || null,
        datini: form.datini,
        datenc: form.datenc,
        statpag: form.statpag,
      });

      setSuccess(
        `Licença criada com sucesso! Chave: ${res.data.chavelic}`
      );
      setShowModal(false);
      resetForm();
      await loadLicencas();
      await loadDashboard();
      
      // Copiar chave automaticamente
      handleCopyChave(res.data.chavelic);
    } catch (e: any) {
      console.error(e);
      setError(getErrMsg(e));
    }
  };

  // ========== UPDATE ==========
  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedLicenca) return;

    setError(null);
    setSuccess(null);

    try {
      await api.put(`${ENDPOINT}/${selectedLicenca.codlic}`, {
        nomlic: form.nomlic.trim(),
        cnplic: form.cnplic.trim() || null,
        datini: form.datini,
        datenc: form.datenc,
        statpag: form.statpag,
      });

      setSuccess("Licença atualizada com sucesso!");
      setShowModal(false);
      setIsEditing(false);
      setSelectedLicenca(null);
      resetForm();
      await loadLicencas();
      await loadDashboard();
    } catch (e: any) {
      console.error(e);
      setError(getErrMsg(e));
    }
  };

  // ========== RENOVAR ==========
  const handleRenovar = async (licenca: Licenca) => {
    const meses = prompt("Por quantos meses deseja renovar a licença?", "12");
    if (!meses) return;

    const numMeses = parseInt(meses);
    if (isNaN(numMeses) || numMeses <= 0) {
      setError("Informe um número válido de meses");
      return;
    }

    setError(null);
    setSuccess(null);

    try {
      await api.post(`${ENDPOINT}/${licenca.codlic}/renovar`, {
        meses: numMeses,
      });

      setSuccess(
        `Licença renovada com sucesso por ${numMeses} ${
          numMeses === 1 ? "mês" : "meses"
        }!`
      );
      await loadLicencas();
      await loadDashboard();
    } catch (e: any) {
      console.error(e);
      setError(getErrMsg(e));
    }
  };

  // ========== ATIVAR ==========
  const handleAtivar = async (licenca: Licenca) => {
    if (!confirm("Deseja ativar esta licença?")) return;

    setError(null);
    setSuccess(null);

    try {
      await api.post(`${ENDPOINT}/${licenca.codlic}/ativar`);
      setSuccess("Licença ativada com sucesso!");
      await loadLicencas();
      await loadDashboard();
    } catch (e: any) {
      console.error(e);
      setError(getErrMsg(e));
    }
  };

  // ========== DESATIVAR ==========
  const handleDesativar = async (licenca: Licenca) => {
    if (!confirm("Deseja desativar esta licença?")) return;

    setError(null);
    setSuccess(null);

    try {
      await api.post(`${ENDPOINT}/${licenca.codlic}/desativar`);
      setSuccess("Licença desativada com sucesso!");
      await loadLicencas();
      await loadDashboard();
    } catch (e: any) {
      console.error(e);
      setError(getErrMsg(e));
    }
  };

  // ========== DELETE ==========
  const handleDelete = async (codlic: number) => {
    if (!confirm("Deseja realmente excluir esta licença? Esta ação não pode ser desfeita.")) return;

    setError(null);
    setSuccess(null);

    try {
      await api.delete(`${ENDPOINT}/${codlic}`);
      setSuccess("Licença excluída com sucesso!");
      await loadLicencas();
      await loadDashboard();
    } catch (e: any) {
      console.error(e);
      setError(getErrMsg(e));
    }
  };

  // ========== COPY CHAVE ==========
  const handleCopyChave = (chave: string) => {
    navigator.clipboard.writeText(chave).then(() => {
      setCopiedChave(chave);
      setTimeout(() => setCopiedChave(null), 2000);
    });
  };

  // ========== OPEN CREATE MODAL ==========
  const openCreateModal = () => {
    resetForm();
    setIsEditing(false);
    setSelectedLicenca(null);
    setShowModal(true);
  };

  // ========== OPEN EDIT MODAL ==========
  const openEditModal = (licenca: Licenca) => {
    setForm({
      nomlic: licenca.nomlic,
      cnplic: licenca.cnplic || "",
      datini: licenca.datini.split("T")[0],
      datenc: licenca.datenc.split("T")[0],
      statpag: licenca.statpag,
    });
    setSelectedLicenca(licenca);
    setIsEditing(true);
    setShowModal(true);
  };

  // ========== RESET FORM ==========
  const resetForm = () => {
    setForm({
      nomlic: "",
      cnplic: "",
      datini: "",
      datenc: "",
      statpag: "PAGO",
    });
  };

  // ========== RENDER ==========
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-slate-800 mb-2">
            🔑 Gestão de Licenças
          </h1>
          <p className="text-slate-600">
            Gerencie licenças de empresas e filiais (SuperAdmin)
          </p>
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

        {/* Dashboard - Estatísticas */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-6">
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-lg p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-100 text-sm font-medium">Total</p>
                <p className="text-3xl font-bold mt-1">{dashboard.total}</p>
              </div>
              <div className="text-4xl opacity-80">📊</div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl shadow-lg p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-100 text-sm font-medium">Ativas</p>
                <p className="text-3xl font-bold mt-1">{dashboard.ativas}</p>
              </div>
              <div className="text-4xl opacity-80">✅</div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-red-500 to-red-600 rounded-xl shadow-lg p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-red-100 text-sm font-medium">Vencidas</p>
                <p className="text-3xl font-bold mt-1">{dashboard.vencidas}</p>
              </div>
              <div className="text-4xl opacity-80">❌</div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-yellow-500 to-yellow-600 rounded-xl shadow-lg p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-yellow-100 text-sm font-medium">A Vencer</p>
                <p className="text-3xl font-bold mt-1">{dashboard.a_vencer}</p>
              </div>
              <div className="text-4xl opacity-80">⏰</div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl shadow-lg p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-orange-100 text-sm font-medium">
                  Inadimplentes
                </p>
                <p className="text-3xl font-bold mt-1">
                  {dashboard.inadimplentes}
                </p>
              </div>
              <div className="text-4xl opacity-80">💸</div>
            </div>
          </div>
        </div>

        {/* Filters Bar */}
        <div className="bg-white rounded-xl shadow-md p-6 mb-6">
          <div className="flex flex-wrap gap-4 items-center justify-between">
            <div className="flex gap-3 flex-wrap flex-1">
              <input
                type="text"
                placeholder="🔍 Buscar por nome, CNPJ ou chave..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent flex-1 min-w-[200px]"
              />

              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Todos os Status</option>
                <option value="ATIVA">Ativa</option>
                <option value="INATIVA">Inativa</option>
                <option value="VENCIDA">Vencida</option>
              </select>

              <select
                value={filterPagamento}
                onChange={(e) => setFilterPagamento(e.target.value)}
                className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Todos os Pagamentos</option>
                <option value="PAGO">Pago</option>
                <option value="PENDENTE">Pendente</option>
              </select>

              <button
                onClick={() => {
                  loadLicencas();
                  loadDashboard();
                }}
                className="px-4 py-2 bg-slate-600 text-white rounded-lg hover:bg-slate-700 transition-colors flex items-center gap-2"
              >
                🔄 Atualizar
              </button>
            </div>

            <button
              onClick={openCreateModal}
              className="px-6 py-2 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all shadow-md flex items-center gap-2"
            >
              ➕ Nova Licença
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
          ) : filteredLicencas.length === 0 ? (
            <div className="p-12 text-center text-slate-500">
              <p className="text-lg">📭 Nenhuma licença encontrada</p>
              <p className="text-sm mt-2">
                {searchTerm
                  ? "Tente ajustar os filtros de busca"
                  : "Crie sua primeira licença"}
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-50 border-b-2 border-slate-200">
                  <tr>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                      ID
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                      Empresa/Filial
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                      CNPJ
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                      Chave
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                      Início
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                      Encerramento
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                      Pagamento
                    </th>
                    <th className="px-6 py-4 text-center text-xs font-semibold text-slate-600 uppercase tracking-wider">
                      Ações
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredLicencas.map((licenca) => {
                    const diasParaVencer = calcularDiasParaVencer(
                      licenca.datenc
                    );

                    return (
                      <tr
                        key={licenca.codlic}
                        className="hover:bg-slate-50 transition-colors"
                      >
                        <td className="px-6 py-4 text-sm text-slate-900">
                          #{licenca.codlic}
                        </td>
                        <td className="px-6 py-4 text-sm font-medium text-slate-900">
                          {licenca.nomlic}
                        </td>
                        <td className="px-6 py-4 text-sm text-slate-600">
                          {licenca.cnplic || "-"}
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-2">
                            <code className="text-xs bg-slate-100 px-2 py-1 rounded font-mono">
                              {licenca.chavelic.substring(0, 16)}...
                            </code>
                            <button
                              onClick={() => handleCopyChave(licenca.chavelic)}
                              className="px-2 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors text-xs"
                              title="Copiar chave completa"
                            >
                              {copiedChave === licenca.chavelic ? "✓" : "📋"}
                            </button>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-sm text-slate-600">
                          {formatDate(licenca.datini)}
                        </td>
                        <td className="px-6 py-4 text-sm text-slate-600">
                          {formatDate(licenca.datenc)}
                          {diasParaVencer > 0 &&
                            diasParaVencer <= 30 &&
                            licenca.statlic === "ATIVA" && (
                              <div className="text-xs text-orange-600 mt-1">
                                ⚠️ {diasParaVencer}{" "}
                                {diasParaVencer === 1 ? "dia" : "dias"}
                              </div>
                            )}
                        </td>
                        <td className="px-6 py-4">
                          <span
                            className={`inline-flex px-3 py-1 text-xs font-medium rounded-full border ${getStatusColor(
                              licenca.statlic
                            )}`}
                          >
                            {getStatusLabel(licenca.statlic)}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <span
                            className={`inline-flex px-3 py-1 text-xs font-medium rounded-full border ${getPagamentoColor(
                              licenca.statpag
                            )}`}
                          >
                            {getPagamentoLabel(licenca.statpag)}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex gap-2 justify-center flex-wrap">
                            <button
                              onClick={() => openEditModal(licenca)}
                              className="px-2 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors text-xs"
                              title="Editar"
                            >
                              ✏️
                            </button>

                            <button
                              onClick={() => handleRenovar(licenca)}
                              className="px-2 py-1 bg-purple-100 text-purple-700 rounded hover:bg-purple-200 transition-colors text-xs"
                              title="Renovar"
                            >
                              🔄
                            </button>

                            {licenca.statlic !== "ATIVA" ? (
                              <button
                                onClick={() => handleAtivar(licenca)}
                                className="px-2 py-1 bg-green-100 text-green-700 rounded hover:bg-green-200 transition-colors text-xs"
                                title="Ativar"
                              >
                                ▶️
                              </button>
                            ) : (
                              <button
                                onClick={() => handleDesativar(licenca)}
                                className="px-2 py-1 bg-orange-100 text-orange-700 rounded hover:bg-orange-200 transition-colors text-xs"
                                title="Desativar"
                              >
                                ⏸️
                              </button>
                            )}

                            <button
                              onClick={() => handleDelete(licenca.codlic)}
                              className="px-2 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors text-xs"
                              title="Excluir"
                            >
                              🗑️
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Modal de Criação/Edição */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-4 flex justify-between items-center">
              <h2 className="text-2xl font-bold">
                {isEditing ? "Editar Licença" : "Nova Licença"}
              </h2>
              <button
                onClick={() => {
                  setShowModal(false);
                  setIsEditing(false);
                  setSelectedLicenca(null);
                  resetForm();
                }}
                className="text-white hover:text-slate-200 text-2xl"
              >
                ×
              </button>
            </div>

            <form
              onSubmit={isEditing ? handleUpdate : handleCreate}
              className="p-6"
            >
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Nome da Empresa/Filial *
                  </label>
                  <input
                    type="text"
                    required
                    value={form.nomlic}
                    onChange={(e) =>
                      setForm({ ...form, nomlic: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Nome da empresa ou filial"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    CNPJ
                  </label>
                  <input
                    type="text"
                    value={form.cnplic}
                    onChange={(e) =>
                      setForm({ ...form, cnplic: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="00.000.000/0000-00"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Data de Início *
                  </label>
                  <input
                    type="date"
                    required
                    value={form.datini}
                    onChange={(e) =>
                      setForm({ ...form, datini: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Data de Encerramento *
                  </label>
                  <input
                    type="date"
                    required
                    value={form.datenc}
                    onChange={(e) =>
                      setForm({ ...form, datenc: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Status de Pagamento *
                  </label>
                  <select
                    required
                    value={form.statpag}
                    onChange={(e) =>
                      setForm({ ...form, statpag: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="PAGO">Pago</option>
                    <option value="PENDENTE">Pendente</option>
                  </select>
                </div>

                {!isEditing && (
                  <div className="md:col-span-2 p-4 bg-blue-50 rounded-lg">
                    <p className="text-sm text-slate-700">
                      <strong>ℹ️ Nota:</strong> A chave de licença será gerada
                      automaticamente após a criação.
                    </p>
                  </div>
                )}
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  type="submit"
                  className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all font-medium"
                >
                  {isEditing ? "💾 Salvar Alterações" : "✓ Criar Licença"}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false);
                    setIsEditing(false);
                    setSelectedLicenca(null);
                    resetForm();
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
    </div>
  );
}
