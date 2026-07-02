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
