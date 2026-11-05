import {
  NextRequest,
  NextResponse,
} from "next/server";

import {
  backendFetch,
} from "../../../../lib/backendAuth";

export const dynamic = "force-dynamic";

function normalizedLimit(
  request: NextRequest
): number {
  const raw =
    request.nextUrl.searchParams.get("limit") ||
    "100";

  const parsed = Number.parseInt(
    raw,
    10
  );

  if (!Number.isFinite(parsed)) {
    return 100;
  }

  return Math.min(
    500,
    Math.max(
      1,
      parsed
    )
  );
}

async function proxyResponse(
  response: Response
): Promise<NextResponse> {
  const body = await response.text();

  let parsed: unknown;

  try {
    parsed = JSON.parse(body);
  } catch {
    parsed = {
      status: "error",
      detail:
        body ||
        "Backend returned a non-JSON notification response.",
    };
  }

  return NextResponse.json(
    parsed,
    {
      status: response.status,
      headers: {
        "Cache-Control":
          "no-store, no-cache, must-revalidate",
      },
    }
  );
}

export async function GET(
  request: NextRequest
) {
  try {
    const limit = normalizedLimit(
      request
    );

    const response = await backendFetch(
      `/api/v1/notifications?limit=${limit}`,
      {
        method: "GET",
        headers: {
          Accept: "application/json",
          "X-Neurovest-Source":
            "frontend_notifications",
        },
        cache: "no-store",
      }
    );

    return await proxyResponse(
      response
    );
  } catch (error) {
    return NextResponse.json(
      {
        status: "error",
        detail:
          "Unable to reach the NeuroVest notification backend.",
        error: String(error),
      },
      {
        status: 502,
      }
    );
  }
}

export async function POST(
  request: NextRequest
) {
  try {
    const payload =
      (await request.json()) as Record<
        string,
        unknown
      >;

    const response = await backendFetch(
      "/api/v1/notifications",
      {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type":
            "application/json",
          "X-Neurovest-Source":
            "frontend_notifications",
        },
        cache: "no-store",
        body: JSON.stringify(
          payload
        ),
      }
    );

    return await proxyResponse(
      response
    );
  } catch (error) {
    return NextResponse.json(
      {
        status: "error",
        detail:
          "Unable to create the NeuroVest notification.",
        error: String(error),
      },
      {
        status: 502,
      }
    );
  }
}
