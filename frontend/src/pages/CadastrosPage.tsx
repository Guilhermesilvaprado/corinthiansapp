import React, { useEffect, useMemo, useState } from "react";
import axios from "axios";

// Ajuste se sua API tiver prefixo /api
const API_BASE = "http://127.0.0.1:8000";

type Pessoa = {
  codpes: number;     // PK
  tippes?: "F" | "J";
  codtre?: number | null;
  nompes: string;
  fanpes?: string | null;
  cpfpes?: string | null;
  cnppes?: string | null;
  em1pes?: string | null;
  em2pes?: string | null;
  celpes?: string | null;
  sitpes?: "A" | "I" | null;
  endpes?: string | null;
  numpes?: string | null;
  baipes?: string | null;
  cidpes?: string | null;
  estpes?: string | null;
  ceppes?: string | null;
};

type FormState = {
  tippes: "F" | "J";
  codtre: string;
  nompes: string;
  fanpes: string;
  cpfpes: string;
  cnppes: string;
  em1pes: string;
  em2pes: string;
  celpes: string;
  sitpes: string; // "Ativo" | "Inativo" | "" (UI), convertemos para "A"/"I" no payload
  endpes: string;
  numpes: string;
  baipes: string;
  cidpes: string;
  estpes: string;
  ceppes: string;
};

const initialForm: FormState = {
  tippes: "F",
  codtre: "",
  nompes: "",
  fanpes: "",
  cpfpes: "",
  cnppes: "",
  em1pes: "",
  em2pes: "",
  celpes: "",
  sitpes: "",
  endpes: "",
  numpes: "",
  baipes: "",
  cidpes: "",
  estpes: "",
  ceppes: "",
};

const toNull = (v: string) => (v?.trim() === "" ? null : v.trim());

const mapSituacaoOut = (v?: string | null) => {
  if (!v) return null;
  const up = v.toUpperCase();
  if (up === "ATIVO") return "A";
  if (up === "INATIVO") return "I";
  if (["A", "I"].includes(up)) return up as "A" | "I";
  return null;
};

const mapSituacaoIn = (v?: string | null) => {
  if (!v) return "";
  const up = v.toUpperCase();
  if (up === "A") return "Ativo";
  if (up === "I") return "Inativo";
  return "";
};

const labelTipo = (t?: string | null) => (t === "J" ? "Jurídica" : "Física");

const labelDoc = (p: Pessoa) => (p.tippes === "J" ? p.cnppes || "-" : p.cpfpes || "-");

const labelSituacao = (s?: string | null) => (s === "A" ? "Ativo" : s === "I" ? "Inativo" : "-");

