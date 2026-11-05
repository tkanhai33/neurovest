"use client";

import {
  fetchSnapTradeBalances,
  fetchSnapTradePortfolio,
  getSnapTradeStatus,
  resolveSnapTradeState,
} from "../../../services/snaptradeService";

import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  useRouter,
} from "next/navigation";

import Link from "next/link";

import MarketWorkspace from "../../components/workspaces/MarketWorkspace";

import UserStrategiesWorkspace from "./UserStrategiesWorkspace";
import DemoJourneyPanel from "./DemoJourneyPanel";
import UserWorkspaceRouter from "./UserWorkspaceRouter";
import type {
  UserWorkspaceId,
} from "./userWorkspaceTypes";

import FloatingChatWidget from "../../components/chat/FloatingChatWidget";
import MarketTickerBanner from "../../components/ticker/MarketTickerBanner";
import LogoutButton from "../../components/auth/LogoutButton";
import PaperOrderPanel from "../components/PaperOrderPanel";
import RecentOrderActivity from "../components/RecentOrderActivity";
import FullPaperHistory from "../components/FullPaperHistory";
import StrategyDecisionPanel from "../components/StrategyDecisionPanel";
import NeuroWelcomeBriefing from "../components/NeuroWelcomeBriefing";

import PageHeader from "../../../components/app-shell/PageHeader";
import WorkspacePage from "../../../components/app-shell/WorkspacePage";

import {
  Panel,
  StatCard,
  StatusBadge,
  StatusMessage,
} from "../../../components/ui";
import BrokerageConnectionBadge from "./BrokerageConnectionBadge";
import { financialTruth } from "./financialTruth";
import PortfolioPerformanceChart from "./components/PortfolioPerformanceChart";
import HoldingsAllocationDonut from "./components/HoldingsAllocationDonut";

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

type ExternalPortfolioPosition = {
  symbol: string;
  instrument_kind?: string | null;
  currency?: string | null;
  shares_quantity: string;
  average_entry_price?: string | null;
  current_price?: string | null;
  market_value?: string | null;
  total_cost_basis?: string | null;
  unrealized_gain?: string | null;
  source_provider?: string;
  read_only?: boolean;
  last_synced_at?: string | null;
};

type ExternalPortfolioPayload = {
  status?: string;
  source_provider?: string;
  scope?: string;
  read_only?: boolean;
  trading_enabled?: boolean;
  order_operations_enabled?: boolean;
  position_count?: number;
  symbols?: string[];
  positions?: ExternalPortfolioPosition[];
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
  net_liquidation_value?: number | null;
  valuation_basis?: string;
  live_market_marking?: boolean;
  error?: string;
};

type ExternalBalancePayload = {
  status?: string;
  source_provider?: string;
  scope?: string;
  read_only?: boolean;
  trading_enabled?: boolean;
  order_operations_enabled?: boolean;
  balance_count?: number;
  cash_total?: string;
  buying_power_total?: string | null;
  balances?: Array<{
    currency?: string;
    cash_amount?: string | null;
    buying_power?: string | null;
    cash_available?: string | null;
    settled_cash?: string | null;
    source_provider?: string;
    read_only?: boolean;
    last_synced_at?: string | null;
  }>;
};

type LearningSummarySymbol = {
  symbol?: string;
  decisions?: Record<string, number>;
  cycles?: number;
  last_close?: number;
  last_timestamp?: string;
  observations?: number;
  average_reward?: number;
  average_confidence?: number;
};

type LearningSummaryPayload = {
  current_run?: {
    run_id?: string;
    status?: string;
    rows?: number;
    reward_total?: number;
    average_confidence?: number;
    decision_counts?: Record<string, number>;
    symbols?: LearningSummarySymbol[];
  } | null;

  lifetime?: {
    runs?: number;
    rows_processed?: number;
    reward_total?: number;
    decision_counts?: Record<string, number>;
  };

  scope?: string;
};

type DashboardState = {
  session: SessionPayload | null;
  positions: PortfolioPosition[];
  externalPositions: ExternalPortfolioPosition[];
  orders: OrderRecord[];
  analytics: AnalyticsPayload;
  valuation: PortfolioValuationPayload;
  externalBalances: ExternalBalancePayload;
  externalPortfolio: ExternalPortfolioPayload;
  learningSummary: LearningSummaryPayload;
  activeExposureCount: number;
  totalOrderRecords: number;
};

