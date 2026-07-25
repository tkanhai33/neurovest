"use client";

export type DashboardTab =
  | "overview"
  | "market"
  | "graph"
  | "observability"
  | "learning"
  | "chat";

export function DashboardTabNavigation({
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
    "learning",
    "chat",
  ];

  return (
    <section className="nv-developer-legacy-tabs">
      <div className="flex flex-wrap gap-2">
        {tabs.map((tab) => (
          <button
            key={tab}
            type="button"
            onClick={() => setActiveTab(tab)}
            className={
              activeTab === tab
                ? "nv-workspace-tab nv-workspace-tab-active"
                : "nv-workspace-tab"
            }
          >
            {tab.toUpperCase()}
          </button>
        ))}
      </div>
    </section>
  );
}

export function Sidebar({
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
    "learning",
    "chat",
  ];

  return (
    <aside className="nv-developer-legacy-sidebar">
      <p className="text-xs uppercase tracking-[0.45em] text-cyan-300">Neurovest</p>
      <h2 className="nv-section-title">V3 Console</h2>

      <div className="mt-8 space-y-2">
        {tabs.map((tab) => (
          <button
            key={tab}
            type="button"
            onClick={() => setActiveTab(tab)}
            className={
              activeTab === tab
                ? "nv-developer-sidebar-link nv-developer-sidebar-link-active"
                : "nv-developer-sidebar-link"
            }
          >
            {tab.toUpperCase()}
          </button>
        ))}
      </div>

      <div className="nv-developer-runtime-locks">
        <p className="text-xs uppercase tracking-[0.25em] text-emerald-300">Runtime</p>
        <p className="mt-2 text-sm text-slate-300">Replay locked</p>
        <p className="text-sm text-slate-300">Broker disabled</p>
        <p className="text-sm text-slate-300">Live execution disabled</p>
      </div>
    </aside>
  );
}

export function DashboardHeader({
  activeTab,
  hydrated,
  setActiveTab,
}: {
  activeTab: DashboardTab;
  hydrated: boolean;
  setActiveTab: (tab: DashboardTab) => void;
}) {
  return (
    <section className="nv-developer-header-panel">
      <p className="text-xs uppercase tracking-[0.4em] text-cyan-300">
        Neurovest V3
      </p>

      <h1 className="mt-2 text-4xl font-black tracking-tight text-white">
        Trading Control Dashboard
      </h1>

      <p className="mt-3 max-w-3xl text-sm text-slate-400">
        Live market data, portfolio state, strategy decisions, and risk gates are separated through certified service chains.
      </p>

      <div className="mt-4 flex flex-wrap items-center gap-3">
        <div className="inline-flex rounded-full border border-cyan-400/30 px-3 py-1 text-xs text-cyan-200">
          Hydration: {hydrated ? "ACTIVE" : "SERVER HTML ONLY"}
        </div>

        <div className="nv-stat-label">
          Active Workspace: <span className="text-cyan-200">{activeTab.toUpperCase()}</span>
        </div>
      </div>

      <div className="lg:hidden">
        <DashboardTabNavigation
          activeTab={activeTab}
          setActiveTab={setActiveTab}
        />
      </div>
    </section>
  );
}

export function DashboardStats({
  analytics,
}: {
  analytics: {
    total_trades_logged?: number;
    buy_signals_count?: number;
    sell_signals_count?: number;
    execution_success_percentage?: number;
  } | null;
}) {
  return (
    <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      {[
        {
          label: "Trades",
          value: analytics?.total_trades_logged ?? 0,
          color: "text-white",
          sub: "Logged decisions",
        },
        {
          label: "Buys",
          value: analytics?.buy_signals_count ?? 0,
          color: "text-emerald-300",
          sub: "Accumulation signals",
        },
        {
          label: "Sells",
          value: analytics?.sell_signals_count ?? 0,
          color: "text-red-300",
          sub: "Exit signals",
        },
        {
          label: "Success",
          value: `${analytics?.execution_success_percentage ?? 0}%`,
          color: "text-cyan-300",
          sub: "Execution health",
        },
      ].map((card) => (
        <div
          key={card.label}
          className="rounded-3xl border border-cyan-400/10 bg-slate-950/80 p-5 shadow-[0_0_35px_rgba(15,23,42,0.45)]"
        >
          <div className="flex items-center justify-between">
            <p className="nv-stat-label">{card.label}</p>
            <span className="h-2 w-2 rounded-full bg-cyan-300 shadow-[0_0_12px_rgba(34,211,238,0.8)]" />
          </div>

          <div className={`mt-3 text-4xl font-black ${card.color}`}>{card.value}</div>
          <p className="mt-2 text-xs text-slate-500">{card.sub}</p>
        </div>
      ))}
    </section>
  );
}
