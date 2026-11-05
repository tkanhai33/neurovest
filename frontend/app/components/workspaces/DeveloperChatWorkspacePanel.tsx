"use client";

import {
  useCallback,
  useEffect,
  useState,
} from "react";


type CountDistribution = {
  count: number;
};

type IntentDistribution =
  CountDistribution & {
    intent: string;
  };

type ValueDistribution =
  CountDistribution & {
    value: string;
  };

type ToolStatusDistribution =
  CountDistribution & {
    status: string;
  };

type ToolDistribution =
  CountDistribution & {
    tool: string;
  };

type QualifiedStatistics = {
  learned_strategy_knowledge?: Array<{
    id: string;
    strategy_id: string;
    strategy_version: number;
    strategy_name: string;
    name: string;
    strategy_family: string | null;
    asset_class: string | null;
    generation_source: string | null;
    validation_status: string | null;
    lifecycle_state: string;
    admission_decision: string | null;
    promotion_status: string | null;
    history_row_count: number | null;
    feature_count: number | null;
    symbols: string[];
    created_at: string | null;
    updated_at: string | null;
  }>;

  conversation_count: number;
  total_message_count: number;
  user_message_count: number;
  assistant_message_count: number;
  tool_evidence_count: number;
  tool_evidence_success_count: number;

  intent_distribution:
    IntentDistribution[];

  provider_distribution_internal:
    ValueDistribution[];

  model_distribution_internal:
    ValueDistribution[];

  tool_status_distribution:
    ToolStatusDistribution[];

  tool_distribution:
    ToolDistribution[];
};

type DeveloperChatStatistics = {
  status: string;
  classification: string;
  source: string;
  scope: string;
  visibility: string;
  read_only: boolean;
  database_mutation: boolean;

  qualified_statistics:
    QualifiedStatistics;

  not_yet_qualified:
    string[];

  broker_execution:
    boolean;

  live_execution:
    boolean;
};


function formatNumber(
  value: number
): string {
  return value.toLocaleString();
}


function humanize(
  value: string
): string {
  return value
    .replaceAll(
      "_",
      " "
    )
    .replace(
      /\b\w/g,
      (
        character
      ) =>
        character.toUpperCase()
    );
}


function MetricCard({
  label,
  value,
  detail,
}: {
  label: string;
  value: string;
  detail?: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
      <p className="text-[11px] font-black uppercase tracking-[0.2em] text-slate-500">
        {label}
      </p>

      <p className="mt-3 text-3xl font-black text-white">
        {value}
      </p>

      {detail && (
        <p className="mt-2 text-xs leading-5 text-slate-400">
          {detail}
        </p>
      )}
    </div>
  );
}


function DistributionCard({
  title,
  subtitle,
  rows,
}: {
  title: string;
  subtitle: string;

  rows: Array<{
    label: string;
    count: number;
  }>;
}) {
  const maximum =
    Math.max(
      1,
      ...rows.map(
        (
          row
        ) =>
          row.count
      )
    );

  return (
    <section className="rounded-3xl border border-slate-800 bg-slate-950/70 p-5">
      <div>
        <p className="text-xs font-black uppercase tracking-[0.22em] text-cyan-300">
          {subtitle}
        </p>

        <h3 className="mt-2 text-xl font-black text-white">
          {title}
        </h3>
      </div>

      <div className="mt-5 space-y-3">
        {rows.length === 0 ? (
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4 text-sm text-slate-400">
            No qualified records.
          </div>
        ) : (
          rows.map(
            (
              row
            ) => {
              const width =
                Math.max(
                  2,
                  (
                    row.count
                    / maximum
                  )
                  * 100
                );

              return (
                <div
                  key={
                    `${title}-${row.label}`
                  }
                  className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4"
                >
                  <div className="flex items-start justify-between gap-4">
                    <span className="min-w-0 break-words text-sm font-bold text-slate-200">
                      {humanize(
                        row.label
                      )}
                    </span>

                    <span className="shrink-0 text-sm font-black text-white">
                      {formatNumber(
                        row.count
                      )}
                    </span>
                  </div>

                  <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-slate-800">
                    <progress
                      className="nv-csp-progress nv-csp-progress-cyan"
                      max="100"
                      value={width}
                      aria-label={`${title}: ${row.label}`}
                    />
                  </div>
                </div>
              );
            }
          )
        )}
      </div>
    </section>
  );
}


