"use client";

import { useSearchParams } from "next/navigation";
import { useEffect, useRef } from "react";

import { ChatHeader } from "@/components/chat/chat-header";
import { ChatInput } from "@/components/chat/chat-input";
import { MessageList } from "@/components/chat/message-list";
import { SuggestedPrompts } from "@/components/chat/suggested-prompts";
import { WelcomeChat } from "@/components/chat/welcome-chat";
import { useChatContext } from "@/components/chat/chat-context";

export function ChatWorkspace() {
  const { messages, isStreaming, isLoading, sendMessage, followUpQuestions } = useChatContext();
  const searchParams = useSearchParams();
  const initialQuestion = searchParams.get("question") ?? "";
  const sentRef = useRef<string | null>(null);

  useEffect(() => {
    if (
      initialQuestion &&
      !isLoading &&
      messages.length === 0 &&
      !isStreaming &&
      sentRef.current !== initialQuestion
    ) {
      sentRef.current = initialQuestion;
      void sendMessage(initialQuestion);
    }
  }, [initialQuestion, isLoading, messages.length, isStreaming, sendMessage]);

  return (
    <div className="flex h-full flex-col">
      {messages.length === 0 && !isStreaming ? (
        <WelcomeChat onStart={sendMessage} />
      ) : (
        <>
          <ChatHeader />
          <MessageList />
          <div className="px-4 pt-2">
            <SuggestedPrompts questions={followUpQuestions} onSelect={sendMessage} />
          </div>
        </>
      )}
      <ChatInput />
    </div>
  );
}
