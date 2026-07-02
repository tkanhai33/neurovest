import { Card, StatusPill } from "../../../components/ui";

export function SystemLockPanel() {
  return (
    <Card>
      <h2>System Locks</h2>
      <StatusPill label="Live Trading Locked" />
      <StatusPill label="Broker Orders Locked" />
      <StatusPill label="Runtime Locked" />
      <StatusPill label="AI Tool Use Locked" />
    </Card>
  );
}
