import { NextRequest } from "next/server";
import { accountSecurityRequest } from "../../../../lib/accountSecurityProxy";

export const dynamic = "force-dynamic";

export async function GET(request: NextRequest) {
  return accountSecurityRequest(request, "profile-read");
}

export async function PATCH(request: NextRequest) {
  return accountSecurityRequest(request, "profile-update");
}
