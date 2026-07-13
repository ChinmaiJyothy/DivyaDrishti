import { apiRequest } from "@/lib/api";
import type { User } from "@/types";

export async function getMe(): Promise<User> {
  return apiRequest<User>("GET", "/users/me");
}
