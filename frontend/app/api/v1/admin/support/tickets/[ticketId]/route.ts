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


async function proxy(
  ticketId: string,
  method: "GET" | "PATCH",
  body?: unknown,
) {
  const response = await backendFetch(
    `/api/v1/admin/support/tickets/${encodeURIComponent(
      ticketId,
    )}`,
    {
      method,
      headers: {
        Accept: "application/json",
        ...(body === undefined
          ? {}
          : {
              "Content-Type":
                "application/json",
            }),
        "X-NeuroVest-Source":
          "frontend_admin_support_ticket_detail",
      },
      body:
        body === undefined
          ? undefined
          : JSON.stringify(body),
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
}


export async function GET(
  _request: Request,
  context: RouteContext,
) {
  const {
    ticketId,
  } = await context.params;

  try {
    return await proxy(
      ticketId,
      "GET",
    );
  } catch {
    return NextResponse.json(
      {
        status: "unavailable",
        detail:
          "Administrative support ticket detail is temporarily unavailable.",
      },
      {
        status: 502,
      },
    );
  }
}


export async function PATCH(
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
    return await proxy(
      ticketId,
      "PATCH",
      body,
    );
  } catch {
    return NextResponse.json(
      {
        status: "unavailable",
        detail:
          "Administrative support update is temporarily unavailable.",
      },
      {
        status: 502,
      },
    );
  }
}
