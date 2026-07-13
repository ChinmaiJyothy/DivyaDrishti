"use client";

import { useRouter } from "next/navigation";

import { NewChatButton } from "@/components/chat/new-chat-button";
import { WelcomeChat } from "@/components/chat/welcome-chat";

export default function ChatPage() {
  const router = useRouter();

  return (
    <div className="flex h-full flex-col items-center justify-center p-6">
      <WelcomeChat onStart={(question) => router.push(`/ask?question=${encodeURIComponent(question)}`)} />
      <NewChatButton className="mt-6" />
    </div>
  );
}
