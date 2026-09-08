export type PerfilUsuario = "administrador" | "tecnico";

export interface Usuario {
  id: number;
  nome: string;
  email: string;
  perfil: PerfilUsuario;
  ativo: boolean;
}
