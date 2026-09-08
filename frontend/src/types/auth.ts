export type PerfilUsuario = "administrador" | "tecnico";

export interface AuthUser {
  id: number;
  nome: string;
  email: string;
  perfil: PerfilUsuario;
}
