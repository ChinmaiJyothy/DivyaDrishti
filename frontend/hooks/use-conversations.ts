"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  archiveConversation,
  createConversation,
  deleteConversation,
  deleteMessage,
  getConversation,
  getConversations,
  pinConversation,
  resumeConversation,
  unpinConversation,
  updateConversation,
  type CreateConversationInput,
  type UpdateConversationInput,
} from "@/services/conversation.service";
import type { Conversation } from "@/types";

const QUERY_KEY = ["conversations"];

export function useConversations(q?: string) {
  return useQuery<Conversation[]>({
    queryKey: [...QUERY_KEY, q ?? ""],
    queryFn: () => getConversations(q),
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

export function useUpdateConversation(id: string) {
  const queryClient = useQueryClient();

  return useMutation<Conversation, Error, UpdateConversationInput>({
    mutationFn: (input) => updateConversation(id, input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: [...QUERY_KEY, id] });
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

export function usePinConversation() {
  const queryClient = useQueryClient();

  return useMutation<void, Error, string>({
    mutationFn: pinConversation,
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: [...QUERY_KEY, id] });
    },
  });
}

export function useUnpinConversation() {
  const queryClient = useQueryClient();

  return useMutation<void, Error, string>({
    mutationFn: unpinConversation,
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: [...QUERY_KEY, id] });
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

export function useDeleteMessage(conversationId: string) {
  const queryClient = useQueryClient();

  return useMutation<void, Error, string>({
    mutationFn: (messageId) => deleteMessage(conversationId, messageId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: [...QUERY_KEY, conversationId] });
    },
  });
}
