"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { DashaPeriod, StudioChartDetail } from "@/types";

interface DashaPanelProps {
  detail: StudioChartDetail;
}

export function DashaPanel({ detail }: DashaPanelProps) {
  const periods = detail.dashas.slice(0, 12);

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="text-base">Vimshottari Dasha Timeline</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2 max-h-[400px] overflow-y-auto">
        {periods.map((period) => (
          <DashaRow key={`${period.planet}-${period.start_date}`} period={period} />
        ))}
      </CardContent>
    </Card>
  );
}

function DashaRow({ period }: { period: DashaPeriod }) {
  return (
    <div className="flex items-center justify-between rounded border p-2 text-sm">
      <div className="flex items-center gap-2">
        <span className="font-medium">{period.planet}</span>
        {period.is_current && <Badge variant="default">Current</Badge>}
      </div>
      <span className="text-muted-foreground">
        {period.start_date} - {period.end_date}
      </span>
    </div>
  );
}
