import { AppShell } from "@/components/layout/app-shell";

interface AdminLayoutProps {
  children: React.ReactNode;
}

export function AdminLayout({ children }: AdminLayoutProps) {
  return <AppShell>{children}</AppShell>;
}
