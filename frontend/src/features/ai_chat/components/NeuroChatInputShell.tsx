import { Card, Button } from "../../../components/ui";

export function NeuroChatInputShell() {
  return (
    <Card>
      <label htmlFor="neuro-chat-input">Message Neuro</label>
      <textarea
        id="neuro-chat-input"
        disabled
        placeholder="Chat input locked during skeleton phase"
        style={{ width: "100%", minHeight: "90px", marginTop: "10px", borderRadius: "12px", padding: "12px" }}
      />
      <div style={{ marginTop: "12px" }}>
        <Button label="Send Locked" />
      </div>
    </Card>
  );
}
