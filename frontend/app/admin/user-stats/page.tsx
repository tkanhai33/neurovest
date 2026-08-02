"use client";

import {
  useCallback,
  useEffect,
  useState,
} from "react";

import PageHeader from "../../../components/app-shell/PageHeader";

type StatisticsMap = Record<
  string,
  number
>;

type AdminUserStatistics = {
  status: string;
  generated_at: string;
  source: string;
  users: {
    registered: number;
    active: number;
    inactive: number;
    password_reset_required: number;
    registered_last_24_hours: number;
    registered_last_7_days: number;
    with_active_sessions: number;
    with_positions: number;
    by_role: StatisticsMap;
    by_subscription_tier: StatisticsMap;
    by_status: StatisticsMap;
  };
  sessions: {
    active: number;
    total: number;
  };
  paper_trading: {
    orders: number;
    executed_orders: number;
    risk_blocked_orders: number;
    positions: number;
    active_positions: number;
  };
  brokerage: {
    registered_users: number;
    live_execution_enabled: boolean;
  };
  billing: {
    configured: boolean;
    monthly_revenue: number | null;
    display_value: string;
    reason: string;
  };
  boundaries: {
    paper_and_simulation_only: boolean;
    live_broker_trading: boolean;
    production_wide_launch: boolean;
  };
};

type MetricCardProps = {
  label: string;
  value: string | number;
  detail: string;
};

function MetricCard({
  label,
  value,
  detail,
}: MetricCardProps) {
  return (
    <article className="rounded-2xl border border-white/10 bg-slate-950/75 p-5 shadow-xl shadow-black/10">
      <p className="text-[11px] font-black uppercase tracking-[0.18em] text-slate-500">
        {label}
      </p>

      <p className="mt-3 text-3xl font-black text-white">
        {value}
      </p>

      <p className="mt-2 text-sm leading-6 text-slate-400">
        {detail}
      </p>
    </article>
  );
}

function DistributionPanel({
  title,
  values,
}: {
  title: string;
  values: StatisticsMap;
}) {
  const rows = Object.entries(values);

  return (
    <section className="rounded-2xl border border-white/10 bg-slate-950/75 p-6">
      <h2 className="text-lg font-black text-white">
        {title}
      </h2>

      <div className="mt-5 space-y-3">
        {rows.length > 0 ? (
          rows.map(([label, value]) => (
            <div
              key={label}
              className="flex items-center justify-between rounded-xl border border-white/5 bg-black/20 px-4 py-3"
            >
              <span className="text-sm font-bold capitalize text-slate-300">
                {label.replaceAll("_", " ")}
              </span>

              <span className="text-lg font-black text-cyan-200">
                {value}
              </span>
            </div>
          ))
        ) : (
          <p className="text-sm text-slate-500">
            No records available.
          </p>
        )}
      </div>
    </section>
  );
}

