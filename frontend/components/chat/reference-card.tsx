"use client";

import { BookOpen } from "lucide-react";

import { cn } from "@/lib/utils";
import type { ReferenceEntry } from "@/types";

interface ReferenceCardProps {
  references: ReferenceEntry[];
  className?: string;
}

export function ReferenceCard({ references, className }: ReferenceCardProps) {
  if (references.length === 0) {
    return <p className="text-sm text-muted-foreground">No classical references cited.</p>;
  }

  return (
    <div className={cn("space-y-3", className)}>
      {references.map((ref, index) => (
        <div key={index} className="flex items-start gap-3 rounded-lg bg-muted p-3 text-sm">
          <BookOpen className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
          <div>
            <p className="font-medium">{ref.book}</p>
            <p className="text-xs text-muted-foreground">
              {ref.chapter && `Chapter ${ref.chapter}`} {ref.verse && `Verse ${ref.verse}`}{" "}
              {ref.page && `Page ${ref.page}`}
            </p>
            {ref.translated_text && (
              <p className="mt-1 text-sm italic text-muted-foreground">{ref.translated_text}</p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
