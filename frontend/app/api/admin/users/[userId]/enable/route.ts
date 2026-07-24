import { NextRequest } from "next/server";

import {
  applyUserId,
  enforceMutationSecurity,
  proxyAuthenticated,
  readOptionalBody,
} from "../../_proxy";

import type {
  RouteContext,
} from "../../_proxy";

const BACKEND_PATH_TEMPLATE = "/api/v1/admin/users/{user_id}/enable";

export const dynamic = "force-dynamic";

export async function POST(
  request: NextRequest,
  context: RouteContext,
) {
  const securityFailure =
    await enforceMutationSecurity(request);

  if (securityFailure) {
    return securityFailure;
  }

  const { userId } = await context.params;

  const backendPath = applyUserId(
    BACKEND_PATH_TEMPLATE,
    userId,
  );

  const body = await readOptionalBody(request);

  return proxyAuthenticated(
    request,
    backendPath,
    "POST",
    body,
  );
}
