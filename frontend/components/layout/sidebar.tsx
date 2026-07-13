import { cn } from "@/lib/utils";

interface SidebarProps {
  children: React.ReactNode;
  className?: string;
}

export function Sidebar({ children, className }: SidebarProps) {
  return (
    <aside
      className={cn(
        "fixed inset-y-0 left-0 z-30 hidden w-64 overflow-y-auto border-r bg-card lg:block",
        className
      )}
    >
      <div className="flex h-full flex-col p-4">{children}</div>
    </aside>
  );
}

export function SidebarGroup({ children, className }: SidebarProps) {
  return <div className={cn("py-2", className)}>{children}</div>;
}

export function SidebarLabel({ children, className }: { children: React.ReactNode; className?: string }) {
  return <div className={cn("mb-2 px-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground", className)}>{children}</div>;
}
