// src/pages/CadastrosPage.tsx
import React, { useState, useCallback, useEffect } from "react";
import api from "../api";

// ========== TYPES ==========
type CadastroGeral = {
  codcad: number;
  tipocad: "FORNECEDOR" | "CLIENTE" | "USUARIO" | "OUTRO";
  nomcad: string;
  doccad: string | null;
  emacad: string | null;
  telcad: string | null;
  endcad: string | null;
  obscad: string | null;
  statcad: "ATIVO" | "INATIVO";
  created_at: string;
  updated_at: string;
  codemp: number;
  codfil: number;
};

type CreateForm = {
  tipocad: string;
  nomcad: string;
  doccad: string;
  emacad: string;
  telcad: string;
  endcad: string;
  obscad: string;
  statcad: string;
};

type CountByType = {
  tipocad: string;
  count: number;
};

// ========== HELPER FUNCTIONS ==========
const getTipoLabel = (tipo: string): string => {
  const labels: Record<string, string> = {
    FORNECEDOR: "Fornecedor",
    CLIENTE: "Cliente",
    USUARIO: "Usuário",
    OUTRO: "Outro",
  };
  return labels[tipo] || tipo;
};

const getTipoColor = (tipo: string): string => {
  const colors: Record<string, string> = {
    FORNECEDOR: "bg-blue-100 text-blue-800 border-blue-300",
    CLIENTE: "bg-green-100 text-green-800 border-green-300",
    USUARIO: "bg-purple-100 text-purple-800 border-purple-300",
    OUTRO: "bg-gray-100 text-gray-800 border-gray-300",
  };
  return colors[tipo] || "bg-gray-100 text-gray-800";
};

const getStatusLabel = (status: string): string => {
  const labels: Record<string, string> = {
    ATIVO: "Ativo",
    INATIVO: "Inativo",
  };
  return labels[status] || status;
};

