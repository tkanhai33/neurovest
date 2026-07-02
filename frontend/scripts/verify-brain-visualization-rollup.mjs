import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/features/dashboard/components/BrainVisualizationLayoutPanel.tsx",
  "src/features/dashboard/components/BrainNodeRelationshipMatrixPanel.tsx",
  "src/features/dashboard/components/BrainLockStateOverlayPanel.tsx",
  "src/features/dashboard/components/DashboardShell.tsx",
  "src/features/dashboard/components/index.ts",
  "src/features/dashboard/contracts/dashboardState.ts"
];

for (const file of required) {
  if (!existsSync(file)) {
    throw new Error(`Missing brain visualization file: ${file}`);
  }
}

const shell = readFileSync("src/features/dashboard/components/DashboardShell.tsx", "utf8");

const requiredPanels = [
  "BrainVisualizationLayoutPanel",
  "BrainNodeRelationshipMatrixPanel",
  "BrainLockStateOverlayPanel"
];

for (const panel of requiredPanels) {
  if (!shell.includes(panel)) {
    throw new Error(`DashboardShell missing brain visualization panel: ${panel}`);
  }
}

const requiredTerms = {
  "src/features/dashboard/components/BrainVisualizationLayoutPanel.tsx": [
    "Market Data",
    "Research",
    "Strategy",
    "Risk",
    "Runtime",
    "Broker",
    "Paper Trading",
    "Portfolio",
    "no backend calls",
    "runtime execution",
    "broker calls",
    "trading paths"
  ],
  "src/features/dashboard/components/BrainNodeRelationshipMatrixPanel.tsx": [
    "Market Data",
    "Research",
    "Research",
    "Strategy",
    "Strategy",
    "Risk",
    "Risk",
    "Runtime",
    "Runtime",
    "Broker",
    "Broker",
    "Paper Trading",
    "Paper Trading",
    "Portfolio",
    "Visual relationship"
  ],
  "src/features/dashboard/components/BrainLockStateOverlayPanel.tsx": [
    "Provider locked",
    "Research locked",
    "Strategy locked",
    "Risk locked",
    "Runtime locked",
    "Broker locked",
    "Paper engine locked",
    "Backend reads locked",
    "AI calls locked",
    "Preview only"
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

console.log("PASS: Brain visualization rollup certified.");
