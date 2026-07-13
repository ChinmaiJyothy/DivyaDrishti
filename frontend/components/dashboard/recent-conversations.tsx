"use client";

import { Archive, Eye, MessageSquare, Trash2 } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/ui/empty-state";
import { useConversations, useArchiveConversation, useDeleteConversation } from "@/hooks/use-conversations";
import { useToast } from "@/hooks/use-toast";
import type { Conversation } from "@/types";
import { useState } from "react";

function formatDate(dateString: string) {
  return new Date(dateString).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
  });
}

function ConversationPreview({
  conversation,
  open,
  onOpenChange,
}: {
  conversation: Conversation | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>{conversation?.title || "Conversation"}</DialogTitle>
          <DialogDescription>
            {conversation?.domain} • {conversation && formatDate(conversation.created_at)}
          </DialogDescription>
        </DialogHeader>
        <div className="max-h-80 space-y-3 overflow-y-auto py-4">
          {conversation?.messages && conversation.messages.length > 0 ? (
            conversation.messages.map((msg) => (
              <div
                key={msg.id}
                className={`rounded-lg p-3 text-sm ${
                  msg.role === "user" ? "bg-muted" : "bg-primary/10"
                }`}
              >
                <p className="text-xs font-semibold uppercase text-muted-foreground">{msg.role}</p>
                <p className="mt-1">{msg.content}</p>
              </div>
            ))
          ) : (
            <p className="text-sm text-muted-foreground">No messages yet.</p>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}

export function RecentConversations() {
  const { data: conversations, isLoading, error } = useConversations();
  const archive = useArchiveConversation();
  const deleteConv = useDeleteConversation();
  const toast = useToast();
  const [preview, setPreview] = useState<Conversation | null>(null);

  const handleArchive = async (id: string) => {
    await archive.mutateAsync(id);
    toast.success("Conversation archived");
  };

  const handleDelete = async (id: string) => {
    await deleteConv.mutateAsync(id);
    toast.success("Conversation deleted");
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-5 w-40" />
        </CardHeader>
        <CardContent className="space-y-3">
          <Skeleton className="h-16 w-full" />
          <Skeleton className="h-16 w-full" />
        </CardContent>
      </Card>
    );
  }

  if (error || !conversations || conversations.length === 0) {
    return (
      <Card>
        <CardContent className="py-6">
          <EmptyState
            icon={MessageSquare}
            title="No recent conversations"
            description="Start a new conversation from Quick Actions."
          />
        </CardContent>
      </Card>
    );
  }

  const recent = conversations.slice(0, 5);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Recent Conversations</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {recent.map((conversation) => (
          <div
            key={conversation.id}
            className="flex flex-col gap-2 rounded-lg border p-3 transition-colors hover:bg-muted/50 sm:flex-row sm:items-center sm:justify-between"
          >
            <div className="min-w-0">
              <p className="truncate font-medium">{conversation.title || "Untitled conversation"}</p>
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <span>{formatDate(conversation.created_at)}</span>
                {conversation.domain && <Badge variant="secondary">{conversation.domain}</Badge>}
                {conversation.confidence && (
                  <span>{Math.round(conversation.confidence * 100)}% confidence</span>
                )}
              </div>
            </div>
            <div className="flex items-center gap-1">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setPreview(conversation)}
                aria-label="Preview conversation"
              >
                <Eye className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => handleArchive(conversation.id)}
                disabled={archive.isPending}
                aria-label="Archive conversation"
              >
                <Archive className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => handleDelete(conversation.id)}
                disabled={deleteConv.isPending}
                aria-label="Delete conversation"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          </div>
        ))}
      </CardContent>
      <ConversationPreview
        conversation={preview}
        open={!!preview}
        onOpenChange={() => setPreview(null)}
      />
    </Card>
  );
}
