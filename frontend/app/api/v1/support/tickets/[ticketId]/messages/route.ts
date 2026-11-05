import {
  NextRequest,
  NextResponse,
} from "next/server";

import {
  backendFetch,
} from "../../../../../../../lib/backendAuth";

import {
  validateCsrf,
  validateSameOrigin,
} from "../../../../../../../lib/requestSecurity";


export const dynamic = "force-dynamic";


type RouteContext = {
  params: Promise<{
    ticketId: string;
  }>;
};


export async function POST(
  request: NextRequest,
  context: RouteContext,
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
      },
    );
  }

  let payload: unknown;

  try {
    payload = await request.json();
  } catch {
    return NextResponse.json(
      {
        status: "rejected",
        detail: "Invalid JSON request body",
      },
      {
        status: 400,
      },
    );
  }

  const {
    ticketId,
  } = await context.params;

  try {
    const response = await backendFetch(
      `/api/v1/support/tickets/${encodeURIComponent(
        ticketId,
      )}/messages`,
      {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
          "X-NeuroVest-Source":
            "frontend_user_support_message",
        },
        body: JSON.stringify(payload),
      },
    );

    let body: unknown;

    try {
      body = await response.json();
    } catch {
      body = {
        detail:
          "Support service returned an invalid response.",
      };
    }

    return NextResponse.json(
      body,
      {
        status: response.status,
        headers: {
          "Cache-Control":
            "no-store, no-cache, must-revalidate",
        },
      },
    );
  } catch {
    return NextResponse.json(
      {
        status: "unavailable",
        detail:
          "Support messaging is temporarily unavailable.",
      },
      {
        status: 502,
        headers: {
          "Cache-Control":
            "no-store, no-cache, must-revalidate",
        },
      },
    );
  }
}
