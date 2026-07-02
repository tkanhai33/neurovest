#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FRONTEND="$ROOT/frontend"

echo "========================================="
echo "PHASE 29 - FRONTEND VISUAL POLISH FOUNDATION"
echo "========================================="

cd "$ROOT"

BRANCH="$(git branch --show-current)"
if [ "$BRANCH" != "frontend-skeleton" ]; then
  echo "ERROR: Expected frontend-skeleton branch, got: $BRANCH"
  exit 1
fi

pytest

cat > "$FRONTEND/src/styles/theme.css" <<'EOF'
:root {
  --bg: #0f172a;
  --bg-soft: #111827;
  --panel: #111827;
  --panel-soft: #1f2937;
  --panel-border: rgba(148, 163, 184, 0.18);
  --text: #e5e7eb;
  --muted: #9ca3af;
  --accent: #38bdf8;
  --safe: #22c55e;
  --locked: #f97316;
  --danger: #ef4444;
  --radius: 16px;
  --shadow: 0 20px 60px rgba(0, 0, 0, 0.24);
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  background:
    radial-gradient(circle at top left, rgba(56, 189, 248, 0.14), transparent 32rem),
    radial-gradient(circle at bottom right, rgba(34, 197, 94, 0.08), transparent 28rem),
    var(--bg);
  color: var(--text);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

a {
  color: inherit;
  text-decoration: none;
}

.nv-shell {
  display: grid;
  grid-template-columns: 280px 1fr;
  min-height: 100vh;
}

.nv-sidebar {
  background: rgba(17, 24, 39, 0.86);
  padding: 24px;
  border-right: 1px solid var(--panel-border);
  backdrop-filter: blur(14px);
}

.nv-brand {
  margin: 0;
  letter-spacing: -0.04em;
}

.nv-subtitle {
  color: var(--muted);
  margin: 8px 0 24px;
}

.nv-nav {
  display: grid;
  gap: 8px;
}

.nv-nav-item {
  color: var(--text);
  border: 1px solid var(--panel-border);
  border-radius: 12px;
  padding: 10px 12px;
  background: rgba(31, 41, 55, 0.45);
}

.nv-main {
  min-width: 0;
}

.nv-topbar {
  padding: 16px 24px;
  border-bottom: 1px solid var(--panel-border);
  background: rgba(15, 23, 42, 0.72);
  backdrop-filter: blur(14px);
  position: sticky;
  top: 0;
  z-index: 10;
}

.nv-content {
  padding: 28px;
}

.nv-grid {
  display: grid;
  gap: 18px;
}

.nv-card {
  background: rgba(17, 24, 39, 0.78);
  border: 1px solid var(--panel-border);
  border-radius: var(--radius);
  padding: 20px;
  box-shadow: var(--shadow);
}

.nv-panel {
  background: rgba(17, 24, 39, 0.78);
  border: 1px solid var(--panel-border);
  border-radius: var(--radius);
  padding: 20px;
}

.nv-metric {
  background: rgba(31, 41, 55, 0.72);
  border: 1px solid var(--panel-border);
  border-radius: 14px;
  padding: 16px;
}

.nv-muted {
  color: var(--muted);
}

.nv-badge {
  display: inline-flex;
  border: 1px solid var(--panel-border);
  border-radius: 999px;
  padding: 5px 11px;
  background: rgba(15, 23, 42, 0.48);
}

.nv-status {
  display: inline-flex;
  color: var(--safe);
  border: 1px solid rgba(34, 197, 94, 0.45);
  border-radius: 999px;
  padding: 5px 11px;
  margin-right: 8px;
  margin-bottom: 8px;
}

.nv-button {
  padding: 10px 14px;
  border-radius: 10px;
  border: 1px solid var(--panel-border);
  background: rgba(56, 189, 248, 0.12);
  color: var(--text);
  cursor: default;
}

@media (max-width: 860px) {
  .nv-shell {
    grid-template-columns: 1fr;
  }

  .nv-sidebar {
    border-right: 0;
    border-bottom: 1px solid var(--panel-border);
  }

  .nv-content {
    padding: 18px;
  }
}
EOF

cat > "$FRONTEND/src/layouts/AppShell.tsx" <<'EOF'
import { Sidebar } from "../components/Sidebar";
import { TopStatusBar } from "../components/TopStatusBar";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <main className="nv-shell">
      <Sidebar />
      <section className="nv-main">
        <TopStatusBar />
        <div className="nv-content">{children}</div>
      </section>
    </main>
  );
}
EOF

cat > "$FRONTEND/src/components/Sidebar.tsx" <<'EOF'
import { frontendRoutes } from "../lib/routes/routeRegistry";

