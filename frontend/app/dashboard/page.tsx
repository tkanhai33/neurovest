"use client";

import {
  useEffect,
  useState,
} from "react";

import LogoutButton from "../components/auth/LogoutButton";
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
  Panel,
  StatusBadge,
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
    <main className="space-y-6">
      <div className="flex justify-end">
        <LogoutButton />
      </div>

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

      <section className="grid gap-4 md:grid-cols-3">
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

      <MarketTickerBanner />

      <section>
        <div className="mb-4 flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="nv-eyebrow">
              Developer workspaces
            </p>

            <h2 className="mt-2 text-2xl font-black tracking-[-0.03em] text-white sm:text-3xl">
              Runtime control surfaces
            </h2>
          </div>

          <StatusBadge
            tone={
              hydrated
                ? "success"
                : "info"
            }
          >
            {hydrated
              ? "Services connected"
              : "Connecting"}
          </StatusBadge>
        </div>

        <div
          role="tablist"
          aria-label="Developer workspaces"
          className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6"
        >
          {workspaces.map(
            (workspace) => {
              const selected =
                workspace.id === activeTab;

              return (
                <button
                  key={workspace.id}
                  type="button"
                  role="tab"
                  aria-selected={selected}
                  onClick={() => {
                    setActiveTab(
                      workspace.id,
                    );
                  }}
                  className={[
                    "rounded-2xl border px-4 py-4 text-left transition duration-200",
                    selected
                      ? "border-cyan-300/35 bg-cyan-300/[0.09] shadow-[0_16px_50px_rgba(34,211,238,0.08)]"
                      : "border-white/[0.08] bg-slate-950/55 hover:-translate-y-0.5 hover:border-cyan-300/20 hover:bg-white/[0.04]",
                  ].join(" ")}
                >
                  <span
                    className={[
                      "block text-sm font-black",
                      selected
                        ? "text-cyan-100"
                        : "text-slate-200",
                    ].join(" ")}
                  >
                    {workspace.label}
                  </span>

                  <span className="mt-2 block text-xs leading-5 text-slate-500">
                    {workspace.description}
                  </span>
                </button>
              );
            },
          )}
        </div>
      </section>

      <DashboardStats
        analytics={analytics}
      />

      <Panel
        variant="default"
        className="overflow-hidden"
      >
        <div className="border-b border-white/[0.07] px-6 py-5">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="nv-eyebrow">
                Active developer surface
              </p>

              <h2 className="mt-2 text-2xl font-black text-white">
                {activeWorkspace.label}
              </h2>

              <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
                {activeWorkspace.description}
              </p>
            </div>

            <StatusBadge tone="violet">
              Internal workspace
            </StatusBadge>
          </div>
        </div>

        <div className="p-4 sm:p-6">
          <WorkspaceRouter
            activeTab={activeTab}
            positions={positions}
          />
        </div>
      </Panel>

      <Panel
        variant="muted"
        className="p-6"
      >
        <div className="flex flex-wrap items-center justify-between gap-5">
          <div>
            <p className="nv-eyebrow">
              Development policy
            </p>

            <h2 className="mt-3 text-xl font-black text-white">
              Internal diagnostics remain separated from customer workflows.
            </h2>

            <p className="mt-3 max-w-4xl text-sm leading-7 text-slate-400">
              Replay mutation, broker execution, and live-money operations remain disabled. Developer surfaces provide qualified visibility without bypassing NeuroVest safety controls.
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            <StatusBadge tone="success">
              Read boundaries active
            </StatusBadge>

            <StatusBadge tone="warning">
              Broker locked
            </StatusBadge>

            <StatusBadge tone="info">
              Replay controlled
            </StatusBadge>
          </div>
        </div>
      </Panel>

      <FloatingChatWidget />
    </main>
  );
}
