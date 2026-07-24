import { expect, test } from "@playwright/test";

test.describe("Authentication boundary", () => {
  test("login page loads with usable form controls", async ({ page }) => {
    const response = await page.goto("/login", {
      waitUntil: "domcontentloaded",
    });

    expect(response).not.toBeNull();
    expect(response?.ok()).toBeTruthy();

    const email = page.locator(
      'input[type="email"], input[name*="email" i], input[autocomplete="email"]',
    ).first();

    const password = page.locator(
      'input[type="password"], input[name*="password" i], input[autocomplete="current-password"]',
    ).first();

    const submit = page.locator(
      'button[type="submit"], input[type="submit"]',
    ).first();

    await expect(email).toBeVisible();
    await expect(password).toBeVisible();
    await expect(submit).toBeVisible();
    await expect(submit).toBeEnabled();
  });

  test("unauthenticated dashboard access is blocked", async ({ page }) => {
    await page.goto("/dashboard", {
      waitUntil: "domcontentloaded",
    });

    await page.waitForLoadState("networkidle");

    const pathname = new URL(page.url()).pathname;

    const loginFormVisible = await page
      .locator(
        'input[type="password"], input[autocomplete="current-password"]',
      )
      .first()
      .isVisible()
      .catch(() => false);

    expect(
      pathname === "/login" ||
        pathname.startsWith("/login/") ||
        loginFormVisible,
    ).toBeTruthy();
  });

  test("unauthenticated admin access is blocked", async ({ page }) => {
    await page.goto("/admin", {
      waitUntil: "domcontentloaded",
    });

    await page.waitForLoadState("networkidle");

    const pathname = new URL(page.url()).pathname;

    expect(
      pathname === "/login" ||
        pathname.startsWith("/login/") ||
        pathname === "/",
    ).toBeTruthy();
  });
});
