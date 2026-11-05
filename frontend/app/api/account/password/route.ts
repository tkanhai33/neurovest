import { NextRequest } from "next/server";
import { accountSecurityRequest } from "../../../../lib/accountSecurityProxy";

export const dynamic = "force-dynamic";

export async function POST(request: NextRequest) {
  return accountSecurityRequest(request, "password");
}
