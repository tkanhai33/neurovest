"use client";

import PageHeader from "../../../components/app-shell/PageHeader";
import { Panel, StatusMessage } from "../../../components/ui";

export default function AdminTicketsPage() {
  return (
    <main className="space-y-6">
      <PageHeader
        eyebrow="NeuroVest Administration"
        title="Support tickets."
        description="Review user-reported problems and controlled support workflows without exposing internal developer systems."
        badge={
          <StatusMessage tone="warning">
            Restricted access
          </StatusMessage>
        }
      />

      <Panel variant="default" className="p-6">
        <StatusMessage tone="info">
          Support ticket system is not activated.
        </StatusMessage>
      </Panel>
    </main>
  );
}
