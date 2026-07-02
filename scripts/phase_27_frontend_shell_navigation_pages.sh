#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FRONTEND="$ROOT/frontend"

echo "========================================="
echo "PHASE 27 - FRONTEND SHELL NAVIGATION PAGES"
echo "========================================="

cd "$ROOT"

BRANCH="$(git branch --show-current)"
if [ "$BRANCH" != "frontend-skeleton" ]; then
  echo "ERROR: Expected frontend-skeleton branch, got: $BRANCH"
  exit 1
fi

pytest

mkdir -p \
  "$FRONTEND/src/app/market-data" \
  "$FRONTEND/src/app/portfolio" \
  "$FRONTEND/src/app/research" \
  "$FRONTEND/src/app/strategy" \
  "$FRONTEND/src/app/risk" \
  "$FRONTEND/src/app/paper-trading" \
  "$FRONTEND/src/app/broker-integration" \
  "$FRONTEND/src/app/runtime" \
  "$FRONTEND/src/app/ai-chat" \
  "$FRONTEND/src/app/admin" \
  "$FRONTEND/src/app/settings"

cat > "$FRONTEND/src/app/market-data/page.tsx" <<'EOF'
import { MarketDataPanel } from "../../features/market_data/components";
import { AppShell } from "../../layouts/AppShell";

export default function MarketDataPage() {
  return (
    <AppShell>
      <MarketDataPanel />
    </AppShell>
  );
}
EOF

cat > "$FRONTEND/src/app/portfolio/page.tsx" <<'EOF'
import { PortfolioPanel } from "../../features/portfolio/components";
import { AppShell } from "../../layouts/AppShell";

export default function PortfolioPage() {
  return (
    <AppShell>
      <PortfolioPanel />
    </AppShell>
  );
}
EOF

cat > "$FRONTEND/src/app/research/page.tsx" <<'EOF'
import { ResearchPanel } from "../../features/research/components";
import { AppShell } from "../../layouts/AppShell";

export default function ResearchPage() {
  return (
    <AppShell>
      <ResearchPanel />
    </AppShell>
  );
}
EOF

cat > "$FRONTEND/src/app/strategy/page.tsx" <<'EOF'
import { StrategyPanel } from "../../features/strategy/components";
import { AppShell } from "../../layouts/AppShell";

export default function StrategyPage() {
  return (
    <AppShell>
      <StrategyPanel />
    </AppShell>
  );
}
EOF

cat > "$FRONTEND/src/app/risk/page.tsx" <<'EOF'
import { RiskPanel } from "../../features/risk/components";
import { AppShell } from "../../layouts/AppShell";

export default function RiskPage() {
  return (
    <AppShell>
      <RiskPanel />
    </AppShell>
  );
}
EOF

cat > "$FRONTEND/src/app/paper-trading/page.tsx" <<'EOF'
import { PaperTradingPanel } from "../../features/paper_trading/components";
import { AppShell } from "../../layouts/AppShell";

export default function PaperTradingPage() {
  return (
    <AppShell>
      <PaperTradingPanel />
    </AppShell>
  );
}
EOF

cat > "$FRONTEND/src/app/broker-integration/page.tsx" <<'EOF'
import { BrokerIntegrationPanel } from "../../features/broker_integration/components";
import { AppShell } from "../../layouts/AppShell";

export default function BrokerIntegrationPage() {
  return (
    <AppShell>
      <BrokerIntegrationPanel />
    </AppShell>
  );
}
EOF

cat > "$FRONTEND/src/app/runtime/page.tsx" <<'EOF'
import { RuntimePanel } from "../../features/runtime/components";
import { AppShell } from "../../layouts/AppShell";

export default function RuntimePage() {
  return (
    <AppShell>
      <RuntimePanel />
    </AppShell>
  );
}
EOF

cat > "$FRONTEND/src/app/ai-chat/page.tsx" <<'EOF'
import { NeuroChatPanel } from "../../features/ai_chat/components";
import { AppShell } from "../../layouts/AppShell";

