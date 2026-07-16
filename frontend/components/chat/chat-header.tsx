"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { Archive, Check, Edit2, PanelRight, Trash2, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { NewChatButton } from "@/components/chat/new-chat-button";
import { useChatContext } from "@/components/chat/chat-context";
import {
  useConversation,
  useUpdateConversation,
  useArchiveConversation,
  useDeleteConversation,
} from "@/hooks/use-conversations";
import { useToast } from "@/hooks/use-toast";

export function ChatHeader() {
  const router = useRouter();
  const { conversationId, setContextPanelOpen } = useChatContext();
  const { data: conversation } = useConversation(conversationId || "");
  const update = useUpdateConversation(conversationId || "");
  const archive = useArchiveConversation();
  const deleteConv = useDeleteConversation();
  const { success, error: showError } = useToast();

  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(conversation?.title || "");

  const title = conversation?.title || "New conversation";
  const domain = conversation?.domain;
  const confidence = conversation?.confidence ? Math.round(conversation.confidence * 100) : null;

  const handleSave = async () => {
    const trimmed = editTitle.trim();
    if (trimmed && trimmed !== title) {
      try {
        await update.mutateAsync({ title: trimmed });
        success("Conversation renamed");
      } catch {
        showError("Failed to rename conversation");
      }
    }
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditTitle(title);
    setIsEditing(false);
  };

  const handleArchive = async () => {
    if (!conversationId) return;
    try {
      await archive.mutateAsync(conversationId);
      success("Conversation archived");
      router.push("/conversations");
    } catch {
      showError("Failed to archive conversation");
    }
  };

  const handleDelete = async () => {
    if (!conversationId) return;
    try {
      await deleteConv.mutateAsync(conversationId);
      success("Conversation deleted");
      router.push("/conversations");
    } catch {
      showError("Failed to delete conversation");
    }
  };

  return (
    <header className="flex items-center justify-between border-b bg-card px-4 py-3 sm:px-6">
      <div className="flex min-w-0 items-center gap-3">
        <div className="min-w-0">
          {isEditing ? (
            <div className="flex items-center gap-2">
              <Input
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    void handleSave();
                  } else if (e.key === "Escape") {
                    handleCancel();
                  }
                }}
                onBlur={handleSave}
                className="h-8 w-48 sm:w-64"
                autoFocus
                aria-label="Edit conversation title"
              />
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8"
                onClick={() => void handleSave()}
                aria-label="Save title"
              >
                <Check className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8"
                onClick={handleCancel}
                aria-label="Cancel rename"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          ) : (
            <div className="group flex items-center gap-2">
              <h2 className="truncate text-base font-semibold sm:text-lg">{title}</h2>
              <Button
                variant="ghost"
                size="icon"
                className="h-7 w-7 opacity-0 transition-opacity group-hover:opacity-100 focus:opacity-100"
                onClick={() => {
                  setEditTitle(title);
                  setIsEditing(true);
                }}
                aria-label="Rename conversation"
              >
                <Edit2 className="h-3.5 w-3.5 text-muted-foreground" />
              </Button>
            </div>
          )}
          <div className="mt-0.5 flex items-center gap-2 text-xs text-muted-foreground">
            {domain && <Badge variant="secondary">{domain}</Badge>}
            {confidence !== null && <span>{confidence}% confidence</span>}
          </div>
        </div>
      </div>

      <div className="flex items-center gap-1">
        <Button
          variant="ghost"
          size="icon"
          className="hidden h-8 w-8 sm:flex"
          onClick={() => {
            setEditTitle(title);
            setIsEditing(true);
          }}
          aria-label="Rename conversation"
        >
          <Edit2 className="h-4 w-4" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="h-8 w-8"
          onClick={() => void handleArchive()}
          disabled={archive.isPending || !conversationId}
          aria-label="Archive conversation"
        >
          <Archive className="h-4 w-4" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="h-8 w-8 text-destructive hover:text-destructive"
          onClick={() => void handleDelete()}
          disabled={deleteConv.isPending || !conversationId}
          aria-label="Delete conversation"
        >
          <Trash2 className="h-4 w-4" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="h-8 w-8 lg:hidden"
          onClick={() => setContextPanelOpen(true)}
          aria-label="Open context panel"
        >
          <PanelRight className="h-4 w-4" />
        </Button>
        <NewChatButton className="hidden h-8 px-2 text-xs md:flex" />
      </div>
    </header>
  );
}
