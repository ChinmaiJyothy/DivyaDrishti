"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";

import { useConversation } from "@/hooks/use-conversations";
import { deleteMessage as apiDeleteMessage } from "@/services/conversation.service";
import { streamChatMessage } from "@/services/chat.service";
import type { Message, SSEEvent } from "@/types";

function buildMessageId(id: string | number): string {
  return String(id);
}

function createUserMessage(id: string, content: string): Message {
  return {
    id,
    role: "user",
    content,
    ai_response_json: null,
    reasoning_result: null,
    explainability_report: null,
    created_at: new Date().toISOString(),
  };
}

function createAssistantMessage(id: string, content: string): Message {
  return {
    id,
    role: "assistant",
    content,
    ai_response_json: null,
    reasoning_result: null,
    explainability_report: null,
    created_at: new Date().toISOString(),
  };
}

export function useChat(conversationId: string | undefined) {
  const { data: conversation, isLoading } = useConversation(conversationId || "");
  const queryClient = useQueryClient();
  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const streamingAssistantRef = useRef<Message | null>(null);

  useEffect(() => {
    if (conversation?.messages && !isStreaming) {
      setMessages(conversation.messages);
    }
  }, [conversation?.messages]);

  const stop = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsStreaming(false);
  }, []);

  const handleEvent = useCallback(
    (event: SSEEvent) => {
      if (event.event === "user") {
        setMessages((prev) => [...prev, createUserMessage(buildMessageId(event.message_id), event.content)]);
        return;
      }

      if (event.event === "delta") {
        if (!streamingAssistantRef.current) {
          streamingAssistantRef.current = createAssistantMessage("streaming", "");
          setMessages((prev) => [...prev, streamingAssistantRef.current!]);
        }
        streamingAssistantRef.current.content += event.content;
        setMessages((prev) => {
          const index = prev.findIndex((m) => m.id === streamingAssistantRef.current!.id);
          if (index === -1) return prev;
          const next = [...prev];
          next[index] = { ...streamingAssistantRef.current! };
          return next;
        });
        return;
      }

      if (event.event === "metadata") {
        const assistantMessage: Message = createAssistantMessage(
          buildMessageId(event.message_id),
          streamingAssistantRef.current?.content || event.ai_response.direct_answer
        );
        assistantMessage.ai_response_json = event.ai_response;
        assistantMessage.reasoning_result = event.reasoning_result;
        assistantMessage.explainability_report = event.explainability_report;

        setMessages((prev) => {
          const index = prev.findIndex((m) => m.id === streamingAssistantRef.current?.id);
          if (index === -1) {
            return [...prev, assistantMessage];
          }
          const next = [...prev];
          next[index] = assistantMessage;
          return next;
        });

        streamingAssistantRef.current = null;
        return;
      }

      if (event.event === "error") {
        setError(new Error(event.detail));
        setIsStreaming(false);
      }
    },
    []
  );

  const invalidateConversation = useCallback(() => {
    if (conversationId) {
      queryClient.invalidateQueries({ queryKey: ["conversations", conversationId] });
      queryClient.invalidateQueries({ queryKey: ["conversations"] });
    }
  }, [conversationId, queryClient]);

  const sendMessage = useCallback(
    async (content: string, messageId?: string) => {
      if (!conversationId || !content.trim()) return;

      setError(null);
      setIsStreaming(true);

      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      streamingAssistantRef.current = null;
      setMessages((prev) =>
        prev.filter((m) => m.id !== "streaming" && m.id !== messageId)
      );

      const controller = new AbortController();
      abortControllerRef.current = controller;

      try {
        await streamChatMessage({
          conversationId,
          content,
          messageId,
          onEvent: handleEvent,
          onError: (err) => {
            setError(err);
            setIsStreaming(false);
            invalidateConversation();
          },
          onDone: () => {
            setIsStreaming(false);
            abortControllerRef.current = null;
            invalidateConversation();
          },
          signal: controller.signal,
        });
      } catch (err) {
        if (err instanceof Error && err.name === "AbortError") {
          setIsStreaming(false);
          return;
        }
        setError(err instanceof Error ? err : new Error(String(err)));
        setIsStreaming(false);
        invalidateConversation();
      }
    },
    [conversationId, handleEvent, invalidateConversation]
  );

  const retry = useCallback(() => {
    const lastUserIndex = messages.findLastIndex((m) => m.role === "user");
    if (lastUserIndex !== -1) {
      const userMessage = messages[lastUserIndex];
      setMessages((prev) => prev.slice(0, lastUserIndex));
      sendMessage(userMessage.content, userMessage.id);
    }
  }, [messages, sendMessage]);

  const regenerate = useCallback(() => {
    const lastUser = messages.findLast((m) => m.role === "user");
    if (lastUser) {
      setMessages((prev) => {
        const lastAssistantIndex = prev.findLastIndex((m) => m.role === "assistant");
        if (lastAssistantIndex === -1) return prev;
        return prev.slice(0, lastAssistantIndex);
      });
      sendMessage(lastUser.content, lastUser.id);
    }
  }, [messages, sendMessage]);

  const editMessage = useCallback(
    (messageId: string, newContent: string) => {
      setMessages((prev) => {
        const index = prev.findIndex((m) => m.id === messageId);
        if (index === -1) return prev;
        return prev.slice(0, index);
      });
      sendMessage(newContent, messageId);
    },
    [sendMessage]
  );

  const deleteMessage = useCallback(
    async (messageId: string) => {
      if (conversationId) {
        await apiDeleteMessage(conversationId, messageId);
      }
      setMessages((prev) => {
        const index = prev.findIndex((m) => m.id === messageId);
        if (index === -1) return prev;
        return prev.slice(0, index);
      });
      invalidateConversation();
    },
    [conversationId, invalidateConversation]
  );

  return {
    messages,
    isStreaming,
    isLoading,
    error,
    sendMessage,
    stop,
    retry,
    regenerate,
    editMessage,
    deleteMessage,
  };
}
