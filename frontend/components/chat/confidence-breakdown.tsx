"use client";

import { cn } from "@/lib/utils";
import type { ConfidenceBreakdown as ConfidenceBreakdownType } from "@/types";

interface ConfidenceBreakdownProps {
  score: ConfidenceBreakdownType | null;
}

function toPercentage(value: number): number {
  return value <= 1 ? Math.round(value * 100) : Math.round(value);
}

export function ConfidenceBreakdown({ score }: ConfidenceBreakdownProps) {
  if (!score) return null;

  const percentage = toPercentage(score.overall_confidence);
  const color =
    percentage >= 80 ? "bg-emerald-500" : percentage >= 50 ? "bg-amber-500" : "bg-rose-500";

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium">Overall confidence</span>
        <span className="text-sm font-semibold">{percentage}%</span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
        <div className={cn("h-full transition-all duration-500", color)} style={{ width: `${percentage}%` }} />
      </div>
      {score.contributors.length > 0 && (
        <ul className="space-y-1 text-sm text-muted-foreground">
          {score.contributors.map((contributor, index) => (
            <li key={index} className="flex justify-between">
              <span>{contributor.name}</span>
              <span className="font-medium">{toPercentage(contributor.contribution)}%</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}