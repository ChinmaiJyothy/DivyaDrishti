import { API_BASE_URL } from "@/lib/api";
import { apiRequest } from "@/lib/api";
import type { Conversation, Message } from "@/types";

export interface CreateConversationInput {
  title?: string;
  domain?: string;
  birth_profile_id?: string;
}

export interface UpdateConversationInput {
  title?: string;
  birth_profile_id?: string;
  is_archived?: boolean;
  is_pinned?: boolean;
}

export interface CreateMessageInput {
  role: string;
  content: string;
  ai_response_json?: unknown;
}

export interface SearchConversationsInput {
  q?: string;
}

export async function getConversations(q?: string): Promise<Conversation[]> {
  const query = q ? `?q=${encodeURIComponent(q)}` : "";
  return apiRequest<Conversation[]>("GET", `/conversations${query}`);
}

export async function getConversation(id: string): Promise<Conversation> {
  return apiRequest<Conversation>("GET", `/conversations/${id}`);
}

export async function createConversation(input: CreateConversationInput): Promise<Conversation> {
  return apiRequest<Conversation>("POST", "/conversations", input);
}

export async function updateConversation(id: string, input: UpdateConversationInput): Promise<Conversation> {
  return apiRequest<Conversation>("PATCH", `/conversations/${id}`, input);
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

export async function pinConversation(id: string): Promise<void> {
  return apiRequest<void>("POST", `/conversations/${id}/pin`);
}

export async function unpinConversation(id: string): Promise<void> {
  return apiRequest<void>("POST", `/conversations/${id}/unpin`);
}

export async function deleteConversation(id: string): Promise<void> {
  return apiRequest<void>("DELETE", `/conversations/${id}`);
}

export async function deleteMessage(conversationId: string, messageId: string): Promise<void> {
  return apiRequest<void>("DELETE", `/conversations/${conversationId}/messages/${messageId}`);
}

export async function exportConversation(id: string): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}/conversations/${id}/export`, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem("access_token") || ""}`,
    },
  });
  if (!response.ok) {
    throw new Error("Export failed");
  }
  return response.blob();
}
