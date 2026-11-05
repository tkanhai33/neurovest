"use client";

import {
  FormEvent,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  Panel,
  StatusBadge,
  StatusMessage,
} from "../../../components/ui";

type UnknownRecord =
  Record<string, unknown>;

type EnabledStrategyResponse = {
  enabled_count?: number;
  strategies?: unknown[];
  detail?: string;
  error?: string;
};

type PaperEvaluation = {
  status?: string;
  observation_count?: number;
  ending_value?: number;
  cumulative_return?: number;
  max_drawdown?: number;
  estimated_transaction_cost?: number;
  strategy_backtest?: boolean;
  execution_enabled?: boolean;
  proposal?: {
    strategy_name?: string;
  };
};

type PaperEvaluationsResponse = {
  evaluations?: PaperEvaluation[];
  detail?: string;
  error?: string;
};

type StrategyContribution = {
  strategy_name: string;
  evaluator_id?: string;
  status?: string;
  decision: string;
  confidence?: number;
  reason?: string;
};

type StrategyDecisionResponse = {
  status?: string;
  symbol?: string;
  decision?: string;
  signal?: string;
  confidence?: number;
  provider?: string;
  source?: string;
  strategy_name?: string;
  enabled_strategy_name?: string;
  enabled_strategy_names?: string[];
  enabled_strategy_count?: number;
  evaluator_id?: string;
  buy_votes?: number;
  sell_votes?: number;
  hold_votes?: number;
  net_vote?: number;
  directional_votes?: number;
  winning_votes?: number;
  eligible_results?: number;
  received_results?: number;
  abstaining_results?: number;
  mean_winner_confidence?: number;
  consensus_ratio?: number;
  participation_ratio?: number;
  contributing_strategies?: string[];
  abstaining_strategies?: string[];
  strategy_results?: StrategyContribution[];
  execution_enabled?: boolean;
  owner_strategy_applied?: boolean;
  owner_strategy_reason?: string;
  reason?: string;
  short_window?: number;
  long_window?: number;
  minimum_bars?: number;
  received_bars?: number;
  previous_fast_sma?: number;
  previous_slow_sma?: number;
  current_fast_sma?: number;
  current_slow_sma?: number;
  fallback_used?: boolean;
  fallback_reason?: string;
  trace_id?: string;
  detail?: string;
  error?: string;
};

const SYMBOL_PATTERN =
  /^[A-Z0-9][A-Z0-9.-]{0,14}$/;

function asRecord(
  value: unknown,
): UnknownRecord | null {
  if (
    typeof value === "object" &&
    value !== null &&
    !Array.isArray(value)
  ) {
    return value as UnknownRecord;
  }

  return null;
}

function readStrategyName(
  value: unknown,
): string | null {
  const record = asRecord(
    value,
  );

  if (!record) {
    return null;
  }

  for (
    const key of [
      "strategy_name",
      "name",
      "title",
      "display_name",
    ]
  ) {
    const candidate =
      record[key];

    if (
      typeof candidate === "string" &&
      candidate.trim()
    ) {
      return candidate.trim();
    }
  }

  return null;
}

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
    value >= 0 &&
    value <= 1
      ? value * 100
      : value;

  return `${percentage.toFixed(1)}%`;
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

function decisionTone(
  decision: string,
):
  | "success"
  | "warning"
  | "danger"
  | "info" {
  const normalized =
    decision.toLowerCase();

  if (
    normalized.includes("buy") ||
    normalized.includes("bull")
  ) {
    return "success";
  }

  if (
    normalized.includes("sell") ||
    normalized.includes("bear")
  ) {
    return "danger";
  }

  if (
    normalized.includes("hold") ||
    normalized.includes("neutral")
  ) {
    return "warning";
  }

  return "info";
}

