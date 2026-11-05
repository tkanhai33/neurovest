"use client";

import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  fetchNewsIntelligence,
  type NewsIntelligenceItem,
} from "../../../services/newsIntelligenceService";

import {
  getEnabledStrategyNames,
} from "../../../services/strategyLibraryService";

import {
  StatusBadge,
} from "../../../components/ui";



type UserSessionProfile = {
  display_name?: string | null;
  displayName?: string | null;
  full_name?: string | null;
  fullName?: string | null;
  name?: string | null;
  username?: string | null;
  email?: string | null;
  role?: string | null;
  subscription_tier?: string | null;
  account_status?: string | null;
  is_active?: boolean | null;
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



type NeuroWelcomeBriefingProps = {
  session?: UserSessionProfile | null;

  externalPositions?: ExternalPortfolioPosition[];

  externalBalances?: ExternalBalancePayload;
};



const SESSION_DISMISSAL_KEY =
  "neurovest_neuro_briefing_session_dismissed";

const PERMANENT_DISMISSAL_KEY =
  "neurovest_neuro_briefing_do_not_show";



function cleanName(
  value: unknown,
): string | null {

  if (
    typeof value
    !==
    "string"
  ) {
    return null;
  }

  const cleaned =
    value.trim();

  return cleaned
    ? cleaned
    : null;
}



function emailPrefix(
  email: unknown,
): string | null {

  const normalized =
    cleanName(
      email,
    );

  if (!normalized) {
    return null;
  }

  const prefix =
    normalized
      .split(
        "@",
      )[0]
      ?.trim();

  return prefix || null;
}



function formatDisplayName(
  value: string,
): string {

  return value
    .replace(
      /[._-]+/g,
      " ",
    )
    .replace(
      /\b\w/g,
      (character) =>
        character.toUpperCase(),
    );
}



function greetingForHour(
  hour: number,
): string {

  if (hour < 12) {
    return "Good morning";
  }

  if (hour < 18) {
    return "Good afternoon";
  }

  return "Good evening";
}



function parseAmount(
  value:
    string
    |
    number
    |
    null
    |
    undefined,
): number {

  if (
    value === null
    ||
    value === undefined
  ) {
    return 0;
  }

  const numeric =
    Number(
      String(
        value,
      ).replace(
        /[^0-9.+-]/g,
        "",
      ),
    );

  return Number.isFinite(
    numeric,
  )
    ? numeric
    : 0;
}



function formatMoney(
  value:
    string
    |
    number
    |
    null
    |
    undefined,
): string {

  return new Intl.NumberFormat(
    "en-CA",
    {
      style:
        "currency",

      currency:
        "CAD",

      maximumFractionDigits:
        2,
    },
  ).format(
    parseAmount(
      value,
    ),
  );
}



function formatQuantity(
  value:
    string
    |
    number
    |
    null
    |
    undefined,
): string {

  return new Intl.NumberFormat(
    "en-CA",
    {
      maximumFractionDigits:
        4,
    },
  ).format(
    parseAmount(
      value,
    ),
  );
}



function formatTimestamp(
  value:
    string
    |
    null
    |
    undefined,
): string {

  if (!value) {
    return "Recently";
  }

  const date =
    new Date(
      value,
    );

  if (
    Number.isNaN(
      date.getTime(),
    )
  ) {
    return "Recently";
  }

  return new Intl.DateTimeFormat(
    "en-CA",
    {
      month:
        "short",

      day:
        "numeric",

      hour:
        "numeric",

      minute:
        "2-digit",
    },
  ).format(
    date,
  );
}



function newsTimestamp(
  item: NewsIntelligenceItem,
): number {

  const candidate =
    item.published_at
    ??
    item.created_at;

  const time =
    new Date(
      candidate,
    ).getTime();

  return Number.isFinite(
    time,
  )
    ? time
    : 0;
}



export default function NeuroWelcomeBriefing({
  session,
  externalPositions = [],
  externalBalances = {},
}: NeuroWelcomeBriefingProps) {

  const [
    enabledStrategyNames,
    setEnabledStrategyNames,
  ] = useState<string[]>([]);

  const [
    portfolioNews,
    setPortfolioNews,
  ] = useState<NewsIntelligenceItem[]>([]);

  const [
    newsLoading,
    setNewsLoading,
  ] = useState(false);

  const [
    newsUnavailable,
    setNewsUnavailable,
  ] = useState(false);

  const [
    open,
    setOpen,
  ] = useState(false);

  const [
    doNotShowAgain,
    setDoNotShowAgain,
  ] = useState(false);

  const [
    initialized,
    setInitialized,
  ] = useState(false);



  const displayName =
    useMemo(
      () => {

        const candidate =
          cleanName(
            session?.display_name,
          )
          ??
          cleanName(
            session?.displayName,
          )
          ??
          cleanName(
            session?.full_name,
          )
          ??
          cleanName(
            session?.fullName,
          )
          ??
          cleanName(
            session?.name,
          )
          ??
          cleanName(
            session?.username,
          )
          ??
          emailPrefix(
            session?.email,
          );

        return candidate
          ? formatDisplayName(
              candidate,
            )
          : "there";
      },
      [
        session,
      ],
    );



  const greeting =
    useMemo(
      () =>
        greetingForHour(
          new Date().getHours(),
        ),
      [],
    );



  const holdingSymbols =
    useMemo(
      () => {

        return Array.from(
          new Set(
            externalPositions
              .map(
                (
                  position,
                ) =>
                  position.symbol
                    ?.trim()
                    .toUpperCase(),
              )
              .filter(
                (
                  symbol,
                ):
                  symbol is string =>
                    Boolean(
                      symbol,
                    ),
              ),
          ),
        );
      },
      [
        externalPositions,
      ],
    );



  const portfolioMarketValue =
    useMemo(
      () =>
        externalPositions.reduce(
          (
            total,
            position,
          ) =>
            total
            +
            parseAmount(
              position.market_value,
            ),
          0,
        ),
      [
        externalPositions,
      ],
    );



  const portfolioUnrealizedGain =
    useMemo(
      () =>
        externalPositions.reduce(
          (
            total,
            position,
          ) =>
            total
            +
            parseAmount(
              position.unrealized_gain,
            ),
          0,
        ),
      [
        externalPositions,
      ],
    );



  const connectedCash =
    parseAmount(
      externalBalances.cash_total,
    );



  const connectedBuyingPower =
    parseAmount(
      externalBalances.buying_power_total,
    );



  const connectedAccountValue =
    connectedCash
    +
    portfolioMarketValue;



  const lastSyncedAt =
    useMemo(
      () => {

        const candidates =
          [
            ...externalPositions.map(
              (
                position,
              ) =>
                position.last_synced_at,
            ),

            ...(
              externalBalances.balances
              ??
              []
            ).map(
              (
                balance,
              ) =>
                balance.last_synced_at,
            ),
          ]
            .filter(
              (
                value,
              ):
                value is string =>
                  Boolean(
                    value,
                  ),
            )
            .map(
              (
                value,
              ) => ({
                value,
                time:
                  new Date(
                    value,
                  ).getTime(),
              }),
            )
            .filter(
              (
                entry,
              ) =>
                Number.isFinite(
                  entry.time,
                ),
            )
            .sort(
              (
                left,
                right,
              ) =>
                right.time
                -
                left.time,
            );

        return candidates[0]
          ?.value
          ??
          null;
      },
      [
        externalPositions,
        externalBalances,
      ],
    );



  useEffect(() => {

    let cancelled =
      false;

    void getEnabledStrategyNames()
      .then(
        (
          names,
        ) => {

          if (!cancelled) {
            setEnabledStrategyNames(
              names,
            );
          }
        },
      )
      .catch(
        () => {

          if (!cancelled) {
            setEnabledStrategyNames(
              [],
            );
          }
        },
      );

    return () => {
      cancelled = true;
    };
  }, []);



  useEffect(() => {

    if (
      holdingSymbols.length
      ===
      0
    ) {
      queueMicrotask(() => {
        setPortfolioNews([]);
        setNewsLoading(false);
        setNewsUnavailable(false);
      });

      return;
    }

    const controller =
      new AbortController();

    let cancelled =
      false;

    queueMicrotask(() => {
      if (!cancelled) {
        setNewsLoading(true);
        setNewsUnavailable(false);
      }
    });



    const symbolsToLoad =
      holdingSymbols.slice(
        0,
        8,
      );



    void Promise.allSettled(
      symbolsToLoad.map(
        (
          symbol,
        ) =>
          fetchNewsIntelligence(
            {
              symbol,
              limit:
                3,

              signal:
                controller.signal,
            },
          ),
      ),
    )
      .then(
        (
          results,
        ) => {

          if (cancelled) {
            return;
          }

          const fulfilled =
            results.filter(
              (
                result,
              ):
                result is PromiseFulfilledResult<
                  Awaited<
                    ReturnType<
                      typeof fetchNewsIntelligence
                    >
                  >
                > =>
                  result.status
                  ===
                  "fulfilled",
            );

          const items =
            fulfilled.flatMap(
              (
                result,
              ) =>
                Array.isArray(
                  result.value.items,
                )
                  ? result.value.items
                  : [],
            );

          const permittedSymbols =
            new Set(
              holdingSymbols,
            );

          const deduplicated =
            new Map<
              string,
              NewsIntelligenceItem
            >();



          for (
            const item
            of items
          ) {

            const symbol =
              item.symbol
                ?.trim()
                .toUpperCase()
              ??
              "";

            if (
              !symbol
              ||
              !permittedSymbols.has(
                symbol,
              )
            ) {
              continue;
            }

            const key =
              [
                symbol,
                item.headline,
                item.source_url
                ??
                item.id,
              ].join(
                "::",
              );

            if (
              !deduplicated.has(
                key,
              )
            ) {
              deduplicated.set(
                key,
                item,
              );
            }
          }



          const sorted =
            Array.from(
              deduplicated.values(),
            )
              .sort(
                (
                  left,
                  right,
                ) =>
                  newsTimestamp(
                    right,
                  )
                  -
                  newsTimestamp(
                    left,
                  ),
              )
              .slice(
                0,
                6,
              );

          setPortfolioNews(
            sorted,
          );

          setNewsUnavailable(
            fulfilled.length
            ===
            0,
          );

          setNewsLoading(
            false,
          );
        },
      )
      .catch(
        () => {

          if (
            !cancelled
            &&
            !controller.signal.aborted
          ) {
            setPortfolioNews(
              [],
            );

            setNewsUnavailable(
              true,
            );

            setNewsLoading(
              false,
            );
          }
        },
      );



    return () => {

      cancelled =
        true;

      controller.abort();
    };
  }, [
    holdingSymbols,
  ]);



  useEffect(() => {

    const initialize =
      window.setTimeout(
        () => {

          const permanentlyDismissed =
            window.localStorage.getItem(
              PERMANENT_DISMISSAL_KEY,
            )
            ===
            "true";

          const dismissedThisSession =
            window.sessionStorage.getItem(
              SESSION_DISMISSAL_KEY,
            )
            ===
            "true";

          setDoNotShowAgain(
            permanentlyDismissed,
          );

          setOpen(
            !permanentlyDismissed
            &&
            !dismissedThisSession,
          );

          setInitialized(
            true,
          );
        },
        0,
      );

    return () => {

      window.clearTimeout(
        initialize,
      );
    };
  }, []);



  function closeBriefing(): void {

    window.sessionStorage.setItem(
      SESSION_DISMISSAL_KEY,
      "true",
    );

    if (doNotShowAgain) {

      window.localStorage.setItem(
        PERMANENT_DISMISSAL_KEY,
        "true",
      );

    } else {

      window.localStorage.removeItem(
        PERMANENT_DISMISSAL_KEY,
      );
    }

    setOpen(
      false,
    );
  }



  function reopenBriefing(): void {

    setOpen(
      true,
    );
  }



  if (!initialized) {
    return null;
  }



  const connected =
    externalPositions.length
    >
    0
    ||
    Number(
      externalBalances.balance_count
      ??
      0
    )
    >
    0;



  return (
    <>
      <button
        type="button"
        onClick={reopenBriefing}
        className="fixed bottom-5 left-5 z-40 flex items-center gap-2 rounded-full border border-cyan-300/20 bg-slate-950/90 px-4 py-3 text-[11px] font-black uppercase tracking-[0.13em] text-cyan-100 shadow-[0_18px_60px_rgba(0,0,0,0.48)] backdrop-blur-xl transition hover:-translate-y-0.5 hover:border-cyan-300/40 hover:text-white"
      >
        <span className="h-1.5 w-1.5 rounded-full bg-cyan-300 shadow-[0_0_12px_rgba(103,232,249,0.8)]" />
        Neuro briefing
      </button>



      {open && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="neuro-briefing-title"
          data-testid="neuro-welcome-briefing"
          className="fixed inset-0 z-[100] flex items-center justify-center bg-[#020713]/90 p-3 backdrop-blur-xl sm:p-5"
          onMouseDown={
            (
              event,
            ) => {

              if (
                event.target
                ===
                event.currentTarget
              ) {
                closeBriefing();
              }
            }
          }
        >
          <section
            data-neuro-briefing-strategy-authority="shared-strategy-library"
            data-neuro-briefing-portfolio-authority="snaptrade-external-positions"
            data-neuro-briefing-news-authority="real-portfolio-symbols-only"
            data-neuro-briefing-enabled-strategy-count={enabledStrategyNames.length}
            className="relative max-h-[94vh] w-full max-w-6xl overflow-y-auto rounded-[28px] border border-white/[0.09] bg-[#050b16] shadow-[0_35px_160px_rgba(0,0,0,0.82)]"
          >
            <button
              type="button"
              aria-label="Close Neuro briefing"
              onClick={closeBriefing}
              className="absolute right-4 top-4 z-30 flex h-10 w-10 items-center justify-center rounded-full border border-white/[0.1] bg-[#050b16]/90 text-xl font-black text-slate-400 backdrop-blur transition hover:border-cyan-300/30 hover:text-white"
            >
              ×
            </button>



            <div className="grid lg:grid-cols-[0.72fr_1.28fr]">

              <aside className="relative min-h-[300px] overflow-hidden border-b border-white/[0.07] lg:min-h-[760px] lg:border-b-0 lg:border-r">
                <div
                  aria-hidden="true"
                  className="absolute inset-0 bg-[radial-gradient(circle_at_50%_30%,rgba(34,211,238,0.17),transparent_36%),radial-gradient(circle_at_70%_65%,rgba(168,85,247,0.13),transparent_40%),linear-gradient(180deg,#07111e,#030814)]"
                />

                <div
                  aria-hidden="true"
                  className="absolute inset-0 opacity-[0.17] [background-image:linear-gradient(rgba(103,232,249,0.12)_1px,transparent_1px),linear-gradient(90deg,rgba(103,232,249,0.12)_1px,transparent_1px)] [background-size:42px_42px]"
                />

                <img
                  src="/images/neuro/neuro-hero.png"
                  alt="Neuro robotic wolf guardian"
                  width={960}
                  height={760}
                  className="absolute inset-0 h-full w-full object-contain object-center p-4 sm:p-7 lg:p-8"
                />



                <div className="absolute left-5 top-5">
                  <p className="text-[9px] font-black uppercase tracking-[0.2em] text-cyan-200/75">
                    Neuro intelligence
                  </p>

                  <p className="mt-1 text-xs font-semibold text-slate-400">
                    Account briefing
                  </p>
                </div>



                <div className="absolute bottom-5 left-5 right-5 rounded-2xl border border-white/[0.08] bg-slate-950/70 p-4 backdrop-blur-xl">
                  <div className="flex flex-wrap gap-2">
                    <StatusBadge
                      tone={
                        connected
                          ? "success"
                          : "warning"
                      }
                    >
                      {connected
                        ? "Brokerage connected"
                        : "Brokerage not synced"}
                    </StatusBadge>

                    <StatusBadge tone="violet">
                      Read only
                    </StatusBadge>

                    <StatusBadge tone="warning">
                      Paper execution
                    </StatusBadge>
                  </div>

                  <p className="mt-4 text-xs leading-6 text-slate-400">
                    Connected brokerage data is used for portfolio
                    intelligence only. Execution remains inside
                    NeuroVest&apos;s controlled paper workflow.
                  </p>
                </div>
              </aside>



              <main className="p-6 sm:p-8 lg:p-10">

                <div className="border-b border-white/[0.07] pb-7">
                  <p className="text-[10px] font-black uppercase tracking-[0.2em] text-cyan-300">
                    Your account briefing
                  </p>

                  <h2
                    id="neuro-briefing-title"
                    className="mt-3 text-3xl font-black tracking-[-0.045em] text-white sm:text-4xl"
                  >
                    {greeting},{" "}
                    <span className="bg-gradient-to-r from-cyan-300 to-fuchsia-400 bg-clip-text text-transparent">
                      {displayName}.
                    </span>
                  </h2>

                  <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-2 text-xs text-slate-500">
                    <span>
                      Connected portfolio intelligence
                    </span>

                    <span aria-hidden="true">
                      •
                    </span>

                    <span>
                      {holdingSymbols.length}{" "}
                      {holdingSymbols.length === 1
                        ? "holding"
                        : "holdings"}
                    </span>

                    {lastSyncedAt && (
                      <>
                        <span aria-hidden="true">
                          •
                        </span>

                        <span>
                          Synced {formatTimestamp(lastSyncedAt)}
                        </span>
                      </>
                    )}
                  </div>
                </div>



                <section className="mt-7">
                  <div className="flex items-end justify-between gap-4">
                    <div>
                      <p className="text-[10px] font-black uppercase tracking-[0.16em] text-slate-500">
                        Connected account
                      </p>

                      <h3 className="mt-2 text-lg font-black text-white">
                        Portfolio snapshot
                      </h3>
                    </div>

                    <span className="rounded-full border border-emerald-300/15 bg-emerald-300/[0.05] px-3 py-1.5 text-[9px] font-black uppercase tracking-[0.12em] text-emerald-200">
                      Read only
                    </span>
                  </div>



                  <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">

                    <div className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-4">
                      <p className="text-[9px] font-black uppercase tracking-[0.14em] text-slate-500">
                        Account value
                      </p>

                      <p className="mt-2 text-xl font-black tracking-tight text-white">
                        {formatMoney(
                          connectedAccountValue,
                        )}
                      </p>

                      <p className="mt-1 text-[10px] text-slate-500">
                        {connectedCash < 0
                          ? "Holdings less margin used"
                          : "Holdings + connected cash"}
                      </p>
                    </div>



                    <div className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-4">
                      <p className="text-[9px] font-black uppercase tracking-[0.14em] text-slate-500">
                        Market value
                      </p>

                      <p className="mt-2 text-xl font-black tracking-tight text-white">
                        {formatMoney(
                          portfolioMarketValue,
                        )}
                      </p>

                      <p className="mt-1 text-[10px] text-slate-500">
                        Connected holdings
                      </p>
                    </div>



                    <div className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-4">
                      <p className="text-[9px] font-black uppercase tracking-[0.14em] text-slate-500">
                        {connectedCash < 0
                          ? "Margin used"
                          : "Connected cash"}
                      </p>

                      <p className="mt-2 text-xl font-black tracking-tight text-white">
                        {formatMoney(
                          connectedCash < 0
                            ? Math.abs(connectedCash)
                            : connectedCash,
                        )}
                      </p>

                      <p className="mt-1 text-[10px] text-slate-500">
                        {connectedCash < 0
                          ? "Borrowed against connected holdings"
                          : "Cash reported by connected brokerage"}
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
                            portfolioUnrealizedGain > 0
                              ? "text-emerald-300"
                              : portfolioUnrealizedGain < 0
                                ? "text-rose-300"
                                : "text-white",
                          ].join(
                            " ",
                          )
                        }
                      >
                        {formatMoney(
                          portfolioUnrealizedGain,
                        )}
                      </p>

                      <p className="mt-1 text-[10px] text-slate-500">
                        Across connected holdings
                      </p>
                    </div>
                  </div>



                  {connectedBuyingPower > 0 && (
                    <p className="mt-3 text-[11px] text-slate-500">
                      Reported buying power:{" "}
                      <span className="font-bold text-slate-300">
                        {formatMoney(
                          connectedBuyingPower,
                        )}
                      </span>
                    </p>
                  )}
                </section>



                <section className="mt-8 border-t border-white/[0.07] pt-7">
                  <div className="flex items-end justify-between gap-4">
                    <div>
                      <p className="text-[10px] font-black uppercase tracking-[0.16em] text-slate-500">
                        Actual portfolio
                      </p>

                      <h3 className="mt-2 text-lg font-black text-white">
                        Holdings in focus
                      </h3>
                    </div>

                    <span className="text-[10px] font-semibold text-slate-500">
                      SnapTrade snapshot
                    </span>
                  </div>



                  {externalPositions.length === 0 ? (
                    <div className="mt-4 rounded-2xl border border-dashed border-white/[0.1] bg-white/[0.015] p-5">
                      <p className="text-sm font-bold text-slate-300">
                        No connected holdings are available yet.
                      </p>

                      <p className="mt-2 text-xs leading-6 text-slate-500">
                        Connect or synchronize a supported brokerage
                        account to give Neuro real portfolio context.
                      </p>
                    </div>
                  ) : (
                    <div className="mt-4 grid gap-2 sm:grid-cols-2">
                      {externalPositions
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
                                  {formatQuantity(
                                    position.shares_quantity,
                                  )}{" "}
                                  shares
                                  {position.currency
                                    ? ` · ${position.currency}`
                                    : ""}
                                </p>
                              </div>

                              <div className="text-right">
                                <p className="text-sm font-bold text-slate-200">
                                  {formatMoney(
                                    position.market_value,
                                  )}
                                </p>

                                {position.current_price && (
                                  <p className="mt-1 text-[10px] text-slate-500">
                                    {formatMoney(
                                      position.current_price,
                                    )} / share
                                  </p>
                                )}
                              </div>
                            </div>
                          ),
                        )}
                    </div>
                  )}



                  {externalPositions.length > 6 && (
                    <p className="mt-3 text-[10px] text-slate-500">
                      +{externalPositions.length - 6} additional connected holdings
                    </p>
                  )}
                </section>



                <section
                  data-testid="neuro-portfolio-news"
                  data-news-symbol-authority="externalPositions"
                  className="mt-8 border-t border-white/[0.07] pt-7"
                >
                  <div className="flex items-end justify-between gap-4">
                    <div>
                      <p className="text-[10px] font-black uppercase tracking-[0.16em] text-cyan-300/80">
                        Portfolio news
                      </p>

                      <h3 className="mt-2 text-lg font-black text-white">
                        What may matter to your holdings
                      </h3>
                    </div>

                    <span className="text-[10px] text-slate-500">
                      Real holdings only
                    </span>
                  </div>



                  {holdingSymbols.length === 0 ? (
                    <div className="mt-4 rounded-2xl border border-white/[0.07] bg-white/[0.02] p-5">
                      <p className="text-sm font-bold text-slate-300">
                        Portfolio news will appear after your brokerage holdings are available.
                      </p>

                      <p className="mt-2 text-xs leading-6 text-slate-500">
                        Paper positions are intentionally excluded from
                        this news briefing.
                      </p>
                    </div>
                  ) : newsLoading ? (
                    <div className="mt-4 grid gap-2">
                      {[0, 1, 2].map(
                        (
                          item,
                        ) => (
                          <div
                            key={item}
                            className="h-[76px] animate-pulse rounded-xl border border-white/[0.06] bg-white/[0.025]"
                          />
                        ),
                      )}
                    </div>
                  ) : newsUnavailable ? (
                    <div className="mt-4 rounded-2xl border border-amber-300/10 bg-amber-300/[0.025] p-5">
                      <p className="text-sm font-bold text-slate-300">
                        Portfolio news is temporarily unavailable.
                      </p>

                      <p className="mt-2 text-xs leading-6 text-slate-500">
                        Your connected holdings remain available; only
                        the news feed could not be loaded.
                      </p>
                    </div>
                  ) : portfolioNews.length === 0 ? (
                    <div className="mt-4 rounded-2xl border border-white/[0.07] bg-white/[0.02] px-4 py-4">
                      <div className="flex items-start gap-3">
                        <div
                          aria-hidden="true"
                          className="mt-0.5 grid h-8 w-8 shrink-0 place-items-center rounded-xl border border-cyan-300/10 bg-cyan-300/[0.04] text-cyan-300/80"
                        >
                          <span className="text-sm">
                            ✓
                          </span>
                        </div>

                        <div className="min-w-0 flex-1">
                          <p className="text-sm font-bold text-slate-200">
                            No portfolio-relevant headlines right now.
                          </p>

                          <p className="mt-1 text-[11px] leading-5 text-slate-500">
                            Neuro is watching your connected holdings and will
                            surface relevant updates here.
                          </p>

                          {holdingSymbols.length > 0 && (
                            <div className="mt-3 flex flex-wrap items-center gap-2">
                              <span className="text-[9px] font-black uppercase tracking-[0.14em] text-slate-600">
                                Watching
                              </span>

                              {holdingSymbols.slice(0, 6).map(
                                (
                                  symbol,
                                ) => (
                                  <span
                                    key={symbol}
                                    className="rounded-full border border-cyan-300/10 bg-cyan-300/[0.035] px-2.5 py-1 text-[9px] font-bold text-slate-400"
                                  >
                                    {symbol}
                                  </span>
                                ),
                              )}

                              {holdingSymbols.length > 6 && (
                                <span className="text-[9px] font-semibold text-slate-600">
                                  +{holdingSymbols.length - 6} more
                                </span>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="mt-4 grid gap-2">
                      {portfolioNews.map(
                        (
                          item,
                        ) => {

                          const content = (
                            <>
                              <div className="flex items-start justify-between gap-4">
                                <div className="min-w-0">
                                  <div className="flex flex-wrap items-center gap-2">
                                    {item.symbol && (
                                      <span className="rounded-md border border-cyan-300/15 bg-cyan-300/[0.05] px-2 py-1 text-[8px] font-black uppercase tracking-[0.1em] text-cyan-200">
                                        {item.symbol}
                                      </span>
                                    )}

                                    <span className="text-[9px] font-semibold text-slate-500">
                                      {item.source_name
                                        ??
                                        "Market news"}
                                    </span>

                                    <span className="text-[9px] text-slate-600">
                                      {formatTimestamp(
                                        item.published_at
                                        ??
                                        item.created_at,
                                      )}
                                    </span>
                                  </div>

                                  <h4 className="mt-2 text-sm font-bold leading-5 text-slate-100">
                                    {item.headline}
                                  </h4>

                                  {item.summary && (
                                    <p className="mt-1 line-clamp-2 text-[11px] leading-5 text-slate-500">
                                      {item.summary}
                                    </p>
                                  )}
                                </div>

                                {item.source_url && (
                                  <span
                                    aria-hidden="true"
                                    className="mt-1 text-xs text-cyan-300/60"
                                  >
                                    ↗
                                  </span>
                                )}
                              </div>
                            </>
                          );



                          if (item.source_url) {
                            return (
                              <a
                                key={
                                  [
                                    item.id,
                                    item.symbol,
                                    item.headline,
                                  ].join(
                                    "::",
                                  )
                                }
                                href={item.source_url}
                                target="_blank"
                                rel="noreferrer"
                                className="block rounded-xl border border-white/[0.07] bg-white/[0.02] p-4 transition hover:border-cyan-300/20 hover:bg-cyan-300/[0.025]"
                              >
                                {content}
                              </a>
                            );
                          }



                          return (
                            <article
                              key={
                                [
                                  item.id,
                                  item.symbol,
                                  item.headline,
                                ].join(
                                  "::",
                                )
                              }
                              className="rounded-xl border border-white/[0.07] bg-white/[0.02] p-4"
                            >
                              {content}
                            </article>
                          );
                        },
                      )}
                    </div>
                  )}
                </section>



                <section className="mt-8 grid gap-3 border-t border-white/[0.07] pt-7 sm:grid-cols-3">

                  <div className="rounded-2xl border border-white/[0.07] bg-white/[0.018] p-4">
                    <p className="text-[9px] font-black uppercase tracking-[0.14em] text-slate-500">
                      Strategies enabled
                    </p>

                    <p className="mt-2 text-lg font-black text-white">
                      {enabledStrategyNames.length}
                    </p>

                    <p className="mt-1 text-[10px] leading-5 text-slate-500">
                      Shared Strategy Library authority
                    </p>
                  </div>



                  <div className="rounded-2xl border border-white/[0.07] bg-white/[0.018] p-4">
                    <p className="text-[9px] font-black uppercase tracking-[0.14em] text-slate-500">
                      Execution
                    </p>

                    <p className="mt-2 text-lg font-black text-cyan-200">
                      Paper only
                    </p>

                    <p className="mt-1 text-[10px] leading-5 text-slate-500">
                      No live brokerage order authority
                    </p>
                  </div>



                  <div className="rounded-2xl border border-white/[0.07] bg-white/[0.018] p-4">
                    <p className="text-[9px] font-black uppercase tracking-[0.14em] text-slate-500">
                      Account scope
                    </p>

                    <p className="mt-2 text-lg font-black text-emerald-200">
                      Protected
                    </p>

                    <p className="mt-1 text-[10px] leading-5 text-slate-500">
                      Authenticated and owner scoped
                    </p>
                  </div>
                </section>



                <div className="mt-7 flex flex-col gap-4 border-t border-white/[0.07] pt-6 sm:flex-row sm:items-center sm:justify-between">

                  <label className="flex cursor-pointer items-start gap-3">
                    <input
                      type="checkbox"
                      checked={doNotShowAgain}
                      onChange={
                        (
                          event,
                        ) => {
                          setDoNotShowAgain(
                            event.target.checked,
                          );
                        }
                      }
                      className="mt-0.5 h-4 w-4 accent-cyan-400"
                    />

                    <span className="max-w-md text-[11px] leading-5 text-slate-500">
                      Don&apos;t show this briefing automatically again.
                      You can reopen it from the workspace.
                    </span>
                  </label>



                  <button
                    type="button"
                    onClick={closeBriefing}
                    className="nv-button nv-button-primary nv-button-lg shrink-0"
                  >
                    Enter workspace
                  </button>
                </div>

              </main>
            </div>
          </section>
        </div>
      )}
    </>
  );
}
