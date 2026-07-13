"use client";

import { createContext, useContext, useMemo, useState } from "react";

interface Settings {
  language: string;
  theme: string;
  currentProfileId: string | null;
}

interface SettingsContextValue {
  settings: Settings;
  updateSettings: (settings: Partial<Settings>) => void;
  setCurrentProfileId: (id: string | null) => void;
}

const SettingsContext = createContext<SettingsContextValue>({
  settings: { language: "en", theme: "system", currentProfileId: null },
  updateSettings: () => {},
  setCurrentProfileId: () => {},
});

export function SettingsProvider({ children }: { children: React.ReactNode }) {
  const [settings, setSettings] = useState<Settings>({
    language: "en",
    theme: "system",
    currentProfileId: null,
  });

  const value = useMemo(
    () => ({
      settings,
      updateSettings: (next: Partial<Settings>) =>
        setSettings((prev) => ({ ...prev, ...next })),
      setCurrentProfileId: (id: string | null) =>
        setSettings((prev) => ({ ...prev, currentProfileId: id })),
    }),
    [settings]
  );

  return <SettingsContext.Provider value={value}>{children}</SettingsContext.Provider>;
}

export function useSettings() {
  return useContext(SettingsContext);
}
