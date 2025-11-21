import React from "react";
import axiosLib from "axios";

type User = {
  codusu: number;
  nomusu: string;
  logusu: string;
  emausu: string;
  situsu: "ATIVO" | "INATIVO";
  codemp: number;
  codfil: number;
  issuper: boolean;
  isadmin: boolean;
};

type CreateForm = {
  nomusu: string;
  logusu: string;
  emausu: string;
  senha: string;
  situsu: "ATIVO" | "INATIVO";
  codemp: number | "";
  codfil: number | "";
  isadmin: boolean;
};

// Helpers de mapeamento (robustos a retorno 'A'/'I' do backend)
const toUiSit = (s: string): "ATIVO" | "INATIVO" => {
  const v = s?.toUpperCase?.() ?? "";
  if (v === "A") return "ATIVO";
  if (v === "I") return "INATIVO";
  return v === "ATIVO" ? "ATIVO" : "INATIVO";
};

// Se seu backend já espera "ATIVO"/"INATIVO", mantemos como está.
// Se ele ainda esperar 'A'/'I', troque para:
// const toApiSit = (s: "ATIVO" | "INATIVO") => (s === "ATIVO" ? "A" : "I");
const toApiSit = (s: "ATIVO" | "INATIVO") => s;

// Tenta usar um axios configurado; se não tiver, usa esse com baseURL simples:
const api = axiosLib.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
});
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

