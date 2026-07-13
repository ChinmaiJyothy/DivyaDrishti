import { API_BASE_URL } from "@/lib/api";
import type { SSEEvent } from "@/types";

export interface StreamChatOptions {
  conversationId: string;
  content: string;
  language?: string;
  messageId?: string;
  onEvent: (event: SSEEvent) => void;
  onError?: (error: Error) => void;
  onDone?: () => void;
  signal?: AbortSignal;
}

export async function streamChatMessage(options: StreamChatOptions): Promise<void> {
  const { conversationId, content, language = "en", messageId, onEvent, onError, onDone, signal } = options;

  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;

  const response = await fetch(`${API_BASE_URL}/chat/${conversationId}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ content, language, message_id: messageId }),
    signal,
  });

  if (!response.ok) {
    const data = await parseError(response);
    throw new ChatStreamError(
      (data as { detail?: string }).detail || response.statusText,
      response.status,
      data
    );
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new ChatStreamError("ReadableStream not supported", 0, null);
  }

  const decoder = new TextDecoder();
  let buffer = "";

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() ?? "";

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed) continue;

        if (trimmed.startsWith("data: ")) {
          try {
            const event = JSON.parse(trimmed.slice(6)) as SSEEvent;
            if (event.event === "user" || event.event === "metadata") {
              event.message_id = String(event.message_id);
            }
            onEvent(event);
          } catch (err) {
            onError?.(new Error(`Failed to parse SSE event: ${trimmed}`));
          }
        }
      }
    }

    onDone?.();
  } catch (err) {
    if (err instanceof Error) {
      if (err.name === "AbortError") {
        onDone?.();
        return;
      }
      onError?.(err);
      throw err;
    }
    throw err;
  }
}

export class ChatStreamError extends Error {
  status: number;
  data: unknown;

  constructor(message: string, status: number, data: unknown) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

async function parseError(response: Response): Promise<unknown> {
  try {
    return await response.json();
  } catch {
    return { detail: response.statusText };
  }
}
