export const navigationState = {
  phase: "phase_15_frontend_route_registry",
  routesImplemented: false,
  registryOnly: true,
  backendCallsEnabled: false,
  brokerCallsEnabled: false,
  tradingEnabled: false,
  aiCallsEnabled: false
} as const;

export const roleAwareNavigationState = {
  phase: "phase_35a_role_aware_navigation_shell",
  previewOnly: true,
  roleFilteringPreviewEnabled: true,
  routeHidingEnabled: false,
  backendAuthEnabled: false,
  enforcementEnabled: false
} as const;
