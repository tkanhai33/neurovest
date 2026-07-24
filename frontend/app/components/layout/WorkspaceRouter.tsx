"use client";

import type { PortfolioPosition } from "../../../services/portfolioService";
import type { DashboardTab } from "./DashboardShell";

import OverviewWorkspace from "../workspaces/OverviewWorkspace";
import NeuroWorkspace from "../workspaces/NeuroWorkspace";
import MarketWorkspace from "../workspaces/MarketWorkspace";
import GraphWorkspacePanel from "../workspaces/GraphWorkspacePanel";
import ObservabilityWorkspacePanel from "../workspaces/ObservabilityWorkspacePanel";
import LearningWorkspacePanel from "../workspaces/LearningWorkspacePanel";

export default function WorkspaceRouter({
  activeTab,
  positions,
}: {
  activeTab: DashboardTab;
  positions: PortfolioPosition[];
}) {
  return (
    <>
      {activeTab === "overview" && (
        <OverviewWorkspace positions={positions} />
      )}

      {activeTab === "market" && (
        <MarketWorkspace positions={positions} />
      )}

      {activeTab === "graph" && (
        <GraphWorkspacePanel />
      )}

      {activeTab === "observability" && (
        <ObservabilityWorkspacePanel />
      )}

      {activeTab === "learning" && (
        <LearningWorkspacePanel />
      )}

      {activeTab === "chat" && (
        <NeuroWorkspace />
      )}
    </>
  );
}
