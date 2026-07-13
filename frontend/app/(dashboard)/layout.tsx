"use client";

import { usePathname } from "next/navigation";

import { ProtectedRoute } from "@/components/auth/protected-route";
import { ChatLayout } from "@/components/chat/chat-layout";
import { DashboardLayout } from "@/components/layout/dashboard-layout";

export default function DashboardGroupLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname() ?? "";
  const isChat = pathname.startsWith("/chat");

  return (
    <ProtectedRoute>
      {isChat ? <ChatLayout>{children}</ChatLayout> : <DashboardLayout>{children}</DashboardLayout>}
    </ProtectedRoute>
  );
}
