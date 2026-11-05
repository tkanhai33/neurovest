import {
  backendFetch,
} from "../../../../../lib/backendAuth";


export async function GET() {
  try {
    const response =
      await backendFetch(
        "/api/v1/training/learning-summary",
        {
          method: "GET",

          headers: {
            "X-NeuroVest-Source":
              "frontend_learning_summary",
          },

          cache: "no-store",
        }
      );

    const body =
      await response.text();

    return new Response(
      body,
      {
        status:
          response.status,

        headers: {
          "Content-Type":
            response.headers.get(
              "content-type"
            ) ??
            "application/json",

          "Cache-Control":
            "no-store",
        },
      }
    );

  } catch {
    return Response.json(
      {
        detail:
          "Learning summary is unavailable.",
      },
      {
        status: 502,

        headers: {
          "Cache-Control":
            "no-store",
        },
      }
    );
  }
}
