"use client";

import { ReactNode } from "react";

import { cn } from "@/lib/utils";
import type { ReasoningGraph as ReasoningGraphType } from "@/types";

interface ReasoningGraphProps {
  graph: ReasoningGraphType | null;
}

function renderNode(node: ReasoningGraphType["root"], depth = 0): ReactNode {
  if (!node) return null;

  const hasChildren = node.children && node.children.length > 0;

  return (
    <li key={node.id} className="mt-2">
      <div
        className={cn(
          "rounded-lg border p-2 text-sm",
          depth === 0 ? "bg-primary/10 font-medium" : "bg-muted"
        )}
      >
        <span className="text-xs uppercase tracking-wider text-muted-foreground">{node.type}</span>
        <p className="mt-0.5">{node.label}</p>
        {node.metadata && Object.keys(node.metadata).length > 0 && (
          <p className="mt-1 text-xs text-muted-foreground">
            {Object.entries(node.metadata)
              .map(([key, value]) => `${key}: ${String(value)}`)
              .join(" · ")}
          </p>
        )}
      </div>
      {hasChildren && (
        <ul className="ml-4 border-l border-border pl-4">
          {node.children.map((child) => renderNode(child, depth + 1))}
        </ul>
      )}
    </li>
  );
}

export function ReasoningGraph({ graph }: ReasoningGraphProps) {
  if (!graph || !graph.root) {
    return <p className="text-sm text-muted-foreground">No reasoning graph available.</p>;
  }

  return (
    <div className="overflow-x-auto">
      <ul className="list-none">{renderNode(graph.root)}</ul>
    </div>
  );
}
