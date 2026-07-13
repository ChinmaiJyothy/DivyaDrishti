"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createContext, useContext, useEffect, useMemo, useState } from "react";

import { getMe, login, logout, register } from "@/services/auth.service";
import type { LoginInput, RegisterInput } from "@/services/auth.service";
import type { AuthTokens, User } from "@/types";

interface AuthContextValue {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (input: LoginInput) => Promise<AuthTokens>;
  register: (input: RegisterInput) => Promise<AuthTokens>;
  logout: () => Promise<void>;
  isLoginPending: boolean;
  isRegisterPending: boolean;
  isLogoutPending: boolean;
  loginError: Error | null;
  registerError: Error | null;
}

const AuthContext = createContext<AuthContextValue | null>(null);

const AUTH_QUERY_KEY = ["auth", "me"];

function getStoredToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("access_token");
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const queryClient = useQueryClient();
  const [token, setToken] = useState<string | null>(getStoredToken());

  useEffect(() => {
    const handleStorage = (event: StorageEvent) => {
      if (event.key === "access_token") {
        setToken(event.newValue);
      }
    };
    window.addEventListener("storage", handleStorage);
    return () => window.removeEventListener("storage", handleStorage);
  }, []);

  const { data: user, isLoading: isUserLoading } = useQuery<User>({
    queryKey: AUTH_QUERY_KEY,
    queryFn: getMe,
    enabled: !!token,
    retry: 1,
  });

  const isAuthenticated = !!user && !!token;

  const loginMutation = useMutation<AuthTokens, Error, LoginInput>({
    mutationFn: login,
    onSuccess: (data) => {
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      setToken(data.access_token);
      queryClient.invalidateQueries({ queryKey: AUTH_QUERY_KEY });
    },
  });

  const registerMutation = useMutation<AuthTokens, Error, RegisterInput>({
    mutationFn: register,
    onSuccess: (data) => {
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      setToken(data.access_token);
      queryClient.invalidateQueries({ queryKey: AUTH_QUERY_KEY });
    },
  });

  const logoutMutation = useMutation<void, Error>({
    mutationFn: async () => {
      const refreshToken = typeof window !== "undefined" ? localStorage.getItem("refresh_token") : null;
      if (refreshToken) {
        await logout(refreshToken);
      }
    },
    onSettled: () => {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      setToken(null);
      queryClient.clear();
    },
  });

  const value = useMemo<AuthContextValue>(
    () => ({
      user: user ?? null,
      token,
      isAuthenticated,
      isLoading: isUserLoading,
      login: loginMutation.mutateAsync,
      register: registerMutation.mutateAsync,
      logout: logoutMutation.mutateAsync,
      isLoginPending: loginMutation.isPending,
      isRegisterPending: registerMutation.isPending,
      isLogoutPending: logoutMutation.isPending,
      loginError: loginMutation.error,
      registerError: registerMutation.error,
    }),
    [
      user,
      token,
      isAuthenticated,
      isUserLoading,
      loginMutation.mutateAsync,
      loginMutation.isPending,
      loginMutation.error,
      registerMutation.mutateAsync,
      registerMutation.isPending,
      registerMutation.error,
      logoutMutation.mutateAsync,
      logoutMutation.isPending,
    ]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
