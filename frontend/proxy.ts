import {
  NextRequest,
  NextResponse,
} from "next/server";

const SESSION_COOKIE =
  "neurovest_session";

const CSRF_COOKIE =
  "neurovest_csrf";

function firstForwardedValue(
  value: string | null
): string | null {
  const first =
    value?.split(",")[0]?.trim();

  return first || null;
}

function sameOrigin(
  request: NextRequest
): boolean {
  const supplied =
    request.headers.get("origin");

  const host =
    firstForwardedValue(
      request.headers.get(
        "x-forwarded-host"
      )
    ) ||
    firstForwardedValue(
      request.headers.get("host")
    );

  if (!supplied || !host) {
    return false;
  }

  const protocol =
    firstForwardedValue(
      request.headers.get(
        "x-forwarded-proto"
      )
    ) ||
    request.nextUrl.protocol.replace(
      ":",
      ""
    );

  try {
    return (
      new URL(supplied).origin ===
      new URL(
        `${protocol}://${host}`
      ).origin
    );
  } catch {
    return false;
  }
}

function validCsrf(
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

  return Boolean(
    cookie &&
    header &&
    cookie === header
  );
}

function forbidden(
  detail: string
): NextResponse {
  return NextResponse.json(
    {
      status: "forbidden",
      detail,
    },
    {
      status: 403,
      headers: {
        "Cache-Control":
          "no-store, no-cache, must-revalidate",
      },
    }
  );
}

const BACKEND_BASE_URL =
  process.env.NEUROVEST_BACKEND_URL ||
  process.env.BACKEND_URL ||
  "http://127.0.0.1:8000";

type RuntimeRole =
  | "user"
  | "admin"
  | "developer"
  | "owner";

type RuntimeIntrospection = {
  role?: unknown;
  status?: unknown;
  is_active?: unknown;
  must_change_password?: unknown;
};

function normalizeRuntimeRole(
  value: unknown
): RuntimeRole {
  const role = String(value ?? "")
    .trim()
    .toLowerCase();

  if (role === "owner") {
    return "owner";
  }

  if (
    role === "developer" ||
    role === "dev"
  ) {
    return "developer";
  }

  if (
    role === "admin" ||
    role === "administrator"
  ) {
    return "admin";
  }

  return "user";
}

async function resolveRuntimeRole(
  request: NextRequest
): Promise<{
  role: RuntimeRole;
  active: boolean;
  mustChangePassword: boolean;
} | null> {
  const accessToken =
    request.cookies.get(
      "neurovest_access"
    )?.value;

  if (!accessToken) {
    return null;
  }

  try {
    const response = await fetch(
      `${BACKEND_BASE_URL}/auth/introspection`,
      {
        method: "GET",
        headers: {
          Accept: "application/json",
          Authorization:
            `Bearer ${accessToken}`,
        },
        cache: "no-store",
      }
    );

    if (!response.ok) {
      return null;
    }

    const payload =
      (await response.json()) as
        RuntimeIntrospection;

    return {
      role: normalizeRuntimeRole(
        payload.role
      ),
      active:
        payload.is_active !== false &&
        String(
          payload.status ?? "active"
        ).toLowerCase() === "active",
      mustChangePassword:
        payload.must_change_password ===
        true,
    };
  } catch {
    return null;
  }
}

function loginRedirect(
  request: NextRequest
): NextResponse {
  const loginUrl =
    request.nextUrl.clone();

  loginUrl.pathname = "/login";
  loginUrl.search = "";
  loginUrl.searchParams.set(
    "next",
    request.nextUrl.pathname
  );

  return NextResponse.redirect(
    loginUrl,
    307
  );
}

function roleHomeRedirect(
  request: NextRequest,
  role: RuntimeRole
): NextResponse {
  const destination =
    request.nextUrl.clone();

  destination.pathname =
    role === "developer" ||
    role === "owner"
      ? "/dashboard"
      : role === "admin"
        ? "/admin"
        : "/user/dashboard";

  destination.search = "";

  return NextResponse.redirect(
    destination,
    307
  );
}

const INTERNAL_CHAT_API_PATH = "/api/v1/chat";
const INTERNAL_ADAPTIVE_API_PREFIX = "/api/v1/training/adaptive";

