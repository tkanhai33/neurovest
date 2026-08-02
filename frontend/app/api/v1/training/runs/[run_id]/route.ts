import {
  NextRequest,
  NextResponse,
} from "next/server";

import {
  backendFetch,
} from "../../../../../../lib/backendAuth";

export const dynamic =
  "force-dynamic";

type RouteContext = {
  params: Promise<{
    run_id: string;
  }>;
};

export async function GET(
  _request: NextRequest,
  context: RouteContext
) {
  try {
    const {
      run_id: runId,
    } = await context.params;

    const cleanRunId =
      String(runId ?? "").trim();

    if (!cleanRunId) {
      return NextResponse.json(
        {
          detail:
            "Training run ID is required",
        },
        {
          status: 400,
          headers: {
            "Cache-Control": "no-store",
          },
        }
      );
    }

    const response =
      await backendFetch(
        `/api/v1/training/runs/${encodeURIComponent(
          cleanRunId
        )}`,
        {
          method: "GET",
          cache: "no-store",
          headers: {
            Accept: "application/json",
            "X-Neurovest-Source":
              "frontend_chat_training_chip",
          },
        }
      );

    const rawBody =
      await response.text();

    let payload: unknown;

    try {
      payload =
        JSON.parse(rawBody);
    } catch {
      payload = {
        detail:
          rawBody ||
          "Backend returned a non-JSON training response.",
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
      }
    );
  } catch (error) {
    return NextResponse.json(
      {
        detail:
          "Training status is temporarily unavailable.",
        error:
          error instanceof Error
            ? error.message
            : String(error),
      },
      {
        status: 502,
        headers: {
          "Cache-Control": "no-store",
        },
      }
    );
  }
}
