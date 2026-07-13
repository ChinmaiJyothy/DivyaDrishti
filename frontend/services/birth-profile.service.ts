import { apiRequest } from "@/lib/api";
import type { BirthChart, BirthProfile } from "@/types";

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

export async function getLatestProfileChart(id: string): Promise<BirthChart> {
  return apiRequest<BirthChart>("GET", `/profiles/${id}/charts/latest`);
}
