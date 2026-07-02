#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FRONTEND="$ROOT/frontend"

echo "========================================="
echo "PHASE 17 - NEURO CHAT UI SKELETON"
echo "========================================="

cd "$ROOT"

BRANCH="$(git branch --show-current)"
if [ "$BRANCH" != "frontend-skeleton" ]; then
  echo "ERROR: Expected frontend-skeleton branch, got: $BRANCH"
  exit 1
fi

pytest

mkdir -p "$FRONTEND/src/features/ai_chat/components" \
  "$FRONTEND/src/features/ai_chat/contracts"

cat > "$FRONTEND/src/features/ai_chat/contracts/neuroChatState.ts" <<'EOF'
export type NeuroChatMessageRole = "system" | "user" | "assistant";

export type NeuroChatMessage = {
  id: string;
  role: NeuroChatMessageRole;
  content: string;
};

export const neuroChatState = {
  phase: "phase_17_neuro_chat_ui_skeleton",
  uiOnly: true,
  modelCallsEnabled: false,
  toolCallsEnabled: false,
  brokerCallsEnabled: false,
  runtimeCallsEnabled: false,
  tradingEnabled: false
} as const;

export const neuroPlaceholderMessages: readonly NeuroChatMessage[] = [
  {
    id: "system_001",
    role: "system",
    content: "Neuro chat UI skeleton. Model calls and tool use are locked."
  },
  {
    id: "assistant_001",
    role: "assistant",
    content: "Neuro online. Standing guard."
  }
] as const;
EOF

cat > "$FRONTEND/src/features/ai_chat/components/NeuroChatStatus.tsx" <<'EOF'
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
EOF

cat > "$FRONTEND/src/features/ai_chat/components/NeuroMessageList.tsx" <<'EOF'
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
EOF

cat > "$FRONTEND/src/features/ai_chat/components/NeuroChatInputShell.tsx" <<'EOF'
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
EOF

cat > "$FRONTEND/src/features/ai_chat/components/NeuroChatPanel.tsx" <<'EOF'
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
EOF

cat > "$FRONTEND/src/features/ai_chat/components/index.ts" <<'EOF'
export { NeuroChatInputShell } from "./NeuroChatInputShell";
export { NeuroChatPanel } from "./NeuroChatPanel";
export { NeuroChatStatus } from "./NeuroChatStatus";
export { NeuroMessageList } from "./NeuroMessageList";
EOF

cat > "$FRONTEND/scripts/verify-neuro-chat-ui-skeleton.mjs" <<'EOF'
import { existsSync, readFileSync } from "node:fs";

const required = [
  "src/features/ai_chat/contracts/neuroChatState.ts",
  "src/features/ai_chat/components/NeuroChatStatus.tsx",
  "src/features/ai_chat/components/NeuroMessageList.tsx",
  "src/features/ai_chat/components/NeuroChatInputShell.tsx",
  "src/features/ai_chat/components/NeuroChatPanel.tsx",
  "src/features/ai_chat/components/index.ts"
];

for (const file of required) {
  if (!existsSync(file)) throw new Error(`Missing Neuro chat UI skeleton file: ${file}`);
}

const forbidden = [
  "fetch(",
  "axios",
  "ollama.chat",
  "ollama.generate",
  "execute_tool",
  "submit_order",
  "place_order",
  "execute_trade",
  "broker_client",
  "runtime_service",
  "useEffect("
];

for (const file of required) {
  const text = readFileSync(file, "utf8");
  for (const term of forbidden) {
    if (text.includes(term)) throw new Error(`Forbidden term ${term} found in ${file}`);
  }
}

console.log("PASS: Neuro chat UI skeleton verified.");
EOF

(cd "$FRONTEND" && node scripts/verify-neuro-chat-ui-skeleton.mjs)
(cd "$FRONTEND" && node scripts/verify-dashboard-skeleton.mjs)
(cd "$FRONTEND" && node scripts/verify-route-registry.mjs)
(cd "$FRONTEND" && node scripts/verify-design-system-skeleton.mjs)
(cd "$FRONTEND" && node scripts/verify-frontend-skeleton.mjs)

cat > docs/contracts/PHASE_17_NEURO_CHAT_UI_SKELETON_CONTRACT.md <<'EOF'
# Phase 17 Neuro Chat UI Skeleton Contract

Status: skeleton only.

Allowed:
- Neuro chat UI shell
- message display placeholder
- disabled input shell
- locked chat state contract
- chat status indicators
- verification script
- certification artifact

Forbidden:
- real AI model calls
- RAG implementation
- memory implementation
- tool execution
- backend API calls
- broker calls
- runtime calls
- trading logic
- business logic
EOF

cat > certification/phase_01/PHASE_17_NEURO_CHAT_UI_SKELETON_CERTIFICATION.md <<'EOF'
# Phase 17 Neuro Chat UI Skeleton Certification

Status: PASS

Verified:
- Neuro chat state exists
- message list exists
- disabled input shell exists
- chat status indicators exist
- chat panel exists
- no model calls
- no tool calls
- no broker calls
- no runtime calls
- no trading logic

Result:
- Phase 17 Neuro chat UI skeleton is certified.
EOF

git add .
git commit -m "Phase 17: Neuro chat UI skeleton"

git tag -a phase-17-neuro-chat-ui-skeleton \
  -m "Certified Phase 17 Neuro chat UI skeleton"

git push
git push --tags

echo "PASS: Phase 17 complete."
