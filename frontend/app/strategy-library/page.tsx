"use client";

import {
  fetchAllocationPaperEvaluations,
  fetchEnabledStrategies,
  fetchStrategyLibrary,
} from "../../services/strategyLibraryService";

import {
  csrfHeaders,
} from "../../lib/clientCsrf";

import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  Button,
  Input,
  PageContainer,
  Panel,
  StatusBadge,
  StatusMessage,
} from "../../components/ui";

import PageHeader from "../../components/app-shell/PageHeader";


type Strategy = {
  strategy_name: string;
  category?: string | null;
  definition?: string | null;
  formula_or_rules?: string | null;
  best_suited_for?: string | null;
  market_applicability?: string[];
  enabled?: boolean;
};


type LibraryPayload = {
  strategy_count: number;
  catalog_total: number;
  enabled_count: number;
  market_filter: string;
  strategies: Strategy[];
};

type PaperEvaluation = {
  status?: string;
  observation_count?: number;
  ending_value?: number;
  cumulative_return?: number;
  max_drawdown?: number;
  estimated_transaction_cost?: number;
  proposal?: {
    strategy_name?: string;
  };
};

type PaperEvaluationsPayload = {
  evaluations?: PaperEvaluation[];
};


const MARKET_OPTIONS = [
  ["all", "All markets"],
  ["crypto", "Crypto"],
  ["equities", "Equities"],
  ["forex", "Forex"],
  ["futures", "Futures"],
  ["options", "Options"],
  ["fixed_income", "Fixed income"],
  ["commodities", "Commodities"],
  ["multi_asset", "Multi Asset"],
] as const;


