// @vitest-environment node

import { describe, expect, it, vi } from "vitest";

import { streamChatMessage } from "./chat.service";

function createStream(chunks: string[]) {
  let index = 0;
  return new ReadableStream<Uint8Array>({
    pull(controller) {
      if (index < chunks.length) {
        controller.enqueue(new TextEncoder().encode(chunks[index]));
        index++;
      } else {
        controller.close();
      }
    },
  });
}

describe("streamChatMessage", () => {
  it("parses user, delta, metadata, and done events", async () => {
    const events: unknown[] = [];

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      body: createStream([
        `data: {"event": "user", "message_id": 1, "role": "user", "content": "Will I marry?"}\n\n`,
        `data: {"event": "delta", "content": "The chart "}\n\n`,
        `data: {"event": "delta", "content": "shows a positive sign."}\n\n`,
        `data: {"event": "metadata", "message_id": 2, "ai_response": {"direct_answer": "The chart shows a positive sign.", "interpretation": "The chart shows a positive sign.", "supporting_factors": [], "conflicting_factors": [], "overall_confidence": 75, "references": [], "follow_up_questions": ["Dasha analysis"], "language": "en"}, "reasoning_result": {"question": "Will I marry?", "domain": "marriage", "relevant_factors": {"houses": [], "planets": [], "signs": [], "nakshatras": [], "yogas": [], "doshas": [], "dashas": [], "topics": []}, "matched_rules": [], "partially_matched_rules": [], "unmatched_rules": [], "supporting_evidence": [], "conflicting_evidence": [], "overall_confidence": 75, "reasoning_summary": "", "reasoning_steps": [], "suggested_follow_up_topics": ["Dasha analysis"]}, "explainability_report": {"question": "Will I marry?", "detected_domain": "marriage", "chart_factors_used": {"lagna": "", "moon_sign": "", "sun_sign": "", "maha_dasha": "", "antar_dasha": "", "planets": {}, "navamsa": {}, "yogas": [], "doshas": []}, "rules_considered": [], "matched_rules": [], "ignored_rules": [], "supporting_evidence": [], "conflicting_evidence": [], "reasoning_path": {"root": {"id": "question", "label": "Question", "type": "question", "children": [], "metadata": {}}}, "confidence_score": {"overall_confidence": 75, "contributors": []}, "limitations": [], "classical_references": [], "suggested_reading": [], "important_notes": [], "visualizations": {"decision_tree": {}, "reasoning_timeline": [], "evidence_tree": {}, "planet_influence_graph": {}, "house_influence_graph": {}, "knowledge_source_graph": {}}}, "follow_up_questions": ["Dasha analysis"], "confidence": 75}\n\n`,
        `data: {"event": "done"}\n\n`,
      ]),
    }) as unknown as typeof fetch;

    await streamChatMessage({
      conversationId: "1",
      content: "Will I marry?",
      onEvent: (event) => events.push(event),
      onDone: () => events.push({ event: "finished" }),
    });

    expect(events).toHaveLength(6);
    expect(events[0]).toMatchObject({ event: "user", message_id: "1" });
    expect(events[1]).toMatchObject({ event: "delta", content: "The chart " });
    expect(events[2]).toMatchObject({ event: "delta", content: "shows a positive sign." });
    expect(events[3]).toMatchObject({ event: "metadata", message_id: "2" });
    expect(events[4]).toMatchObject({ event: "done" });
    expect(events[5]).toMatchObject({ event: "finished" });
  });

  it("throws ChatStreamError on non-ok response", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
      json: async () => ({ detail: "Internal error" }),
    }) as unknown as typeof fetch;

    await expect(
      streamChatMessage({
        conversationId: "1",
        content: "Hi",
        onEvent: () => {},
      })
    ).rejects.toThrow("Internal error");
  });

  it("respects abort signal", async () => {
    const controller = new AbortController();
    const events: unknown[] = [];

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      body: createStream([`data: {"event": "delta", "content": "A"}\n\n`]),
    }) as unknown as typeof fetch;

    controller.abort();

    await expect(
      streamChatMessage({
        conversationId: "1",
        content: "Hi",
        onEvent: (event) => events.push(event),
        signal: controller.signal,
      })
    ).rejects.toThrow();
  });
});
