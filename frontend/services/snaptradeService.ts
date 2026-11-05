import {
  csrfHeaders,
} from "../lib/clientCsrf";


type UnknownRecord = Record<
  string,
  unknown
>;


export type SnapTradeState = {
  registered?: boolean;
  connected?: boolean;
  connection_status?: string;
  last_sync_status?: string | null;
  last_synced_at?: string | null;
  trading_enabled?: boolean;
  read_only?: boolean;
  snaptrade_user_id?: string;

  detail?: string;
  status?: string;

  connection_url?: string;
  portal_url?: string;
  connection_portal_url?: string;
  redirect_url?: string;
  redirect_uri?: string;
  url?: string;

  [key: string]: unknown;
};


export type SnapTradeResponse = {
  status?: string;
  detail?: string;
  message?: string;

  registered?: boolean;
  connected?: boolean;
  connection_status?: string;
  last_sync_status?: string | null;
  last_synced_at?: string | null;
  trading_enabled?: boolean;
  read_only?: boolean;
  snaptrade_user_id?: string;

  connection_url?: string;
  portal_url?: string;
  connection_portal_url?: string;
  redirect_url?: string;
  redirect_uri?: string;
  url?: string;

  state?: SnapTradeState;
  credential?: SnapTradeState;
  connection?: SnapTradeState;

  data?: UnknownRecord;

  [key: string]: unknown;
};


function textValue(
  value: unknown
): string | null {
  return (
    typeof value === "string"
    &&
    value.trim()
  )
    ? value.trim()
    : null;
}


function objectValue(
  value: unknown
): UnknownRecord | null {
  return (
    value !== null
    &&
    typeof value === "object"
    &&
    !Array.isArray(
      value
    )
  )
    ? value as UnknownRecord
    : null;
}


async function parseResponse(
  response: Response,
  fallbackMessage: string,
): Promise<SnapTradeResponse> {
  let payload: SnapTradeResponse;

  try {
    payload =
      (
        await response.json()
      ) as SnapTradeResponse;

  } catch {

    payload = {
      status:
        "invalid_response",

      detail:
        "The SnapTrade endpoint returned a non-JSON response.",
    };
  }

  if (!response.ok) {
    throw new Error(
      (
        typeof payload.detail === "string"
        &&
        payload.detail
      )
      ||
      (
        typeof payload.message === "string"
        &&
        payload.message
      )
      ||
      fallbackMessage
    );
  }

  return payload;
}


export async function getSnapTradeStatus():
Promise<SnapTradeResponse> {
  const response =
    await fetch(
      "/api/v1/snaptrade/status",
      {
        method:
          "GET",

        credentials:
          "include",

        cache:
          "no-store",

        headers: {
          Accept:
            "application/json",
        },
      }
    );

  return parseResponse(
    response,
    "SnapTrade status is unavailable.",
  );
}


export async function registerSnapTradeUser():
Promise<SnapTradeResponse> {
  const response =
    await fetch(
      "/api/v1/snaptrade/register",
      {
        method:
          "POST",

        credentials:
          "include",

        cache:
          "no-store",

        headers: {
          Accept:
            "application/json",

          "Content-Type":
            "application/json",

          ...csrfHeaders(),
        },

        body:
          JSON.stringify(
            {}
          ),
      }
    );

  return parseResponse(
    response,
    "SnapTrade registration failed.",
  );
}


export async function createSnapTradeConnectionPortal():
Promise<SnapTradeResponse> {
  const response =
    await fetch(
      "/api/v1/snaptrade/connection-portal",
      {
        method:
          "POST",

        credentials:
          "include",

        cache:
          "no-store",

        headers: {
          Accept:
            "application/json",

          "Content-Type":
            "application/json",

          ...csrfHeaders(),
        },

        body:
          JSON.stringify(
            {}
          ),
      }
    );

  return parseResponse(
    response,
    "The read-only connection portal could not be created.",
  );
}


