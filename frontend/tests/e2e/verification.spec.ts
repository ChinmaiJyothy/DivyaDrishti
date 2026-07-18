import { test, expect, type Page } from "@playwright/test";
import * as fs from "node:fs";
import * as path from "node:path";

const repoRoot = path.resolve(__dirname, "..", "..", "..");
const screenshotDir = path.join(repoRoot, "verification", "screenshots");
fs.mkdirSync(screenshotDir, { recursive: true });

const credentialsPath = path.join(repoRoot, "verification", "TEST_CREDENTIALS.env");
const credentials = fs.readFileSync(credentialsPath, "utf-8")
  .split("\n")
  .filter((l) => l.trim() && !l.startsWith("#"))
  .reduce((acc, line) => {
    const [key, ...rest] = line.split("=");
    acc[key] = rest.join("=").trim();
    return acc;
  }, {} as Record<string, string>);

const TEST_EMAIL = credentials["TEST_EMAIL"] || "verify-262ec337@example.com";
const TEST_PASSWORD = credentials["TEST_PASSWORD"] || "Password123!";

interface ConsoleEntry {
  type: string;
  text: string;
  location?: string;
}

interface Result {
  phase: string;
  ok: boolean;
  error?: string;
  durationMs: number;
  screenshot?: string;
}

type ConsoleListener = (msg: {
  type: () => string;
  text: () => string;
  location: () => object;
}) => void;

type ErrorListener = (error: Error) => void;
type ResponseListener = (response: { url: () => string; status: () => number; ok: () => boolean }) => void;

function attachListeners(page: Page, logs: { console: ConsoleEntry[]; errors: string[]; network: { url: string; status: number }[] }) {
  page.on("console", ((msg) => {
    const entry: ConsoleEntry = { type: msg.type(), text: msg.text(), location: JSON.stringify(msg.location()) };
    logs.console.push(entry);
    if (msg.type() === "error") logs.errors.push(`console: ${msg.text()}`);
  }) as ConsoleListener);
  page.on("pageerror", ((err) => {
    logs.errors.push(`pageerror: ${err.message}`);
  }) as ErrorListener);
  page.on("response", ((res) => {
    if (!res.ok() && res.status() >= 400) {
      logs.network.push({ url: res.url(), status: res.status() });
    }
  }) as ResponseListener);
}

async function screenshot(page: Page, name: string): Promise<string> {
  const file = path.join(screenshotDir, `${name}.png`);
  await page.screenshot({ path: file, fullPage: true });
  return file;
}

async function goto(page: Page, url: string, name: string) {
  await page.goto(url, { waitUntil: "networkidle" });
  await screenshot(page, name);
}

