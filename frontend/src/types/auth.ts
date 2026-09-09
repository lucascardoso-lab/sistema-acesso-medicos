export type PerfilUsuario = "administrador" | "tecnico";

export interface AuthUser {
  id: number;
  nome: string;
  login: string;
  email: string;
  perfil: PerfilUsuario;
}
