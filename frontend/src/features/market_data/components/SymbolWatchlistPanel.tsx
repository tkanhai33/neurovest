import { Card, Badge } from "../../../components/ui";
import { marketSymbols } from "../contracts/marketDataUiState";

export function SymbolWatchlistPanel() {
  return (
    <Card>
      <h2>Symbol Watchlist</h2>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
        {marketSymbols.map((symbol) => (
          <Badge key={symbol} label={`${symbol}: Placeholder`} />
        ))}
      </div>
    </Card>
  );
}
