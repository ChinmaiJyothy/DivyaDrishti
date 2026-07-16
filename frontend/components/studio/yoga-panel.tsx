"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { StudioChartDetail, YogaDetail } from "@/types";

interface YogaPanelProps {
  detail: StudioChartDetail;
}

export function YogaPanel({ detail }: YogaPanelProps) {
  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="text-base">Yoga Explorer</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3 max-h-[400px] overflow-y-auto">
        {detail.yogas.length === 0 && (
          <p className="text-sm text-muted-foreground">No major yogas detected.</p>
        )}
        {detail.yogas.map((yoga) => (
          <YogaRow key={yoga.name} yoga={yoga} />
        ))}
      </CardContent>
    </Card>
  );
}

function YogaRow({ yoga }: { yoga: YogaDetail }) {
  return (
    <div className="rounded border p-3 text-sm space-y-2">
      <div className="flex items-center justify-between">
        <span className="font-medium">{yoga.name}</span>
        <Badge variant={yoga.strength === "strong" ? "default" : "secondary"}>{yoga.strength}</Badge>
      </div>
      <p className="text-muted-foreground">{yoga.description}</p>
      {yoga.matched_conditions.length > 0 && (
        <ul className="list-disc pl-4 text-xs text-muted-foreground">
          {yoga.matched_conditions.map((c) => (
            <li key={c}>{c}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
