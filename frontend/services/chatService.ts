import {
  csrfHeaders,
} from "../lib/clientCsrf";
import type {
  ThreadedChatRequest,
  ThreadedChatResponse,
} from "./chat/chatContracts";

export type ChatRole =
  | "user"
  | "assistant";

export type TrainingRunSummary = {
  run_id: string;
  scope?: string | null;
  status?: string | null;
  duration_seconds?: number | null;
  progress_percent?: number | null;
  universe?: string | null;
  eligible_symbol_count?: number | null;
  rows_evaluated?: number | null;
  cycles?: number | null;
};

export type ChatMessage = {
  id: string;
  role: ChatRole;
  content: string;
  trainingRun?: TrainingRunSummary | null;
};

export type ChatResponsePayload =
  Partial<ThreadedChatResponse> & {
    response?:
      | string
      | {
          type?: string;
          message?: string;
          command?: string;
          symbol?: string | null;
        };

    training_run?:
      | TrainingRunSummary
      | null;
  };

export type StoredChatThread = {
  thread_id: string;
  parent_message_id: string | null;
  updated_at: string;
};

const CHAT_ENDPOINT = "/api/v1/chat";

const CHAT_THREAD_STORAGE_KEY =
  "neurovest_chat_thread_v1";

function canUseStorage(): boolean {
  return (
    typeof window !== "undefined" &&
    typeof window.localStorage !== "undefined"
  );
}

function createClientMessageId(): string {
  if (
    typeof crypto !== "undefined" &&
    typeof crypto.randomUUID === "function"
  ) {
    return `client-${crypto.randomUUID()}`;
  }

  return [
    "client",
    Date.now().toString(36),
    Math.random().toString(36).slice(2),
  ].join("-");
}

export function createChatMessage(
  role: ChatRole,
  content: string,
  trainingRun: TrainingRunSummary | null = null
): ChatMessage {
  return {
    id: [
      role,
      Date.now().toString(36),
      Math.random().toString(36).slice(2),
    ].join("-"),
    role,
    content,
    trainingRun,
  };
}

export function getStoredChatThread():
  | StoredChatThread
  | null {
  if (!canUseStorage()) {
    return null;
  }

  try {
    const raw = window.localStorage.getItem(
      CHAT_THREAD_STORAGE_KEY
    );

    if (!raw) {
      return null;
    }

    const parsed = JSON.parse(
      raw
    ) as Partial<StoredChatThread>;

    if (
      typeof parsed.thread_id !== "string" ||
      !parsed.thread_id
    ) {
      return null;
    }

    return {
      thread_id: parsed.thread_id,
      parent_message_id:
        typeof parsed.parent_message_id === "string"
          ? parsed.parent_message_id
          : null,
      updated_at:
        typeof parsed.updated_at === "string"
          ? parsed.updated_at
          : new Date().toISOString(),
    };
  } catch {
    window.localStorage.removeItem(
      CHAT_THREAD_STORAGE_KEY
    );

    return null;
  }
}

export function storeChatThread(
  response: ChatResponsePayload
): StoredChatThread | null {
  if (
    !response.thread_id ||
    !canUseStorage()
  ) {
    return null;
  }

  const state: StoredChatThread = {
    thread_id: response.thread_id,
    parent_message_id:
      response.assistant_message_id ?? null,
    updated_at: new Date().toISOString(),
  };

  window.localStorage.setItem(
    CHAT_THREAD_STORAGE_KEY,
    JSON.stringify(state)
  );

  return state;
}

export function clearStoredChatThread(): void {
  if (!canUseStorage()) {
    return;
  }

  window.localStorage.removeItem(
    CHAT_THREAD_STORAGE_KEY
  );
}

