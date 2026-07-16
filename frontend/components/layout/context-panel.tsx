"use client";

import { X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

import { BirthProfileCard } from "../dashboard/birth-profile-card";

interface ContextPanelProps {
  open: boolean;
  onToggle: () => void;
}

export function ContextPanel({ open, onToggle }: ContextPanelProps) {
  return (
    <aside
      className={cn(
        "hidden h-full flex-col border-l bg-card transition-all duration-300 ease-in-out lg:flex",
        open ? "w-80" : "w-0 overflow-hidden border-l-0"
      )}
    >
      {open && (
        <div className="flex h-full flex-col p-4">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
              Context
            </h2>
            <Button variant="ghost" size="icon" onClick={onToggle} aria-label="Close context panel">
              <X className="h-4 w-4" />
            </Button>
          </div>
          <div className="flex-1 space-y-6 overflow-y-auto">
            <BirthProfileCard />
          </div>
        </div>
      )}
    </aside>
  );
}
