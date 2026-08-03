import "server-only";

import {
  createHash,
  randomBytes,
} from "node:crypto";

import { cookies } from "next/headers";

export const ACCESS_COOKIE =
  "neurovest_access";

export const REFRESH_COOKIE =
  "neurovest_refresh";

export const SESSION_COOKIE =
  "neurovest_session";

export const CSRF_COOKIE =
  "neurovest_csrf";

export const PREFERENCE_SCOPE_COOKIE =
  "neurovest_preference_scope";

/**
 * Browser cookies are secure in production by default.
 *
 * Plain HTTP is permitted only when the controlled runtime explicitly sets:
 *
 *   NEUROVEST_COOKIE_SECURE=false
 *
 * Production deployments must omit the override or set it to true.
 */
const secureBrowserCookies =
  process.env.NEUROVEST_COOKIE_SECURE === "false"
    ? false
    : process.env.NODE_ENV === "production";

const privateOptions = {
  httpOnly: true,
  secure: secureBrowserCookies,
  sameSite: "strict" as const,
  path: "/",
};

const readableOptions = {
  httpOnly: false,
  secure: secureBrowserCookies,
  sameSite: "strict" as const,
  path: "/",
};

export type BrowserTokenPair = {
  token_type: string;
  access_token: string;
  refresh_token: string;
  password_change_required?: boolean;
};

function decodeSubject(
  accessToken: string
): string | null {
  try {
    const parts = accessToken.split(".");

    if (parts.length !== 3) {
      return null;
    }

    const payload = JSON.parse(
      Buffer.from(
        parts[1],
        "base64url"
      ).toString("utf-8")
    ) as {
      sub?: unknown;
    };

    return typeof payload.sub === "string"
      ? payload.sub
      : null;
  } catch {
    return null;
  }
}

function derivePreferenceScope(
  accessToken: string
): string {
  const subject =
    decodeSubject(accessToken);

  if (!subject) {
    return randomBytes(16).toString("hex");
  }

  return createHash("sha256")
    .update(
      `neurovest-ui-scope:${subject}`
    )
    .digest("hex")
    .slice(0, 32);
}

function createCsrfToken(): string {
  return randomBytes(32).toString("base64url");
}

export async function readBrowserTokens(): Promise<{
  accessToken: string | null;
  refreshToken: string | null;
  sessionMarker: string | null;
  csrfToken: string | null;
  preferenceScope: string | null;
}> {
  const store = await cookies();

  return {
    accessToken:
      store.get(ACCESS_COOKIE)?.value || null,
    refreshToken:
      store.get(REFRESH_COOKIE)?.value || null,
    sessionMarker:
      store.get(SESSION_COOKIE)?.value || null,
    csrfToken:
      store.get(CSRF_COOKIE)?.value || null,
    preferenceScope:
      store.get(
        PREFERENCE_SCOPE_COOKIE
      )?.value || null,
  };
}

export async function setBrowserTokens(
  pair: BrowserTokenPair
): Promise<void> {
  const store = await cookies();

  store.set(
    ACCESS_COOKIE,
    pair.access_token,
    privateOptions
  );

  store.set(
    REFRESH_COOKIE,
    pair.refresh_token,
    privateOptions
  );

  store.set(
    SESSION_COOKIE,
    pair.password_change_required
      ? "password_change_required"
      : "authenticated",
    privateOptions
  );

  store.set(
    CSRF_COOKIE,
    createCsrfToken(),
    readableOptions
  );

  store.set(
    PREFERENCE_SCOPE_COOKIE,
    derivePreferenceScope(
      pair.access_token
    ),
    readableOptions
  );
}

export async function ensureCsrfCookie(): Promise<string> {
  const store = await cookies();

  const existing =
    store.get(CSRF_COOKIE)?.value;

  if (existing) {
    return existing;
  }

  const created = createCsrfToken();

  store.set(
    CSRF_COOKIE,
    created,
    readableOptions
  );

  return created;
}

export async function clearBrowserTokens(): Promise<void> {
  const store = await cookies();

  for (const [
    name,
    options,
  ] of [
    [ACCESS_COOKIE, privateOptions],
    [REFRESH_COOKIE, privateOptions],
    [SESSION_COOKIE, privateOptions],
    [CSRF_COOKIE, readableOptions],
    [
      PREFERENCE_SCOPE_COOKIE,
      readableOptions,
    ],
  ] as const) {
    store.set(name, "", {
      ...options,
      maxAge: 0,
    });
  }
}
