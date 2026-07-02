import { Badge, Card } from "../../../components/ui";
import { mutationLockState } from "../contracts/runtimeUiState";

export function MutationLockedPanel() {
  return (
    <Card>
      <h2>Mutation Locked</h2>
      <p className="nv-muted">
        Mutation remains fully disabled. No AI, learning, strategy, or runtime writes are allowed.
      </p>

      <div style={{ display: "flex", flexWrap: "wrap", gap: "8px", marginTop: "14px" }}>
        {mutationLockState.map((item) => (
          <Badge key={item} label={item} />
        ))}
      </div>
    </Card>
  );
}
