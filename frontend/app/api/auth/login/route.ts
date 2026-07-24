import {
  NextRequest,
  NextResponse,
} from "next/server";

import {
  clearBrowserTokens,
  setBrowserTokens,
  type BrowserTokenPair,
} from "../../../../lib/sessionCookies";

import {
  validateSameOrigin,
} from "../../../../lib/requestSecurity";

export const dynamic = "force-dynamic";

const BACKEND_BASE_URL =
  process.env.NEUROVEST_BACKEND_URL ||
  process.env.BACKEND_URL ||
  "http://127.0.0.1:8000";

type IntrospectionPayload = {
  role?: string;
  subscription_tier?: string;
  permissions?: string[];
};

function destinationForRole(
  roleValue: unknown,
): string {
  const role = String(roleValue ?? "")
    .trim()
    .toLowerCase();

  if (
    role === "developer" ||
    role === "dev" ||
    role === "owner"
  ) {
    return "/dashboard";
  }

  if (
    role === "admin" ||
    role === "administrator"
  ) {
    return "/admin";
  }

  return "/user/dashboard";
}

export async function POST(
  request: NextRequest,
) {
  if (!validateSameOrigin(request)) {
    return NextResponse.json(
      {
        status: "rejected",
        detail: "Request origin rejected",
      },
      {
        status: 403,
        headers: {
          "Cache-Control":
            "no-store, no-cache, must-revalidate",
        },
      },
    );
  }

  await clearBrowserTokens();

  let payload: {
    email?: unknown;
    password?: unknown;
  };

  try {
    payload = await request.json();
  } catch {
    return NextResponse.json(
      {
        status: "rejected",
        detail:
          "Enter your email address and password.",
      },
      {
        status: 400,
        headers: {
          "Cache-Control":
            "no-store, no-cache, must-revalidate",
        },
      },
    );
  }

  const email =
    typeof payload.email === "string"
      ? payload.email.trim()
      : "";

  const password =
    typeof payload.password === "string"
      ? payload.password
      : "";

  if (!email || !password) {
    return NextResponse.json(
      {
        status: "rejected",
        detail:
          "Enter your email address and password.",
      },
      {
        status: 400,
        headers: {
          "Cache-Control":
            "no-store, no-cache, must-revalidate",
        },
      },
    );
  }

  let backendResponse: Response;

  try {
    backendResponse = await fetch(
      `${BACKEND_BASE_URL}/auth/login`,
      {
        method: "POST",
        headers: {
          "Content-Type":
            "application/json",
          Accept: "application/json",
        },
        cache: "no-store",
        body: JSON.stringify({
          email,
          password,
        }),
      },
    );
  } catch {
    return NextResponse.json(
      {
        status: "unavailable",
        detail:
          "Sign-in is temporarily unavailable. Please try again.",
      },
      {
        status: 503,
        headers: {
          "Cache-Control":
            "no-store, no-cache, must-revalidate",
        },
      },
    );
  }

  let tokens: Partial<BrowserTokenPair> = {};

  try {
    tokens =
      (await backendResponse.json()) as
        Partial<BrowserTokenPair>;
  } catch {
    tokens = {};
  }

  if (
    !backendResponse.ok ||
    tokens.token_type?.toLowerCase() !==
      "bearer" ||
    !tokens.access_token ||
    !tokens.refresh_token ||
    tokens.access_token ===
      tokens.refresh_token
  ) {
    await clearBrowserTokens();

    return NextResponse.json(
      {
        status: "rejected",
        detail:
          "That email and password combination is incorrect.",
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
            `Bearer ${tokens.access_token}`,
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

  await setBrowserTokens({
    token_type: "bearer",
    access_token: tokens.access_token,
    refresh_token: tokens.refresh_token,
    password_change_required:
      tokens.password_change_required ===
        true,
  });

  const role =
    typeof introspection.role === "string"
      ? introspection.role
      : "user";

  const redirect =
    tokens.password_change_required === true
      ? "/change-password"
      : destinationForRole(role);

  return NextResponse.json(
    {
      status:
        tokens.password_change_required ===
        true
          ? "password_change_required"
          : "authenticated",
      redirect,
      role,
      subscription_tier:
        introspection.subscription_tier ??
        "free",
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