test("DivyaDrishti end-to-end frontend verification", async ({ page, browser, request }, testInfo) => {
  test.setTimeout(180000);
  const results: Result[] = [];
  const logs = { console: [] as ConsoleEntry[], errors: [] as string[], network: [] as { url: string; status: number }[] };
  attachListeners(page, logs);

  const start = Date.now();
  const record = async (phase: string, fn: () => Promise<void>) => {
    const t = Date.now();
    let ok = true;
    let error: string | undefined;
    try {
      await fn();
    } catch (e) {
      ok = false;
      error = e instanceof Error ? e.message : String(e);
    }
    results.push({ phase, ok, error, durationMs: Date.now() - t });
  };

  const email = TEST_EMAIL;
  const password = TEST_PASSWORD;

  // Use a large desktop viewport to avoid mobile drawer/sheet overlays
  await page.setViewportSize({ width: 1440, height: 900 });

  // 1. Login page and authentication
  await record("login-page", async () => {
    await page.goto("/", { waitUntil: "networkidle" });
    await expect(page.locator('input#email')).toBeVisible();
    await screenshot(page, "01-login");
  });

  await record("login-submit", async () => {
    await page.fill('input#email', email);
    await page.fill('input#password', password);
    await page.click('button:has-text("Sign in")');
    const dashboard = page.locator('text=Welcome back');
    const alert = page.locator('[role="alert"]');
    const errorMsg = await Promise.race([
      dashboard.waitFor({ state: 'visible', timeout: 15000 }).then(() => null as string | null),
      alert.waitFor({ state: 'visible', timeout: 15000 }).then(() => alert.textContent()).catch(() => 'Login did not complete'),
    ]);
    if (errorMsg) {
      await screenshot(page, "02-login-error");
      throw new Error(`Login failed: ${errorMsg}`);
    }
    await screenshot(page, "02-dashboard");
  });

  // Responsive layout (mobile)
  await record("responsive-mobile", async () => {
    const mobilePage = await browser.newPage({ viewport: { width: 390, height: 844 } });
    attachListeners(mobilePage, logs);
    await mobilePage.goto("/", { waitUntil: "domcontentloaded" });
    await mobilePage.fill('input#email', email);
    await mobilePage.fill('input#password', password);
    await mobilePage.click('button:has-text("Sign in")');
    const mDashboard = mobilePage.locator('text=Welcome back');
    const mAlert = mobilePage.locator('[role="alert"]');
    const mError = await Promise.race([
      mDashboard.waitFor({ state: 'visible', timeout: 15000 }).then(() => null as string | null),
      mAlert.waitFor({ state: 'visible', timeout: 15000 }).then(() => mAlert.textContent()).catch(() => 'Login did not complete'),
    ]);
    if (mError) {
      await screenshot(mobilePage, "03-login-error-mobile");
      throw new Error(`Mobile login failed: ${mError}`);
    }
    await screenshot(mobilePage, "03-dashboard-mobile");
    await mobilePage.close();
  });

  // 2. Chat workspace with streaming (use /ask to create a conversation)
  await record("chat-workspace", async () => {
    await page.goto("/ask", { waitUntil: "domcontentloaded" });
    const askHeading = page.locator('h1:has-text("Ask DivyaDrishti")');
    const loading = page.locator('[aria-label="Loading"]');
    const loginDialog = page.locator('text=Welcome to DivyaDrishti');
    const found = await Promise.race([
      askHeading.waitFor({ state: 'visible', timeout: 15000 }).then(() => 'ask'),
      loading.waitFor({ state: 'visible', timeout: 15000 }).then(() => 'loading'),
      loginDialog.waitFor({ state: 'visible', timeout: 15000 }).then(() => 'login'),
    ]).catch(() => 'timeout');
    if (found !== 'ask') {
      await screenshot(page, "04-chat-error");
      throw new Error(`Ask page did not load; state=${found}, url=${page.url()}`);
    }
    await expect(page.locator('input#question')).toBeVisible({ timeout: 5000 });
    await screenshot(page, "04-chat-workspace");
  });

  await record("chat-streaming", async () => {
    const question = "What are my career prospects?";
    await page.fill('input#question', question);
    await page.click('[id="domain"]', { timeout: 5000 });
    await page.getByRole('option', { name: 'Career' }).click({ timeout: 5000 });
    await page.click('button:has-text("Ask")', { timeout: 5000 });
    await page.waitForURL(/\/chat\/.+/, { timeout: 15000, waitUntil: 'domcontentloaded' });
    await screenshot(page, "05-chat-initial");

    // Wait for assistant response
    const assistant = page.locator('[aria-label="Assistant message"]').first();
    await assistant.waitFor({ state: 'visible', timeout: 45000 });
    await page.waitForTimeout(1000);
    await screenshot(page, "06-chat-response");

    // Try to open explainability panel by clicking the assistant message
    if (await assistant.isVisible().catch(() => false)) {
      await assistant.click();
      await page.waitForTimeout(500);
      await screenshot(page, "07-explainability");
    }
  });

  // 3. Birth profiles
  await record("birth-profiles", async () => {
    await page.goto("/profiles", { waitUntil: "networkidle" });
    await page.click('button:has-text("Add Profile")');
    await page.fill('input#profile_name', "Verification Profile");
    await page.fill('input#date_of_birth', "1990-01-01");
    await page.fill('input#time_of_birth', "10:00");
    await page.fill('input#birth_place', "Delhi, India");
    await page.fill('input#latitude', "28.61");
    await page.fill('input#longitude', "77.21");
    await page.fill('input#timezone', "Asia/Kolkata");
    await page.click('button:has-text("Create Profile")');
    await page.waitForSelector('text=Verification Profile', { timeout: 10000 });
    await screenshot(page, "07-profiles");
  });

  // 4. Knowledge library (admin)
  await record("knowledge-library", async () => {
    await page.goto("/knowledge", { waitUntil: "networkidle" });
    await screenshot(page, "08-knowledge");
  });

  // 5. Settings
  await record("settings", async () => {
    await page.goto("/settings", { waitUntil: "networkidle" });
    await screenshot(page, "09-settings");
  });

  // 6. Feedback
  await record("feedback", async () => {
    await page.goto("/feedback", { waitUntil: "networkidle" });
    await page.fill('textarea#comment', "This is a verification feedback entry.");
    await page.click('button:has-text("Submit Feedback")');
    await page.waitForTimeout(1000);
    await screenshot(page, "10-feedback");
  });

  // 7. Admin
  await record("admin", async () => {
    await page.goto("/admin", { waitUntil: "networkidle" });
    await screenshot(page, "11-admin");
  });

  // 8. Conversations (persistence)
  await record("conversations", async () => {
    await page.goto("/conversations", { waitUntil: "networkidle" });
    await screenshot(page, "12-conversations");
  });

  // 9. Error state (404)
  await record("error-404", async () => {
    const res = await page.goto("/this-page-does-not-exist", { waitUntil: "domcontentloaded" });
    if (res && res.status() >= 400) {
      await screenshot(page, "13-error-404");
    }
  });

  // Write logs and results
  const duration = Date.now() - start;
  fs.writeFileSync(
    path.join(repoRoot, "verification", "frontend_results.json"),
    JSON.stringify(
      {
        startedAt: new Date(start).toISOString(),
        durationMs: duration,
        results,
        console: logs.console,
        errors: logs.errors,
        network: logs.network,
      },
      null,
      2
    )
  );

  if (logs.errors.length > 0) {
    fs.writeFileSync(path.join(repoRoot, "verification", "frontend_console.log"), logs.errors.join("\n"));
  }

  const failed = results.filter((r) => !r.ok);
  expect(failed, `Frontend verification failed: ${JSON.stringify(failed)}`).toHaveLength(0);
});
