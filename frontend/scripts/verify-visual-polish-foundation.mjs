import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/styles/theme.css",
  "src/layouts/AppShell.tsx",
  "src/components/Sidebar.tsx",
  "src/components/TopStatusBar.tsx",
  "src/components/ui/Button.tsx",
  "src/components/ui/Card.tsx",
  "src/components/ui/Badge.tsx",
  "src/components/ui/StatusPill.tsx",
  "src/components/ui/SectionPanel.tsx",
  "src/components/ui/MetricTile.tsx"
];

for (const file of required) {
  if (!existsSync(file)) throw new Error(`Missing visual polish file: ${file}`);
}

const css = readFileSync("src/styles/theme.css", "utf8");
const expectedClasses = [
  ".nv-shell",
  ".nv-sidebar",
  ".nv-topbar",
  ".nv-content",
  ".nv-card",
  ".nv-metric",
  ".nv-badge",
  ".nv-status",
  "@media"
];

for (const cls of expectedClasses) {
  if (!css.includes(cls)) throw new Error(`Missing visual class: ${cls}`);
}

const forbidden = [
  "fetch(",
  "axios",
  "useEffect(",
  "submit_order",
  "place_order",
  "execute_trade",
  "broker_client",
  "ollama.chat",
  "ollama.generate",
  "setInterval",
  "setTimeout"
];

for (const file of required) {
  const text = readFileSync(file, "utf8");
  for (const term of forbidden) {
    if (text.includes(term)) throw new Error(`Forbidden term ${term} found in ${file}`);
  }
}

console.log("PASS: Visual polish foundation verified.");
