export interface DashboardCards {
  total: number;
  recebidas_hoje: number;
  pendentes: number;
  em_analise: number;
  aprovadas: number;
  rejeitadas: number;
  respondidas: number;
}

export interface PontoSerieDiaria {
  data: string;
  total: number;
}

export interface DashboardResponse {
  cards: DashboardCards;
  serie_30_dias: PontoSerieDiaria[];
  distribuicao_status: Record<string, number>;
}
