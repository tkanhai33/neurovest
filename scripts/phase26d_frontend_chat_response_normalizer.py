#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(".").resolve()
CHAT = ROOT / "frontend/services/chatService.ts"

text = CHAT.read_text()

text = text.replace(
'''export function normalizeChatReply(data: ChatResponse): string {
  if (typeof data.message === "string" && data.message.trim()) return data.message;
  if (typeof data.error === "string" && data.error.trim()) return data.error;

  if (typeof data.response === "object" && data.response !== null && "message" in data.response) {
    const response = data.response as { message?: unknown };
    if (typeof response.message === "string" && response.message.trim()) return response.message;
  }

  return JSON.stringify(data.response ?? data, null, 2);
}''',
'''export function normalizeChatReply(data: ChatResponse): string {
  const first = data as Record<string, unknown>;

  if (typeof first.message === "string" && first.message.trim()) return first.message;
  if (typeof first.error === "string" && first.error.trim()) return first.error;

  const response = first.response;

  if (typeof response === "string" && response.trim()) return response;

  if (response && typeof response === "object") {
    const second = response as Record<string, unknown>;

    if (typeof second.message === "string" && second.message.trim()) return second.message;
    if (typeof second.error === "string" && second.error.trim()) return second.error;

    const nested = second.response;

    if (typeof nested === "string" && nested.trim()) return nested;

    if (nested && typeof nested === "object") {
      const third = nested as Record<string, unknown>;

      if (typeof third.message === "string" && third.message.trim()) return third.message;
      if (typeof third.error === "string" && third.error.trim()) return third.error;
    }
  }

  return "Neuro responded, but no readable message was returned.";
}'''
)

CHAT.write_text(text)
print("patched Phase 26D frontend chat response normalizer")
