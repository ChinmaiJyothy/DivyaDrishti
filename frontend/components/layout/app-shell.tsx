"use client";

import * as React from "react";

import { Footer } from "@/components/layout/footer";
import { MobileNav } from "@/components/layout/mobile-nav";
import { Navbar } from "@/components/layout/navbar";
import { Sidebar, SidebarGroup, SidebarLabel } from "@/components/layout/sidebar";
import { cn } from "@/lib/utils";

interface AppShellProps {
  children: React.ReactNode;
  className?: string;
}

export function AppShell({ children, className }: AppShellProps) {
  const [mobileOpen, setMobileOpen] = React.useState(false);

  return (
    <div className={cn("flex min-h-screen flex-col bg-background", className)}>
      <Navbar onMenuClick={() => setMobileOpen(true)} />
      <MobileNav open={mobileOpen} onOpenChange={setMobileOpen}>
        <SidebarGroup>
          <SidebarLabel>Navigation</SidebarLabel>
          <p className="px-2 text-sm text-muted-foreground">Mobile navigation links will go here.</p>
        </SidebarGroup>
      </MobileNav>
      <div className="flex flex-1">
        <Sidebar>
          <SidebarGroup>
            <SidebarLabel>Navigation</SidebarLabel>
            <p className="px-2 text-sm text-muted-foreground">Sidebar links will go here.</p>
          </SidebarGroup>
        </Sidebar>
        <main className="flex flex-1 flex-col lg:pl-64">
          <div className="flex-1 p-4 sm:p-6 lg:p-8">{children}</div>
          <Footer />
        </main>
      </div>
    </div>
  );
}
