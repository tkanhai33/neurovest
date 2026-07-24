import { expect, Locator, Page, test } from "@playwright/test";

type ApiSchema = {
  required?: string[];
  properties?: Record<string, { type?: string }>;
};

function buildPayload(
  schema: ApiSchema,
  email: string,
  password: string,
  token: string,
): Record<string, string | boolean | number> {
  const payload: Record<string, string | boolean | number> = {};

  for (const field of schema.required ?? []) {
    const lowered = field.toLowerCase();
    const definition = schema.properties?.[field];

    if (lowered.includes("email")) {
      payload[field] = email;
    } else if (lowered.includes("password")) {
      payload[field] = password;
    } else if (
      lowered === "username" ||
      lowered === "name" ||
      lowered === "display_name"
    ) {
      payload[field] = `playwright_navigation_${token}`;
    } else if (lowered === "role") {
      payload[field] = "user";
    } else if (
      lowered === "tier" ||
      lowered === "subscription_tier"
    ) {
      payload[field] = "free";
    } else if (definition?.type === "boolean") {
      payload[field] = true;
    } else if (definition?.type === "integer") {
      payload[field] = 1;
    } else if (definition?.type === "number") {
      payload[field] = 1;
    } else {
      payload[field] = `playwright-navigation-${token}`;
    }
  }

  return payload;
}

function resolveReferencedSchema(
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  openApi: any,
  route: string,
): ApiSchema {
  const reference =
    openApi.paths[route].post.requestBody.content[
      "application/json"
    ].schema.$ref;

  const schemaName = reference.split("/").pop();

  if (!schemaName) {
    throw new Error(`Unable to resolve schema for ${route}`);
  }

  return openApi.components.schemas[schemaName];
}

async function findNavigationControl(
  page: Page,
  name: RegExp,
): Promise<Locator | null> {
  const link = page
    .getByRole("link", { name })
    .first();

  if (await link.isVisible().catch(() => false)) {
    return link;
  }

  const button = page
    .getByRole("button", { name })
    .first();

  if (await button.isVisible().catch(() => false)) {
    return button;
  }

  const textControl = page
    .getByText(name)
    .first();

  if (await textControl.isVisible().catch(() => false)) {
    return textControl;
  }

  return null;
}

async function verifyRenderedPage(
  page: Page,
  label: string,
): Promise<void> {
  await expect(page.locator("body")).toBeVisible();

  const bodyText = (
    await page.locator("body").innerText()
  ).trim();

  expect(
    bodyText.length,
    `${label} rendered an empty page`,
  ).toBeGreaterThan(0);

  await expect(
    page.getByText(
      /application error|internal server error|something went wrong/i,
    ),
  ).toHaveCount(0);
}

test.describe("Authenticated dashboard navigation", () => {
  test("dashboard, portfolio, and analytics render for a user", async ({
    page,
    request,
  }) => {
    const browserErrors: string[] = [];

    page.on("pageerror", (error) => {
      browserErrors.push(error.message);
    });
        await page.addLocatorHandler(
          page.getByTestId(
            "neuro-welcome-briefing",
          ),
          async (
            briefing,
          ) => {
            const enterWorkspace =
              briefing.getByRole(
                "button",
                {
                  name:
                    "Enter workspace",
                },
              );

            if (
              await enterWorkspace
                .isVisible()
                .catch(
                  () => false,
                )
            ) {
              await enterWorkspace.click();
              return;
            }

            const closeBriefing =
              briefing.getByRole(
                "button",
                {
                  name:
                    "Close Neuro briefing",
                },
              );

            if (
              await closeBriefing
                .isVisible()
                .catch(
                  () => false,
                )
            ) {
              await closeBriefing.click();
            }
          },
        );


    const token = `${Date.now()}-${Math.random()
      .toString(16)
      .slice(2)}`;

    const email =
      `objective-playwright-navigation-${token}` +
      "@qualification.invalid";

    const password =
      `NeuroVest!${token.replaceAll("-", "")}Aa9#`;

    const openApiResponse = await request.get(
      "http://127.0.0.1:8000/openapi.json",
    );

    expect(openApiResponse.ok()).toBeTruthy();

    const openApi = await openApiResponse.json();

    const registerSchema = resolveReferencedSchema(
      openApi,
      "/auth/register",
    );

    const registerPayload = buildPayload(
      registerSchema,
      email,
      password,
      token,
    );

    const registerResponse = await request.post(
      "http://127.0.0.1:8000/auth/register",
      {
        data: registerPayload,
      },
    );

    expect([200, 201]).toContain(
      registerResponse.status(),
    );

    await page.goto("/login", {
      waitUntil: "domcontentloaded",
    });

    await page
      .locator(
        'input[type="email"], input[name*="email" i], input[autocomplete="email"]',
      )
      .first()
      .fill(email);

    await page
      .locator(
        'input[type="password"], input[name*="password" i], input[autocomplete="current-password"]',
      )
      .first()
      .fill(password);

    await page
      .locator(
        'button[type="submit"], input[type="submit"]',
      )
      .first()
      .click();

    await page.waitForURL(
      (url) =>
        url.pathname === "/dashboard" ||
        url.pathname === "/user/dashboard",
      {
        timeout: 15_000,
      },
    );

    // Next.js may keep background requests active after the page is usable.
    // Wait for the document, then rely on the test's URL and UI assertions.
    await page.waitForLoadState(
      "domcontentloaded",
    );

    await verifyRenderedPage(
      page,
      "Authenticated dashboard",
    );

    expect(
      ["/dashboard", "/user/dashboard"],
    ).toContain(
      new URL(page.url()).pathname,
    );

    const portfolioControl =
      await findNavigationControl(
        page,
        /portfolio|positions|holdings/i,
      );

    expect(
      portfolioControl,
      "No visible Portfolio, Positions, or Holdings navigation control was found",
    ).not.toBeNull();

    await portfolioControl!.click();

    await page.waitForLoadState(
      "domcontentloaded",
    );

    await page.waitForTimeout(500);

    await verifyRenderedPage(
      page,
      "Portfolio view",
    );

    const portfolioText = (
      await page.locator("body").innerText()
    ).toLowerCase();

    expect(
      portfolioText,
      "Portfolio view does not contain portfolio-related content",
    ).toMatch(
      /portfolio|position|holding|shares|allocation/,
    );

    const analyticsControl =
      await findNavigationControl(
        page,
        /analytics|performance|insights/i,
      );

    expect(
      analyticsControl,
      "No visible Analytics, Performance, or Insights navigation control was found",
    ).not.toBeNull();

    await analyticsControl!.click();

    await page.waitForLoadState(
      "domcontentloaded",
    );

    await page.waitForTimeout(500);

    await verifyRenderedPage(
      page,
      "Analytics view",
    );

    const analyticsText = (
      await page.locator("body").innerText()
    ).toLowerCase();

    expect(
      analyticsText,
      "Analytics view does not contain analytics-related content",
    ).toMatch(
      /analytics|performance|profit|loss|pnl|return|win rate|insight/,
    );

    expect(
      browserErrors,
      `Browser errors occurred: ${browserErrors.join(" | ")}`,
    ).toEqual([]);
  });
});
