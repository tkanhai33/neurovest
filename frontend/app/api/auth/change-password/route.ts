import {
  NextRequest,
  NextResponse,
} from "next/server";

import {
  clearBrowserTokens,
  readBrowserTokens,
} from "../../../../lib/sessionCookies";

import {
  validateCsrf,
  validateSameOrigin,
} from "../../../../lib/requestSecurity";

export const dynamic = "force-dynamic";

const BACKEND_BASE_URL =
  process.env.NEUROVEST_BACKEND_URL ||
  process.env.BACKEND_URL ||
  "http://127.0.0.1:8000";

export async function POST(
  request: NextRequest
) {
  if (
    !validateSameOrigin(request) ||
    !validateCsrf(request)
  ) {
    return NextResponse.json(
      {
        status: "rejected",
        detail: "Request validation failed",
      },
      {
        status: 403,
        headers: {
          "Cache-Control":
            "no-store, no-cache, must-revalidate",
        },
      }
    );
  }

  const {
    accessToken,
    sessionMarker,
  } = await readBrowserTokens();

  if (
    !accessToken ||
    sessionMarker !==
      "password_change_required"
  ) {
    return NextResponse.json(
      {
        status: "unauthorized",
        detail:
          "Password-change session required",
      },
      {
        status: 401,
      }
    );
  }

  let payload: {
    current_password?: unknown;
    new_password?: unknown;
  };

  try {
    payload = await request.json();
  } catch {
    return NextResponse.json(
      {
        status: "rejected",
        detail:
          "Password replacement was rejected",
      },
      {
        status: 400,
      }
    );
  }

  const response = await fetch(
    `${BACKEND_BASE_URL}/auth/change-required-password`,
    {
      method: "POST",
      headers: {
        Authorization:
          `Bearer ${accessToken}`,
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      cache: "no-store",
      body: JSON.stringify(payload),
    }
  );

  let body: unknown;

  try {
    body = await response.json();
  } catch {
    body = {
      status: "rejected",
      detail:
        "Password replacement was rejected",
    };
  }

  if (!response.ok) {
    return NextResponse.json(
      body,
      {
        status: response.status,
        headers: {
          "Cache-Control":
            "no-store, no-cache, must-revalidate",
        },
      }
    );
  }

  await clearBrowserTokens();

  return NextResponse.json(
    {
      status: "password_changed",
      redirect: "/login",
    },
    {
      status: 200,
      headers: {
        "Cache-Control":
          "no-store, no-cache, must-revalidate",
      },
    }
  );
}
