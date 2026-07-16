"use client";

import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { PlanetPosition } from "@/types";

interface PlanetPanelProps {
  planet: string;
  position: PlanetPosition;
}

export function PlanetPanel({ planet, position }: PlanetPanelProps) {
  const router = useRouter();

  const aspects = position.aspects?.length
    ? position.aspects
    : [];
  const conjunctions = position.conjunctions?.length
    ? position.conjunctions.filter((p) => p !== planet)
    : [];

  return (
    <Card className="h-full">
      <CardHeader className="flex flex-row items-center justify-between gap-2">
        <CardTitle className="text-base">{planet}</CardTitle>
        <Button
          size="sm"
          variant="outline"
          onClick={() =>
            router.push(`/ask?question=${encodeURIComponent(`Tell me about ${planet} in my chart`)}`)
          }
        >
          Ask DivyaDrishti
        </Button>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className="rounded bg-muted p-2">
            <span className="text-muted-foreground">Sign</span>
            <p className="font-medium">{position.sign}</p>
          </div>
          <div className="rounded bg-muted p-2">
            <span className="text-muted-foreground">House</span>
            <p className="font-medium">{position.house}</p>
          </div>
          <div className="rounded bg-muted p-2">
            <span className="text-muted-foreground">Degree</span>
            <p className="font-medium">{position.degree?.toFixed(2)}°</p>
          </div>
          <div className="rounded bg-muted p-2">
            <span className="text-muted-foreground">Nakshatra</span>
            <p className="font-medium">{position.nakshatra}</p>
          </div>
          <div className="rounded bg-muted p-2">
            <span className="text-muted-foreground">Dignity</span>
            <p className="font-medium">{position.dignity}</p>
          </div>
          <div className="rounded bg-muted p-2">
            <span className="text-muted-foreground">Nakshatra Lord</span>
            <p className="font-medium">{position.nakshatra_lord}</p>
          </div>
          <div className="rounded bg-muted p-2">
            <span className="text-muted-foreground">Retrograde</span>
            <p className="font-medium">{position.retrograde ? "Yes" : "No"}</p>
          </div>
          <div className="rounded bg-muted p-2">
            <span className="text-muted-foreground">Combust</span>
            <p className="font-medium">{position.combust ? "Yes" : "No"}</p>
          </div>
        </div>

        {position.navamsa_sign && (
          <div className="rounded bg-muted p-3 text-sm">
            <span className="text-muted-foreground">Navamsa</span>
            <p className="font-medium">{position.navamsa_sign} (house {position.navamsa_house})</p>
          </div>
        )}

        {aspects.length > 0 && (
          <div>
            <p className="mb-2 text-sm font-medium">Aspects</p>
            <div className="flex flex-wrap gap-2">
              {aspects.map((target) => (
                <Badge key={target} variant="secondary">
                  {target}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {conjunctions.length > 0 && (
          <div>
            <p className="mb-2 text-sm font-medium">Conjunctions</p>
            <div className="flex flex-wrap gap-2">
              {conjunctions.map((p) => (
                <Badge key={p} variant="outline">
                  {p}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
