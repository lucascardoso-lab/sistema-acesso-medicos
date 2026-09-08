import type { ReactNode } from "react";
import { useAuth } from "../contexts/AuthContext";

export function AdminLayout({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth();

  return (
    <div>
      <header>
        <span>{user?.nome}</span>
        <button onClick={() => logout()}>Sair</button>
      </header>
      <main>{children}</main>
    </div>
  );
}
