import { api } from "./api";

export interface SmtpConfig {
  host: string;
  port: number;
  usuario: string;
  remetente: string;
  senha_configurada: boolean;
  updated_at: string;
}

export interface SmtpConfigInput {
  host: string;
  port: number;
  usuario: string;
  remetente: string;
  senha?: string;
}

export async function obterConfiguracaoSmtp(): Promise<SmtpConfig | null> {
  const { data } = await api.get<SmtpConfig | null>("/configuracoes/smtp");
  return data;
}

export async function salvarConfiguracaoSmtp(input: SmtpConfigInput): Promise<SmtpConfig> {
  const { data } = await api.put<SmtpConfig>("/configuracoes/smtp", input);
  return data;
}

export async function testarConfiguracaoSmtp(destinatario: string): Promise<void> {
  await api.post("/configuracoes/smtp/testar", { destinatario });
}
