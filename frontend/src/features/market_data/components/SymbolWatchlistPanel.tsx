import { Badge, Card } from "../../../components/ui";
import { marketSymbols } from "../contracts/marketDataUiState";

export function SymbolWatchlistPanel() {
  return (
    <Card>
      <h2>Symbol Watchlist</h2>
      <p className="nv-muted">
        Static symbols prepared for future contract-backed quotes and candles.
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(190px, 1fr))", gap: "12px", marginTop: "14px" }}>
        {marketSymbols.map((item) => (
          <div key={item.symbol} className="nv-panel">
            <strong>{item.symbol}</strong>
            <p className="nv-muted" style={{ margin: "6px 0 10px" }}>{item.name}</p>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
              <Badge label={item.exchange} />
              <Badge label={item.currency} />
              <Badge label={item.state} />
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
