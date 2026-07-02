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
