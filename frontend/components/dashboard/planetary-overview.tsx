"use client";

import { Sparkles } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/empty-state";
import { useBirthProfiles } from "@/hooks/use-birth-profiles";
import { useLatestProfileChart } from "@/hooks/use-birth-profiles";
import { useSettings } from "@/providers/settings-provider";

export function PlanetaryOverview() {
  const { data: profiles, isLoading: profilesLoading } = useBirthProfiles();
  const { settings } = useSettings();
  const currentId = String(settings.currentProfileId || profiles?.[0]?.id || "");
  const { data: chart, isLoading: chartLoading } = useLatestProfileChart(currentId || "");

  const isLoading = profilesLoading || chartLoading;

  const planets = chart?.chart_data
    ? (chart.chart_data as { planets?: { name: string; sign: string; house: number; nakshatra?: string }[] }).planets
    : undefined;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Planetary Positions</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
            {Array.from({ length: 8 }).map((_, i) => (
              <Skeleton key={i} className="h-24 w-full" />
            ))}
          </div>
        ) : !planets || planets.length === 0 ? (
          <EmptyState
            icon={Sparkles}
            title="No chart data"
            description="Select a birth profile to view planetary positions."
          />
        ) : (
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
            {planets.map((planet) => (
              <div
                key={planet.name}
                className="rounded-lg border bg-card p-3 text-center transition-colors hover:bg-muted/50"
              >
                <p className="font-semibold">{planet.name}</p>
                <p className="text-sm text-muted-foreground">{planet.sign}</p>
                <p className="text-xs text-muted-foreground">House {planet.house}</p>
                {planet.nakshatra && (
                  <p className="text-xs text-muted-foreground">{planet.nakshatra}</p>
                )}
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
