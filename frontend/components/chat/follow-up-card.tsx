"use client";

import { motion } from "framer-motion";
import { Lightbulb } from "lucide-react";

import { Button } from "@/components/ui/button";
import { useChatContext } from "@/components/chat/chat-context";
import { cn } from "@/lib/utils";

interface FollowUpCardProps {
  questions: string[];
  onSelect?: (question: string) => void | Promise<void>;
  className?: string;
}

export function FollowUpCard({ questions, onSelect, className }: FollowUpCardProps) {
  const { sendMessage } = useChatContext();

  if (questions.length === 0) return null;

  const handleSelect = (question: string) => {
    if (onSelect) {
      onSelect(question);
    } else {
      sendMessage(question);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn("flex flex-wrap items-center gap-2", className)}
      role="list"
      aria-label="Suggested follow-up questions"
    >
      <Lightbulb className="h-4 w-4 text-muted-foreground" aria-hidden="true" />
      {questions.map((question, index) => (
        <motion.div
          key={`${question}-${index}`}
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: index * 0.05 }}
        >
          <Button
            variant="outline"
            size="sm"
            className="h-auto whitespace-normal rounded-full px-3 py-1.5 text-xs font-normal"
            onClick={() => handleSelect(question)}
            aria-label={`Follow up with: ${question}`}
          >
            {question}
          </Button>
        </motion.div>
      ))}
    </motion.div>
  );
}