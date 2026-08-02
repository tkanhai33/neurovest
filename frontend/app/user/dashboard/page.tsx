"use client";

import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  useRouter,
} from "next/navigation";

import FloatingChatWidget from "../../components/chat/FloatingChatWidget";
import MarketTickerBanner from "../../components/ticker/MarketTickerBanner";
import PaperOrderPanel from "../components/PaperOrderPanel";
import RecentOrderActivity from "../components/RecentOrderActivity";
import NeuroWelcomeBriefing from "../components/NeuroWelcomeBriefing";

import {
  Panel,
  StatCard,
  StatusBadge,
  StatusMessage,
} from "../../../components/ui";

type SessionPayload = {
  authenticated?: boolean;
  user_id?: string | null;
  role?: string;
  subscription_tier?: string;
  account_status?: string;
  is_active?: boolean;
};

type PortfolioPosition = {
  id: number | string;
  symbol: string;
  shares_quantity: number;
  average_entry_price: number;
  total_cost_basis: number;
  realized_pnl: number;
  last_updated?: string | null;
};

type PositionsPayload = {
  active_exposure_count?: number;
  positions?: PortfolioPosition[];
  error?: string;
};

type OrderRecord = {
  id: number | string;
  symbol: string;
  signal: string;
  status: string;
  timestamp: string;
  shares_quantity?: number | null;
  allocated_capital?: number | null;
  slippage_price?: number | null;
  commission_paid?: number | null;
};

type OrdersPayload = {
  total_records?: number;
  orders?: OrderRecord[];
  error?: string;
};

type AnalyticsPayload = {
  total_trades_logged?: number;
  buy_signals_count?: number;
  sell_signals_count?: number;
  risk_blocked_percentage?: number;
  execution_success_percentage?: number;
  error?: string;
};

type PortfolioValuationPayload = {
  starting_capital?: number;
  current_cash_balance?: number;
  total_fees_paid?: number;
  net_liquidation_value?: number;
  valuation_basis?: string;
  live_market_marking?: boolean;
  error?: string;
};

type DashboardState = {
  session: SessionPayload | null;
  positions: PortfolioPosition[];
  orders: OrderRecord[];
  analytics: AnalyticsPayload;
  valuation: PortfolioValuationPayload;
  activeExposureCount: number;
  totalOrderRecords: number;
};

const EMPTY_STATE: DashboardState = {
  session: null,
  positions: [],
  orders: [],
  analytics: {},
  valuation: {},
  activeExposureCount: 0,
  totalOrderRecords: 0,
};

function formatMoney(
  value: number | null | undefined,
): string {
  const safeValue =
    Number.isFinite(Number(value))
      ? Number(value)
      : 0;

  return new Intl.NumberFormat(
    "en-CA",
    {
      style: "currency",
      currency: "CAD",
      maximumFractionDigits: 2,
    },
  ).format(safeValue);
}

function formatNumber(
  value: number | null | undefined,
  maximumFractionDigits = 4,
): string {
  const safeValue =
    Number.isFinite(Number(value))
      ? Number(value)
      : 0;

  return new Intl.NumberFormat(
    "en-CA",
    {
      maximumFractionDigits,
    },
  ).format(safeValue);
}

