import type { UserRole } from "./roleRegistry";

export const currentRolePreviewState = {
  phase: "phase_35a_role_aware_navigation_shell",
  frontendOnly: true,
  previewOnly: true,
  backendAuthEnabled: false,
  authEnforcementEnabled: false,
  routeHidingEnabled: false,
  runtimeEnabled: false,
  brokerCallsEnabled: false,
  tradingEnabled: false,
  currentRole: "developer" as UserRole
} as const;
