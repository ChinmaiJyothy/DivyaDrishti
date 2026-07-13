import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";

import { AuthProvider, useAuth } from "@/providers/auth-provider";

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

function wrapper({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>{children}</AuthProvider>
    </QueryClientProvider>
  );
}

vi.mock("@/services/auth.service", () => ({
  getMe: vi.fn().mockResolvedValue({ id: 1, name: "Test", email: "test@example.com", role: "user" }),
  login: vi.fn().mockResolvedValue({ access_token: "token", refresh_token: "refresh", token_type: "bearer" }),
  register: vi.fn(),
  logout: vi.fn(),
}));

describe("useAuth", () => {
  beforeEach(() => {
    localStorage.clear();
    queryClient.clear();
  });

  it("is unauthenticated when no token exists", async () => {
    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current.isAuthenticated).toBe(false);
  });

  it("fetches user when token is present", async () => {
    localStorage.setItem("access_token", "token");

    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => expect(result.current.isAuthenticated).toBe(true));
    expect(result.current.user?.name).toBe("Test");
  });
});
