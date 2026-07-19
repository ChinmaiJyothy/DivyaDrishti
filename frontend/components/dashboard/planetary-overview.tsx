"use client";

import { Sparkles, AlertCircle } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/empty-state";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  useBirthProfiles,
  useGenerateChart,
  useLatestProfileChart,
} from "@/hooks/use-birth-profiles";
import { useSettings } from "@/providers/settings-provider";

export function PlanetaryOverview() {
  const { data: profiles, isLoading: profilesLoading } = useBirthProfiles();
  const { settings } = useSettings();
  const currentId = String(settings.currentProfileId || profiles?.[0]?.id || "");
  const currentProfile = profiles?.find((p) => String(p.id) === currentId);
  const { data: chart, isLoading: chartLoading } = useLatestProfileChart(currentId || "");
  const generate = useGenerateChart(currentId || "");

  const isLoading = profilesLoading || chartLoading;

  const planets = chart?.chart_data
    ? Object.values(
        (chart.chart_data as { planets?: Record<string, { name: string; sign: string; house: number; nakshatra?: string }> }).planets || {}
      )
    : undefined;

  const handleGenerate = () => {
    generate.reset();
    generate.mutate("rashi");
  };

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
        ) : !currentId ? (
          <EmptyState
            icon={Sparkles}
            title="No profile selected"
            description="Select or create a birth profile."
          />
        ) : (generate.isError || chartLoading === false) && !chart?.chart_data ? (
          <div className="space-y-4 text-center">
            <EmptyState
              icon={Sparkles}
              title="No birth chart generated yet"
              description={
                currentProfile
                  ? `Generate a birth chart for ${currentProfile.profile_name}.`
                  : "Generate a birth chart for this profile."
              }
            />
            <Button onClick={handleGenerate} disabled={generate.isPending}>
              {generate.isPending ? "Generating..." : "Generate Birth Chart"}
            </Button>
            {generate.isError && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>Chart generation failed</AlertTitle>
                <AlertDescription>
                  {generate.error?.message || "An unexpected error occurred."}
                </AlertDescription>
              </Alert>
            )}
          </div>
        ) : planets && planets.length > 0 ? (
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
        ) : null}
      </CardContent>
    </Card>
  );
}
