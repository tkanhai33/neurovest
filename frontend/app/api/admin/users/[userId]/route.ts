import {
  NextRequest,
} from "next/server";

import {
  applyUserId,
  enforceMutationSecurity,
  proxyAuthenticated,
} from "../_proxy";

import type {
  RouteContext,
} from "../_proxy";

const BACKEND_PATH_TEMPLATE =
  "/api/v1/admin/users/{user_id}";

export const dynamic = "force-dynamic";

export async function GET(
  request: NextRequest,
  context: RouteContext,
) {
  const { userId } =
    await context.params;

  return proxyAuthenticated(
    request,
    applyUserId(
      BACKEND_PATH_TEMPLATE,
      userId,
    ),
    "GET",
  );
}

export async function DELETE(
  request: NextRequest,
  context: RouteContext,
) {
  const securityFailure =
    await enforceMutationSecurity(
      request,
    );

  if (securityFailure) {
    return securityFailure;
  }

  const { userId } =
    await context.params;

  return proxyAuthenticated(
    request,
    applyUserId(
      BACKEND_PATH_TEMPLATE,
      userId,
    ),
    "DELETE",
  );
}
