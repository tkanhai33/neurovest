import { frontendSystemState } from "../lib/contracts/frontendSystemState";

export function TopStatusBar() {
  return (
    <header className="nv-topbar">
      <strong>System Locked</strong>
      <span className="nv-muted" style={{ marginLeft: "12px" }}>
        {frontendSystemState.phase}
      </span>
    </header>
  );
}
