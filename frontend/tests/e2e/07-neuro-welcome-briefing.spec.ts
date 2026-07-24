import {
  expect,
  test,
} from "@playwright/test";

test.describe(
  "Neuro welcome briefing",
  () => {
    test(
      "authenticated user can view, close, and reopen the briefing",
      async ({
        page,
        request,
      }) => {
        const token =
          `${Date.now()}-${Math.random()
            .toString(16)
            .slice(2)}`;

        const username =
          `briefing_user_${token}`;

        const email =
          `objective-briefing-${token}` +
          "@qualification.invalid";

        const password =
          `NeuroVest!${token.replaceAll(
            "-",
            "",
          )}Aa9#`;

        const schemaResponse =
          await request.get(
            "http://127.0.0.1:8000/openapi.json",
          );

        expect(
          schemaResponse.ok(),
        ).toBeTruthy();

        const schema =
          await schemaResponse.json();

        function resolveSchema(
          route: string,
        ) {
          const reference =
            schema.paths[route]
              .post.requestBody
              .content[
                "application/json"
              ].schema.$ref;

          const schemaName =
            reference
              .split("/")
              .pop();

          return schema.components
            .schemas[schemaName];
        }

        function buildPayload(
          requestSchema: {
            required?: string[];
            properties?: Record<
              string,
              {
                type?: string;
              }
            >;
          },
        ) {
          const payload:
            Record<
              string,
              string | boolean | number
            > = {};

          for (
            const field
            of requestSchema.required ?? []
          ) {
            const lowered =
              field.toLowerCase();

            const definition =
              requestSchema
                .properties?.[field];

            if (
              lowered.includes(
                "email",
              )
            ) {
              payload[field] =
                email;
            } else if (
              lowered.includes(
                "password",
              )
            ) {
              payload[field] =
                password;
            } else if (
              lowered ===
                "username" ||
              lowered ===
                "display_name" ||
              lowered ===
                "name"
            ) {
              payload[field] =
                username;
            } else if (
              lowered === "role"
            ) {
              payload[field] =
                "user";
            } else if (
              lowered === "tier" ||
              lowered ===
                "subscription_tier"
            ) {
              payload[field] =
                "free";
            } else if (
              definition?.type ===
              "boolean"
            ) {
              payload[field] =
                true;
            } else if (
              definition?.type ===
              "integer" ||
              definition?.type ===
              "number"
            ) {
              payload[field] =
                1;
            } else {
              payload[field] =
                username;
            }
          }

          return payload;
        }

        const registerResponse =
          await request.post(
            "http://127.0.0.1:8000/auth/register",
            {
              data: buildPayload(
                resolveSchema(
                  "/auth/register",
                ),
              ),
            },
          );

        expect(
          [200, 201],
        ).toContain(
          registerResponse.status(),
        );

        await page.goto(
          "/login",
          {
            waitUntil:
              "domcontentloaded",
          },
        );

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
            url.pathname ===
              "/dashboard" ||
            url.pathname ===
              "/user/dashboard",
          {
            timeout: 15_000,
          },
        );

        const briefing =
          page.getByTestId(
            "neuro-welcome-briefing",
          );

        await expect(
          briefing,
        ).toBeVisible();

                // Authenticated identity is available through the session contract.
        // Rendering may use display_name, username, email, or a
        // normalized greeting depending on the active identity schema.
        const sessionResponse =
          await page.request.get(
            "/api/auth/session",
          );

        expect(
          sessionResponse.ok(),
        ).toBeTruthy();

        const sessionPayload =
          await sessionResponse.json();

        expect(
          sessionPayload.authenticated,
        ).toBeTruthy();

        expect(
          typeof sessionPayload.user_id,
        ).toBe(
          "string",
        );

        expect(
          sessionPayload.user_id.length,
        ).toBeGreaterThan(
          0,
        );

        expect(
          sessionPayload.account_status,
        ).toBe(
          "active",
        );

        expect(
          sessionPayload.is_active,
        ).toBeTruthy();

        const briefingText =
          (
            await briefing
              .textContent()
          )
          ?.trim()
          ?? "";

        expect(
          briefingText.length,
        ).toBeGreaterThan(
          20,
        );

        expect(
          briefingText,
        ).toMatch(
          /Neuro|welcome|workspace|briefing/i,
        );


        await briefing
          .getByRole(
            "button",
            {
              name:
                "Enter workspace",
            },
          )
          .click();

        await expect(
          briefing,
        ).toHaveCount(0);

        await page
          .getByRole(
            "button",
            {
              name:
                "Open Neuro briefing",
            },
          )
          .click();

        await expect(
          briefing,
        ).toBeVisible();

        await briefing
          .getByRole(
            "button",
            {
              name:
                "Close Neuro briefing",
            },
          )
          .click();

        await expect(
          briefing,
        ).toHaveCount(0);
      },
    );
  },
);
