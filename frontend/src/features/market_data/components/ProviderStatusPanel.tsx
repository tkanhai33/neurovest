import { Card, MetricTile, StatusPill } from "../../../components/ui";
import { marketDataUiState, marketProviders } from "../contracts/marketDataUiState";

export function ProviderStatusPanel() {
  return (
    <Card>
      <h2>Provider Status</h2>
      <p className="nv-muted">
        Market providers are mapped for visibility only. Live calls remain locked.
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "12px", marginTop: "14px" }}>
        {marketProviders.map((provider) => (
          <MetricTile key={provider.name} label={provider.role} value={`${provider.name}: ${provider.status}`} />
        ))}
      </div>

      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginTop: "14px" }}>
        <StatusPill label={`UI Only: ${marketDataUiState.uiOnly ? "True" : "False"}`} />
        <StatusPill label={`Provider Calls: ${marketDataUiState.providerCallsEnabled ? "Enabled" : "Locked"}`} />
        <StatusPill label={`Backend Calls: ${marketDataUiState.backendCallsEnabled ? "Enabled" : "Locked"}`} />
      </div>
    </Card>
  );
}
