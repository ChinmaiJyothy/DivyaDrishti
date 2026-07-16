import { apiRequest } from "@/lib/api";
import type { BirthChart, BirthProfile, StudioChartDetail, StudioInsight } from "@/types";

export interface CreateBirthProfileInput {
  profile_name: string;
  relationship: string;
  date_of_birth: string;
  time_of_birth?: string;
  birth_place?: string;
  latitude?: number;
  longitude?: number;
  timezone?: string;
  accuracy_level?: string;
  notes?: string;
}

export interface UpdateBirthProfileInput {
  profile_name?: string;
  relationship?: string;
  date_of_birth?: string;
  time_of_birth?: string;
  birth_place?: string;
  latitude?: number;
  longitude?: number;
  timezone?: string;
  accuracy_level?: string;
  notes?: string;
}

export async function getProfiles(): Promise<BirthProfile[]> {
  return apiRequest<BirthProfile[]>("GET", "/profiles");
}

export async function getProfile(id: string): Promise<BirthProfile> {
  return apiRequest<BirthProfile>("GET", `/profiles/${id}`);
}

export async function createProfile(input: CreateBirthProfileInput): Promise<BirthProfile> {
  return apiRequest<BirthProfile>("POST", "/profiles", input);
}

export async function updateProfile(id: string, input: UpdateBirthProfileInput): Promise<BirthProfile> {
  return apiRequest<BirthProfile>("PATCH", `/profiles/${id}`, input);
}

export async function deleteProfile(id: string): Promise<void> {
  return apiRequest<void>("DELETE", `/profiles/${id}`);
}

export async function getProfileCharts(id: string): Promise<BirthChart[]> {
  return apiRequest<BirthChart[]>("GET", `/profiles/${id}/charts`);
}

export async function getLatestProfileChart(id: string, chartType = "rashi"): Promise<BirthChart> {
  const query = chartType ? `?chart_type=${encodeURIComponent(chartType)}` : "";
  return apiRequest<BirthChart>("GET", `/profiles/${id}/charts/latest${query}`);
}

export async function getProfileChartByType(id: string, chartType: string): Promise<BirthChart> {
  return apiRequest<BirthChart>("GET", `/profiles/${id}/charts/${chartType}`);
}

export async function generateChart(id: string, chartType = "rashi"): Promise<BirthChart> {
  return apiRequest<BirthChart>("POST", `/profiles/${id}/charts?chart_type=${encodeURIComponent(chartType)}`);
}

export async function getStudioDetail(chartId: string, question?: string): Promise<StudioChartDetail> {
  const query = question ? `?question=${encodeURIComponent(question)}` : "";
  return apiRequest<StudioChartDetail>("GET", `/charts/${chartId}/studio${query}`);
}

export async function analyzeChart(chartId: string, question: string): Promise<StudioInsight> {
  return apiRequest<StudioInsight>("POST", `/charts/${chartId}/analyze`, { question });
}

export async function searchChart(chartId: string, q: string): Promise<Array<Record<string, unknown>>> {
  return apiRequest<Array<Record<string, unknown>>>("GET", `/charts/${chartId}/search?q=${encodeURIComponent(q)}`);
}
