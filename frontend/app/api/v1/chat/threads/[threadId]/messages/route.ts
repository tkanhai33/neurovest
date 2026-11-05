import "server-only";

import { backendFetch } from "../../../../../../../lib/backendAuth";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export async function GET(
  _request: Request,
  context: {
    params: Promise<{ threadId: string }>;
  }
) {
  const { threadId } = await context.params;

  if (
    !threadId ||
    threadId.length > 160 ||
    !/^[a-zA-Z0-9_-]+$/.test(threadId)
  ) {
    return Response.json(
      { detail: "Invalid chat thread." },
      { status: 400 }
    );
  }

  try {
    const upstream = await backendFetch(
      `/api/v1/chat/threads/${encodeURIComponent(threadId)}/messages`,
      {
        method: "GET",
        headers: { Accept: "application/json" },
      }
    );

    const body = await upstream.text();
    let payload: unknown;
    try {
      payload = JSON.parse(body);
    } catch {
      return Response.json(
        { detail: "Invalid chat history response." },
        { status: 502 }
      );
    }

    return Response.json(payload, {
      status: upstream.status,
      headers: { "Cache-Control": "no-store" },
    });
  } catch {
    return Response.json(
      { detail: "Chat history unavailable." },
      { status: 502 }
    );
  }
}
