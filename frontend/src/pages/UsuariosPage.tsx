// src/pages/UsuariosPage.tsx
import React from "react";
import api from "../api";

type User = {
  codusu: number;
  nomusu: string;
  logusu: string;
  emausu: string | null;
  situsu: string; // pode vir "A"/"I" ou "ATIVO"/"INATIVO"
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
  isadmin: boolean;
};

const normalizeSit = (s: string | null | undefined): "ATIVO" | "INATIVO" => {
  const v = (s || "").toUpperCase().trim();
  if (v === "A" || v === "ATIVO") return "ATIVO";
  if (v === "I" || v === "INATIVO") return "INATIVO";
  return "INATIVO";
};

const sitLabel = (s: string) => (normalizeSit(s) === "ATIVO" ? "Ativo" : "Inativo");

// Converte payloads de erro (FastAPI/Pydantic) para string apresentável
const getErrMsg = (e: any): string => {
  const d = e?.response?.data;
  if (!d) return e?.message || "Erro desconhecido";
  if (typeof d === "string") return d;
  const det = d.detail;
  if (!det) return JSON.stringify(d);
  if (typeof det === "string") return det;
  if (Array.isArray(det)) {
    // pydantic v2 costuma vir como lista de objetos {type, loc, msg, ...}
    return det.map((it: any) => it?.msg || JSON.stringify(it)).join("; ");
  }
  if (typeof det === "object" && det?.msg) return det.msg;
  try {
    return JSON.stringify(det);
  } catch {
    return "Erro de validação";
  }
};

