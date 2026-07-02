import { PageHeader } from "../../../components/ui";
import { CandlePlaceholderPanel } from "./CandlePlaceholderPanel";
import { ProviderStatusPanel } from "./ProviderStatusPanel";
import { QuotePlaceholderPanel } from "./QuotePlaceholderPanel";
import { SymbolWatchlistPanel } from "./SymbolWatchlistPanel";

export function MarketDataPanel() {
  return (
    <div style={{ display: "grid", gap: "18px" }}>
      <PageHeader
        title="Market Data"
        subtitle="Static market data UI skeleton. Provider and backend calls are locked."
      />
      <ProviderStatusPanel />
      <SymbolWatchlistPanel />
      <QuotePlaceholderPanel />
      <CandlePlaceholderPanel />
    </div>
  );
}
