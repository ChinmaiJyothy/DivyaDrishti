import { apiRequest } from "@/lib/api";
import type { Report } from "@/types";

export interface CreateReportInput {
  title: string;
  category: string;
}

export interface UpdateReportInput {
  title?: string;
  category?: string;
  status?: "pending" | "ready" | "failed";
  file_url?: string;
  file_name?: string;
}

export async function getReports(): Promise<Report[]> {
  return apiRequest<Report[]>("GET", "/reports");
}

export async function getReport(id: string): Promise<Report> {
  return apiRequest<Report>("GET", `/reports/${id}`);
}

export async function createReport(input: CreateReportInput): Promise<Report> {
  return apiRequest<Report>("POST", "/reports", input);
}

export async function updateReport(id: string, input: UpdateReportInput): Promise<Report> {
  return apiRequest<Report>("PATCH", `/reports/${id}`, input);
}

export async function deleteReport(id: string): Promise<void> {
  return apiRequest<void>("DELETE", `/reports/${id}`);
}