export async function synchronizeSnapTrade():
Promise<SnapTradeResponse> {
  const response =
    await fetch(
      "/api/v1/snaptrade/synchronize",
      {
        method:
          "POST",

        credentials:
          "include",

        cache:
          "no-store",

        headers: {
          Accept:
            "application/json",

          "Content-Type":
            "application/json",

          ...csrfHeaders(),
        },

        body:
          JSON.stringify(
            {}
          ),
      }
    );

  return parseResponse(
    response,
    "SnapTrade synchronization failed.",
  );
}


export function resolveConnectionPortalUrl(
  payload: SnapTradeResponse
): string | null {
  const data =
    objectValue(
      payload.data
    );

  const portal =
    objectValue(
      data?.portal
    );

  const candidates = [
    payload.connection_url,
    payload.portal_url,
    payload.connection_portal_url,
    payload.redirect_url,
    payload.redirect_uri,
    payload.url,

    payload.state?.connection_url,
    payload.state?.portal_url,
    payload.state?.connection_portal_url,
    payload.state?.redirect_url,
    payload.state?.redirect_uri,
    payload.state?.url,

    payload.connection?.connection_url,
    payload.connection?.portal_url,
    payload.connection?.connection_portal_url,
    payload.connection?.redirect_url,
    payload.connection?.redirect_uri,
    payload.connection?.url,

    textValue(
      data?.connection_url
    ),

    textValue(
      data?.portal_url
    ),

    textValue(
      data?.connection_portal_url
    ),

    textValue(
      data?.redirect_url
    ),

    textValue(
      data?.redirect_uri
    ),

    textValue(
      data?.url
    ),

    textValue(
      portal?.url
    ),
  ];

  for (
    const candidate
    of candidates
  ) {
    const value =
      textValue(
        candidate
      );

    if (value) {
      return value;
    }
  }

  return null;
}


export function resolveSnapTradeState(
  payload: SnapTradeResponse
): SnapTradeState {
  const data =
    objectValue(
      payload.data
    );

  const nestedState =
    objectValue(
      data?.state
    );

  return {
    ...(
      payload.credential
      ||
      {}
    ),

    ...(
      payload.connection
      ||
      {}
    ),

    ...(
      payload.state
      ||
      {}
    ),

    ...(
      nestedState
      ||
      {}
    ),

    registered:
      payload.registered
      ??
      payload.state?.registered
      ??
      payload.connection?.registered
      ??
      payload.credential?.registered
      ??
      (
        data?.registered
        ===
        true
      ),

    connected:
      payload.connected
      ??
      payload.state?.connected
      ??
      payload.connection?.connected
      ??
      (
        data?.connected
        ===
        true
      ),

    connection_status:
      payload.connection_status
      ??
      payload.state?.connection_status
      ??
      payload.connection?.connection_status
      ??
      textValue(
        data?.connection_status
      )
      ??
      undefined,

    last_sync_status:
      payload.last_sync_status
      ??
      payload.state?.last_sync_status
      ??
      payload.connection?.last_sync_status
      ??
      textValue(
        data?.last_sync_status
      ),

    last_synced_at:
      payload.last_synced_at
      ??
      payload.state?.last_synced_at
      ??
      payload.connection?.last_synced_at
      ??
      textValue(
        data?.last_synced_at
      ),

    snaptrade_user_id:
      payload.snaptrade_user_id
      ??
      payload.state?.snaptrade_user_id
      ??
      payload.connection?.snaptrade_user_id
      ??
      payload.credential?.snaptrade_user_id
      ??
      textValue(
        data?.snaptrade_user_id
      )
      ??
      undefined,

    trading_enabled:
      false,

    read_only:
      true,
  };
}


/**
 * Canonical browser-side SnapTrade read boundaries.
 *
 * Browser consumers call NeuroVest frontend API routes only.
 * Session/auth propagation remains owned by the Next.js proxy layer.
 */
export function fetchSnapTradeBalances(
  init?: RequestInit,
): Promise<Response> {
  return fetch(
    "/api/v1/snaptrade/balances",
    init,
  );
}


export function fetchSnapTradePortfolio(
  init?: RequestInit,
): Promise<Response> {
  return fetch(
    "/api/v1/snaptrade/portfolio",
    init,
  );
}
