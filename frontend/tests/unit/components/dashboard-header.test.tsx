import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";

import { DashboardHeader } from "@/components/dashboard/dashboard-header";

vi.mock("@/providers/auth-provider", () => ({
  useAuth: () => ({ user: { name: "Seeker" }, isAuthenticated: true }),
  AuthProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

describe("DashboardHeader", () => {
  it("renders a welcome message with the user name", () => {
    render(<DashboardHeader />);
    expect(screen.getByText("Welcome back, Seeker")).toBeInTheDocument();
  });
});
