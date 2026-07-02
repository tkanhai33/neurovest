#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FRONTEND="$ROOT/frontend"

echo "========================================="
echo "PHASE 14 - DESIGN SYSTEM SKELETON"
echo "========================================="

cd "$ROOT"

BRANCH="$(git branch --show-current)"
if [ "$BRANCH" != "frontend-skeleton" ]; then
  echo "ERROR: Expected frontend-skeleton branch, got: $BRANCH"
  exit 1
fi

pytest

mkdir -p "$FRONTEND/src/components/ui" "$FRONTEND/src/lib/contracts"

cat > "$FRONTEND/src/components/ui/Button.tsx" <<'EOF'
export function Button({ label }: { label: string }) {
  return (
    <button style={{ padding: "10px 14px", borderRadius: "10px", border: "0", cursor: "default" }}>
      {label}
    </button>
  );
}
EOF

cat > "$FRONTEND/src/components/ui/Card.tsx" <<'EOF'
export function Card({ children }: { children: React.ReactNode }) {
  return (
    <section style={{ background: "var(--panel)", borderRadius: "14px", padding: "18px" }}>
      {children}
    </section>
  );
}
EOF

cat > "$FRONTEND/src/components/ui/Badge.tsx" <<'EOF'
export function Badge({ label }: { label: string }) {
  return (
    <span style={{ border: "1px solid var(--panel-soft)", borderRadius: "999px", padding: "4px 10px" }}>
      {label}
    </span>
  );
}
EOF

cat > "$FRONTEND/src/components/ui/StatusPill.tsx" <<'EOF'
export function StatusPill({ label }: { label: string }) {
  return (
    <span style={{ color: "var(--safe)", border: "1px solid var(--safe)", borderRadius: "999px", padding: "4px 10px" }}>
      {label}
    </span>
  );
}
EOF

cat > "$FRONTEND/src/components/ui/PageHeader.tsx" <<'EOF'
export function PageHeader({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <header>
      <h1>{title}</h1>
      <p style={{ color: "var(--muted)" }}>{subtitle}</p>
    </header>
  );
}
EOF

cat > "$FRONTEND/src/components/ui/SectionPanel.tsx" <<'EOF'
export function SectionPanel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section style={{ background: "var(--panel)", borderRadius: "16px", padding: "20px" }}>
      <h2>{title}</h2>
      {children}
    </section>
  );
}
EOF

cat > "$FRONTEND/src/components/ui/MetricTile.tsx" <<'EOF'
export function MetricTile({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ background: "var(--panel-soft)", borderRadius: "14px", padding: "16px" }}>
      <div style={{ color: "var(--muted)" }}>{label}</div>
      <strong>{value}</strong>
    </div>
  );
}
EOF

cat > "$FRONTEND/src/components/ui/index.ts" <<'EOF'
export { Badge } from "./Badge";
export { Button } from "./Button";
export { Card } from "./Card";
export { MetricTile } from "./MetricTile";
export { PageHeader } from "./PageHeader";
export { SectionPanel } from "./SectionPanel";
export { StatusPill } from "./StatusPill";
EOF

cat > "$FRONTEND/src/lib/contracts/designSystemState.ts" <<'EOF'
export const designSystemState = {
  phase: "phase_14_design_system_skeleton",
  componentsImplemented: false,
  visualPrimitivesOnly: true,
  backendCallsEnabled: false,
  brokerCallsEnabled: false,
  tradingEnabled: false,
  aiCallsEnabled: false
} as const;
EOF

cat > "$FRONTEND/scripts/verify-design-system-skeleton.mjs" <<'EOF'
import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/components/ui/Button.tsx",
  "src/components/ui/Card.tsx",
  "src/components/ui/Badge.tsx",
  "src/components/ui/StatusPill.tsx",
  "src/components/ui/PageHeader.tsx",
  "src/components/ui/SectionPanel.tsx",
  "src/components/ui/MetricTile.tsx",
  "src/components/ui/index.ts",
  "src/lib/contracts/designSystemState.ts"
];

for (const file of required) {
  if (!existsSync(file)) throw new Error(`Missing design system file: ${file}`);
}

const forbidden = [
  "fetch(",
  "axios",
  "submit_order",
  "place_order",
  "execute_trade",
  "ollama.chat",
  "broker_client"
];

for (const file of required) {
  const text = readFileSync(file, "utf8");
  for (const term of forbidden) {
    if (text.includes(term)) throw new Error(`Forbidden term ${term} found in ${file}`);
  }
}

console.log("PASS: Design system skeleton verified.");
EOF

(cd "$FRONTEND" && node scripts/verify-design-system-skeleton.mjs)

cat > docs/contracts/PHASE_14_DESIGN_SYSTEM_SKELETON_CONTRACT.md <<'EOF'
# Phase 14 Design System Skeleton Contract

Status: skeleton only.

Allowed:
- reusable UI primitives
- design-system state contract
- frontend verification script
- certification artifact

Forbidden:
- backend API calls
- broker calls
- AI calls
- trading logic
- business logic
EOF

cat > certification/phase_01/PHASE_14_DESIGN_SYSTEM_SKELETON_CERTIFICATION.md <<'EOF'
# Phase 14 Design System Skeleton Certification

Status: PASS

Verified:
- Button
- Card
- Badge
- StatusPill
- PageHeader
- SectionPanel
- MetricTile
- design system state contract
- no backend calls
- no broker calls
- no AI calls
- no trading logic

Result:
- Phase 14 design system skeleton is certified.
EOF

git add .
git commit -m "Phase 14: Design system skeleton"

git tag -a phase-14-design-system-skeleton \
  -m "Certified Phase 14 design system skeleton"

git push
git push --tags

echo "PASS: Phase 14 complete."
