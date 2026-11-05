"use client";

import { getStoredChatThread } from "../../../services/chatService";

import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";

const CHAT_ACTIVITY_STEPS = [
  "Understanding your question",
  "Checking relevant context",
  "Preparing a grounded response",
] as const;


function stripInternalCitationTokens(
  value: string,
): string {
  return value.replace(
    /\s*\[chunk_[a-f0-9]+\]/gi,
    "",
  ).replace(
    /[ \t]+\n/g,
    "\n",
  ).trim();
}

import {
  createChatMessage,
  loadChatHistory,
  getTrainingRun,
  normalizeChatMeta,
  normalizeChatReply,
  normalizeTrainingRun,
  sendChatMessage,
  type ChatMessage,
  type TrainingRunSummary,
} from "../../../services/chatService";

// NEUROVEST_V88_SAFE_ASSISTANT_MARKDOWN
// Render a small, explicitly supported Markdown subset with
// React elements. Never interpret message text as HTML.
function renderInlineMarkdown(
  text: string,
  prefix: string,
): ReactNode[] {
  return text
    .split(/(\*\*[^*\n]+\*\*|`[^`\n]+`|\*[^*\n]+\*)/g)
    .filter((part) => part.length > 0)
    .map((part, index) => {
      const key = `${prefix}-inline-${index}`;

      if (
        part.startsWith("**") &&
        part.endsWith("**")
      ) {
        return (
          <strong key={key} className="font-bold">
            {part.slice(2, -2)}
          </strong>
        );
      }

      if (
        part.startsWith("`") &&
        part.endsWith("`")
      ) {
        return (
          <code
            key={key}
            className="rounded bg-white/10 px-1 py-0.5 font-mono text-[0.9em]"
          >
            {part.slice(1, -1)}
          </code>
        );
      }

      if (
        part.startsWith("*") &&
        part.endsWith("*")
      ) {
        return (
          <em key={key}>
            {part.slice(1, -1)}
          </em>
        );
      }

      return part;
    });
}

function renderChatMessageContent(
  content: string,
  assistant: boolean,
): ReactNode[] {
  // Preserve the widget's existing Markdown-link and
  // raw-URL handling, including its cyan link styling.
  return content
    .split(
      /(\[[^\]]+\]\(https?:\/\/[^\s)]+\)|https?:\/\/[^\s]+)/g,
    )
    .flatMap((part, index): ReactNode[] => {
      const markdownMatch = part.match(
        /^\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)$/,
      );

      const rawUrlMatch = part.match(
        /^(https?:\/\/[^\s]+)$/,
      );

      const href = markdownMatch
        ? markdownMatch[2]
        : rawUrlMatch
          ? rawUrlMatch[1]
          : null;

      if (href) {
        return [
          <a
            key={`link-${index}`}
            href={href}
            target="_blank"
            rel="noreferrer"
            className="text-cyan-300 underline underline-offset-2 hover:text-cyan-200"
          >
            {markdownMatch ? markdownMatch[1] : href}
          </a>,
        ];
      }

      // User messages retain the original plain-text behavior.
      if (!assistant) {
        return [part];
      }

      return renderInlineMarkdown(part, `part-${index}`);
    });
}


// NEUROVEST_R87_BLOCK_MARKDOWN_RENDERER
// Structural Markdown rendering without HTML injection.
// Existing inline formatting and URL handling remain authoritative.

