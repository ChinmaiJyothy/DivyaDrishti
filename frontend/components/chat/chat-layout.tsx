"use client";

import { useState } from "react";

import { ChatContextPanel } from "@/components/chat/chat-context-panel";
import { ChatContextProvider, useChatContext } from "@/components/chat/chat-context";
import { ConversationSidebar } from "@/components/chat/conversation-sidebar";
import { Navbar } from "@/components/layout/navbar";

function ChatLayoutInner({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { setContextPanelOpen } = useChatContext();

  return (
    <div className="flex h-screen flex-col bg-background">
      <Navbar
        onMenuClick={() => setSidebarOpen(true)}
        onContextToggle={() => setContextPanelOpen(true)}
      />
      <div className="flex flex-1 overflow-hidden">
        <ConversationSidebar isOpen={sidebarOpen} onOpenChange={setSidebarOpen} />
        <main className="flex flex-1 flex-col overflow-hidden">
          {children}
        </main>
        <ChatContextPanel />
      </div>
    </div>
  );
}

export function ChatLayout({ children }: { children: React.ReactNode }) {
  return (
    <ChatContextProvider>
      <ChatLayoutInner>{children}</ChatLayoutInner>
    </ChatContextProvider>
  );
}
