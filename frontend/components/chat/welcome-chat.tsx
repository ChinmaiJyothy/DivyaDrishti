"use client";

import { motion } from "framer-motion";
import { Sparkles } from "lucide-react";

import { Button } from "@/components/ui/button";
import { SuggestedPrompts } from "@/components/chat/suggested-prompts";

interface WelcomeChatProps {
  onStart?: (question: string) => void;
}

const exampleQuestions = [
  "What does my birth chart say about my career path?",
  "When is the right time for marriage according to my chart?",
  "How will my health be in the next year?",
  "What does my chart reveal about my financial prospects?",
];

export function WelcomeChat({ onStart }: WelcomeChatProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4 }}
      className="flex h-full flex-col items-center justify-center px-4 text-center"
    >
      <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10">
        <Sparkles className="h-8 w-8 text-primary" aria-hidden="true" />
      </div>
      <h1 className="text-3xl font-bold tracking-tight">Welcome to DivyaDrishti</h1>
      <p className="mt-3 max-w-md text-muted-foreground">
        Ask me anything about your career, marriage, health, or finances. I will analyze your
        birth chart and provide astrological insights.
      </p>
      <div className="mt-8 w-full max-w-xl">
        <SuggestedPrompts
          questions={exampleQuestions}
          onSelect={onStart}
          className="justify-center"
        />
      </div>
      <div className="mt-8 grid w-full max-w-2xl gap-3 sm:grid-cols-2">
        {exampleQuestions.map((question, index) => (
          <motion.div
            key={question}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 + index * 0.08 }}
          >
            <Button
              variant="outline"
              className="h-auto w-full justify-start whitespace-normal px-4 py-3 text-left text-sm font-normal"
              onClick={() => onStart?.(question)}
              aria-label={`Start with: ${question}`}
            >
              {question}
            </Button>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