const SuperAdminUsersPage: React.FC = () => {
  const [codemp, setCodemp] = React.useState<number | "">("");
  const [codfil, setCodfil] = React.useState<number | "">("");
  const [users, setUsers] = React.useState<User[]>([]);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [success, setSuccess] = React.useState<string | null>(null);

  const [form, setForm] = React.useState<CreateForm>({
    nomusu: "",
    logusu: "",
    emausu: "",
    senha: "",
    situsu: "ATIVO",
    codemp: "",
    codfil: "",
    isadmin: false,
  });

  const loadUsers = React.useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params: any = {};
      if (codemp !== "") params.codemp = codemp;
      if (codfil !== "") params.codfil = codfil;

      const { data } = await api.get<any[]>("/superadmin/users", { params });
      // Mapeia situsu para ATIVO/INATIVO na UI
      const mapped: User[] = data.map((u: any) => ({
        ...u,
        situsu: toUiSit(u.situsu),
      }));
      setUsers(mapped);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Erro ao carregar usuários");
    } finally {
      setLoading(false);
    }
  }, [codemp, codfil]);

  React.useEffect(() => {
    loadUsers();
  }, [loadUsers]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (form.codemp === "" || form.codfil === "") {
      setError("Informe empresa e filial para criar o usuário.");
      return;
    }

    try {
      const payload = {
        nomusu: form.nomusu.trim(),
        logusu: form.logusu.trim(),
        emausu: form.emausu.trim(),
        senha: form.senha,
        situsu: toApiSit(form.situsu), // envia "ATIVO" / "INATIVO" (ou troque para 'A'/'I' se necessário)
        codemp: Number(form.codemp),
        codfil: Number(form.codfil),
        isadmin: form.isadmin,
      };

      await api.post("/superadmin/users", payload);
      setSuccess("Usuário criado com sucesso!");
      setForm({
        nomusu: "",
        logusu: "",
        emausu: "",
        senha: "",
        situsu: "ATIVO",
        codemp: "",
        codfil: "",
        isadmin: false,
      });
      await loadUsers();
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Erro ao criar usuário");
    }
  };

  const toggleAdmin = async (u: User) => {
    setError(null);
    setSuccess(null);
    try {
      const body = { isadmin: !u.isadmin };
      await api.patch(`/superadmin/users/${u.codusu}/set-admin`, body);
      setSuccess(`Usuário ${u.nomusu} agora ${!u.isadmin ? "é" : "não é"} admin.`);
      await loadUsers();
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Erro ao atualizar admin");
    }
  };

  const sitLabel = (s: "ATIVO" | "INATIVO") => (s === "ATIVO" ? "Ativo" : "Inativo");

  return (
    <div className="p-4 space-y-6">
      <h1 className="text-xl font-semibold">SuperAdmin - Gestão de Usuários</h1>

      {/* Filtros por Empresa/Filial */}
      <div className="bg-white shadow rounded p-4">
        <h2 className="font-medium mb-3">Filtros</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Empresa (codemp)</label>
            <input
              type="number"
              className="w-full border rounded px-3 py-2"
              value={codemp}
              onChange={(e) => setCodemp(e.target.value === "" ? "" : Number(e.target.value))}
              placeholder="Ex: 1"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Filial (codfil)</label>
            <input
              type="number"
              className="w-full border rounded px-3 py-2"
              value={codfil}
              onChange={(e) => setCodfil(e.target.value === "" ? "" : Number(e.target.value))}
              placeholder="Ex: 1"
            />
          </div>
          <div className="flex items-end">
            <button
              onClick={loadUsers}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
            >
              Aplicar Filtros
            </button>
          </div>
        </div>
      </div>

      {/* Formulário de criação */}
      <div className="bg-white shadow rounded p-4">
        <h2 className="font-medium mb-3">Criar Usuário</h2>
        <form onSubmit={handleCreate} className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Nome</label>
            <input
              className="w-full border rounded px-3 py-2"
              value={form.nomusu}
              onChange={(e) => setForm((s) => ({ ...s, nomusu: e.target.value }))}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Login</label>
            <input
              className="w-full border rounded px-3 py-2"
              value={form.logusu}
              onChange={(e) => setForm((s) => ({ ...s, logusu: e.target.value }))}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              type="email"
              className="w-full border rounded px-3 py-2"
              value={form.emausu}
              onChange={(e) => setForm((s) => ({ ...s, emausu: e.target.value }))}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Senha</label>
            <input
              type="password"
              className="w-full border rounded px-3 py-2"
              value={form.senha}
              onChange={(e) => setForm((s) => ({ ...s, senha: e.target.value }))}
              required
              minLength={3}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Situação</label>
            <select
              className="w-full border rounded px-3 py-2"
              value={form.situsu}
              onChange={(e) =>
                setForm((s) => ({ ...s, situsu: e.target.value as "ATIVO" | "INATIVO" }))
              }
            >
              <option value="ATIVO">Ativo</option>
              <option value="INATIVO">Inativo</option>
            </select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Empresa</label>
              <input
                type="number"
                className="w-full border rounded px-3 py-2"
                value={form.codemp}
                onChange={(e) =>
                  setForm((s) => ({
                    ...s,
                    codemp: e.target.value === "" ? "" : Number(e.target.value),
                  }))
                }
                placeholder="Ex: 1"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Filial</label>
              <input
                type="number"
                className="w-full border rounded px-3 py-2"
                value={form.codfil}
                onChange={(e) =>
                  setForm((s) => ({
                    ...s,
                    codfil: e.target.value === "" ? "" : Number(e.target.value),
                  }))
                }
                placeholder="Ex: 1"
                required
              />
            </div>
          </div>

          <div className="flex items-center space-x-2 md:col-span-3">
            <input
              id="isadmin"
              type="checkbox"
              className="h-4 w-4"
              checked={form.isadmin}
              onChange={(e) => setForm((s) => ({ ...s, isadmin: e.target.checked }))}
            />
            <label htmlFor="isadmin" className="text-sm text-gray-700">
              Criar como admin da empresa/filial selecionada
            </label>
          </div>

          <div className="md:col-span-3">
            <button
              type="submit"
              className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded"
            >
              Criar Usuário
            </button>
          </div>
        </form>
      </div>

      {/* Lista de usuários */}
      <div className="bg-white shadow rounded p-4">
        <h2 className="font-medium mb-3">Usuários</h2>

        {loading && <div className="text-gray-600">Carregando...</div>}
        {error && <div className="text-red-600 mb-2">{error}</div>}
        {success && <div className="text-green-700 mb-2">{success}</div>}

        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="text-left border-b">
                <th className="py-2 pr-3">ID</th>
                <th className="py-2 pr-3">Nome</th>
                <th className="py-2 pr-3">Login</th>
                <th className="py-2 pr-3">Email</th>
                <th className="py-2 pr-3">Empresa</th>
                <th className="py-2 pr-3">Filial</th>
                <th className="py-2 pr-3">Situação</th>
                <th className="py-2 pr-3">Super</th>
                <th className="py-2 pr-3">Admin</th>
                <th className="py-2 pr-3">Ações</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.codusu} className="border-b">
                  <td className="py-2 pr-3">{u.codusu}</td>
                  <td className="py-2 pr-3">{u.nomusu}</td>
                  <td className="py-2 pr-3">{u.logusu}</td>
                  <td className="py-2 pr-3">{u.emausu}</td>
                  <td className="py-2 pr-3">{u.codemp}</td>
                  <td className="py-2 pr-3">{u.codfil}</td>
                  <td className="py-2 pr-3">{sitLabel(u.situsu)}</td>
                  <td className="py-2 pr-3">
                    <span className={`px-2 py-1 rounded ${u.issuper ? "bg-purple-100 text-purple-700" : "bg-gray-100 text-gray-600"}`}>
                      {u.issuper ? "Sim" : "Não"}
                    </span>
                  </td>
                  <td className="py-2 pr-3">
                    <span className={`px-2 py-1 rounded ${u.isadmin ? "bg-blue-100 text-blue-700" : "bg-gray-100 text-gray-600"}`}>
                      {u.isadmin ? "Sim" : "Não"}
                    </span>
                  </td>
                  <td className="py-2 pr-3">
                    {!u.issuper && (
                      <button
                        onClick={() => toggleAdmin(u)}
                        className={`px-3 py-1 rounded ${u.isadmin ? "bg-orange-600 hover:bg-orange-700" : "bg-blue-600 hover:bg-blue-700"} text-white`}
                        title={u.isadmin ? "Remover admin" : "Promover a admin"}
                      >
                        {u.isadmin ? "Remover Admin" : "Promover a Admin"}
                      </button>
                    )}
                  </td>
                </tr>
              ))}
              {users.length === 0 && !loading && (
                <tr>
                  <td colSpan={10} className="py-4 text-gray-600">
                    Nenhum usuário encontrado para os filtros informados.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default SuperAdminUsersPage;