import {
  NextRequest,
  NextResponse,
} from "next/server";

import {
  backendFetch,
} from "../../../../../lib/backendAuth";

import {
  validateCsrf,
  validateSameOrigin,
} from "../../../../../lib/requestSecurity";


export const dynamic = "force-dynamic";


async function responseJson(
  response: Response
): Promise<unknown> {
  try {
    return await response.json();
  } catch {
    return {
      detail:
        "Support service returned an invalid response.",
    };
  }
}


function rejectedRequest() {
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


export async function GET() {
  try {
    const response = await backendFetch(
      "/api/v1/support/tickets",
      {
        method: "GET",
        headers: {
          Accept: "application/json",
          "X-NeuroVest-Source":
            "frontend_user_support_tickets",
        },
      },
    );

    const body = await responseJson(
      response,
    );

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
          "Support tickets are temporarily unavailable.",
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


export async function POST(
  request: NextRequest,
) {
  if (
    !validateSameOrigin(request) ||
    !validateCsrf(request)
  ) {
    return rejectedRequest();
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
        headers: {
          "Cache-Control":
            "no-store, no-cache, must-revalidate",
        },
      },
    );
  }

  try {
    const response = await backendFetch(
      "/api/v1/support/tickets",
      {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
          "X-NeuroVest-Source":
            "frontend_user_support_ticket_create",
        },
        body: JSON.stringify(payload),
      },
    );

    const body = await responseJson(
      response,
    );

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
          "Support ticket creation is temporarily unavailable.",
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
