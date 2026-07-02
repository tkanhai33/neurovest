import { Card, StatusPill } from "../../../components/ui";

export function BrokerOrderLockedPanel() {
  return (
    <Card>
      <h2>Order Submission Locked</h2>
      <StatusPill label="Orders Disabled" />
      <StatusPill label="Execution Disabled" />
      <StatusPill label="Live Trading Disabled" />
    </Card>
  );
}
