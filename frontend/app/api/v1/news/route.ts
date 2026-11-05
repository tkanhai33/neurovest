import {
  NextRequest,
  NextResponse,
} from "next/server";

import {
  backendFetch,
} from "../../../../lib/backendAuth";


export async function GET(
  request: NextRequest,
) {
  const search = request.nextUrl.search;

  const response = await backendFetch(
    `/api/v1/news${search}`,
    {
      method: "GET",
      cache: "no-store",
      headers: {
        "X-NeuroVest-Source":
          "frontend_news_intelligence",
      },
    },
  );

  const text = await response.text();

  let payload: unknown = null;

  if (text) {
    try {
      payload = JSON.parse(text);
    } catch {
      payload = {
        detail: text,
      };
    }
  }

  return NextResponse.json(
    payload,
    {
      status: response.status,
      headers: {
        "Cache-Control":
          "no-store",
      },
    },
  );
}
