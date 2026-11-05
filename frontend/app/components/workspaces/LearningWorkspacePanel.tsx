"use client";

import {
  useCallback,
  useEffect,
  useState,
} from "react";


type RuntimeRecord =
  Record<string, unknown>;


type LearningSymbol = {
  symbol: string;
  cycles: number | null;
  observations: number | null;
  average_reward: number | null;
  average_confidence: number | null;
  decisions: Record<string, number>;
  last_close: number | null;
  last_timestamp: string | null;
};


type LearningState = {
  current_run?: {
    run_id?: string;
    rows?: number;
    reward_total?: number | null;
    decision_counts?: Record<string, number>;
    symbols?: LearningSymbol[];
    average_confidence?: number | null;
  };

  lifetime?: {
    runs?: number;
    rows_processed?: number;
    reward_total?: number | null;
    decision_counts?: Record<string, number>;
  };
};


function isRecord(
  value: unknown
): value is RuntimeRecord {
  return (
    value !== null &&
    typeof value === "object" &&
    !Array.isArray(value)
  );
}


function optionalNumber(
  value: unknown
): number | null {
  if (
    typeof value === "number" &&
    Number.isFinite(value)
  ) {
    return value;
  }

  if (
    typeof value === "string" &&
    value.trim()
  ) {
    const parsed =
      Number(value);

    if (
      Number.isFinite(parsed)
    ) {
      return parsed;
    }
  }

  return null;
}


function numberOrZero(
  value: unknown
): number {
  return (
    optionalNumber(value) ??
    0
  );
}


function normalizeDecisionCounts(
  value: unknown
): Record<string, number> {
  if (!isRecord(value)) {
    return {};
  }

  const output:
    Record<string, number> = {};

  for (
    const [key, rawValue]
    of Object.entries(value)
  ) {
    output[key] =
      numberOrZero(
        rawValue
      );
  }

  return output;
}


// V36-POST — actual live per_symbol adapter
//
// Live runtime truth:
//
// per_symbol[symbol] = {
//   BUY_SIGNAL,
//   HOLD,
//   SELL_SIGNAL,
//   cycles,
//   last_close,
//   last_timestamp
// }
//
// Confidence/reward/observation values are supplied separately by
// sanitized_learning_contribution.symbol_confidence.
//
// This adapter combines those two real structures without changing
// backend runtime or training semantics.

function normalizeSymbols(
  perSymbolValue: unknown,
  contributionValue: unknown
): LearningSymbol[] {
  if (!isRecord(perSymbolValue)) {
    return [];
  }

  const contribution =
    isRecord(contributionValue)
      ? contributionValue
      : {};

  const confidenceRows =
    Array.isArray(
      contribution.symbol_confidence
    )
      ? contribution.symbol_confidence.filter(
          isRecord
        )
      : [];

  const confidenceBySymbol =
    new Map<string, RuntimeRecord>();

  for (
    const record
    of confidenceRows
  ) {
    const symbol =
      typeof record.symbol === "string"
        ? record.symbol
        : null;

    if (symbol) {
      confidenceBySymbol.set(
        symbol,
        record
      );
    }
  }

  const symbols: LearningSymbol[] = [];

  for (
    const [
      symbol,
      value,
    ]
    of Object.entries(
      perSymbolValue
    )
  ) {
    if (!isRecord(value)) {
      continue;
    }

    const confidence =
      confidenceBySymbol.get(
        symbol
      );

    const decisions:
      Record<string, number> = {};

    for (
      const key
      of [
        "BUY_SIGNAL",
        "HOLD",
        "SELL_SIGNAL",
      ]
    ) {
      const candidate =
        value[key];

      if (
        typeof candidate === "number"
        && Number.isFinite(candidate)
      ) {
        decisions[key] =
          candidate;
      }
    }

    symbols.push(
      {
        symbol,

        cycles:
          typeof value.cycles === "number"
          && Number.isFinite(
            value.cycles
          )
            ? value.cycles
            : null,

        observations:
          confidence
          && typeof confidence.observations === "number"
          && Number.isFinite(
            confidence.observations
          )
            ? confidence.observations
            : null,

        average_reward:
          confidence
          && typeof confidence.average_reward === "number"
          && Number.isFinite(
            confidence.average_reward
          )
            ? confidence.average_reward
            : null,

        average_confidence:
          confidence
          && typeof confidence.average_confidence === "number"
          && Number.isFinite(
            confidence.average_confidence
          )
            ? confidence.average_confidence
            : null,

        decisions,

        last_close:
          typeof value.last_close === "number"
          && Number.isFinite(
            value.last_close
          )
            ? value.last_close
            : null,

        last_timestamp:
          typeof value.last_timestamp === "string"
            ? value.last_timestamp
            : null,
      }
    );
  }

  return symbols.sort(
    (
      left,
      right
    ) =>
      left.symbol.localeCompare(
        right.symbol
      )
  );
}


