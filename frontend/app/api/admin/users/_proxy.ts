import { NextRequest, NextResponse } from "next/server";

import {
  backendFetch,
} from "@/lib/backendAuth";

import {
  validateCsrf,
  validateSameOrigin,
} from "../../../../lib/requestSecurity";

type RouteContext = {
  params: Promise<{
    userId: string;
  }>;
};

function sanitizeUserId(userId: string): string {
  const normalized = userId.trim();

  if (
    normalized.length === 0 ||
    normalized.length > 128 ||
    !/^[A-Za-z0-9_.:@-]+$/.test(normalized)
  ) {
    throw new Error("Invalid user identifier");
  }

  return encodeURIComponent(normalized);
}

function applyUserId(
  template: string,
  userId: string,
): string {
  const encoded = sanitizeUserId(userId);

  const replacements = [
    "{user_id}",
    "{userId}",
    "{id}",
  ];

  for (const marker of replacements) {
    if (template.includes(marker)) {
      return template.replace(marker, encoded);
    }
  }

  return `${template.replace(/\/$/, "")}/${encoded}`;
}

async function readOptionalBody(
  request: NextRequest,
): Promise<string | undefined> {
  const contentLength = request.headers.get("content-length");

  if (contentLength === "0") {
    return undefined;
  }

  const text = await request.text();

  return text.length > 0
    ? text
    : undefined;
}

async function passThrough(
  response: Response,
): Promise<NextResponse> {
  const body = await response.text();
  const headers = new Headers();

  const contentType = response.headers.get("content-type");

  if (contentType) {
    headers.set("content-type", contentType);
  }

  headers.set("cache-control", "no-store");

  return new NextResponse(
    body.length > 0
      ? body
      : null,
    {
      status: response.status,
      headers,
    },
  );
}

async function enforceMutationSecurity(
  request: NextRequest,
): Promise<NextResponse | null> {
  const originValid =
    await validateSameOrigin(request);

  if (!originValid) {
    return NextResponse.json(
      {
        detail: "Invalid request origin",
      },
      {
        status: 403,
        headers: {
          "cache-control": "no-store",
        },
      },
    );
  }

  const csrfValid =
    await validateCsrf(request);

  if (!csrfValid) {
    return NextResponse.json(
      {
        detail: "Invalid CSRF token",
      },
      {
        status: 403,
        headers: {
          "cache-control": "no-store",
        },
      },
    );
  }

  return null;
}

async function proxyAuthenticated(
  request: NextRequest,
  backendPath: string,
  method: "GET" | "POST" | "DELETE",
  body?: string,
): Promise<NextResponse> {
  const headers = new Headers();

  if (body !== undefined) {
    headers.set(
      "content-type",
      request.headers.get("content-type")
        ?? "application/json",
    );
  }

  const response = await backendFetch(
    backendPath,
    {
      method,
      headers,
      body,
      cache: "no-store",
    },
  );

  return passThrough(response);
}

export {
  applyUserId,
  enforceMutationSecurity,
  proxyAuthenticated,
  readOptionalBody,
};

export type {
  RouteContext,
};
