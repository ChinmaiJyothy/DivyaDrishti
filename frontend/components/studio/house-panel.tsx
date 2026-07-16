"use client";

import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { HouseDetail } from "@/types";

interface HousePanelProps {
  house: string;
  data: HouseDetail;
}

export function HousePanel({ house, data }: HousePanelProps) {
  const router = useRouter();

  return (
    <Card className="h-full">
      <CardHeader className="flex flex-row items-center justify-between gap-2">
        <CardTitle className="text-base">House {house}</CardTitle>
        <Button
          size="sm"
          variant="outline"
          onClick={() =>
            router.push(`/ask?question=${encodeURIComponent(`What does house ${house} mean in my chart?`)}`)
          }
        >
          Ask about this house
        </Button>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className="rounded bg-muted p-2">
            <span className="text-muted-foreground">Sign</span>
            <p className="font-medium">{data.sign}</p>
          </div>
          <div className="rounded bg-muted p-2">
            <span className="text-muted-foreground">Lord</span>
            <p className="font-medium">{data.lord}</p>
          </div>
          <div className="rounded bg-muted p-2 col-span-2">
            <span className="text-muted-foreground">Meaning</span>
            <p className="font-medium">{data.meaning}</p>
          </div>
        </div>

        <div>
          <p className="mb-2 text-sm font-medium">Occupying Planets</p>
          <div className="flex flex-wrap gap-2">
            {data.planets.length > 0 ? (
              data.planets.map((p) => (
                <Badge key={p} variant="secondary">
                  {p}
                </Badge>
              ))
            ) : (
              <span className="text-sm text-muted-foreground">No planets</span>
            )}
          </div>
        </div>

        {data.aspected_by.length > 0 && (
          <div>
            <p className="mb-2 text-sm font-medium">Aspected By</p>
            <div className="flex flex-wrap gap-2">
              {data.aspected_by.map((p) => (
                <Badge key={p} variant="outline">
                  {p}
                </Badge>
              ))}
            </div>
          </div>
        )}

        <div className="flex flex-wrap gap-2">
          {data.is_kendra && <Badge>Kendra</Badge>}
          {data.is_upachaya && <Badge variant="outline">Upachaya</Badge>}
          {data.is_benefic && <Badge variant="secondary">Benefic</Badge>}
          {data.is_malefic && <Badge variant="destructive">Malefic</Badge>}
        </div>
      </CardContent>
    </Card>
  );
}
