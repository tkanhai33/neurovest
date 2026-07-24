#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(".").resolve()
CHAT_SERVICE_TS = r'''export type ChatRole = "user" | "assistant" | "system";

export type ChatMessage = {
  id: string;
  role: ChatRole;
  content: string;
  createdAt: string;
};

export type ChatResponse = {
  status?: string;
  response?: unknown;
  message?: string;
  error?: string;
};

export function createChatMessage(role: ChatRole, content: string): ChatMessage {
  return {
    id: `${role}-${Date.now()}-${Math.random().toString(16).slice(2)}`,
    role,
    content,
    createdAt: new Date().toISOString(),
  };
}

export function normalizeChatReply(data: ChatResponse): string {
  if (typeof data.message === "string" && data.message.trim()) return data.message;
  if (typeof data.error === "string" && data.error.trim()) return data.error;

  if (typeof data.response === "object" && data.response !== null && "message" in data.response) {
    const response = data.response as { message?: unknown };
    if (typeof response.message === "string" && response.message.trim()) return response.message;
  }

  return JSON.stringify(data.response ?? data, null, 2);
}

export async function sendChatMessage(message: string): Promise<ChatResponse> {
  const cleanMessage = message.trim();

  if (!cleanMessage) return { status: "error", error: "missing_message" };

  const response = await fetch("/api/v1/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    cache: "no-store",
    body: JSON.stringify({ message: cleanMessage }),
  });

  return await response.json();
}
'''

(ROOT / "frontend/services/chatService.ts").write_text(CHAT_SERVICE_TS)

p = ROOT / "scripts/phase20_floating_chat_widget_service_chain.py"
text = p.read_text()

start = text.find('(services / "chatService.ts").write_text(r')
end = text.find("''')", start)

if start == -1 or end == -1:
    raise RuntimeError("Could not locate old chatService writer")

new_writer = '(services / "chatService.ts").write_text(' + repr(CHAT_SERVICE_TS) + ')'
text = text[:start] + new_writer + text[end + 4:]

p.write_text(text)
print("fixed live chatService and Phase 20 generator")