export default function AdminUserStatsPage() {
  const [
    statistics,
    setStatistics,
  ] = useState<AdminUserStatistics | null>(
    null,
  );

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    error,
    setError,
  ] = useState<string | null>(
    null,
  );

  const loadStatistics = useCallback(
    async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch(
          "/api/admin/user-stats",
          {
            method: "GET",
            cache: "no-store",
            credentials: "same-origin",
          },
        );

        const payload: unknown =
          await response
            .json()
            .catch(() => null);

        if (!response.ok) {
          const message =
            payload &&
            typeof payload === "object" &&
            "detail" in payload
              ? String(
                  (
                    payload as {
                      detail?: unknown;
                    }
                  ).detail,
                )
              : (
                  "Unable to load administrative statistics"
                );

          throw new Error(message);
        }

        setStatistics(
          payload as AdminUserStatistics,
        );
      } catch (loadError) {
        setError(
          loadError instanceof Error
            ? loadError.message
            : String(loadError),
        );
      } finally {
        setLoading(false);
      }
    },
    [],
  );

  useEffect(() => {
    void loadStatistics();
  }, [loadStatistics]);

  return (
    <main className="space-y-6">
      <PageHeader
        eyebrow="NeuroVest Administration"
        title="User statistics"
        description="Server-authoritative account, session, paper-trading, portfolio, and brokerage registration totals."
        actions={
          <button
            type="button"
            onClick={() => {
              void loadStatistics();
            }}
            disabled={loading}
            className="rounded-xl border border-cyan-300/20 bg-cyan-300/10 px-4 py-3 text-xs font-black uppercase tracking-[0.14em] text-cyan-100 transition hover:border-cyan-300/40 disabled:cursor-wait disabled:opacity-50"
          >
            {loading
              ? "Refreshing…"
              : "Refresh statistics"}
          </button>
        }
      />

      {error ? (
        <section className="rounded-2xl border border-red-400/25 bg-red-950/25 p-5">
          <p className="font-black text-red-200">
            Statistics unavailable
          </p>

          <p className="mt-2 text-sm text-red-100/70">
            {error}
          </p>
        </section>
      ) : null}

      {loading && !statistics ? (
        <section className="rounded-2xl border border-white/10 bg-slate-950/75 p-8 text-sm text-slate-400">
          Loading server-authoritative statistics…
        </section>
      ) : null}

      {statistics ? (
        <>
          <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <MetricCard
              label="Registered users"
              value={statistics.users.registered}
              detail="Canonical identities in identity_users"
            />

            <MetricCard
              label="Active users"
              value={statistics.users.active}
              detail="Enabled accounts with active status"
            />

            <MetricCard
              label="Inactive users"
              value={statistics.users.inactive}
              detail="Disabled or non-active accounts"
            />

            <MetricCard
              label="Password reset"
              value={
                statistics.users
                  .password_reset_required
              }
              detail="Accounts requiring a password change"
            />

            <MetricCard
              label="Active sessions"
              value={statistics.sessions.active}
              detail={`${statistics.sessions.total} total refresh sessions`}
            />

            <MetricCard
              label="Users online-capable"
              value={
                statistics.users
                  .with_active_sessions
              }
              detail="Distinct users with an unexpired, non-revoked session"
            />

            <MetricCard
              label="New users — 24 hours"
              value={
                statistics.users
                  .registered_last_24_hours
              }
              detail="Accounts created during the previous 24 hours"
            />

            <MetricCard
              label="New users — 7 days"
              value={
                statistics.users
                  .registered_last_7_days
              }
              detail="Accounts created during the previous seven days"
            />
          </section>

          <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <MetricCard
              label="Paper orders"
              value={
                statistics.paper_trading.orders
              }
              detail={`${statistics.paper_trading.executed_orders} executed`}
            />

            <MetricCard
              label="Risk-blocked orders"
              value={
                statistics.paper_trading
                  .risk_blocked_orders
              }
              detail="Orders stopped by the paper risk boundary"
            />

            <MetricCard
              label="Active positions"
              value={
                statistics.paper_trading
                  .active_positions
              }
              detail={`${statistics.paper_trading.positions} total inventory rows`}
            />

            <MetricCard
              label="Users with positions"
              value={
                statistics.users.with_positions
              }
              detail="Distinct owners with positive paper exposure"
            />

            <MetricCard
              label="Broker registered"
              value={
                statistics.brokerage
                  .registered_users
              }
              detail="Distinct users with stored SnapTrade registration"
            />

            <MetricCard
              label="Monthly revenue"
              value={
                statistics.billing.configured &&
                statistics.billing
                  .monthly_revenue !== null
                  ? (
                      `$${statistics.billing.monthly_revenue.toFixed(2)}`
                    )
                  : statistics.billing
                      .display_value
              }
              detail={statistics.billing.reason}
            />

            <MetricCard
              label="Execution boundary"
              value={
                statistics.boundaries
                  .paper_and_simulation_only
                  ? "Paper only"
                  : "Unverified"
              }
              detail="Live broker execution remains disabled"
            />

            <MetricCard
              label="Data source"
              value="PostgreSQL"
              detail="Server-authoritative database calculations"
            />
          </section>

          <section className="grid gap-6 lg:grid-cols-3">
            <DistributionPanel
              title="Users by subscription tier"
              values={
                statistics.users
                  .by_subscription_tier
              }
            />

            <DistributionPanel
              title="Users by role"
              values={
                statistics.users.by_role
              }
            />

            <DistributionPanel
              title="Users by account status"
              values={
                statistics.users.by_status
              }
            />
          </section>

          <section className="rounded-2xl border border-white/10 bg-slate-950/75 p-6">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <p className="text-xs font-black uppercase tracking-[0.16em] text-emerald-300">
                  Statistics connected
                </p>

                <p className="mt-2 text-sm text-slate-400">
                  Generated{" "}
                  {new Date(
                    statistics.generated_at,
                  ).toLocaleString()}
                </p>
              </div>

              <div className="rounded-full border border-emerald-300/20 bg-emerald-300/10 px-4 py-2 text-xs font-black uppercase tracking-[0.14em] text-emerald-200">
                Live execution disabled
              </div>
            </div>
          </section>
        </>
      ) : null}
    </main>
  );
}