export async function proxy(
  request: NextRequest
) {

  /*
   * /api/v1/chat is an internal API route, not page navigation.
   * Its handler preserves authentication, CSRF forwarding,
   * backend authorization, and public chat controls.
   */
  if (
    request.nextUrl.pathname ===
      INTERNAL_CHAT_API_PATH ||
    request.nextUrl.pathname.startsWith(
      INTERNAL_ADAPTIVE_API_PREFIX
    )
  ) {
    return NextResponse.next();
  }

  /*
   * Stage 9D-B standalone restricted-session guard.
   * This executes before all normal proxy routing.
   */
  const stage9dbSessionState =
    request.cookies.get(
      SESSION_COOKIE
    )?.value;

  const stage9dbPasswordChangeRequired =
    stage9dbSessionState ===
      "password_change_required";

  const stage9dbAuthenticated =
    stage9dbSessionState ===
      "authenticated" ||
    stage9dbPasswordChangeRequired;

  const stage9dbPath =
    request.nextUrl.pathname;

  const stage9dbChangePage =
    stage9dbPath ===
      "/change-password";

  const stage9dbChangeApi =
    stage9dbPath.startsWith(
      "/api/auth/change-password"
    );

  if (
    stage9dbPasswordChangeRequired &&
    !stage9dbChangePage &&
    !stage9dbChangeApi
  ) {
    if (
      stage9dbPath.startsWith("/api/") ||
      stage9dbPath.startsWith("/admin")
    ) {
      return NextResponse.json(
        {
          status:
            "password_change_required",
          detail:
            "Password change required",
        },
        {
          status: 403,
          headers: {
            "Cache-Control":
              "no-store, no-cache, must-revalidate",
          },
        }
      );
    }

    const stage9dbChangeUrl =
      request.nextUrl.clone();

    stage9dbChangeUrl.pathname =
      "/change-password";

    stage9dbChangeUrl.search =
      "";

    return NextResponse.redirect(
      stage9dbChangeUrl,
      307
    );
  }

  if (
    stage9dbChangePage &&
    !stage9dbPasswordChangeRequired
  ) {
    const stage9dbDestination =
      request.nextUrl.clone();

    stage9dbDestination.pathname =
      stage9dbAuthenticated
        ? "/dashboard"
        : "/login";

    stage9dbDestination.search =
      "";

    return NextResponse.redirect(
      stage9dbDestination,
      307
    );
  }

  const path =
    request.nextUrl.pathname;

  const sessionState =
    request.cookies.get(
      SESSION_COOKIE
    )?.value;

  const authenticated =
    sessionState === "authenticated" ||
    sessionState ===
      "password_change_required";

  const passwordChangeRequired =
    sessionState ===
      "password_change_required";

  const isProtectedApi =
    path.startsWith("/api/v1/");

  const isAdmin =
    path.startsWith("/admin");

  const isDeveloperDashboard =
    path === "/dashboard" ||
    path.startsWith("/dashboard/");

  const isUserWorkspace =
    path === "/user" ||
    path.startsWith("/user/");

  const requiresRoleResolution =
    isAdmin ||
    isDeveloperDashboard ||
    isUserWorkspace;

  if (!authenticated) {
    if (isProtectedApi) {
      return NextResponse.json(
        {
          status: "unauthorized",
          detail:
            "Authentication required",
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

    const loginUrl =
      request.nextUrl.clone();

    loginUrl.pathname = "/login";
    loginUrl.searchParams.set(
      "next",
      path
    );

    return NextResponse.redirect(
      loginUrl
    );
  }

  const isPasswordChangePage =
    path.startsWith(
      "/change-password"
    );

  const isPasswordChangeApi =
    path.startsWith(
      "/api/auth/change-password"
    );

  if (
    passwordChangeRequired &&
    !isPasswordChangePage &&
    !isPasswordChangeApi
  ) {
    if (
      isProtectedApi ||
      isAdmin
    ) {
      return forbidden(
        "Password change required"
      );
    }

    const changeUrl =
      request.nextUrl.clone();

    changeUrl.pathname =
      "/change-password";

    changeUrl.search = "";

    return NextResponse.redirect(
      changeUrl
    );
  }

  if (
    isPasswordChangePage &&
    !passwordChangeRequired
  ) {
    const dashboardUrl =
      request.nextUrl.clone();

    dashboardUrl.pathname =
      authenticated
        ? "/dashboard"
        : "/login";

    dashboardUrl.search = "";

    return NextResponse.redirect(
      dashboardUrl
    );
  }

  if (requiresRoleResolution) {
    const runtimeIdentity =
      await resolveRuntimeRole(
        request
      );

    if (
      !runtimeIdentity ||
      !runtimeIdentity.active
    ) {
      return loginRedirect(request);
    }

    if (
      runtimeIdentity.mustChangePassword &&
      !isPasswordChangePage
    ) {
      const changeUrl =
        request.nextUrl.clone();

      changeUrl.pathname =
        "/change-password";

      changeUrl.search = "";

      return NextResponse.redirect(
        changeUrl,
        307
      );
    }

    const role =
      runtimeIdentity.role;

    const administrative =
      role === "admin" ||
      role === "developer" ||
      role === "owner";

    const developer =
      role === "developer" ||
      role === "owner";

    if (
      isAdmin &&
      !administrative
    ) {
      return roleHomeRedirect(
        request,
        role
      );
    }

    if (
      isDeveloperDashboard &&
      !developer
    ) {
      return roleHomeRedirect(
        request,
        role
      );
    }

    /*
     * Administrative, developer, and owner identities may inspect the
     * genuine lower-level User workspace without changing role truth.
     *
     * This is downward view access only:
     * - the authenticated principal remains unchanged;
     * - backend authorization remains server authoritative;
     * - no user impersonation is introduced;
     * - privileged routes still require their normal role.
     */
  }

  if (
    isProtectedApi &&
    ![
      "GET",
      "HEAD",
      "OPTIONS",
    ].includes(request.method)
  ) {
    if (
      !sameOrigin(request) ||
      !validCsrf(request)
    ) {
      return forbidden(
        "Request validation failed"
      );
    }
  }

  const response =
    NextResponse.next();

  response.headers.set(
    "Cache-Control",
    "no-store, no-cache, must-revalidate"
  );

  return response;
}

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/admin/:path*",
    "/change-password",
    "/api/auth/change-password",
    "/api/v1/:path*",
    "/user/:path*",
],
};
