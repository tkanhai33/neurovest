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
    refreshToken,
  } = await readBrowserTokens();

  try {
    if (refreshToken) {
      await fetch(
        `${BACKEND_BASE_URL}/auth/logout`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
          },
          cache: "no-store",
          body: JSON.stringify({
            refresh_token: refreshToken,
          }),
        }
      );
    }
  } finally {
    await clearBrowserTokens();
  }

  return NextResponse.json(
    {
      status: "logged_out",
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
