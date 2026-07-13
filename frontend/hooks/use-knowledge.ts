"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  deleteBook,
  getBooks,
  getKnowledgeOverview,
  getKnowledgeVersions,
  uploadBook,
  type UploadBookInput,
} from "@/services/knowledge.service";
import type { KnowledgeOverview, KnowledgeVersion, UploadedBook } from "@/types";

const BOOKS_QUERY_KEY = ["knowledge", "books"];
const VERSIONS_QUERY_KEY = ["knowledge", "versions"];
const OVERVIEW_QUERY_KEY = ["knowledge", "overview"];

export function useBooks() {
  return useQuery<UploadedBook[]>({
    queryKey: BOOKS_QUERY_KEY,
    queryFn: getBooks,
    retry: 1,
  });
}

export function useKnowledgeVersions() {
  return useQuery<KnowledgeVersion[]>({
    queryKey: VERSIONS_QUERY_KEY,
    queryFn: getKnowledgeVersions,
    retry: 1,
  });
}

export function useKnowledgeOverview() {
  return useQuery<KnowledgeOverview>({
    queryKey: OVERVIEW_QUERY_KEY,
    queryFn: getKnowledgeOverview,
    retry: 1,
  });
}

export function useUploadBook() {
  const queryClient = useQueryClient();

  return useMutation<UploadedBook, Error, UploadBookInput>({
    mutationFn: uploadBook,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: BOOKS_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: OVERVIEW_QUERY_KEY });
    },
  });
}

export function useDeleteBook() {
  const queryClient = useQueryClient();

  return useMutation<void, Error, string>({
    mutationFn: deleteBook,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: BOOKS_QUERY_KEY });
      queryClient.invalidateQueries({ queryKey: OVERVIEW_QUERY_KEY });
    },
  });
}
