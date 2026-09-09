import { api } from "./api";
import type { AuthUser } from "../types/auth";

export async function login(loginOuEmail: string, senha: string): Promise<AuthUser> {
  const { data } = await api.post<AuthUser>("/auth/login", {
    login_ou_email: loginOuEmail,
    senha,
  });
  return data;
}

export async function logout(): Promise<void> {
  await api.post("/auth/logout");
}

export async function getCurrentUser(): Promise<AuthUser> {
  const { data } = await api.get<AuthUser>("/auth/me");
  return data;
}