function extractRuns(
  payload: unknown
): RuntimeRecord[] {
  if (Array.isArray(payload)) {
    return payload.filter(
      isRecord
    );
  }

  if (!isRecord(payload)) {
    return [];
  }

  for (
    const key
    of [
      "runs",
      "training_runs",
      "items",
      "results",
    ]
  ) {
    const value =
      payload[key];

    if (Array.isArray(value)) {
      return value.filter(
        isRecord
      );
    }
  }

  if (
    typeof payload.run_id ===
    "string"
  ) {
    return [payload];
  }

  return [];
}


function adaptRuntimeRuns(
  runs: RuntimeRecord[]
): LearningState {
  const completed =
    runs.filter(
      (run) =>
        run.status ===
        "completed"
    );

  const latest =
    completed[0] ??
    runs[0];

  if (!latest) {
    throw new Error(
      "No authoritative training run is available."
    );
  }

  const symbols =
    normalizeSymbols(
      latest.per_symbol,
      latest.sanitized_learning_contribution
    );

  const latestRows =
    numberOrZero(
      latest.rows_evaluated
    );

  const currentDecisions =
    normalizeDecisionCounts(
      latest.decision_counts
    );

  const completedRows =
    completed.reduce(
      (total, run) =>
        total +
        numberOrZero(
          run.rows_evaluated
        ),
      0
    );

  const lifetimeDecisions:
    Record<string, number> = {};

  for (const run of completed) {
    const decisions =
      normalizeDecisionCounts(
        run.decision_counts
      );

    for (
      const [decision, count]
      of Object.entries(decisions)
    ) {
      lifetimeDecisions[decision] =
        (
          lifetimeDecisions[
            decision
          ] ??
          0
        ) +
        count;
    }
  }

  return {
    current_run: {
      run_id:
        typeof latest.run_id ===
        "string"
          ? latest.run_id
          : undefined,

      rows:
        latestRows,

      reward_total:
        optionalNumber(
          latest.reward_total ??
          latest.total_reward
        ),

      average_confidence:
        optionalNumber(
          latest.average_confidence ??
          latest.current_average_confidence
        ),

      decision_counts:
        currentDecisions,

      symbols,
    },

    lifetime: {
      runs:
        completed.length,

      rows_processed:
        completedRows,

      reward_total:
        null,

      decision_counts:
        lifetimeDecisions,
    },
  };
}


function displayNumber(
  value: number | null | undefined,
  digits = 4
): string {
  if (
    value === null ||
    value === undefined ||
    !Number.isFinite(value)
  ) {
    return "Unavailable";
  }

  return value.toFixed(
    digits
  );
}


