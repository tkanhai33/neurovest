import { Card, StatusPill } from "../../../components/ui";

export function BrokerAuthLockedPanel() {
  return (
    <Card>
      <h2>Authentication Locked</h2>
      <StatusPill label="Auth Flow Disabled" />
      <StatusPill label="Token Storage Disabled" />
      <p style={{ color: "var(--muted)" }}>
        Broker authentication and token storage are not implemented during the skeleton phase.
      </p>
    </Card>
  );
}
