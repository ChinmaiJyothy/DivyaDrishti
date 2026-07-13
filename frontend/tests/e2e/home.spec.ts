import { expect, test } from "@playwright/test";

test.describe("Home page", () => {
  test("shows the frontend foundation placeholder", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByText("Frontend Foundation")).toBeVisible();
  });
});
