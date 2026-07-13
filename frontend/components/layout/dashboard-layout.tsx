"use client";

import * as React from "react";

import { BottomNav } from "@/components/layout/bottom-nav";
import { ContextPanel } from "@/components/layout/context-panel";
import { MobileNav } from "@/components/layout/mobile-nav";
import { Navbar } from "@/components/layout/navbar";
import { Sidebar } from "@/components/layout/sidebar";
import { cn } from "@/lib/utils";

interface DashboardLayoutProps {
  children: React.ReactNode;
  className?: string;
}

export function DashboardLayout({ children, className }: DashboardLayoutProps) {
  const [mobileOpen, setMobileOpen] = React.useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = React.useState(false);
  const [contextPanelOpen, setContextPanelOpen] = React.useState(true);

  return (
    <div className={cn("flex min-h-screen flex-col bg-background", className)}>
      <Navbar
        onMenuClick={() => setMobileOpen(true)}
        onContextToggle={() => setContextPanelOpen((prev) => !prev)}
      />
      <MobileNav open={mobileOpen} onOpenChange={setMobileOpen} />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar
          collapsed={sidebarCollapsed}
          onToggleCollapse={() => setSidebarCollapsed((prev) => !prev)}
        />
        <main
          className={cn(
            "flex flex-1 flex-col transition-all duration-300 ease-in-out",
            sidebarCollapsed ? "lg:pl-20" : "lg:pl-64"
          )}
        >
          <div className="flex flex-1 overflow-hidden">
            <div className="flex flex-1 flex-col overflow-y-auto">
              <div className="flex-1 p-4 sm:p-6 lg:p-8">{children}</div>
            </div>
            <ContextPanel
              open={contextPanelOpen}
              onToggle={() => setContextPanelOpen((prev) => !prev)}
            />
          </div>
        </main>
      </div>
      <BottomNav />
    </div>
  );
}
