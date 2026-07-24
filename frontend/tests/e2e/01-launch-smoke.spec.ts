import { expect, test } from "@playwright/test";

test("NeuroVest frontend loads", async ({ page }) => {
  const response = await page.goto("/", {
    waitUntil: "domcontentloaded",
  });

  expect(response).not.toBeNull();
  expect(response?.ok()).toBeTruthy();

  await expect(page.locator("body")).toBeVisible();

  await expect(page).toHaveTitle(/NeuroVest|Neuro/i);
});
