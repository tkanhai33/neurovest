import type { FrontendRouteKey } from "../routes/routeRegistry";
import type { UserRole } from "./roleRegistry";

export const dashboardPermissionState = {
  phase: "phase_34b_dashboard_permission_registry",
  frontendOnly: true,
  roleFilteringEnabled: false,
  backendAuthEnabled: false,
  enforcementEnabled: false
} as const;

export const dashboardPermissions: Record<FrontendRouteKey, readonly UserRole[]> = {
  dashboard: ["user", "admin", "developer"],
  market_data: ["user", "admin", "developer"],
  portfolio: ["user", "admin", "developer"],
  research: ["user", "admin", "developer"],
  strategy: ["admin", "developer"],
  risk: ["admin", "developer"],
  paper_trading: ["user", "admin", "developer"],
  broker_integration: ["admin", "developer"],
  runtime: ["developer"],
  ai_chat: ["user", "admin", "developer"],
  admin_control: ["admin", "developer"],
  settings: ["user", "admin", "developer"]
} as const;

export function getVisibleRoutesForRole(role: UserRole) {
  return Object.entries(dashboardPermissions)
    .filter(([, roles]) => roles.includes(role))
    .map(([key]) => key as FrontendRouteKey);
}

export function getVisibleFrontendRoutesForRole<T extends { key: FrontendRouteKey }>(
  role: UserRole,
  routes: readonly T[]
): T[] {
  return routes.filter((route) => dashboardPermissions[route.key].includes(role));
}
