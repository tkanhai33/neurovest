import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/features/broker_integration/contracts/brokerIntegrationUiState.ts",
  "src/features/broker_integration/components/BrokerOverviewPanel.tsx",
  "src/features/broker_integration/components/BrokerProviderPanel.tsx",
  "src/features/broker_integration/components/BrokerConnectionStatusPanel.tsx",
  "src/features/broker_integration/components/BrokerAuthLockedPanel.tsx",
  "src/features/broker_integration/components/BrokerAccountPlaceholderPanel.tsx",
  "src/features/broker_integration/components/BrokerOrderLockedPanel.tsx",
  "src/features/broker_integration/components/BrokerIntegrationPanel.tsx",
  "src/features/broker_integration/components/index.ts"
];

for (const file of required) {
  if (!existsSync(file)) throw new Error(`Missing broker integration UI skeleton file: ${file}`);
}

const forbidden = [
  "fetch(",
  "axios",
  "import snaptrade",
  "SnapTradeClient",
  "access_token",
  "refresh_token",
  "submit_order",
  "place_order",
  "execute_trade",
  "live_trade",
  "broker_client",
  "useEffect("
];

for (const file of required) {
  const text = readFileSync(file, "utf8");
  for (const term of forbidden) {
    if (text.includes(term)) throw new Error(`Forbidden term ${term} found in ${file}`);
  }
}

console.log("PASS: Broker integration UI skeleton verified.");
