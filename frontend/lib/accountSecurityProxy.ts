import { NextRequest, NextResponse } from "next/server";

import {
  clearBrowserTokens,
  readBrowserTokens,
} from "./sessionCookies";

import {
  validateCsrf,
  validateSameOrigin,
} from "./requestSecurity";

const BACKEND =
  process.env.NEUROVEST_BACKEND_URL ||
  process.env.BACKEND_URL ||
  "http://127.0.0.1:8000";

const NO_STORE = {
  "Cache-Control": "no-store, no-cache, must-revalidate",
};

type AccountOperation = "profile-read" | "profile-update" | "password";

export async function accountSecurityRequest(
  request: NextRequest,
  operation: AccountOperation
) {
  const changing = operation !== "profile-read";

  if (
    changing &&
    (!validateSameOrigin(request) || !validateCsrf(request))
  ) {
    return NextResponse.json(
      { detail: "Request validation failed" },
      { status: 403, headers: NO_STORE }
    );
  }

  const { accessToken, sessionMarker } =
    await readBrowserTokens();

  if (!accessToken) {
    return NextResponse.json(
      { detail: "Sign in to manage your account" },
      { status: 401, headers: NO_STORE }
    );
  }

  if (sessionMarker === "password_change_required") {
    return NextResponse.json(
      { detail: "Complete your required password change first" },
      { status: 403, headers: NO_STORE }
    );
  }

  let body: unknown = undefined;

  if (changing) {
    try {
      body = await request.json();
    } catch {
      return NextResponse.json(
        { detail: "Invalid request body" },
        { status: 400, headers: NO_STORE }
      );
    }

    if (
      body === null ||
      typeof body !== "object" ||
      Array.isArray(body)
    ) {
      return NextResponse.json(
        { detail: "Invalid request body" },
        { status: 400, headers: NO_STORE }
      );
    }
  }

  const target =
    operation === "password"
      ? "/api/v1/account/password"
      : "/api/v1/account/profile";

  const method =
    operation === "profile-read"
      ? "GET"
      : operation === "profile-update"
        ? "PATCH"
        : "POST";

  try {
    const response = await fetch(`${BACKEND}${target}`, {
      method,
      headers: {
        Authorization: `Bearer ${accessToken}`,
        Accept: "application/json",
        ...(changing ? { "Content-Type": "application/json" } : {}),
      },
      ...(changing ? { body: JSON.stringify(body) } : {}),
      cache: "no-store",
      signal: AbortSignal.timeout(20000),
    });

    let payload: unknown;

    try {
      payload = await response.json();
    } catch {
      payload = {
        detail: response.ok
          ? "Unexpected backend response"
          : "Account request failed",
      };
    }

    if (operation === "password" && response.ok) {
      // F12 revokes old refresh sessions and credential generations.
      // Clear browser-side cookies as well.
      await clearBrowserTokens();
    }

    return NextResponse.json(payload, {
      status: response.status,
      headers: NO_STORE,
    });
  } catch {
    return NextResponse.json(
      { detail: "Account service temporarily unavailable" },
      { status: 502, headers: NO_STORE }
    );
  }
}
