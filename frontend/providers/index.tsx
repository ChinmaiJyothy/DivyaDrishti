import { TooltipProvider } from "@/components/ui/tooltip";

import { AuthProvider } from "./auth-provider";
import { QueryProvider } from "./query-provider";
import { SettingsProvider } from "./settings-provider";
import { ThemeProvider } from "./theme-provider";
import { ToastProvider } from "./toast-provider";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
      <QueryProvider>
        <AuthProvider>
          <SettingsProvider>
            <TooltipProvider delayDuration={200}>
              {children}
              <ToastProvider />
            </TooltipProvider>
          </SettingsProvider>
        </AuthProvider>
      </QueryProvider>
    </ThemeProvider>
  );
}
