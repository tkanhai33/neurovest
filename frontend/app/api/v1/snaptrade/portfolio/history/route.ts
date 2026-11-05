import {
  backendFetch,
} from "../../../../../../lib/backendAuth";

export const dynamic =
  "force-dynamic";

export async function GET(
  request: Request,
) {
  try {
    const url =
      new URL(
        request.url,
      );

    const limit =
      url.searchParams.get(
        "limit",
      ) ?? "1000";

    const response =
      await backendFetch(
        `/api/v1/snaptrade/portfolio/history?limit=${encodeURIComponent(
          limit,
        )}`,
        {
          method:
            "GET",

          headers: {
            "X-NeuroVest-Source":
              "frontend_portfolio_performance_history",
          },
        },
      );

    return new Response(
      await response.text(),
      {
        status:
          response.status,

        headers: {
          "Content-Type":
            response.headers.get(
              "Content-Type",
            ) ??
            "application/json",

          "Cache-Control":
            "no-store",
        },
      },
    );

  } catch {

    return Response.json(
      {
        status:
          "unavailable",
      },
      {
        status:
          502,

        headers: {
          "Cache-Control":
            "no-store",
        },
      },
    );
  }
}
