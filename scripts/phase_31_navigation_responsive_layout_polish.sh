#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FRONTEND="$ROOT/frontend"

echo "========================================="
echo "PHASE 31 - NAVIGATION & RESPONSIVE LAYOUT POLISH"
echo "========================================="

cd "$ROOT"

BRANCH="$(git branch --show-current)"
if [ "$BRANCH" != "frontend-skeleton" ]; then
  echo "ERROR: Expected frontend-skeleton branch, got: $BRANCH"
  exit 1
fi

if [ -x "$ROOT/backend/.venv/bin/pytest" ]; then
  "$ROOT/backend/.venv/bin/pytest"
else
  pytest
fi

cat >> "$FRONTEND/src/styles/theme.css" <<'EOF'

.nv-nav-section {
  display: grid;
  gap: 8px;
}

.nv-nav-item-active {
  border-color: rgba(56, 189, 248, 0.55);
  background: rgba(56, 189, 248, 0.12);
}

.nv-breadcrumbs {
  color: var(--muted);
  font-size: 0.9rem;
  margin-bottom: 10px;
}

.nv-page-frame {
  display: grid;
  gap: 18px;
  max-width: 1440px;
  margin: 0 auto;
}

@media (max-width: 640px) {
  .nv-sidebar {
    padding: 18px;
  }

  .nv-nav {
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  }

  .nv-topbar {
    padding: 14px 18px;
  }
}
EOF

cat > "$FRONTEND/src/components/Sidebar.tsx" <<'EOF'
import { frontendRoutes } from "../lib/routes/routeRegistry";

export function Sidebar() {
  return (
    <aside className="nv-sidebar">
      <h1 className="nv-brand">NeuroVest</h1>
      <p className="nv-subtitle">Certified skeleton UI</p>
      <nav className="nv-nav nv-nav-section" aria-label="Primary navigation">
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
      <div className="nv-breadcrumbs">NeuroVest / Certified Skeleton</div>
      <strong>System Locked</strong>
      <span className="nv-muted" style={{ marginLeft: "12px" }}>
        {frontendSystemState.phase}
      </span>
    </header>
  );
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
        <div className="nv-content">
          <div className="nv-page-frame">{children}</div>
        </div>
      </section>
    </main>
  );
}
EOF

cat > "$FRONTEND/scripts/verify-navigation-responsive-layout-polish.mjs" <<'EOF'
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
EOF

(
  cd "$FRONTEND"
  node scripts/verify-navigation-responsive-layout-polish.mjs
  node scripts/verify-dashboard-visual-composition.mjs
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

cat > docs/contracts/PHASE_31_NAVIGATION_RESPONSIVE_LAYOUT_POLISH_CONTRACT.md <<'EOF'
# Phase 31 Navigation & Responsive Layout Polish Contract

Status: visual/navigation polish only.

Allowed:
- sidebar navigation polish
- breadcrumb shell
- responsive shell spacing
- page frame polish
- accessibility labels
- verification script
- certification artifact

Forbidden:
- backend API calls
- provider calls
- broker calls
- AI calls
- runtime execution
- scheduler logic
- trading logic
- business logic
EOF

cat > certification/phase_01/PHASE_31_NAVIGATION_RESPONSIVE_LAYOUT_POLISH_CERTIFICATION.md <<'EOF'
# Phase 31 Navigation & Responsive Layout Polish Certification

Status: PASS

Verified:
- sidebar navigation polish exists
- breadcrumb shell exists
- responsive layout polish exists
- page frame exists
- no backend calls
- no provider calls
- no broker calls
- no AI calls
- no runtime execution
- no trading logic

Result:
- Phase 31 navigation and responsive layout polish is certified.
EOF

git add .
git commit -m "Phase 31: Navigation responsive layout polish"

git tag -a phase-31-navigation-responsive-layout-polish \
  -m "Certified Phase 31 navigation responsive layout polish"

git push
git push --tags

echo "PASS: Phase 31 complete."
