"use client";

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Card, CardContent } from "@/components/ui/card";
import { ConfidenceBreakdown } from "@/components/chat/confidence-breakdown";
import { EvidenceCard } from "@/components/chat/evidence-card";
import { ReferenceCard } from "@/components/chat/reference-card";
import { ReasoningGraph } from "@/components/chat/reasoning-graph";
import { ReasoningTimeline } from "@/components/chat/reasoning-timeline";
import { SuggestedPrompts } from "@/components/chat/suggested-prompts";
import { useChatContext } from "@/components/chat/chat-context";
import type { AIResponse, ExplainabilityReport, Message, ReasoningResult } from "@/types";

interface ExplainabilityPanelProps {
  message?: Message;
  report?: ExplainabilityReport | null;
  aiResponse?: AIResponse | null;
  reasoningResult?: ReasoningResult | null;
  isActive?: boolean;
  onValueChange?: (values: string[]) => void;
}

export function ExplainabilityPanel({
  message,
  report: reportProp,
  aiResponse: aiResponseProp,
  reasoningResult: reasoningResultProp,
  onValueChange,
}: ExplainabilityPanelProps) {
  const { sendMessage } = useChatContext();

  const report = reportProp ?? message?.explainability_report ?? null;
  const aiResponse = aiResponseProp ?? message?.ai_response_json ?? null;
  const reasoningResult = reasoningResultProp ?? message?.reasoning_result ?? null;

  if (!report) return null;

  const directAnswer = aiResponse?.direct_answer || message?.content || "No direct answer available.";
  const interpretation = aiResponse?.interpretation || reasoningResult?.reasoning_summary || "";
  const why = aiResponse?.why_this_conclusion || reasoningResult?.reasoning_summary || "";
  const supporting = report.supporting_evidence || [];
  const conflicting = report.conflicting_evidence || [];
  const confidence = report.confidence_score || null;
  const references = report.classical_references || [];
  const reasoningSteps = reasoningResult?.reasoning_steps || [];
  const reasoningGraph = report.reasoning_path || null;
  const followUp = aiResponse?.follow_up_questions || reasoningResult?.suggested_follow_up_topics || [];

  return (
    <Card className="mt-2 overflow-hidden border border-border/50 bg-card/50">
      <CardContent className="p-0">
        <Accordion
          type="multiple"
          defaultValue={["direct-answer"]}
          className="w-full"
          onValueChange={onValueChange}
        >
          <AccordionItem value="direct-answer">
            <AccordionTrigger className="px-4 py-3 text-sm font-medium hover:no-underline">
              Direct Answer
            </AccordionTrigger>
            <AccordionContent className="px-4 pb-4 text-sm">
              <p className="whitespace-pre-wrap leading-relaxed">{directAnswer}</p>
            </AccordionContent>
          </AccordionItem>

          {interpretation && (
            <AccordionItem value="interpretation">
              <AccordionTrigger className="px-4 py-3 text-sm font-medium hover:no-underline">
                Astrological Interpretation
              </AccordionTrigger>
              <AccordionContent className="px-4 pb-4 text-sm">
                <p className="whitespace-pre-wrap leading-relaxed">{interpretation}</p>
              </AccordionContent>
            </AccordionItem>
          )}

          {why && (
            <AccordionItem value="why">
              <AccordionTrigger className="px-4 py-3 text-sm font-medium hover:no-underline">
                Why this conclusion?
              </AccordionTrigger>
              <AccordionContent className="px-4 pb-4 text-sm">
                <p className="whitespace-pre-wrap leading-relaxed">{why}</p>
              </AccordionContent>
            </AccordionItem>
          )}

          {supporting.length > 0 && (
            <AccordionItem value="supporting-evidence">
              <AccordionTrigger className="px-4 py-3 text-sm font-medium hover:no-underline">
                Supporting Evidence
              </AccordionTrigger>
              <AccordionContent className="px-4 pb-4">
                <EvidenceCard evidence={supporting} type="supporting" />
              </AccordionContent>
            </AccordionItem>
          )}

          {conflicting.length > 0 && (
            <AccordionItem value="conflicting-evidence">
              <AccordionTrigger className="px-4 py-3 text-sm font-medium hover:no-underline">
                Conflicting Evidence
              </AccordionTrigger>
              <AccordionContent className="px-4 pb-4">
                <EvidenceCard evidence={conflicting} type="conflicting" />
              </AccordionContent>
            </AccordionItem>
          )}

          {confidence && (
            <AccordionItem value="confidence">
              <AccordionTrigger className="px-4 py-3 text-sm font-medium hover:no-underline">
                Confidence Breakdown
              </AccordionTrigger>
              <AccordionContent className="px-4 pb-4">
                <ConfidenceBreakdown score={confidence} />
              </AccordionContent>
            </AccordionItem>
          )}

          {references.length > 0 && (
            <AccordionItem value="references">
              <AccordionTrigger className="px-4 py-3 text-sm font-medium hover:no-underline">
                Classical References
              </AccordionTrigger>
              <AccordionContent className="px-4 pb-4">
                <ReferenceCard references={references} />
              </AccordionContent>
            </AccordionItem>
          )}

          {reasoningSteps.length > 0 && (
            <AccordionItem value="timeline">
              <AccordionTrigger className="px-4 py-3 text-sm font-medium hover:no-underline">
                Reasoning Timeline
              </AccordionTrigger>
              <AccordionContent className="px-4 pb-4">
                <ReasoningTimeline steps={reasoningSteps} />
              </AccordionContent>
            </AccordionItem>
          )}

          {reasoningGraph && (
            <AccordionItem value="graph">
              <AccordionTrigger className="px-4 py-3 text-sm font-medium hover:no-underline">
                Reasoning Graph
              </AccordionTrigger>
              <AccordionContent className="px-4 pb-4">
                <ReasoningGraph graph={reasoningGraph} />
              </AccordionContent>
            </AccordionItem>
          )}

          {followUp.length > 0 && (
            <AccordionItem value="follow-up">
              <AccordionTrigger className="px-4 py-3 text-sm font-medium hover:no-underline">
                Suggested Follow-up Questions
              </AccordionTrigger>
              <AccordionContent className="px-4 pb-4">
                <SuggestedPrompts questions={followUp} onSelect={sendMessage} />
              </AccordionContent>
            </AccordionItem>
          )}
        </Accordion>
      </CardContent>
    </Card>
  );
}
