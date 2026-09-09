import type { ReactNode } from "react";
import logoIngoh from "../assets/ingoh-marca.webp";

export function PublicLayout({ children }: { children: ReactNode }) {
  return (
    <div>
      <header className="public-header">
        <img src={logoIngoh} alt="INGOH — Instituto Goiano de Oncologia e Hematologia" className="logo-header" />
      </header>
      <main>{children}</main>
    </div>
  );
}
