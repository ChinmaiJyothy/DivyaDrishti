import { cn } from "@/lib/utils";

interface FooterProps {
  className?: string;
}

export function Footer({ className }: FooterProps) {
  return (
    <footer className={cn("w-full border-t bg-background py-6", className)}>
      <div className="container flex flex-col items-center justify-between gap-4 px-4 text-sm text-muted-foreground sm:flex-row sm:px-6 lg:px-8">
        <p>© {new Date().getFullYear()} DivyaDrishti. All rights reserved.</p>
      </div>
    </footer>
  );
}
