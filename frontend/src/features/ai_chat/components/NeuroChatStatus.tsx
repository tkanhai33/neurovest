import { StatusPill } from "../../../components/ui";

export function NeuroChatStatus() {
  return (
    <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
      <StatusPill label="Model Calls Locked" />
      <StatusPill label="Tool Use Locked" />
      <StatusPill label="Broker Calls Locked" />
      <StatusPill label="Runtime Locked" />
    </div>
  );
}
