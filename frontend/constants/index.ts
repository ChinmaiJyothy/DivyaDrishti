export const APP_NAME = "DivyaDrishti";

export const LANGUAGES = [
  { code: "en", label: "English" },
  { code: "hi", label: "Hindi" },
  { code: "sa", label: "Sanskrit" },
];

export const ROLES = ["user", "researcher", "admin", "super_admin"] as const;

export const CHART_STYLES = ["north_indian", "south_indian"] as const;

export const EXPLANATION_DEPTHS = ["brief", "balanced", "detailed"] as const;
