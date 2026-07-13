"use client";

import { MessageActions } from "@/components/chat/message-actions";
import { MessageBubble } from "@/components/chat/message-bubble";
import type { Message } from "@/types";

interface StreamingMessageProps {
  content: string;
}

export function StreamingMessage({ content }: StreamingMessageProps) {
  const message: Message = {
    id: "streaming",
    role: "assistant",
    content,
    ai_response_json: null,
    reasoning_result: null,
    explainability_report: null,
    created_at: new Date().toISOString(),
  };

  return (
    <div className="group flex max-w-[80%] flex-col items-start gap-1">
      <div className="inline-flex items-end gap-1">
        <MessageBubble
          message={message}
          className="inline-block bg-primary/10 text-foreground border-primary/20"
        />
        <span className="animate-pulse text-primary" aria-hidden="true">
          ▋
        </span>
      </div>
      <MessageActions message={message} isStreaming />
    </div>
  );
}
