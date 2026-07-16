"use client";

import { useState } from "react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { useAnalyzeChart } from "@/hooks/use-birth-profiles";
import type { StudioChartDetail, StudioInsight } from "@/types";

interface InsightPanelProps {
  detail: StudioChartDetail;
  chartId: string;
}

const TOPIC_LABELS: Record<string, string> = {
  career: "Career & Status",
  marriage: "Marriage & Relationships",
  finance: "Finance & Wealth",
  health: "Health & Vitality",
  general: "General Analysis",
};

export function InsightPanel({ detail, chartId }: InsightPanelProps) {
  const [question, setQuestion] = useState("");
  const [insight, setInsight] = useState<StudioInsight | null>(detail.insight);
  const analyze = useAnalyzeChart(chartId);

  const handleAsk = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;
    const result = await analyze.mutateAsync(question);
    setInsight(result);
  };

  const active = insight ?? detail.insight;

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="text-base">Insight Panel</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <form onSubmit={handleAsk} className="flex gap-2">
          <Input
            placeholder="Ask about career, marriage, finance, health..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />
          <Button type="submit" disabled={analyze.isPending}>
            Analyze
          </Button>
        </form>

        {active && (
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground">Topic:</span>
              <Badge variant="outline">{TOPIC_LABELS[active.topic] ?? active.topic}</Badge>
            </div>

            <p className="text-sm">{active.summary}</p>

            <div className="space-y-2">
              {active.highlights.map((h) => (
                <div
                  key={`${h.type}-${h.id}`}
                  className="flex items-center justify-between rounded bg-muted p-2 text-sm"
                >
                  <div className="flex items-center gap-2">
                    <Badge variant="secondary" className="capitalize">
                      {h.type}
                    </Badge>
                    <span className="font-medium">{h.label}</span>
                  </div>
                  <span className="text-xs text-muted-foreground">{h.reason}</span>
                </div>
              ))}
            </div>

            {active.recommendations.length > 0 && (
              <ul className="list-disc pl-4 text-sm text-muted-foreground">
                {active.recommendations.map((r) => (
                  <li key={r}>{r}</li>
                ))}
              </ul>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
