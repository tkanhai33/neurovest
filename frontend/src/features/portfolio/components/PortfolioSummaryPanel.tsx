import { Card, MetricTile, StatusPill } from "../../../components/ui";
import { portfolioSummaryState, portfolioUiState } from "../contracts/portfolioUiState";

export function PortfolioSummaryPanel() {
  return (
    <Card>
      <h2>Portfolio Summary</h2>
      <p className="nv-muted">
        Portfolio composition is prepared for future contract-backed account data.
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "12px", marginTop: "14px" }}>
        <MetricTile label="Account" value={portfolioSummaryState.accountName} />
        <MetricTile label="Total Equity" value={portfolioSummaryState.totalEquity} />
        <MetricTile label="Cash Available" value={portfolioSummaryState.cashAvailable} />
        <MetricTile label="Daily P/L" value={portfolioSummaryState.dailyPnL} />
        <MetricTile label="Buying Power" value={portfolioSummaryState.buyingPower} />
      </div>

      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginTop: "14px" }}>
        <StatusPill label={`UI Only: ${portfolioUiState.uiOnly ? "True" : "False"}`} />
        <StatusPill label={`Broker Calls: ${portfolioUiState.brokerCallsEnabled ? "Enabled" : "Locked"}`} />
        <StatusPill label={`Trading: ${portfolioUiState.tradingEnabled ? "Enabled" : "Locked"}`} />
      </div>
    </Card>
  );
}
