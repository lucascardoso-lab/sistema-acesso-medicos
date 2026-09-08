import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { getDashboard } from "../../services/dashboardApi";
import type { DashboardResponse } from "../../types/dashboard";

const CORES_STATUS: Record<string, string> = {
  pendente: "#f59e0b",
  em_analise: "#3b82f6",
  aprovada: "#22c55e",
  rejeitada: "#ef4444",
  respondida: "#8b5cf6",
};

const ROTULOS_CARD: { chave: keyof DashboardResponse["cards"]; titulo: string }[] = [
  { chave: "total", titulo: "Total de solicitações" },
  { chave: "recebidas_hoje", titulo: "Recebidas hoje" },
  { chave: "pendentes", titulo: "Pendentes" },
  { chave: "em_analise", titulo: "Em análise" },
  { chave: "aprovadas", titulo: "Aprovadas" },
  { chave: "rejeitadas", titulo: "Rejeitadas" },
  { chave: "respondidas", titulo: "Respondidas" },
];

export function Dashboard() {
  const [dados, setDados] = useState<DashboardResponse | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    getDashboard()
      .then(setDados)
      .catch(() => setErro("Não foi possível carregar o dashboard."));
  }, []);

  if (erro) return <p className="form-error">{erro}</p>;
  if (!dados) return <p>Carregando...</p>;

  const distribuicao = Object.entries(dados.distribuicao_status).map(([status, total]) => ({
    status,
    total,
  }));

  return (
    <div>
      <h1>Dashboard</h1>

      <div className="card-row">
        {ROTULOS_CARD.map(({ chave, titulo }) => (
          <div className="card" key={chave}>
            <h3>{titulo}</h3>
            <div className="valor">{dados.cards[chave]}</div>
          </div>
        ))}
      </div>

      <div className="card-row">
        <div className="card" style={{ minWidth: 400, flex: 2 }}>
          <h3>Solicitações recebidas nos últimos 30 dias</h3>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={dados.serie_30_dias}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="data" tick={{ fontSize: 10 }} interval={4} />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="total" fill="#2563eb" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card" style={{ minWidth: 300, flex: 1 }}>
          <h3>Distribuição por status</h3>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={distribuicao} dataKey="total" nameKey="status" outerRadius={90} label>
                {distribuicao.map((entrada) => (
                  <Cell key={entrada.status} fill={CORES_STATUS[entrada.status] ?? "#94a3b8"} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
