"use client";

import PageHeader from "../../../components/app-shell/PageHeader";
import { Panel, StatusMessage } from "../../../components/ui";

export default function AdminAuditPage() {
  return (
    <main className="space-y-6">
      <PageHeader
        eyebrow="NeuroVest Administration"
        title="Audit operations."
        description="Review immutable decision records, administrative events, and read-only system audit history."
        badge={
          <StatusMessage tone="warning">
            Restricted access
          </StatusMessage>
        }
      />

      <Panel variant="default" className="p-6">
        <StatusMessage tone="info">
          Administrative audit access is not activated.
        </StatusMessage>
      </Panel>
    </main>
  );
}
