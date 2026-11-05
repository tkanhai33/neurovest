import {
  NextRequest,
  NextResponse,
} from "next/server";

import {
  backendFetch,
} from "../../../../../../lib/backendAuth";

export const dynamic = "force-dynamic";

type RouteContext = {
  params: Promise<{
    notification_id: string;
    action: string;
  }>;
};

export async function PATCH(
  _request: NextRequest,
  context: RouteContext
) {
  try {
    const {
      notification_id: notificationId,
      action,
    } = await context.params;

    if (
      action !== "read" &&
      action !== "acknowledge"
    ) {
      return NextResponse.json(
        {
          status: "error",
          detail:
            "Unsupported notification action.",
        },
        {
          status: 404,
        }
      );
    }

    const normalizedId =
      encodeURIComponent(
        notificationId
      );

    const response = await backendFetch(
      `/api/v1/notifications/${normalizedId}/${action}`,
      {
        method: "PATCH",
        headers: {
          Accept: "application/json",
          "X-Neurovest-Source":
            "frontend_notifications",
        },
        cache: "no-store",
      }
    );

    const body =
      await response.text();

    let parsed: unknown;

    try {
      parsed = JSON.parse(
        body
      );
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
  } catch (error) {
    return NextResponse.json(
      {
        status: "error",
        detail:
          "Unable to update the NeuroVest notification.",
        error: String(error),
      },
      {
        status: 502,
      }
    );
  }
}
