#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(".").resolve()
PAGE = ROOT / "frontend/app/page.tsx"

text = PAGE.read_text()

# Add workspace wrapper components without moving the protected floating chat widget.
if "function MarketWorkspacePanel()" not in text:
    component = r'''
function MarketWorkspacePanel({
  positions,
}: {
  positions: PortfolioPosition[];
}) {
  return (
    <>
      <section className="mt-8 grid gap-6 xl:grid-cols-2">
        <LivePriceCard />
        <StrategyDecisionCard />
      </section>

      <section className="mt-6 grid gap-6 xl:grid-cols-2">
        <RiskGateCard />
        <PositionsPanel positions={positions} />
      </section>

      <LiveMarketWatchlist />
    </>
  );
}

function GraphWorkspacePanel() {
  return (
    <>
      <LiveSystemGraphPanel />
    </>
  );
}

function ObservabilityWorkspacePanel() {
  return (
    <>
      <FrontendObservabilityPanel />
      <ObservabilityEventTimeline />
    </>
  );
}
'''
    text = text.replace(
        "function ChatTabPanel()",
        component + "\n\nfunction ChatTabPanel()",
        1,
    )

# Replace old always-on core dashboard panels with tabbed workspace panels.
old_core = '''      <section className="mt-8 grid gap-6 xl:grid-cols-2">
        <LivePriceCard />
        <StrategyDecisionCard />
      </section>

      <section className="mt-6 grid gap-6 xl:grid-cols-2">
        <RiskGateCard />
        <PositionsPanel positions={positions} />
      </section>
'''

text = text.replace(old_core, "")

# Replace old individual tab conditions with workspace wrappers.
text = text.replace(
'''      {(activeTab === "overview" || activeTab === "market") && (
        <LiveMarketWatchlist />
      )}

      {(activeTab === "overview" || activeTab === "graph") && (
        <LiveSystemGraphPanel />
      )}

      {(activeTab === "overview" || activeTab === "observability") && (
        <>
          <FrontendObservabilityPanel />
          <ObservabilityEventTimeline />
        </>
      )}

      {activeTab === "chat" && (
        <ChatTabPanel />
      )}''',
'''      {(activeTab === "overview" || activeTab === "market") && (
        <MarketWorkspacePanel positions={positions} />
      )}

      {(activeTab === "overview" || activeTab === "graph") && (
        <GraphWorkspacePanel />
      )}

      {(activeTab === "overview" || activeTab === "observability") && (
        <ObservabilityWorkspacePanel />
      )}

      {activeTab === "chat" && (
        <ChatTabPanel />
      )}'''
)

PAGE.write_text(text)
print("patched Phase 25C split dashboard panels into tab workspaces")
