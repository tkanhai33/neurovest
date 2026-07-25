"use client";

import {
  useEffect,
  useState,
} from "react";

import FloatingChatWidget from "../components/chat/FloatingChatWidget";
import {
  DashboardStats,
  type DashboardTab,
} from "../components/layout/DashboardShell";
import WorkspaceRouter from "../components/layout/WorkspaceRouter";
import MarketTickerBanner from "../components/ticker/MarketTickerBanner";
import { useDashboardData } from "../hooks/useDashboardData";

import PageHeader from "../../components/app-shell/PageHeader";
import {
  PageContainer,
  Panel,
  StatusBadge,
  WorkspaceTabs,
} from "../../components/ui";

import {
  saveSafeUiPreferences,
} from "../../lib/uiPreferences";

type WorkspaceDefinition = {
  id: DashboardTab;
  label: string;
  description: string;
};

const workspaces: WorkspaceDefinition[] = [
  {
    id: "overview",
    label: "Overview",
    description:
      "System health, portfolio state, execution safety, and runtime summaries.",
  },
  {
    id: "market",
    label: "Market",
    description:
      "Market-data services, pricing context, and symbol-level intelligence.",
  },
  {
    id: "graph",
    label: "Graph",
    description:
      "Architecture relationships, service connectivity, and runtime graph state.",
  },
  {
    id: "observability",
    label: "Observability",
    description:
      "Operational telemetry, service checks, and qualified runtime diagnostics.",
  },
  {
    id: "learning",
    label: "Learning",
    description:
      "Read-only replay intelligence and controlled learning-system visibility.",
  },
  {
    id: "chat",
    label: "Chat",
    description:
      "Developer-facing Neuro interaction and diagnostic assistance.",
  },
];

export default function DashboardPage() {
  const [activeTab, setActiveTab] =
    useState<DashboardTab>("overview");

  useEffect(() => {
    saveSafeUiPreferences({
      activeWorkspace: activeTab,
    });
  }, [activeTab]);

  const {
    hydrated,
    positions,
    analytics,
  } = useDashboardData();

  const activeWorkspace =
    workspaces.find(
      (workspace) =>
        workspace.id === activeTab,
    ) ?? workspaces[0];

  return (
    <PageContainer
      data-testid="developer-dashboard"
      className="nv-developer-dashboard"
    >
      <main className="nv-developer-page">
        <section className="nv-developer-page-header">
          <PageHeader
        eyebrow="NeuroVest Developer Workspace"
        title="System control and observability."
        description="A controlled development workspace for runtime health, market services, architecture visibility, replay intelligence, and diagnostic tooling."
        badge={
          <StatusBadge tone="warning">
            Developer access
          </StatusBadge>
        }
      />
        </section>

        <section
          className="nv-developer-status-strip"
          aria-label="Developer system status"
        >
          <Panel
          variant="elevated"
          className="p-5"
        >
          <p className="nv-stat-label">
            Runtime hydration
          </p>

          <p className="mt-3 text-2xl font-black text-white">
            {hydrated
              ? "Active"
              : "Loading"}
          </p>

          <p className="mt-3 text-sm leading-6 text-slate-400">
            Developer data is loaded through the qualified frontend service boundaries.
          </p>
        </Panel>

          <Panel
          variant="elevated"
          className="p-5"
        >
          <p className="nv-stat-label">
            Execution policy
          </p>

          <p className="mt-3 text-2xl font-black text-white">
            Live trading disabled
          </p>

          <p className="mt-3 text-sm leading-6 text-slate-400">
            Broker execution remains locked while simulation and read-only diagnostics are active.
          </p>
        </Panel>

          <Panel
          variant="elevated"
          className="p-5"
        >
          <p className="nv-stat-label">
            Active workspace
          </p>

          <p className="mt-3 text-2xl font-black text-white">
            {activeWorkspace.label}
          </p>

          <p className="mt-3 text-sm leading-6 text-slate-400">
            {activeWorkspace.description}
          </p>
        </Panel>
        </section>

        <section
          className="nv-developer-ticker"
          aria-label="Market ticker"
        >
          <MarketTickerBanner />
        </section>

        <nav
          className="nv-developer-workspace-navigation"
          aria-label="Developer workspaces"
        >
          <div className="nv-developer-navigation-label">
            <p className="nv-eyebrow">
              Workspace
            </p>

            <p className="nv-developer-navigation-title">
              Select an operational surface
            </p>
          </div>

          <WorkspaceTabs
          items={workspaces}
          activeId={activeTab}
          onChange={(workspaceId: DashboardTab) => {
            setActiveTab(workspaceId);
          }}
          label="Developer dashboard workspaces"
        />
        </nav>

        <section
          className="nv-developer-metrics"
          aria-labelledby="developer-runtime-metrics"
        >
          <div className="nv-developer-section-heading">
            <div>
              <p className="nv-eyebrow">
                Runtime metrics
              </p>

              <h2
                id="developer-runtime-metrics"
                className="nv-section-title"
              >
                Current system activity
              </h2>
            </div>

            <StatusBadge tone="success">
              Services connected
            </StatusBadge>
          </div>

          <DashboardStats
        analytics={analytics}
      />
        </section>

        <section
          className="nv-developer-active-workspace"
          aria-label="Active Developer workspace"
        >
          <WorkspaceRouter
            activeTab={activeTab}
            positions={positions}
          />
        </section>

        <FloatingChatWidget />
      </main>
    </PageContainer>
  );
}
