import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/lib/auth/roleRegistry.ts",
  "src/lib/auth/dashboardPermissions.ts",
  "src/lib/auth/index.ts",
  "src/lib/auth/currentRolePreview.ts"
];

for (const file of required) {
  if (!existsSync(file)) throw new Error(`Missing role visibility registry file: ${file}`);
}

const forbidden = [
  "fetch(",
  "axios",
  "localStorage",
  "sessionStorage",
  "document.cookie",
  "submit_order",
  "place_order",
  "execute_trade",
  "broker_client",
  "useEffect("
];

for (const file of required) {
  const text = readFileSync(file, "utf8");
  for (const term of forbidden) {
    if (text.includes(term)) throw new Error(`Forbidden term ${term} found in ${file}`);
  }
}

const dashboardRequired = [
  "src/features/dashboard/components/RoleVisibilityPreviewPanel.tsx",
  "src/features/dashboard/components/RoleSurfaceSummaryPanel.tsx",
  "src/features/dashboard/components/RoleDashboardPreviewPanel.tsx",
  "src/features/dashboard/components/DashboardNavigationMatrixPanel.tsx",
  "src/components/Sidebar.tsx"
];

for (const file of dashboardRequired) {
  if (!existsSync(file)) throw new Error(`Missing role visibility dashboard file: ${file}`);
}


const requiredTerms = {
  "src/components/Sidebar.tsx": [
    "getVisibleFrontendRoutesForRole",
    "currentRolePreviewState.currentRole"
  ],
  "src/lib/auth/currentRolePreview.ts": [
    "phase_35a_role_aware_navigation_shell",
    "routeHidingEnabled: false",
    "backendAuthEnabled: false",
    "authEnforcementEnabled: false"
  ]
};

for (const [file, terms] of Object.entries(requiredTerms)) {
  const text = readFileSync(file, "utf8");
  for (const term of terms) {
    if (!text.includes(term)) throw new Error(`Required term ${term} missing from ${file}`);
  }
}

console.log("PASS: Role visibility registry verified.");
