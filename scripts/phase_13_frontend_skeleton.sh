#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FRONTEND="$ROOT/frontend"

echo "========================================="
echo "PHASE 13 - FRONTEND SKELETON"
echo "========================================="

cd "$ROOT"

echo "Running backend baseline tests..."
pytest

mkdir -p "$FRONTEND/src"/{app,components,layouts,providers,hooks,stores,styles,lib/{api,contracts,types},features/{dashboard,market_data,portfolio,research,strategy,risk,paper_trading,broker_integration,runtime,ai_chat,admin_control,settings}}

cat > "$FRONTEND/package.json" <<'EOF'
{
  "name": "neurovest-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "test:skeleton": "node scripts/verify-frontend-skeleton.mjs"
  },
  "dependencies": {},
  "devDependencies": {}
}
EOF

mkdir -p "$FRONTEND/scripts"

cat > "$FRONTEND/scripts/verify-frontend-skeleton.mjs" <<'EOF'
import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/app/page.tsx",
  "src/app/layout.tsx",
  "src/layouts/AppShell.tsx",
  "src/components/Sidebar.tsx",
  "src/components/TopStatusBar.tsx",
  "src/components/FeatureCard.tsx",
  "src/lib/api/client.ts",
  "src/lib/contracts/frontendSystemState.ts",
  "src/styles/theme.css"
];

for (const file of required) {
  if (!existsSync(file)) {
    throw new Error(`Missing required frontend skeleton file: ${file}`);
  }
}

const forbidden = [
  "fetch(",
  "axios",
  "submit_order",
  "place_order",
  "execute_trade",
  "ollama.chat",
  "ollama.generate",
  "broker_client"
];

for (const file of required) {
  const text = readFileSync(file, "utf8");
  for (const term of forbidden) {
    if (text.includes(term)) {
      throw new Error(`Forbidden frontend term ${term} found in ${file}`);
    }
  }
}

console.log("PASS: Frontend skeleton verified.");
EOF

cat > "$FRONTEND/src/lib/contracts/frontendSystemState.ts" <<'EOF'
export const frontendSystemState = {
  phase: "phase_13_frontend_skeleton",
  backendCallsEnabled: false,
  brokerCallsEnabled: false,
  marketDataCallsEnabled: false,
  aiModelCallsEnabled: false,
  tradingEnabled: false,
  runtimeEnabled: false
} as const;
EOF

cat > "$FRONTEND/src/lib/api/client.ts" <<'EOF'
export function apiClientPlaceholder(): string {
  return "phase_13_skeleton_only_no_api_calls";
}
EOF

cat > "$FRONTEND/src/styles/theme.css" <<'EOF'
:root {
  --bg: #0f172a;
  --panel: #111827;
  --panel-soft: #1f2937;
  --text: #e5e7eb;
  --muted: #9ca3af;
  --accent: #38bdf8;
  --safe: #22c55e;
  --locked: #f97316;
  --danger: #ef4444;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
EOF

cat > "$FRONTEND/src/app/layout.tsx" <<'EOF'
import "../styles/theme.css";

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
EOF

cat > "$FRONTEND/src/layouts/AppShell.tsx" <<'EOF'
import { Sidebar } from "../components/Sidebar";
import { TopStatusBar } from "../components/TopStatusBar";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <main style={{ display: "grid", gridTemplateColumns: "260px 1fr", minHeight: "100vh" }}>
      <Sidebar />
      <section>
        <TopStatusBar />
        <div style={{ padding: "24px" }}>{children}</div>
      </section>
    </main>
  );
}
EOF

cat > "$FRONTEND/src/components/Sidebar.tsx" <<'EOF'
const navItems = [
  "Dashboard",
  "Market Data",
  "Portfolio",
  "Research",
  "Strategy",
  "Risk",
  "Paper Trading",
  "Broker Integration",
  "Runtime",
  "Neuro Chat",
  "Admin",
  "Settings"
];

