"use client";

import { useMemo, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { MessageSquare, Search } from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";

import { Drawer, DrawerContent, DrawerHeader, DrawerTitle } from "@/components/ui/drawer";
import { EmptyState } from "@/components/ui/empty-state";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { ConversationItem } from "@/components/chat/conversation-item";
import { NewChatButton } from "@/components/chat/new-chat-button";
import { useMediaQuery } from "@/hooks/use-media-query";
import {
  useConversations,
  useArchiveConversation,
  useDeleteConversation,
  usePinConversation,
  useUnpinConversation,
} from "@/hooks/use-conversations";
import { useToast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";
import type { Conversation } from "@/types";

interface ConversationSidebarProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  className?: string;
}

const GROUP_ORDER = ["Today", "Yesterday", "Previous 7 Days", "Older"];

function getDateGroup(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  now.setHours(0, 0, 0, 0);
  const then = new Date(date);
  then.setHours(0, 0, 0, 0);
  const diff = now.getTime() - then.getTime();
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));

  if (days === 0) return "Today";
  if (days === 1) return "Yesterday";
  if (days >= 2 && days <= 7) return "Previous 7 Days";
  return "Older";
}

function groupConversations(conversations: Conversation[]) {
  const pinned = conversations.filter((c) => c.is_pinned);
  const unpinned = conversations.filter((c) => !c.is_pinned);

  const groups: Record<string, Conversation[]> = {};
  for (const group of GROUP_ORDER) {
    groups[group] = [];
  }

  for (const conversation of unpinned) {
    const group = getDateGroup(conversation.updated_at || conversation.created_at);
    groups[group] = groups[group] || [];
    groups[group].push(conversation);
  }

  return { pinned, groups };
}

function SidebarContent({
  conversations,
  isLoading,
  activeId,
  onSelect,
  className,
}: {
  conversations: Conversation[];
  isLoading: boolean;
  activeId?: string;
  onSelect: (conversation: Conversation) => void;
  className?: string;
}) {
  const { success, error: showError } = useToast();
  const archive = useArchiveConversation();
  const deleteConv = useDeleteConversation();
  const pin = usePinConversation();
  const unpin = useUnpinConversation();

  const handleArchive = async (conversation: Conversation) => {
    try {
      await archive.mutateAsync(conversation.id);
      success("Conversation archived");
    } catch {
      showError("Failed to archive conversation");
    }
  };

  const handleDelete = async (conversation: Conversation) => {
    try {
      await deleteConv.mutateAsync(conversation.id);
      success("Conversation deleted");
    } catch {
      showError("Failed to delete conversation");
    }
  };

  const handlePin = async (conversation: Conversation) => {
    try {
      if (conversation.is_pinned) {
        await unpin.mutateAsync(conversation.id);
        success("Conversation unpinned");
      } else {
        await pin.mutateAsync(conversation.id);
        success("Conversation pinned");
      }
    } catch {
      showError("Failed to update pin status");
    }
  };

  const handleRename = (_conversation: Conversation, title: string) => {
    success(`Conversation renamed to "${title}"`);
  };

  if (isLoading) {
    return (
      <div className={cn("space-y-3 p-4", className)}>
        <Skeleton className="h-8 w-full" />
        <Skeleton className="h-20 w-full" />
        <Skeleton className="h-20 w-full" />
        <Skeleton className="h-20 w-full" />
      </div>
    );
  }

  if (!conversations || conversations.length === 0) {
    return (
      <div className={cn("p-4", className)}>
        <EmptyState
          icon={MessageSquare}
          title="No conversations"
          description="Start a new chat to begin your astrological journey."
          action={<NewChatButton className="mt-4" />}
        />
      </div>
    );
  }

  const { pinned, groups } = groupConversations(conversations);

  return (
    <div className={cn("space-y-4 p-4", className)}>
      <AnimatePresence>
        {pinned.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
          >
            <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Pinned
            </h3>
            <div className="space-y-2">
              {pinned.map((conversation) => (
                <ConversationItem
                  key={conversation.id}
                  conversation={conversation}
                  isActive={conversation.id === activeId}
                  onSelect={onSelect}
                  onArchive={handleArchive}
                  onDelete={handleDelete}
                  onPin={handlePin}
                  onRename={handleRename}
                />
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {GROUP_ORDER.map((group) => {
        const items = groups[group];
        if (!items || items.length === 0) return null;
        return (
          <div key={group}>
            <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              {group}
            </h3>
            <div className="space-y-2">
              {items.map((conversation) => (
                <ConversationItem
                  key={conversation.id}
                  conversation={conversation}
                  isActive={conversation.id === activeId}
                  onSelect={onSelect}
                  onArchive={handleArchive}
                  onDelete={handleDelete}
                  onPin={handlePin}
                  onRename={handleRename}
                />
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}

export function ConversationSidebar({ isOpen, onOpenChange, className }: ConversationSidebarProps) {
  const router = useRouter();
  const params = useParams<{ id?: string }>();
  const activeId = params?.id;
  const isDesktop = useMediaQuery("(min-width: 1024px)");

  const { data: conversations, isLoading } = useConversations();
  const [search, setSearch] = useState("");

  const filtered = useMemo(() => {
    if (!conversations) return [];
    if (!search.trim()) return conversations;
    const q = search.toLowerCase();
    return conversations.filter((conversation) => {
      const title = (conversation.title || "Untitled conversation").toLowerCase();
      const last = conversation.messages[conversation.messages.length - 1]?.content?.toLowerCase() || "";
      return title.includes(q) || last.includes(q);
    });
  }, [conversations, search]);

  const handleSelect = (conversation: Conversation) => {
    router.push(`/chat/${conversation.id}`);
    onOpenChange(false);
  };

  const handleOpenChange = (open: boolean) => {
    onOpenChange(open);
  };

  if (isDesktop) {
    return (
      <aside
        className={cn(
          "hidden h-full w-72 flex-col overflow-y-auto border-r bg-card lg:flex",
          className
        )}
        aria-label="Conversation sidebar"
      >
        <div className="sticky top-0 z-10 space-y-3 border-b bg-card p-4">
          <NewChatButton />
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search conversations"
              className="pl-9"
              aria-label="Search conversations"
            />
          </div>
        </div>
        <SidebarContent
          conversations={filtered}
          isLoading={isLoading}
          activeId={activeId}
          onSelect={handleSelect}
          className="flex-1"
        />
      </aside>
    );
  }

  return (
    <Drawer open={isOpen} onOpenChange={handleOpenChange} direction="left">
      <DrawerContent
        className={cn(
          "inset-y-0 left-0 right-auto mt-0 h-full w-72 rounded-none border-r bg-card p-0 [&>div:first-child]:hidden",
          className
        )}
      >
        <DrawerHeader className="sr-only">
          <DrawerTitle>Conversations</DrawerTitle>
        </DrawerHeader>
        <div className="flex h-full flex-col">
          <div className="space-y-3 border-b bg-card p-4">
            <NewChatButton />
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search conversations"
                className="pl-9"
                aria-label="Search conversations"
              />
            </div>
          </div>
          <div className="flex-1 overflow-y-auto">
            <SidebarContent
              conversations={filtered}
              isLoading={isLoading}
              activeId={activeId}
              onSelect={handleSelect}
            />
          </div>
        </div>
      </DrawerContent>
    </Drawer>
  );
}
