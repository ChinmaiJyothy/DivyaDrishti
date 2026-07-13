import { apiRequest } from "@/lib/api";
import type { Conversation, Message } from "@/types";

export interface CreateConversationInput {
  title?: string;
  domain?: string;
  birth_profile_id?: string;
}

export interface CreateMessageInput {
  role: string;
  content: string;
  ai_response_json?: unknown;
}

export async function getConversations(): Promise<Conversation[]> {
  return apiRequest<Conversation[]>("GET", "/conversations");
}

export async function getConversation(id: string): Promise<Conversation> {
  return apiRequest<Conversation>("GET", `/conversations/${id}`);
}

export async function createConversation(input: CreateConversationInput): Promise<Conversation> {
  return apiRequest<Conversation>("POST", "/conversations", input);
}

export async function addMessage(conversationId: string, input: CreateMessageInput): Promise<Message> {
  return apiRequest<Message>("POST", `/conversations/${conversationId}/messages`, input);
}

export async function archiveConversation(id: string): Promise<void> {
  return apiRequest<void>("POST", `/conversations/${id}/archive`);
}

export async function resumeConversation(id: string): Promise<void> {
  return apiRequest<void>("POST", `/conversations/${id}/resume`);
}

export async function deleteConversation(id: string): Promise<void> {
  return apiRequest<void>("DELETE", `/conversations/${id}`);
}

export async function exportConversation(id: string): Promise<Blob> {
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"}/conversations/${id}/export`, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem("access_token") || ""}`,
    },
  });
  if (!response.ok) {
    throw new Error("Export failed");
  }
  return response.blob();
}