export function Sidebar() {
  return (
    <aside className="nv-sidebar">
      <h1 className="nv-brand">NeuroVest</h1>
      <p className="nv-subtitle">Certified skeleton UI</p>
      <nav className="nv-nav">
        {frontendRoutes.map((route) => (
          <div key={route.key} className="nv-nav-item">
            {route.label} {route.locked ? "🔒" : ""}
          </div>
        ))}
      </nav>
    </aside>
  );
}
EOF

cat > "$FRONTEND/src/components/TopStatusBar.tsx" <<'EOF'
import { frontendSystemState } from "../lib/contracts/frontendSystemState";

export function TopStatusBar() {
  return (
    <header className="nv-topbar">
      <strong>System Locked</strong>
      <span className="nv-muted" style={{ marginLeft: "12px" }}>
        {frontendSystemState.phase}
      </span>
    </header>
  );
}
EOF

cat > "$FRONTEND/src/components/ui/Button.tsx" <<'EOF'
export function Button({ label }: { label: string }) {
  return <button className="nv-button">{label}</button>;
}
EOF

cat > "$FRONTEND/src/components/ui/Card.tsx" <<'EOF'
export function Card({ children }: { children: React.ReactNode }) {
  return <section className="nv-card">{children}</section>;
}
EOF

cat > "$FRONTEND/src/components/ui/Badge.tsx" <<'EOF'
export function Badge({ label }: { label: string }) {
  return <span className="nv-badge">{label}</span>;
}
EOF

cat > "$FRONTEND/src/components/ui/StatusPill.tsx" <<'EOF'
export function StatusPill({ label }: { label: string }) {
  return <span className="nv-status">{label}</span>;
}
EOF

cat > "$FRONTEND/src/components/ui/SectionPanel.tsx" <<'EOF'
export function SectionPanel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="nv-panel">
      <h2>{title}</h2>
      {children}
    </section>
  );
}
EOF

cat > "$FRONTEND/src/components/ui/MetricTile.tsx" <<'EOF'
export function MetricTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="nv-metric">
      <div className="nv-muted">{label}</div>
      <strong>{value}</strong>
    </div>
  );
}
EOF

cat > "$FRONTEND/scripts/verify-visual-polish-foundation.mjs" <<'EOF'
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
EOF

(
  cd "$FRONTEND"
  node scripts/verify-visual-polish-foundation.mjs
  node scripts/verify-shell-navigation-pages.mjs
  node scripts/verify-frontend-integration-registry.mjs
  node scripts/verify-runtime-ui-skeleton.mjs
  node scripts/verify-broker-integration-ui-skeleton.mjs
  node scripts/verify-paper-trading-ui-skeleton.mjs
  node scripts/verify-risk-ui-skeleton.mjs
  node scripts/verify-strategy-ui-skeleton.mjs
  node scripts/verify-research-ui-skeleton.mjs
  node scripts/verify-portfolio-ui-skeleton.mjs
  node scripts/verify-market-data-ui-skeleton.mjs
  node scripts/verify-neuro-chat-ui-skeleton.mjs
  node scripts/verify-dashboard-skeleton.mjs
  node scripts/verify-route-registry.mjs
  node scripts/verify-design-system-skeleton.mjs
  node scripts/verify-frontend-skeleton.mjs
)

cat > docs/contracts/PHASE_29_FRONTEND_VISUAL_POLISH_FOUNDATION_CONTRACT.md <<'EOF'
# Phase 29 Frontend Visual Polish Foundation Contract

Status: styling only.

Allowed:
- theme CSS polish
- shell spacing polish
- sidebar polish
- topbar polish
- card polish
- badge/status polish
- responsive shell rules
- verification script
- certification artifact

Forbidden:
- new business features
- backend API calls
- provider calls
- broker calls
- AI calls
- runtime execution
- scheduler logic
- trading logic
- config writes
- secrets handling
- business logic
EOF

cat > certification/phase_01/PHASE_29_FRONTEND_VISUAL_POLISH_FOUNDATION_CERTIFICATION.md <<'EOF'
# Phase 29 Frontend Visual Polish Foundation Certification

Status: PASS

Verified:
- theme polish exists
- responsive shell rules exist
- sidebar visual polish exists
- topbar visual polish exists
- design primitives use shared visual classes
- no backend calls
- no provider calls
- no broker calls
- no AI calls
- no runtime execution
- no trading logic

Result:
- Phase 29 frontend visual polish foundation is certified.
EOF

git add .
git commit -m "Phase 29: Frontend visual polish foundation"

git tag -a phase-29-frontend-visual-polish-foundation \
  -m "Certified Phase 29 frontend visual polish foundation"

git push
git push --tags

echo "PASS: Phase 29 complete."
