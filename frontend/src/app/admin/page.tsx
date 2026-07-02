import { PageHeader, Card, StatusPill } from "../../components/ui";
import { AppShell } from "../../layouts/AppShell";

export default function AdminPage() {
  return (
    <AppShell>
      <PageHeader
        title="Admin"
        subtitle="Static admin shell. Governance controls, mutation, runtime, and broker unlocks are disabled."
      />
      <Card>
        <h2>Admin Controls Locked</h2>
        <StatusPill label="Governance Locked" />
        <StatusPill label="Runtime Unlock Disabled" />
        <StatusPill label="Broker Unlock Disabled" />
      </Card>
    </AppShell>
  );
}
