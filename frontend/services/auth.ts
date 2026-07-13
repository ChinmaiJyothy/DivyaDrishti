import { apiRequest } from "@/lib/api";
import type { AuthTokens, User } from "@/types";

export interface LoginInput {
  email: string;
  password: string;
}

export interface RegisterInput {
  email: string;
  password: string;
  name: string;
}

export async function login(input: LoginInput): Promise<AuthTokens> {
  return apiRequest<AuthTokens>("POST", "/auth/login", input);
}

export async function register(input: RegisterInput): Promise<AuthTokens> {
  return apiRequest<AuthTokens>("POST", "/auth/register", input);
}

export async function logout(refreshToken: string): Promise<void> {
  return apiRequest<void>("POST", "/auth/logout", { refresh_token: refreshToken });
}

export async function refresh(refreshToken: string): Promise<AuthTokens> {
  return apiRequest<AuthTokens>("POST", "/auth/refresh", { refresh_token: refreshToken });
}

export async function getMe(): Promise<User> {
  return apiRequest<User>("GET", "/users/me");
}
