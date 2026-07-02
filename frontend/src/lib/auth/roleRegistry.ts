export type UserRole = "user" | "admin" | "developer";

export const roleRegistryState = {
  phase: "phase_34b_role_visibility_registry_foundation",
  frontendOnly: true,
  backendCallsEnabled: false,
  authEnforcementEnabled: false,
  runtimeEnabled: false,
  brokerCallsEnabled: false,
  tradingEnabled: false
} as const;

export const userRoles = [
  { role: "user", label: "User", description: "Safe trading assistant view" },
  { role: "admin", label: "Admin", description: "Operations and safety oversight view" },
  { role: "developer", label: "Developer", description: "Architecture, diagnostics, and certification view" }
] as const;
