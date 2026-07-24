import { expect, test } from "@playwright/test";

test.describe("Frontend and backend connectivity", () => {
  test("backend documentation endpoint is reachable", async ({ request }) => {
    const response = await request.get(
      "http://127.0.0.1:8000/docs",
    );

    expect(response.ok()).toBeTruthy();
  });

  test("backend OpenAPI contract is reachable", async ({ request }) => {
    const response = await request.get(
      "http://127.0.0.1:8000/openapi.json",
    );

    expect(response.ok()).toBeTruthy();

    const schema = await response.json();

    expect(schema.paths).toBeDefined();
    expect(schema.paths["/auth/login"]).toBeDefined();
    expect(schema.paths["/auth/register"]).toBeDefined();
    expect(schema.paths["/api/v1/positions"]).toBeDefined();
    expect(schema.paths["/api/v1/orders"]).toBeDefined();
    expect(schema.paths["/api/v1/analytics"]).toBeDefined();
  });

  test("protected backend route rejects anonymous request", async ({
    request,
  }) => {
    const response = await request.get(
      "http://127.0.0.1:8000/api/v1/positions",
    );

    expect([401, 403]).toContain(response.status());
  });
});
