import {
  NextResponse,
} from "next/server";

import {
  ensureCsrfCookie,
  readBrowserTokens,
} from "../../../../lib/sessionCookies";

export const dynamic = "force-dynamic";

const BACKEND_BASE_URL =
  process.env.NEUROVEST_BACKEND_URL ||
  process.env.BACKEND_URL ||
  "http://127.0.0.1:8000";

type IntrospectionPayload = {
  user_id?: string;
  role?: string;
  subscription_tier?: string;
  permissions?: string[];
  is_administrative?: boolean;
  status?: string;
  is_active?: boolean;
  must_change_password?: boolean;
};

export async function GET() {
  await ensureCsrfCookie();

  const {
    accessToken,
    refreshToken,
    sessionMarker,
  } = await readBrowserTokens();

  const authenticated = Boolean(
    accessToken &&
    refreshToken &&
    sessionMarker,
  );

  if (!authenticated || !accessToken) {
    return NextResponse.json(
      {
        authenticated: false,
        password_change_required: false,
      },
      {
        status: 401,
        headers: {
          "Cache-Control":
            "no-store, no-cache, must-revalidate",
        },
      },
    );
  }

  let introspection: IntrospectionPayload = {};

  try {
    const response = await fetch(
      `${BACKEND_BASE_URL}/auth/introspection`,
      {
        method: "GET",
        headers: {
          Accept: "application/json",
          Authorization:
            `Bearer ${accessToken}`,
        },
        cache: "no-store",
      },
    );

    if (response.ok) {
      introspection =
        (await response.json()) as
          IntrospectionPayload;
    }
  } catch {
    introspection = {};
  }

  const role =
    typeof introspection.role === "string"
      ? introspection.role
      : "user";

  const subscriptionTier =
    typeof introspection.subscription_tier ===
      "string"
      ? introspection.subscription_tier
      : "free";

  const permissions =
    Array.isArray(introspection.permissions)
      ? introspection.permissions.filter(
          (
            permission,
          ): permission is string =>
            typeof permission === "string",
        )
      : [];

  return NextResponse.json(
    {
      authenticated: true,
      password_change_required:
        sessionMarker ===
          "password_change_required" ||
        introspection.must_change_password ===
          true,
      user_id:
        introspection.user_id ?? null,
      role,
      subscription_tier:
        subscriptionTier,
      permissions,
      is_administrative:
        introspection.is_administrative ===
          true,
      account_status:
        introspection.status ?? "active",
      is_active:
        introspection.is_active !== false,
    },
    {
      status: 200,
      headers: {
        "Cache-Control":
          "no-store, no-cache, must-revalidate",
      },
    },
  );
}
