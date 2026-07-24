import { expect, test } from "@playwright/test";

test.describe("Public navigation", () => {
  test("homepage renders without browser errors", async ({ page }) => {
    const browserErrors: string[] = [];

    page.on("pageerror", (error) => {
      browserErrors.push(error.message);
    });

    const response = await page.goto("/", {
      waitUntil: "networkidle",
    });

    expect(response).not.toBeNull();
    expect(response?.ok()).toBeTruthy();

    await expect(page.locator("body")).toBeVisible();

    expect(browserErrors).toEqual([]);
  });

  test("login page has no empty document", async ({ page }) => {
    await page.goto("/login", {
      waitUntil: "networkidle",
    });

    const bodyText = await page.locator("body").innerText();

    expect(bodyText.trim().length).toBeGreaterThan(0);
  });

  test("unknown route displays a controlled response", async ({ page }) => {
    const response = await page.goto(
      "/objective-playwright-route-that-does-not-exist",
      {
        waitUntil: "domcontentloaded",
      },
    );

    expect(response).not.toBeNull();

    await expect(page.locator("body")).toBeVisible();

    const bodyText = await page.locator("body").innerText();

    expect(bodyText.trim().length).toBeGreaterThan(0);
  });
});
