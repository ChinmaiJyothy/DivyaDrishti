"use client";

import { Plus } from "lucide-react";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { useCreateConversation } from "@/hooks/use-conversations";
import { useToast } from "@/hooks/use-toast";
import { cn } from "@/lib/utils";

interface NewChatButtonProps {
  className?: string;
}

export function NewChatButton({ className }: NewChatButtonProps) {
  const router = useRouter();
  const create = useCreateConversation();
  const { success, error: showError } = useToast();

  const handleClick = async () => {
    try {
      const conversation = await create.mutateAsync({
        title: "New conversation",
        domain: "general",
      });
      success("New conversation created");
      router.push(`/chat/${conversation.id}`);
    } catch {
      showError("Failed to create conversation");
    }
  };

  return (
    <Button
      className={cn("w-full", className)}
      onClick={handleClick}
      disabled={create.isPending}
      isLoading={create.isPending}
      aria-label="New chat"
    >
      <Plus className="mr-2 h-4 w-4" />
      New chat
    </Button>
  );
}
