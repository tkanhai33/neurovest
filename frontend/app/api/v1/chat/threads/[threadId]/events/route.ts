import "server-only";

import { backendFetch } from "../../../../../../../lib/backendAuth";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

// NEUROVEST_CHAT_FINDINGS_SSE_V2
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
      `/api/v1/chat/threads/${encodeURIComponent(threadId)}/events`,
      {
        method: "GET",
        headers: {
          Accept: "text/event-stream",
        },
      }
    );

    if (!upstream.ok) {
      return Response.json(
        { detail: "Chat stream unavailable." },
        {
          status: upstream.status,
          headers: {
            "Cache-Control": "no-store",
          },
        }
      );
    }

    const contentType =
      upstream.headers.get("content-type") ?? "";

    if (
      !upstream.body ||
      !contentType.includes("text/event-stream")
    ) {
      return Response.json(
        { detail: "Invalid upstream event stream." },
        { status: 502 }
      );
    }

    return new Response(upstream.body, {
      status: 200,
      headers: {
        "Content-Type": "text/event-stream; charset=utf-8",
        "Cache-Control": "no-cache, no-transform",
        "X-Accel-Buffering": "no",
      },
    });
  } catch {
    return Response.json(
      { detail: "Chat stream unavailable." },
      { status: 502 }
    );
  }
}
