"use client";

import {
  BookOpen,
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

import {
  Drawer,
  DrawerContent,
  DrawerHeader,
  DrawerTitle,
} from "@/components/ui/drawer";
import { cn } from "@/lib/utils";
import { useAuth } from "@/providers/auth-provider";

interface MobileNavProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
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

export function MobileNav({ open, onOpenChange }: MobileNavProps) {
  const pathname = usePathname();
  const { user } = useAuth();
  const isAdmin = user?.is_superuser || user?.role === "admin" || user?.role === "super_admin";

  const visibleItems = navItems.filter((item) => !item.admin || isAdmin);

  return (
    <Drawer open={open} onOpenChange={onOpenChange}>
      <DrawerContent className="h-[80vh]">
        <DrawerHeader className="text-left">
          <DrawerTitle className="font-display">DivyaDrishti</DrawerTitle>
        </DrawerHeader>
        <nav className="flex flex-col gap-1 p-4" aria-label="Mobile navigation">
          {visibleItems.map((item) => {
            const active = isActive(pathname, item.href);
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => onOpenChange(false)}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-3 text-sm font-medium transition-colors",
                  active
                    ? "bg-primary/10 text-primary"
                    : "text-muted-foreground hover:bg-accent hover:text-foreground"
                )}
              >
                <Icon className="h-5 w-5" aria-hidden="true" />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </DrawerContent>
    </Drawer>
  );
}
