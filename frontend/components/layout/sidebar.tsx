"use client";

import {
  BookOpen,
  ChevronLeft,
  ChevronRight,
  LayoutDashboard,
  MessageCircleQuestion,
  MessageSquare,
  MessageSquareWarning,
  Settings,
  Shield,
  Sparkles,
  Users,
  User,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";
import { useAuth } from "@/providers/auth-provider";

interface SidebarProps {
  collapsed: boolean;
  onToggleCollapse: () => void;
  className?: string;
}

const navItems = [
  { label: "Dashboard", href: "/", icon: LayoutDashboard },
  { label: "Ask DivyaDrishti", href: "/ask", icon: MessageCircleQuestion },
  { label: "Birth Profiles", href: "/profiles", icon: Users },
  { label: "Birth Charts", href: "/charts", icon: Sparkles },
  { label: "Conversations", href: "/conversations", icon: MessageSquare },
  { label: "Reports", href: "/reports", icon: BookOpen },
  { label: "Knowledge Library", href: "/knowledge", icon: BookOpen, admin: true },
  { label: "Settings", href: "/settings", icon: Settings },
  { label: "Feedback", href: "/feedback", icon: MessageSquareWarning },
  { label: "Admin", href: "/admin", icon: Shield, admin: true },
  { label: "User Profile", href: "/profile", icon: User },
];

function isActive(pathname: string, href: string): boolean {
  if (href === "/") return pathname === "/";
  return pathname.startsWith(href);
}

export function Sidebar({ collapsed, onToggleCollapse, className }: SidebarProps) {
  const pathname = usePathname();
  const { user } = useAuth();
  const isAdmin = user?.is_superuser || user?.role === "admin" || user?.role === "super_admin";

  const visibleItems = navItems.filter((item) => !item.admin || isAdmin);

  return (
    <aside
      className={cn(
        "fixed inset-y-0 left-0 z-30 hidden flex-col border-r bg-card transition-all duration-300 ease-in-out lg:flex",
        collapsed ? "w-20" : "w-64",
        className
      )}
    >
      <TooltipProvider delayDuration={200}>
        <div className="flex h-full flex-col p-3">
          <div className={cn("flex items-center py-4", collapsed ? "justify-center" : "px-2")}>
            {!collapsed && (
              <span className="font-display text-xl font-semibold tracking-tight">DivyaDrishti</span>
            )}
          </div>

          <nav className="flex-1 space-y-1 overflow-y-auto" aria-label="Sidebar navigation">
            {visibleItems.map((item) => {
              const active = isActive(pathname, item.href);
              const Icon = item.icon;
              return (
                <Tooltip key={item.href}>
                  <TooltipTrigger asChild>
                    <Link
                      href={item.href}
                      className={cn(
                        "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                        active
                          ? "bg-primary/10 text-primary"
                          : "text-muted-foreground hover:bg-accent hover:text-foreground",
                        collapsed && "justify-center"
                      )}
                      aria-current={active ? "page" : undefined}
                    >
                      <Icon className="h-5 w-5 shrink-0" aria-hidden="true" />
                      {!collapsed && <span>{item.label}</span>}
                    </Link>
                  </TooltipTrigger>
                  {collapsed && <TooltipContent side="right">{item.label}</TooltipContent>}
                </Tooltip>
              );
            })}
          </nav>

          <div className="space-y-1 border-t pt-3">
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size={collapsed ? "icon" : "default"}
                  className={cn(
                    "w-full justify-start gap-3 text-sm font-medium text-muted-foreground hover:bg-accent hover:text-foreground",
                    collapsed && "justify-center"
                  )}
                  onClick={onToggleCollapse}
                  aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
                >
                  {collapsed ? (
                    <ChevronRight className="h-5 w-5" />
                  ) : (
                    <>
                      <ChevronLeft className="h-5 w-5" />
                      <span>Collapse</span>
                    </>
                  )}
                </Button>
              </TooltipTrigger>
              {collapsed && <TooltipContent side="right">Expand</TooltipContent>}
            </Tooltip>
          </div>
        </div>
      </TooltipProvider>
    </aside>
  );
}
