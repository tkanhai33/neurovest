import { Card, StatusPill } from "../../../components/ui";

export function ApprovalDecisionPlaceholderPanel() {
  return (
    <Card>
      <h2>Approval Decision Shell</h2>
      <StatusPill label="All Approvals Locked" />
      <p style={{ color: "var(--muted)" }}>
        Risk approval engine is not implemented during the skeleton phase.
      </p>
    </Card>
  );
}
