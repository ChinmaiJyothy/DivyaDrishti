"use client";

import { useEffect, useState } from "react";

import { Loader2, Search } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  useGenerateChart,
  useLatestProfileChart,
  useSearchChart,
  useStudio,
} from "@/hooks/use-birth-profiles";
import { useSettings } from "@/providers/settings-provider";
import { BirthChartSvg } from "./birth-chart-svg";
import { DashaPanel } from "./dasha-panel";
import { DoshaPanel } from "./dosha-panel";
import { HousePanel } from "./house-panel";
import { InsightPanel } from "./insight-panel";
import { NakshatraPanel } from "./nakshatra-panel";
import { PlanetPanel } from "./planet-panel";
import { YogaPanel } from "./yoga-panel";

export function StudioPage() {
  const { settings } = useSettings();
  const profileId = settings.currentProfileId;

  const [chartType, setChartType] = useState("rashi");
  const [selected, setSelected] = useState<{ type: "planet" | "sign" | "house"; id: string } | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<Array<Record<string, unknown>>>([]);

  const chartQuery = useLatestProfileChart(profileId ?? "", chartType);
  const generate = useGenerateChart(profileId ?? "");
  const studio = useStudio(chartQuery.data?.id ?? "", undefined);
  const search = useSearchChart(chartQuery.data?.id ?? "");

  useEffect(() => {
    if (profileId && !chartQuery.data && !chartQuery.isLoading && !generate.isPending) {
      generate.mutate(chartType);
    }
  }, [profileId, chartQuery.data, chartQuery.isLoading, generate, chartType]);

  useEffect(() => {
    if (chartType && chartQuery.data?.id) {
      studio.refetch();
    }
  }, [chartType, chartQuery.data?.id, studio]);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim() || !chartQuery.data?.id) return;
    const results = await search.mutateAsync(searchQuery);
    setSearchResults(results);
  };

  const handleChartTypeChange = (value: string) => {
    setChartType(value);
    setSelected(null);
  };

  if (!profileId) {
    return (
      <Card className="m-6">
        <CardContent className="py-12 text-center">
          <p className="text-muted-foreground">Select a birth profile in settings to open the studio.</p>
        </CardContent>
      </Card>
    );
  }

  if (chartQuery.isLoading || studio.isLoading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  const detail = studio.data;

  if (!detail) {
    return (
      <Card className="m-6">
        <CardContent className="py-12 text-center">
          <p className="text-muted-foreground">No chart data available. Generate a chart to get started.</p>
          <Button
            className="mt-4"
            onClick={() => generate.mutate(chartType)}
            disabled={generate.isPending}
          >
            {generate.isPending ? "Generating..." : "Generate Chart"}
          </Button>
        </CardContent>
      </Card>
    );
  }

  const selectedPlanet = selected?.type === "planet" ? detail.planets[selected.id] : undefined;
  const selectedHouse = selected?.type === "house" ? detail.houses[selected.id] : undefined;
  const selectedNakshatra =
    selected?.type === "planet" && selectedPlanet
      ? detail.nakshatras[selected.id]
      : undefined;

  return (
    <div className="space-y-6 p-4 md:p-6 pb-24">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Birth Chart Studio</h1>
          <p className="text-sm text-muted-foreground">
            {detail.lagna} Lagna · {detail.moon_sign} Moon · {detail.sun_sign} Sun · {detail.maha_dasha} Maha Dasha
          </p>
        </div>

        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <Tabs value={chartType} onValueChange={handleChartTypeChange}>
            <TabsList>
              <TabsTrigger value="rashi">D1 Rashi</TabsTrigger>
              <TabsTrigger value="navamsa">D9 Navamsa</TabsTrigger>
            </TabsList>
          </Tabs>

          <form onSubmit={handleSearch} className="flex gap-2">
            <Input
              placeholder="Search planets, houses, yogas..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-56"
            />
            <Button type="submit" size="icon" variant="outline" disabled={search.isPending}>
              <Search className="h-4 w-4" />
            </Button>
          </form>
        </div>
      </div>

      {searchResults.length > 0 && (
        <Card>
          <CardContent className="py-3">
            <p className="text-sm font-medium mb-2">Search results</p>
            <div className="flex flex-wrap gap-2">
              {searchResults.map((result, idx) => (
                <Button
                  key={idx}
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    const type = String(result.type) as "planet" | "sign" | "house";
                    const id = String(result.id);
                    if (["planet", "sign", "house"].includes(type)) {
                      setSelected({ type, id });
                    }
                  }}
                >
                  {String(result.type)}: {String(result.label)}
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-6">
          <BirthChartSvg
            data={detail}
            selectedId={selected?.id}
            selectedType={selected?.type}
            onSelect={setSelected}
          />

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <YogaPanel detail={detail} />
            <DoshaPanel detail={detail} />
            <DashaPanel detail={detail} />
            <InsightPanel detail={detail} chartId={chartQuery.data?.id ?? ""} />
          </div>
        </div>

        <div className="space-y-4">
          {selectedPlanet ? (
            <PlanetPanel planet={selected?.id ?? ""} position={selectedPlanet} />
          ) : selectedHouse ? (
            <HousePanel house={selected?.id ?? ""} data={selectedHouse} />
          ) : selectedNakshatra ? (
            <NakshatraPanel nakshatra={selectedNakshatra} />
          ) : (
            <Card>
              <CardContent className="py-12 text-center">
                <p className="text-sm text-muted-foreground">
                  Click a planet, sign, or house on the chart to explore details.
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