export default function StrategyDecisionPanel() {
  const [
    symbol,
    setSymbol,
  ] = useState("");

  const [
    enabledLoading,
    setEnabledLoading,
  ] = useState(true);

  const [
    enabledError,
    setEnabledError,
  ] =
    useState<string | null>(
      null,
    );

  const [
    enabledStrategies,
    setEnabledStrategies,
  ] =
    useState<string[]>([]);

  const [
    paperEvaluationsLoading,
    setPaperEvaluationsLoading,
  ] = useState(true);

  const [
    paperEvaluationsError,
    setPaperEvaluationsError,
  ] =
    useState<string | null>(
      null,
    );

  const [
    paperEvaluations,
    setPaperEvaluations,
  ] =
    useState<PaperEvaluation[]>([]);

  const [
    decisionLoading,
    setDecisionLoading,
  ] = useState(false);

  const [
    decisionError,
    setDecisionError,
  ] =
    useState<string | null>(
      null,
    );

  const [
    decision,
    setDecision,
  ] =
    useState<StrategyDecisionResponse | null>(
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
      let active = true;

      async function loadEnabledStrategies():
        Promise<void> {
        setEnabledLoading(true);
        setEnabledError(null);

        try {
          const response =
            await fetch(
              "/api/v1/strategy-library/enabled",
              {
                method: "GET",
                credentials: "include",
                cache: "no-store",
              },
            );

          let payload:
            EnabledStrategyResponse;

          try {
            payload =
              await response.json() as
              EnabledStrategyResponse;
          } catch {
            payload = {
              detail:
                "The enabled-strategy service returned an invalid response.",
            };
          }

          if (!active) {
            return;
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
              "Enabled strategies are unavailable.",
            );
          }

          const names =
            Array.isArray(
              payload.strategies,
            )
              ? payload.strategies
                  .map(
                    readStrategyName,
                  )
                  .filter(
                    (
                      value,
                    ): value is string =>
                      Boolean(value),
                  )
              : [];

          setEnabledStrategies(
            names,
          );
        } catch (caught) {
          if (active) {
            setEnabledError(
              caught instanceof Error
                ? caught.message
                : "Enabled strategies could not be loaded.",
            );
          }
        } finally {
          if (active) {
            setEnabledLoading(false);
          }
        }
      }

      void loadEnabledStrategies();

      return () => {
        active = false;
      };
    },
    [],
  );

  useEffect(
    () => {
      let active = true;

      async function loadPaperEvaluations():
        Promise<void> {
        setPaperEvaluationsLoading(true);
        setPaperEvaluationsError(null);

        try {
          const response =
            await fetch(
              "/api/v1/strategy-library/allocation-proposals/paper-evaluations",
              {
                method: "GET",
                credentials: "include",
                cache: "no-store",
              },
            );

          let payload:
            PaperEvaluationsResponse;

          try {
            payload =
              await response.json() as
              PaperEvaluationsResponse;
          } catch {
            payload = {
              detail:
                "The allocation-snapshot service returned an invalid response.",
            };
          }

          if (!active) {
            return;
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
              "Allocation proposal snapshots are unavailable.",
            );
          }

          setPaperEvaluations(
            Array.isArray(payload.evaluations)
              ? payload.evaluations
              : [],
          );
        } catch (caught) {
          if (active) {
            setPaperEvaluationsError(
              caught instanceof Error
                ? caught.message
                : "Allocation proposal snapshots could not be loaded.",
            );
          }
        } finally {
          if (active) {
            setPaperEvaluationsLoading(false);
          }
        }
      }

      void loadPaperEvaluations();

      return () => {
        active = false;
      };
    },
    [],
  );

  async function requestDecision(
    event: FormEvent<HTMLFormElement>,
  ): Promise<void> {
    event.preventDefault();

    if (!symbolValid) {
      setDecisionError(
        "Enter a valid market symbol using letters, numbers, dots, or hyphens.",
      );
      setDecision(null);
      return;
    }

    setDecisionLoading(true);
    setDecisionError(null);
    setDecision(null);

    try {
      const response =
        await fetch(
          `/api/v1/strategy/decision/${encodeURIComponent(
            normalizedSymbol,
          )}`,
          {
            method: "GET",
            credentials: "include",
            cache: "no-store",
          },
        );

      let payload:
        StrategyDecisionResponse;

      try {
        payload =
          await response.json() as
          StrategyDecisionResponse;
      } catch {
        payload = {
          status: "error",
          detail:
            "The strategy-decision service returned an invalid response.",
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
          "The strategy decision could not be generated.",
        );
      }

      setDecision(
        payload,
      );
    } catch (caught) {
      setDecisionError(
        caught instanceof Error
          ? caught.message
          : "The strategy decision could not be generated.",
      );
    } finally {
      setDecisionLoading(false);
    }
  }

  const decisionValue =
    (
      decision?.decision ??
      decision?.signal ??
      "Unavailable"
    ).toUpperCase();

  const provider =
    decision?.provider ??
    decision?.source ??
    "Unavailable";

  const appliedStrategy =
    decision?.enabled_strategy_name ??
    decision?.strategy_name;

  const decisionReason =
    decision?.reason ??
    decision?.owner_strategy_reason ??
    decision?.fallback_reason;

  const ownerStrategyApplied =
    decision?.owner_strategy_applied;

  const strategyResults =
    decision?.strategy_results ??
    [];

  const enabledQualifiedStrategies =
    decision?.enabled_strategy_names ??
    [];

  const hasAggregationEvidence =
    strategyResults.length > 0;

  const hasSmaMetrics =
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

  function openStrategyExplanation(): void {
    if (!decision) {
      return;
    }

    const message = [
      "Please explain this read-only dashboard strategy snapshot.",
      "Treat these values as user-provided on-screen context, not as a",
      "trade instruction or independently fetched evidence.",
      `Symbol: ${decision.symbol ?? normalizedSymbol}`,
      `Decision: ${decisionValue}`,
      `Confidence: ${formatConfidence(decision.confidence)}`,
      `Provider: ${provider}`,
      `Reason: ${formatReason(decisionReason)}`,
      `Owner strategy applied: ${
        ownerStrategyApplied === true ? "Yes" : "No"
      }`,
      `Buy votes: ${decision.buy_votes ?? 0}`,
      `Sell votes: ${decision.sell_votes ?? 0}`,
      `Hold votes: ${decision.hold_votes ?? 0}`,
      "Explain the result, uncertainty, and paper-only boundary.",
    ].join("\n");

    window.dispatchEvent(
      new CustomEvent(
        "neurovest:strategy-explanation-draft",
        {
          detail: {
            message,
          },
        },
      ),
    );
  }


  function preparePaperOrderReview(): void {
    if (
      !decision ||
      ownerStrategyApplied !== true ||
      !["BUY", "SELL"].includes(decisionValue)
    ) {
      return;
    }

    window.sessionStorage.setItem(
      "neurovest_strategy_paper_order_intent_v1",
      JSON.stringify(
        {
          version: 1,
          symbol:
            decision.symbol ??
            normalizedSymbol,
          action:
            decisionValue.toLowerCase(),
          source:
            "owner_strategy_decision",
        },
      ),
    );

    window.dispatchEvent(
      new CustomEvent(
        "neurovest:open-user-workspace-v1",
        {
          detail: {
            workspace: "orders",
          },
        },
      ),
    );
  }


  return (
    <div className="space-y-5">
      <Panel
        variant="default"
        className="overflow-hidden"
      >
        <div className="flex flex-wrap items-start justify-between gap-4 border-b border-white/[0.07] p-6">
          <div>
            <p className="nv-eyebrow">
              Your strategy selection
            </p>

            <h2 className="mt-3 text-2xl font-black text-white">
              Enabled reference strategies
            </h2>

            <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-400">
              Authenticated, owner-scoped strategy selections from the
              NeuroVest reference library.
            </p>
          </div>

          <StatusBadge tone="violet">
            {enabledLoading
              ? "Loading"
              : `${enabledStrategies.length} enabled`}
          </StatusBadge>
        </div>

        <div
          data-testid="enabled-strategy-summary"
          className="p-6"
        >
          {enabledError ? (
            <StatusMessage tone="danger">
              {enabledError}
            </StatusMessage>
          ) : enabledLoading ? (
            <StatusMessage tone="info">
              Loading your enabled strategies…
            </StatusMessage>
          ) : enabledStrategies.length === 0 ? (
            <StatusMessage tone="info">
              No reference strategies are currently enabled for this account.
              Use Manage enabled strategies below to choose from the catalog.
            </StatusMessage>
          ) : (
            <details
              data-testid="f7-enabled-strategy-disclosure"
              className="group rounded-2xl border border-cyan-300/15 bg-cyan-300/[0.035]"
            >
              <summary className="flex min-h-14 cursor-pointer list-none items-center justify-between gap-4 rounded-2xl px-4 py-3 focus-visible:outline focus-visible:outline-2 focus-visible:outline-cyan-300 [&::-webkit-details-marker]:hidden">
                <span className="min-w-0">
                  <span className="block text-sm font-bold text-cyan-100">
                    View {enabledStrategies.length} enabled strategies
                  </span>
                  <span className="mt-1 block text-xs leading-5 text-slate-400">
                    Account selections, not active trade execution
                  </span>
                </span>
                <span
                  aria-hidden="true"
                  className="shrink-0 rounded-lg border border-cyan-300/20 px-3 py-2 text-xs font-bold text-cyan-200"
                >
                  <span className="group-open:hidden">Expand +</span>
                  <span className="hidden group-open:inline">Collapse −</span>
                </span>
              </summary>
              <div className="border-t border-white/[0.07] px-4 py-4">
                <div className="flex flex-wrap gap-2">
                  {enabledStrategies.map(
                    strategy => (
                      <StatusBadge
                        key={strategy}
                        tone="success"
                      >
                        {strategy}
                      </StatusBadge>
                    ),
                  )}
                </div>
              </div>
            </details>
          )}
        </div>
      </Panel>

      <Panel
        variant="default"
        className="overflow-hidden"
        data-testid="dashboard-allocation-paper-evaluations"
      >
        <div className="flex flex-wrap items-start justify-between gap-4 border-b border-white/[0.07] p-6">
          <div>
            <p className="nv-eyebrow">
              Allocation proposals
            </p>

            <h2 className="mt-3 text-2xl font-black text-white">
              Historical allocation proposal snapshots
            </h2>

            <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-400">
              Fixed current target weights evaluated across the available
              historical window with modeled rebalance costs. These are not
              strategy backtests, forecasts, or trading instructions.
            </p>
          </div>

          <StatusBadge tone="info">
            Read only
          </StatusBadge>
        </div>

        <div className="p-6">
          {paperEvaluationsError ? (
            <StatusMessage tone="danger">
              {paperEvaluationsError}
            </StatusMessage>
          ) : paperEvaluationsLoading ? (
            <StatusMessage tone="info">
              Loading allocation proposal snapshots…
            </StatusMessage>
          ) : paperEvaluations.length === 0 ? (
            <StatusMessage tone="info">
              No enabled allocation proposal snapshots are available.
            </StatusMessage>
          ) : (
            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
              {paperEvaluations.map(
                (evaluation, index) => (
                  <div
                    key={
                      evaluation.proposal?.strategy_name ??
                      `allocation-proposal-${index}`
                    }
                    className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4"
                  >
                    <p className="break-words text-base font-black text-white">
                      {evaluation.proposal?.strategy_name ??
                        "Allocation proposal"}
                    </p>

                    <p className="mt-2 text-xs leading-5 text-slate-400">
                      Historical modeled snapshot · read only
                    </p>

                    <div className="mt-4 grid grid-cols-2 gap-3">
                      <div>
                        <p className="nv-stat-label">
                          Cumulative return
                        </p>

                        <p className="mt-2 text-sm font-black text-cyan-200">
                          {formatConfidence(
                            evaluation.cumulative_return,
                          )}
                        </p>
                      </div>

                      <div>
                        <p className="nv-stat-label">
                          Maximum drawdown
                        </p>

                        <p className="mt-2 text-sm font-black text-white">
                          {formatConfidence(
                            evaluation.max_drawdown,
                          )}
                        </p>
                      </div>

                      <div>
                        <p className="nv-stat-label">
                          Ending value
                        </p>

                        <p className="mt-2 text-sm font-black text-white">
                          {formatMetric(
                            evaluation.ending_value,
                          )}
                        </p>
                      </div>

                      <div>
                        <p className="nv-stat-label">
                          Observations
                        </p>

                        <p className="mt-2 text-sm font-black text-white">
                          {evaluation.observation_count ??
                            "Unavailable"}
                        </p>
                      </div>
                    </div>

                    <p className="mt-4 text-xs leading-5 text-slate-500">
                      Estimated modeled cost:{" "}
                      {formatMetric(
                        evaluation.estimated_transaction_cost,
                      )}
                    </p>
                  </div>
                ),
              )}
            </div>
          )}
        </div>
      </Panel>

      <Panel
        variant="elevated"
        className="overflow-hidden"
      >
        <div className="flex flex-wrap items-start justify-between gap-4 border-b border-white/[0.07] p-6">
          <div>
            <p className="nv-eyebrow">
              Read-only analysis
            </p>

            <h2 className="mt-3 text-2xl font-black text-white">
              Owner-scoped strategy decision
            </h2>

            <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-400">
              Inspect the authenticated owner&apos;s current read-only strategy
              decision. A qualified enabled evaluator is used when available;
              otherwise NeuroVest preserves the system strategy fallback.
              This output never places an order.
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            <StatusBadge tone="info">
              Read only
            </StatusBadge>

            <StatusBadge tone="warning">
              No execution
            </StatusBadge>
          </div>
        </div>

        <form
          onSubmit={requestDecision}
          className="p-6"
        >
          <div className="grid gap-4 lg:grid-cols-[1fr_auto]">
            <div>
              <label
                htmlFor="strategy-decision-symbol"
                className="nv-stat-label"
              >
                Market symbol
              </label>

              <input
                id="strategy-decision-symbol"
                name="strategy-decision-symbol"
                type="text"
                inputMode="text"
                autoComplete="off"
                maxLength={15}
                value={symbol}
                onChange={event => {
                  setSymbol(
                    event.target.value.toUpperCase(),
                  );

                  setDecision(null);
                  setDecisionError(null);
                }}
                placeholder="AAPL"
                className="mt-3 w-full rounded-2xl border border-white/[0.1] bg-slate-950/75 px-4 py-3 font-black uppercase tracking-[0.08em] text-white outline-none transition placeholder:text-slate-700 focus:border-cyan-300/40 focus:ring-2 focus:ring-cyan-300/10"
              />

              <p className="mt-2 text-xs text-slate-500">
                Examples: AAPL, MSFT, TD.TO
              </p>
            </div>

            <button
              type="submit"
              disabled={
                !symbolValid ||
                decisionLoading
              }
              className="nv-button nv-button-primary nv-button-lg self-end"
            >
              {decisionLoading
                ? "Analyzing…"
                : "Get decision"}
            </button>
          </div>

          {decisionError && (
            <div className="mt-5">
              <StatusMessage tone="danger">
                {decisionError}
              </StatusMessage>
            </div>
          )}

          {decision && (
            <div
              data-testid="strategy-decision-result"
              className="mt-6"
            >
              <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
                <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
                  <p className="nv-stat-label">
                    Symbol
                  </p>

                  <p className="mt-2 text-lg font-black text-white">
                    {decision.symbol ??
                      normalizedSymbol}
                  </p>
                </div>

                <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
                  <p className="nv-stat-label">
                    Decision
                  </p>

                  <div className="mt-2">
                    <StatusBadge
                      tone={decisionTone(
                        decisionValue,
                      )}
                    >
                      {decisionValue}
                    </StatusBadge>
                  </div>
                </div>

                <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
                  <p className="nv-stat-label">
                    Confidence
                  </p>

                  <p className="mt-2 text-lg font-black text-cyan-200">
                    {formatConfidence(
                      decision.confidence,
                    )}
                  </p>
                </div>

                <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
                  <p className="nv-stat-label">
                    Provider
                  </p>

                  <p className="mt-2 break-words text-sm font-black text-white">
                    {provider}
                  </p>
                </div>

                <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
                  <p className="nv-stat-label">
                    Status
                  </p>

                  <p className="mt-2 text-sm font-black uppercase text-white">
                    {decision.status ??
                      "Available"}
                  </p>
                </div>
              </div>

              <div className="mt-4 grid gap-3 md:grid-cols-2">
                <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
                  <p className="nv-stat-label">
                    Applied strategy
                  </p>

                  <p className="mt-2 break-words text-sm font-black text-white">
                    {appliedStrategy ??
                      (
                        ownerStrategyApplied === false
                          ? "System strategy engine"
                          : "Unavailable"
                      )}
                  </p>
                </div>

                <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
                  <p className="nv-stat-label">
                    Owner strategy applied
                  </p>

                  <div className="mt-2">
                    <StatusBadge
                      tone={
                        ownerStrategyApplied === true
                          ? "success"
                          : ownerStrategyApplied === false
                            ? "warning"
                            : "info"
                      }
                    >
                      {ownerStrategyApplied === true
                        ? "Yes"
                        : ownerStrategyApplied === false
                          ? "No — system fallback"
                          : "Unavailable"}
                    </StatusBadge>
                  </div>
                </div>

                <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
                  <p className="nv-stat-label">
                    Evaluator
                  </p>

                  <p className="mt-2 break-words text-sm font-black text-white">
                    {decision.evaluator_id ??
                      (
                        ownerStrategyApplied === false
                          ? "System strategy engine"
                          : "Unavailable"
                      )}
                  </p>
                </div>

                <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
                  <p className="nv-stat-label">
                    Decision reason
                  </p>

                  <p className="mt-2 text-sm font-black text-white">
                    {formatReason(
                      decisionReason,
                    )}
                  </p>
                </div>
              </div>

              <div
                data-testid="strategy-chat-paper-handoff-v1"
                className="mt-4 flex flex-wrap items-center gap-3 rounded-2xl border border-cyan-300/15 bg-cyan-300/[0.035] p-4"
              >
                <div className="min-w-0 flex-1">
                  <p className="nv-stat-label">
                    Review options
                  </p>

                  <p className="mt-2 text-xs leading-6 text-slate-400">
                    Neuro can explain this displayed read-only snapshot.
                    Paper-order review remains explicit and never submits an
                    order automatically.
                  </p>
                </div>

                <button
                  type="button"
                  onClick={openStrategyExplanation}
                  className="nv-button nv-button-secondary nv-button-md"
                >
                  Explain in Neuro
                </button>

                {ownerStrategyApplied === true &&
                  ["BUY", "SELL"].includes(decisionValue) && (
                  <button
                    type="button"
                    onClick={preparePaperOrderReview}
                    className="nv-button nv-button-primary nv-button-md"
                  >
                    Prepare simulated {decisionValue} review
                  </button>
                )}
              </div>

              {hasAggregationEvidence && (
                <div
                  data-testid="strategy-aggregation-evidence"
                  className="mt-4 rounded-2xl border border-violet-300/20 bg-violet-300/[0.035] p-4"
                >
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <p className="nv-stat-label">
                        Strategy aggregation evidence
                      </p>

                      <p className="mt-2 max-w-3xl text-xs leading-6 text-slate-400">
                        Each qualified owner-enabled evaluator receives one
                        directional vote. HOLD has no directional weight and
                        abstentions are excluded from the majority.
                      </p>
                    </div>

                    <StatusBadge tone="violet">
                      {decision.enabled_strategy_count ??
                        strategyResults.length}
                      {" "}qualified
                    </StatusBadge>
                  </div>

                  <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                    <div className="rounded-xl border border-emerald-300/15 bg-emerald-300/[0.035] p-3">
                      <p className="nv-stat-label">
                        Buy votes
                      </p>

                      <p className="mt-2 text-xl font-black text-emerald-300">
                        {decision.buy_votes ?? 0}
                      </p>
                    </div>

                    <div className="rounded-xl border border-rose-300/15 bg-rose-300/[0.035] p-3">
                      <p className="nv-stat-label">
                        Sell votes
                      </p>

                      <p className="mt-2 text-xl font-black text-rose-300">
                        {decision.sell_votes ?? 0}
                      </p>
                    </div>

                    <div className="rounded-xl border border-amber-300/15 bg-amber-300/[0.035] p-3">
                      <p className="nv-stat-label">
                        Hold votes
                      </p>

                      <p className="mt-2 text-xl font-black text-amber-300">
                        {decision.hold_votes ?? 0}
                      </p>
                    </div>

                    <div className="rounded-xl border border-slate-300/15 bg-slate-300/[0.025] p-3">
                      <p className="nv-stat-label">
                        Abstained
                      </p>

                      <p className="mt-2 text-xl font-black text-slate-300">
                        {decision.abstaining_results ?? 0}
                      </p>
                    </div>
                  </div>

                  <div className="mt-3 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                    <div className="rounded-xl border border-white/[0.07] bg-slate-950/45 p-3">
                      <p className="nv-stat-label">
                        Results received
                      </p>

                      <p className="mt-2 font-black text-white">
                        {decision.received_results ??
                          strategyResults.length}
                      </p>
                    </div>

                    <div className="rounded-xl border border-white/[0.07] bg-slate-950/45 p-3">
                      <p className="nv-stat-label">
                        Eligible results
                      </p>

                      <p className="mt-2 font-black text-white">
                        {decision.eligible_results ??
                          strategyResults.filter(
                            result =>
                              result.decision.toUpperCase() !==
                              "ABSTAIN",
                          ).length}
                      </p>
                    </div>

                    <div className="rounded-xl border border-white/[0.07] bg-slate-950/45 p-3">
                      <p className="nv-stat-label">
                        Directional consensus
                      </p>

                      <p className="mt-2 font-black text-cyan-200">
                        {formatConfidence(
                          decision.consensus_ratio,
                        )}
                      </p>
                    </div>

                    <div className="rounded-xl border border-white/[0.07] bg-slate-950/45 p-3">
                      <p className="nv-stat-label">
                        Participation
                      </p>

                      <p className="mt-2 font-black text-cyan-200">
                        {formatConfidence(
                          decision.participation_ratio,
                        )}
                      </p>
                    </div>
                  </div>

                  {enabledQualifiedStrategies.length > 0 && (
                    <div className="mt-4">
                      <p className="nv-stat-label">
                        Enabled qualified strategies
                      </p>

                      <div className="mt-3 flex flex-wrap gap-2">
                        {enabledQualifiedStrategies.map(
                          strategy => (
                            <StatusBadge
                              key={strategy}
                              tone="violet"
                            >
                              {strategy}
                            </StatusBadge>
                          ),
                        )}
                      </div>
                    </div>
                  )}

                  <div className="mt-4 space-y-3">
                    <p className="nv-stat-label">
                      Evaluator contributions
                    </p>

                    {strategyResults.map(
                      result => {
                        const resultDecision =
                          result.decision.toUpperCase();

                        return (
                          <div
                            key={result.strategy_name}
                            className="grid gap-3 rounded-xl border border-white/[0.07] bg-slate-950/45 p-4 md:grid-cols-[minmax(0,1.4fr)_auto_minmax(0,0.7fr)_minmax(0,1.5fr)] md:items-center"
                          >
                            <div>
                              <p className="break-words text-sm font-black text-white">
                                {result.strategy_name}
                              </p>

                              <p className="mt-1 break-words text-[10px] uppercase tracking-[0.12em] text-slate-600">
                                {result.evaluator_id ??
                                  "Evaluator unavailable"}
                              </p>
                            </div>

                            <div>
                              <StatusBadge
                                tone={decisionTone(
                                  resultDecision,
                                )}
                              >
                                {resultDecision}
                              </StatusBadge>
                            </div>

                            <div>
                              <p className="nv-stat-label">
                                Confidence
                              </p>

                              <p className="mt-1 text-sm font-black text-cyan-200">
                                {formatConfidence(
                                  result.confidence,
                                )}
                              </p>
                            </div>

                            <div>
                              <p className="nv-stat-label">
                                Reason
                              </p>

                              <p className="mt-1 text-sm font-bold text-slate-300">
                                {formatReason(
                                  result.reason,
                                )}
                              </p>
                            </div>
                          </div>
                        );
                      },
                    )}
                  </div>
                </div>
              )}

              {hasSmaMetrics && (
                <div className="mt-4 rounded-2xl border border-cyan-300/15 bg-cyan-300/[0.035] p-4">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <p className="nv-stat-label">
                        SMA crossover evidence
                      </p>

                      <p className="mt-2 text-xs leading-6 text-slate-400">
                        Previous-to-current averages used by the qualified
                        deterministic evaluator.
                      </p>
                    </div>

                    <StatusBadge tone="info">
                      {decision.short_window ?? 5}
                      /
                      {decision.long_window ?? 20}
                      {" "}SMA
                    </StatusBadge>
                  </div>

                  <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                    <div className="rounded-xl border border-white/[0.07] bg-slate-950/45 p-3">
                      <p className="nv-stat-label">
                        Previous fast
                      </p>

                      <p className="mt-2 font-black text-white">
                        {formatMetric(
                          decision.previous_fast_sma,
                        )}
                      </p>
                    </div>

                    <div className="rounded-xl border border-white/[0.07] bg-slate-950/45 p-3">
                      <p className="nv-stat-label">
                        Previous slow
                      </p>

                      <p className="mt-2 font-black text-white">
                        {formatMetric(
                          decision.previous_slow_sma,
                        )}
                      </p>
                    </div>

                    <div className="rounded-xl border border-white/[0.07] bg-slate-950/45 p-3">
                      <p className="nv-stat-label">
                        Current fast
                      </p>

                      <p className="mt-2 font-black text-cyan-200">
                        {formatMetric(
                          decision.current_fast_sma,
                        )}
                      </p>
                    </div>

                    <div className="rounded-xl border border-white/[0.07] bg-slate-950/45 p-3">
                      <p className="nv-stat-label">
                        Current slow
                      </p>

                      <p className="mt-2 font-black text-cyan-200">
                        {formatMetric(
                          decision.current_slow_sma,
                        )}
                      </p>
                    </div>
                  </div>

                  <p className="mt-3 text-xs text-slate-500">
                    Bars received:{" "}
                    <strong className="text-white">
                      {decision.received_bars ??
                        "Unavailable"}
                    </strong>
                    {" · "}
                    Minimum required:{" "}
                    <strong className="text-white">
                      {decision.minimum_bars ??
                        21}
                    </strong>
                  </p>
                </div>
              )}

              {decision.trace_id && (
                <p className="mt-3 break-all text-[10px] uppercase tracking-[0.12em] text-slate-600">
                  Trace: {decision.trace_id}
                </p>
              )}
            </div>
          )}
        </form>

        <div className="flex flex-wrap gap-2 border-t border-white/[0.07] px-6 py-5">
          <StatusBadge tone="info">
            Authenticated read
          </StatusBadge>

          <StatusBadge tone="violet">
            Owner scoped
          </StatusBadge>

          <StatusBadge tone="warning">
            Not a trade
          </StatusBadge>

          <StatusBadge tone="warning">
            Training controls withheld
          </StatusBadge>
        </div>
      </Panel>
    </div>
  );
}
