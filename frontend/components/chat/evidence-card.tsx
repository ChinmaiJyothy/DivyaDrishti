"use client";

import { cn } from "@/lib/utils";
import type { EvidenceExplanation } from "@/types";

interface EvidenceCardProps {
  evidence: EvidenceExplanation[];
  type: "supporting" | "conflicting";
}

function formatImpact(value: number): string {
  const pct = Math.abs(value) <= 1 ? Math.round(value * 100) : Math.round(value);
  const sign = pct > 0 ? "+" : "";
  return `${sign}${pct}%`;
}

export function EvidenceCard({ evidence, type }: EvidenceCardProps) {
  if (evidence.length === 0) {
    return <p className="text-sm text-muted-foreground">No {type} evidence recorded.</p>;
  }

  return (
    <div className="space-y-3">
      {evidence.map((item, index) => (
        <div
          key={index}
          className={cn(
            "rounded-lg border-l-4 p-3 text-sm",
            type === "supporting"
              ? "border-emerald-500 bg-emerald-50/50"
              : "border-rose-500 bg-rose-50/50"
          )}
        >
          <p className="font-medium">{item.factor}</p>
          <p className="mt-1 text-muted-foreground">{item.why_it_matters}</p>
          {item.source && (
            <p className="mt-1 text-xs text-muted-foreground">Source: {item.source}</p>
          )}
          {item.confidence_impact !== 0 && (
            <p className="mt-1 text-xs font-medium">
              Impact: {formatImpact(item.confidence_impact)}
            </p>
          )}
        </div>
      ))}
    </div>
  );
}