import { Card, StatusPill } from "../../../components/ui";

export function SystemLockPanel() {
  return (
    <Card>
      <h2>System Locks</h2>
      <StatusPill label="Backend API Calls Locked" />
      <StatusPill label="Market Provider Calls Locked" />
      <StatusPill label="AI Model Calls Locked" />
      <StatusPill label="Runtime Execution Locked" />
      <StatusPill label="Broker Orders Locked" />
      <StatusPill label="Live Trading Locked" />
    </Card>
  );
}
