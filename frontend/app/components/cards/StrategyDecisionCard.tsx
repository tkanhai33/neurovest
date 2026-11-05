"use client";

import {
  useCallback,
  useEffect,
  useState,
} from "react";

import {
  getStrategyDecision,
  type StrategyDecision,
} from "../../../services/strategyService";

function formatConfidence(
  value: number | undefined,
): string {
  if (
    typeof value !== "number" ||
    !Number.isFinite(value)
  ) {
    return "Unavailable";
  }

  const percentage =
    value >= 0 && value <= 1
      ? value * 100
      : value;

  return `${percentage.toFixed(3)}%`;
}

function formatMetric(
  value: number | undefined,
): string {
  if (
    typeof value !== "number" ||
    !Number.isFinite(value)
  ) {
    return "Unavailable";
  }

  return value.toFixed(6);
}

function formatReason(
  value: string | undefined,
): string {
  if (!value) {
    return "Unavailable";
  }

  return value
    .replaceAll("_", " ")
    .replace(
      /^./,
      character =>
        character.toUpperCase(),
    );
}

export default function StrategyDecisionCard() {
  const [
    symbol,
    setSymbol,
  ] = useState("AAPL");

  const [
    decision,
    setDecision,
  ] =
    useState<StrategyDecision | null>(
      null,
    );

  const [
    loading,
    setLoading,
  ] = useState(false);

  const loadDecision = useCallback(
    async (
      nextSymbol = symbol,
    ) => {
      const cleanSymbol =
        nextSymbol
          .trim()
          .toUpperCase();

      if (!cleanSymbol) {
        return;
      }

      setLoading(true);

      try {
        const data =
          await getStrategyDecision(
            cleanSymbol,
          );

        setDecision(data);
      } finally {
        setLoading(false);
      }
    },
    [
      symbol,
    ],
  );

  useEffect(
    () => {
      const firstLoad = setTimeout(
        () => {
          void loadDecision(
            symbol,
          );
        },
        0,
      );

      const timer = setInterval(
        () => {
          void loadDecision(
            symbol,
          );
        },
        30000,
      );

      return () => {
        clearTimeout(firstLoad);
        clearInterval(timer);
      };
    },
    [
      loadDecision,
      symbol,
    ],
  );

  const visibleDecision = String(
    decision?.decision ||
    (
      typeof decision?.signal === "string"
        ? decision.signal
        : "hold"
    ),
  );

  const appliedStrategy =
    decision?.enabled_strategy_name ??
    decision?.strategy_name ??
    (
      decision?.owner_strategy_applied === false
        ? "System strategy engine"
        : "Unavailable"
    );

  const evaluator =
    decision?.evaluator_id ??
    (
      decision?.owner_strategy_applied === false
        ? "System strategy engine"
        : "Unavailable"
    );

  const reason =
    decision?.reason ??
    decision?.owner_strategy_reason ??
    "Unavailable";

  const hasSmaEvidence =
    [
      decision?.previous_fast_sma,
      decision?.previous_slow_sma,
      decision?.current_fast_sma,
      decision?.current_slow_sma,
    ].some(
      value =>
        typeof value === "number" &&
        Number.isFinite(value),
    );

  return (
    <section className="mt-6 rounded-2xl border border-violet-400/30 bg-slate-950/80 p-5 shadow-[0_0_30px_rgba(167,139,250,0.12)]">
      <div className="mb-4 flex items-center justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-violet-300">
            Strategy Decision
          </p>

          <h2 className="mt-1 text-2xl font-bold text-white">
            {decision?.symbol ||
              symbol}
          </h2>
        </div>

        <div className="rounded-full border border-violet-400/30 px-3 py-1 text-xs text-violet-200">
          {decision?.status ||
            "idle"}
        </div>
      </div>

      <div className="mb-4 text-4xl font-black text-white">
        {visibleDecision.toUpperCase()}
      </div>

      <div className="mb-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-xl bg-slate-900/80 p-3">
          <p className="text-slate-400">
            Confidence
          </p>

          <p className="font-semibold text-violet-200">
            {formatConfidence(
              decision?.confidence,
            )}
          </p>
        </div>

        <div className="rounded-xl bg-slate-900/80 p-3">
          <p className="text-slate-400">
            Provider
          </p>

          <p className="break-words font-semibold text-violet-200">
            {decision?.provider ||
              "Unavailable"}
          </p>
        </div>

        <div className="rounded-xl bg-slate-900/80 p-3">
          <p className="text-slate-400">
            Owner strategy
          </p>

          <p
            className={
              decision?.owner_strategy_applied
                ? "font-semibold text-emerald-300"
                : "font-semibold text-amber-300"
            }
          >
            {decision?.owner_strategy_applied === true
              ? "Applied"
              : decision?.owner_strategy_applied === false
                ? "System fallback"
                : "Unavailable"}
          </p>
        </div>

        <div className="rounded-xl bg-slate-900/80 p-3">
          <p className="text-slate-400">
            Evaluator
          </p>

          <p className="break-words font-semibold text-violet-200">
            {evaluator}
          </p>
        </div>
      </div>

      <div className="mb-4 grid gap-3 md:grid-cols-2">
        <div className="rounded-xl border border-white/[0.07] bg-slate-900/55 p-3">
          <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
            Applied strategy
          </p>

          <p className="mt-2 break-words text-sm font-semibold text-white">
            {appliedStrategy}
          </p>
        </div>

        <div className="rounded-xl border border-white/[0.07] bg-slate-900/55 p-3">
          <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
            Decision reason
          </p>

          <p className="mt-2 text-sm font-semibold text-white">
            {formatReason(
              reason,
            )}
          </p>
        </div>
      </div>

      {hasSmaEvidence && (
        <div className="mb-4 rounded-xl border border-cyan-300/20 bg-cyan-300/[0.035] p-4">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-cyan-300">
                SMA crossover evidence
              </p>

              <p className="mt-1 text-xs leading-5 text-slate-400">
                Previous-to-current averages used by the deterministic evaluator.
              </p>
            </div>

            <div className="rounded-full border border-cyan-300/20 px-3 py-1 text-xs font-semibold text-cyan-200">
              {decision?.short_window ??
                5}
              /
              {decision?.long_window ??
                20}
              {" "}SMA
            </div>
          </div>

          <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <div className="rounded-lg bg-slate-950/60 p-3">
              <p className="text-xs text-slate-500">
                Previous fast
              </p>

              <p className="mt-1 font-semibold text-white">
                {formatMetric(
                  decision?.previous_fast_sma,
                )}
              </p>
            </div>

            <div className="rounded-lg bg-slate-950/60 p-3">
              <p className="text-xs text-slate-500">
                Previous slow
              </p>

              <p className="mt-1 font-semibold text-white">
                {formatMetric(
                  decision?.previous_slow_sma,
                )}
              </p>
            </div>

            <div className="rounded-lg bg-slate-950/60 p-3">
              <p className="text-xs text-slate-500">
                Current fast
              </p>

              <p className="mt-1 font-semibold text-cyan-200">
                {formatMetric(
                  decision?.current_fast_sma,
                )}
              </p>
            </div>

            <div className="rounded-lg bg-slate-950/60 p-3">
              <p className="text-xs text-slate-500">
                Current slow
              </p>

              <p className="mt-1 font-semibold text-cyan-200">
                {formatMetric(
                  decision?.current_slow_sma,
                )}
              </p>
            </div>
          </div>

          <p className="mt-3 text-xs text-slate-500">
            Bars received:{" "}
            <strong className="text-white">
              {decision?.received_bars ??
                "Unavailable"}
            </strong>
            {" · "}
            Minimum required:{" "}
            <strong className="text-white">
              {decision?.minimum_bars ??
                21}
            </strong>
          </p>
        </div>
      )}

      {decision?.error && (
        <p className="mb-3 rounded-xl border border-red-400/30 bg-red-950/40 p-3 text-xs text-red-200">
          {decision.error}
        </p>
      )}

      <div className="flex gap-2">
        <input
          value={symbol}
          onChange={
            event =>
              setSymbol(
                event.target.value.toUpperCase(),
              )
          }
          className="min-w-0 flex-1 rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white outline-none focus:border-violet-400"
          placeholder="AAPL"
        />

        <button
          type="button"
          onClick={
            () =>
              void loadDecision(
                symbol,
              )
          }
          disabled={loading}
          className="rounded-xl bg-violet-400 px-4 py-2 text-sm font-bold text-slate-950 disabled:opacity-60"
        >
          {loading
            ? "Loading"
            : "Update"}
        </button>
      </div>
    </section>
  );
}
