"use client";

import { useState } from "react";
import { Archive, Check, Edit2, Pin, Trash2, X } from "lucide-react";
import { motion } from "framer-motion";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useUpdateConversation } from "@/hooks/use-conversations";
import { useToast } from "@/hooks/use-toast";
import { cn, formatDate } from "@/lib/utils";
import type { Conversation } from "@/types";

interface ConversationItemProps {
  conversation: Conversation;
  isActive?: boolean;
  onSelect?: (conversation: Conversation) => void;
  onArchive?: (conversation: Conversation) => void;
  onDelete?: (conversation: Conversation) => void;
  onPin?: (conversation: Conversation) => void;
  onRename?: (conversation: Conversation, title: string) => void;
}

export function ConversationItem({
  conversation,
  isActive = false,
  onSelect,
  onArchive,
  onDelete,
  onPin,
  onRename,
}: ConversationItemProps) {
  const update = useUpdateConversation(conversation.id);
  const { error: showError } = useToast();

  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(conversation.title || "Untitled conversation");

  const lastMessage = conversation.messages[conversation.messages.length - 1];
  const confidence = conversation.confidence ? Math.round(conversation.confidence * 100) : null;

  const handleSave = async () => {
    const trimmed = editTitle.trim();
    if (trimmed && trimmed !== (conversation.title || "Untitled conversation")) {
      try {
        await update.mutateAsync({ title: trimmed });
        onRename?.(conversation, trimmed);
      } catch {
        showError("Failed to rename conversation");
      }
    }
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditTitle(conversation.title || "Untitled conversation");
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleSave();
    } else if (e.key === "Escape") {
      handleCancel();
    }
  };

  const handleAction = (e: React.MouseEvent, callback: (conversation: Conversation) => void) => {
    e.stopPropagation();
    callback(conversation);
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 4 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -4 }}
      className={cn(
        "group relative flex flex-col gap-1 rounded-lg border p-3 transition-colors cursor-pointer",
        isActive ? "bg-accent/60 border-accent" : "bg-card hover:bg-accent/40 border-transparent"
      )}
      onClick={() => onSelect?.(conversation)}
      role="listitem"
      aria-current={isActive ? "true" : undefined}
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onSelect?.(conversation);
        }
      }}
    >
      <div className="flex items-start justify-between gap-2">
        {isEditing ? (
          <div className="flex flex-1 items-center gap-1">
            <Input
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
              onKeyDown={handleKeyDown}
              onBlur={handleSave}
              className="h-7 px-1 py-0 text-sm"
              autoFocus
              aria-label="Rename conversation"
              onClick={(e) => e.stopPropagation()}
            />
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7"
              onClick={handleSave}
              aria-label="Save title"
            >
              <Check className="h-3.5 w-3.5" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7"
              onClick={handleCancel}
              aria-label="Cancel rename"
            >
              <X className="h-3.5 w-3.5" />
            </Button>
          </div>
        ) : (
          <>
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-1.5">
                <h3 className="truncate text-sm font-medium">
                  {conversation.title || "Untitled conversation"}
                </h3>
                {conversation.is_pinned && (
                  <Pin className="h-3 w-3 shrink-0 fill-primary text-primary" aria-label="Pinned" />
                )}
              </div>
              {lastMessage && (
                <p className="mt-0.5 line-clamp-1 text-xs text-muted-foreground">
                  {lastMessage.content}
                </p>
              )}
              <div className="mt-1.5 flex flex-wrap items-center gap-1.5 text-xs text-muted-foreground">
                <span>{formatDate(conversation.updated_at || conversation.created_at)}</span>
                {conversation.domain && (
                  <Badge variant="secondary" className="text-[10px]">
                    {conversation.domain}
                  </Badge>
                )}
                {confidence !== null && (
                  <span className="text-[10px]">{confidence}% confidence</span>
                )}
              </div>
            </div>
            <div className="flex items-center gap-0.5 opacity-0 transition-opacity group-hover:opacity-100 group-focus-within:opacity-100">
              <Button
                variant="ghost"
                size="icon"
                className="h-7 w-7"
                onClick={(e) => handleAction(e, onPin)}
                aria-label={conversation.is_pinned ? "Unpin conversation" : "Pin conversation"}
                aria-pressed={conversation.is_pinned}
              >
                <Pin
                  className={cn(
                    "h-3.5 w-3.5",
                    conversation.is_pinned ? "fill-primary text-primary" : "text-muted-foreground"
                  )}
                />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="h-7 w-7"
                onClick={(e) => {
                  e.stopPropagation();
                  setIsEditing(true);
                }}
                aria-label="Rename conversation"
                disabled={!onRename}
              >
                <Edit2 className="h-3.5 w-3.5 text-muted-foreground" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="h-7 w-7"
                onClick={(e) => handleAction(e, onArchive)}
                aria-label="Archive conversation"
              >
                <Archive className="h-3.5 w-3.5 text-muted-foreground" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="h-7 w-7 text-destructive hover:text-destructive"
                onClick={(e) => handleAction(e, onDelete)}
                aria-label="Delete conversation"
              >
                <Trash2 className="h-3.5 w-3.5" />
              </Button>
            </div>
          </>
        )}
      </div>
    </motion.div>
  );
}
