import { expect, test } from "@playwright/test";

test("dashboard renders public shell elements", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("text=DivyaDrishti")).toBeVisible();
});
