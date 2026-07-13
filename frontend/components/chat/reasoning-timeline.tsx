"use client";

import { motion } from "framer-motion";
import { CheckCircle2, Circle } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { ReasoningStep } from "@/types";

interface ReasoningTimelineProps {
  steps: ReasoningStep[];
}

export function ReasoningTimeline({ steps }: ReasoningTimelineProps) {
  if (steps.length === 0) {
    return <p className="text-sm text-muted-foreground">No reasoning steps recorded.</p>;
  }

  return (
    <div className="relative space-y-4 pl-4">
      <div className="absolute left-[21px] top-2 h-full w-px bg-border" />
      {steps.map((step, index) => {
        const isLast = index === steps.length - 1;

        return (
          <motion.div
            key={index}
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.05 }}
            className="relative flex items-start gap-3"
          >
            <div
              className={cn(
                "z-10 flex h-4 w-4 shrink-0 items-center justify-center rounded-full border-2 bg-background",
                isLast ? "border-primary" : "border-muted-foreground"
              )}
            >
              {isLast ? (
                <CheckCircle2 className="h-3 w-3 text-primary" />
              ) : (
                <Circle className="h-2 w-2 text-muted-foreground" />
              )}
            </div>
            <div className="flex-1 rounded-lg bg-muted p-2 text-sm">
              <p className="font-medium">{step.step}</p>
              <p className="text-muted-foreground">{step.details}</p>
              {step.evidence.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {step.evidence.map((evidence, evidenceIndex) => (
                    <Badge key={evidenceIndex} variant="secondary" className="text-xs">
                      {evidence}
                    </Badge>
                  ))}
                </div>
              )}
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}