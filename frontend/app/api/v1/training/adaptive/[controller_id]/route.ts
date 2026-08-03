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
    controller_id: string;
  }>;
};

export async function GET(
  _request: NextRequest,
  context: RouteContext
) {
  try {
    const {
      controller_id: controllerId,
    } = await context.params;

    const cleanControllerId =
      String(
        controllerId ?? ""
      ).trim();

    if (!cleanControllerId) {
      return NextResponse.json(
        {
          detail:
            "Adaptive controller ID is required",
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
        `/api/v1/training/adaptive/${encodeURIComponent(
          cleanControllerId
        )}`,
        {
          method: "GET",
          cache: "no-store",
          headers: {
            Accept: "application/json",
            "X-Neurovest-Source":
              "frontend_adaptive_training",
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
          "Backend returned a non-JSON adaptive training response.",
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
          "Adaptive training status is temporarily unavailable.",
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
