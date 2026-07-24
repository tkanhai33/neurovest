import {
  NextRequest,
  NextResponse,
} from "next/server";

import {
  validateSameOrigin,
} from "../../../../lib/requestSecurity";

export const dynamic = "force-dynamic";

const BACKEND_BASE_URL =
  process.env.NEUROVEST_BACKEND_URL ||
  process.env.BACKEND_URL ||
  "http://127.0.0.1:8000";

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
          "Registration could not be completed",
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
          "Registration could not be completed",
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
      `${BACKEND_BASE_URL}/auth/register`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
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
          "Registration service is unavailable",
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

  let responseBody: unknown = null;

  try {
    responseBody =
      await backendResponse.json();
  } catch {
    responseBody = null;
  }

  if (!backendResponse.ok) {
    let detail =
      "Registration could not be completed. Please try again.";

    if (
      backendResponse.status === 400 ||
      backendResponse.status === 409
    ) {
      detail =
        "An account with this email may already exist. Try signing in or use a different email.";
    } else if (
      backendResponse.status === 422
    ) {
      detail =
        "Check your email address and password requirements.";
    } else if (
      backendResponse.status === 429
    ) {
      detail =
        "Too many registration attempts. Please wait and try again.";
    } else if (
      backendResponse.status >= 500
    ) {
      detail =
        "Registration is temporarily unavailable. Please try again.";
    }

    return NextResponse.json(
      {
        status: "rejected",
        detail,
      },
      {
        status:
          backendResponse.status >= 400 &&
          backendResponse.status < 500
            ? backendResponse.status
            : 503,
        headers: {
          "Cache-Control":
            "no-store, no-cache, must-revalidate",
        },
      },
    );
  }

  return NextResponse.json(
    (
      responseBody &&
      typeof responseBody === "object"
    )
      ? responseBody
      : {
          status: "registered",
        },
    {
      status: 201,
      headers: {
        "Cache-Control":
          "no-store, no-cache, must-revalidate",
      },
    },
  );
}
