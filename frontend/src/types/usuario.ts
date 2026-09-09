export type PerfilUsuario = "administrador" | "tecnico";

export interface Usuario {
  id: number;
  nome: string;
  login: string;
  email: string;
  perfil: PerfilUsuario;
  ativo: boolean;
}
