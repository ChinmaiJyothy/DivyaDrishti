"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { DoshaDetail, StudioChartDetail } from "@/types";

interface DoshaPanelProps {
  detail: StudioChartDetail;
}

export function DoshaPanel({ detail }: DoshaPanelProps) {
  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="text-base">Dosha Explorer</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3 max-h-[400px] overflow-y-auto">
        {detail.doshas.length === 0 && (
          <p className="text-sm text-muted-foreground">No major doshas detected.</p>
        )}
        {detail.doshas.map((dosha) => (
          <DoshaRow key={dosha.name} dosha={dosha} />
        ))}
      </CardContent>
    </Card>
  );
}

function DoshaRow({ dosha }: { dosha: DoshaDetail }) {
  return (
    <div className="rounded border p-3 text-sm space-y-2">
      <div className="flex items-center justify-between">
        <span className="font-medium">{dosha.name}</span>
        <Badge variant={dosha.severity === "high" ? "destructive" : "secondary"}>{dosha.severity}</Badge>
      </div>
      <p className="text-muted-foreground">{dosha.conditions.join(", ")}</p>
      {dosha.mitigating_factors.length > 0 && (
        <p className="text-xs text-muted-foreground">Mitigation: {dosha.mitigating_factors.join(", ")}</p>
      )}
    </div>
  );
}
