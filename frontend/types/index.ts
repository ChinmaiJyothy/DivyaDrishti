// Shared TypeScript types used across the application.

export interface User {
  id: string;
  email: string;
  name: string;
  role: string;
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
