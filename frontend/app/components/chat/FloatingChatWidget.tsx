"use client";

import Image from "next/image";

import {
  useCallback,
  useEffect,
  useState,
} from "react";

import {
  createChatMessage,
  getTrainingRun,
  normalizeChatMeta,
  normalizeChatReply,
  normalizeTrainingRun,
  sendChatMessage,
  type ChatMessage,
  type TrainingRunSummary,
} from "../../../services/chatService";

export default function FloatingChatWidget() {
  const [open, setOpen] =
    useState(false);

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
      "general conversation",
    );

  const [loading, setLoading] =
    useState(false);

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
          normalizeChatReply(data),
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

  return (
    <div className="fixed bottom-5 right-5 z-[999999] sm:bottom-6 sm:right-6">
      {open && (
        <section className="mb-4 w-[min(380px,calc(100vw-2.5rem))] rounded-3xl border border-cyan-300/35 bg-slate-950/95 p-4 shadow-[0_0_60px_rgba(34,211,238,0.24)] backdrop-blur-xl">
          <div className="mb-3 flex items-center justify-between gap-4">
            <div className="flex min-w-0 items-center gap-3">
              <div className="relative h-11 w-11 shrink-0 overflow-hidden rounded-full border border-cyan-300/60 shadow-[0_0_20px_rgba(34,211,238,0.35)]">
                <Image
                  src="/images/neuro/chat_hero.png"
                  alt=""
                  fill
                  sizes="44px"
                  className="object-cover"
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

            <button
              type="button"
              onClick={() =>
                setOpen(false)
              }
              className="nv-button nv-button-secondary nv-button-sm"
            >
              Close
            </button>
          </div>

          <div className="mb-3 max-h-72 space-y-2 overflow-auto rounded-2xl border border-white/[0.08] bg-slate-900/65 p-3">
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
                        ? "inline-block max-w-[85%] rounded-2xl bg-cyan-300 px-3 py-2 text-sm font-semibold text-slate-950"
                        : "inline-block max-w-[85%] rounded-2xl border border-white/[0.09] bg-slate-950 px-3 py-2 text-sm text-slate-200"
                    }
                  >
                    <p>
                      {item.content}
                    </p>

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

                        <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-slate-800">
                          <div
                            className="h-full rounded-full bg-cyan-300 transition-[width] duration-500"
                            style={{
                              width:
                                `${Math.min(
                                  100,
                                  Math.max(
                                    0,
                                    Number(
                                      item.trainingRun
                                        .progress_percent ??
                                      0
                                    )
                                  )
                                )}%`,
                            }}
                          />
                        </div>

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
              <div className="text-left">
                <div className="inline-block rounded-2xl border border-white/[0.09] bg-slate-950 px-3 py-2 text-sm text-slate-400">
                  Neuro is thinking...
                </div>
              </div>
            )}
          </div>

          <div className="mb-3">
            <span className="nv-status-badge" data-tone="info">
              {chatMeta}
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
            className="nv-input min-h-24 resize-none"
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
          <Image
            src="/images/neuro/chat_hero.png"
            alt=""
            fill
            priority
            sizes="72px"
            className="scale-110 object-cover transition duration-200 group-hover:scale-[1.16]"
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