export async function sendChatMessage(
  message: string
): Promise<ChatResponsePayload> {
  const cleanMessage = message.trim();

  if (!cleanMessage) {
    throw new Error(
      "Chat message cannot be empty."
    );
  }

  const storedThread = getStoredChatThread();

  const request: ThreadedChatRequest = {
    message: cleanMessage,
    thread_id:
      storedThread?.thread_id ?? null,
    parent_message_id:
      storedThread?.parent_message_id ?? null,
    client_message_id:
      createClientMessageId(),
    stream: false,
    metadata: {
      client: "floating_chat_widget",
      contract: "134A.v1",
      frontend_phase:
        "134B5_FRONTEND_THREAD_RETENTION",
    },
  };

  const response = await fetch(
    CHAT_ENDPOINT,
    {
      method: "POST",
      headers: {
        ...csrfHeaders(),
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      cache: "no-store",
      body: JSON.stringify(request),
    }
  );

  const rawText = await response.text();

  let data: ChatResponsePayload;

  try {
    data = JSON.parse(
      rawText
    ) as ChatResponsePayload;
  } catch {
    throw new Error(
      rawText ||
        `Chat request failed with status ${response.status}.`
    );
  }

  if (!response.ok) {
    throw new Error(
      data.error ||
        normalizeChatReply(data) ||
        `Chat request failed with status ${response.status}.`
    );
  }

  storeChatThread(data);

  return data;
}


function isRecord(
  value: unknown
): value is Record<string, unknown> {
  return (
    typeof value === "object" &&
    value !== null &&
    !Array.isArray(value)
  );
}

export function normalizeTrainingRun(
  value: unknown
): TrainingRunSummary | null {
  if (!isRecord(value)) {
    return null;
  }

  const runId =
    typeof value.run_id === "string"
      ? value.run_id
      : "";

  if (!runId) {
    return null;
  }

  return {
    run_id: runId,

    scope:
      typeof value.scope === "string"
        ? value.scope
        : null,

    status:
      typeof value.status === "string"
        ? value.status
        : null,

    duration_seconds:
      typeof value.duration_seconds === "number"
        ? value.duration_seconds
        : null,

    progress_percent:
      typeof value.progress_percent === "number"
        ? value.progress_percent
        : null,

    universe:
      typeof value.universe === "string"
        ? value.universe
        : null,

    eligible_symbol_count:
      typeof value.eligible_symbol_count === "number"
        ? value.eligible_symbol_count
        : null,

    rows_evaluated:
      typeof value.rows_evaluated === "number"
        ? value.rows_evaluated
        : null,

    cycles:
      typeof value.cycles === "number"
        ? value.cycles
        : null,
  };
}

export async function getTrainingRun(
  runId: string
): Promise<TrainingRunSummary> {
  const cleanRunId = runId.trim();

  if (!cleanRunId) {
    throw new Error(
      "Training run ID is required."
    );
  }

  const response = await fetch(
    `/api/v1/training/runs/${encodeURIComponent(
      cleanRunId
    )}`,
    {
      method: "GET",
      credentials: "include",
      cache: "no-store",
      headers: {
        Accept: "application/json",
      },
    }
  );

  const payload: unknown =
    await response.json().catch(
      () => null
    );

  if (!response.ok) {
    const detail =
      isRecord(payload) &&
      typeof payload.detail === "string"
        ? payload.detail
        : (
            "Training status request failed " +
            `with status ${response.status}.`
          );

    throw new Error(detail);
  }

  const direct =
    normalizeTrainingRun(payload);

  if (direct) {
    return direct;
  }

  if (isRecord(payload)) {
    const nested =
      normalizeTrainingRun(
        payload.training_run ??
        payload.run ??
        payload.result
      );

    if (nested) {
      return nested;
    }
  }

  throw new Error(
    "Training status response did not match the required contract."
  );
}

export function normalizeChatReply(
  data: ChatResponsePayload
): string {
  if (
    typeof data.message === "string" &&
    data.message.trim()
  ) {
    return data.message;
  }

  if (
    typeof data.response === "string" &&
    data.response.trim()
  ) {
    return data.response;
  }

  if (
    data.response &&
    typeof data.response === "object"
  ) {
    if (
      typeof data.response.message === "string" &&
      data.response.message.trim()
    ) {
      return data.response.message;
    }

    const command =
      data.response.command ||
      data.response.type;

    if (command) {
      const symbol = data.response.symbol;

      return symbol
        ? `Command prepared: ${command} for ${symbol}.`
        : `Command prepared: ${command}.`;
    }
  }

  if (data.error) {
    return data.error;
  }

  return "Neuro returned an empty response.";
}

export function normalizeChatMeta(
  data: ChatResponsePayload
): string {
  const parts: string[] = [];

  if (data.intent) {
    parts.push(data.intent);
  }

  if (data.symbol) {
    parts.push(data.symbol);
  }

  if (data.provider) {
    parts.push(data.provider);
  }

  if (data.model) {
    parts.push(data.model);
  }

  if (data.thread_id) {
    parts.push(
      `thread ${data.thread_id.slice(-8)}`
    );
  }

  if (
    data.metadata?.idempotent_replay === true
  ) {
    parts.push("replayed");
  }

  return (
    parts.join(" · ") ||
    "general conversation"
  );
}
