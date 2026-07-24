"use client";

import {
  FormEvent,
  useMemo,
  useState,
} from "react";

import {
  csrfHeaders,
} from "../../../lib/clientCsrf";

import {
  Panel,
  StatusBadge,
  StatusMessage,
} from "../../../components/ui";

type PaperOrderAction =
  | "buy"
  | "sell";

type PaperOrderResponse = {
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

  const [
    result,
    setResult,
  ] =
    useState<PaperOrderResponse | null>(
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
        throw new Error(
          payload.detail ??
          payload.error ??
          "The paper order was rejected.",
        );
      }

      setResult(
        payload,
      );

      setConfirmation(
        false,
      );

      await onOrderProcessed();
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
            Orders use NeuroVest&apos;s
            authenticated paper-execution,
            risk, accounting, and ledger
            pipeline. No live broker order
            is created.
          </p>
        </div>

        <StatusBadge tone="success">
          Simulation only
        </StatusBadge>
      </div>

      <form
        onSubmit={submitOrder}
        className="p-6"
      >
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

            <p className="mt-2 text-xs leading-5 text-slate-500">
              Examples: AAPL, MSFT,
              BRK.B
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