export default function UsuariosPage() {
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
    isadmin: false,
  });

  const USERS_ENDPOINT = "/admin/users";

  const load = React.useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get<User[]>(USERS_ENDPOINT);
      const data = (res.data || []).map((u) => ({
        ...u,
        situsu: normalizeSit(u.situsu), // força UI consistente
      }));
      setUsers(data);
    } catch (e: any) {
      console.error(e);
      setError(getErrMsg(e));
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    load();
  }, [load]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    try {
      await api.post(USERS_ENDPOINT, {
        nomusu: form.nomusu.trim(),
        logusu: form.logusu.trim(),
        emausu: form.emausu.trim(),
        senha: form.senha,
        situsu: form.situsu, // envia "ATIVO" ou "INATIVO"
        isadmin: form.isadmin,
      });
      setSuccess("Usuário criado com sucesso");
      setForm({
        nomusu: "",
        logusu: "",
        emausu: "",
        senha: "",
        situsu: "ATIVO",
        isadmin: false,
      });
      await load();
    } catch (e: any) {
      console.error(e);
      setError(getErrMsg(e));
    }
  };

  const toggleAdmin = async (u: User) => {
    setError(null);
    setSuccess(null);
    try {
      // Envia o payload no corpo da requisição, não como query param
      await api.patch(`${USERS_ENDPOINT}/${u.codusu}/set-admin`, { isadmin: !u.isadmin });
      setSuccess(`Usuário ${u.nomusu} agora ${!u.isadmin ? "é" : "não é"} admin`);
      await load();
    } catch (e: any) {
      console.error("DETAIL:", e?.response?.data);
      setError(getErrMsg(e));
    }
  };

  const toggleSit = async (u: User) => {
    setError(null);
    setSuccess(null);
    try {
      const current = normalizeSit(u.situsu);
      const next = current === "ATIVO" ? "INATIVO" : "ATIVO";
      // Envia "ATIVO" ou "INATIVO" para o backend
      await api.patch(`${USERS_ENDPOINT}/${u.codusu}`, { situsu: next });
      setSuccess("Situação alterada");
      await load();
    } catch (e: any) {
      console.error(e);
      setError(getErrMsg(e));
    }
  };

  const resetPwd = async (u: User) => {
    const nova = prompt(`Nova senha para ${u.nomusu}:`);
    if (!nova) return;
    setError(null);
    setSuccess(null);
    try {
      await api.post(`${USERS_ENDPOINT}/${u.codusu}/reset-password`, {
        nova_senha: nova,
      });
      setSuccess("Senha redefinida");
    } catch (e: any) {
      console.error(e);
      setError(getErrMsg(e));
    }
  };

  const deleteUser = async (u: User) => {
  if (!window.confirm(`Confirma a exclusão do usuário ${u.nomusu}?`)) return;
  setError(null);
  setSuccess(null);
  try {
    await api.delete(`${USERS_ENDPOINT}/${u.codusu}`);
    setSuccess(`Usuário ${u.nomusu} excluído com sucesso`);
    await load();
  } catch (e: any) {
    console.error(e);
    setError(getErrMsg(e));
  }
  };  

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Criar Usuário (Tenant)</h2>
        <form onSubmit={handleCreate} className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <input
            className="border rounded px-3 py-2"
            placeholder="Nome"
            value={form.nomusu}
            onChange={(e) => setForm((s) => ({ ...s, nomusu: e.target.value }))}
            required
          />
          <input
            className="border rounded px-3 py-2"
            placeholder="Login"
            value={form.logusu}
            onChange={(e) => setForm((s) => ({ ...s, logusu: e.target.value }))}
            required
          />
          <input
            type="email"
            className="border rounded px-3 py-2"
            placeholder="Email"
            value={form.emausu}
            onChange={(e) => setForm((s) => ({ ...s, emausu: e.target.value }))}
            required
          />
          <input
            type="password"
            autoComplete="current-password"
            className="border rounded px-3 py-2"
            placeholder="Senha"
            value={form.senha}
            onChange={(e) => setForm((s) => ({ ...s, senha: e.target.value }))}
            required
          />
          <select
            className="border rounded px-3 py-2"
            value={form.situsu}
            onChange={(e) =>
              setForm((s) => ({ ...s, situsu: e.target.value as "ATIVO" | "INATIVO" }))
            }
          >
            <option value="ATIVO">Ativo</option>
            <option value="INATIVO">Inativo</option>
          </select>
          <div className="md:col-span-3">
            <button className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded">
              Criar
            </button>
          </div>
        </form>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Usuários do Tenant</h2>

        {loading && <div>Carregando...</div>}
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
                <th className="py-2 pr-3">Situação</th>
                <th className="py-2 pr-3">Admin</th>
                <th className="py-2 pr-3">Ações</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => {
                const sitNorm = normalizeSit(u.situsu);
                return (
                  <tr key={u.codusu} className="border-b">
                    <td className="py-2 pr-3">{u.codusu}</td>
                    <td className="py-2 pr-3">{u.nomusu}</td>
                    <td className="py-2 pr-3">{u.logusu}</td>
                    <td className="py-2 pr-3">{u.emausu || "-"}</td>
                    <td className="py-2 pr-3">
                    <span
                      className={`px-2 py-0.5 rounded text-white ${
                        sitNorm === "ATIVO"
                          ? "bg-green-600"
                          : sitNorm === "INATIVO"
                          ? "bg-gray-500"
                          : "bg-gray-300"
                      }`}
                    >
                      {sitLabel(sitNorm)}
                    </span>
                    </td>
                    <td className="py-2 pr-3">{u.isadmin ? "Sim" : "Não"}</td>
                    <td className="py-2 pr-3 space-x-2">
                      {!u.issuper && (
                        <>
                          <button
                            onClick={() => toggleAdmin(u)}
                            className={`px-3 py-1 rounded text-white ${
                              u.isadmin
                                ? "bg-orange-600 hover:bg-orange-700"
                                : "bg-blue-600 hover:bg-blue-700"
                            }`}
                          >
                            {u.isadmin ? "Remover Admin" : "Promover Admin"}
                          </button>
                          <button
                            onClick={() => toggleSit(u)}
                            className={`px-3 py-1 rounded text-white ${
                              sitNorm === "ATIVO"
                                ? "bg-gray-600 hover:bg-gray-700"
                                : "bg-green-600 hover:bg-green-700"
                            }`}
                          >
                            {sitNorm === "ATIVO" ? "Inativar" : "Ativar"}
                          </button>
                          <button
                            onClick={() => resetPwd(u)}
                            className="px-3 py-1 rounded text-white bg-indigo-600 hover:bg-indigo-700"
                          >
                            Resetar Senha
                          </button>
                          <button
                            onClick={() => deleteUser(u)}
                            className="px-3 py-1 rounded text-white bg-red-600 hover:bg-red-700"
                          >
                            Excluir
                          </button>
                        </>
                      )}
                    </td>
                  </tr>
                );
              })}
              {users.length === 0 && !loading && (
                <tr>
                  <td colSpan={7} className="py-4 text-gray-600">
                    Nenhum usuário no tenant.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}