import { backendFetch } from "../../../../../lib/backendAuth";

const FROZEN25_BACKEND_PATH =
  "/api/v1/strategy/model-inference/frozen25";

/**
 * Authenticated read-only bridge between NeuroVest's frontend/chat
 * boundary and the persisted Frozen25 inference endpoint.
 *
 * This adapter performs no model loading, training, execution,
 * database mutation, broker access, or runtime activation.
 *
 * Authentication/session behavior remains owned by backendFetch.
 */
export async function POST(
  request: Request,
): Promise<Response> {
  let payload: unknown;

  try {
    payload = await request.json();
  } catch {
    return Response.json(
      {
        detail: "Invalid JSON request body",
      },
      {
        status: 400,
      },
    );
  }

  const response = await backendFetch(
    FROZEN25_BACKEND_PATH,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
      cache: "no-store",
    },
  );

  const body = await response.text();

  return new Response(
    body,
    {
      status: response.status,
      headers: {
        "Content-Type":
          response.headers.get(
            "content-type",
          ) ?? "application/json",
        "Cache-Control": "no-store",
      },
    },
  );
}
