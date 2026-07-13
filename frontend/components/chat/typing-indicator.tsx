"use client";

import { motion } from "framer-motion";

export function TypingIndicator() {
  return (
    <div
      className="flex items-center gap-1 px-4 py-2 text-sm text-muted-foreground"
      aria-live="polite"
      aria-label="AI is typing"
    >
      <motion.span
        className="h-2 w-2 rounded-full bg-primary"
        animate={{ y: [0, -4, 0] }}
        transition={{ repeat: Infinity, duration: 0.6, ease: "easeInOut" }}
      />
      <motion.span
        className="h-2 w-2 rounded-full bg-primary"
        animate={{ y: [0, -4, 0] }}
        transition={{ repeat: Infinity, duration: 0.6, delay: 0.15, ease: "easeInOut" }}
      />
      <motion.span
        className="h-2 w-2 rounded-full bg-primary"
        animate={{ y: [0, -4, 0] }}
        transition={{ repeat: Infinity, duration: 0.6, delay: 0.3, ease: "easeInOut" }}
      />
      <span className="sr-only">AI is typing</span>
    </div>
  );
}
