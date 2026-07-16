import { defineConfig, devices } from "@playwright/test";
import path from "path";

const frontend = __dirname;
const root = path.join(frontend, "..");
const nodeDir = path.join(root, "tools", "node");
const node = process.platform === "win32" ? "node.exe" : "node";
const nodePath = path.join(nodeDir, node);
const nextPath = path.join(frontend, "node_modules", "next", "dist", "bin", "next");

export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: "html",
  use: {
    baseURL: "http://localhost:3000",
    trace: "on-first-retry",
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "firefox", use: { ...devices["Desktop Firefox"] } },
    { name: "webkit", use: { ...devices["Desktop Safari"] } },
    { name: "Mobile Chrome", use: { ...devices["Pixel 5"] } },
    { name: "Mobile Safari", use: { ...devices["iPhone 12"] } },
  ],
  webServer: {
    command: `"${nodePath}" "${nextPath}" dev`,
    url: "http://localhost:3000",
    reuseExistingServer: !process.env.CI,
    env: {
      ...process.env,
      PATH: `"${nodeDir}"` + path.delimiter + (process.env.PATH ?? ""),
      NEXT_TELEMETRY_DISABLED: "1",
    },
  },
});
