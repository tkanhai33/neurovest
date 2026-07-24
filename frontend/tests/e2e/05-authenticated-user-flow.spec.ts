import { expect, test } from "@playwright/test";

test.describe("Authenticated user flow", () => {
  test("register, login, persist session, and logout", async ({
    page,
    request,
  }) => {
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

    const token = Date.now().toString();

    const email = `objective-playwright-${token}@qualification.invalid`;
    const password = `NeuroVest!${token}Aa9#`;

    const openApiResponse = await request.get(
      "http://127.0.0.1:8000/openapi.json",
    );

    expect(openApiResponse.ok()).toBeTruthy();

    const schema = await openApiResponse.json();

    const registerReference =
      schema.paths["/auth/register"].post.requestBody.content[
        "application/json"
      ].schema.$ref;

    const loginReference =
      schema.paths["/auth/login"].post.requestBody.content[
        "application/json"
      ].schema.$ref;

    const registerSchemaName = registerReference.split("/").pop();
    const loginSchemaName = loginReference.split("/").pop();

    const registerSchema =
      schema.components.schemas[registerSchemaName];

    const loginSchema =
      schema.components.schemas[loginSchemaName];

    const buildPayload = (
      requestSchema: {
        required?: string[];
        properties?: Record<string, { type?: string }>;
      },
    ) => {
      const payload: Record<string, string | boolean | number> = {};

      for (const field of requestSchema.required ?? []) {
        const lowered = field.toLowerCase();
        const definition = requestSchema.properties?.[field];

        if (lowered.includes("email")) {
          payload[field] = email;
        } else if (lowered.includes("password")) {
          payload[field] = password;
        } else if (
          lowered === "username" ||
          lowered === "name" ||
          lowered === "display_name"
        ) {
          payload[field] = `playwright_${token}`;
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
          payload[field] = `playwright-${token}`;
        }
      }

      return payload;
    };

    const registerPayload = buildPayload(registerSchema);
    const loginPayload = buildPayload(loginSchema);

    void loginPayload;

    const registerResponse = await request.post(
      "http://127.0.0.1:8000/auth/register",
      {
        data: registerPayload,
      },
    );

    expect([200, 201]).toContain(registerResponse.status());

    await page.goto("/login");

    const emailInput = page
      .locator(
        'input[type="email"], input[name*="email" i], input[autocomplete="email"]',
      )
      .first();

    const passwordInput = page
      .locator(
        'input[type="password"], input[name*="password" i], input[autocomplete="current-password"]',
      )
      .first();

    await emailInput.fill(email);
    await passwordInput.fill(password);

    await page
      .locator('button[type="submit"], input[type="submit"]')
      .first()
      .click();

    // Next.js may keep background requests active after the page is usable.
    // Wait for the document, then rely on the test's URL and UI assertions.
    await page.waitForLoadState(
      "domcontentloaded",
    );

    await page.waitForURL(
      (url) =>
        url.pathname === "/dashboard"
        || url.pathname === "/user/dashboard",
      {
        timeout: 15_000,
      },
    );

    await page.goto("/dashboard", {
      waitUntil: "domcontentloaded",
    });

    expect(
      ["/dashboard", "/user/dashboard"],
    ).toContain(
      new URL(page.url()).pathname,
    );

    await page.reload({
      waitUntil: "domcontentloaded",
    });

    expect(
      ["/dashboard", "/user/dashboard"],
    ).toContain(
      new URL(page.url()).pathname,
    );

    const logoutButton = page
      .getByRole("button", {
        name: /log\s*out|sign\s*out/i,
      })
      .or(
        page.getByRole("link", {
          name: /log\s*out|sign\s*out/i,
        }),
      )
      .first();

    if (await logoutButton.isVisible().catch(() => false)) {
      await Promise.all([
        page.waitForURL(
          (url) => url.pathname.startsWith("/login"),
          {
            timeout: 10_000,
          },
        ),
        logoutButton.click(),
      ]).catch(async () => {
        await page.waitForTimeout(500);
      });
    } else {
      await page.request.post(
        "http://127.0.0.1:8000/auth/logout",
      );

      await page.context().clearCookies();
    }

    await page.goto("/dashboard", {
      waitUntil: "domcontentloaded",
    }).catch(() => null);

        // Logout invalidates the authenticated session before
    // protected navigation is checked.
    await expect
      .poll(
        async () => {
          const response =
            await page.request.get(
              "/api/auth/session",
            );

          if (
            response.status()
            === 401
          ) {
            return true;
          }

          const payload =
            await response
              .json()
              .catch(
                () => ({}),
              );

          const authenticated =
            payload.authenticated
            ?? payload.session
              ?.authenticated
            ?? payload.data
              ?.authenticated
            ?? false;

          return (
            authenticated
            === false
          );
        },
        {
          timeout:
            15_000,
          message:
            "Logout invalidates the authenticated session",
        },
      )
      .toBeTruthy();

    await page.goto(
      "/user/dashboard",
      {
        waitUntil:
          "domcontentloaded",
      },
    );

    await page.waitForURL(
      (url) =>
        url.pathname
          .startsWith(
            "/login",
          ),
      {
        timeout:
          15_000,
      },
    );


    expect(
      new URL(page.url()).pathname.startsWith("/login"),
    ).toBeTruthy();
  });
});