const getStatusColor = (status: string): string => {
  const colors: Record<string, string> = {
    ATIVO: "bg-green-100 text-green-800 border-green-300",
    INATIVO: "bg-red-100 text-red-800 border-red-300",
  };
  return colors[status] || "bg-gray-100 text-gray-800";
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
export default function CadastrosPage() {
  const [cadastros, setCadastros] = useState<CadastroGeral[]>([]);
  const [countByType, setCountByType] = useState<CountByType[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [selectedCadastro, setSelectedCadastro] = useState<CadastroGeral | null>(null);

  // Filtros e busca
  const [filterTipo, setFilterTipo] = useState<string>("");
  const [filterStatus, setFilterStatus] = useState<string>("");
  const [searchTerm, setSearchTerm] = useState<string>("");

  // Form de criação/edição
  const [form, setForm] = useState<CreateForm>({
    tipocad: "FORNECEDOR",
    nomcad: "",
    doccad: "",
    emacad: "",
    telcad: "",
    endcad: "",
    obscad: "",
    statcad: "ATIVO",
  });

  const ENDPOINT = "/cadastros-gerais";

  // ========== LOAD CADASTROS ==========
  const loadCadastros = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params: any = {};
      if (filterTipo) params.tipocad = filterTipo;
      if (filterStatus) params.statcad = filterStatus;

      const res = await api.get<CadastroGeral[]>(ENDPOINT, { params });
      setCadastros(res.data || []);
    } catch (e: any) {
      console.error(e);
      setError(getErrMsg(e));
    } finally {
      setLoading(false);
    }
  }, [filterTipo, filterStatus]);

  // ========== LOAD COUNT BY TYPE ==========
  const loadCountByType = useCallback(async () => {
    try {
      const res = await api.get<CountByType[]>(`${ENDPOINT}/count-by-type`);
      setCountByType(res.data || []);
    } catch (e: any) {
      console.error("Erro ao carregar estatísticas:", e);
    }
  }, []);

  useEffect(() => {
    loadCadastros();
    loadCountByType();
  }, [loadCadastros, loadCountByType]);

  // ========== FILTERED CADASTROS ==========
  const filteredCadastros = cadastros.filter((cad) => {
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      return (
        cad.nomcad.toLowerCase().includes(term) ||
        (cad.doccad && cad.doccad.toLowerCase().includes(term))
      );
    }
    return true;
  });

  // ========== CREATE ==========
  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (!form.nomcad.trim()) {
      setError("Nome é obrigatório");
      return;
    }

    try {
      await api.post(ENDPOINT, {
        tipocad: form.tipocad,
        nomcad: form.nomcad.trim(),
        doccad: form.doccad.trim() || null,
        emacad: form.emacad.trim() || null,
        telcad: form.telcad.trim() || null,
        endcad: form.endcad.trim() || null,
        obscad: form.obscad.trim() || null,
        statcad: form.statcad,
      });

      setSuccess("Cadastro criado com sucesso!");
      setShowModal(false);
      resetForm();
      await loadCadastros();
      await loadCountByType();
    } catch (e: any) {
      console.error(e);
      setError(getErrMsg(e));
    }
  };

  // ========== UPDATE ==========
  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCadastro) return;

    setError(null);
    setSuccess(null);

    try {
      await api.put(`${ENDPOINT}/${selectedCadastro.codcad}`, {
        tipocad: form.tipocad,
        nomcad: form.nomcad.trim(),
        doccad: form.doccad.trim() || null,
        emacad: form.emacad.trim() || null,
        telcad: form.telcad.trim() || null,
        endcad: form.endcad.trim() || null,
        obscad: form.obscad.trim() || null,
        statcad: form.statcad,
      });

      setSuccess("Cadastro atualizado com sucesso!");
      setShowModal(false);
      setIsEditing(false);
      setSelectedCadastro(null);
      resetForm();
      await loadCadastros();
      await loadCountByType();
    } catch (e: any) {
      console.error(e);
      setError(getErrMsg(e));
    }
  };

  // ========== TOGGLE STATUS ==========
  const handleToggleStatus = async (cadastro: CadastroGeral) => {
    const newStatus = cadastro.statcad === "ATIVO" ? "INATIVO" : "ATIVO";
    const action = newStatus === "INATIVO" ? "inativar" : "ativar";

    if (!confirm(`Deseja realmente ${action} este cadastro?`)) return;

    setError(null);
    setSuccess(null);

    try {
      await api.delete(`${ENDPOINT}/${cadastro.codcad}`);
      setSuccess(`Cadastro ${action === "inativar" ? "inativado" : "ativado"} com sucesso!`);
      await loadCadastros();
      await loadCountByType();
    } catch (e: any) {
      console.error(e);
      setError(getErrMsg(e));
    }
  };

  // ========== OPEN CREATE MODAL ==========
  const openCreateModal = () => {
    resetForm();
    setIsEditing(false);
    setSelectedCadastro(null);
    setShowModal(true);
  };

  // ========== OPEN EDIT MODAL ==========
  const openEditModal = (cadastro: CadastroGeral) => {
    setForm({
      tipocad: cadastro.tipocad,
      nomcad: cadastro.nomcad,
      doccad: cadastro.doccad || "",
      emacad: cadastro.emacad || "",
      telcad: cadastro.telcad || "",
      endcad: cadastro.endcad || "",
      obscad: cadastro.obscad || "",
      statcad: cadastro.statcad,
    });
    setSelectedCadastro(cadastro);
    setIsEditing(true);
    setShowModal(true);
  };

  // ========== RESET FORM ==========
  const resetForm = () => {
    setForm({
      tipocad: "FORNECEDOR",
      nomcad: "",
      doccad: "",
      emacad: "",
      telcad: "",
      endcad: "",
      obscad: "",
      statcad: "ATIVO",
    });
  };

  // ========== GET COUNT FOR TYPE ==========
  const getCountForType = (tipo: string): number => {
    const found = countByType.find((c) => c.tipocad === tipo);
    return found ? found.count : 0;
  };

  // ========== RENDER ==========
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-slate-800 mb-2">
            📑 Cadastros Gerais
          </h1>
          <p className="text-slate-600">
            Gerencie fornecedores, clientes, usuários e outros cadastros
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
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-lg p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-100 text-sm font-medium">Fornecedores</p>
                <p className="text-3xl font-bold mt-1">{getCountForType("FORNECEDOR")}</p>
              </div>
              <div className="text-4xl opacity-80">📦</div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl shadow-lg p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-100 text-sm font-medium">Clientes</p>
                <p className="text-3xl font-bold mt-1">{getCountForType("CLIENTE")}</p>
              </div>
              <div className="text-4xl opacity-80">👥</div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl shadow-lg p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-100 text-sm font-medium">Usuários</p>
                <p className="text-3xl font-bold mt-1">{getCountForType("USUARIO")}</p>
              </div>
              <div className="text-4xl opacity-80">👤</div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-gray-500 to-gray-600 rounded-xl shadow-lg p-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-100 text-sm font-medium">Outros</p>
                <p className="text-3xl font-bold mt-1">{getCountForType("OUTRO")}</p>
              </div>
              <div className="text-4xl opacity-80">📋</div>
            </div>
          </div>
        </div>

        {/* Filters Bar */}
        <div className="bg-white rounded-xl shadow-md p-6 mb-6">
          <div className="flex flex-wrap gap-4 items-center justify-between">
            <div className="flex gap-3 flex-wrap flex-1">
              <input
                type="text"
                placeholder="🔍 Buscar por nome ou documento..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent flex-1 min-w-[200px]"
              />

              <select
                value={filterTipo}
                onChange={(e) => setFilterTipo(e.target.value)}
                className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Todos os Tipos</option>
                <option value="FORNECEDOR">Fornecedor</option>
                <option value="CLIENTE">Cliente</option>
                <option value="USUARIO">Usuário</option>
                <option value="OUTRO">Outro</option>
              </select>

              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Todos os Status</option>
                <option value="ATIVO">Ativo</option>
                <option value="INATIVO">Inativo</option>
              </select>

              <button
                onClick={() => {
                  loadCadastros();
                  loadCountByType();
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
              ➕ Novo Cadastro
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
          ) : filteredCadastros.length === 0 ? (
            <div className="p-12 text-center text-slate-500">
              <p className="text-lg">📭 Nenhum cadastro encontrado</p>
              <p className="text-sm mt-2">
                {searchTerm
                  ? "Tente ajustar os filtros de busca"
                  : "Crie seu primeiro cadastro"}
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
                      Nome
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                      Tipo
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                      Documento
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                      E-mail
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                      Telefone
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-4 text-center text-xs font-semibold text-slate-600 uppercase tracking-wider">
                      Ações
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredCadastros.map((cadastro) => (
                    <tr
                      key={cadastro.codcad}
                      className="hover:bg-slate-50 transition-colors"
                    >
                      <td className="px-6 py-4 text-sm text-slate-900">
                        #{cadastro.codcad}
                      </td>
                      <td className="px-6 py-4 text-sm font-medium text-slate-900">
                        {cadastro.nomcad}
                      </td>
                      <td className="px-6 py-4">
                        <span
                          className={`inline-flex px-3 py-1 text-xs font-medium rounded-full border ${getTipoColor(
                            cadastro.tipocad
                          )}`}
                        >
                          {getTipoLabel(cadastro.tipocad)}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-slate-600">
                        {cadastro.doccad || "-"}
                      </td>
                      <td className="px-6 py-4 text-sm text-slate-600">
                        {cadastro.emacad || "-"}
                      </td>
                      <td className="px-6 py-4 text-sm text-slate-600">
                        {cadastro.telcad || "-"}
                      </td>
                      <td className="px-6 py-4">
                        <span
                          className={`inline-flex px-3 py-1 text-xs font-medium rounded-full border ${getStatusColor(
                            cadastro.statcad
                          )}`}
                        >
                          {getStatusLabel(cadastro.statcad)}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex gap-2 justify-center">
                          <button
                            onClick={() => openEditModal(cadastro)}
                            className="px-3 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors text-sm"
                            title="Editar"
                          >
                            ✏️ Editar
                          </button>
                          <button
                            onClick={() => handleToggleStatus(cadastro)}
                            className={`px-3 py-1 rounded hover:opacity-80 transition-colors text-sm ${
                              cadastro.statcad === "ATIVO"
                                ? "bg-orange-100 text-orange-700"
                                : "bg-green-100 text-green-700"
                            }`}
                            title={
                              cadastro.statcad === "ATIVO"
                                ? "Inativar"
                                : "Ativar"
                            }
                          >
                            {cadastro.statcad === "ATIVO" ? "⏸️ Inativar" : "▶️ Ativar"}
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Modal de Criação/Edição */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-4 flex justify-between items-center">
              <h2 className="text-2xl font-bold">
                {isEditing ? "Editar Cadastro" : "Novo Cadastro"}
              </h2>
              <button
                onClick={() => {
                  setShowModal(false);
                  setIsEditing(false);
                  setSelectedCadastro(null);
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
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Tipo de Cadastro *
                  </label>
                  <select
                    required
                    value={form.tipocad}
                    onChange={(e) =>
                      setForm({ ...form, tipocad: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="FORNECEDOR">Fornecedor</option>
                    <option value="CLIENTE">Cliente</option>
                    <option value="USUARIO">Usuário</option>
                    <option value="OUTRO">Outro</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Status *
                  </label>
                  <select
                    required
                    value={form.statcad}
                    onChange={(e) =>
                      setForm({ ...form, statcad: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="ATIVO">Ativo</option>
                    <option value="INATIVO">Inativo</option>
                  </select>
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Nome *
                  </label>
                  <input
                    type="text"
                    required
                    value={form.nomcad}
                    onChange={(e) =>
                      setForm({ ...form, nomcad: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Nome completo"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Documento (CPF/CNPJ)
                  </label>
                  <input
                    type="text"
                    value={form.doccad}
                    onChange={(e) =>
                      setForm({ ...form, doccad: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="000.000.000-00"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Telefone
                  </label>
                  <input
                    type="text"
                    value={form.telcad}
                    onChange={(e) =>
                      setForm({ ...form, telcad: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="(00) 00000-0000"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    E-mail
                  </label>
                  <input
                    type="email"
                    value={form.emacad}
                    onChange={(e) =>
                      setForm({ ...form, emacad: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="email@exemplo.com"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Endereço
                  </label>
                  <input
                    type="text"
                    value={form.endcad}
                    onChange={(e) =>
                      setForm({ ...form, endcad: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Rua, número, bairro, cidade - UF"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Observações
                  </label>
                  <textarea
                    value={form.obscad}
                    onChange={(e) =>
                      setForm({ ...form, obscad: e.target.value })
                    }
                    rows={3}
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Observações adicionais..."
                  />
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  type="submit"
                  className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all font-medium"
                >
                  {isEditing ? "💾 Salvar Alterações" : "✓ Criar Cadastro"}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false);
                    setIsEditing(false);
                    setSelectedCadastro(null);
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
