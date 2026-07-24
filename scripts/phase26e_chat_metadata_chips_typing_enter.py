#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(".").resolve()
CHAT = ROOT / "frontend/services/chatService.ts"
PAGE = ROOT / "frontend/app/page.tsx"

chat = CHAT.read_text()

if "export function normalizeChatMeta" not in chat:
    chat += r'''

export function normalizeChatMeta(data: ChatResponse): string {
  const first = data as Record<string, unknown>;
  const outer = first.response;

  const source =
    outer && typeof outer === "object"
      ? (outer as Record<string, unknown>)
      : first;

  const intent = source.intent;
  const symbol = source.symbol;
  const status = source.status;

  const parts = [];

  if (typeof status === "string" && status.trim()) parts.push(status);
  if (typeof intent === "string" && intent.trim()) parts.push(intent.replaceAll("_", " "));
  if (typeof symbol === "string" && symbol.trim()) parts.push(symbol);

  return parts.length ? parts.join(" • ") : "general conversation";
}
'''
CHAT.write_text(chat)

page = PAGE.read_text()

if "normalizeChatMeta" not in page:
    page = page.replace(
        'import { createChatMessage, normalizeChatReply, sendChatMessage, type ChatMessage } from "../services/chatService";',
        'import { createChatMessage, normalizeChatMeta, normalizeChatReply, sendChatMessage, type ChatMessage } from "../services/chatService";'
    )

page = page.replace(
'''  const [messages, setMessages] = useState<ChatMessage[]>([
    createChatMessage("assistant", "Neuro online. Standing guard."),
  ]);''',
'''  const [messages, setMessages] = useState<ChatMessage[]>([
    createChatMessage("assistant", "Neuro online. Standing guard."),
  ]);
  const [chatMeta, setChatMeta] = useState<string>("general conversation");
  const [chatThinking, setChatThinking] = useState(false);'''
)

page = page.replace(
'''      const data = await sendChatMessage(input);
      const reply = normalizeChatReply(data);''',
'''      setChatThinking(true);
      const data = await sendChatMessage(input);
      const reply = normalizeChatReply(data);
      setChatMeta(normalizeChatMeta(data));
      setChatThinking(false);'''
)

page = page.replace(
'''    } catch (error) {
      setMessages((current) => [
        ...current,
        createChatMessage("assistant", `Chat error: ${String(error)}`),
      ]);
    }''',
'''    } catch (error) {
      setChatThinking(false);
      setChatMeta("error");
      setMessages((current) => [
        ...current,
        createChatMessage("assistant", `Chat error: ${String(error)}`),
      ]);
    }'''
)

if "Neuro is thinking" not in page:
    page = page.replace(
'''          {messages.map((message) => (''',
'''          {chatThinking && (
            <div className="rounded-xl border border-cyan-400/30 bg-slate-900/80 p-2 text-xs text-cyan-200">
              Neuro is thinking…
            </div>
          )}

          <div className="mb-2 inline-flex rounded-full border border-cyan-400/30 px-2 py-1 text-xs text-cyan-200">
            {chatMeta}
          </div>

          {messages.map((message) => ('''
    )

page = re.sub(
    r'(<input\\s+)([^>]*placeholder="Ask Neuro\\.\\.\\."[^>]*>)',
    r"""\\1onKeyDown={(event) => {
              if (event.key === "Enter") {
                event.preventDefault();
                void sendMessage();
              }
            }}
            \\2""",
    page,
    count=1,
    flags=re.S,
)

PAGE.write_text(page)
print("patched Phase 26E chat metadata chips + typing + enter send")
