"use client";

import { Copy, Check, Edit2, RefreshCw, RotateCw, Trash2, Square, X } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { useChatContext } from "@/components/chat/chat-context";
import { useToast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";
import type { Message } from "@/types";

interface MessageActionsProps {
  message: Message;
  isStreaming?: boolean;
  onEdit?: (messageId: string, newContent: string) => void;
  onDelete?: (messageId: string) => void;
  onRetry?: () => void;
  onRegenerate?: () => void;
}

export function MessageActions({
  message,
  isStreaming: isStreamingProp,
  onEdit,
  onDelete,
  onRetry,
  onRegenerate,
}: MessageActionsProps) {
  const {
    stop,
    editMessage: editMessageContext,
    deleteMessage: deleteMessageContext,
    retry: retryContext,
    regenerate: regenerateContext,
  } = useChatContext();

  const isStreaming = isStreamingProp ?? false;
  const { success, error: showError } = useToast();
  const [copied, setCopied] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(message.content);

  const isUser = message.role === "user";

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
    success("Copied to clipboard");
  };

  const handleEdit = () => {
    const trimmed = editValue.trim();
    if (trimmed && trimmed !== message.content) {
      if (onEdit) {
        onEdit(message.id, trimmed);
      } else {
        editMessageContext?.(message.id, trimmed);
      }
    }
    setIsEditing(false);
  };

  const handleRetry = () => {
    if (onRetry) {
      onRetry();
    } else {
      retryContext?.();
    }
  };

  const handleRegenerate = () => {
    if (onRegenerate) {
      onRegenerate();
    } else {
      regenerateContext?.();
    }
  };

  const handleDelete = async () => {
    try {
      if (onDelete) {
        await onDelete(message.id);
      } else {
        await deleteMessageContext?.(message.id);
      }
      success("Message deleted");
    } catch {
      showError("Failed to delete message");
    }
  };

  if (isEditing) {
    return (
      <div className="flex w-full items-center gap-2">
        <input
          type="text"
          value={editValue}
          onChange={(e) => setEditValue(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") handleEdit();
            if (e.key === "Escape") {
              setEditValue(message.content);
              setIsEditing(false);
            }
          }}
          onBlur={handleEdit}
          className="flex-1 rounded border px-2 py-1 text-sm"
          autoFocus
        />
        <Button variant="ghost" size="icon" className="h-7 w-7" onClick={handleEdit}>
          <Check className="h-3.5 w-3.5" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="h-7 w-7"
          onClick={() => {
            setEditValue(message.content);
            setIsEditing(false);
          }}
        >
          <X className="h-3.5 w-3.5" />
        </Button>
      </div>
    );
  }

  return (
    <div
      className={cn(
        "flex items-center gap-1 opacity-0 transition-opacity group-hover:opacity-100 focus-within:opacity-100",
        isUser ? "justify-end" : "justify-start"
      )}
      onClick={(e) => e.stopPropagation()}
    >
      <Button
        variant="ghost"
        size="icon"
        className="h-7 w-7"
        onClick={handleCopy}
        aria-label="Copy message"
      >
        {copied ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
      </Button>

      {isUser ? (
        <>
          <Button
            variant="ghost"
            size="icon"
            className="h-7 w-7"
            onClick={() => setIsEditing(true)}
            disabled={isStreaming}
            aria-label="Edit message"
          >
            <Edit2 className="h-3.5 w-3.5" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="h-7 w-7 text-destructive hover:text-destructive"
            onClick={handleDelete}
            aria-label="Delete message"
          >
            <Trash2 className="h-3.5 w-3.5" />
          </Button>
        </>
      ) : (
        <>
          {isStreaming ? (
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7"
              onClick={stop}
              aria-label="Stop generating"
            >
              <Square className="h-3.5 w-3.5" />
            </Button>
          ) : (
            <>
              <Button
                variant="ghost"
                size="icon"
                className="h-7 w-7"
                onClick={handleRetry}
                aria-label="Retry response"
              >
                <RefreshCw className="h-3.5 w-3.5" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="h-7 w-7"
                onClick={handleRegenerate}
                aria-label="Regenerate response"
              >
                <RotateCw className="h-3.5 w-3.5" />
              </Button>
            </>
          )}
        </>
      )}
    </div>
  );
}