export function Sidebar() {
  return (
    <aside style={{ background: "var(--panel)", padding: "24px", borderRight: "1px solid var(--panel-soft)" }}>
      <h1 style={{ marginTop: 0 }}>NeuroVest</h1>
      <p style={{ color: "var(--muted)" }}>Skeleton UI</p>
      <nav style={{ display: "grid", gap: "10px" }}>
        {navItems.map((item) => (
          <div key={item} style={{ color: "var(--text)" }}>{item}</div>
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
    <header style={{ padding: "16px 24px", borderBottom: "1px solid var(--panel-soft)" }}>
      <strong>System Locked</strong>
      <span style={{ color: "var(--muted)", marginLeft: "12px" }}>
        {frontendSystemState.phase}
      </span>
    </header>
  );
}
EOF

cat > "$FRONTEND/src/components/FeatureCard.tsx" <<'EOF'
export function FeatureCard({
  title,
  status
}: {
  title: string;
  status: string;
}) {
  return (
    <section style={{ background: "var(--panel)", padding: "18px", borderRadius: "14px" }}>
      <h2 style={{ marginTop: 0 }}>{title}</h2>
      <p style={{ color: "var(--muted)" }}>{status}</p>
    </section>
  );
}
EOF

cat > "$FRONTEND/src/app/page.tsx" <<'EOF'
import { FeatureCard } from "../components/FeatureCard";
import { AppShell } from "../layouts/AppShell";

const features = [
  "Market Data",
  "Portfolio",
  "Research",
  "Strategy",
  "Risk",
  "Paper Trading",
  "Broker Integration",
  "Runtime",
  "Neuro Chat"
];

export default function HomePage() {
  return (
    <AppShell>
      <h1>NeuroVest Dashboard</h1>
      <p style={{ color: "var(--muted)" }}>
        Phase 13 frontend skeleton. All business logic, broker calls, AI calls, and runtime execution are locked.
      </p>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "16px" }}>
        {features.map((feature) => (
          <FeatureCard key={feature} title={feature} status="Skeleton only — locked" />
        ))}
      </div>
    </AppShell>
  );
}
EOF

for feature in dashboard market_data portfolio research strategy risk paper_trading broker_integration runtime ai_chat admin_control settings; do
  cat > "$FRONTEND/src/features/$feature/README.md" <<EOF
# $feature

Phase 13 frontend skeleton only.

Forbidden:
- backend API calls
- broker calls
- provider calls
- AI model calls
- runtime execution
- trading logic
EOF
done

cat > "$ROOT/docs/contracts/PHASE_13_FRONTEND_SKELETON_CONTRACT.md" <<'EOF'
# Phase 13 Frontend Skeleton Contract

Status: skeleton only.

Allowed:
- app shell
- layout
- navigation
- placeholder dashboard
- feature folders
- shared components
- frontend state contract
- API placeholder
- frontend skeleton verification

Forbidden:
- real backend API calls
- broker calls
- market data calls
- AI model calls
- runtime execution
- trading logic
- business logic
EOF

cat > "$ROOT/certification/phase_01/PHASE_13_FRONTEND_SKELETON_CERTIFICATION.md" <<'EOF'
# Phase 13 Frontend Skeleton Certification

Status: pending

Checks:
- frontend shell exists
- feature folders exist
- no real API calls
- no broker calls
- no AI calls
- no trading logic
EOF

echo
echo "Running frontend skeleton verification..."
cd "$FRONTEND"
node scripts/verify-frontend-skeleton.mjs

cd "$ROOT"
pytest

cat > "$ROOT/certification/phase_01/PHASE_13_FRONTEND_SKELETON_CERTIFICATION.md" <<'EOF'
# Phase 13 Frontend Skeleton Certification

Status: PASS

Checks:
- frontend shell exists
- feature folders exist
- no real API calls
- no broker calls
- no AI calls
- no trading logic
- backend tests pass

Result:
- Phase 13 frontend skeleton is certified.
EOF

echo
echo "========================================="
echo "PHASE 13 COMPLETE"
echo "========================================="
echo "PASS: Frontend skeleton created and certified."
