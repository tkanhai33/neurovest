"use client";

import {
  fetchEnabledStrategies,
  fetchStrategyLibrary,
} from "../../../services/strategyLibraryService";

import {
  useEffect,
  useMemo,
  useState,
} from "react";


import StrategyAdaptiveTrainingAction from "./StrategyAdaptiveTrainingAction";
import {
  Panel,
  StatusBadge,
} from "../../../components/ui";

type UnknownRecord = Record<
  string,
  unknown
>;

type LibraryStrategy = {
  strategy_name: string;
  category?: string | null;
  definition?: string | null;
  formula_or_rules?: string | null;
  best_suited_for?: string | null;
  market_applicability?: string[];
  enabled?: boolean;
};

type LibraryPayload = {
  strategy_count?: number;
  catalog_total?: number;
  enabled_count?: number;
  market_filter?: string;
  strategies?: LibraryStrategy[];
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


type StrategyActivity = {
  action: string;
  name: string;
  symbol: string;
  timestamp: string | null;
};

type StrategyUsage = {
  count: number;
  name: string;
  percentage: number;
};

type UserStrategiesWorkspaceProps = {
  orders: readonly unknown[];
};

const STRATEGY_KEYS = [
  "strategy_name",
  "strategyName",
  "strategy_id",
  "strategyId",
  "strategy",
  "decision_strategy",
  "decisionStrategy",
  "provider_strategy",
  "providerStrategy",
] as const;

const PROVIDER_KEYS = [
  "strategy_provider",
  "strategyProvider",
  "decision_provider",
  "decisionProvider",
  "provider",
] as const;

const SYMBOL_KEYS = [
  "symbol",
  "ticker",
  "asset_symbol",
  "assetSymbol",
] as const;

const ACTION_KEYS = [
  "signal",
  "action",
  "side",
  "decision",
  "order_type",
  "orderType",
] as const;

const TIMESTAMP_KEYS = [
  "timestamp",
  "created_at",
  "createdAt",
  "executed_at",
  "executedAt",
  "updated_at",
  "updatedAt",
] as const;

function asRecord(
  value: unknown,
): UnknownRecord | null {
  if (
    typeof value !== "object" ||
    value === null ||
    Array.isArray(value)
  ) {
    return null;
  }

  return value as UnknownRecord;
}

function readString(
  record: UnknownRecord,
  keys: readonly string[],
): string | null {
  for (const key of keys) {
    const value = record[key];

    if (
      typeof value === "string" &&
      value.trim()
    ) {
      return value.trim();
    }

    if (
      typeof value === "number" &&
      Number.isFinite(value)
    ) {
      return String(value);
    }
  }

  return null;
}

function normalizeLabel(
  value: string,
): string {
  return value
    .replace(/[_-]+/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .replace(
      /\b\w/g,
      (character) =>
        character.toUpperCase(),
    );
}

function resolveStrategyName(
  record: UnknownRecord,
): string | null {
  const strategy = readString(
    record,
    STRATEGY_KEYS,
  );

  if (strategy) {
    return normalizeLabel(strategy);
  }

  const provider = readString(
    record,
    PROVIDER_KEYS,
  );

  if (provider) {
    return normalizeLabel(provider);
  }

  return null;
}

function resolveActivity(
  value: unknown,
): StrategyActivity | null {
  const record = asRecord(value);

  if (!record) {
    return null;
  }

  const name = resolveStrategyName(
    record,
  );

  if (!name) {
    return null;
  }

  return {
    name,
    symbol:
      readString(
        record,
        SYMBOL_KEYS,
      ) ?? "—",
    action:
      readString(
        record,
        ACTION_KEYS,
      ) ?? "Recorded",
    timestamp:
      readString(
        record,
        TIMESTAMP_KEYS,
      ),
  };
}

function formatTimestamp(
  value: string | null,
): string {
  if (!value) {
    return "Time unavailable";
  }

  const parsed = new Date(value);

  if (
    Number.isNaN(
      parsed.getTime(),
    )
  ) {
    return value;
  }

  return new Intl.DateTimeFormat(
    "en-US",
    {
      dateStyle: "medium",
      timeStyle: "short",
    },
  ).format(parsed);
}

export default function UserStrategiesWorkspace({
  orders,
}: UserStrategiesWorkspaceProps) {
  const [libraryStrategies, setLibraryStrategies] =
    useState<LibraryStrategy[]>([]);

  const [enabledNames, setEnabledNames] =
    useState<Set<string>>(
      new Set(),
    );

  const [libraryLoading, setLibraryLoading] =
    useState(true);

  const [libraryError, setLibraryError] =
    useState<string | null>(null);

  const [market, setMarket] =
    useState("all");

  const [query, setQuery] =
    useState("");

  const [pagination, setPagination] =
    useState({
      key: "",
      limit: 24,
    });

  const [catalogTotal, setCatalogTotal] =
    useState(0);


  useEffect(
    () => {
      let cancelled = false;

      async function loadLibrary() {
        setLibraryLoading(true);
        setLibraryError(null);

        try {
          const params =
            market === "all"
              ? ""
              : `?market=${encodeURIComponent(
                  market,
                )}`;

          const [
            libraryResponse,
            enabledResponse,
          ] = await Promise.all([
            fetchStrategyLibrary(params,
              {
                method: "GET",
                credentials: "include",
                cache: "no-store",
              },
            ),

            fetchEnabledStrategies(
              {
                method: "GET",
                credentials: "include",
                cache: "no-store",
              },
            ),
          ]);

          if (!libraryResponse.ok) {
            throw new Error(
              `Strategy Library request failed with HTTP ${libraryResponse.status}.`,
            );
          }

          const libraryPayload =
            await libraryResponse.json() as LibraryPayload;

          const rows =
            Array.isArray(
              libraryPayload.strategies,
            )
              ? libraryPayload.strategies
              : [];

          if (!cancelled) {
            setLibraryStrategies(
              rows,
            );

            setCatalogTotal(
              Number(
                libraryPayload.catalog_total
                ?? libraryPayload.strategy_count
                ?? rows.length,
              ),
            );
          }

          if (enabledResponse.ok) {
            const enabledPayload =
              await enabledResponse.json() as LibraryPayload;

            const enabledRows =
              Array.isArray(
                enabledPayload.strategies,
              )
                ? enabledPayload.strategies
                : [];

            if (!cancelled) {
              setEnabledNames(
                new Set(
                  enabledRows.map(
                    (
                      row,
                    ) =>
                      row.strategy_name,
                  ),
                ),
              );
            }
          }

        } catch (error) {

          if (!cancelled) {
            setLibraryStrategies(
              [],
            );

            setCatalogTotal(
              0,
            );

            setLibraryError(
              error instanceof Error
                ? error.message
                : "Strategy Library is unavailable.",
            );
          }

        } finally {

          if (!cancelled) {
            setLibraryLoading(
              false,
            );
          }
        }
      }

      void loadLibrary();

      return () => {
        cancelled = true;
      };
    },
    [
      market,
    ],
  );


  const visibleLibraryStrategies =
    useMemo(
      () => {
        const needle =
          query.trim().toLowerCase();

        if (!needle) {
          return libraryStrategies;
        }

        return libraryStrategies.filter(
          (
            row,
          ) => {
            const searchable = [
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

            return searchable.includes(
              needle,
            );
          },
        );
      },
      [
        libraryStrategies,
        query,
      ],
    );



  // F7-R2: Client-side catalog exploration only.
  // Existing owner-scoped API data remains authoritative.
  const [statusFilter, setStatusFilter] =
    useState<"all" | "enabled" | "available">("all");

  const [familyFilter, setFamilyFilter] =
    useState("all");

  const strategyFamilies = useMemo(
    () =>
      Array.from(
        new Set(
          libraryStrategies
            .map((row) => (row.category ?? "").trim())
            .filter(Boolean),
        ),
      ).sort((a, b) => a.localeCompare(b)),
    [libraryStrategies],
  );

  const filteredLibraryStrategies = useMemo(
    () =>
      visibleLibraryStrategies.filter((row) => {
        const enabled =
          enabledNames.has(row.strategy_name) ||
          row.enabled === true;

        const matchesStatus =
          statusFilter === "all" ||
          (statusFilter === "enabled" && enabled) ||
          (statusFilter === "available" && !enabled);

        const matchesFamily =
          familyFilter === "all" ||
          (row.category ?? "") === familyFilter;

        return matchesStatus && matchesFamily;
      }),
    [
      visibleLibraryStrategies,
      enabledNames,
      statusFilter,
      familyFilter,
    ],
  );

  const filterKey = JSON.stringify([market, query, statusFilter, familyFilter]);

  const visibleLimit =
    pagination.key === filterKey
      ? pagination.limit
      : 24;

  const displayedLibraryStrategies =
    filteredLibraryStrategies.slice(0, visibleLimit);

  const activity = orders
    .map(resolveActivity)
    .filter(
      (
        item,
      ): item is StrategyActivity =>
        item !== null,
    );

  const counts = new Map<
    string,
    number
  >();

  for (const item of activity) {
    counts.set(
      item.name,
      (
        counts.get(item.name) ??
        0
      ) + 1,
    );
  }

  const totalRecordedUses =
    activity.length;

  const strategies:
    StrategyUsage[] = Array.from(
      counts.entries(),
    )
      .map(
        (
          [
            name,
            count,
          ],
        ) => ({
          name,
          count,
          percentage:
            totalRecordedUses > 0
              ? (
                  count /
                  totalRecordedUses
                ) * 100
              : 0,
        }),
      )
      .sort(
        (
          left,
          right,
        ) =>
          right.count -
          left.count,
      );

  const recentActivity = [
    ...activity,
  ]
    .sort(
      (
        left,
        right,
      ) => {
        const leftTime =
          left.timestamp
            ? Date.parse(
                left.timestamp,
              )
            : 0;

        const rightTime =
          right.timestamp
            ? Date.parse(
                right.timestamp,
              )
            : 0;

        return (
          (
            Number.isNaN(
              rightTime,
            )
              ? 0
              : rightTime
          ) -
          (
            Number.isNaN(
              leftTime,
            )
              ? 0
              : leftTime
          )
        );
      },
    )
    .slice(0, 12);

  return (
    <div className="nv-user-strategies">
      <nav
        aria-label="Strategy workspace navigation"
        className="mb-4 flex flex-wrap items-center gap-2 rounded-2xl border border-white/[0.08] bg-[#061120]/70 p-3"
      >
        <a
          href="#f7-strategy-catalog"
          className="inline-flex min-h-11 items-center rounded-xl border border-cyan-300/20 bg-cyan-300/[0.07] px-4 py-2 text-sm font-semibold text-cyan-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-cyan-300"
        >
          Browse catalog
        </a>
        <span className="text-xs text-slate-400">
          Filter and inspect research strategies.
          Enabled does not mean executing.
        </span>
      </nav>
      <section
        id="f7-strategy-catalog"
        className="nv-user-strategy-catalog scroll-mt-24"
        data-testid="user-strategy-library"
      >
        <Panel
          variant="elevated"
          className="p-5 md:p-6"
        >
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="min-w-0">
              <p className="nv-eyebrow">
                Strategy Library
              </p>

              <h3 className="nv-section-title">
                Neuro reference strategies
              </h3>

              <p className="nv-section-description">
                Browse the same research-derived catalog available in
                the full Strategy Library. Search or filter the catalog,
                then open a strategy when you want its detailed rules.
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <StatusBadge tone="info">
                {catalogTotal || libraryStrategies.length} catalog
              </StatusBadge>

              <StatusBadge tone="success">
                {enabledNames.size} enabled
              </StatusBadge>
            </div>
          </div>


          <div className="mt-5 grid gap-3 lg:grid-cols-[220px_minmax(0,1fr)]">
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

              <input
                value={query}
                onChange={
                  (
                    event,
                  ) =>
                    setQuery(
                      event.target.value,
                    )
                }
                placeholder="Search strategies, formulas, definitions, markets..."
                className="nv-input mt-2"
              />
            </label>
          </div>



          <div
            className="mt-4 grid gap-3 sm:grid-cols-2"
            data-testid="f7-strategy-filters"
          >
            <label className="block min-w-0">
              <span className="nv-eyebrow">Selection status</span>
              <select
                data-testid="f7-strategy-status-filter"
                className="nv-input mt-2"
                value={statusFilter}
                onChange={(event) =>
                  setStatusFilter(
                    event.target.value as
                      "all" | "enabled" | "available",
                  )
                }
              >
                <option value="all">All strategies</option>
                <option value="enabled">Enabled strategies</option>
                <option value="available">Not enabled</option>
              </select>
            </label>

            <label className="block min-w-0">
              <span className="nv-eyebrow">Strategy family</span>
              <select
                data-testid="f7-strategy-family-filter"
                className="nv-input mt-2"
                value={familyFilter}
                onChange={(event) =>
                  setFamilyFilter(event.target.value)
                }
              >
                <option value="all">All strategy families</option>
                {strategyFamilies.map((family) => (
                  <option key={family} value={family}>
                    {family.replaceAll("_", " ")}
                  </option>
                ))}
              </select>
            </label>
          </div>

          {(query || market !== "all" ||
            statusFilter !== "all" || familyFilter !== "all") && (
            <div className="mt-3 flex flex-wrap items-center justify-between gap-3">
              <p className="text-xs text-slate-400" aria-live="polite">
                {filteredLibraryStrategies.length} matching strategies
              </p>
              <button
                type="button"
                data-testid="f7-strategy-clear-filters"
                className="nv-button nv-button-secondary nv-button-sm"
                onClick={() => {
                  setMarket("all");
                  setQuery("");
                  setStatusFilter("all");
                  setFamilyFilter("all");
                  setPagination({ key: "", limit: 24 });
                }}
              >
                Clear filters
              </button>
            </div>
          )}

          <div className="mt-4 flex flex-wrap items-center justify-between gap-3 border-t border-white/[0.07] pt-4">
            <p
              className="text-sm font-semibold text-slate-400"
              data-testid="strategy-library-visible-count"
            >
              Showing{" "}
              <strong className="text-slate-100">
                {filteredLibraryStrategies.length}
              </strong>{" "}
              strategies
              {
                market !== "all"
                  ? ` for ${market.replaceAll("_", " ")}`
                  : ""
              }
            </p>

            <a
              href="/strategy-library"
              className="nv-button nv-button-secondary nv-button-sm"
            >
              Manage enabled strategies
            </a>
          </div>
        </Panel>


        {libraryLoading ? (
          <div className="mt-5">
            <Panel
              variant="muted"
              className="p-5"
            >
              <p className="text-sm font-semibold text-slate-400">
                Loading Strategy Library...
              </p>
            </Panel>
          </div>

        ) : libraryError ? (
          <div className="mt-5">
            <Panel
              variant="muted"
              className="p-5"
            >
              <p className="font-black text-red-300">
                Strategy Library unavailable
              </p>

              <p className="mt-2 text-sm leading-6 text-slate-400">
                {libraryError}
              </p>
            </Panel>
          </div>

        ) : filteredLibraryStrategies.length === 0 ? (
          <div className="mt-5">
            <Panel
              variant="muted"
              className="p-6"
            >
              <div className="text-center">
                <p className="nv-eyebrow">
                  No results
                </p>

                <h4 className="nv-section-title">
                  No strategies match this view
                </h4>

                <p className="nv-section-description mx-auto">
                  Clear the search or choose another market filter.
                </p>
              </div>
            </Panel>
          </div>

        ) : (
          <div
            className="mt-5 grid gap-3 md:grid-cols-2 2xl:grid-cols-3"
            data-testid="strategy-library-list"
          >
            {displayedLibraryStrategies.map(
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

                          <h4 className="nv-card-title mt-2 break-words">
                            {
                              strategy.strategy_name
                            }
                          </h4>
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
                      </div>
                    </article>
                  </Panel>
                );
              },
            )}
          </div>
        )}
        {!libraryLoading &&
          !libraryError &&
          filteredLibraryStrategies.length > visibleLimit ? (
            <div className="mt-5 flex justify-center">
              <button
                type="button"
                className="nv-button nv-button-secondary"
                onClick={() =>
                  setPagination({
                    key: filterKey,
                    limit: visibleLimit + 24,
                  })
                }
                data-testid="strategy-library-show-more"
              >
                Show 24 more
                {" · "}
                {Math.min(
                  visibleLimit,
                  filteredLibraryStrategies.length,
                )} of {filteredLibraryStrategies.length} shown
              </button>
            </div>
          ) : null}
      </section>



      <section className="mt-8">
        <div className="nv-user-workspace-heading">
          <div>
            <p className="nv-eyebrow text-[10px] leading-4 tracking-[0.16em]">
              Account activity
            </p>

            <h3 className="nv-section-title">
              Strategies observed in your history
            </h3>

            <p className="nv-section-description">
              Usage counts below are reconstructed only from this
              account&apos;s recorded decisions and orders.
            </p>
          </div>

          <StatusBadge tone="violet">
            {strategies.length} observed
          </StatusBadge>
        </div>

        {strategies.length === 0 ? (
          <Panel
            variant="muted"
            className="nv-user-strategy-empty"
          >
            <p className="nv-user-strategy-empty-title">
              No strategy-specific account activity yet.
            </p>

            <p className="nv-user-strategy-empty-description">
              This does not affect the Strategy Library above.
              Historical usage will appear here when account records
              identify a strategy or provider.
            </p>
          </Panel>
        ) : (
          <div className="nv-user-strategy-list">
            {strategies.map(
              (
                strategy,
              ) => (
                <Panel
                  key={strategy.name}
                  variant="default"
                  className="nv-user-strategy-row"
                >
                  <div className="nv-user-strategy-row-main">
                    <div>
                      <h4 className="nv-user-strategy-name">
                        {strategy.name}
                      </h4>

                      <StrategyAdaptiveTrainingAction
                        strategyName={strategy.name}
                      />

                      <p className="nv-user-strategy-usage-label">
                        Used {strategy.count}{" "}
                        {strategy.count === 1
                          ? "time"
                          : "times"}{" "}
                        for this account
                      </p>
                    </div>

                    <div className="nv-user-strategy-count">
                      <strong>
                        {strategy.count}
                      </strong>

                      <span>
                        uses
                      </span>
                    </div>
                  </div>

                  <progress
                    className="nv-user-strategy-progress"
                    max="100"
                    value={
                      Math.max(
                        strategy.percentage,
                        2,
                      )
                    }
                    aria-label={`${strategy.name} strategy activity`}
                  />

                  <p className="nv-user-strategy-percentage">
                    {strategy.percentage.toFixed(1)}% of recorded
                    strategy activity
                  </p>
                </Panel>
              ),
            )}
          </div>
        )}
      </section>


      <section className="nv-user-strategy-history">
        <div className="nv-user-workspace-heading">
          <div>
            <p className="nv-eyebrow text-[10px] leading-4 tracking-[0.16em]">
              Strategy history
            </p>

            <h3 className="nv-section-title">
              Recent Neuro strategy activity
            </h3>

            <p className="nv-section-description">
              The latest account records that identify the strategy
              or strategy provider used by Neuro.
            </p>
          </div>

          <StatusBadge tone="info">
            {totalRecordedUses} recorded uses
          </StatusBadge>
        </div>

        {recentActivity.length === 0 ? (
          <Panel
            variant="muted"
            className="nv-user-strategy-empty"
          >
            <p className="nv-user-strategy-empty-description">
              No strategy-specific history is available for this
              account yet.
            </p>
          </Panel>
        ) : (
          <Panel
            variant="default"
            className="nv-user-strategy-history-panel"
          >
            <div className="nv-user-strategy-history-table-wrap">
              <table className="nv-user-strategy-history-table">
                <thead>
                  <tr>
                    <th>
                      Strategy
                    </th>

                    <th>
                      Symbol
                    </th>

                    <th>
                      Action
                    </th>

                    <th>
                      Time
                    </th>
                  </tr>
                </thead>

                <tbody>
                  {recentActivity.map(
                    (
                      item,
                      index,
                    ) => (
                      <tr
                        key={[
                          item.name,
                          item.symbol,
                          item.timestamp ??
                            "unknown",
                          String(index),
                        ].join(":")}
                      >
                        <td>
                          <strong>
                            {item.name}
                          </strong>
                        </td>

                        <td>
                          {item.symbol}
                        </td>

                        <td>
                          <StatusBadge tone="info">
                            {normalizeLabel(
                              item.action,
                            )}
                          </StatusBadge>
                        </td>

                        <td>
                          {formatTimestamp(
                            item.timestamp,
                          )}
                        </td>
                      </tr>
                    ),
                  )}
                </tbody>
              </table>
            </div>
          </Panel>
        )}
      </section>


    </div>
  );
}
