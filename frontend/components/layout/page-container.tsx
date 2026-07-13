import { cn } from "@/lib/utils";

interface PageContainerProps {
  children: React.ReactNode;
  className?: string;
}

export function PageContainer({ children, className }: PageContainerProps) {
  return (
    <main className={cn("min-h-screen w-full py-8 md:py-12", className)}>
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">{children}</div>
    </main>
  );
}
