"use client";

import { useEffect, useRef, useState } from "react";
import { Image as ImageIcon, Mic, Send, Square } from "lucide-react";

import { Button } from "@/components/ui/button";
import { SuggestedPrompts } from "@/components/chat/suggested-prompts";
import { Textarea } from "@/components/ui/textarea";
import { useChatContext } from "@/components/chat/chat-context";
import { cn } from "@/lib/utils";

const quickPrompts = [
  "Career guidance",
  "Marriage prospects",
  "Health outlook",
  "Financial future",
];

export function ChatInput() {
  const { sendMessage, isStreaming, stop } = useChatContext();
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [rows, setRows] = useState(1);

  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    const style = window.getComputedStyle(textarea);
    const lineHeight = parseFloat(style.lineHeight) || 20;
    const paddingTop = parseFloat(style.paddingTop) || 0;
    const paddingBottom = parseFloat(style.paddingBottom) || 0;
    const minHeight = lineHeight;
    const maxHeight = lineHeight * 6 + paddingTop + paddingBottom;

    textarea.style.height = "auto";
    const scrollHeight = textarea.scrollHeight;
    const clampedHeight = Math.min(Math.max(scrollHeight, minHeight), maxHeight);
    textarea.style.height = `${clampedHeight}px`;

    const calculatedRows = Math.min(6, Math.max(1, Math.round((clampedHeight - paddingTop - paddingBottom) / lineHeight)));
    setRows(calculatedRows);
  }, [value]);

  const handleSend = () => {
    const content = value.trim();
    if (!content || isStreaming) return;
    setValue("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
    void sendMessage(content);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    } else if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="space-y-3 border-t bg-background p-4">
      <div className="flex items-end gap-2 rounded-2xl border bg-card p-2 shadow-sm">
        <Button
          variant="ghost"
          size="icon"
          className="shrink-0 rounded-full"
          disabled
          aria-label="Upload image"
          title="Image upload coming soon"
        >
          <ImageIcon className="h-5 w-5 text-muted-foreground" />
        </Button>

        <Textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={rows}
          placeholder="Ask about career, marriage, health, finance..."
          className={cn(
            "min-h-[44px] resize-none border-0 bg-transparent px-2 py-2.5 shadow-none"
          )}
          aria-label="Message input"
          disabled={isStreaming}
        />

        <Button
          variant="ghost"
          size="icon"
          className="shrink-0 rounded-full"
          disabled
          aria-label="Voice input"
          title="Voice input coming soon"
        >
          <Mic className="h-5 w-5 text-muted-foreground" />
        </Button>

        {isStreaming ? (
          <Button
            variant="destructive"
            size="icon"
            className="shrink-0 rounded-full"
            onClick={stop}
            aria-label="Stop generating"
          >
            <Square className="h-4 w-4 fill-current" />
          </Button>
        ) : (
          <Button
            variant="default"
            size="icon"
            className="shrink-0 rounded-full"
            onClick={handleSend}
            disabled={!value.trim()}
            aria-label="Send message"
          >
            <Send className="h-5 w-5" />
          </Button>
        )}
      </div>

      <SuggestedPrompts
        questions={quickPrompts}
        onSelect={(question) => {
          setValue(question);
          textareaRef.current?.focus();
        }}
        className="justify-center"
      />
    </div>
  );
}
