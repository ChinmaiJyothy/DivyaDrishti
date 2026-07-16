"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { NakshatraDetail } from "@/types";

interface NakshatraPanelProps {
  nakshatra: NakshatraDetail;
}

export function NakshatraPanel({ nakshatra }: NakshatraPanelProps) {
  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="text-base">{nakshatra.name}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className="rounded bg-muted p-2">
            <span className="text-muted-foreground">Planet</span>
            <p className="font-medium">{nakshatra.planet}</p>
          </div>
          <div className="rounded bg-muted p-2">
            <span className="text-muted-foreground">Lord</span>
            <p className="font-medium">{nakshatra.lord}</p>
          </div>
          <div className="rounded bg-muted p-2">
            <span className="text-muted-foreground">Pada</span>
            <p className="font-medium">{nakshatra.pada}</p>
          </div>
          <div className="rounded bg-muted p-2">
            <span className="text-muted-foreground">Longitude</span>
            <p className="font-medium">{nakshatra.longitude.toFixed(2)}°</p>
          </div>
        </div>

        <div className="rounded bg-muted p-3 text-sm">
          <span className="text-muted-foreground">Characteristics</span>
          <p className="font-medium">{nakshatra.characteristics}</p>
        </div>

        <div className="rounded bg-muted p-3 text-sm">
          <span className="text-muted-foreground">Current Influence</span>
          <p className="font-medium">{nakshatra.current_influence}</p>
        </div>
      </CardContent>
    </Card>
  );
}
