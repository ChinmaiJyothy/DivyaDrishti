import { apiRequest } from "@/lib/api";
import type { KnowledgeOverview, KnowledgeVersion, UploadedBook } from "@/types";

export interface UploadBookInput {
  file: File;
  title?: string;
  author?: string;
  language?: string;
}

export async function getBooks(): Promise<UploadedBook[]> {
  return apiRequest<UploadedBook[]>("GET", "/books");
}

export async function uploadBook(input: UploadBookInput): Promise<UploadedBook> {
  const formData = new FormData();
  formData.append("file", input.file);
  if (input.title) formData.append("title", input.title);
  if (input.author) formData.append("author", input.author);
  if (input.language) formData.append("language", input.language);

  return apiRequest<UploadedBook>("POST", "/books", formData);
}

export async function deleteBook(id: string): Promise<void> {
  return apiRequest<void>("DELETE", `/books/${id}`);
}

export async function getKnowledgeVersions(): Promise<KnowledgeVersion[]> {
  return apiRequest<KnowledgeVersion[]>("GET", "/knowledge/versions");
}

export async function getKnowledgeOverview(): Promise<KnowledgeOverview> {
  return apiRequest<KnowledgeOverview>("GET", "/knowledge");
}