const EMPTY_STATE: DashboardState = {
  session: null,
  positions: [],
  externalPositions: [],
  orders: [],
  analytics: {},
  valuation: {},
  externalBalances: {},
  externalPortfolio: {},
  learningSummary: {},
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

  const [ordersUnavailable, setOrdersUnavailable] =
    useState(false);

  const [brokerageConnection, setBrokerageConnection] =
    useState<"connected" | "not_connected" | "unavailable">("unavailable");

  const [
    activeWorkspace,
    setActiveWorkspace,
  ] = useState<UserWorkspaceId>(
    "quick",
  );

  useEffect(
    () => {
      const openRequestedWorkspace = (
        event: Event,
      ): void => {
        const detail =
          (event as CustomEvent<{
            workspace?: unknown;
          }>).detail;

        if (detail?.workspace === "orders") {
          setActiveWorkspace("orders");
        }
      };

      window.addEventListener(
        "neurovest:open-user-workspace-v1",
        openRequestedWorkspace,
      );

      return () => {
        window.removeEventListener(
          "neurovest:open-user-workspace-v1",
          openRequestedWorkspace,
        );
      };
    },
    [],
  );

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
        setOrdersUnavailable(true);
        setBrokerageConnection("unavailable");

        try {
          const [
            sessionResponse,
            positionsResponse,
            externalPortfolioResponse,
            ordersResponse,
            analyticsResponse,
            valuationResponse,
            externalBalancesResponse,
            learningSummaryResponse,
            connectionResult,
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
            fetchSnapTradePortfolio(
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
            fetchSnapTradeBalances(
              {
                method: "GET",
                credentials: "include",
                cache: "no-store",
              },
            ),
            fetch(
              "/api/v1/training/learning-summary",
              {
                method: "GET",
                credentials: "include",
                cache: "no-store",
              },
            ),
            getSnapTradeStatus()
              .then((payload) => {
                const state = resolveSnapTradeState(payload);
                const status = state.connection_status?.toLowerCase();

                if (status === "connected") {
                  return "connected" as const;
                }

                if (
                  status === "not_registered" ||
                  status === "not_connected" ||
                  status === "registered"
                ) {
                  return "not_connected" as const;
                }

                return "unavailable" as const;
              })
              .catch(() => "unavailable" as const),
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
            externalPortfolioResponse.status === 401 ||
            ordersResponse.status === 401 ||
            analyticsResponse.status === 401 ||
            valuationResponse.status === 401 ||
            externalBalancesResponse.status === 401 ||
            learningSummaryResponse.status === 401
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

          const externalPortfolioPayload =
            await readJson<ExternalPortfolioPayload>(
              externalPortfolioResponse,
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

          const externalBalancesPayload =
            await readJson<ExternalBalancePayload>(
              externalBalancesResponse,
              {},
            );

          const learningSummaryPayload =
            await readJson<LearningSummaryPayload>(
              learningSummaryResponse,
              {},
            );

          const orderHistoryFailed =
            !ordersResponse.ok ||
            !Array.isArray(ordersPayload.orders);

          setOrdersUnavailable(orderHistoryFailed);
          setBrokerageConnection(connectionResult);

          const failedSections: string[] = [];

          if (!positionsResponse.ok) {
            failedSections.push(
              "positions",
            );
          }

          if (!externalPortfolioResponse.ok) {
            failedSections.push(
              "SnapTrade portfolio",
            );
          }

          if (orderHistoryFailed) {
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

          if (!externalBalancesResponse.ok) {
            failedSections.push(
              "SnapTrade balances",
            );
          }

          if (!learningSummaryResponse.ok) {
            failedSections.push(
              "learning profile",
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
            externalPositions:
              Array.isArray(
                externalPortfolioPayload.positions,
              )
                ? externalPortfolioPayload.positions
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
            externalBalances:
              externalBalancesResponse.ok
                ? externalBalancesPayload
                : {},
            externalPortfolio:
              externalPortfolioResponse.ok
                ? externalPortfolioPayload
                : {},
            learningSummary:
              learningSummaryPayload,
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
          setOrdersUnavailable(true);
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

  const financial = financialTruth(
    brokerageConnection,
    dashboard.externalBalances,
    dashboard.externalPortfolio,
  );

  const visibleExternalPositions =
    brokerageConnection === "connected" &&
    dashboard.externalPortfolio.status === "ok" &&
    dashboard.externalPortfolio.position_count ===
      dashboard.externalPositions.length
      ? dashboard.externalPositions
      : [];

  const brokerCash = financial.cash;
  const brokerBuyingPower =
    financial.state === "verified" &&
    dashboard.externalBalances.buying_power_total != null &&
    dashboard.externalBalances.buying_power_total.trim() !== "" &&
    Number.isFinite(Number(dashboard.externalBalances.buying_power_total))
      ? Number(dashboard.externalBalances.buying_power_total)
      : null;
  const brokerPositionMarketValue = financial.marketValue;
  const brokerEquityProxy = financial.accountValue;
  const brokerUnrealizedGain = financial.unrealizedGain;

  const formatPositionMoney = (
    value: string | null | undefined,
    currency: string | null | undefined,
  ): string => {
    if (
      value == null ||
      !value.trim() ||
      !currency ||
      !/^[A-Za-z]{3}$/.test(currency)
    ) {
      return "Unavailable";
    }

    const amount = Number(value);

    if (!Number.isFinite(amount)) {
      return "Unavailable";
    }

    try {
      return new Intl.NumberFormat("en-CA", {
        style: "currency",
        currency: currency.toUpperCase(),
        currencyDisplay: "code",
        maximumFractionDigits: 2,
      }).format(amount);
    } catch {
      return "Unavailable";
    }
  };

  const formatBrokerMoney = (amount: number | null): string =>
    amount === null ? "—" : formatMoney(amount);

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
    <WorkspacePage
      testId="user-dashboard"
      className="nv-user-dashboard"
      top={
        <>
          <MarketTickerBanner />
          {error && (
            <div role="alert" className="px-3 pt-3">
              <StatusMessage tone="warning">
                {error}
              </StatusMessage>
            </div>
          )}
        </>
      }
      header={
        <PageHeader
          eyebrow="NeuroVest Investing"
          title="Your portfolio."
          description="Track your holdings, follow markets, manage paper orders, review history, and inspect strategy decisions."
          badge={
            <StatusBadge tone="success">
              Paper account
            </StatusBadge>
          }
          actions={
            <>
              <button
                type="button"
                onClick={() => {
                  void loadDashboard(true);
                }}
                disabled={loading || refreshing}
                className="nv-button nv-button-primary nv-button-lg"
              >
                {refreshing
                  ? "Refreshing…"
                  : "Refresh account"}
              </button>

              <LogoutButton />
            </>
          }
        />
      }
      navigation={
        <div className="rounded-[22px] border border-white/[0.07] bg-[#050b16]/92 p-2 shadow-[0_18px_60px_rgba(0,0,0,0.22)] backdrop-blur-xl">
          <div
            className="flex gap-1.5 overflow-x-auto overscroll-x-contain pb-1"
            role="tablist"
            aria-label="Investing workspace"
          >
            {[
              ["quick", "Quick View"],
              ["markets", "Markets"],
              ["portfolio", "Portfolio"],
              ["orders", "Orders"],
              ["history", "History"],
              ["strategies", "Strategies"],
              ["options", "Account"],
            ].map(
              (
                [
                  workspaceId,
                  label,
                ],
              ) => {
                const selected =
                  activeWorkspace ===
                  workspaceId;

                return (
                  <button
                    key={workspaceId}
                    type="button"
                    role="tab"
                    aria-selected={selected}
                    onClick={(event) => {
                      const tab = event.currentTarget;
                      const strip = tab.parentElement;
                      if (strip) {
                        const left = tab.offsetLeft - strip.offsetLeft;
                        const right = left + tab.offsetWidth;
                        if (left < strip.scrollLeft) {
                          strip.scrollTo({ left, behavior: "smooth" });
                        } else if (right > strip.scrollLeft + strip.clientWidth) {
                          strip.scrollTo({
                            left: right - strip.clientWidth,
                            behavior: "smooth",
                          });
                        }
                      }
                      setActiveWorkspace(
                        workspaceId as UserWorkspaceId,
                      );
                    }}
                    className={
                      [
                        "shrink-0 min-h-11 whitespace-nowrap rounded-xl border px-4 py-2.5 text-xs font-black tracking-[0.02em] transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300",
                        selected
                          ? "border-cyan-300/35 bg-cyan-300/[0.07] text-cyan-100 shadow-[0_0_28px_rgba(34,211,238,0.06)]"
                          : "border-transparent bg-transparent text-slate-500 hover:border-white/[0.08] hover:bg-white/[0.025] hover:text-slate-200",
                      ].join(
                        " ",
                      )
                    }
                  >
                    {label}
                  </button>
                );
              },
            )}
          </div>
        </div>
      }
      primary={
        <UserWorkspaceRouter
          activeWorkspace={activeWorkspace}
          quick={
            <div className="nv-user-quick-view">
              <DemoJourneyPanel
                onOpenWorkspace={(workspace) => {
                  setActiveWorkspace(workspace);
                }}
              />
          <div
            className="
              grid gap-4
              md:grid-cols-[minmax(0,1.7fr)_minmax(280px,0.8fr)]
              md:items-start
            "
          >
            <PortfolioPerformanceChart
              currentAccountValue={brokerEquityProxy}
            />

            <HoldingsAllocationDonut
              positions={visibleExternalPositions}
            />
          </div>

              <section
                aria-label="Brokerage portfolio snapshot"
                data-dashboard-portfolio-authority="snaptrade-external-positions"
                className="rounded-[28px] border border-white/[0.08] bg-[#050b16] p-5 shadow-[0_24px_90px_rgba(0,0,0,0.28)] sm:p-6"
              >
                <div className="flex flex-wrap items-end justify-between gap-4">
                  <div>
                    <p className="text-[10px] font-black uppercase tracking-[0.16em] text-slate-500">
                      Brokerage portfolio
                    </p>

                    <h2 className="mt-2 text-2xl font-black tracking-tight text-white">
                      Portfolio snapshot
                    </h2>

                    <p className="mt-2 text-xs leading-5 text-slate-500">
                      Stored read-only brokerage holdings and balances, shown when the connection and data are available.
                    </p>
                  </div>

                  <StatusBadge tone="success">
                    Read only
                  </StatusBadge>
                </div>



                <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                  <div className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-4">
                    <p className="text-[9px] font-black uppercase tracking-[0.14em] text-slate-500">
                      Account value
                    </p>

                    <p className="mt-2 text-xl font-black tracking-tight text-white">
                      {formatBrokerMoney(
                        brokerEquityProxy,
                      )}
                    </p>

                    <p className="mt-1 text-[10px] leading-5 text-slate-500">
                      {brokerCash !== null && brokerCash < 0
                        ? "Holdings less margin used"
                        : "Holdings plus stored cash"}
                    </p>
                  </div>



                  <div className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-4">
                    <p className="text-[9px] font-black uppercase tracking-[0.14em] text-slate-500">
                      Market value
                    </p>

                    <p className="mt-2 text-xl font-black tracking-tight text-white">
                      {formatBrokerMoney(
                        brokerPositionMarketValue,
                      )}
                    </p>

                    <p className="mt-1 text-[10px] leading-5 text-slate-500">
                      Brokerage holdings
                    </p>
                  </div>



                  <div className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-4">
                    <p className="text-[9px] font-black uppercase tracking-[0.14em] text-slate-500">
                      {brokerCash !== null && brokerCash < 0
                        ? "Margin used"
                        : "Connected cash"}
                    </p>

                    <p className="mt-2 text-xl font-black tracking-tight text-white">
                      {formatBrokerMoney(brokerCash !== null && brokerCash < 0 ? Math.abs(brokerCash) : brokerCash)}
                    </p>

                    <p className="mt-1 text-[10px] leading-5 text-slate-500">
                      {brokerCash !== null && brokerCash < 0
                        ? "Borrowed against connected holdings"
                        : "Cash reported in brokerage inventory"}
                    </p>
                  </div>



                  <div className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-4">
                    <p className="text-[9px] font-black uppercase tracking-[0.14em] text-slate-500">
                      Unrealized
                    </p>

                    <p
                      className={
                        [
                          "mt-2 text-xl font-black tracking-tight",
                          brokerUnrealizedGain !== null && brokerUnrealizedGain > 0
                            ? "text-emerald-300"
                            : brokerUnrealizedGain !== null && brokerUnrealizedGain < 0
                              ? "text-rose-300"
                              : "text-white",
                        ].join(
                          " ",
                        )
                      }
                    >
                      {formatBrokerMoney(
                        brokerUnrealizedGain,
                      )}
                    </p>

                    <p className="mt-1 text-[10px] leading-5 text-slate-500">
                      Across stored brokerage holdings
                    </p>
                  </div>
                </div>



                {brokerBuyingPower !== null && brokerBuyingPower > 0 && (
                  <p className="mt-3 text-[11px] text-slate-500">
                    Reported buying power:{" "}
                    <span className="font-bold text-slate-300">
                      {formatBrokerMoney(
                        brokerBuyingPower,
                      )}
                    </span>
                  </p>
                )}



                <section className="mt-7 border-t border-white/[0.07] pt-6">
                  <div className="flex flex-wrap items-end justify-between gap-4">
                    <div>
                      <p className="text-[10px] font-black uppercase tracking-[0.16em] text-slate-500">
                        Brokerage holdings
                      </p>

                      <h3 className="mt-2 text-lg font-black text-white">
                        Holdings in focus
                      </h3>
                    </div>

                    <span className="text-[10px] font-semibold text-slate-500">
                      Stored SnapTrade inventory
                    </span>
                  </div>



                  {visibleExternalPositions.length === 0 ? (
                    <div className="mt-4 rounded-2xl border border-dashed border-white/[0.1] bg-white/[0.015] p-5">
                      <p className="text-sm font-bold text-slate-300">
                        No brokerage holdings are available to display.
                      </p>

                      <p className="mt-2 text-xs leading-6 text-slate-500">
                        {brokerageConnection === "not_connected"
                          ? "Connect a supported brokerage account to view its read-only holdings."
                          : brokerageConnection === "unavailable"
                            ? "Brokerage connection status could not be verified. Try refreshing the dashboard."
                            : "No verified holdings snapshot is currently available."}
                      </p>
                    </div>
                  ) : (
                    <div className="mt-4 grid gap-2 sm:grid-cols-2">
                      {visibleExternalPositions
                        .slice(
                          0,
                          6,
                        )
                        .map(
                          (
                            position,
                          ) => (
                            <div
                              key={
                                [
                                  position.symbol,
                                  position.source_provider,
                                ].join(
                                  "::",
                                )
                              }
                              className="flex items-center justify-between gap-4 rounded-xl border border-white/[0.07] bg-white/[0.02] px-4 py-3"
                            >
                              <div className="min-w-0">
                                <p className="truncate text-sm font-black text-white">
                                  {position.symbol}
                                </p>

                                <p className="mt-1 text-[10px] text-slate-500">
                                  {formatNumber(
                                    Number(
                                      position.shares_quantity ??
                                      0,
                                    ),
                                    4,
                                  )}{" "}
                                  shares
                                  {position.currency
                                    ? ` · ${position.currency}`
                                    : ""}
                                </p>
                              </div>

                              <div className="text-right">
                                <p className="text-sm font-bold text-slate-200">
                                  {formatPositionMoney(
                                    position.market_value,
                                    position.currency,
                                  )}
                                </p>

                                {position.current_price && (
                                  <p className="mt-1 text-[10px] text-slate-500">
                                    {formatPositionMoney(
                                      position.current_price,
                                      position.currency,
                                    )} / share
                                  </p>
                                )}
                              </div>
                            </div>
                          ),
                        )}
                    </div>
                  )}



                  {visibleExternalPositions.length > 6 && (
                    <p className="mt-3 text-[10px] text-slate-500">
                      +{visibleExternalPositions.length - 6} additional brokerage holdings
                    </p>
                  )}
                </section>
              </section>



              <section className="nv-user-quick-briefing">
                <NeuroWelcomeBriefing
                  session={dashboard.session}
                  externalPositions={
                    visibleExternalPositions
                  }
                  externalBalances={
                    dashboard.externalBalances
                  }
                />
              </section>



              <section
                aria-label="Your learning profile"
                className="nv-user-quick-metrics"
              >
                <div className="nv-user-workspace-heading">
                  <div>
                    <p className="nv-eyebrow">
                      Your learning profile
                    </p>

                    <h2 className="nv-section-title">
                      Personal strategy learning
                    </h2>

                    <p className="nv-section-description">
                      Owner-scoped training history for this account only.
                      System and global training runs are excluded.
                    </p>
                  </div>

                  <StatusBadge tone="info">
                    Profile scoped
                  </StatusBadge>
                </div>

                <section
                  aria-label="Learning profile summary"
                  className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4"
                >
                  <StatCard
                    label="Completed runs"
                    value={String(
                      dashboard.learningSummary
                        .lifetime?.runs ??
                      0,
                    )}
                    detail="Completed training runs across your profile"
                  />

                  <StatCard
                    label="Rows processed"
                    value={formatNumber(
                      dashboard.learningSummary
                        .lifetime?.rows_processed ??
                      0,
                    )}
                    detail="Historical rows processed by your profile"
                  />

                  <StatCard
                    label="Lifetime reward"
                    value={formatNumber(
                      dashboard.learningSummary
                        .lifetime?.reward_total ??
                      0,
                      4,
                    )}
                    detail="Aggregate reward from your completed profile runs"
                  />

                  <StatCard
                    label="Current confidence"
                    value={formatNumber(
                      dashboard.learningSummary
                        .current_run
                        ?.average_confidence ??
                      0,
                      4,
                    )}
                    detail="Average confidence from your latest completed run"
                  />
                </section>

                <div className="mt-4 flex flex-wrap gap-2">
                  <StatusBadge tone="success">
                    {dashboard.learningSummary
                      .current_run?.status ??
                      "No completed run"}
                  </StatusBadge>

                  <StatusBadge tone="violet">
                    {dashboard.learningSummary
                      .current_run?.symbols
                      ?.length ??
                      0} symbols
                  </StatusBadge>

                  <StatusBadge tone="warning">
                    Global training excluded
                  </StatusBadge>
                </div>
              </section>

              
            </div>
          }
          markets={
            <div className="nv-user-role-workspace">
              <div className="nv-user-workspace-heading">
                <div>
                  <p className="nv-eyebrow">
                    Markets
                  </p>

                  <h2 className="nv-section-title">
                    Prices and market intelligence
                  </h2>

                  <p className="nv-section-description">
                    Read-only quotes, watchlists, active symbols, and market context.
                  </p>
                </div>

                <StatusBadge tone="info">
                  Read only
                </StatusBadge>
              </div>

              <MarketWorkspace
                positions={dashboard.positions}
              />
            </div>
          }
          portfolio={
            <div className="nv-user-role-workspace">
              <div className="nv-user-workspace-heading">
                <div>
                  <p className="nv-eyebrow">
                    Portfolio
                  </p>

                  <h2 className="nv-section-title">
                    Holdings and account performance
                  </h2>

                  <p className="nv-section-description">
                    Review available brokerage holdings separately from NeuroVest paper simulation.
                  </p>
                </div>

                <StatusBadge tone="success">
                  Account scoped
                </StatusBadge>
              </div>

              <Panel
                variant="elevated"
                className="overflow-hidden"
              >
                <div className="flex flex-wrap items-start justify-between gap-4 border-b border-white/[0.07] p-6">
                  <div>
                    <p className="nv-eyebrow">
                      Brokerage data
                    </p>

                    <h2 className="mt-3 text-2xl font-black text-white">
                      Brokerage portfolio
                    </h2>

                    <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-400">
                      Read-only positions and balances returned through the existing
                      SnapTrade connection. These values are never combined with
                      NeuroVest paper capital or simulation results.
                    </p>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    <BrokerageConnectionBadge />

                    <StatusBadge tone="info">
                      Read only
                    </StatusBadge>
                  </div>
                </div>

                <div
                  data-testid="connected-portfolio-summary"
                  className="grid gap-4 p-6 sm:grid-cols-2 xl:grid-cols-5"
                >
                  <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
                    <p className="nv-stat-label">
                      Account value
                    </p>

                    <p className="mt-3 text-xl font-black text-white">
                      {formatBrokerMoney(
                        brokerEquityProxy,
                      )}
                    </p>
                  </div>

                  <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
                    <p className="nv-stat-label">
                      Connected cash
                    </p>

                    <p className="mt-3 text-xl font-black text-cyan-200">
                      {formatBrokerMoney(
                        brokerCash,
                      )}
                    </p>
                  </div>

                  <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
                    <p className="nv-stat-label">
                      Holdings market value
                    </p>

                    <p className="mt-3 text-xl font-black text-white">
                      {formatBrokerMoney(
                        brokerPositionMarketValue,
                      )}
                    </p>
                  </div>

                  <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
                    <p className="nv-stat-label">
                      Unrealized gain
                    </p>

                    <p
                      className={[
                        "mt-3 text-xl font-black",
                        brokerUnrealizedGain !== null && brokerUnrealizedGain >= 0
                          ? "text-emerald-300"
                          : "text-amber-300",
                      ].join(" ")}
                    >
                      {formatBrokerMoney(
                        brokerUnrealizedGain,
                      )}
                    </p>
                  </div>

                  <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
                    <p className="nv-stat-label">
                      Buying power
                    </p>

                    <p className="mt-3 text-xl font-black text-violet-200">
                      {formatBrokerMoney(
                        brokerBuyingPower,
                      )}
                    </p>
                  </div>
                </div>

                <div className="border-t border-white/[0.07] p-6">
                  <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <p className="nv-eyebrow">
                        Brokerage holdings
                      </p>

                      <p className="mt-2 text-sm text-slate-400">
                        {visibleExternalPositions.length} stored brokerage{" "}
                        {visibleExternalPositions.length === 1
                          ? "position"
                          : "positions"}
                      </p>
                    </div>

                    <StatusBadge tone="info">
                      SnapTrade inventory source
                    </StatusBadge>
                  </div>

                  {visibleExternalPositions.length === 0 ? (
                    <StatusMessage tone="info">
                      No brokerage positions are available to display.
                    </StatusMessage>
                  ) : (
                    <div
                      data-testid="connected-portfolio-positions"
                      className="grid gap-3 xl:grid-cols-2"
                    >
                      {visibleExternalPositions.map(
                        (
                          position,
                          index,
                        ) => {
                          const positionUnrealized =
                            position.unrealized_gain == null ||
                            !position.unrealized_gain.trim()
                              ? null
                              : Number(position.unrealized_gain);

                          const positionUnrealizedValid =
                            positionUnrealized !== null &&
                            Number.isFinite(positionUnrealized);

                          return (
                            <article
                              key={`${position.symbol}-${index}`}
                              className="min-w-0 rounded-2xl border border-white/[0.08] bg-slate-950/55 p-4"
                            >
                              <div className="flex flex-wrap items-start justify-between gap-4">
                                <div className="min-w-0">
                                  <p className="text-lg font-black text-white">
                                    {position.symbol}
                                  </p>

                                  <p className="mt-1 text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
                                    {position.currency ||
                                      "Currency unavailable"}
                                    {" · "}
                                    {position.instrument_kind ||
                                      "Security type unavailable"}
                                  </p>
                                </div>

                                <StatusBadge
                                  tone={
                                    positionUnrealizedValid &&
                                    positionUnrealized >= 0
                                      ? "success"
                                      : "info"
                                  }
                                >
                                  {positionUnrealizedValid
                                    ? formatPositionMoney(
                                        position.unrealized_gain,
                                        position.currency,
                                      )
                                    : "Unavailable"}{" "}
                                  unrealized
                                </StatusBadge>
                              </div>

                              <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                                <div>
                                  <p className="nv-stat-label">
                                    Shares
                                  </p>

                                  <p className="mt-2 font-black text-white">
                                    {formatNumber(
                                      Number(
                                        position.shares_quantity,
                                      ),
                                    )}
                                  </p>
                                </div>

                                <div>
                                  <p className="nv-stat-label">
                                    Average entry
                                  </p>

                                  <p className="mt-2 font-black text-white">
                                    {formatPositionMoney(
                                          position.average_entry_price,
                                          position.currency,
                                        )}
                                  </p>
                                </div>

                                <div>
                                  <p className="nv-stat-label">
                                    Current price
                                  </p>

                                  <p className="mt-2 font-black text-white">
                                    {formatPositionMoney(
                                          position.current_price,
                                          position.currency,
                                        )}
                                  </p>
                                </div>

                                <div>
                                  <p className="nv-stat-label">
                                    Market value
                                  </p>

                                  <p className="mt-2 font-black text-cyan-200">
                                    {formatPositionMoney(
                                          position.market_value,
                                          position.currency,
                                        )}
                                  </p>
                                </div>
                              </div>

                              <div className="mt-4 flex flex-wrap items-center justify-between gap-3 border-t border-white/[0.05] pt-3 text-[10px] uppercase tracking-[0.12em] text-slate-600">
                                <span>
                                  Provider:{" "}
                                  {position.source_provider ||
                                    "SnapTrade"}
                                </span>

                                <span>
                                  Synced:{" "}
                                  {formatDate(
                                    position.last_synced_at,
                                  )}
                                </span>
                              </div>
                            </article>
                          );
                        },
                      )}
                    </div>
                  )}
                </div>
              </Panel>

              <div className="flex flex-wrap items-end justify-between gap-4 border-t border-white/[0.07] pt-2">
                <div>
                  <p className="nv-eyebrow">
                    Paper simulation
                  </p>

                  <h2 className="mt-2 text-2xl font-black text-white">
                    NeuroVest paper portfolio
                  </h2>

                  <p className="mt-2 text-sm text-slate-400">
                    Simulated capital, positions, executions, and results.
                    Completely separate from any linked brokerage account.
                  </p>
                </div>

                <StatusBadge tone="violet">
                  Simulation only
                </StatusBadge>
              </div>

              <Panel
                                variant="default"
                                className="overflow-hidden"
                              >
                                <div className="flex flex-wrap items-start justify-between gap-4 border-b border-white/[0.07] p-6">
                                  <div>
                                    <p className="nv-eyebrow">
                                      Paper portfolio valuation
                                    </p>

                                    <h2 className="mt-3 text-2xl font-black text-white">
                                      Simulated capital and account value
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
                                        Paper holdings
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
            </div>
          }
          orders={
            <div className="nv-user-role-workspace">
              <div className="nv-user-workspace-heading">
                <div>
                  <p className="nv-eyebrow">
                    Orders
                  </p>

                  <h2 className="nv-section-title">
                    Paper order entry
                  </h2>

                  <p className="nv-section-description">
                    Choose a symbol and direction. NeuroVest&apos;s risk-gated paper pipeline
                    determines the simulated allocation, execution price, and filled quantity.
                  </p>
                </div>

                <StatusBadge tone="warning">
                  Simulation only
                </StatusBadge>
              </div>

              <div className="space-y-6">
                <PaperOrderPanel
                  onOrderProcessed={async () => {
                    await loadDashboard(true);
                  }}
                />

                <RecentOrderActivity
                  orders={recentOrders}
                  unavailable={ordersUnavailable}
                />
              </div>
            </div>
          }
          history={
            <div className="nv-user-role-workspace">
              <div className="nv-user-workspace-heading">
                <div>
                  <p className="nv-eyebrow">
                    History
                  </p>

                  <h2 className="nv-section-title">
                    Connected performance and paper records
                  </h2>

                  <p className="nv-section-description">
                    Review recorded brokerage account-value history separately from
                    NeuroVest&apos;s owner-scoped paper execution ledger.
                  </p>
                </div>

                <StatusBadge tone="info">
                  Read only
                </StatusBadge>
              </div>

              <section
                data-testid="connected-performance-history"
                className="space-y-4"
              >
                <div className="flex flex-wrap items-end justify-between gap-4">
                  <div>
                    <p className="nv-eyebrow">
                      Brokerage history
                    </p>

                    <h2 className="mt-2 text-2xl font-black text-white">
                      Brokerage account value history
                    </h2>

                    <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
                      Real owner-scoped SnapTrade portfolio-value observations.
                      Account value is recorded as holdings market value plus cash.
                      No connected trades or transactions are represented here.
                    </p>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    <StatusBadge tone="info">
                      SnapTrade history source
                    </StatusBadge>

                    <StatusBadge tone="info">
                      Read only
                    </StatusBadge>
                  </div>
                </div>

                <PortfolioPerformanceChart
                currentAccountValue={brokerEquityProxy}
                />
              </section>

              <section
                data-testid="paper-order-history"
                className="space-y-4 border-t border-white/[0.07] pt-6"
              >
                <div className="flex flex-wrap items-end justify-between gap-4">
                  <div>
                    <p className="nv-eyebrow">
                      Paper simulation
                    </p>

                    <h2 className="mt-2 text-2xl font-black text-white">
                      Paper execution history
                    </h2>

                    <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
                      Detailed simulated quantities, execution prices, allocated
                      capital, fees, status, and timestamps from this
                      authenticated owner&apos;s paper ledger.
                    </p>
                  </div>

                  <StatusBadge tone="violet">
                    Simulation only
                  </StatusBadge>
                </div>

                <FullPaperHistory
                  orders={dashboard.orders}
                  unavailable={ordersUnavailable}
                  totalRecords={dashboard.totalOrderRecords}
                />
              </section>
            </div>
          }
          strategies={
            <div className="nv-user-role-workspace">
              <div className="nv-user-workspace-heading">
                <div>
                  <p className="nv-eyebrow">
                    Strategies
                  </p>

                  <h2 className="nv-section-title">
                    Strategy decisions and signals
                  </h2>

                  <p className="nv-section-description">
                    Inspect current read-only decisions, confidence, and strategy provider output.
                  </p>
                </div>

                <StatusBadge tone="info">
                  Read only
                </StatusBadge>
              </div>

              <StrategyDecisionPanel />

              <UserStrategiesWorkspace
                orders={dashboard.orders}
              />
            </div>
          }
          options={
            <div className="nv-user-role-workspace">
              <div className="nv-user-workspace-heading">
                <div>
                  <p className="nv-eyebrow">
                    Account
                  </p>

                  <h2 className="nv-section-title">
                    Account settings and protection
                  </h2>

                  <p className="nv-section-description">
                    Review account scope, subscription, security, notifications, and preferences.
                  </p>
                </div>

                <Link
                  href="/user/settings"
                  className="nv-button nv-button-primary"
                >
                  Open settings
                </Link>
              </div>

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
                                          dashboard.session?.is_active === true
                                             ? "success"
                                             : "warning"
                                        }
                                      >
                                        {dashboard.session?.is_active === true
                                           ? "Account active"
                                           : dashboard.session?.is_active === false
                                             ? "Account inactive"
                                             : "Account state unavailable"}
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
                                        {dashboard.session?.role ?? "Unavailable"}
                                      </p>
                                    </div>

                                    <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
                                      <p className="nv-stat-label">
                                        Subscription
                                      </p>

                                      <p className="mt-3 text-lg font-black capitalize text-white">
                                        {dashboard.session?.subscription_tier ?? "Unavailable"}
                                      </p>
                                    </div>

                                    <div className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4">
                                      <p className="nv-stat-label">
                                        Account status
                                      </p>

                                      <p className="mt-3 text-lg font-black capitalize text-white">
                                        {dashboard.session?.account_status ?? "Unavailable"}
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
            </div>
          }
        />
      }
      footer={
        <div className="nv-workspace-policy-line">
          <span>
            Personal investing workspace
          </span>

          <span>
            Owner scoped · Paper trading · Read-only market data · No live execution
          </span>
        </div>
      }
      floating={
        <FloatingChatWidget />
      }
    />
  );
}
