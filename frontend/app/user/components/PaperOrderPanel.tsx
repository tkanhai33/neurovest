"use client";

import {
  FormEvent,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import {
  csrfHeaders,
} from "../../../lib/clientCsrf";

import {
  getLivePrice,
  type LiveQuote,
} from "../../../services/marketService";

import {
  Panel,
  StatusBadge,
  StatusMessage,
} from "../../../components/ui";

type PaperOrderAction =
  | "buy"
  | "sell";

type PaperOrderResponse = {
  request_id?: string;
  replayed?: boolean;
  order_id?: number;
  trade_status?: string;
  status?: string;
  symbol?: string;
  action?: string;
  execution_mode?: string;
  live_execution?: boolean;
  owner_scope?: string;
  trace_id?: string;
  detail?: string;
  error?: string;
};

type PaperOrderPanelProps = {
  onOrderProcessed: () =>
    void | Promise<void>;
};

const SYMBOL_PATTERN =
  /^[A-Z0-9][A-Z0-9.-]{0,14}$/;

function formatPaperOrderError(
  payload: PaperOrderResponse,
): string {
  const detail = payload.detail

  if (typeof detail === "string" && detail.trim()) {
    return detail.trim()
  }

  if (
    typeof detail === "object" &&
    detail !== null &&
    !Array.isArray(detail)
  ) {
    const record = detail as Record<string, unknown>

    for (const key of [
      "message",
      "reason",
      "error",
      "detail",
    ]) {
      const value = record[key]

      if (
        typeof value === "string" &&
        value.trim()
      ) {
        return value.trim()
      }
    }
  }

  if (
    typeof payload.error === "string" &&
    payload.error.trim()
  ) {
    return payload.error.trim()
  }

  return "The paper order was rejected."
}

function finiteQuoteNumber(
  value: number | null | undefined,
): number | null {
  return typeof value === "number" &&
    Number.isFinite(value)
    ? value
    : null;
}

function formatQuoteMoney(
  value: number | null,
  currency?: string,
): string {
  if (value === null) {
    return "Unavailable";
  }

  if (currency) {
    try {
      return new Intl.NumberFormat(
        "en-CA",
        {
          style: "currency",
          currency,
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        },
      ).format(value);
    } catch {
      // Fall through to an honest currency-neutral value.
    }
  }

  return `$${value.toFixed(2)}`;
}

function quoteReference(
  quote: LiveQuote | null,
): {
  label: string;
  value: number;
} | null {
  if (!quote) {
    return null;
  }

  const previousClose =
    finiteQuoteNumber(
      quote.previous_close,
    );

  if (previousClose !== null) {
    return {
      label: "previous close",
      value: previousClose,
    };
  }

  const open =
    finiteQuoteNumber(
      quote.open_price ??
      quote.open ??
      quote.regularMarketOpen,
    );

  if (open !== null) {
    return {
      label: "market open",
      value: open,
    };
  }

  return null;
}

export default function PaperOrderPanel({
  onOrderProcessed,
}: PaperOrderPanelProps) {
  const [
    symbol,
    setSymbol,
  ] = useState("");

  const [
    action,
    setAction,
  ] =
    useState<PaperOrderAction>(
      "buy",
    );

  const [
    confirmation,
    setConfirmation,
  ] = useState(false);

  const [
    submitting,
    setSubmitting,
  ] = useState(false);

  const [
    error,
    setError,
  ] =
    useState<string | null>(
      null,
    );

  const pendingOrderRef = useRef<{
    intent: string;
    requestId: string;
  } | null>(null);

  const [
    result,
    setResult,
  ] =
    useState<PaperOrderResponse | null>(
      null,
    );

  const [
    liveQuote,
    setLiveQuote,
  ] =
    useState<LiveQuote | null>(
      null,
    );

  const [
    quoteLoading,
    setQuoteLoading,
  ] = useState(false);

  const [
    strategyHandoffNotice,
    setStrategyHandoffNotice,
  ] =
    useState<string | null>(
      null,
    );

  const normalizedSymbol =
    useMemo(
      () =>
        symbol
          .trim()
          .toUpperCase(),
      [
        symbol,
      ],
    );

  const symbolValid =
    SYMBOL_PATTERN.test(
      normalizedSymbol,
    );

  useEffect(
    () => {
      const raw = window.sessionStorage.getItem(
        "neurovest_strategy_paper_order_intent_v1",
      );

      if (!raw) {
        return;
      }

      window.sessionStorage.removeItem(
        "neurovest_strategy_paper_order_intent_v1",
      );

      try {
        const parsed = JSON.parse(raw) as {
          symbol?: unknown;
          action?: unknown;
          source?: unknown;
        };

        const nextSymbol =
          typeof parsed.symbol === "string"
            ? parsed.symbol.trim().toUpperCase()
            : "";

        const nextAction =
          parsed.action === "buy" ||
          parsed.action === "sell"
            ? parsed.action
            : null;

        if (
          !SYMBOL_PATTERN.test(nextSymbol) ||
          !nextAction
        ) {
          return;
        }

        queueMicrotask(() => {
          setSymbol(nextSymbol);
          setAction(nextAction);
          setConfirmation(false);
          setError(null);
          setResult(null);
          setStrategyHandoffNotice(
            `Prepared ${nextAction.toUpperCase()} review for ${nextSymbol}. Confirm the paper-only disclosure before submitting.`,
          );
        });
      } catch {
        // Invalid browser-only handoff data is ignored safely.
      }
    },
    [],
  );


  useEffect(
    () => {
      let active = true;
      let loading = false;

      if (!symbolValid) {
        queueMicrotask(() => {
          setLiveQuote(null);
          setQuoteLoading(false);
        });
        return;
      }

      const refreshQuote =
        async (): Promise<void> => {
          if (loading) {
            return;
          }

          loading = true;

          if (active) {
            setQuoteLoading(true);
          }

          try {
            const nextQuote =
              await getLivePrice(
                normalizedSymbol,
              );

            if (active) {
              setLiveQuote(
                nextQuote,
              );
            }
          } catch (caught) {
            if (active) {
              setLiveQuote({
                status: "error",
                symbol:
                  normalizedSymbol,
                error:
                  caught instanceof Error
                    ? caught.message
                    : "The current quote could not be loaded.",
              });
            }
          } finally {
            loading = false;

            if (active) {
              setQuoteLoading(false);
            }
          }
        };

      const initialTimer =
        window.setTimeout(
          () => {
            void refreshQuote();
          },
          400,
        );

      const refreshTimer =
        window.setInterval(
          () => {
            void refreshQuote();
          },
          30_000,
        );

      return () => {
        active = false;

        window.clearTimeout(
          initialTimer,
        );

        window.clearInterval(
          refreshTimer,
        );
      };
    },
    [
      normalizedSymbol,
      symbolValid,
    ],
  );

  const quotePrice =
    finiteQuoteNumber(
      liveQuote?.price,
    );

  const reference =
    quoteReference(
      liveQuote,
    );

  const quoteChange =
    quotePrice !== null &&
    reference !== null
      ? quotePrice -
        reference.value
      : null;

  const quoteChangePercent =
    quoteChange !== null &&
    reference !== null &&
    reference.value !== 0
      ? (
          quoteChange /
          reference.value
        ) * 100
      : null;

  const canSubmit =
    symbolValid &&
    confirmation &&
    !submitting;

  async function submitOrder(
    event: FormEvent<HTMLFormElement>,
  ): Promise<void> {
    event.preventDefault();

    if (!symbolValid) {
      setError(
        "Enter a valid market symbol using letters, numbers, dots, or hyphens.",
      );
      return;
    }

    if (!confirmation) {
      setError(
        "Confirm that this is a simulated paper order.",
      );
      return;
    }

    // Retain an uncertain submission's identity across retries.
    // Persist it only in this browser tab, never in a cookie.
    const intent = `${normalizedSymbol}:${action}`;
    const storageKey =
      "neurovest_pending_paper_order_v1";

    let pending = pendingOrderRef.current;

    if (!pending) {
      try {
        const stored = window.sessionStorage.getItem(
          storageKey,
        );

        if (stored) {
          const candidate = JSON.parse(stored) as {
            intent?: unknown;
            requestId?: unknown;
          };

          if (
            candidate.intent === intent &&
            typeof candidate.requestId === "string" &&
            /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(
              candidate.requestId,
            )
          ) {
            pending = {
              intent,
              requestId: candidate.requestId,
            };
          }
        }
      } catch {
        // Browser storage can be unavailable or contain
        // invalid data. Keep the in-memory fallback.
      }
    }

    if (!pending || pending.intent !== intent) {
      pending = {
        intent,
        requestId: window.crypto.randomUUID(),
      };
    }

    pendingOrderRef.current = pending;

    try {
      window.sessionStorage.setItem(
        storageKey,
        JSON.stringify(pending),
      );
    } catch {
      // In-memory retry identity still works.
    }

    setSubmitting(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(
        "/api/v1/paper/orders",
        {
          method: "POST",
          credentials: "include",
          cache: "no-store",
          headers: {
            "Content-Type":
              "application/json",
            ...csrfHeaders(),
          },
          body: JSON.stringify({
            symbol:
              normalizedSymbol,
            action,
            request_id: pending.requestId,
          }),
        },
      );

      let payload:
        PaperOrderResponse;

      try {
        payload =
          await response.json() as
            PaperOrderResponse;
      } catch {
        payload = {
          status: "error",
          detail:
            "The paper-order service returned an invalid response.",
        };
      }

      if (response.status === 401) {
        window.location.assign(
          "/login?next=/user/dashboard",
        );
        return;
      }

      if (!response.ok) {
        // A definitive validation/conflict/rejection response
        // ends this attempt. Transport failures and 5xx results
        // remain uncertain and keep the same request identity.
        const detailRecord =
          typeof payload.detail === "object" &&
          payload.detail !== null &&
          !Array.isArray(payload.detail)
            ? payload.detail as Record<string, unknown>
            : null;

        const rejectionReason =
          detailRecord &&
          typeof detailRecord.reason === "string"
            ? detailRecord.reason
            : "";

        // An execution-mode block is not proof that the
        // original request never committed. Retain its ID.
        const executionModeBlocked =
          response.status === 409 &&
          rejectionReason ===
            "paper_execution_not_allowed";

        const definitiveRejection =
          response.status >= 400 &&
          response.status < 500 &&
          response.status !== 408 &&
          response.status !== 429 &&
          !executionModeBlocked;

        if (definitiveRejection) {
          pendingOrderRef.current = null;
          try {
            window.sessionStorage.removeItem(storageKey);
          } catch {
            // In-memory request state is already cleared.
          }
        }

        throw new Error(
          formatPaperOrderError(payload),
        );
      }

      // Only confirmed execution may clear the retry identity.
      if (
        payload.trade_status !== "executed" ||
        payload.status !== "processed"
      ) {
        throw new Error(
          "The paper-order response did not confirm execution. " +
          "The same request ID will be used when retrying.",
        );
      }

      pendingOrderRef.current = null;

      try {
        window.sessionStorage.removeItem(
          storageKey,
        );
      } catch {
        // No browser storage is required for confirmation.
      }

      setResult(
        payload,
      );

      setConfirmation(
        false,
      );

      try {
        await onOrderProcessed();
      } catch {
        // The order was confirmed. A dashboard refresh error
        // must not be described as an order submission failure.
      }
    } catch (caught) {
      setError(
        caught instanceof Error
          ? caught.message
          : "The paper order could not be submitted.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Panel
      variant="elevated"
      className="overflow-hidden"
    >
      <div className="flex flex-wrap items-start justify-between gap-4 border-b border-white/[0.07] p-6">
        <div>
          <p className="nv-eyebrow">
            Paper trading
          </p>

          <h2 className="mt-3 text-2xl font-black text-white">
            Submit a simulated order
          </h2>

          <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-400">
            Choose only the market symbol and direction. NeuroVest&apos;s
            authenticated paper pipeline owns risk checks, sizing, pricing,
            accounting, and ledger persistence. No live broker order is created.
          </p>
        </div>

        <StatusBadge tone="success">
          Simulation only
        </StatusBadge>
      </div>

      <div
        data-testid="paper-order-sizing-disclosure"
        className="grid gap-3 border-b border-white/[0.07] p-6 md:grid-cols-2 xl:grid-cols-4"
      >
        <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
          <p className="nv-stat-label">
            Order sizing
          </p>

          <p className="mt-2 text-sm font-semibold leading-6 text-white">
            Automatic volatility-based allocation
          </p>
        </div>

        <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
          <p className="nv-stat-label">
            Capital source
          </p>

          <p className="mt-2 text-sm font-semibold leading-6 text-white">
            Available paper-account capital
          </p>
        </div>

        <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
          <p className="nv-stat-label">
            Simulated execution
          </p>

          <p className="mt-2 text-sm font-semibold leading-6 text-white">
            Market quote with 0.01%–0.05% simulated slippage
          </p>
        </div>

        <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
          <p className="nv-stat-label">
            Simulated fee
          </p>

          <p className="mt-2 text-sm font-semibold leading-6 text-white">
            $1.00 commission per processed execution
          </p>
        </div>
      </div>

      <div className="border-b border-white/[0.07] px-6 py-4">
        <p className="text-xs leading-6 text-slate-500">
          Filled quantity is calculated from the risk-approved allocation and
          simulated execution price. The completed values appear in the
          owner-scoped order ledger below.
        </p>
      </div>

      <div
        data-testid="paper-order-live-quote"
        className="border-b border-white/[0.07] p-6"
      >
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="nv-eyebrow">
              Current market quote
            </p>

            <h3 className="mt-2 text-xl font-black text-white">
              {symbolValid
                ? normalizedSymbol
                : "Enter a market symbol"}
            </h3>

            <p className="mt-2 text-xs leading-5 text-slate-500">
              Read-only market data refreshes automatically every 30 seconds.
              It is used only as a paper-execution reference.
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            <StatusBadge tone="info">
              Market data only
            </StatusBadge>

            <StatusBadge tone="warning">
              No broker order
            </StatusBadge>
          </div>
        </div>

        {!symbolValid ? (
          <div className="mt-5">
            <StatusMessage tone="info">
              Type a valid symbol below to load its current read-only quote.
            </StatusMessage>
          </div>
        ) : quoteLoading && !liveQuote ? (
          <div className="mt-5">
            <StatusMessage tone="info">
              Loading the current quote for {normalizedSymbol}…
            </StatusMessage>
          </div>
        ) : liveQuote?.error ? (
          <div className="mt-5">
            <StatusMessage tone="danger">
              {liveQuote.error}
            </StatusMessage>
          </div>
        ) : (
          <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
            <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
              <p className="nv-stat-label">
                Current price
              </p>

              <p className="mt-2 text-xl font-black text-cyan-200">
                {formatQuoteMoney(
                  quotePrice,
                  liveQuote?.currency,
                )}
              </p>
            </div>

            <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
              <p className="nv-stat-label">
                Movement
              </p>

              <p
                className={[
                  "mt-2 text-sm font-black",
                  quoteChange === null
                    ? "text-slate-300"
                    : quoteChange >= 0
                      ? "text-emerald-300"
                      : "text-rose-300",
                ].join(" ")}
              >
                {quoteChange === null
                  ? "Reference unavailable"
                  : `${quoteChange >= 0 ? "+" : ""}${quoteChange.toFixed(2)} · ${quoteChangePercent === null ? "N/A" : `${quoteChangePercent >= 0 ? "+" : ""}${quoteChangePercent.toFixed(2)}%`}`}
              </p>

              <p className="mt-1 text-[10px] uppercase tracking-[0.12em] text-slate-600">
                {reference
                  ? `vs ${reference.label}`
                  : "No comparison returned"}
              </p>
            </div>

            <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
              <p className="nv-stat-label">
                Currency
              </p>

              <p className="mt-2 text-sm font-black text-white">
                {liveQuote?.currency ||
                  "Unavailable"}
              </p>
            </div>

            <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
              <p className="nv-stat-label">
                Provider
              </p>

              <p className="mt-2 text-sm font-black text-white">
                {liveQuote?.provider ||
                  "Unavailable"}
              </p>
            </div>

            <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
              <p className="nv-stat-label">
                Quote status
              </p>

              <p className="mt-2 text-sm font-black uppercase text-white">
                {quoteLoading
                  ? "Refreshing"
                  : liveQuote?.status ||
                    (quotePrice !== null
                      ? "Available"
                      : "Unavailable")}
              </p>
            </div>
          </div>
        )}
      </div>

      <form
        onSubmit={submitOrder}
        className="p-6"
      >
        {strategyHandoffNotice && (
          <div className="mb-5">
            <StatusMessage tone="info">
              {strategyHandoffNotice}
            </StatusMessage>
          </div>
        )}
        <div className="grid gap-5 lg:grid-cols-[1fr_auto]">
          <div>
            <label
              htmlFor="paper-order-symbol"
              className="nv-stat-label"
            >
              Market symbol
            </label>

            <input
              id="paper-order-symbol"
              name="symbol"
              type="text"
              aria-describedby="paper-order-symbol-help"
              aria-invalid={symbol.length > 0 && !symbolValid}
              inputMode="text"
              autoComplete="off"
              maxLength={15}
              value={symbol}
              onChange={(event) => {
                setSymbol(
                  event.target.value
                    .toUpperCase(),
                );

                setError(null);
                setResult(null);
              }}
              placeholder="AAPL"
              className="mt-3 w-full rounded-2xl border border-white/[0.1] bg-slate-950/75 px-4 py-3 font-black uppercase tracking-[0.08em] text-white outline-none transition placeholder:text-slate-700 focus:border-cyan-300/40 focus:ring-2 focus:ring-cyan-300/10"
            />

            <p
              id="paper-order-symbol-help"
              className="mt-2 text-xs leading-5 text-slate-500"
            >
              Examples: AAPL, MSFT, BRK.B. Letters,
              numbers, periods, and hyphens only.
            </p>
          </div>

          <fieldset>
            <legend className="nv-stat-label">
              Order action
            </legend>

            <div className="mt-3 grid grid-cols-2 gap-3">
              {(
                [
                  "buy",
                  "sell",
                ] as const
              ).map(
                (
                  candidate,
                ) => {
                  const selected =
                    action ===
                    candidate;

                  return (
                    <button
                      key={
                        candidate
                      }
                      type="button"
                      aria-pressed={
                        selected
                      }
                      onClick={() => {
                        setAction(
                          candidate,
                        );

                        setError(
                          null,
                        );

                        setResult(
                          null,
                        );
                      }}
                      className={[
                        "min-w-[110px] rounded-2xl border px-5 py-3 text-sm font-black uppercase tracking-[0.12em] transition",
                        selected &&
                        candidate ===
                          "buy"
                          ? "border-emerald-300/40 bg-emerald-300/[0.12] text-emerald-200"
                          : "",
                        selected &&
                        candidate ===
                          "sell"
                          ? "border-amber-300/40 bg-amber-300/[0.12] text-amber-200"
                          : "",
                        !selected
                          ? "border-white/[0.08] bg-slate-950/55 text-slate-500 hover:border-white/[0.16] hover:text-white"
                          : "",
                      ].join(" ")}
                    >
                      {
                        candidate
                      }
                    </button>
                  );
                },
              )}
            </div>
          </fieldset>
        </div>

        <section
          data-testid="f8-paper-order-review"
          aria-label="Simulated order review"
          aria-live="polite"
          className="mt-6 rounded-2xl border border-cyan-300/15 bg-cyan-300/[0.04] p-4"
        >
          <p className="nv-eyebrow">Review your paper order</p>
          <p className="mt-2 text-sm font-bold text-slate-100">
            {action.toUpperCase()}{" "}
            {symbolValid ? normalizedSymbol : "— select a symbol"}
          </p>
          <p className="mt-2 text-xs leading-5 text-slate-400">
            Simulated execution only. NeuroVest calculates the
            approved quantity, simulated price, and applicable
            costs after its risk checks. This is not a live
            brokerage order.
          </p>
          {!symbolValid && symbol.length > 0 && (
            <p className="mt-2 text-xs text-amber-200">
              Enter a valid symbol before submitting.
            </p>
          )}
        </section>

        <label className="mt-6 flex cursor-pointer items-start gap-3 rounded-2xl border border-white/[0.08] bg-white/[0.025] p-4">
          <input
            type="checkbox"
            checked={
              confirmation
            }
            onChange={(
              event,
            ) => {
              setConfirmation(
                event.target
                  .checked,
              );

              setError(null);
            }}
            className="mt-1 h-4 w-4 accent-cyan-400"
          />

          <span className="text-sm leading-6 text-slate-300">
            I understand this is a
            simulated paper order and
            cannot place a live-money
            broker trade.
          </span>
        </label>

        {error && (
          <div className="mt-5">
            <StatusMessage tone="danger">
              {error}
            </StatusMessage>
          </div>
        )}

        {result && (
          <div
            data-testid="paper-order-result"
            className="mt-5"
          >
            <StatusMessage tone="success">
              Paper order processed:{" "}
              {result.action?.toUpperCase()}{" "}
              {result.symbol}. Live
              execution remained disabled.
            </StatusMessage>

            {result.trace_id && (
              <p className="mt-2 break-all text-xs text-slate-600">
                Trace:{" "}
                {result.trace_id}
              </p>
            )}
          </div>
        )}

        <div className="mt-6 flex flex-wrap items-center justify-between gap-4 border-t border-white/[0.07] pt-5">
          <div className="flex flex-wrap gap-2">
            <StatusBadge tone="info">
              Authenticated
            </StatusBadge>

            <StatusBadge tone="violet">
              Owner scoped
            </StatusBadge>

            <StatusBadge tone="warning">
              Risk gated
            </StatusBadge>
          </div>

          <button
            type="submit"
            disabled={!canSubmit}
            className="nv-button nv-button-primary nv-button-lg"
          >
            {submitting
              ? "Processing paper order…"
              : `Submit ${action} order`}
          </button>
        </div>
      </form>
    </Panel>
  );
}
