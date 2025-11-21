import { useState, useEffect } from "react";
import Login from "./pages/Login";
import DashboardLayout from "./components/DashboardLayout";

function App() {
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const saved = localStorage.getItem("token");
    if (saved) setToken(saved);
  }, []);

  if (!token) return <Login onLogin={(t) => { setToken(t); localStorage.setItem("token", t); }} />;

  return <DashboardLayout token={token} onLogout={() => { setToken(null); localStorage.removeItem("token"); }} />;
}

export default App;