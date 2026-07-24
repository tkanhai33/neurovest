#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(".").resolve()
PAGE = ROOT / "frontend/app/page.tsx"

text = PAGE.read_text()

if 'type DashboardTab =' not in text:
    imports_end = text.find("\n\nfunction")
    injection = '''

type DashboardTab =
  | "overview"
  | "market"
  | "graph"
  | "observability"
  | "chat";
'''
    text = text[:imports_end] + injection + text[imports_end:]

if 'function DashboardTabNavigation(' not in text:
    component = r'''
function DashboardTabNavigation({
  activeTab,
  setActiveTab,
}: {
  activeTab: DashboardTab;
  setActiveTab: (tab: DashboardTab) => void;
}) {
  const tabs: DashboardTab[] = [
    "overview",
    "market",
    "graph",
    "observability",
    "chat",
  ];

  return (
    <section className="mb-6 rounded-2xl border border-cyan-400/20 bg-slate-950/80 p-3">
      <div className="flex flex-wrap gap-2">
        {tabs.map((tab) => (
          <button
            key={tab}
            type="button"
            onClick={() => setActiveTab(tab)}
            className={
              activeTab === tab
                ? "rounded-xl border border-cyan-300 bg-cyan-500/20 px-4 py-2 text-sm font-bold text-cyan-100"
                : "rounded-xl border border-slate-700 bg-slate-900/80 px-4 py-2 text-sm text-slate-300"
            }
          >
            {tab.toUpperCase()}
          </button>
        ))}
      </div>
    </section>
  );
}
'''
    text = text.replace(
        "function FloatingChatWidget()",
        component + "\n\nfunction FloatingChatWidget()",
        1,
    )

dashboard_start = text.find("export default function Dashboard()")
if dashboard_start == -1:
    raise RuntimeError("Dashboard component not found")

if 'const [activeTab, setActiveTab]' not in text:
    marker = text.find("{", dashboard_start)
    insertion = '''

  const [activeTab, setActiveTab] =
    useState<DashboardTab>("overview");
'''
    text = text[:marker + 1] + insertion + text[marker + 1:]

if "<DashboardTabNavigation" not in text:
    text = text.replace(
        "<main",
        '''<main''',
        1,
    )

    text = text.replace(
        "      <LiveMarketWatchlist />",
        '''
      <DashboardTabNavigation
        activeTab={activeTab}
        setActiveTab={setActiveTab}
      />

      {(activeTab === "overview" || activeTab === "market") && (
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

      {(activeTab === "overview" || activeTab === "chat") && (
        <></>
      )}
''',
        1,
    )

    text = text.replace(
        "\n      <LiveSystemGraphPanel />",
        "",
        1,
    )
    text = text.replace(
        "\n      <FrontendObservabilityPanel />",
        "",
        1,
    )
    text = text.replace(
        "\n      <ObservabilityEventTimeline />",
        "",
        1,
    )

PAGE.write_text(text)
print("patched Phase 25A dashboard tab shell navigation")
