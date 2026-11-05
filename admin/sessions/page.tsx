"use client";

import PageHeader from "../../../components/app-shell/PageHeader";
import { Panel, StatusMessage } from "../../../components/ui";

export default function AdminSessionsPage() {
  return (
    <main className="space-y-6">
      <PageHeader
        eyebrow="NeuroVest Administration"
        title="Session administration."
        description="Review authenticated session state, identify active access, and manage session revocation workflows."
        badge={
          <StatusMessage tone="warning">
            Restricted access
          </StatusMessage>
        }
      />

      <Panel variant="default" className="p-6">
        <StatusMessage tone="info">
          Session administration is not activated.
        </StatusMessage>
      </Panel>
    </main>
  );
}
