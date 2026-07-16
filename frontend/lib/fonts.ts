import localFont from "next/font/local";

export const inter = localFont({
  display: "swap",
  variable: "--font-sans",
  fallback: ["system-ui", "sans-serif"],
  src: [
    {
      path: "../node_modules/@fontsource/inter/files/inter-latin-400-normal.woff2",
      weight: "400",
      style: "normal",
    },
    {
      path: "../node_modules/@fontsource/inter/files/inter-latin-700-normal.woff2",
      weight: "700",
      style: "normal",
    },
  ],
});

export const playfairDisplay = localFont({
  display: "swap",
  variable: "--font-display",
  fallback: ["Georgia", "serif"],
  src: [
    {
      path: "../node_modules/@fontsource/playfair-display/files/playfair-display-latin-400-normal.woff2",
      weight: "400",
      style: "normal",
    },
    {
      path: "../node_modules/@fontsource/playfair-display/files/playfair-display-latin-700-normal.woff2",
      weight: "700",
      style: "normal",
    },
  ],
});
