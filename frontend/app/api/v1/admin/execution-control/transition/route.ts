import {
  NextRequest,
  NextResponse,
} from "next/server";

import {
  backendFetch,
} from "../../../../../../lib/backendAuth";

export const dynamic = "force-dynamic";

type TransitionPayload = {
  mode?: unknown;
  reason?: unknown;
};

const ALLOWED_MODES = new Set([
  "SAFE",
  "SIMULATION",
  "LOCKED",
]);

function errorResponse(
  detail: string,
  status: number
) {
  return NextResponse.json(
    {
      status: "error",
      detail,
    },
    {
      status,
      headers: {
        "Cache-Control":
          "no-store, no-cache, must-revalidate",
      },
    }
  );
}

export async function POST(
  request: NextRequest
) {
  let body: TransitionPayload;

  try {
    body =
      (await request.json()) as TransitionPayload;
  } catch {
    return errorResponse(
      "A valid JSON transition request is required.",
      400
    );
  }

  const mode =
    typeof body.mode === "string"
      ? body.mode.trim().toUpperCase()
      : "";

  const reason =
    typeof body.reason === "string"
      ? body.reason.trim()
      : "";

  if (!ALLOWED_MODES.has(mode)) {
    return errorResponse(
      "Mode must be SAFE, SIMULATION, or LOCKED.",
      400
    );
  }

  if (
    reason.length < 3 ||
    reason.length > 500
  ) {
    return errorResponse(
      "A transition reason between 3 and 500 characters is required.",
      400
    );
  }

  try {
    const response = await backendFetch(
      "/api/v1/admin/execution-control/transition",
      {
        method: "POST",
        cache: "no-store",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
          "X-Neurovest-Source":
            "frontend_execution_control",
        },
        body: JSON.stringify({
          mode,
          reason,
        }),
      }
    );

    const rawBody = await response.text();

    let payload: unknown;

    try {
      payload = JSON.parse(rawBody);
    } catch {
      return errorResponse(
        rawBody ||
          "Backend returned a non-JSON transition response.",
        response.status || 502
      );
    }

    return NextResponse.json(
      payload,
      {
        status: response.status,
        headers: {
          "Cache-Control":
            "no-store, no-cache, must-revalidate",
        },
      }
    );
  } catch (error) {
    return NextResponse.json(
      {
        status: "error",
        detail:
          "Unable to reach the NeuroVest execution-control backend.",
        error:
          error instanceof Error
            ? error.message
            : String(error),
      },
      {
        status: 502,
        headers: {
          "Cache-Control":
            "no-store, no-cache, must-revalidate",
        },
      }
    );
  }
}
