import type { ReactNode } from "react";
import { NavLink } from "react-router-dom";
import logoIngohBranca from "../assets/ingoh-marca-branca.webp";
import { useAuth } from "../contexts/AuthContext";

export function AdminLayout({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth();

  return (
    <div>
      <header className="admin-header">
        <img
          src={logoIngohBranca}
          alt="INGOH — Instituto Goiano de Oncologia e Hematologia"
          className="logo-header"
        />
        <nav className="admin-nav">
          <NavLink to="/admin/dashboard">Dashboard</NavLink>
          <NavLink to="/admin/solicitacoes">Solicitações</NavLink>
          {user?.perfil === "administrador" && <NavLink to="/admin/usuarios">Usuários</NavLink>}
        </nav>
        <div className="admin-user">
          <span>{user?.nome}</span>
          <button onClick={() => logout()}>Sair</button>
        </div>
      </header>
      <main className="admin-main">{children}</main>
    </div>
  );
}
