export type StatusSolicitacao =
  | "pendente"
  | "em_analise"
  | "aprovada"
  | "rejeitada"
  | "respondida";

export interface SolicitacaoListItem {
  id: number;
  protocolo: string;
  nome_completo: string;
  conselho: string;
  numero_conselho: string;
  uf_conselho: string;
  especialidade: string;
  email: string;
  telefone: string;
  status: StatusSolicitacao;
  responsavel_nome: string | null;
  created_at: string;
}

export interface SolicitacaoListResponse {
  items: SolicitacaoListItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface SolicitacaoDetail extends Omit<SolicitacaoListItem, never> {
  observacao_interna: string | null;
  motivo_rejeicao: string | null;
  updated_at: string;
  analise_iniciada_at: string | null;
  analisado_at: string | null;
  respondido_at: string | null;
}

export interface HistoricoItem {
  id: number;
  acao: string;
  status_anterior: string | null;
  status_novo: string | null;
  descricao: string | null;
  usuario_nome: string | null;
  created_at: string;
}

export interface SolicitacaoFiltros {
  status?: StatusSolicitacao | "";
  nome?: string;
  numero_conselho?: string;
  conselho?: string;
  especialidade?: string;
  data_inicial?: string;
  data_final?: string;
  busca?: string;
  page: number;
  page_size: number;
}

export const STATUS_LABELS: Record<StatusSolicitacao, string> = {
  pendente: "Pendente",
  em_analise: "Em análise",
  aprovada: "Aprovada",
  rejeitada: "Rejeitada",
  respondida: "Respondida",
};