// Axios com token do localStorage
const axiosWithAuth = () => {
  const token = localStorage.getItem("token");
  const instance = axios.create({
    baseURL: API_BASE,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
  return instance;
};

const CadastrosPage: React.FC = () => {
  const [pessoas, setPessoas] = useState<Pessoa[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [showModal, setShowModal] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);

  const [form, setForm] = useState<FormState>(initialForm);

  const client = useMemo(() => axiosWithAuth(), []);

  const fetchPessoas = async () => {
    try {
      setLoading(true);
      setError(null);
      const resp = await client.get<Pessoa[]>("/pessoas/");
      setPessoas(resp.data || []);
    } catch (e: any) {
      console.error(e);
      setError(e?.response?.data?.detail || "Erro ao carregar pessoas");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPessoas();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const resetForm = () => {
    setForm(initialForm);
    setIsEditing(false);
    setEditingId(null);
  };

  const buildPayload = (f: FormState) => {
    const payload: any = {
      tippes: f.tippes,
      codtre: f.codtre ? Number(f.codtre) : null,
      nompes: f.nompes.trim(),
      fanpes: toNull(f.fanpes),
      endpes: toNull(f.endpes),
      numpes: toNull(f.numpes),
      baipes: toNull(f.baipes),
      cidpes: toNull(f.cidpes),
      estpes: toNull(f.estpes),
      ceppes: toNull(f.ceppes),
      em1pes: toNull(f.em1pes),
      em2pes: toNull(f.em2pes),
      celpes: toNull(f.celpes),
      sitpes: mapSituacaoOut(f.sitpes), // A/I
    };

    if (f.tippes === "F") {
      payload.cpfpes = toNull(f.cpfpes);
      payload.cnppes = null;
    } else {
      payload.cpfpes = null;
      payload.cnppes = toNull(f.cnppes);
    }

    return payload;
  };

  const openCreate = () => {
    resetForm();
    setIsEditing(false);
    setShowModal(true);
  };

  const openEdit = (p: Pessoa) => {
    setIsEditing(true);
    setEditingId(p.codpes);
    setForm({
      tippes: (p.tippes as "F" | "J") || "F",
      codtre: p.codtre != null ? String(p.codtre) : "",
      nompes: p.nompes || "",
      fanpes: p.fanpes || "",
      cpfpes: p.cpfpes || "",
      cnppes: p.cnppes || "",
      em1pes: p.em1pes || "",
      em2pes: p.em2pes || "",
      celpes: p.celpes || "",
      sitpes: mapSituacaoIn(p.sitpes), // "Ativo"/"Inativo"
      endpes: p.endpes || "",
      numpes: p.numpes || "",
      baipes: p.baipes || "",
      cidpes: p.cidpes || "",
      estpes: p.estpes || "",
      ceppes: p.ceppes || "",
    });
    setShowModal(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const payload = buildPayload(form);
    try {
      if (isEditing && editingId != null) {
        await client.put(`/pessoas/${editingId}`, payload);
      } else {
        await client.post("/pessoas/", payload);
      }
      setShowModal(false);
      resetForm();
      await fetchPessoas();
    } catch (e: any) {
      console.error(e);
      const msg = e?.response?.data?.detail || JSON.stringify(e?.response?.data || e.message);
      alert(`Erro ao salvar: ${msg}`);
    }
  };

  const handleDelete = async (codpes: number) => {
    const ok = confirm("Tem certeza que deseja excluir este cadastro?");
    if (!ok) return;
    try {
      await client.delete(`/pessoas/${codpes}`);
      await fetchPessoas();
    } catch (e: any) {
      console.error(e);
      const msg = e?.response?.data?.detail || JSON.stringify(e?.response?.data || e.message);
      alert(`Erro ao excluir: ${msg}`);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      {/* Header com botão */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold">📑 Cadastros Gerais</h2>
        <button
          onClick={openCreate}
          className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
        >
          + Cadastrar
        </button>
      </div>

      {/* Tabela de listagem */}
      <div className="bg-white border rounded-lg">
        {loading ? (
          <div className="p-6 text-gray-500">Carregando...</div>
        ) : error ? (
          <div className="p-6 text-red-600">{error}</div>
        ) : pessoas.length === 0 ? (
          <div className="p-6 text-gray-500">Nenhum cadastro encontrado.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Código</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nome</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tipo</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">CPF/CNPJ</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">E-mail</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Celular</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cidade/UF</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Situação</th>
                  <th className="px-4 py-2"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {pessoas.map((p) => (
                  <tr key={p.codpes} className="hover:bg-gray-50">
                    <td className="px-4 py-2 text-sm text-gray-700">{p.codpes}</td>
                    <td className="px-4 py-2 text-sm text-gray-700">{p.nompes}</td>
                    <td className="px-4 py-2 text-sm text-gray-700">{labelTipo(p.tippes)}</td>
                    <td className="px-4 py-2 text-sm text-gray-700">{labelDoc(p)}</td>
                    <td className="px-4 py-2 text-sm text-gray-700">{p.em1pes || "-"}</td>
                    <td className="px-4 py-2 text-sm text-gray-700">{p.celpes || "-"}</td>
                    <td className="px-4 py-2 text-sm text-gray-700">
                      {p.cidpes || "-"}{p.estpes ? `/${p.estpes}` : ""}
                    </td>
                    <td className="px-4 py-2 text-sm">
                      <span
                        className={`px-2 py-0.5 rounded text-white ${
                          p.sitpes === "A" ? "bg-green-600" : p.sitpes === "I" ? "bg-gray-500" : "bg-gray-300"
                        }`}
                      >
                        {labelSituacao(p.sitpes)}
                      </span>
                    </td>
                    <td className="px-4 py-2 text-sm text-right">
                      <button
                        onClick={() => openEdit(p)}
                        className="px-3 py-1 rounded bg-amber-500 text-white hover:bg-amber-600 mr-2"
                      >
                        Editar
                      </button>
                      <button
                        onClick={() => handleDelete(p.codpes)}
                        className="px-3 py-1 rounded bg-red-600 text-white hover:bg-red-700"
                      >
                        Excluir
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal de cadastro/edição */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
          <div className="bg-white w-full max-w-5xl rounded-lg shadow-lg">
            {/* Cabeçalho modal */}
            <div className="p-6 border-b flex items-center justify-between">
              <h3 className="text-xl font-semibold">
                {isEditing ? `Editar Cadastro #${editingId}` : "Novo Cadastro"}
              </h3>
              <button
                onClick={() => {
                  setShowModal(false);
                  resetForm();
                }}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="p-6 space-y-6">
              {/* 1ª fileira - Dados principais */}
              <section className="border rounded-lg p-4">
                <h4 className="font-medium mb-3">Dados Principais</h4>
                <div className="grid grid-cols-4 gap-4">
                  <div>
                    <label className="block text-sm">Tipo Pessoa</label>
                    <select
                      name="tippes"
                      value={form.tippes}
                      onChange={(e) => {
                        const val = e.target.value as "F" | "J";
                        setForm((prev) => ({ ...prev, tippes: val, cpfpes: "", cnppes: "" }));
                      }}
                      className="w-full border px-3 py-2 rounded"
                    >
                      <option value="F">Física</option>
                      <option value="J">Jurídica</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm">Código Regime</label>
                    <input
                      type="number"
                      name="codtre"
                      value={form.codtre}
                      onChange={handleChange}
                      className="w-full border px-3 py-2 rounded"
                    />
                  </div>
                  <div className="col-span-2">
                    <label className="block text-sm">Nome *</label>
                    <input
                      type="text"
                      name="nompes"
                      value={form.nompes}
                      onChange={handleChange}
                      className="w-full border px-3 py-2 rounded"
                      required
                    />
                  </div>
                  {form.tippes === "F" ? (
                    <div>
                      <label className="block text-sm">CPF</label>
                      <input
                        type="text"
                        name="cpfpes"
                        value={form.cpfpes}
                        onChange={handleChange}
                        className="w-full border px-3 py-2 rounded"
                      />
                    </div>
                  ) : (
                    <div>
                      <label className="block text-sm">CNPJ</label>
                      <input
                        type="text"
                        name="cnppes"
                        value={form.cnppes}
                        onChange={handleChange}
                        className="w-full border px-3 py-2 rounded"
                      />
                    </div>
                  )}
                  <div className="col-span-3">
                    <label className="block text-sm">Nome Fantasia</label>
                    <input
                      type="text"
                      name="fanpes"
                      value={form.fanpes}
                      onChange={handleChange}
                      className="w-full border px-3 py-2 rounded"
                    />
                  </div>
                </div>
              </section>

              {/* 2ª fileira - Contato */}
              <section className="border rounded-lg p-4">
                <h4 className="font-medium mb-3">Contatos</h4>
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm">E-mail</label>
                    <input
                      type="email"
                      name="em1pes"
                      value={form.em1pes}
                      onChange={handleChange}
                      className="w-full border px-3 py-2 rounded"
                    />
                  </div>
                  <div>
                    <label className="block text-sm">E-mail 2</label>
                    <input
                      type="email"
                      name="em2pes"
                      value={form.em2pes}
                      onChange={handleChange}
                      className="w-full border px-3 py-2 rounded"
                    />
                  </div>
                  <div>
                    <label className="block text-sm">Celular</label>
                    <input
                      type="text"
                      name="celpes"
                      value={form.celpes}
                      onChange={handleChange}
                      className="w-full border px-3 py-2 rounded"
                    />
                  </div>
                  <div>
                    <label className="block text-sm">Situação</label>
                    <select
                      name="sitpes"
                      value={form.sitpes}
                      onChange={handleChange}
                      className="w-full border px-3 py-2 rounded"
                    >
                      <option value="">-</option>
                      <option value="Ativo">Ativo</option>
                      <option value="Inativo">Inativo</option>
                    </select>
                  </div>
                </div>
              </section>

              {/* 3ª fileira - Endereço */}
              <section className="border rounded-lg p-4">
                <h4 className="font-medium mb-3">Endereço</h4>
                <div className="grid grid-cols-3 gap-4">
                  <div className="col-span-2">
                    <label className="block text-sm">Endereço</label>
                    <input
                      type="text"
                      name="endpes"
                      value={form.endpes}
                      onChange={handleChange}
                      className="w-full border px-3 py-2 rounded"
                    />
                  </div>
                  <div>
                    <label className="block text-sm">Número</label>
                    <input
                      type="text"
                      name="numpes"
                      value={form.numpes}
                      onChange={handleChange}
                      className="w-full border px-3 py-2 rounded"
                    />
                  </div>
                  <div>
                    <label className="block text-sm">Bairro</label>
                    <input
                      type="text"
                      name="baipes"
                      value={form.baipes}
                      onChange={handleChange}
                      className="w-full border px-3 py-2 rounded"
                    />
                  </div>
                  <div>
                    <label className="block text-sm">Cidade</label>
                    <input
                      type="text"
                      name="cidpes"
                      value={form.cidpes}
                      onChange={handleChange}
                      className="w-full border px-3 py-2 rounded"
                    />
                  </div>
                  <div>
                    <label className="block text-sm">Estado</label>
                    <input
                      type="text"
                      name="estpes"
                      value={form.estpes}
                      onChange={handleChange}
                      className="w-full border px-3 py-2 rounded"
                    />
                  </div>
                  <div>
                    <label className="block text-sm">CEP</label>
                    <input
                      type="text"
                      name="ceppes"
                      value={form.ceppes}
                      onChange={handleChange}
                      className="w-full border px-3 py-2 rounded"
                    />
                  </div>
                </div>
              </section>

              {/* Footer */}
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false);
                    resetForm();
                  }}
                  className="px-4 py-2 border rounded hover:bg-gray-100"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
                >
                  {isEditing ? "Salvar alterações" : "Salvar"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default CadastrosPage;