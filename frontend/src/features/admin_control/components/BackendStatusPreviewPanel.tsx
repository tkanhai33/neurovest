import { Card, MetricTile, StatusPill } from "../../../components/ui";
import {
  backendStatusDisplayModel,
  backendStatusViewModelState
} from "../view_model";

export function BackendStatusPreviewPanel() {
  return (
    <Card>
      <h2>Read-Only Backend Status</h2>

      <p className="nv-muted">
        Static frontend mirror and Static frontend view model for backend status. No fetch, backend call,
        runtime execution, broker call, AI call, provider call, mutation, or trading path is active.
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px", marginTop: "14px" }}>
        <MetricTile label="Stack" value={backendStatusDisplayModel.stack} />
        <MetricTile label="Backend" value={backendStatusDisplayModel.backend} />
        <MetricTile label="Runtime" value={backendStatusDisplayModel.runtime} />
        <MetricTile label="Broker Calls" value={backendStatusDisplayModel.brokerCalls} />
        <MetricTile label="Trading" value={backendStatusDisplayModel.trading} />
        <MetricTile label="Mutation" value={backendStatusDisplayModel.mutation} />
        <MetricTile label="Providers" value={backendStatusDisplayModel.providers} />
        <MetricTile label="AI Calls" value={backendStatusDisplayModel.aiCalls} />
        <MetricTile label="Client" value={backendStatusDisplayModel.client} />
      </div>

      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginTop: "14px" }}>
        <StatusPill label={`View model only: ${backendStatusViewModelState.viewModelOnly ? "True" : "False"}`} />
        <StatusPill label={`Read only: ${backendStatusViewModelState.readOnly ? "True" : "False"}`} />
        <StatusPill label={`Backend calls: ${backendStatusViewModelState.backendCallsEnabled ? "Enabled" : "Locked"}`} />
      </div>
    </Card>
  );
}
