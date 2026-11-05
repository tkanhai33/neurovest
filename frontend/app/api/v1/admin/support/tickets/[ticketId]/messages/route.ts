import {
  NextRequest,
  NextResponse,
} from "next/server";

import {
  backendFetch,
} from "../../../../../../../../lib/backendAuth";

import {
  validateCsrf,
  validateSameOrigin,
} from "../../../../../../../../lib/requestSecurity";


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
      },
    );
  }

  let body: unknown;

  try {
    body = await request.json();
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
      `/api/v1/admin/support/tickets/${encodeURIComponent(
        ticketId,
      )}/messages`,
      {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
          "X-NeuroVest-Source":
            "frontend_admin_support_message",
        },
        body: JSON.stringify(body),
      },
    );

    let payload: unknown;

    try {
      payload = await response.json();
    } catch {
      payload = {
        detail:
          "Administrative support service returned an invalid response.",
      };
    }

    return NextResponse.json(
      payload,
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
          "Administrative support messaging is temporarily unavailable.",
      },
      {
        status: 502,
      },
    );
  }
}
