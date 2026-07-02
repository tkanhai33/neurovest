import { Card, MetricTile, StatusPill } from "../../../components/ui";
import { approvalPreviewState } from "../contracts/riskUiState";

export function ApprovalDecisionPlaceholderPanel() {
  return (
    <Card>
      <h2>Approval Decision Preview</h2>
      <p className="nv-muted">
        Approval gates are displayed only. No approval engine, broker path, or runtime decision is active.
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(170px, 1fr))", gap: "12px", marginTop: "14px" }}>
        {approvalPreviewState.map((item) => (
          <MetricTile key={item.label} label={item.label} value={item.value} />
        ))}
      </div>

      <div style={{ marginTop: "14px" }}>
        <StatusPill label="All approvals locked" />
      </div>
    </Card>
  );
}
