"use client";

import PageHeader from "../../../components/app-shell/PageHeader";
import { Panel, StatusMessage } from "../../../components/ui";

export default function UserStatsPage() {
  return (
    <main className="space-y-6">
      <PageHeader
        eyebrow="NeuroVest Administration"
        title="User statistics."
        description="Inspect account-level platform statistics and aggregate user activity surfaces."
        badge={
          <StatusMessage tone="warning">
            Read-only view
          </StatusMessage>
        }
      />

      <Panel variant="default" className="p-6">
        <StatusMessage tone="info">
          User statistics are not activated.
        </StatusMessage>
      </Panel>
    </main>
  );
}
