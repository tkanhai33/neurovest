import { PageHeader } from "../../../components/ui";
import { NeuroChatInputShell } from "./NeuroChatInputShell";
import { NeuroChatStatus } from "./NeuroChatStatus";
import { NeuroMessageList } from "./NeuroMessageList";

export function NeuroChatPanel() {
  return (
    <div style={{ display: "grid", gap: "18px" }}>
      <PageHeader
        title="Neuro Chat"
        subtitle="Chat UI skeleton only. No model, tool, runtime, broker, or trading calls."
      />
      <NeuroChatStatus />
      <NeuroMessageList />
      <NeuroChatInputShell />
    </div>
  );
}
