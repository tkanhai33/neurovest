import { PageHeader } from "../../../components/ui";
import { BrokerAccountPlaceholderPanel } from "./BrokerAccountPlaceholderPanel";
import { BrokerAuthLockedPanel } from "./BrokerAuthLockedPanel";
import { BrokerConnectionStatusPanel } from "./BrokerConnectionStatusPanel";
import { BrokerOrderLockedPanel } from "./BrokerOrderLockedPanel";
import { BrokerOverviewPanel } from "./BrokerOverviewPanel";
import { BrokerProviderPanel } from "./BrokerProviderPanel";

export function BrokerIntegrationPanel() {
  return (
    <div style={{ display: "grid", gap: "18px" }}>
      <PageHeader
        title="Broker Integration"
        subtitle="Static broker UI skeleton. Auth, tokens, account sync, order submission, and live trading are locked."
      />
      <BrokerOverviewPanel />
      <BrokerProviderPanel />
      <BrokerConnectionStatusPanel />
      <BrokerAuthLockedPanel />
      <BrokerAccountPlaceholderPanel />
      <BrokerOrderLockedPanel />
    </div>
  );
}
