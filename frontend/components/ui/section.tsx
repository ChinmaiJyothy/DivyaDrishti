import { cn } from "@/lib/utils";

interface SectionProps {
  children: React.ReactNode;
  className?: string;
  id?: string;
}

export function Section({ children, className, id }: SectionProps) {
  return (
    <section id={id} className={cn("py-12 md:py-16", className)}>
      {children}
    </section>
  );
}

interface SectionHeaderProps {
  title: string;
  description?: string;
  className?: string;
}

export function SectionHeader({ title, description, className }: SectionHeaderProps) {
  return (
    <div className={cn("mb-8 space-y-2", className)}>
      <h2 className="font-display text-3xl font-semibold tracking-tight">{title}</h2>
      {description && <p className="text-lg text-muted-foreground">{description}</p>}
    </div>
  );
}
