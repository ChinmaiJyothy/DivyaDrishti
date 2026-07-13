"use client";

import { createContext, useContext, useMemo, useState } from "react";

interface AuthContextValue {
  isAuthenticated: boolean;
  user: null;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextValue>({
  isAuthenticated: false,
  user: null,
  isLoading: false,
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isLoading] = useState(false);

  const value = useMemo(
    () => ({
      isAuthenticated: false,
      user: null,
      isLoading,
    }),
    [isLoading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
