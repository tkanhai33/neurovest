import { PageHeader, Card, StatusPill } from "../../components/ui";
import { AppShell } from "../../layouts/AppShell";

export default function SettingsPage() {
  return (
    <AppShell>
      <PageHeader
        title="Settings"
        subtitle="Static settings shell. No configuration writes occur during the skeleton phase."
      />
      <Card>
        <h2>Settings Locked</h2>
        <StatusPill label="Config Writes Disabled" />
        <StatusPill label="Secrets Disabled" />
        <StatusPill label="Provider Keys Disabled" />
      </Card>
    </AppShell>
  );
}