export default function LearningWorkspacePanel() {
  const [
    data,
    setData,
  ] = useState<LearningState | null>(
    null
  );

  const [
    loadError,
    setLoadError,
  ] = useState<string | null>(
    null
  );


  const loadLearning =
    useCallback(
      async () => {
        try {
          const response =
            await fetch(
              "/api/v1/developer/training/runs",
              {
                cache:
                  "no-store",
              }
            );

          const payload =
            await response
              .json()
              .catch(
                () => null
              );

          if (!response.ok) {
            throw new Error(
              isRecord(payload) &&
              typeof payload.detail ===
                "string"
                ? payload.detail
                : (
                    "Developer training runtime request failed."
                  )
            );
          }

          const liveState =
            adaptRuntimeRuns(
              extractRuns(
                payload
              )
            );

          setData(
            liveState
          );

          setLoadError(
            null
          );

        } catch (
          error
        ) {
          setData(
            null
          );

          setLoadError(
            error instanceof Error
              ? error.message
              : "Learning runtime unavailable."
          );
        }
      },
      []
    );


  useEffect(() => {
    const firstLoad =
      setTimeout(
        () =>
          void loadLearning(),
        0
      );

    const timer =
      setInterval(
        () =>
          void loadLearning(),
        30000
      );

    return () => {
      clearTimeout(
        firstLoad
      );

      clearInterval(
        timer
      );
    };
  }, [
    loadLearning,
  ]);


  const symbols =
    data?.current_run
      ?.symbols ??
    [];

  const decisions =
    data?.current_run
      ?.decision_counts ??
    {};

  const currentConfidence =
    data?.current_run
      ?.average_confidence ??
    null;

  const rewardValues =
    symbols
      .map(
        (symbol) =>
          symbol.average_reward
      )
      .filter(
        (
          value
        ): value is number =>
          value !== null &&
          Number.isFinite(
            value
          )
      );

  const confidenceValues =
    symbols
      .map(
        (symbol) =>
          symbol.average_confidence
      )
      .filter(
        (
          value
        ): value is number =>
          value !== null &&
          Number.isFinite(
            value
          )
      );

  const maxReward =
    Math.max(
      1,
      ...rewardValues.map(
        (value) =>
          Math.abs(
            value
          )
      )
    );

  const maxConfidence =
    Math.max(
      1,
      ...confidenceValues
    );

  const decisionTotal =
    Object.values(
      decisions
    ).reduce(
      (
        sum,
        value
      ) =>
        sum +
        Number(
          value ||
          0
        ),
      0
    );


  return (
    <section className="mt-6 space-y-6">
      <section className="overflow-hidden rounded-3xl border border-fuchsia-400/30 bg-slate-950/80 shadow-[0_0_40px_rgba(217,70,239,0.12)]">
        <div className="border-b border-slate-800 bg-gradient-to-r from-fuchsia-500/10 via-cyan-500/10 to-transparent p-5">
          <p className="text-xs uppercase tracking-[0.3em] text-fuchsia-300">
            Learning
          </p>

          <h2 className="mt-1 text-3xl font-black text-white">
            Training Intelligence
          </h2>

          <p className="mt-2 max-w-3xl text-sm text-slate-400">
            Live bounded-training runtime metrics, symbol learning quality,
            confidence, and decision distribution.
          </p>

          {loadError && (
            <p className="mt-3 rounded-xl border border-amber-400/20 bg-amber-400/5 px-3 py-2 text-xs text-amber-300">
              Runtime unavailable: {loadError}
            </p>
          )}
        </div>

        <div className="grid gap-3 p-5 md:grid-cols-4">
          {[
            [
              "Latest Run",
              data?.current_run
                ?.run_id ??
                "Unavailable",
              "text-cyan-200",
            ],
            [
              "Rows Evaluated",
              data
                ? String(
                    data.current_run
                      ?.rows ??
                      0
                  )
                : "Unavailable",
              "text-white",
            ],
            [
              "Avg Confidence",
              displayNumber(
                currentConfidence
              ),
              "text-emerald-300",
            ],
            [
              "Completed Runs",
              data
                ? String(
                    data.lifetime
                      ?.runs ??
                      0
                  )
                : "Unavailable",
              "text-fuchsia-300",
            ],
          ].map(
            ([
              label,
              value,
              color,
            ]) => (
              <div
                key={label}
                className="rounded-2xl border border-slate-800 bg-slate-900/70 p-4"
              >
                <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
                  {label}
                </p>

                <p
                  className={`mt-2 break-all text-2xl font-black ${color}`}
                >
                  {value}
                </p>
              </div>
            )
          )}
        </div>
      </section>


      <section className="grid gap-6 xl:grid-cols-[1.4fr_0.8fr]">
        <div className="nv-surface-section p-5">
          <div className="mb-5 flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-cyan-300">
                Performance
              </p>

              <h3 className="text-xl font-black text-white">
                Average Reward by Symbol
              </h3>
            </div>

            <span className="rounded-full border border-emerald-400/20 px-3 py-1 text-xs text-emerald-300">
              latest completed run
            </span>
          </div>

          <div className="space-y-4">
            {symbols.map(
              (
                symbol,
                index
              ) => {
                const value =
                  symbol.average_reward;

                const width =
                  value === null
                    ? 0
                    : Math.max(
                        4,
                        Math.min(
                          100,
                          (
                            Math.abs(
                              value
                            ) /
                            maxReward
                          ) *
                            100
                        )
                      );

                return (
                  <div
                    key={symbol.symbol}
                    className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4"
                  >
                    <div className="mb-2 flex items-center justify-between gap-3">
                      <div className="flex items-center gap-3">
                        <span className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-800 text-xs font-black text-cyan-200">
                          {index + 1}
                        </span>

                        <div>
                          <p className="font-black text-white">
                            {symbol.symbol}
                          </p>

                          <p className="text-xs text-slate-500">
                            {symbol.cycles === null
                              ? "cycles unavailable"
                              : `${symbol.cycles.toLocaleString()} cycles`}
                            {" · "}
                            {symbol.observations === null
                              ? "observations unavailable"
                              : `${symbol.observations.toLocaleString()} learning observations`}
                          </p>
                        </div>
                      </div>

                      <p
                        className={
                          value === null
                            ? "font-black text-slate-500"
                            : (
                                value >= 0
                                  ? "font-black text-emerald-300"
                                  : "font-black text-red-300"
                              )
                        }
                      >
                        {displayNumber(
                          value
                        )}
                      </p>
                    </div>

                    <div className="h-4 overflow-hidden rounded-full bg-slate-800">
                      {value !== null && (
                        <progress
                          className={
                            value >= 0
                              ? "nv-csp-progress nv-csp-progress-positive"
                              : "nv-csp-progress nv-csp-progress-negative"
                          }
                          max="100"
                          value={width}
                          aria-label={`${symbol.symbol} reward`}
                        />
                      )}
                    </div>

                    <div className="mt-2 flex flex-wrap justify-between gap-2 text-xs text-slate-500">
                      <span>
                        Last close{" "}
                        {displayNumber(
                          symbol.last_close,
                          4
                        )}
                      </span>

                      <span>
                        {symbol.last_timestamp ??
                          "timestamp unavailable"}
                      </span>
                    </div>
                  </div>
                );
              }
            )}

            {!symbols.length && (
              <p className="text-sm text-slate-500">
                No per-symbol learning statistics are available from the current runtime.
              </p>
            )}
          </div>
        </div>


        <div className="space-y-6">
          <div className="nv-surface-section p-5">
            <p className="text-xs uppercase tracking-[0.25em] text-cyan-300">
              Decision Mix
            </p>

            <h3 className="mt-1 text-xl font-black text-white">
              Action Distribution
            </h3>

            <div className="mt-5 space-y-4">
              {Object.entries(
                decisions
              ).map(
                ([
                  decision,
                  count,
                ]) => {
                  const pct =
                    decisionTotal
                      ? (
                          Number(
                            count
                          ) /
                          decisionTotal
                        ) *
                        100
                      : 0;

                  return (
                    <div
                      key={decision}
                    >
                      <div className="mb-1 flex justify-between text-xs">
                        <span className="font-bold text-white">
                          {decision}
                        </span>

                        <span className="text-slate-400">
                          {Number(count)} · {pct.toFixed(1)}%
                        </span>
                      </div>

                      <div className="h-3 rounded-full bg-slate-800">
                        <progress
                          className="nv-csp-progress nv-csp-progress-cyan"
                          max="100"
                          value={pct}
                          aria-label={`${decision} decision share`}
                        />
                      </div>
                    </div>
                  );
                }
              )}
            </div>
          </div>


          <div className="nv-surface-section p-5">
            <p className="text-xs uppercase tracking-[0.25em] text-cyan-300">
              Confidence
            </p>

            <h3 className="mt-1 text-xl font-black text-white">
              Symbol Confidence
            </h3>

            <div className="mt-5 space-y-3">
              {symbols.map(
                (symbol) => {
                  const confidence =
                    symbol.average_confidence;

                  const pct =
                    confidence === null
                      ? 0
                      : Math.min(
                          100,
                          (
                            confidence /
                            maxConfidence
                          ) *
                            100
                        );

                  return (
                    <div
                      key={symbol.symbol}
                    >
                      <div className="mb-1 flex justify-between text-xs">
                        <span className="font-bold text-white">
                          {symbol.symbol}
                        </span>

                        <span className="text-cyan-200">
                          {displayNumber(
                            confidence
                          )}
                        </span>
                      </div>

                      <div className="h-3 rounded-full bg-slate-800">
                        {confidence !==
                          null && (
                          <progress
                            className="nv-csp-progress nv-csp-progress-fuchsia"
                            max="100"
                            value={pct}
                            aria-label={`${symbol.symbol} confidence`}
                          />
                        )}
                      </div>
                    </div>
                  );
                }
              )}
            </div>
          </div>
        </div>
      </section>


      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {symbols.map(
          (symbol) => {
            const reward =
              symbol.average_reward;

            return (
              <div
                key={symbol.symbol}
                className="rounded-3xl border border-slate-800 bg-slate-950/80 p-5"
              >
                <p className="text-xs uppercase tracking-[0.25em] text-slate-500">
                  Symbol
                </p>

                <h3 className="mt-1 text-2xl font-black text-white">
                  {symbol.symbol}
                </h3>

                <p
                  className={
                    reward === null
                      ? "mt-3 text-2xl font-black text-slate-500"
                      : (
                          reward >= 0
                            ? "mt-3 text-2xl font-black text-emerald-300"
                            : "mt-3 text-2xl font-black text-red-300"
                        )
                  }
                >
                  {displayNumber(
                    reward
                  )}
                </p>

                <p className="mt-2 text-xs text-slate-500">
                  Avg reward{" "}
                  {displayNumber(
                    symbol.average_reward,
                    8
                  )}
                </p>

                <p className="mt-1 text-xs text-slate-500">
                  Confidence{" "}
                  {displayNumber(
                    symbol.average_confidence
                  )}
                </p>

                <p className="mt-1 text-xs text-slate-500">
                  Observations{" "}
                  {symbol.observations === null
                    ? "Unavailable"
                    : symbol.observations.toLocaleString()}
                </p>

                <p className="mt-1 text-xs text-slate-500">
                  Cycles{" "}
                  {symbol.cycles === null
                    ? "Unavailable"
                    : symbol.cycles.toLocaleString()}
                </p>

                <div className="mt-3 space-y-1 text-xs text-slate-500">
                  {Object.entries(
                    symbol.decisions
                  ).map(
                    ([decision, count]) => (
                      <div
                        key={decision}
                        className="flex justify-between gap-2"
                      >
                        <span>
                          {decision}
                        </span>

                        <span className="font-bold text-white">
                          {count.toLocaleString()}
                        </span>
                      </div>
                    )
                  )}
                </div>
              </div>
            );
          }
        )}
      </section>


      <p className="text-xs text-slate-600">
        Learning data source: authenticated bounded-training runtime.
        Signal counts, cycles, last close, and timestamps come from per_symbol.
        Confidence, average reward, and observations come from
        sanitized_learning_contribution.symbol_confidence.
        Missing runtime fields are shown as unavailable rather than inferred.
      </p>
    </section>
  );
}
