import { Card, MetricTile, StatusPill } from "../../../components/ui";
import {
  backendStatusPreviewState,
  backendStatusUiState
} from "../contracts/backendStatusUiState";

export function BackendStatusPreviewPanel() {
  return (
    <Card>
      <h2>Read-Only Backend Status</h2>

      <p className="nv-muted">
        Static frontend mirror of the backend status contract. No fetch, backend call,
        runtime execution, broker call, AI call, provider call, mutation, or trading path is active.
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px", marginTop: "14px" }}>
        <MetricTile label="Stack" value={backendStatusPreviewState.stack} />
        <MetricTile label="Backend" value={backendStatusPreviewState.backendOnline} />
        <MetricTile label="Runtime" value={backendStatusPreviewState.runtimeEnabled ? "Enabled" : "Locked"} />
        <MetricTile label="Broker Calls" value={backendStatusPreviewState.brokerCallsEnabled ? "Enabled" : "Locked"} />
        <MetricTile label="Trading" value={backendStatusPreviewState.tradingEnabled ? "Enabled" : "Locked"} />
        <MetricTile label="Mutation" value={backendStatusPreviewState.mutationEnabled ? "Enabled" : "Locked"} />
        <MetricTile label="Providers" value={backendStatusPreviewState.providerCallsEnabled ? "Enabled" : "Locked"} />
        <MetricTile label="AI Calls" value={backendStatusPreviewState.aiCallsEnabled ? "Enabled" : "Locked"} />
      </div>

      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginTop: "14px" }}>
        <StatusPill label={`Frontend only: ${backendStatusUiState.frontendOnly ? "True" : "False"}`} />
        <StatusPill label={`Read only: ${backendStatusUiState.readOnly ? "True" : "False"}`} />
        <StatusPill label={`Backend calls: ${backendStatusUiState.backendCallsEnabled ? "Enabled" : "Locked"}`} />
      </div>
    </Card>
  );
}
