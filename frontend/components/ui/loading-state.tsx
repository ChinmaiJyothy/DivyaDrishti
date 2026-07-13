import { Loader2 } from "lucide-react";

import { cn } from "@/lib/utils";

interface LoadingStateProps {
  message?: string;
  className?: string;
}

export function LoadingState({ message = "Loading...", className }: LoadingStateProps) {
  return (
    <div className={cn("flex min-h-40 flex-col items-center justify-center gap-3 text-muted-foreground", className)}>
      <Loader2 className="h-8 w-8 animate-spin" />
      <p className="text-sm font-medium">{message}</p>
    </div>
  );
}
