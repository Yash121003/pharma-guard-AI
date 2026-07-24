import { apiClient } from "./client";
import type { UserPublic, UserRole } from "../types";

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  const { data } = await apiClient.post<TokenResponse>("/auth/login", { email, password });
  return data;
}

export async function register(payload: {
  email: string;
  password: string;
  full_name: string;
  role: UserRole;
}): Promise<UserPublic> {
  const { data } = await apiClient.post<UserPublic>("/auth/register", payload);
  return data;
}

export async function me(): Promise<UserPublic> {
  const { data } = await apiClient.get<UserPublic>("/auth/me");
  return data;
}

export async function logout(): Promise<void> {
  await apiClient.post("/auth/logout");
}
