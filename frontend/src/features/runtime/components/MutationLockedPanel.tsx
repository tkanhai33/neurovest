import { Card, StatusPill } from "../../../components/ui";

export function MutationLockedPanel() {
  return (
    <Card>
      <h2>Mutation Locked</h2>
      <StatusPill label="AI Mutation Disabled" />
      <StatusPill label="Strategy Mutation Disabled" />
      <StatusPill label="Runtime Mutation Disabled" />
    </Card>
  );
}
