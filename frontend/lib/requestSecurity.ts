import "server-only";

import { timingSafeEqual } from "node:crypto";

import { NextRequest } from "next/server";

import {
  CSRF_COOKIE,
} from "./sessionCookies";

function normalizedOrigin(
  value: string
): string | null {
  try {
    return new URL(value).origin;
  } catch {
    return null;
  }
}

function firstForwardedValue(
  value: string | null
): string | null {
  const first =
    value?.split(",")[0]?.trim();

  return first || null;
}

export function expectedRequestOrigin(
  request: NextRequest
): string | null {
  const host =
    firstForwardedValue(
      request.headers.get(
        "x-forwarded-host"
      )
    ) ||
    firstForwardedValue(
      request.headers.get("host")
    );

  if (!host) {
    return null;
  }

  const forwardedProtocol =
    firstForwardedValue(
      request.headers.get(
        "x-forwarded-proto"
      )
    );

  const protocol =
    forwardedProtocol ||
    request.nextUrl.protocol.replace(
      ":",
      ""
    );

  return normalizedOrigin(
    `${protocol}://${host}`
  );
}

export function validateSameOrigin(
  request: NextRequest
): boolean {
  const suppliedOrigin =
    normalizedOrigin(
      request.headers.get("origin") || ""
    );

  const expectedOrigin =
    expectedRequestOrigin(request);

  if (
    !suppliedOrigin ||
    !expectedOrigin
  ) {
    return false;
  }

  return (
    suppliedOrigin === expectedOrigin
  );
}

function constantTimeEqual(
  left: string,
  right: string
): boolean {
  const leftBuffer = Buffer.from(left);
  const rightBuffer = Buffer.from(right);

  if (
    leftBuffer.length !==
    rightBuffer.length
  ) {
    return false;
  }

  return timingSafeEqual(
    leftBuffer,
    rightBuffer
  );
}

export function validateCsrf(
  request: NextRequest
): boolean {
  const cookie =
    request.cookies.get(
      CSRF_COOKIE
    )?.value;

  const header =
    request.headers.get(
      "x-neurovest-csrf"
    );

  if (!cookie || !header) {
    return false;
  }

  return constantTimeEqual(
    cookie,
    header
  );
}

export function requiresCsrf(
  method: string
): boolean {
  return ![
    "GET",
    "HEAD",
    "OPTIONS",
  ].includes(
    method.toUpperCase()
  );
}
