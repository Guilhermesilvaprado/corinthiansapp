import { useState } from "react";
import axios from "axios";
import Logo from "../components/Logo";

interface LoginProps {
  onLogin: (token: string) => void;
}

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function Login({ onLogin }: LoginProps) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const params = new URLSearchParams();
      params.append("username", username.trim());
      params.append("password", password);

      const resp = await axios.post(`${API}/auth/login`, params, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });

      const { access_token } = resp.data;
      if (!access_token) throw new Error("Token não retornado pelo servidor.");

      // Salva o token e configura Authorization para as próximas requisições
      localStorage.setItem("token", access_token);
      axios.defaults.headers.common["Authorization"] = `Bearer ${access_token}`;

      // Teste imediato: rota protegida
      const me = await axios.get(`${API}/auth/me`);
      console.log("Auth OK, /auth/me:", me.data);

      onLogin(access_token);
    } catch (err: any) {
      if (axios.isAxiosError(err)) {
        console.error("Axios error", {
          status: err.response?.status,
          data: err.response?.data,
          message: err.message,
          code: err.code,
          url: err.config?.url,
          method: err.config?.method,
        });
        setError(err.response?.data?.detail ?? err.message ?? "Falha no login.");
      } else {
        console.error(err);
        setError("Falha de conexão com o servidor.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-screen flex items-center justify-center bg-gradient-to-br from-indigo-600 to-purple-700 px-4">
      <div className="bg-white w-full max-w-sm p-8 rounded-2xl shadow-xl">
        {/* Logo / Nome */}
        <div className="mb-8">
          <Logo />
        </div>

        {/* Formulário */}
        <form className="space-y-6" onSubmit={handleSubmit}>
          {error && <div className="text-red-600 text-sm">{error}</div>}

          <div>
            <input
              placeholder="Login (logusu)"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full border-b-2 border-gray-300 py-2 focus:border-indigo-500 focus:outline-none text-gray-700"
              autoFocus
              required
            />
          </div>
          <div>
            <input
              type="password"
              placeholder="Senha"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full border-b-2 border-gray-300 py-2 focus:border-indigo-500 focus:outline-none text-gray-700"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:opacity-60 text-white py-2 rounded-full font-semibold transition-colors"
          >
            {loading ? "Entrando..." : "Entrar"}
          </button>
        </form>

        {/* Links extras */}
        <div className="flex justify-between items-center mt-6 text-sm text-gray-600">
          <label className="flex items-center">
            <input type="checkbox" className="mr-2" />
            Lembrar-me
          </label>
          <a href="#" className="text-indigo-600 hover:underline">
            Esqueceu a senha?
          </a>
        </div>
      </div>
    </div>
  );
}

export default Login;