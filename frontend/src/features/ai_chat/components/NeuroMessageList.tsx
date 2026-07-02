import { Card } from "../../../components/ui";
import { neuroPlaceholderMessages } from "../contracts/neuroChatState";

export function NeuroMessageList() {
  return (
    <Card>
      <h2>Neuro Messages</h2>
      <div style={{ display: "grid", gap: "10px" }}>
        {neuroPlaceholderMessages.map((message) => (
          <div key={message.id} style={{ border: "1px solid var(--panel-soft)", borderRadius: "12px", padding: "12px" }}>
            <strong>{message.role}</strong>
            <p style={{ color: "var(--muted)" }}>{message.content}</p>
          </div>
        ))}
      </div>
    </Card>
  );
}
