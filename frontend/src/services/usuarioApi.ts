import { api } from "./api";
import type { PerfilUsuario, Usuario } from "../types/usuario";

export async function listarUsuarios(): Promise<Usuario[]> {
  const { data } = await api.get<Usuario[]>("/usuarios");
  return data;
}

export async function criarUsuario(input: {
  nome: string;
  email: string;
  senha: string;
  perfil: PerfilUsuario;
}): Promise<Usuario> {
  const { data } = await api.post<Usuario>("/usuarios", input);
  return data;
}

export async function atualizarUsuario(
  id: number,
  input: Partial<{ nome: string; perfil: PerfilUsuario; ativo: boolean }>
): Promise<Usuario> {
  const { data } = await api.patch<Usuario>(`/usuarios/${id}`, input);
  return data;
}

export async function redefinirSenha(id: number, senha: string): Promise<Usuario> {
  const { data } = await api.post<Usuario>(`/usuarios/${id}/redefinir-senha`, { senha });
  return data;
}
