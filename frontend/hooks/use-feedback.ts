"use client";

import { useMutation } from "@tanstack/react-query";

import { createFeedback, type CreateFeedbackInput } from "@/services/feedback.service";
import type { Feedback } from "@/types";

export function useCreateFeedback() {
  return useMutation<Feedback, Error, CreateFeedbackInput>({
    mutationFn: createFeedback,
  });
}
