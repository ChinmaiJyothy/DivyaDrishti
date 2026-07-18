"use client";

import { BirthProfileCard } from "@/components/dashboard/birth-profile-card";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogTitle,
} from "@/components/ui/dialog";
import { useChatContext } from "@/components/chat/chat-context";
import { useMediaQuery } from "@/hooks/use-media-query";
import { cn } from "@/lib/utils";
import { useEffect, useState } from "react";

function ActiveMessageDetails() {
  const { activeMessage } = useChatContext();

  if (!activeMessage) {
    return (
      <Card>
        <CardContent className="py-6 text-sm text-muted-foreground">
          Select an assistant message to see its astrological context.
        </CardContent>
      </Card>
    );
  }

  const report = activeMessage.explainability_report;
  const chartFactors = report?.chart_factors_used;
  const reasoning = activeMessage.reasoning_result;
  const relevant = reasoning?.relevant_factors;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Insight Context</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {chartFactors && (
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div className="rounded-lg bg-muted p-2">
              <span className="block text-xs text-muted-foreground">Lagna</span>
              <span className="font-medium">{chartFactors.lagna || "—"}</span>
            </div>
            <div className="rounded-lg bg-muted p-2">
              <span className="block text-xs text-muted-foreground">Moon Sign</span>
              <span className="font-medium">{chartFactors.moon_sign || "—"}</span>
            </div>
            <div className="rounded-lg bg-muted p-2">
              <span className="block text-xs text-muted-foreground">Sun Sign</span>
              <span className="font-medium">{chartFactors.sun_sign || "—"}</span>
            </div>
            <div className="rounded-lg bg-muted p-2">
              <span className="block text-xs text-muted-foreground">Maha Dasha</span>
              <span className="font-medium">{chartFactors.maha_dasha || "—"}</span>
            </div>
          </div>
        )}

        {relevant && (
          <div className="space-y-2">
            {relevant.planets.length > 0 && (
              <div>
                <span className="text-xs text-muted-foreground">Relevant Planets</span>
                <p className="text-sm font-medium">{relevant.planets.join(", ")}</p>
              </div>
            )}
            {relevant.houses.length > 0 && (
              <div>
                <span className="text-xs text-muted-foreground">Relevant Houses</span>
                <p className="text-sm font-medium">{relevant.houses.join(", ")}</p>
              </div>
            )}
            {relevant.dashas.length > 0 && (
              <div>
                <span className="text-xs text-muted-foreground">Relevant Dashas</span>
                <p className="text-sm font-medium">{relevant.dashas.join(", ")}</p>
              </div>
            )}
            {relevant.yogas.length > 0 && (
              <div>
                <span className="text-xs text-muted-foreground">Yogas</span>
                <p className="text-sm font-medium">{relevant.yogas.join(", ")}</p>
              </div>
            )}
          </div>
        )}

        {report?.confidence_score && (
          <div>
            <span className="text-xs text-muted-foreground">Confidence</span>
            <p className="text-sm font-medium">
              {Math.round(report.confidence_score.overall_confidence)}%
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function SuggestedQuestions() {
  const { followUpQuestions, sendMessage } = useChatContext();

  if (followUpQuestions.length === 0) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Suggested Follow-ups</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {followUpQuestions.map((question, index) => (
          <Button
            key={index}
            variant="outline"
            size="sm"
            className="h-auto w-full justify-start whitespace-normal text-left text-sm"
            onClick={() => sendMessage(question)}
          >
            {question}
          </Button>
        ))}
      </CardContent>
    </Card>
  );
}

function PanelContent({ className }: { className?: string }) {
  return (
    <div className={cn("flex h-full flex-col space-y-4 overflow-y-auto p-4", className)}>
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
          Context
        </h2>
      </div>
      <BirthProfileCard />
      <ActiveMessageDetails />
      <SuggestedQuestions />
    </div>
  );
}

export function ChatContextPanel() {
  const { isContextPanelOpen, setContextPanelOpen } = useChatContext();
  const isDesktop = useMediaQuery("(min-width: 1024px)");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <>
      <aside
        className={cn(
          "hidden h-full flex-col border-l bg-card transition-all duration-300 ease-in-out lg:flex",
          isContextPanelOpen ? "w-80" : "w-0 overflow-hidden border-l-0"
        )}
      >
        {isContextPanelOpen && <PanelContent />}
      </aside>

      {mounted && !isDesktop && (
        <Dialog open={isContextPanelOpen} onOpenChange={setContextPanelOpen}>
          <DialogContent className="fixed inset-y-0 right-0 h-full w-80 max-w-none translate-x-0 translate-y-0 rounded-none border-r-0 border-l p-0 left-auto sm:rounded-none">
            <DialogTitle className="sr-only">Context Panel</DialogTitle>
            <PanelContent />
          </DialogContent>
        </Dialog>
      )}
    </>
  );
}
