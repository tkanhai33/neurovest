import { NextRequest } from "next/server";

import {
  proxyAuthenticated,
} from "./_proxy";

const BACKEND_PATH = "/api/v1/admin/users";

export const dynamic = "force-dynamic";

export async function GET(
  request: NextRequest,
) {
  return proxyAuthenticated(
    request,
    BACKEND_PATH,
    "GET",
  );
}
