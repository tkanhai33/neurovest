import { Card, StatusPill } from "../../../components/ui";

export function ProviderStatusPanel() {
  return (
    <Card>
      <h2>Provider Status</h2>
      <StatusPill label="yfinance Locked" />
      <StatusPill label="Finnhub Locked" />
      <StatusPill label="Backend Calls Locked" />
    </Card>
  );
}
