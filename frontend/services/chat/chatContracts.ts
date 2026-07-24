export type ChatRole =
  | "system"
  | "user"
  | "assistant"
  | "tool";

export type ThreadStatus =
  | "active"
  | "archived";

export type MemoryStatus =
  | "active"
  | "superseded"
  | "retracted";

export type EvidenceStatus =
  | "success"
  | "error"
  | "unavailable";

export type ToolTruthState =
  | "grounded"
  | "partial"
  | "ungrounded"
  | "not_required";

export type ChatThreadContract = {
  thread_id: string;
  user_id?: string | null;
  title?: string | null;
  status: ThreadStatus;
  summary?: string | null;
  message_count: number;
  created_at: string;
  updated_at: string;
  metadata: Record<string, unknown>;
};

export type ChatMessageContract = {
  message_id: string;
  thread_id: string;
  parent_message_id?: string | null;
  role: ChatRole;
  content: string;
  intent?: string | null;
  symbol?: string | null;
  provider?: string | null;
  model?: string | null;
  tool_evidence_ids: string[];
  created_at: string;
  metadata: Record<string, unknown>;
};

export type PendingConversationTaskContract = {
  task_id: string;
  task_type: string;
  description: string;
  status:
    | "pending"
    | "running"
    | "completed"
    | "failed"
    | "cancelled";
  source_message_id?: string | null;
  details: Record<string, unknown>;
};

export type ConversationStateContract = {
  thread_id: string;
  summary: string;
  active_entities: Record<string, unknown>;
  active_strategy?: Record<string, unknown> | null;
  portfolio_context: Record<string, unknown>;
  pending_tasks: PendingConversationTaskContract[];
  remembered_terms: Record<string, string>;
  last_message_id?: string | null;
  updated_at: string;
  metadata: Record<string, unknown>;
};

export type MemoryFactContract = {
  memory_id: string;
  thread_id: string;
  key: string;
  value: unknown;
  confidence: number;
  status: MemoryStatus;
  source_message_id?: string | null;
  created_at: string;
  updated_at: string;
  metadata: Record<string, unknown>;
};

export type ToolEvidenceContract = {
  evidence_id: string;
  thread_id: string;
  tool_name: string;
  tool_call_id?: string | null;
  claim_types: string[];
  request: Record<string, unknown>;
  result: Record<string, unknown>;
  status: EvidenceStatus;
  observed_at: string;
  expires_at?: string | null;
  metadata: Record<string, unknown>;
};

export type ThreadedChatRequest = {
  message: string;
  thread_id?: string | null;
  parent_message_id?: string | null;
  client_message_id?: string | null;
  stream?: boolean;
  metadata?: Record<string, unknown>;
};

export type ThreadedChatResponse = {
  status: "ok" | "error" | "blocked";
  thread_id: string;
  user_message_id: string;
  assistant_message_id?: string | null;
  message: string;
  intent?: string | null;
  symbol?: string | null;
  provider?: string | null;
  model?: string | null;
  tool_truth_state: ToolTruthState;
  evidence: ToolEvidenceContract[];
  memory_updates: MemoryFactContract[];
  conversation_state?: ConversationStateContract | null;
  error?: string | null;
  metadata: Record<string, unknown>;
};

export const CHAT_CONTRACT_VERSION =
  "134A.v1" as const;