export default function DeveloperChatWorkspacePanel() {
  const [
    statistics,
    setStatistics,
  ] =
    useState<DeveloperChatStatistics | null>(
      null
    );

  const [
    loading,
    setLoading,
  ] =
    useState(
      true
    );

  const [
    error,
    setError,
  ] =
    useState<string | null>(
      null
    );

  const [
    lastUpdated,
    setLastUpdated,
  ] =
    useState<string | null>(
      null
    );


  const loadStatistics =
    useCallback(
      async () => {
        setLoading(
          true
        );

        setError(
          null
        );

        try {
          const response =
            await fetch(
              "/api/v1/developer/chat/statistics",
              {
                method:
                  "GET",

                credentials:
                  "include",

                headers: {
                  Accept:
                    "application/json",

                  "Cache-Control":
                    "no-cache",
                },

                cache:
                  "no-store",
              }
            );

          const payload =
            await response
              .json()
              .catch(
                () =>
                  null
              );

          if (
            !response.ok
          ) {
            const detail =
              payload &&
              typeof payload ===
                "object" &&
              "detail" in payload
                ? String(
                    payload.detail
                  )
                : (
                    `Statistics request failed with HTTP ${response.status}.`
                  );

            throw new Error(
              detail
            );
          }

          if (
            !payload ||
            typeof payload !==
              "object" ||
            !(
              "qualified_statistics"
              in payload
            )
          ) {
            throw new Error(
              "Statistics endpoint returned an unexpected payload."
            );
          }

          setStatistics(
            payload as
              DeveloperChatStatistics
          );

          setLastUpdated(
            new Date()
              .toLocaleTimeString()
          );

        } catch (
          requestError
        ) {
          setError(
            requestError
              instanceof Error
              ? requestError.message
              : "Developer Chat statistics are unavailable."
          );

        } finally {
          setLoading(
            false
          );
        }
      },
      []
    );


  useEffect(
    () => {
      queueMicrotask(() => { void loadStatistics(); });
    },
    [
      loadStatistics,
    ]
  );


  const qualified =
    statistics
      ?.qualified_statistics;

  const successRate =
    qualified &&
    qualified.tool_evidence_count >
      0
      ? (
          (
            qualified
              .tool_evidence_success_count
            /
            qualified
              .tool_evidence_count
          )
          * 100
        ).toFixed(
          1
        )
      : null;


  return (
    <section
      className="mt-6 space-y-6"
      data-testid="developer-chat-statistics-workspace"
    >
      <section className="overflow-hidden rounded-3xl border border-cyan-400/20 bg-slate-950/80">
        <div className="border-b border-slate-800 bg-gradient-to-r from-cyan-500/10 via-fuchsia-500/10 to-transparent p-6">
          <div className="flex flex-wrap items-start justify-between gap-5">
            <div>
              <p className="text-xs font-black uppercase tracking-[0.3em] text-cyan-300">
                Developer Chat
              </p>

              <h2 className="mt-2 text-3xl font-black text-white">
                Chat Statistics
              </h2>

              <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-400">
                Server-authoritative,
                read-only Chat
                telemetry from the
                qualified PostgreSQL
                statistics boundary.
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <span className="rounded-full border border-emerald-400/20 bg-emerald-400/5 px-3 py-1.5 text-xs font-bold text-emerald-300">
                Read only
              </span>

              <span className="rounded-full border border-cyan-400/20 bg-cyan-400/5 px-3 py-1.5 text-xs font-bold text-cyan-300">
                Developer internal
              </span>
            </div>
          </div>

          <div className="mt-5 flex flex-wrap items-center gap-3">
            <button
              type="button"
              onClick={
                () => {
                  void loadStatistics();
                }
              }
              disabled={
                loading
              }
              className="rounded-xl border border-cyan-400/30 bg-cyan-400/10 px-4 py-2 text-sm font-bold text-cyan-200 transition hover:bg-cyan-400/15 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading
                ? "Refreshing..."
                : "Refresh statistics"}
            </button>

            <span className="text-xs text-slate-500">
              {lastUpdated
                ? `Last refreshed ${lastUpdated}`
                : "Waiting for statistics"}
            </span>
          </div>
        </div>

        {error && (
          <div className="border-b border-red-400/20 bg-red-400/5 px-6 py-4">
            <p className="text-sm font-bold text-red-300">
              Statistics unavailable
            </p>

            <p className="mt-1 text-sm text-red-200/80">
              {error}
            </p>
          </div>
        )}

        {qualified ? (
          <div className="grid gap-4 p-6 sm:grid-cols-2 xl:grid-cols-4">
            <MetricCard
              label="Conversations"
              value={
                formatNumber(
                  qualified
                    .conversation_count
                )
              }
              detail="Qualified Chat conversation records."
            />

            <MetricCard
              label="Total messages"
              value={
                formatNumber(
                  qualified
                    .total_message_count
                )
              }
              detail="User and assistant messages combined."
            />

            <MetricCard
              label="User messages"
              value={
                formatNumber(
                  qualified
                    .user_message_count
                )
              }
            />

            <MetricCard
              label="Assistant messages"
              value={
                formatNumber(
                  qualified
                    .assistant_message_count
                )
              }
            />

            <MetricCard
              label="Tool evidence"
              value={
                formatNumber(
                  qualified
                    .tool_evidence_count
                )
              }
              detail="Recorded evidence-producing tool activity."
            />

            <MetricCard
              label="Tool successes"
              value={
                formatNumber(
                  qualified
                    .tool_evidence_success_count
                )
              }
            />

            <MetricCard
              label="Tool success rate"
              value={
                successRate
                  ? `${successRate}%`
                  : "Unavailable"
              }
              detail="Calculated from qualified evidence records."
            />

            <MetricCard
              label="Data source"
              value={
                statistics
                  ?.source ??
                "Unavailable"
              }
              detail={
                statistics
                  ? `${statistics.scope} scope`
                  : undefined
              }
            />
          </div>
        ) : (
          <div className="p-6">
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 text-sm text-slate-400">
              {loading
                ? "Loading qualified Chat statistics..."
                : "No qualified statistics are currently available."}
            </div>
          </div>
        )}
      </section>


      {qualified && (
        <>
          <section className="grid gap-6 xl:grid-cols-2">
            <DistributionCard
              title="Intent Distribution"
              subtitle="Qualified activity"
              rows={
                qualified
                  .intent_distribution
                  .map(
                    (
                      row
                    ) => ({
                      label:
                        row.intent,

                      count:
                        row.count,
                    })
                  )
              }
            />

            <DistributionCard
              title="Tool Distribution"
              subtitle="Evidence runtime"
              rows={
                qualified
                  .tool_distribution
                  .map(
                    (
                      row
                    ) => ({
                      label:
                        row.tool,

                      count:
                        row.count,
                    })
                  )
              }
            />

            <DistributionCard
              title="Tool Status"
              subtitle="Evidence outcomes"
              rows={
                qualified
                  .tool_status_distribution
                  .map(
                    (
                      row
                    ) => ({
                      label:
                        row.status,

                      count:
                        row.count,
                    })
                  )
              }
            />

            <DistributionCard
              title="Provider Distribution"
              subtitle="Internal routing"
              rows={
                qualified
                  .provider_distribution_internal
                  .map(
                    (
                      row
                    ) => ({
                      label:
                        row.value,

                      count:
                        row.count,
                    })
                  )
              }
            />
          </section>


          <section className="grid gap-6 xl:grid-cols-2">
            <DistributionCard
              title="Model Distribution"
              subtitle="Internal models"
              rows={
                qualified
                  .model_distribution_internal
                  .map(
                    (
                      row
                    ) => ({
                      label:
                        row.value,

                      count:
                        row.count,
                    })
                  )
              }
            />

            <section className="rounded-3xl border border-slate-800 bg-slate-950/70 p-5">
              <p className="text-xs font-black uppercase tracking-[0.22em] text-amber-300">
                Qualification boundary
              </p>

              <h3 className="mt-2 text-xl font-black text-white">
                Not Yet Qualified
              </h3>

              <p className="mt-2 text-sm leading-6 text-slate-400">
                These metrics are
                intentionally not
                represented as
                authoritative until
                their collection
                contracts are
                qualified.
              </p>

              <div className="mt-5 space-y-3">
                {(
                  statistics
                    ?.not_yet_qualified ??
                  []
                ).map(
                  (
                    item
                  ) => (
                    <div
                      key={
                        item
                      }
                      className="rounded-2xl border border-amber-400/15 bg-amber-400/5 p-4"
                    >
                      <p className="break-words text-sm font-bold text-amber-200">
                        {humanize(
                          item
                        )}
                      </p>
                    </div>
                  )
                )}

                {(
                  statistics
                    ?.not_yet_qualified
                    ?.length ??
                  0
                ) ===
                  0 && (
                  <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4 text-sm text-slate-400">
                    No pending
                    qualification
                    metrics reported.
                  </div>
                )}
              </div>
            </section>
          </section>


          <section className="rounded-3xl border border-slate-800 bg-slate-950/70 p-5">
            <div className="flex flex-wrap items-start justify-between gap-5">
              <div>
                <p className="text-xs font-black uppercase tracking-[0.22em] text-emerald-300">
                  Safety contract
                </p>

                <h3 className="mt-2 text-xl font-black text-white">
                  Statistics Boundary
                </h3>

                <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
                  This workspace reads
                  qualified statistics
                  only. It does not
                  provide Chat input,
                  training controls,
                  portfolio mutation,
                  broker execution, or
                  live execution.
                </p>
              </div>

              <div className="flex flex-wrap gap-2">
                <span className="rounded-full border border-emerald-400/20 bg-emerald-400/5 px-3 py-1.5 text-xs font-bold text-emerald-300">
                  Database mutation:{" "}
                  {statistics
                    ?.database_mutation
                    ? "enabled"
                    : "none"}
                </span>

                <span className="rounded-full border border-emerald-400/20 bg-emerald-400/5 px-3 py-1.5 text-xs font-bold text-emerald-300">
                  Broker execution:{" "}
                  {statistics
                    ?.broker_execution
                    ? "enabled"
                    : "disabled"}
                </span>

                <span className="rounded-full border border-emerald-400/20 bg-emerald-400/5 px-3 py-1.5 text-xs font-bold text-emerald-300">
                  Live execution:{" "}
                  {statistics
                    ?.live_execution
                    ? "enabled"
                    : "disabled"}
                </span>
              </div>
            
      <section className="mt-6 space-y-3">
        <div>
          <h3 className="text-sm font-semibold">
            Learned Strategy Knowledge
          </h3>
          <p className="text-xs text-muted-foreground">
            Latest persisted learned strategy records from the read-only
            Developer Chat statistics endpoint.
          </p>
        </div>

        {statistics?.qualified_statistics?.learned_strategy_knowledge?.length ? (
          <div className="space-y-2">
            {statistics.qualified_statistics.learned_strategy_knowledge.map(
              (strategy) => (
                <div
                  key={strategy.id}
                  className="rounded-md border p-3 text-sm"
                >
                  <div className="font-medium">
                    {strategy.strategy_name}
                  </div>

                  <div className="mt-1 text-xs text-muted-foreground">
                    {strategy.strategy_id}
                    {" · v"}
                    {strategy.strategy_version}
                    {" · "}
                    {strategy.lifecycle_state}
                  </div>

                  <div className="mt-2 grid gap-1 text-xs sm:grid-cols-2">
                    <div>
                      Validation:{" "}
                      {strategy.validation_status ?? "unclassified"}
                    </div>

                    <div>
                      Admission:{" "}
                      {strategy.admission_decision ?? "none"}
                    </div>

                    <div>
                      Promotion:{" "}
                      {strategy.promotion_status ?? "none"}
                    </div>

                    <div>
                      Source:{" "}
                      {strategy.generation_source ?? "unknown"}
                    </div>

                    <div>
                      History rows:{" "}
                      {strategy.history_row_count ?? "unknown"}
                    </div>

                    <div>
                      Features:{" "}
                      {strategy.feature_count ?? "unknown"}
                    </div>
                  </div>

                  {strategy.symbols?.length ? (
                    <div className="mt-2 text-xs text-muted-foreground">
                      Symbols: {strategy.symbols.join(", ")}
                    </div>
                  ) : null}
                </div>
              ),
            )}
          </div>
        ) : (
          <div className="rounded-md border border-dashed p-3 text-sm text-muted-foreground">
            No learned StrategyKnowledge records are currently persisted.
          </div>
        )}
      </section>

</div>
          </section>
        </>
      )}
    </section>
  );
}