export default function AiChatPage() {
  return (
    <AppShell>
      <NeuroChatPanel />
    </AppShell>
  );
}
EOF

cat > "$FRONTEND/src/app/admin/page.tsx" <<'EOF'
import { PageHeader, Card, StatusPill } from "../../components/ui";
import { AppShell } from "../../layouts/AppShell";

export default function AdminPage() {
  return (
    <AppShell>
      <PageHeader
        title="Admin"
        subtitle="Static admin shell. Governance controls, mutation, runtime, and broker unlocks are disabled."
      />
      <Card>
        <h2>Admin Controls Locked</h2>
        <StatusPill label="Governance Locked" />
        <StatusPill label="Runtime Unlock Disabled" />
        <StatusPill label="Broker Unlock Disabled" />
      </Card>
    </AppShell>
  );
}
EOF

cat > "$FRONTEND/src/app/settings/page.tsx" <<'EOF'
import { PageHeader, Card, StatusPill } from "../../components/ui";
import { AppShell } from "../../layouts/AppShell";

export default function SettingsPage() {
  return (
    <AppShell>
      <PageHeader
        title="Settings"
        subtitle="Static settings shell. No configuration writes occur during the skeleton phase."
      />
      <Card>
        <h2>Settings Locked</h2>
        <StatusPill label="Config Writes Disabled" />
        <StatusPill label="Secrets Disabled" />
        <StatusPill label="Provider Keys Disabled" />
      </Card>
    </AppShell>
  );
}
EOF

cat > "$FRONTEND/scripts/verify-shell-navigation-pages.mjs" <<'EOF'
import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/app/page.tsx",
  "src/app/market-data/page.tsx",
  "src/app/portfolio/page.tsx",
  "src/app/research/page.tsx",
  "src/app/strategy/page.tsx",
  "src/app/risk/page.tsx",
  "src/app/paper-trading/page.tsx",
  "src/app/broker-integration/page.tsx",
  "src/app/runtime/page.tsx",
  "src/app/ai-chat/page.tsx",
  "src/app/admin/page.tsx",
  "src/app/settings/page.tsx"
];

for (const file of required) {
  if (!existsSync(file)) throw new Error(`Missing shell navigation page: ${file}`);
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

console.log("PASS: Shell navigation pages verified.");
EOF

(
  cd "$FRONTEND"
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

cat > docs/contracts/PHASE_27_FRONTEND_SHELL_NAVIGATION_PAGES_CONTRACT.md <<'EOF'
# Phase 27 Frontend Shell Navigation Pages Contract

Status: skeleton only.

Allowed:
- static Next shell route pages
- route-to-panel rendering
- admin placeholder page
- settings placeholder page
- shell page verification
- certification artifact

Forbidden:
- backend API calls
- provider calls
- broker calls
- AI model calls
- runtime execution
- scheduler logic
- trading logic
- config writes
- secrets handling
- business logic
EOF

cat > certification/phase_01/PHASE_27_FRONTEND_SHELL_NAVIGATION_PAGES_CERTIFICATION.md <<'EOF'
# Phase 27 Frontend Shell Navigation Pages Certification

Status: PASS

Verified:
- dashboard route exists
- market data route exists
- portfolio route exists
- research route exists
- strategy route exists
- risk route exists
- paper trading route exists
- broker integration route exists
- runtime route exists
- Neuro chat route exists
- admin route exists
- settings route exists
- no backend calls
- no broker calls
- no AI calls
- no runtime execution
- no trading logic

Result:
- Phase 27 frontend shell navigation pages are certified.
EOF

git add .
git commit -m "Phase 27: Frontend shell navigation pages"

git tag -a phase-27-frontend-shell-navigation-pages \
  -m "Certified Phase 27 frontend shell navigation pages"

git push
git push --tags

echo "PASS: Phase 27 complete."
