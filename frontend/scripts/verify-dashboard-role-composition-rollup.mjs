import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/features/dashboard/components/DashboardShell.tsx",
  "src/features/dashboard/components/SystemFlowMapPanel.tsx",
  "src/features/dashboard/components/RoleVisibilityPreviewPanel.tsx",
  "src/features/dashboard/components/RoleSurfaceSummaryPanel.tsx",
  "src/features/dashboard/components/RoleDashboardPreviewPanel.tsx",
  "src/features/dashboard/components/DashboardNavigationMatrixPanel.tsx",
  "src/features/dashboard/components/DeveloperDashboardCompositionPanel.tsx",
  "src/features/dashboard/components/AdminDashboardCompositionPanel.tsx",
  "src/features/dashboard/components/UserDashboardCompositionPanel.tsx",
  "src/features/dashboard/components/BrainVisualizationLayoutPanel.tsx",
  "src/features/dashboard/components/BrainNodeRelationshipMatrixPanel.tsx",
  "src/features/dashboard/components/SystemLockPanel.tsx",
  "src/features/dashboard/components/StackOverviewPanel.tsx",
  "src/features/dashboard/components/PhaseProgressPanel.tsx",
  "src/features/dashboard/components/index.ts",
  "src/features/dashboard/contracts/dashboardState.ts",
  "src/lib/auth/roleRegistry.ts",
  "src/lib/auth/dashboardPermissions.ts",
  "src/lib/auth/currentRolePreview.ts",
  "src/lib/auth/index.ts",
  "src/lib/routes/navigationState.ts",
  "src/lib/routes/routeRegistry.ts",
  "src/components/Sidebar.tsx"
];

for (const file of required) {
  if (!existsSync(file)) {
    throw new Error(`Missing dashboard rollup file: ${file}`);
  }
}

const shell = readFileSync("src/features/dashboard/components/DashboardShell.tsx", "utf8");

const requiredPanels = [
  "SystemFlowMapPanel",
  "BrainVisualizationLayoutPanel",
  "BrainNodeRelationshipMatrixPanel",
  "RoleVisibilityPreviewPanel",
  "RoleSurfaceSummaryPanel",
  "RoleDashboardPreviewPanel",
  "DashboardNavigationMatrixPanel",
  "DeveloperDashboardCompositionPanel",
  "AdminDashboardCompositionPanel",
  "UserDashboardCompositionPanel",
  "PhaseProgressPanel",
  "SystemLockPanel",
  "StackOverviewPanel"
];

for (const panel of requiredPanels) {
  if (!shell.includes(panel)) {
    throw new Error(`DashboardShell missing rollup panel: ${panel}`);
  }
}

const requiredTerms = {
  "src/components/Sidebar.tsx": [
    "getVisibleFrontendRoutesForRole",
    "currentRolePreviewState.currentRole"
  ],
  "src/lib/auth/currentRolePreview.ts": [
    "phase_35a_role_aware_navigation_shell",
    "previewOnly: true",
    "backendAuthEnabled: false",
    "authEnforcementEnabled: false",
    "routeHidingEnabled: false",
    "tradingEnabled: false"
  ],
  "src/lib/routes/navigationState.ts": [
    "roleAwareNavigationState",
    "roleFilteringPreviewEnabled: true",
    "routeHidingEnabled: false",
    "backendAuthEnabled: false",
    "enforcementEnabled: false"
  ]
};

for (const [file, terms] of Object.entries(requiredTerms)) {
  const text = readFileSync(file, "utf8");
  for (const term of terms) {
    if (!text.includes(term)) {
      throw new Error(`Required term ${term} missing from ${file}`);
    }
  }
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
  "useEffect(",
  "setInterval(",
  "setTimeout("
];

for (const file of required) {
  const text = readFileSync(file, "utf8");
  for (const term of forbidden) {
    if (text.includes(term)) {
      throw new Error(`Forbidden term ${term} found in ${file}`);
    }
  }
}

console.log("PASS: Dashboard role composition rollup certified.");
