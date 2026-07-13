import { expect, test } from "@playwright/test";

test.describe("Dashboard", () => {
  test("shows the dashboard shell", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByText("Welcome back")).toBeVisible();
    await expect(page.getByText("Quick Actions")).toBeVisible();
  });
});
