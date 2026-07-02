export const paperTradingUiState = {
  phase: "phase_33h_paper_trading_ui_composition",
  uiOnly: true,
  backendCallsEnabled: false,
  simulatedOrderEngineEnabled: false,
  simulatedFillEngineEnabled: false,
  pnlLogicEnabled: false,
  brokerCallsEnabled: false,
  tradingEnabled: false
} as const;

export const paperTradingModules = [
  { name: "Paper Account", status: "Locked", role: "Static simulated account view" },
  { name: "Simulated Orders", status: "Locked", role: "No order creation" },
  { name: "Simulated Fills", status: "Locked", role: "No fill engine" },
  { name: "Paper Positions", status: "Locked", role: "No position mutation" },
  { name: "Paper PnL", status: "Locked", role: "No PnL calculation" }
] as const;

export const paperAccountPreviewState = [
  { label: "Account", value: "Paper Preview" },
  { label: "Currency", value: "CAD" },
  { label: "Starting Cash", value: "Locked" },
  { label: "Broker Link", value: "None" }
] as const;

export const simulatedOrderLockState = [
  "Order creation locked",
  "Order validation locked",
  "Order queue disabled",
  "Broker routing disabled"
] as const;

export const simulatedFillPreviewState = [
  { label: "Fill Engine", value: "Locked" },
  { label: "Slippage", value: "Disabled" },
  { label: "Commission", value: "Disabled" },
  { label: "Execution Source", value: "None" }
] as const;

export const paperPositionPreviewState = [
  { symbol: "RY.TO", quantity: "Locked", value: "Locked" },
  { symbol: "SHOP.TO", quantity: "Locked", value: "Locked" },
  { symbol: "VFV.TO", quantity: "Locked", value: "Locked" }
] as const;

export const paperPnlPreviewState = [
  { label: "Realized PnL", value: "Locked" },
  { label: "Unrealized PnL", value: "Locked" },
  { label: "Daily PnL", value: "Disabled" },
  { label: "Currency", value: "CAD" }
] as const;
