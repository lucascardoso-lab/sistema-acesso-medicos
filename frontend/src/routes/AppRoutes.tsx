import { Navigate, Route, Routes } from "react-router-dom";
import { PublicLayout } from "../layouts/PublicLayout";
import { AdminLayout } from "../layouts/AdminLayout";
import { ProtectedRoute } from "../components/ProtectedRoute";
import { SolicitacaoForm } from "../pages/publico/SolicitacaoForm";
import { SolicitacaoSucesso } from "../pages/publico/SolicitacaoSucesso";
import { Login } from "../pages/admin/Login";
import { Dashboard } from "../pages/admin/Dashboard";
import { SolicitacoesLista } from "../pages/admin/SolicitacoesLista";
import { SolicitacaoDetalhe } from "../pages/admin/SolicitacaoDetalhe";
import { Usuarios } from "../pages/admin/Usuarios";

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/solicitacao" replace />} />

      <Route
        path="/solicitacao"
        element={
          <PublicLayout>
            <SolicitacaoForm />
          </PublicLayout>
        }
      />
      <Route
        path="/solicitacao/sucesso"
        element={
          <PublicLayout>
            <SolicitacaoSucesso />
          </PublicLayout>
        }
      />

      <Route
        path="/login"
        element={
          <PublicLayout>
            <Login />
          </PublicLayout>
        }
      />

      <Route
        path="/admin/dashboard"
        element={
          <ProtectedRoute>
            <AdminLayout>
              <Dashboard />
            </AdminLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/solicitacoes"
        element={
          <ProtectedRoute>
            <AdminLayout>
              <SolicitacoesLista />
            </AdminLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/solicitacoes/:id"
        element={
          <ProtectedRoute>
            <AdminLayout>
              <SolicitacaoDetalhe />
            </AdminLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/usuarios"
        element={
          <ProtectedRoute>
            <AdminLayout>
              <Usuarios />
            </AdminLayout>
          </ProtectedRoute>
        }
      />

      <Route path="*" element={<Navigate to="/solicitacao" replace />} />
    </Routes>
  );
}
