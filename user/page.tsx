"use client";

import {
  redirect,
} from "next/navigation";
import PageHeader from "../../components/app-shell/PageHeader";
import { Panel, StatusMessage } from "../../components/ui";

export default function UserWorkspacePage() {
  // This will redirect to /user/dashboard
  redirect("/user/dashboard");
  
  // This code won't be reached due to redirect above
  return (
    <main className="space-y-6">
      <PageHeader
        eyebrow="NeuroVest Personal Workspace"
        title="User dashboard."
        description="Review your paper portfolio, market intelligence, risk information, and conversations with Neuro."
        badge={
          <StatusMessage tone="success">
            Authenticated
          </StatusMessage>
        }
      />

      <Panel variant="default" className="p-6">
        <StatusMessage tone="info">
          Redirecting to dashboard...
        </StatusMessage>
      </Panel>
    </main>
  );
}
