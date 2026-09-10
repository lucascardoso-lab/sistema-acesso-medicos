import { api } from "./api";
import type {
  HistoricoItem,
  SolicitacaoDetail,
  SolicitacaoFiltros,
  SolicitacaoListResponse,
} from "../types/solicitacaoAdmin";

export async function listarSolicitacoes(
  filtros: SolicitacaoFiltros
): Promise<SolicitacaoListResponse> {
  const params = Object.fromEntries(
    Object.entries(filtros).filter(([, v]) => v !== undefined && v !== "")
  );
  const { data } = await api.get<SolicitacaoListResponse>("/solicitacoes", { params });
  return data;
}

export async function obterSolicitacao(id: number): Promise<SolicitacaoDetail> {
  const { data } = await api.get<SolicitacaoDetail>(`/solicitacoes/${id}`);
  return data;
}

export async function obterHistorico(id: number): Promise<HistoricoItem[]> {
  const { data } = await api.get<HistoricoItem[]>(`/solicitacoes/${id}/historico`);
  return data;
}

export async function iniciarAnalise(id: number): Promise<SolicitacaoDetail> {
  const { data } = await api.post<SolicitacaoDetail>(`/solicitacoes/${id}/iniciar-analise`);
  return data;
}

export async function aprovar(id: number): Promise<SolicitacaoDetail> {
  const { data } = await api.post<SolicitacaoDetail>(`/solicitacoes/${id}/aprovar`);
  return data;
}

export async function rejeitar(id: number, motivo: string): Promise<SolicitacaoDetail> {
  const { data } = await api.post<SolicitacaoDetail>(`/solicitacoes/${id}/rejeitar`, { motivo });
  return data;
}

export async function adicionarObservacao(
  id: number,
  observacao_interna: string
): Promise<SolicitacaoDetail> {
  const { data } = await api.patch<SolicitacaoDetail>(`/solicitacoes/${id}/observacao`, {
    observacao_interna,
  });
  return data;
}

export async function enviarEmail(
  id: number,
  mensagem: string,
  anexo?: File
): Promise<SolicitacaoDetail> {
  const formData = new FormData();
  formData.append("mensagem", mensagem);
  if (anexo) formData.append("anexo", anexo);

  const { data } = await api.post<SolicitacaoDetail>(`/solicitacoes/${id}/enviar-email`, formData);
  return data;
}

export async function marcarRespondida(id: number): Promise<SolicitacaoDetail> {
  const { data } = await api.post<SolicitacaoDetail>(`/solicitacoes/${id}/marcar-respondida`);
  return data;
}

export function urlDocumento(id: number, tipo: "documento" | "foto"): string {
  const base = api.defaults.baseURL ?? "";
  return `${base}/solicitacoes/${id}/documentos/${tipo}`;
}
