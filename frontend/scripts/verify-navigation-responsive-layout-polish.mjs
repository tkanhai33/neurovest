import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/styles/theme.css",
  "src/components/Sidebar.tsx",
  "src/components/TopStatusBar.tsx",
  "src/layouts/AppShell.tsx"
];

for (const file of required) {
  if (!existsSync(file)) throw new Error(`Missing navigation polish file: ${file}`);
}

const css = readFileSync("src/styles/theme.css", "utf8");
const expected = [
  ".nv-nav-section",
  ".nv-nav-item-active",
  ".nv-breadcrumbs",
  ".nv-page-frame",
  "@media (max-width: 640px)"
];

for (const item of expected) {
  if (!css.includes(item)) throw new Error(`Missing responsive/navigation polish: ${item}`);
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

console.log("PASS: Navigation and responsive layout polish verified.");
