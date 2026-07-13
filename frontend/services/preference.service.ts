import { apiRequest } from "@/lib/api";
import type { Preference } from "@/types";

export type PreferenceUpdateInput = Partial<Preference>;

export async function getPreferences(): Promise<Preference> {
  return apiRequest<Preference>("GET", "/preferences");
}

export async function updatePreferences(input: PreferenceUpdateInput): Promise<Preference> {
  return apiRequest<Preference>("PATCH", "/preferences", input);
}
