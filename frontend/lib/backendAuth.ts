import "server-only";

import {
  clearBrowserTokens,
  readBrowserTokens,
  setBrowserTokens,
  type BrowserTokenPair,
} from "./sessionCookies";

const BACKEND_BASE_URL =
  process.env.NEUROVEST_BACKEND_URL ||
  process.env.BACKEND_URL ||
  "http://127.0.0.1:8000";

function unauthorizedResponse(): Response {
  return Response.json(
    {
      status: "unauthorized",
      detail: "Authentication required",
    },
    {
      status: 401,
      headers: {
        "Cache-Control":
          "no-store, no-cache, must-revalidate",
      },
    }
  );
}

async function parseTokenPair(
  response: Response
): Promise<BrowserTokenPair | null> {
  let body: Partial<BrowserTokenPair>;

  try {
    body =
      (await response.json()) as Partial<BrowserTokenPair>;
  } catch {
    return null;
  }

  if (
    !response.ok ||
    body.token_type?.toLowerCase() !== "bearer" ||
    !body.access_token ||
    !body.refresh_token ||
    body.access_token === body.refresh_token
  ) {
    return null;
  }

  return {
    token_type: "bearer",
    access_token: body.access_token,
    refresh_token: body.refresh_token,
  };
}

function authenticatedHeaders(
  init: RequestInit,
  accessToken: string
): Headers {
  const headers = new Headers(init.headers);

  headers.set(
    "Authorization",
    `Bearer ${accessToken}`
  );

  if (!headers.has("Accept")) {
    headers.set("Accept", "application/json");
  }

  return headers;
}

async function refreshBrowserSession(
  refreshToken: string
): Promise<BrowserTokenPair | null> {
  const response = await fetch(
    `${BACKEND_BASE_URL}/auth/refresh`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      cache: "no-store",
      body: JSON.stringify({
        refresh_token: refreshToken,
      }),
    }
  );

  const pair = await parseTokenPair(response);

  if (!pair) {
    await clearBrowserTokens();
    return null;
  }

  await setBrowserTokens(pair);

  return pair;
}

export async function backendFetch(
  path: string,
  init: RequestInit = {}
): Promise<Response> {
  const {
    accessToken,
    refreshToken,
  } = await readBrowserTokens();

  if (!accessToken) {
    await clearBrowserTokens();
    return unauthorizedResponse();
  }

  const normalizedPath = path.startsWith("/")
    ? path
    : `/${path}`;

  const requestInit: RequestInit = {
    ...init,
    cache: "no-store",
    headers: authenticatedHeaders(
      init,
      accessToken
    ),
  };

  let response = await fetch(
    `${BACKEND_BASE_URL}${normalizedPath}`,
    requestInit
  );

  if (response.status !== 401) {
    return response;
  }

  if (!refreshToken) {
    await clearBrowserTokens();
    return unauthorizedResponse();
  }

  const replacement =
    await refreshBrowserSession(refreshToken);

  if (!replacement) {
    return unauthorizedResponse();
  }

  response = await fetch(
    `${BACKEND_BASE_URL}${normalizedPath}`,
    {
      ...init,
      cache: "no-store",
      headers: authenticatedHeaders(
        init,
        replacement.access_token
      ),
    }
  );

  if (response.status === 401) {
    await clearBrowserTokens();
  }

  return response;
}
