import { frontendSystemState } from "../lib/contracts/frontendSystemState";

export function TopStatusBar() {
  return (
    <header style={{ padding: "16px 24px", borderBottom: "1px solid var(--panel-soft)" }}>
      <strong>System Locked</strong>
      <span style={{ color: "var(--muted)", marginLeft: "12px" }}>
        {frontendSystemState.phase}
      </span>
    </header>
  );
}
