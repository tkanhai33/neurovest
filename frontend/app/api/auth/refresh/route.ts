import {
  NextRequest,
  NextResponse,
} from "next/server";

export const dynamic =
  "force-dynamic";

const BACKEND_BASE_URL =
  process.env.NEUROVEST_BACKEND_URL ??
  process.env.BACKEND_URL ??
  "http://127.0.0.1:8000";

type RefreshPayload = {
  access_token?: string;
  refresh_token?: string;
  csrf_token?: string;
  session_state?: string;
  access_expires_in?: number;
  refresh_expires_in?: number;
  [key: string]: unknown;
};

function appendBackendCookies(
  source: Response,
  target: NextResponse,
): number {
  const headers =
    source.headers as Headers & {
      getSetCookie?: () => string[];
    };

  const values =
    typeof headers.getSetCookie ===
    "function"
      ? headers.getSetCookie()
      : [];

  if (values.length > 0) {
    for (const value of values) {
      target.headers.append(
        "Set-Cookie",
        value,
      );
    }

    return values.length;
  }

  const combined =
    source.headers.get(
      "set-cookie",
    );

  if (combined) {
    target.headers.append(
      "Set-Cookie",
      combined,
    );

    return 1;
  }

  return 0;
}

function positiveMaxAge(
  value: unknown,
  fallback: number,
): number {
  if (
    typeof value === "number" &&
    Number.isFinite(value) &&
    value > 0
  ) {
    return Math.floor(value);
  }

  return fallback;
}

function installReturnedTokens(
  response: NextResponse,
  payload: RefreshPayload,
): void {
  const secure =
    process.env.NODE_ENV ===
    "production";

  const common = {
    path:
      "/",
    sameSite:
      "lax" as const,
    secure,
  };

  if (
    typeof payload.access_token ===
      "string" &&
    payload.access_token.length > 0
  ) {
    response.cookies.set(
      "neurovest_access",
      payload.access_token,
      {
        ...common,
        httpOnly:
          true,
        maxAge:
          positiveMaxAge(
            payload.access_expires_in,
            15 * 60,
          ),
      },
    );
  }

  if (
    typeof payload.refresh_token ===
      "string" &&
    payload.refresh_token.length > 0
  ) {
    response.cookies.set(
      "neurovest_refresh",
      payload.refresh_token,
      {
        ...common,
        httpOnly:
          true,
        maxAge:
          positiveMaxAge(
            payload.refresh_expires_in,
            30 * 24 * 60 * 60,
          ),
      },
    );
  }

  if (
    typeof payload.csrf_token ===
      "string" &&
    payload.csrf_token.length > 0
  ) {
    response.cookies.set(
      "neurovest_csrf",
      payload.csrf_token,
      {
        ...common,
        httpOnly:
          false,
        maxAge:
          positiveMaxAge(
            payload.refresh_expires_in,
            30 * 24 * 60 * 60,
          ),
      },
    );
  }

  response.cookies.set(
    "neurovest_session",
    (
      typeof payload.session_state ===
        "string" &&
      payload.session_state.length > 0
    )
      ? payload.session_state
      : "authenticated",
    {
      ...common,
      httpOnly:
        false,
      maxAge:
        positiveMaxAge(
          payload.refresh_expires_in,
          30 * 24 * 60 * 60,
        ),
    },
  );
}

export async function POST(
  request: NextRequest,
): Promise<NextResponse> {
  const refreshToken =
    request.cookies.get(
      "neurovest_refresh",
    )?.value ??
    "";

  const csrfToken =
    request.headers.get(
      "x-csrf-token",
    ) ??
    request.cookies.get(
      "neurovest_csrf",
    )?.value ??
    "";

  if (!refreshToken) {
    return NextResponse.json(
      {
        detail:
          "Refresh token is missing",
      },
      {
        status:
          401,
        headers: {
          "Cache-Control":
            "no-store",
        },
      },
    );
  }

  let backendResponse: Response;

  try {
    backendResponse =
      await fetch(
        `${BACKEND_BASE_URL}/auth/refresh`,
        {
          method:
            "POST",
          headers: {
            Accept:
              "application/json",
            "Content-Type":
              "application/json",
            Cookie:
              request.headers.get(
                "cookie",
              ) ??
              "",
            Origin:
              request.nextUrl.origin,
            Referer:
              `${request.nextUrl.origin}/user/chat`,
            ...(csrfToken
              ? {
                  "X-CSRF-Token":
                    csrfToken,
                }
              : {}),
          },
          body:
            JSON.stringify({
              refresh_token:
                refreshToken,
            }),
          cache:
            "no-store",
        },
      );
  } catch {
    return NextResponse.json(
      {
        detail:
          "Authentication service unavailable",
      },
      {
        status:
          503,
        headers: {
          "Cache-Control":
            "no-store",
        },
      },
    );
  }

  const raw =
    await backendResponse.text();

  let parsed:
    | RefreshPayload
    | null =
    null;

  if (raw) {
    try {
      parsed =
        JSON.parse(
          raw,
        ) as RefreshPayload;
    } catch {
      parsed =
        null;
    }
  }

  const response =
    new NextResponse(
      raw || null,
      {
        status:
          backendResponse.status,
        headers: {
          "Content-Type":
            backendResponse.headers.get(
              "content-type",
            ) ??
            "application/json",
          "Cache-Control":
            "no-store",
        },
      },
    );

  const backendCookieCount =
    appendBackendCookies(
      backendResponse,
      response,
    );

  if (
    backendResponse.ok &&
    backendCookieCount === 0 &&
    parsed
  ) {
    installReturnedTokens(
      response,
      parsed,
    );
  }

  return response;
}
