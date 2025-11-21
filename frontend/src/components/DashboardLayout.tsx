import React from "react";
import { Routes, Route, Link, useLocation, Navigate } from "react-router-dom";
import CadastrosPage from "../pages/CadastrosPage";
import SuperAdminUsersPage from "../pages/SuperAdminUsersPage";
import UsuariosPage from "../pages/UsuariosPage";
import ContasPagarPage from "../pages/ContasPagarPage";
import ContasReceberPage from "../pages/ContasReceberPage";
import LicencasPage from "../pages/LicencasPage";
import api from "../api";

interface DashboardLayoutProps {
  token: string;
  onLogout: () => void;
}

type Me = {
  nomusu: string;
  issuper: boolean;
  isadmin: boolean;
  codemp: number;
  codfil: number;
};

const DashboardLayout: React.FC<DashboardLayoutProps> = ({ onLogout }) => {
  const location = useLocation();
  const [me, setMe] = React.useState<Me | null>(null);

  // Busca perfil do usuário logado usando o cliente axios com interceptor
  React.useEffect(() => {
    api
      .get("/auth/me")
      .then((response) => setMe(response.data))
      .catch((e) => console.error("Erro ao carregar perfil:", e));
  }, []);

  const isActive = (path: string) => {
    return location.pathname === path
      ? "bg-indigo-100 text-indigo-600"
      : "hover:bg-indigo-50 hover:text-indigo-600";
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <aside className="w-64 bg-white shadow-md flex flex-col">
        <div className="h-16 flex items-center justify-center text-xl font-bold text-indigo-600 border-b">
          App Fiscal
        </div>
        <nav className="flex-1 p-4 space-y-2">
          <Link to="/" className={`block px-4 py-2 rounded-lg ${isActive("/")}`}>
            Dashboard
          </Link>
          <Link to="/cadastros" className={`block px-4 py-2 rounded-lg ${isActive("/cadastros")}`}>
            Cadastros Gerais
          </Link>
          
          {/* Financeiro */}
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase">
              Financeiro
            </div>
          </div>
          <Link to="/contas-pagar" className={`block px-4 py-2 rounded-lg ${isActive("/contas-pagar")}`}>
            💰 Contas a Pagar
          </Link>
          <Link to="/contas-receber" className={`block px-4 py-2 rounded-lg ${isActive("/contas-receber")}`}>
            💵 Contas a Receber
          </Link>
          
          {/* Outros */}
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase">
              Sistema
            </div>
          </div>
          <Link to="/empresas" className={`block px-4 py-2 rounded-lg ${isActive("/empresas")}`}>
            Empresas
          </Link>
          <Link to="/notas" className={`block px-4 py-2 rounded-lg ${isActive("/notas")}`}>
            Notas Fiscais
          </Link>
          <Link to="/usuarios" className={`block px-4 py-2 rounded-lg ${isActive("/usuarios")}`}>
            Usuários
          </Link>

          {/* Menu SuperAdmin (visível apenas para issuper) */}
          {me?.issuper && (
            <>
              <div className="mt-6 pt-4 border-t border-gray-200">
                <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase">
                  SuperAdmin
                </div>
              </div>
              <Link
                to="/superadmin/users"
                className={`block px-4 py-2 rounded-lg ${isActive("/superadmin/users")}`}
              >
                👥 Gestão de Usuários
              </Link>
              <Link
                to="/superadmin/licencas"
                className={`block px-4 py-2 rounded-lg ${isActive("/superadmin/licencas")}`}
              >
                🔑 Gestão de Licenças
              </Link>
            </>
          )}
        </nav>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="h-16 bg-white shadow flex items-center justify-between px-6">
          <div>
            <h1 className="text-xl font-semibold text-gray-800">App Fiscal</h1>
            {me && (
              <p className="text-xs text-gray-500">
                {me.nomusu} {me.issuper && "(SuperAdmin)"} {me.isadmin && !me.issuper && "(Admin)"}
              </p>
            )}
          </div>
          <button
            onClick={onLogout}
            className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
          >
            Logout
          </button>
        </header>

        {/* Dynamic content */}
        <main className="flex-1 p-6 overflow-y-auto">
          <Routes>
            <Route path="/" element={<DashboardHome me={me} />} />
            <Route path="/cadastros" element={<CadastrosPage />} />
            <Route path="/contas-pagar" element={<ContasPagarPage />} />
            <Route path="/contas-receber" element={<ContasReceberPage />} />
            <Route path="/empresas" element={<EmpresasPage />} />
            <Route path="/notas" element={<NotasPage />} />
            <Route path="/usuarios" element={<UsuariosPage />} />

            {/* Rotas SuperAdmin com guard */}
            <Route
              path="/superadmin/users"
              element={
                <RequireSuperAdmin me={me}>
                  <SuperAdminUsersPage />
                </RequireSuperAdmin>
              }
            />
            <Route
              path="/superadmin/licencas"
              element={
                <RequireSuperAdmin me={me}>
                  <LicencasPage />
                </RequireSuperAdmin>
              }
            />
          </Routes>
        </main>
      </div>
    </div>
  );
};

// Guard para proteger rotas de SuperAdmin
const RequireSuperAdmin: React.FC<{ me: Me | null; children: React.ReactNode }> = ({
  me,
  children,
}) => {
  // Ainda carregando o perfil
  if (me === null) {
    return (
      <div className="flex items-center justify-center h-40">
        <div className="text-gray-500">Carregando...</div>
      </div>
    );
  }
  // Não é superadmin: redireciona para o dashboard
  if (!me.issuper) {
    return <Navigate to="/" replace />;
  }
  // Autorizado
  return <>{children}</>;
};

// Componentes das páginas (placeholders por enquanto)
const DashboardHome = ({ me }: { me: Me | null }) => (
  <div className="bg-white rounded-lg shadow p-6">
    <h2 className="text-2xl font-bold mb-4">Bem-vindo ao App Fiscal! 👋</h2>
    {me && (
      <div className="mb-4 text-gray-700">
        <p>
          <strong>Usuário:</strong> {me.nomusu}
        </p>
        <p>
          <strong>Empresa/Filial:</strong> {me.codemp}/{me.codfil}
        </p>
        <p>
          <strong>Perfil:</strong>{" "}
          {me.issuper ? "SuperAdmin" : me.isadmin ? "Admin do Tenant" : "Usuário Comum"}
        </p>
      </div>
    )}
    <p className="text-gray-600">Selecione um módulo no menu lateral para começar.</p>
  </div>
);

const EmpresasPage = () => (
  <div className="bg-white rounded-lg shadow p-6">
    <h2 className="text-2xl font-bold mb-4">Empresas</h2>
    <p className="text-gray-600">Módulo de empresas (em breve).</p>
  </div>
);

const NotasPage = () => (
  <div className="bg-white rounded-lg shadow p-6">
    <h2 className="text-2xl font-bold mb-4">Notas Fiscais</h2>
    <p className="text-gray-600">Módulo de notas fiscais (em breve).</p>
  </div>
);

export default DashboardLayout;