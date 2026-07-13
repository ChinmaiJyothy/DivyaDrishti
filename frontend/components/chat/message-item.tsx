"use client";

import { motion } from "framer-motion";

import { ExplainabilityPanel } from "@/components/chat/explainability-panel";
import { MessageActions } from "@/components/chat/message-actions";
import { MessageBubble } from "@/components/chat/message-bubble";
import { useChatContext } from "@/components/chat/chat-context";
import { cn } from "@/lib/utils";
import type { Message } from "@/types";

interface MessageItemProps {
  message: Message;
  isActive?: boolean;
  onSelect?: (message: Message) => void;
  isStreaming?: boolean;
  onEdit?: (messageId: string, newContent: string) => void;
  onDelete?: (messageId: string) => void;
  onRetry?: () => void;
  onRegenerate?: () => void;
}

export function MessageItem({
  message,
  isActive,
  onSelect,
  isStreaming,
  onEdit,
  onDelete,
  onRetry,
  onRegenerate,
}: MessageItemProps) {
  const { setActiveMessage } = useChatContext();
  const isUser = message.role === "user";

  const handleClick = () => {
    if (!isUser) {
      setActiveMessage(message);
      onSelect?.(message);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isUser && (e.key === "Enter" || e.key === " ")) {
      e.preventDefault();
      handleClick();
    }
  };

  return (
    <div
      className={cn("group flex flex-col", isUser ? "items-end" : "items-start")}
      role="listitem"
      aria-label={isUser ? "User message" : "Assistant message"}
    >
      <div className={cn("flex max-w-[85%] flex-col gap-1", isUser ? "items-end" : "items-start")}>
        <MessageBubble
          message={message}
          onClick={!isUser ? handleClick : undefined}
          onKeyDown={!isUser ? handleKeyDown : undefined}
          role={!isUser ? "button" : undefined}
          tabIndex={!isUser ? 0 : undefined}
        />
        <MessageActions
          message={message}
          isStreaming={isStreaming}
          onEdit={onEdit}
          onDelete={onDelete}
          onRetry={onRetry}
          onRegenerate={onRegenerate}
        />
        {!isUser && message.explainability_report && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            className="w-full"
          >
            <ExplainabilityPanel
              message={message}
              isActive={isActive}
              onValueChange={() => onSelect?.(message)}
            />
          </motion.div>
        )}
      </div>
    </div>
  );
}