export default function StrategyLibraryPage() {
  const [market, setMarket] =
    useState("all");

  const [query, setQuery] =
    useState("");

  const [strategies, setStrategies] =
    useState<Strategy[]>([]);

  const [enabledNames, setEnabledNames] =
    useState<Set<string>>(
      new Set(),
    );

  const [loading, setLoading] =
    useState(true);

  const [saving, setSaving] =
    useState(false);

  const [message, setMessage] =
    useState("");

  const [paperEvaluations, setPaperEvaluations] =
    useState<PaperEvaluation[]>([]);

  const [paperEvaluationsLoading, setPaperEvaluationsLoading] =
    useState(true);

  const [paperEvaluationsError, setPaperEvaluationsError] =
    useState("");


  async function loadLibrary(
    selectedMarket: string,
  ) {
    setLoading(true);
    setMessage("");

    try {
      const params =
        selectedMarket === "all"
          ? ""
          : `?market=${encodeURIComponent(
              selectedMarket,
            )}`;

      const response = await fetchStrategyLibrary(params,
        {
          cache: "no-store",
        },
      );

      if (!response.ok) {
        throw new Error(
          `Library request failed: ${response.status}`,
        );
      }

      const payload: LibraryPayload =
        await response.json();

      setStrategies(
        payload.strategies ?? [],
      );
    } catch (error) {
      setMessage(
        error instanceof Error
          ? error.message
          : "Unable to load Strategy Library.",
      );
    } finally {
      setLoading(false);
    }
  }


  async function loadEnabledSelection() {
    try {
      const response = await fetchEnabledStrategies(
        {
          cache: "no-store",
        },
      );

      if (!response.ok) {
        return;
      }

      const payload =
        await response.json();

      setEnabledNames(
        new Set<string>(
          (
            payload.strategies
            ?? []
          ).map(
            (row: Strategy) =>
              row.strategy_name,
          ),
        ),
      );
    } catch {
      // Preserve the main library view.
    }
  }


  async function loadPaperEvaluations() {
    setPaperEvaluationsLoading(true);
    setPaperEvaluationsError("");

    try {
      const response =
        await fetchAllocationPaperEvaluations(
          {
            method: "GET",
            credentials: "include",
            cache: "no-store",
          },
        );

      if (!response.ok) {
        throw new Error(
          `Paper evaluations request failed with HTTP ${response.status}.`,
        );
      }

      const payload =
        await response.json() as PaperEvaluationsPayload;

      setPaperEvaluations(
        Array.isArray(payload.evaluations)
          ? payload.evaluations
          : [],
      );
    } catch (error) {
      setPaperEvaluationsError(
        error instanceof Error
          ? error.message
          : "Allocation proposal snapshots are unavailable.",
      );
    } finally {
      setPaperEvaluationsLoading(false);
    }
  }


  function percent(value: number | undefined) {
    return typeof value === "number"
      ? `${(value * 100).toFixed(2)}%`
      : "—";
  }


  function amount(value: number | undefined) {
    return typeof value === "number"
      ? value.toFixed(4)
      : "—";
  }


  useEffect(() => {
    queueMicrotask(() => {
      void loadLibrary(
        market,
      );

      void loadEnabledSelection();
    });
  }, [market]);


  useEffect(() => {
    queueMicrotask(() => { void loadPaperEvaluations(); });
  }, []);


  const visible = useMemo(
    () => {
      const needle =
        query.trim().toLowerCase();

      if (!needle) {
        return strategies;
      }

      return strategies.filter(
        (row) => {
          const haystack = [
            row.strategy_name,
            row.category,
            row.definition,
            row.formula_or_rules,
            row.best_suited_for,
            ...(
              row.market_applicability
              ?? []
            ),
          ]
            .filter(Boolean)
            .join(" ")
            .toLowerCase();

          return haystack.includes(
            needle,
          );
        },
      );
    },
    [
      strategies,
      query,
    ],
  );


  function toggleStrategy(
    name: string,
  ) {
    setEnabledNames(
      (current) => {
        const next = new Set(
          current,
        );

        if (next.has(name)) {
          next.delete(name);
        } else {
          next.add(name);
        }

        return next;
      },
    );
  }


  function enableVisible() {
    setEnabledNames(
      (current) => {
        const next = new Set(
          current,
        );

        for (const row of visible) {
          next.add(
            row.strategy_name,
          );
        }

        return next;
      },
    );
  }


  function disableVisible() {
    setEnabledNames(
      (current) => {
        const next = new Set(
          current,
        );

        for (const row of visible) {
          next.delete(
            row.strategy_name,
          );
        }

        return next;
      },
    );
  }


  async function saveSelection() {
    setSaving(true);
    setMessage("");

    try {
      const response = await fetchEnabledStrategies(
        {
          method: "PUT",
          headers: {
            "Content-Type":
              "application/json",
            ...csrfHeaders(),
          },
          body: JSON.stringify({
            strategy_names:
              Array.from(
                enabledNames,
              ).sort(),
          }),
        },
      );

      const payload =
        await response.json();

      if (!response.ok) {
        throw new Error(
          payload?.detail
          ?? "Unable to save selection.",
        );
      }

      setMessage(
        `Saved ${payload.enabled_count} enabled strategies.`,
      );

      await loadEnabledSelection();

    } catch (error) {
      setMessage(
        error instanceof Error
          ? error.message
          : "Unable to save selection.",
      );
    } finally {
      setSaving(false);
    }
  }


  return (
    <PageContainer
      className="nv-strategy-library-page"
      data-testid="strategy-library-page"
    >
      <div className="nv-workspace-page">
        <PageHeader
          eyebrow="Strategy Library"
          title="Neuro reference strategies"
          description="Browse the research-derived strategy catalog available to Neuro. Choose which reference strategies may be used as strategy knowledge. These selections do not authorize trading or execution."
          badge={
            <StatusBadge tone="info">
              {strategies.length} loaded
            </StatusBadge>
          }
        />

        <section
          className="mt-6"
          aria-label="Allocation proposal snapshots"
          data-testid="allocation-paper-evaluations"
        >
          <Panel
            variant="elevated"
            className="p-5 md:p-6"
          >
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div className="min-w-0">
                <p className="nv-eyebrow">
                  Allocation proposals
                </p>

                <h2 className="nv-section-title">
                  Historical proposal snapshots
                </h2>

                <p className="nv-section-description max-w-3xl">
                  Fixed current target weights evaluated across the available
                  historical window with modeled rebalance costs. These are
                  not strategy backtests, forecasts, or trading instructions.
                </p>
              </div>

              <StatusBadge tone="info">
                Read-only
              </StatusBadge>
            </div>

            {paperEvaluationsLoading ? (
              <p className="mt-5 text-sm font-semibold text-slate-400">
                Loading proposal snapshots...
              </p>
            ) : paperEvaluationsError ? (
              <p className="mt-5 text-sm font-semibold text-red-300">
                {paperEvaluationsError}
              </p>
            ) : paperEvaluations.length === 0 ? (
              <p className="mt-5 text-sm font-semibold text-slate-400">
                No enabled allocation proposal snapshots are available.
              </p>
            ) : (
              <div className="mt-5 grid gap-4 md:grid-cols-2 2xl:grid-cols-3">
                {paperEvaluations.map(
                  (evaluation, index) => (
                    <Panel
                      key={
                        evaluation.proposal?.strategy_name
                        ?? `proposal-snapshot-${index}`
                      }
                      variant="default"
                      className="min-w-0 p-4"
                    >
                      <p className="font-black text-slate-100">
                        {
                          evaluation.proposal?.strategy_name
                          ?? "Allocation proposal"
                        }
                      </p>

                      <p className="mt-2 text-xs leading-5 text-slate-400">
                        Historical modeled snapshot · not a forecast
                      </p>

                      <dl className="mt-4 grid grid-cols-2 gap-3 text-sm">
                        <div>
                          <dt className="text-slate-500">
                            Cumulative return
                          </dt>
                          <dd className="font-bold text-cyan-200">
                            {percent(evaluation.cumulative_return)}
                          </dd>
                        </div>

                        <div>
                          <dt className="text-slate-500">
                            Maximum drawdown
                          </dt>
                          <dd className="font-bold text-slate-200">
                            {percent(evaluation.max_drawdown)}
                          </dd>
                        </div>

                        <div>
                          <dt className="text-slate-500">
                            Ending value
                          </dt>
                          <dd className="font-bold text-slate-200">
                            {amount(evaluation.ending_value)}
                          </dd>
                        </div>

                        <div>
                          <dt className="text-slate-500">
                            Observations
                          </dt>
                          <dd className="font-bold text-slate-200">
                            {evaluation.observation_count ?? "—"}
                          </dd>
                        </div>
                      </dl>

                      <p className="mt-4 text-xs leading-5 text-slate-500">
                        Estimated modeled cost:{" "}
                        {amount(evaluation.estimated_transaction_cost)}
                      </p>
                    </Panel>
                  ),
                )}
              </div>
            )}
          </Panel>
        </section>


        <Panel
          variant="elevated"
          className="p-5 md:p-6"
        >
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="nv-eyebrow">
                Catalog controls
              </p>

              <h2 className="nv-section-title">
                Find and manage strategies
              </h2>

              <p className="nv-section-description">
                Filter the catalog by market or search strategy names,
                definitions, formulas, rules, and suitability.
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <StatusBadge tone="info">
                {visible.length} visible
              </StatusBadge>

              <StatusBadge tone="success">
                {enabledNames.size} enabled
              </StatusBadge>
            </div>
          </div>


          <div className="mt-6 grid gap-4 lg:grid-cols-[220px_minmax(0,1fr)]">
            <label className="block min-w-0">
              <span className="nv-eyebrow">
                Market
              </span>

              <select
                value={market}
                onChange={
                  (
                    event,
                  ) =>
                    setMarket(
                      event.target.value,
                    )
                }
                className="nv-input mt-2"
              >
                {MARKET_OPTIONS.map(
                  (
                    [
                      value,
                      label,
                    ],
                  ) => (
                    <option
                      key={value}
                      value={value}
                    >
                      {label}
                    </option>
                  ),
                )}
              </select>
            </label>


            <label className="block min-w-0">
              <span className="nv-eyebrow">
                Search
              </span>

              <Input
                value={query}
                onChange={
                  (
                    event,
                  ) =>
                    setQuery(
                      event.target.value,
                    )
                }
                placeholder="Search strategies, definitions, formulas, markets..."
                className="mt-2"
              />
            </label>
          </div>


          <div className="mt-5 flex flex-wrap gap-3 border-t border-white/[0.07] pt-5">
            <Button
              variant="secondary"
              size="sm"
              onClick={
                enableVisible
              }
            >
              Enable visible
            </Button>

            <Button
              variant="secondary"
              size="sm"
              onClick={
                disableVisible
              }
            >
              Disable visible
            </Button>

            <Button
              variant="ghost"
              size="sm"
              onClick={
                () =>
                  setEnabledNames(
                    new Set(),
                  )
              }
            >
              Disable all
            </Button>

            <Button
              variant="primary"
              size="sm"
              onClick={
                saveSelection
              }
              disabled={saving}
            >
              {
                saving
                  ? "Saving..."
                  : "Save selection"
              }
            </Button>
          </div>
        </Panel>


        {message ? (
          <StatusMessage
            tone={
              message.startsWith(
                "Saved "
              )
                ? "success"
                : "danger"
            }
          >
            {message}
          </StatusMessage>
        ) : null}


        {loading ? (
          <StatusMessage tone="info">
            Loading Strategy Library...
          </StatusMessage>

        ) : visible.length === 0 ? (
          <Panel
            variant="muted"
            className="p-6"
          >
            <div className="text-center">
              <p className="nv-eyebrow">
                No results
              </p>

              <h2 className="nv-section-title">
                No strategies match this view
              </h2>

              <p className="nv-section-description mx-auto">
                Clear the search or choose another market filter.
              </p>
            </div>
          </Panel>

        ) : (
          <section
            aria-label="Strategy catalog"
            data-testid="strategy-library-catalog"
          >
            <div className="mb-4 flex flex-wrap items-end justify-between gap-4">
              <div>
                <p className="nv-eyebrow">
                  Catalog
                </p>

                <h2 className="nv-section-title">
                  Available reference strategies
                </h2>
              </div>

              <p className="text-sm font-semibold text-slate-400">
                Showing{" "}
                <strong className="text-slate-100">
                  {visible.length}
                </strong>{" "}
                strategies
              </p>
            </div>


            <div className="grid gap-4 md:grid-cols-2 2xl:grid-cols-3">
              {visible.map(
                (
                  strategy,
                ) => {
                  const enabled =
                    enabledNames.has(
                      strategy.strategy_name,
                    );

                  const markets =
                    strategy.market_applicability
                    ?? [];

                  return (
                    <Panel
                      key={
                        strategy.strategy_name
                      }
                      variant="default"
                      className="min-w-0 overflow-hidden p-5"
                    >
                      <article
                        className="flex h-full min-w-0 flex-col"
                        data-testid="strategy-library-item"
                        data-strategy-name={
                          strategy.strategy_name
                        }
                      >
                        <div className="flex min-w-0 items-start justify-between gap-4">
                          <div className="min-w-0 flex-1">
                            <p className="nv-eyebrow">
                              {
                                (
                                  strategy.category
                                  ?? "Uncategorized"
                                ).replaceAll(
                                  "_",
                                  " ",
                                )
                              }
                            </p>

                            <h3 className="nv-card-title mt-2 break-words">
                              {
                                strategy.strategy_name
                              }
                            </h3>
                          </div>

                          <StatusBadge
                            tone={
                              enabled
                                ? "success"
                                : "neutral"
                            }
                          >
                            {
                              enabled
                                ? "Enabled"
                                : "Available"
                            }
                          </StatusBadge>
                        </div>


                        {strategy.definition ? (
                          <p className="nv-card-description mt-3 line-clamp-3">
                            {
                              strategy.definition
                            }
                          </p>
                        ) : (
                          <p className="nv-card-description mt-3 italic">
                            No summary available.
                          </p>
                        )}


                        {markets.length > 0 ? (
                          <div className="mt-4 flex flex-wrap gap-2">
                            {markets
                              .slice(
                                0,
                                4,
                              )
                              .map(
                                (
                                  marketName,
                                ) => (
                                  <span
                                    key={
                                      `${strategy.strategy_name}-${marketName}`
                                    }
                                    className="rounded-full border border-cyan-400/15 bg-cyan-400/[0.05] px-2.5 py-1 text-xs font-bold capitalize text-cyan-200/80"
                                  >
                                    {
                                      marketName.replaceAll(
                                        "_",
                                        " ",
                                      )
                                    }
                                  </span>
                                ),
                              )}

                            {markets.length > 4 ? (
                              <span className="rounded-full border border-white/[0.08] bg-white/[0.03] px-2.5 py-1 text-xs font-bold text-slate-500">
                                +{markets.length - 4}
                              </span>
                            ) : null}
                          </div>
                        ) : null}


                        <div className="mt-auto pt-5">
                          <details>
                            <summary className="cursor-pointer select-none border-t border-white/[0.07] pt-4 text-sm font-black text-cyan-300 transition hover:text-cyan-100">
                              View strategy details
                            </summary>

                            <div className="mt-4 space-y-4">
                              {strategy.formula_or_rules ? (
                                <div>
                                  <p className="nv-eyebrow">
                                    Formula / rules
                                  </p>

                                  <div className="mt-2 rounded-xl border border-white/[0.07] bg-black/20 p-3">
                                    <p className="break-words font-mono text-xs leading-6 text-slate-300">
                                      {
                                        strategy.formula_or_rules
                                      }
                                    </p>
                                  </div>
                                </div>
                              ) : null}


                              {strategy.best_suited_for ? (
                                <div>
                                  <p className="nv-eyebrow">
                                    Best suited for
                                  </p>

                                  <p className="mt-2 text-sm leading-6 text-slate-400">
                                    {
                                      strategy.best_suited_for
                                    }
                                  </p>
                                </div>
                              ) : null}


                              {markets.length > 0 ? (
                                <div>
                                  <p className="nv-eyebrow">
                                    Market applicability
                                  </p>

                                  <div className="mt-2 flex flex-wrap gap-2">
                                    {markets.map(
                                      (
                                        marketName,
                                      ) => (
                                        <span
                                          key={
                                            `${strategy.strategy_name}-detail-${marketName}`
                                          }
                                          className="rounded-full border border-white/[0.08] bg-white/[0.03] px-2.5 py-1 text-xs font-bold capitalize text-slate-400"
                                        >
                                          {
                                            marketName.replaceAll(
                                              "_",
                                              " ",
                                            )
                                          }
                                        </span>
                                      ),
                                    )}
                                  </div>
                                </div>
                              ) : null}
                            </div>
                          </details>


                          <label className="mt-4 flex cursor-pointer items-center gap-3 border-t border-white/[0.07] pt-4">
                            <input
                              type="checkbox"
                              checked={enabled}
                              onChange={
                                () =>
                                  toggleStrategy(
                                    strategy.strategy_name,
                                  )
                              }
                              className="h-4 w-4 accent-cyan-400"
                            />

                            <span className="text-sm font-bold text-slate-300">
                              {
                                enabled
                                  ? "Enabled for Neuro"
                                  : "Enable for Neuro"
                              }
                            </span>
                          </label>
                        </div>
                      </article>
                    </Panel>
                  );
                },
              )}
            </div>
          </section>
        )}
      </div>
    </PageContainer>
  );
}
