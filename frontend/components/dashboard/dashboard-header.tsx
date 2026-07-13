"use client";

import { useAuth } from "@/providers/auth-provider";

export function DashboardHeader() {
  const { user } = useAuth();

  return (
    <div className="space-y-2">
      <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">
        Welcome back, {user?.name || "Seeker"}
      </h1>
      <p className="text-muted-foreground">
        Explore your birth charts, continue conversations, and generate Vedic astrology reports.
      </p>
    </div>
  );
}
