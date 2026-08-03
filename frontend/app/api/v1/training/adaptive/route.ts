import {
  NextRequest,
  NextResponse,
} from "next/server";

import {
  backendFetch,
} from "../../../../../lib/backendAuth";

export const dynamic =
  "force-dynamic";

async function responsePayload(
  response: Response
): Promise<unknown> {
  const rawBody =
    await response.text();

  try {
    return JSON.parse(rawBody);
  } catch {
    return {
      detail:
        rawBody ||
        "Backend returned a non-JSON adaptive training response.",
    };
  }
}

export async function POST(
  request: NextRequest
) {
  try {
    const incoming =
      await request.json()
        .catch(() => ({}));

    const payload =
      incoming &&
      typeof incoming === "object"
        ? incoming as Record<string, unknown>
        : {};

    const params =
      new URLSearchParams();

    const allowed = [
      "confidence_threshold",
      "maximum_rounds",
      "duration_seconds_per_round",
      "lookback_rows",
      "row_offset",
    ] as const;

    for (const key of allowed) {
      const value =
        payload[key];

      if (
        value !== undefined &&
        value !== null
      ) {
        params.set(
          key,
          String(value)
        );
      }
    }

    const query =
      params.toString();

    const response =
      await backendFetch(
        `/api/v1/training/adaptive${
          query ? `?${query}` : ""
        }`,
        {
          method: "POST",
          cache: "no-store",
          headers: {
            Accept: "application/json",
            "X-Neurovest-Source":
              "frontend_adaptive_training",
          },
        }
      );

    return NextResponse.json(
      await responsePayload(response),
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
          "Adaptive training could not be started.",
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

export async function GET(
  request: NextRequest
) {
  try {
    const limit =
      request.nextUrl.searchParams.get(
        "limit"
      );

    const query =
      limit
        ? `?limit=${encodeURIComponent(limit)}`
        : "";

    const response =
      await backendFetch(
        `/api/v1/training/adaptive${query}`,
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

    return NextResponse.json(
      await responsePayload(response),
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
          "Adaptive training controllers are temporarily unavailable.",
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
