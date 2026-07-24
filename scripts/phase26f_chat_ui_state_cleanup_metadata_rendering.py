#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(".").resolve()
PAGE = ROOT / "frontend/app/page.tsx"

text = PAGE.read_text()

# Remove unused chatThinking state; existing loading state already drives typing indicator.
text = text.replace('  const [chatThinking, setChatThinking] = useState(false);\n', '')

# Ensure chat metadata is updated from backend response.
text = text.replace(
'''      const data = await sendChatMessage(cleanMessage);
      const assistantMessage = createChatMessage("assistant", normalizeChatReply(data));''',
'''      const data = await sendChatMessage(cleanMessage);
      setChatMeta(normalizeChatMeta(data));
      const assistantMessage = createChatMessage("assistant", normalizeChatReply(data));'''
)

text = text.replace(
'''      const data = await sendChatMessage(message);
      const assistantMessage = createChatMessage("assistant", normalizeChatReply(data));''',
'''      const data = await sendChatMessage(message);
      setChatMeta(normalizeChatMeta(data));
      const assistantMessage = createChatMessage("assistant", normalizeChatReply(data));'''
)

# Fallback for older shape.
text = text.replace(
'''      const data = await sendChatMessage(cleanMessage);
      setReply(data);''',
'''      const data = await sendChatMessage(cleanMessage);
      setChatMeta(normalizeChatMeta(data));
      setReply(data);'''
)

# Render metadata chip in the floating chat panel.
if "{chatMeta}" not in text:
    text = text.replace(
'''          <div className="mb-3 flex items-center justify-between">''',
'''          <div className="mb-3 flex items-center justify-between">''',
1
    )

    text = text.replace(
'''          <div className="max-h-64 overflow-auto rounded-2xl border border-slate-800 bg-slate-900/60 p-3">''',
'''          <div className="mb-3 inline-flex rounded-full border border-cyan-400/30 px-2 py-1 text-xs text-cyan-200">
            {chatMeta}
          </div>

          <div className="max-h-64 overflow-auto rounded-2xl border border-slate-800 bg-slate-900/60 p-3">''',
1
    )

PAGE.write_text(text)
print("patched Phase 26F chat UI state cleanup + metadata rendering")
