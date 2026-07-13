import { cn } from "@/lib/utils";

interface AuthLayoutProps {
  children: React.ReactNode;
  className?: string;
}

export function AuthLayout({ children, className }: AuthLayoutProps) {
  return (
    <div
      className={cn(
        "flex min-h-screen flex-col items-center justify-center bg-ivory p-4 dark:bg-background",
        className
      )}
    >
      <div className="w-full max-w-md space-y-6">
        <div className="text-center">
          <h1 className="font-display text-3xl font-semibold tracking-tight">DivyaDrishti</h1>
          <p className="mt-2 text-sm text-muted-foreground">AI-powered Vedic Astrology</p>
        </div>
        {children}
      </div>
    </div>
  );
}