function renderNeuroMarkdown(
  content: string,
  assistant: boolean,
): ReactNode[] {
  if (!assistant) {
    return [content];
  }

  const rawLines = content.replace(/\r\n?/g, "\n").split("\n");
  const result: ReactNode[] = [];
  let i = 0;

  function normalize(line: string): string {
    return line
      .replace(/^(\s*)\\(#{1,6}\s)/, "$1$2")
      .replace(/^(\s*)\\([-*+]\s)/, "$1$2")
      .replace(/^(\s*)\\(>\s)/, "$1$2")
      .replace(/^(\s*)\\(```)/, "$1$2");
  }

  function isTableDivider(line: string): boolean {
    const stripped = normalize(line).trim().replace(/\\\|/g, "|");
    return /^\|?[\s:|-]+\|?$/.test(stripped)
      && stripped.includes("-");
  }

  function cells(line: string): string[] {
    const stripped = normalize(line).trim().replace(/\\\|/g, "|");
    return stripped
      .replace(/^\|/, "")
      .replace(/\|$/, "")
      .split("|")
      .map((cell) => cell.trim());
  }

  function isBlock(line: string): boolean {
    const value = normalize(line).trim();
    return /^#{1,6}\s/.test(value)
      || /^[-*+]\s/.test(value)
      || /^\d+[.)]\s/.test(value)
      || /^>\s/.test(value)
      || /^```/.test(value)
      || /^(-{3,}|\*{3,}|_{3,})$/.test(value);
  }

  while (i < rawLines.length) {
    const line = normalize(rawLines[i]);
    const trimmed = line.trim();

    if (!trimmed) {
      i++;
      continue;
    }

    const fence = trimmed.match(/^```([\w+-]*)\s*$/);

    if (fence) {
      const language = fence[1];
      const body: string[] = [];
      const start = i;
      i++;

      while (i < rawLines.length
        && !/^```/.test(normalize(rawLines[i]).trim())) {
        body.push(rawLines[i]);
        i++;
      }

      if (i < rawLines.length) {
        i++;
      }

      result.push(
        <pre
          key={`code-${start}`}
          className="my-3 max-w-full overflow-x-auto rounded-xl border border-white/10 bg-slate-900 p-3 text-xs leading-6 text-slate-100"
        >
          <code data-language={language || undefined}>
            {body.join("\n")}
          </code>
        </pre>,
      );
      continue;
    }

    const heading = trimmed.match(/^(#{1,6})\s+(.+)$/);

    if (heading) {
      const level = heading[1].length;
      const text = heading[2];
      result.push(
        <div
          key={`heading-${i}`}
          role="heading"
          aria-level={level}
          className={
            level <= 2
              ? "mt-4 mb-2 font-bold text-base text-slate-50"
              : "mt-3 mb-1 font-semibold text-sm text-slate-50"
          }
        >
          {renderChatMessageContent(text, true)}
        </div>,
      );
      i++;
      continue;
    }

    if (/^(-{3,}|\*{3,}|_{3,})$/.test(trimmed)) {
      result.push(
        <hr key={`rule-${i}`} className="my-3 border-white/10" />,
      );
      i++;
      continue;
    }

    if (i + 1 < rawLines.length
      && line.includes("|")
      && isTableDivider(rawLines[i + 1])) {
      const headers = cells(line);
      const rows: string[][] = [];
      const start = i;
      i += 2;

      while (i < rawLines.length) {
        const next = normalize(rawLines[i]);

        if (!next.trim() || !next.includes("|")) {
          break;
        }

        rows.push(cells(next));
        i++;
      }

      result.push(
        <div key={`table-${start}`} className="my-3 max-w-full overflow-x-auto">
          <table className="w-full border-collapse text-left text-xs">
            <thead>
              <tr>
                {headers.map((value, index) => (
                  <th
                    key={`header-${index}`}
                    className="border-b border-white/20 px-2 py-2 font-semibold text-cyan-100"
                  >
                    {renderChatMessageContent(value, true)}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, rowIndex) => (
                <tr key={`row-${rowIndex}`}>
                  {headers.map((_, cellIndex) => (
                    <td
                      key={`cell-${cellIndex}`}
                      className="border-b border-white/10 px-2 py-2 align-top"
                    >
                      {renderChatMessageContent(row[cellIndex] || "", true)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>,
      );
      continue;
    }

    const bullet = trimmed.match(/^([-*+]|\d+[.)])\s/);

    if (bullet) {
      const ordered = /^\d/.test(bullet[1]);
      const orderedStart = ordered ? Number.parseInt(bullet[1], 10) : 1;
      const entries: string[] = [];
      const start = i;

      while (i < rawLines.length) {
        const next = normalize(rawLines[i]).trim();
        const match = next.match(
          ordered ? /^\d+[.)]\s+(.+)$/ : /^[-*+]\s+(.+)$/,
        );

        if (!match) {
          break;
        }

        entries.push(match[1]);
        i++;
      }

      const children = entries.map((value, index) => (
        <li key={`item-${index}`} className="my-1">
          {renderChatMessageContent(value, true)}
        </li>
      ));

      result.push(
        ordered ? (
          <ol
            start={orderedStart}
            key={`list-${start}`}
            className="my-2 list-decimal space-y-1 pl-5"
          >
            {children}
          </ol>
        ) : (
          <ul
            key={`list-${start}`}
            className="my-2 list-disc space-y-1 pl-5"
          >
            {children}
          </ul>
        ),
      );
      continue;
    }

    if (/^>\s/.test(trimmed)) {
      const quote: string[] = [];
      const start = i;

      while (i < rawLines.length) {
        const next = normalize(rawLines[i]).trim();
        if (!/^>\s/.test(next)) {
          break;
        }
        quote.push(next.replace(/^>\s*/, ""));
        i++;
      }

      result.push(
        <blockquote
          key={`quote-${start}`}
          className="my-2 border-l-2 border-cyan-400/50 pl-3 italic text-slate-300"
        >
          {quote.map((value, index) => (
            <div key={`quote-line-${index}`}>
              {renderChatMessageContent(value, true)}
            </div>
          ))}
        </blockquote>,
      );
      continue;
    }

    const paragraph: string[] = [];
    const start = i;

    while (i < rawLines.length) {
      const next = normalize(rawLines[i]);

      if (!next.trim() || isBlock(next)) {
        break;
      }

      if (i + 1 < rawLines.length
        && next.includes("|")
        && isTableDivider(rawLines[i + 1])) {
        break;
      }

      paragraph.push(next);
      i++;
    }

    if (paragraph.length === 0) {
      paragraph.push(line);
      i++;
    }

    result.push(
      <p key={`paragraph-${start}`} className="my-2 whitespace-pre-wrap">
        {paragraph.map((value, index) => (
          <span key={`paragraph-line-${index}`}>
            {index > 0 ? "\n" : null}
            {renderChatMessageContent(value, true)}
          </span>
        ))}
      </p>,
    );
  }

  return result;
}

export default function FloatingChatWidget() {
  const [open, setOpen] =
    useState(false);

  // F1: Presentation state only. Conversation state stays
  // mounted when switching between compact and expanded.
  const [expanded, setExpanded] =
    useState(false);

  const messageScrollRef =
    useRef<HTMLDivElement>(null);

  const [message, setMessage] =
    useState("");

  const [messages, setMessages] =
    useState<ChatMessage[]>([
      createChatMessage(
        "assistant",
        "Neuro online. Standing guard.",
      ),
    ]);

  const [chatMeta, setChatMeta] =
    useState<string>(
      "Neuro chat",
    );

  const [loading, setLoading] =
    useState(false);

  const [activityStep, setActivityStep] =
    useState(0);

  // Keep newly received messages visible in both layouts.
  // No external requests or conversation resets.
  useEffect(() => {
    if (!open) {
      return;
    }

    const node = messageScrollRef.current;
    if (node) {
      node.scrollTop = node.scrollHeight;
    }
  }, [messages.length, open, expanded, loading]);

  useEffect(() => {
    const storedThread = getStoredChatThread();
    if (!storedThread?.thread_id) {
      return;
    }

    let cancelled = false;
    void loadChatHistory(storedThread.thread_id).then(history => {
      if (
        cancelled ||
        history.length === 0 ||
        getStoredChatThread()?.thread_id !== storedThread.thread_id
      ) {
        return;
      }

      setMessages(current => {
        const greeting = current.filter(
          item =>
            item.role === "assistant" &&
            item.content === "Neuro online. Standing guard."
        );
        return [...greeting, ...history];
      });
    });

    return () => {
      cancelled = true;
    };
  }, []);

  const send = useCallback(async () => {
    const cleanMessage =
      message.trim();

    if (!cleanMessage) {
      return;
    }

    const userMessage =
      createChatMessage(
        "user",
        cleanMessage,
      );

    setMessages(
      (current) => [
        ...current,
        userMessage,
      ],
    );

    setMessage("");
    setLoading(true);

    try {
      const data =
        await sendChatMessage(
          cleanMessage,
        );

      setChatMeta(
        normalizeChatMeta(data),
      );

      const assistantMessage =
        createChatMessage(
          "assistant",
          stripInternalCitationTokens(
            normalizeChatReply(data),
          ),
          normalizeTrainingRun(
            data.training_run
          ),
        );

      setMessages(
        (current) => [
          ...current,
          assistantMessage,
        ],
      );
    } catch (error) {
      const errorMessage =
        createChatMessage(
          "assistant",
          String(error),
        );

      setMessages(
        (current) => [
          ...current,
          errorMessage,
        ],
      );
    } finally {
      setLoading(false);
    }
  }, [message]);

  useEffect(() => {
    queueMicrotask(() => {
      setActivityStep(0);
    });

    if (!loading) {
      return;
    }

    const contextTimer = window.setTimeout(
      () => setActivityStep(1),
      650,
    );

    const responseTimer = window.setTimeout(
      () => setActivityStep(2),
      1_300,
    );

    return () => {
      window.clearTimeout(contextTimer);
      window.clearTimeout(responseTimer);
    };
  }, [loading]);

  useEffect(() => {
    const receiveStrategyDraft = (
      event: Event,
    ): void => {
      const detail =
        (event as CustomEvent<{
          message?: unknown;
        }>).detail;

      const draft =
        typeof detail?.message === "string"
          ? detail.message.trim()
          : "";

      if (!draft) {
        return;
      }

      setOpen(true);
      setMessage(draft);
    };

    window.addEventListener(
      "neurovest:strategy-explanation-draft",
      receiveStrategyDraft,
    );

    return () => {
      window.removeEventListener(
        "neurovest:strategy-explanation-draft",
        receiveStrategyDraft,
      );
    };
  }, []);


  useEffect(() => {
    const activeRuns =
      messages
        .filter(
          (
            item
          ): item is ChatMessage & {
            trainingRun:
              TrainingRunSummary;
          } => {
            const run =
              item.trainingRun;

            if (!run?.run_id) {
              return false;
            }

            const status =
              String(
                run.status ?? ""
              )
                .trim()
                .toLowerCase();

            return ![
              "completed",
              "failed",
              "cancelled",
              "canceled",
            ].includes(status);
          }
        );

    if (activeRuns.length === 0) {
      return;
    }

    let cancelled = false;

    const poll = async (): Promise<void> => {
      const updates =
        await Promise.all(
          activeRuns.map(
            async (item) => {
              try {
                const trainingRun =
                  await getTrainingRun(
                    item.trainingRun.run_id
                  );

                return {
                  messageId: item.id,
                  trainingRun,
                };
              } catch {
                return null;
              }
            }
          )
        );

      if (cancelled) {
        return;
      }

      setMessages(
        current =>
          current.map(item => {
            const update =
              updates.find(
                candidate =>
                  candidate?.messageId ===
                  item.id
              );

            return update
              ? {
                  ...item,
                  trainingRun:
                    update.trainingRun,
                }
              : item;
          })
      );
    };

    void poll();

    const interval =
      window.setInterval(
        () => {
          void poll();
        },
        1500
      );

    return () => {
      cancelled = true;

      window.clearInterval(
        interval
      );
    };
  }, [messages]);

  // NEUROVEST_CHAT_FINDINGS_SSE_V2
  useEffect(() => {
    if (!open) {
      return;
    }

    let stream: EventSource | null = null;
    let activeThread = "";

    const connect = () => {
      const threadId = getStoredChatThread()?.thread_id ?? "";

      if (threadId === activeThread) {
        return;
      }

      stream?.close();
      stream = null;
      activeThread = threadId;

      if (!threadId) {
        return;
      }

      stream = new EventSource(
        `/api/v1/chat/threads/${encodeURIComponent(threadId)}/events`
      );

      stream.addEventListener("chat_message", (event: Event) => {
        if (!(event instanceof MessageEvent)) {
          return;
        }

        try {
          const payload = JSON.parse(event.data) as {
            message_id?: string;
            thread_id?: string;
            role?: string;
            content?: string;
            intent?: string;
          };

          if (
            payload.thread_id !== activeThread ||
            payload.role !== "assistant" ||
            payload.intent !== "connected_owner_training_findings" ||
            typeof payload.message_id !== "string" ||
            typeof payload.content !== "string"
          ) {
            return;
          }

          const messageId = payload.message_id;
          const content = payload.content;

          setMessages(current => {
            if (current.some(item => item.id === messageId)) {
              return current;
            }

            return [
              ...current,
              {
                id: messageId,
                role: "assistant" as const,
                content,
              },
            ];
          });
        } catch {
          // Reject malformed event payloads.
        }
      });
    };

    connect();

    window.addEventListener(
      "neurovest:chat-thread-updated",
      connect
    );

    window.addEventListener("storage", connect);

    return () => {
      window.removeEventListener(
        "neurovest:chat-thread-updated",
        connect
      );

      window.removeEventListener("storage", connect);

      stream?.close();
    };
  }, [open]);

  return (
    <div className="fixed bottom-3 right-3 z-[999999] sm:bottom-6 sm:right-6">
      {open && (
        <section
          aria-label="Neuro conversation"
          data-chat-mode={expanded ? "expanded" : "compact"}
          className={
            expanded
              ? "mb-3 flex h-[min(72dvh,800px)] max-h-[calc(100dvh-7rem)] w-[min(560px,calc(100vw-1.5rem))] flex-col overflow-hidden rounded-3xl border border-cyan-300/35 bg-slate-950/95 p-4 shadow-[0_0_60px_rgba(34,211,238,0.24)] backdrop-blur-xl sm:mb-4"
              : "mb-3 w-[min(380px,calc(100vw-1.5rem))] rounded-3xl border border-cyan-300/35 bg-slate-950/95 p-4 shadow-[0_0_60px_rgba(34,211,238,0.24)] backdrop-blur-xl sm:mb-4"
          }
        >
          <div className="mb-3 flex items-center justify-between gap-4">
            <div className="flex min-w-0 items-center gap-3">
              <div className="relative h-11 w-11 shrink-0 overflow-hidden rounded-full border border-cyan-300/60 shadow-[0_0_20px_rgba(34,211,238,0.35)]">
                <img
                  src="/images/neuro/chat_hero.png"
                  alt=""
                  width={44}
                  height={44}
                  className="h-full w-full object-cover"
                />
              </div>

              <div className="min-w-0">
                <p className="nv-eyebrow">
                  Neuro Chat
                </p>

                <h2 className="truncate text-lg font-black text-white">
                  Assistant
                </h2>
              </div>
            </div>

            <div className="flex shrink-0 items-center gap-2">
              <button
                type="button"
                onClick={() => setExpanded((value) => !value)}
                aria-pressed={expanded}
                aria-label={
                  expanded
                    ? "Return Neuro chat to compact view"
                    : "Expand Neuro chat"
                }
                title={
                  expanded
                    ? "Compact chat"
                    : "Expand chat"
                }
                className="nv-button nv-button-secondary nv-button-sm"
              >
                {expanded ? "Compact" : "Expand"}
              </button>

              <button
                type="button"
                onClick={() => setOpen(false)}
                aria-label="Close Neuro chat"
                className="nv-button nv-button-secondary nv-button-sm"
              >
                Close
              </button>
            </div>
          </div>

          <div
            ref={messageScrollRef}
            role="log"
            aria-label="Neuro chat messages"
            aria-live="polite"
            aria-relevant="additions"
            className={
              expanded
                ? "mb-3 min-h-0 flex-1 space-y-3 overflow-y-auto overscroll-contain rounded-2xl border border-white/[0.08] bg-slate-900/65 p-3 sm:p-4"
                : "mb-3 max-h-72 space-y-2 overflow-y-auto overscroll-contain rounded-2xl border border-white/[0.08] bg-slate-900/65 p-3"
            }
          >
            {messages.map(
              (item) => (
                <div
                  key={item.id}
                  className={
                    item.role === "user"
                      ? "text-right"
                      : "text-left"
                  }
                >
                  <div
                    className={
                      item.role === "user"
                        ? "inline-block max-w-[90%] break-words rounded-2xl bg-cyan-300 px-3 py-2 text-sm font-semibold leading-6 text-slate-950"
                        : "inline-block max-w-[95%] break-words rounded-2xl border border-white/[0.09] bg-slate-950 px-3 py-2 text-sm leading-6 text-slate-200"
                    }
                  >
                    <div className="min-w-0">
                      {renderNeuroMarkdown(
                        item.content,
                        item.role === "assistant",
                      )}
                    </div>

                    {item.trainingRun && (
                      <div
                        data-testid="chat-training-chip"
                        className="mt-3 min-w-[235px] rounded-xl border border-cyan-300/25 bg-cyan-300/[0.06] p-3 text-left"
                      >
                        <div className="flex items-center justify-between gap-3">
                          <span className="text-[10px] font-black uppercase tracking-[0.16em] text-cyan-200">
                            {[
                              "completed",
                            ].includes(
                              String(
                                item.trainingRun
                                  .status ?? ""
                              ).toLowerCase()
                            )
                              ? "Training complete"
                              : [
                                  "failed",
                                  "cancelled",
                                  "canceled",
                                ].includes(
                                  String(
                                    item.trainingRun
                                      .status ?? ""
                                  ).toLowerCase()
                                )
                                ? "Training stopped"
                                : "Training active"}
                          </span>

                          <span className="text-[10px] font-bold uppercase text-slate-400">
                            {item.trainingRun.status ??
                              "queued"}
                          </span>
                        </div>

                        <p className="mt-2 text-xs font-semibold text-slate-200">
                          {item.trainingRun.universe ===
                          "canada"
                            ? "Canadian symbols"
                            : (
                                item.trainingRun.universe ??
                                "Training universe"
                              )}
                          {" · "}
                          {item.trainingRun.scope ===
                          "user"
                            ? "Your session"
                            : (
                                item.trainingRun.scope ??
                                "Bounded"
                              )}
                        </p>

                        <progress
                          className="nv-csp-progress nv-csp-progress-cyan mt-3"
                          max="100"
                          value={
                            Math.min(
                              100,
                              Math.max(
                                0,
                                Number(
                                  item.trainingRun
                                    .progress_percent ??
                                  0
                                )
                              )
                            )
                          }
                          aria-label="Training run progress"
                        />

                        <div className="mt-2 flex items-center justify-between gap-3 text-[10px] text-slate-400">
                          <span>
                            {Math.round(
                              Number(
                                item.trainingRun
                                  .progress_percent ??
                                0
                              )
                            )}
                            %
                          </span>

                          <span>
                            {item.trainingRun
                              .eligible_symbol_count !=
                            null
                              ? `${item.trainingRun.eligible_symbol_count} symbols`
                              : `${item.trainingRun.duration_seconds ?? 0}s bounded`}
                          </span>
                        </div>

                        {item.trainingRun.status ===
                          "completed" && (
                          <p className="mt-2 text-[10px] font-semibold text-emerald-300">
                            {item.trainingRun
                              .rows_evaluated != null
                              ? `${item.trainingRun.rows_evaluated.toLocaleString()} rows evaluated`
                              : "Session completed safely"}
                          </p>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ),
            )}

            {loading && (
              <div
                className="text-left"
                aria-live="polite"
                aria-label="Neuro activity"
              >
                <div className="inline-flex items-center gap-2 rounded-2xl border border-cyan-300/20 bg-slate-950 px-3 py-2 text-sm text-slate-300">
                  <span
                    aria-hidden="true"
                    className="h-2 w-2 shrink-0 animate-pulse rounded-full bg-cyan-300 shadow-[0_0_12px_rgba(34,211,238,0.9)]"
                  />

                  <span>
                    {
                      CHAT_ACTIVITY_STEPS[
                        activityStep
                      ]
                    }
                  </span>
                </div>
              </div>
            )}
          </div>

          <div className="mb-3">
            <span className="nv-status-badge" data-tone="info">
              {chatMeta.replace(
                /^\s*general(?:[_\s-]+)conversation(?=\s*·|$)/i,
                "Neuro chat",
              )}
            </span>
          </div>

          <label
            htmlFor="floating-neuro-message"
            className="sr-only"
          >
            Message Neuro
          </label>

          <textarea
            id="floating-neuro-message"
            value={message}
            onChange={(event) =>
              setMessage(
                event.target.value,
              )
            }
            onKeyDown={(event) => {
              if (
                event.key === "Enter" &&
                !event.shiftKey
              ) {
                event.preventDefault();
                void send();
              }
            }}
            className={
              expanded
                ? "nv-input min-h-24 max-h-40 shrink-0 resize-y"
                : "nv-input min-h-24 resize-none"
            }
            placeholder="Ask Neuro..."
          />

          <button
            type="button"
            onClick={() =>
              void send()
            }
            disabled={loading}
            className="nv-button nv-button-primary nv-button-md mt-3 w-full"
          >
            {loading
              ? "Sending"
              : "Send"}
          </button>
        </section>
      )}

      <button
        type="button"
        onClick={() =>
          setOpen(
            (value) => !value,
          )
        }
        aria-expanded={open}
        aria-label={
          open
            ? "Close Neuro chat"
            : "Open Neuro chat"
        }
        className="group relative flex min-h-[72px] items-center rounded-full border-2 border-cyan-300 bg-[linear-gradient(135deg,rgba(4,20,32,0.98),rgba(6,30,40,0.98))] pr-7 text-white shadow-[0_0_34px_rgba(34,211,238,0.48)] transition duration-200 hover:-translate-y-1 hover:shadow-[0_0_48px_rgba(34,211,238,0.68)]"
      >
        <span className="relative -ml-[2px] mr-4 h-[72px] w-[72px] shrink-0 overflow-hidden rounded-full border-2 border-cyan-300 shadow-[0_0_26px_rgba(34,211,238,0.62)]">
          <img
            src="/images/neuro/chat_hero.png"
            alt=""
            width={72}
            height={72}
            className="h-full w-full scale-110 object-cover transition duration-200 group-hover:scale-[1.16]"
          />

          <span
            aria-hidden="true"
            className="absolute -right-[3px] top-[9px] h-[50px] w-[7px] bg-[#061e28]"
          />
        </span>

        <span className="text-lg font-black tracking-[-0.02em]">
          Chat
        </span>
      </button>
    </div>
  );
}
