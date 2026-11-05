"use client";

import PageHeader from "../../../components/app-shell/PageHeader";
import { Panel, StatusMessage } from "../../../components/ui";

export default function AdministrativeUserDashboardPage() {
  return (
    <main className="space-y-6">
      <PageHeader
        eyebrow="NeuroVest Administration"
        title="User workspace preview."
        description="Inspect the customer-facing workspace presentation without changing the authenticated role boundary."
        badge={
          <StatusMessage tone="warning">
            Read-only view
          </StatusMessage>
        }
      />

      <Panel variant="default" className="p-6">
        <StatusMessage tone="info">
          User dashboard preview is not activated.
        </StatusMessage>
      </Panel>
    </main>
  );
}
