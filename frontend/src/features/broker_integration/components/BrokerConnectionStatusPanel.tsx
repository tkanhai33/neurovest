import { Card, StatusPill } from "../../../components/ui";

export function BrokerConnectionStatusPanel() {
  return (
    <Card>
      <h2>Connection Status</h2>
      <StatusPill label="Not Connected" />
      <StatusPill label="Read-Only Locked" />
      <StatusPill label="Live Trading Locked" />
    </Card>
  );
}
