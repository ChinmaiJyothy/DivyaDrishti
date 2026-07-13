import { apiRequest } from "@/lib/api";
import type { Feedback } from "@/types";

export interface CreateFeedbackInput {
  rating: string;
  comment?: string;
}

export async function createFeedback(input: CreateFeedbackInput): Promise<Feedback> {
  return apiRequest<Feedback>("POST", "/feedback", input);
}
