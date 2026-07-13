"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  addMessage,
  archiveConversation,
  createConversation,
  deleteConversation,
  getConversation,
  getConversations,
  resumeConversation,
  type CreateConversationInput,
  type CreateMessageInput,
} from "@/services/conversation.service";
import type { Conversation, Message } from "@/types";

const QUERY_KEY = ["conversations"];

export function useConversations() {
  return useQuery<Conversation[]>({
    queryKey: QUERY_KEY,
    queryFn: getConversations,
    retry: 1,
  });
}

export function useConversation(id: string) {
  return useQuery<Conversation>({
    queryKey: [...QUERY_KEY, id],
    queryFn: () => getConversation(id),
    enabled: !!id,
    retry: 1,
  });
}

export function useCreateConversation() {
  const queryClient = useQueryClient();

  return useMutation<Conversation, Error, CreateConversationInput>({
    mutationFn: createConversation,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
    },
  });
}

export function useAddMessage(conversationId: string) {
  const queryClient = useQueryClient();

  return useMutation<Message, Error, CreateMessageInput>({
    mutationFn: (input) => addMessage(conversationId, input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [...QUERY_KEY, conversationId] });
    },
  });
}

export function useArchiveConversation() {
  const queryClient = useQueryClient();

  return useMutation<void, Error, string>({
    mutationFn: archiveConversation,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
    },
  });
}

export function useResumeConversation() {
  const queryClient = useQueryClient();

  return useMutation<void, Error, string>({
    mutationFn: resumeConversation,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
    },
  });
}

export function useDeleteConversation() {
  const queryClient = useQueryClient();

  return useMutation<void, Error, string>({
    mutationFn: deleteConversation,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
    },
  });
}
