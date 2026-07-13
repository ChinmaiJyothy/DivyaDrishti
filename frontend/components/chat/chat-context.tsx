"use client";

import { useParams } from "next/navigation";
import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

import { useChat } from "@/hooks/use-chat";
import type { Message } from "@/types";

interface ChatContextValue {
  conversationId: string | undefined;
  messages: Message[];
  isStreaming: boolean;
  isLoading: boolean;
  error: Error | null;
  sendMessage: (content: string) => Promise<void>;
  stop: () => void;
  retry: () => void;
  regenerate: () => void;
  editMessage: (messageId: string, newContent: string) => void;
  deleteMessage: (messageId: string) => void;
  followUpQuestions: string[];
  activeMessage: Message | null;
  setActiveMessage: (message: Message | null) => void;
  isContextPanelOpen: boolean;
  setContextPanelOpen: (open: boolean) => void;
}

const ChatContext = createContext<ChatContextValue | null>(null);

export function ChatContextProvider({ children }: { children: React.ReactNode }) {
  const params = useParams<{ id?: string }>();
  const conversationId = params?.id;

  const {
    messages,
    isStreaming,
    isLoading,
    error,
    sendMessage: send,
    stop,
    retry,
    regenerate,
    editMessage,
    deleteMessage,
  } = useChat(conversationId);

  const [activeMessage, setActiveMessageState] = useState<Message | null>(null);
  const [isContextPanelOpen, setContextPanelOpen] = useState(true);

  const setActiveMessage = useCallback((message: Message | null) => {
    setActiveMessageState(message);
  }, []);

  useEffect(() => {
    const lastAssistant = messages.findLast((m) => m.role === "assistant" && m.ai_response_json);
    if (lastAssistant) {
      setActiveMessageState(lastAssistant);
    }
  }, [messages]);

  const followUpQuestions = useMemo(() => {
    const lastAssistant = messages.findLast((m) => m.role === "assistant");
    return lastAssistant?.ai_response_json?.follow_up_questions ?? [];
  }, [messages]);

  const value = useMemo<ChatContextValue>(
    () => ({
      conversationId,
      messages,
      isStreaming,
      isLoading,
      error,
      sendMessage: send,
      stop,
      retry,
      regenerate,
      editMessage,
      deleteMessage,
      followUpQuestions,
      activeMessage,
      setActiveMessage,
      isContextPanelOpen,
      setContextPanelOpen,
    }),
    [
      conversationId,
      messages,
      isStreaming,
      isLoading,
      error,
      send,
      stop,
      retry,
      regenerate,
      editMessage,
      deleteMessage,
      followUpQuestions,
      activeMessage,
      setActiveMessage,
      isContextPanelOpen,
      setContextPanelOpen,
    ]
  );

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
}

export function useChatContext() {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error("useChatContext must be used within ChatContextProvider");
  }
  return context;
}
