"use client";

import { useEffect, useMemo, useRef } from "react";
import { Virtuoso, type VirtuosoHandle } from "react-virtuoso";

import { MessageItem } from "@/components/chat/message-item";
import { StreamingMessage } from "@/components/chat/streaming-message";
import { TypingIndicator } from "@/components/chat/typing-indicator";
import { useChatContext } from "@/components/chat/chat-context";
import type { Message } from "@/types";

export function MessageList() {
  const { messages, isStreaming, activeMessage, setActiveMessage } = useChatContext();
  const virtuosoRef = useRef<VirtuosoHandle>(null);

  const lastMessage = messages[messages.length - 1];
  const isStreamingMessage = isStreaming && lastMessage?.id === "streaming";
  const displayMessages = isStreamingMessage ? messages.slice(0, -1) : messages;
  const displayLastMessage = displayMessages[displayMessages.length - 1];

  const data = useMemo<Message[]>(
    () => (isStreamingMessage && lastMessage ? [...displayMessages, lastMessage] : displayMessages),
    [displayMessages, isStreamingMessage, lastMessage]
  );

  useEffect(() => {
    if (data.length > 0) {
      virtuosoRef.current?.scrollToIndex({ index: data.length - 1, behavior: "auto" });
    }
  }, [data.length, isStreaming]);

  const TypingFooter = () => {
    if (!isStreaming || isStreamingMessage || messages.length === 0 || lastMessage?.role !== "user") return null;
    return <TypingIndicator />;
  };

  return (
    <div
      className="flex-1 min-h-0"
      aria-label="Messages"
      role="log"
      aria-live="polite"
    >
      <Virtuoso
        ref={virtuosoRef}
        data={data}
        style={{ height: "100%" }}
        followOutput="smooth"
        components={{ Footer: TypingFooter }}
        itemContent={(_index, message) => {
          if (isStreaming && message.id === "streaming") {
            return <StreamingMessage content={message.content} />;
          }

          const isLastInDisplay = message.id === displayLastMessage?.id;
          const isStreamingItem =
            isStreaming &&
            isLastInDisplay &&
            displayLastMessage?.role === "user";

          return (
            <MessageItem
              message={message}
              isActive={message.id === activeMessage?.id}
              onSelect={setActiveMessage}
              isStreaming={isStreamingItem}
            />
          );
        }}
      />
    </div>
  );
}
