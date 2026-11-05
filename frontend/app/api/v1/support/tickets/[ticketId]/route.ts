import {
  NextResponse,
} from "next/server";

import {
  backendFetch,
} from "../../../../../../lib/backendAuth";


export const dynamic = "force-dynamic";


type RouteContext = {
  params: Promise<{
    ticketId: string;
  }>;
};


export async function GET(
  _request: Request,
  context: RouteContext,
) {
  const {
    ticketId,
  } = await context.params;

  try {
    const response = await backendFetch(
      `/api/v1/support/tickets/${encodeURIComponent(
        ticketId,
      )}`,
      {
        method: "GET",
        headers: {
          Accept: "application/json",
          "X-NeuroVest-Source":
            "frontend_user_support_ticket_detail",
        },
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
          "Support ticket detail is temporarily unavailable.",
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