function formatDate(
  value: string | null | undefined,
): string {
  if (!value) {
    return "Unavailable";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat(
    "en-CA",
    {
      dateStyle: "medium",
      timeStyle: "short",
    },
  ).format(date);
}

async function readJson<T>(
  response: Response,
  fallback: T,
): Promise<T> {
  try {
    return await response.json() as T;
  } catch {
    return fallback;
  }
}

export default function UserDashboardPage() {
  const router = useRouter();

  const [dashboard, setDashboard] =
    useState<DashboardState>(
      EMPTY_STATE,
    );

  const [loading, setLoading] =
    useState(true);

  const [refreshing, setRefreshing] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  const loadDashboard =
    useCallback(
      async (
        refresh = false,
      ): Promise<void> => {
        if (refresh) {
          setRefreshing(true);
        } else {
          setLoading(true);
        }

        setError(null);

        try {
          const [
            sessionResponse,
            positionsResponse,
            ordersResponse,
            analyticsResponse,
            valuationResponse,
          ] = await Promise.all([
            fetch(
              "/api/auth/session",
              {
                method: "GET",
                credentials: "include",
                cache: "no-store",
              },
            ),
            fetch(
              "/api/v1/positions",
              {
                method: "GET",
                credentials: "include",
                cache: "no-store",
              },
            ),
            fetch(
              "/api/v1/orders",
              {
                method: "GET",
                credentials: "include",
                cache: "no-store",
              },
            ),
            fetch(
              "/api/v1/analytics",
              {
                method: "GET",
                credentials: "include",
                cache: "no-store",
              },
            ),
            fetch(
              "/api/v1/portfolio/valuation",
              {
                method: "GET",
                credentials: "include",
                cache: "no-store",
              },
            ),
          ]);

          if (
            sessionResponse.status === 401
          ) {
            router.replace(
              "/login?next=/user/dashboard",
            );
            return;
          }

          if (!sessionResponse.ok) {
            throw new Error(
              "Your account session could not be loaded.",
            );
          }

          const session =
            await readJson<SessionPayload>(
              sessionResponse,
              {},
            );

          if (
            session.authenticated === false
          ) {
            router.replace(
              "/login?next=/user/dashboard",
            );
            return;
          }

          if (
            positionsResponse.status === 401 ||
            ordersResponse.status === 401 ||
            analyticsResponse.status === 401 ||
            valuationResponse.status === 401
          ) {
            router.replace(
              "/login?next=/user/dashboard",
            );
            return;
          }

          const positionsPayload =
            await readJson<PositionsPayload>(
              positionsResponse,
              {
                positions: [],
              },
            );

          const ordersPayload =
            await readJson<OrdersPayload>(
              ordersResponse,
              {
                orders: [],
              },
            );

          const analyticsPayload =
            await readJson<AnalyticsPayload>(
              analyticsResponse,
              {},
            );

          const valuationPayload =
            await readJson<PortfolioValuationPayload>(
              valuationResponse,
              {},
            );

          const failedSections: string[] = [];

          if (!positionsResponse.ok) {
            failedSections.push(
              "positions",
            );
          }

          if (!ordersResponse.ok) {
            failedSections.push(
              "orders",
            );
          }

          if (!analyticsResponse.ok) {
            failedSections.push(
              "analytics",
            );
          }

          if (!valuationResponse.ok) {
            failedSections.push(
              "portfolio valuation",
            );
          }

          setDashboard({
            session,
            positions:
              Array.isArray(
                positionsPayload.positions,
              )
                ? positionsPayload.positions
                : [],
            orders:
              Array.isArray(
                ordersPayload.orders,
              )
                ? ordersPayload.orders
                : [],
            analytics:
              analyticsPayload,
            valuation:
              valuationPayload,
            activeExposureCount:
              Number(
                positionsPayload
                  .active_exposure_count ??
                0,
              ),
            totalOrderRecords:
              Number(
                ordersPayload
                  .total_records ??
                0,
              ),
          });

          if (
            failedSections.length > 0
          ) {
            setError(
              `Some account data could not be loaded: ${failedSections.join(
                ", ",
              )}.`,
            );
          }
        } catch (caught) {
          setError(
            caught instanceof Error
              ? caught.message
              : "The dashboard could not be loaded.",
          );
        } finally {
          setLoading(false);
          setRefreshing(false);
        }
      },
      [
        router,
      ],
    );

  useEffect(() => {
    const initialLoad =
      window.setTimeout(
        () => {
          void loadDashboard();
        },
        0,
      );

    return () => {
      window.clearTimeout(
        initialLoad,
      );
    };
  }, [
    loadDashboard,
  ]);

  const totalCostBasis =
    useMemo(
      () =>
        dashboard.positions.reduce(
          (
            total,
            position,
          ) =>
            total +
            Number(
              position.total_cost_basis ??
              0,
            ),
          0,
        ),
      [
        dashboard.positions,
      ],
    );

  const availableCash =
    Number(
      dashboard.valuation
        .current_cash_balance ??
      0,
    );

  const startingCapital =
    Number(
      dashboard.valuation
        .starting_capital ??
      0,
    );

  const totalFeesPaid =
    Number(
      dashboard.valuation
        .total_fees_paid ??
      0,
    );

  const accountValueAtCost =
    availableCash +
    totalCostBasis;

  const capitalUtilization =
    startingCapital > 0
      ? (
          totalCostBasis /
          startingCapital
        ) * 100
      : 0;

  const totalRealizedPnl =
    useMemo(
      () =>
        dashboard.positions.reduce(
          (
            total,
            position,
          ) =>
            total +
            Number(
              position.realized_pnl ??
              0,
            ),
          0,
        ),
      [
        dashboard.positions,
      ],
    );

  const recentOrders =
    dashboard.orders.slice(
      0,
      8,
    );

  return (
    <main className="space-y-5">
      <NeuroWelcomeBriefing
        session={dashboard.session}
      />

      <section className="relative overflow-hidden rounded-[2rem] border border-cyan-300/15 bg-slate-950/80 shadow-[0_24px_100px_rgba(0,0,0,0.42)]">
        <div
          aria-hidden="true"
          className="absolute inset-0 bg-[linear-gradient(90deg,rgba(2,6,23,0.98)_0%,rgba(2,6,23,0.93)_42%,rgba(2,6,23,0.42)_72%,rgba(2,6,23,0.18)_100%)]"
        />

        <div
          aria-hidden="true"
          className="absolute inset-y-0 right-0 w-[64%] bg-[url('/images/neuro/neuro-hero.png')] bg-contain bg-right bg-no-repeat opacity-75"
        />

        <div
          aria-hidden="true"
          className="absolute inset-0 bg-[radial-gradient(circle_at_78%_20%,rgba(168,85,247,0.18),transparent_34%),radial-gradient(circle_at_55%_80%,rgba(34,211,238,0.11),transparent_35%)]"
        />

        <div className="relative z-10 min-h-[310px] p-7 sm:p-10">
          <div className="max-w-3xl">
            <p className="nv-eyebrow">
              Welcome back
            </p>

            <h1 className="mt-4 text-4xl font-black tracking-[-0.045em] text-white sm:text-5xl xl:text-6xl">
              Your market{" "}
              <span className="bg-gradient-to-r from-cyan-300 to-fuchsia-400 bg-clip-text text-transparent">
                workspace.
              </span>
            </h1>

            <p className="mt-5 max-w-2xl text-base leading-8 text-slate-300 sm:text-lg">
              Review your simulated portfolio, account-scoped activity,
              analytics, and market intelligence from one protected workspace.
            </p>

            <div className="mt-6 flex flex-wrap items-center gap-3">
              <StatusBadge tone="success">
                Simulation mode active
              </StatusBadge>

              <StatusBadge tone="violet">
                {dashboard.session
                  ?.subscription_tier ??
                  "free"}{" "}
                tier
              </StatusBadge>

              <span className="text-sm font-semibold text-slate-400">
                Live execution is disabled
              </span>
            </div>

            <div className="mt-7">
              <button
                type="button"
                onClick={() => {
                  void loadDashboard(true);
                }}
                disabled={
                  loading ||
                  refreshing
                }
                className="nv-button nv-button-secondary"
              >
                {refreshing
                  ? "Refreshing account…"
                  : "Refresh account data"}
              </button>
            </div>
          </div>
        </div>
      </section>

      <MarketTickerBanner />

      {loading && (
        <StatusMessage tone="info">
          Loading your protected account data…
        </StatusMessage>
      )}

      {error && (
        <StatusMessage tone="danger">
          {error}
        </StatusMessage>
      )}

      <PaperOrderPanel
        onOrderProcessed={async () => {
          await loadDashboard(true);
        }}
      />

      <section
        aria-label="Account summary"
        className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4"
      >
        <StatCard
          label="Open exposures"
          value={String(
            dashboard.activeExposureCount,
          )}
          detail="Positions with a positive share quantity"
        />

        <StatCard
          label="Available cash"
          value={formatMoney(
            availableCash,
          )}
          detail="Owner-scoped cash reconstructed from the order ledger"
        />

        <StatCard
          label="Orders logged"
          value={String(
            dashboard.totalOrderRecords,
          )}
          detail="Authenticated order-history records"
        />

        <StatCard
          label="Execution success"
          value={`${formatNumber(
            dashboard.analytics
              .execution_success_percentage,
            2,
          )}%`}
          detail="Executed orders as a share of logged activity"
        />
      </section>

      <RecentOrderActivity
        orders={dashboard.orders}
      />

      <Panel
        variant="default"
        className="overflow-hidden"
      >
        <div className="flex flex-wrap items-start justify-between gap-4 border-b border-white/[0.07] p-6">
          <div>
            <p className="nv-eyebrow">
              Portfolio valuation
            </p>

            <h2 className="mt-3 text-2xl font-black text-white">
              Capital and account value
            </h2>

            <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-400">
              Cash is reconstructed from this account&apos;s authenticated
              order ledger. Open positions are currently valued at cost basis
              until qualified live market marking is added.
            </p>
          </div>

          <StatusBadge tone="info">
            Ledger + cost basis
          </StatusBadge>
        </div>

        <div
          data-testid="user-portfolio-valuation"
          className="grid gap-4 p-6 sm:grid-cols-2 xl:grid-cols-5"
        >
          <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
            <p className="nv-stat-label">
              Starting capital
            </p>

            <p className="mt-3 text-xl font-black text-white">
              {formatMoney(
                startingCapital,
              )}
            </p>
          </div>

          <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
            <p className="nv-stat-label">
              Available cash
            </p>

            <p className="mt-3 text-xl font-black text-cyan-200">
              {formatMoney(
                availableCash,
              )}
            </p>
          </div>

          <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
            <p className="nv-stat-label">
              Deployed at cost
            </p>

            <p className="mt-3 text-xl font-black text-white">
              {formatMoney(
                totalCostBasis,
              )}
            </p>
          </div>

          <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
            <p className="nv-stat-label">
              Account value at cost
            </p>

            <p className="mt-3 text-xl font-black text-emerald-200">
              {formatMoney(
                accountValueAtCost,
              )}
            </p>
          </div>

          <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
            <p className="nv-stat-label">
              Fees paid
            </p>

            <p className="mt-3 text-xl font-black text-amber-200">
              {formatMoney(
                totalFeesPaid,
              )}
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center justify-between gap-4 border-t border-white/[0.07] px-6 py-5">
          <div className="flex flex-wrap gap-2">
            <StatusBadge tone="violet">
              Account scoped
            </StatusBadge>

            <StatusBadge tone="success">
              Cash ledger active
            </StatusBadge>

            <StatusBadge tone="warning">
              Live price marking pending
            </StatusBadge>
          </div>

          <p className="text-sm font-semibold text-slate-400">
            Capital utilization:{" "}
            <span className="text-white">
              {formatNumber(
                capitalUtilization,
                2,
              )}
              %
            </span>
          </p>
        </div>
      </Panel>

      <section className="grid gap-5 xl:grid-cols-[1.3fr_0.7fr]">
        <Panel
          variant="elevated"
          className="overflow-hidden"
        >
          <div className="flex flex-wrap items-start justify-between gap-4 border-b border-white/[0.07] p-6">
            <div>
              <p className="nv-eyebrow">
                Your portfolio
              </p>

              <h2 className="mt-3 text-2xl font-black text-white">
                Personal paper positions
              </h2>
            </div>

            <StatusBadge tone="violet">
              Account scoped
            </StatusBadge>
          </div>

          <div
            data-testid="user-positions"
            className="p-6"
          >
            {dashboard.positions.length === 0 ? (
              <StatusMessage tone="info">
                No simulated positions are currently recorded for this account.
              </StatusMessage>
            ) : (
              <div className="space-y-3">
                {dashboard.positions.map(
                  (position) => (
                    <article
                      key={String(
                        position.id ??
                        position.symbol,
                      )}
                      className="rounded-2xl border border-white/[0.08] bg-slate-950/55 p-4"
                    >
                      <div className="flex flex-wrap items-start justify-between gap-4">
                        <div>
                          <p className="text-lg font-black text-white">
                            {position.symbol}
                          </p>

                          <p className="mt-1 text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
                            Updated{" "}
                            {formatDate(
                              position.last_updated,
                            )}
                          </p>
                        </div>

                        <StatusBadge
                          tone={
                            Number(
                              position.realized_pnl,
                            ) >= 0
                              ? "success"
                              : "warning"
                          }
                        >
                          {formatMoney(
                            position.realized_pnl,
                          )}{" "}
                          realized
                        </StatusBadge>
                      </div>

                      <div className="mt-4 grid gap-3 sm:grid-cols-3">
                        <div>
                          <p className="nv-stat-label">
                            Shares
                          </p>
                          <p className="mt-2 font-black text-white">
                            {formatNumber(
                              position.shares_quantity,
                            )}
                          </p>
                        </div>

                        <div>
                          <p className="nv-stat-label">
                            Average entry
                          </p>
                          <p className="mt-2 font-black text-white">
                            {formatMoney(
                              position.average_entry_price,
                            )}
                          </p>
                        </div>

                        <div>
                          <p className="nv-stat-label">
                            Cost basis
                          </p>
                          <p className="mt-2 font-black text-white">
                            {formatMoney(
                              position.total_cost_basis,
                            )}
                          </p>
                        </div>
                      </div>
                    </article>
                  ),
                )}
              </div>
            )}
          </div>
        </Panel>

        <Panel
          variant="default"
          className="p-6"
        >
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="nv-eyebrow">
                Account analytics
              </p>

              <h2 className="mt-3 text-2xl font-black text-white">
                Simulation activity
              </h2>
            </div>

            <StatusBadge tone="info">
              Read only
            </StatusBadge>
          </div>

          <div
            data-testid="user-analytics"
            className="mt-6 space-y-3"
          >
            {[
              [
                "Trades logged",
                dashboard.analytics
                  .total_trades_logged ??
                  0,
              ],
              [
                "Buy signals",
                dashboard.analytics
                  .buy_signals_count ??
                  0,
              ],
              [
                "Sell signals",
                dashboard.analytics
                  .sell_signals_count ??
                  0,
              ],
              [
                "Risk blocked",
                `${
                  dashboard.analytics
                    .risk_blocked_percentage ??
                  0
                }%`,
              ],
              [
                "Execution success",
                `${
                  dashboard.analytics
                    .execution_success_percentage ??
                  0
                }%`,
              ],
            ].map(
              (
                [
                  label,
                  value,
                ],
              ) => (
                <div
                  key={label}
                  className="flex items-center justify-between gap-4 rounded-xl border border-white/[0.07] bg-white/[0.025] px-4 py-3"
                >
                  <span className="text-sm text-slate-400">
                    {label}
                  </span>

                  <strong className="text-sm text-white">
                    {value}
                  </strong>
                </div>
              ),
            )}
          </div>

          <div className="mt-6 border-t border-white/[0.07] pt-5">
            <p className="nv-stat-label">
              Total realized P/L
            </p>

            <p
              className={[
                "mt-2 text-2xl font-black",
                totalRealizedPnl >= 0
                  ? "text-emerald-300"
                  : "text-amber-300",
              ].join(" ")}
            >
              {formatMoney(
                totalRealizedPnl,
              )}
            </p>
          </div>
        </Panel>
      </section>

      <Panel
        variant="default"
        className="overflow-hidden"
      >
        <div className="flex flex-wrap items-start justify-between gap-4 border-b border-white/[0.07] p-6">
          <div>
            <p className="nv-eyebrow">
              Recent activity
            </p>

            <h2 className="mt-3 text-2xl font-black text-white">
              Account order history
            </h2>
          </div>

          <StatusBadge tone="success">
            Owner isolated
          </StatusBadge>
        </div>

        <div
          data-testid="user-orders"
          className="p-6"
        >
          {recentOrders.length === 0 ? (
            <StatusMessage tone="info">
              No simulated orders are currently recorded for this account.
            </StatusMessage>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full text-left">
                <thead>
                  <tr className="border-b border-white/[0.08] text-[10px] font-black uppercase tracking-[0.16em] text-slate-500">
                    <th className="px-3 py-3">
                      Symbol
                    </th>
                    <th className="px-3 py-3">
                      Signal
                    </th>
                    <th className="px-3 py-3">
                      Status
                    </th>
                    <th className="px-3 py-3">
                      Time
                    </th>
                  </tr>
                </thead>

                <tbody>
                  {recentOrders.map(
                    (order) => (
                      <tr
                        key={String(
                          order.id,
                        )}
                        className="border-b border-white/[0.05] text-sm text-slate-300 last:border-0"
                      >
                        <td className="px-3 py-4 font-black text-white">
                          {order.symbol}
                        </td>

                        <td className="px-3 py-4 uppercase">
                          {order.signal}
                        </td>

                        <td className="px-3 py-4">
                          {order.status}
                        </td>

                        <td className="px-3 py-4 text-slate-500">
                          {formatDate(
                            order.timestamp,
                          )}
                        </td>
                      </tr>
                    ),
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </Panel>

      <Panel
        variant="muted"
        className="overflow-hidden"
      >
        <div className="border-b border-white/[0.07] p-6">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="nv-eyebrow">
                Account protection
              </p>

              <h2 className="mt-3 text-xl font-black text-white">
                Authenticated paper-trading account
              </h2>

              <p className="mt-3 max-w-4xl text-sm leading-7 text-slate-400">
                Orders, positions, and analytics are scoped to the currently
                authenticated account. Paper orders pass through NeuroVest
                risk, accounting, execution, and ledger boundaries without
                enabling a live broker.
              </p>
            </div>

            <StatusBadge
              tone={
                dashboard.session?.is_active === false
                  ? "warning"
                  : "success"
              }
            >
              {dashboard.session?.is_active === false
                ? "Account inactive"
                : "Account active"}
            </StatusBadge>
          </div>
        </div>

        <div
          data-testid="user-account-status"
          className="grid gap-4 p-6 sm:grid-cols-2 xl:grid-cols-4"
        >
          <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
            <p className="nv-stat-label">
              Role
            </p>

            <p className="mt-3 text-lg font-black capitalize text-white">
              {dashboard.session?.role ?? "user"}
            </p>
          </div>

          <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
            <p className="nv-stat-label">
              Subscription
            </p>

            <p className="mt-3 text-lg font-black capitalize text-white">
              {dashboard.session?.subscription_tier ?? "free"}
            </p>
          </div>

          <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
            <p className="nv-stat-label">
              Account status
            </p>

            <p className="mt-3 text-lg font-black capitalize text-white">
              {dashboard.session?.account_status ?? "active"}
            </p>
          </div>

          <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
            <p className="nv-stat-label">
              Execution mode
            </p>

            <p className="mt-3 text-lg font-black text-cyan-200">
              Paper only
            </p>
          </div>
        </div>

        <div className="flex flex-wrap gap-2 border-t border-white/[0.07] px-6 py-5">
          <StatusBadge tone="info">
            Session authenticated
          </StatusBadge>

          <StatusBadge tone="violet">
            Owner isolated
          </StatusBadge>

          <StatusBadge tone="warning">
            Live broker disabled
          </StatusBadge>

          <StatusBadge tone="success">
            Paper submission qualified
          </StatusBadge>
        </div>
      </Panel>

      <FloatingChatWidget />
    </main>
  );
}
