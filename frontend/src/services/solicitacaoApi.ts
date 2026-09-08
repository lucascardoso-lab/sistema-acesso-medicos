import { api } from "./api";
import type { SolicitacaoCreatedResponse } from "../types/solicitacao";

export interface CriarSolicitacaoInput {
  nome_completo: string;
  conselho: string;
  numero_conselho: string;
  uf_conselho: string;
  especialidade: string;
  email: string;
  telefone: string;
  consentimento_lgpd: boolean;
  documento: File;
  foto_documento: File;
}

export async function criarSolicitacao(
  input: CriarSolicitacaoInput
): Promise<SolicitacaoCreatedResponse> {
  const formData = new FormData();
  formData.append("nome_completo", input.nome_completo);
  formData.append("conselho", input.conselho);
  formData.append("numero_conselho", input.numero_conselho);
  formData.append("uf_conselho", input.uf_conselho);
  formData.append("especialidade", input.especialidade);
  formData.append("email", input.email);
  formData.append("telefone", input.telefone);
  formData.append("consentimento_lgpd", String(input.consentimento_lgpd));
  formData.append("documento", input.documento);
  formData.append("foto_documento", input.foto_documento);

  const { data } = await api.post<SolicitacaoCreatedResponse>("/solicitacoes", formData);
  return data;
}
