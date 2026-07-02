import { Card, Badge } from "../../../components/ui";
import { portfolioHoldings } from "../contracts/portfolioUiState";

export function HoldingsPlaceholderPanel() {
  return (
    <Card>
      <h2>Holdings Placeholder</h2>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
        {portfolioHoldings.map((symbol) => (
          <Badge key={symbol} label={`${symbol}: Locked`} />
        ))}
      </div>
    </Card>
  );
}
