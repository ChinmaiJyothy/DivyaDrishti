export interface User {
  id: string;
  email: string;
  name: string;
  role: string;
  is_superuser?: boolean;
}

export interface Role {
  id: string;
  name: string;
  description?: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface AuthResponse extends AuthTokens {
  user?: User;
}

export interface BirthProfile {
  id: string;
  user_id: string;
  profile_name: string;
  relationship: string;
  date_of_birth: string;
  time_of_birth: string | null;
  birth_place: string | null;
  latitude: number | null;
  longitude: number | null;
  timezone: string;
  accuracy_level: string;
  notes: string | null;
  chart_metadata: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface BirthChart {
  id: string;
  profile_id: string;
  chart_type: string;
  chart_data: Record<string, unknown> | null;
  generated_at: string;
}

export interface Message {
  id: string;
  role: string;
  content: string;
  created_at: string;
}

export interface Conversation {
  id: string;
  user_id: string;
  birth_profile_id: string | null;
  title: string | null;
  domain: string | null;
  is_archived: boolean;
  is_deleted: boolean;
  confidence: number | null;
  created_at: string;
  updated_at: string;
  messages: Message[];
}

export interface Report {
  id: string;
  user_id: string;
  title: string;
  category: string;
  status: "pending" | "ready" | "failed";
  file_url: string | null;
  file_name: string | null;
  file_format: string;
  created_at: string;
  updated_at: string;
}

export interface UploadedBook {
  id: string;
  user_id: string;
  file_path: string;
  file_name: string;
  title: string | null;
  author: string | null;
  language: string | null;
  status: string;
  book_metadata: Record<string, unknown> | null;
  is_active: boolean;
  created_at: string;
}

export interface KnowledgeVersion {
  id: string;
  rule_id: string;
  version: string;
  created_at: string;
  modified_at: string;
  modified_by: string | null;
  approval_status: string;
  change_history: string | null;
  deprecated: boolean;
}

export interface KnowledgeOverview {
  books_count: number;
  versions_count: number;
  last_updated: string | null;
}

export interface Preference {
  id: string;
  user_id: string;
  preferred_language: string;
  preferred_explanation_depth: string;
  preferred_astrology_school: string;
  preferred_chart_style: string;
  citation_mode: string;
  dark_mode: boolean;
  units: string;
  notification_settings: Record<string, unknown> | null;
  timezone: string;
  country: string | null;
  theme_preference: string;
  privacy_settings: Record<string, unknown> | null;
}

export interface Feedback {
  id: string;
  user_id: string;
  rating: string;
  comment: string | null;
  created_at: string;
}

export interface ThemeSettings {
  theme: "light" | "dark" | "system";
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface ApiError {
  message: string;
  code?: string;
}
