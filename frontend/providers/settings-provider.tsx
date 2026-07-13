"use client";

import { createContext, useContext, useMemo, useState } from "react";

interface Settings {
  language: string;
  theme: string;
}

interface SettingsContextValue {
  settings: Settings;
  updateSettings: (settings: Partial<Settings>) => void;
}

const SettingsContext = createContext<SettingsContextValue>({
  settings: { language: "en", theme: "system" },
  updateSettings: () => {},
});

export function SettingsProvider({ children }: { children: React.ReactNode }) {
  const [settings, setSettings] = useState<Settings>({ language: "en", theme: "system" });

  const value = useMemo(
    () => ({
      settings,
      updateSettings: (next: Partial<Settings>) =>
        setSettings((prev) => ({ ...prev, ...next })),
    }),
    [settings]
  );

  return <SettingsContext.Provider value={value}>{children}</SettingsContext.Provider>;
}

export function useSettings() {
  return useContext(SettingsContext);
}
