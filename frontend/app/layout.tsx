import type { Metadata, Viewport } from "next";

import { inter, playfairDisplay } from "@/lib/fonts";
import { Providers } from "@/providers";

import "./globals.css";

export const metadata: Metadata = {
  title: "DivyaDrishti",
  description: "AI-powered Vedic Astrology Expert System",
};

export const viewport: Viewport = {
  themeColor: "#4338ca",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} ${playfairDisplay.variable} font-sans`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
