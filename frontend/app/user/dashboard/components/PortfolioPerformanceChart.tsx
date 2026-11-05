"use client";

import {
  useEffect,
  useMemo,
  useState,
} from "react";


type Period =
  | "1D"
  | "1W"
  | "1M"
  | "3M"
  | "1Y"
  | "ALL";


type HistoryPoint = {
  observed_at: string;
  market_value: string;
  cash: string;
  account_value: string;
  unrealized_gain: string | null;
  source_provider: string;
  read_only: boolean;
};


type HistoryResponse = {
  status?: string;
  point_count?: number;
  points?: HistoryPoint[];
};


type Props = {
  currentAccountValue:
    number
    | null
    | undefined;
};


type ParsedPoint = {
  observedAt: Date;
  timestamp: number;
  accountValue: number;
  marketValue: number | null;
  cash: number | null;
  unrealizedGain: number | null;
};


type Coordinate = ParsedPoint & {
  x: number;
  y: number;
};


const periods: Period[] = [
  "1D",
  "1W",
  "1M",
  "3M",
  "1Y",
  "ALL",
];


const periodMs: Record<
  Exclude<Period, "ALL">,
  number
> = {
  "1D":
    24 * 60 * 60 * 1000,

  "1W":
    7 * 24 * 60 * 60 * 1000,

  "1M":
    30 * 24 * 60 * 60 * 1000,

  "3M":
    90 * 24 * 60 * 60 * 1000,

  "1Y":
    365 * 24 * 60 * 60 * 1000,
};


function finiteNumber(
  value:
    string
    | number
    | null
    | undefined,
): number | null {

  if (
    value === null
    ||
    value === undefined
    ||
    value === ""
  ) {
    return null;
  }

  const parsed = Number(
    value,
  );

  return Number.isFinite(
    parsed,
  )
    ? parsed
    : null;
}


function money(
  value:
    number
    | null
    | undefined,
): string {

  if (
    value === null
    ||
    value === undefined
    ||
    !Number.isFinite(value)
  ) {
    return "—";
  }

  return new Intl.NumberFormat(
    "en-CA",
    {
      style: "currency",
      currency: "CAD",
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    },
  ).format(
    value,
  );
}


function signedMoney(
  value: number,
): string {

  if (!Number.isFinite(value)) {
    return "—";
  }

  const absolute = money(
    Math.abs(value),
  );

  if (value > 0) {
    return `+${absolute}`;
  }

  if (value < 0) {
    return `-${absolute}`;
  }

  return absolute;
}


function signedPercent(
  value: number,
): string {

  if (!Number.isFinite(value)) {
    return "—";
  }

  const rendered = Math.abs(
    value,
  ).toFixed(
    2,
  );

  if (value > 0) {
    return `+${rendered}%`;
  }

  if (value < 0) {
    return `-${rendered}%`;
  }

  return `${rendered}%`;
}


function compactMoney(
  value: number,
): string {

  const absolute = Math.abs(
    value,
  );

  if (absolute >= 1_000_000) {
    return `$${(
      value / 1_000_000
    ).toFixed(1)}M`;
  }

  if (absolute >= 1_000) {
    return `$${(
      value / 1_000
    ).toFixed(1)}K`;
  }

  return `$${value.toFixed(0)}`;
}


function formatObservationDate(
  date: Date,
  period: Period,
): string {

  if (period === "1D") {
    return new Intl.DateTimeFormat(
      "en-CA",
      {
        hour: "numeric",
        minute: "2-digit",
      },
    ).format(
      date,
    );
  }

  if (
    period === "1W"
    ||
    period === "1M"
    ||
    period === "3M"
  ) {
    return new Intl.DateTimeFormat(
      "en-CA",
      {
        month: "short",
        day: "numeric",
      },
    ).format(
      date,
    );
  }

  return new Intl.DateTimeFormat(
    "en-CA",
    {
      month: "short",
      year: "numeric",
    },
  ).format(
    date,
  );
}


function formatTooltipDate(
  date: Date,
): string {

  return new Intl.DateTimeFormat(
    "en-CA",
    {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
    },
  ).format(
    date,
  );
}


function buildSmoothPath(
  coordinates: Coordinate[],
): string {

  if (coordinates.length === 0) {
    return "";
  }

  if (coordinates.length === 1) {
    return (
      `M ${coordinates[0].x} ` +
      `${coordinates[0].y}`
    );
  }

  let path =
    `M ${coordinates[0].x} ` +
    `${coordinates[0].y}`;

  for (
    let index = 1;
    index < coordinates.length;
    index += 1
  ) {

    const previous =
      coordinates[index - 1];

    const current =
      coordinates[index];

    const controlX =
      (
        previous.x
        +
        current.x
      )
      / 2;

    path +=
      ` C ${controlX} ${previous.y},` +
      ` ${controlX} ${current.y},` +
      ` ${current.x} ${current.y}`;
  }

  return path;
}


export default function PortfolioPerformanceChart({
  currentAccountValue,
}: Props) {

  const [
    period,
    setPeriod,
  ] = useState<Period>(
    "1M",
  );

  const [
    rawPoints,
    setRawPoints,
  ] = useState<HistoryPoint[]>(
    [],
  );

  const [
    historyReferenceTime,
    setHistoryReferenceTime,
  ] = useState<number | null>(
    null,
  );

  const [
    loading,
    setLoading,
  ] = useState(
    true,
  );

  const [
    unavailable,
    setUnavailable,
  ] = useState(
    false,
  );

  const [
    hoveredIndex,
    setHoveredIndex,
  ] = useState<
    number | null
  >(
    null,
  );


  useEffect(
    () => {

      let cancelled = false;

      const loadHistory =
        async () => {

          setLoading(
            true,
          );

          setHistoryReferenceTime(
            null,
          );

          setRawPoints(
            [],
          );

          setUnavailable(
            false,
          );

          try {

            const response =
              await fetch(
                "/api/v1/snaptrade/portfolio/history?limit=1000",
                {
                  method: "GET",
                  credentials: "include",
                  cache: "no-store",
                },
              );

            if (!response.ok) {
              throw new Error(
                "History unavailable.",
              );
            }

            const payload =
              (
                await response.json()
              ) as HistoryResponse;

            if (cancelled) {
              return;
            }

            setHistoryReferenceTime(
              Date.now(),
            );

            setRawPoints(
              Array.isArray(
                payload.points,
              )
                ? payload.points
                : [],
            );

          } catch {

            if (!cancelled) {
              setUnavailable(
                true,
              );
            }

          } finally {

            if (!cancelled) {
              setLoading(
                false,
              );
            }
          }
        };

      void loadHistory();

      return () => {
        cancelled = true;
      };
    },
    [],
  );


  const allPoints =
    useMemo(
      () => {

        const parsed:
          ParsedPoint[] =
          [];

        for (
          const point
          of rawPoints
        ) {

          const observedAt =
            new Date(
              point.observed_at,
            );

          const accountValue =
            finiteNumber(
              point.account_value,
            );

          if (
            Number.isNaN(
              observedAt.getTime(),
            )
            ||
            accountValue === null
          ) {
            continue;
          }

          parsed.push(
            {
              observedAt,

              timestamp:
                observedAt.getTime(),

              accountValue,

              marketValue:
                finiteNumber(
                  point.market_value,
                ),

              cash:
                finiteNumber(
                  point.cash,
                ),

              unrealizedGain:
                finiteNumber(
                  point.unrealized_gain,
                ),
            },
          );
        }

        parsed.sort(
          (
            left,
            right,
          ) =>
            left.timestamp
            -
            right.timestamp,
        );

        return parsed;
      },
      [
        rawPoints,
      ],
    );


  const points =
    useMemo(
      () => {

        if (
          period === "ALL"
        ) {
          return allPoints;
        }

        if (
          historyReferenceTime === null
        ) {
          return [];
        }

        const cutoff =
          historyReferenceTime -
          periodMs[period];

        return allPoints.filter(
          point =>
            point.timestamp
            >=
            cutoff,
        );
      },
      [
        allPoints,
        period,
        historyReferenceTime,
      ],
    );





  const currentHistoryPoint =
    points.length > 0
      ? points[
          points.length - 1
        ]
      : null;


  const firstHistoryPoint =
    points.length > 0
      ? points[0]
      : null;


  const displayValue =
    typeof currentAccountValue === "number" &&
    Number.isFinite(currentAccountValue)
      ? currentAccountValue
      : null;


  const periodChange =
    (
      points.length >= 2
      &&
      firstHistoryPoint
      &&
      currentHistoryPoint
    )
      ? (
          currentHistoryPoint
            .accountValue
          -
          firstHistoryPoint
            .accountValue
        )
      : null;


  const periodChangePercent =
    (
      periodChange !== null
      &&
      firstHistoryPoint
      &&
      firstHistoryPoint
        .accountValue
      !== 0
    )
      ? (
          periodChange
          /
          Math.abs(
            firstHistoryPoint
              .accountValue,
          )
        )
        *
        100
      : null;


  const graph =
    useMemo(
      () => {

        if (
          points.length < 2
        ) {
          return null;
        }

        const width =
          1000;

        const height =
          360;

        const left =
          74;

        const right =
          22;

        const top =
          22;

        const bottom =
          48;

        const plotWidth =
          width
          -
          left
          -
          right;

        const plotHeight =
          height
          -
          top
          -
          bottom;

        const minTimestamp =
          points[0]
            .timestamp;

        const maxTimestamp =
          points[
            points.length - 1
          ].timestamp;

        const timestampRange =
          Math.max(
            1,
            maxTimestamp
            -
            minTimestamp,
          );

        const rawValues =
          points.map(
            point =>
              point.accountValue,
          );

        let minimum =
          Math.min(
            ...rawValues,
          );

        let maximum =
          Math.max(
            ...rawValues,
          );

        const rawRange =
          maximum
          -
          minimum;

        const padding =
          Math.max(
            rawRange * 0.12,
            Math.max(
              Math.abs(
                maximum,
              ),
              1,
            )
            * 0.012,
            0.5,
          );

        minimum -= padding;
        maximum += padding;

        if (
          maximum
          ===
          minimum
        ) {
          maximum += 1;
          minimum -= 1;
        }

        const valueRange =
          maximum
          -
          minimum;

        const coordinates:
          Coordinate[] =
          points.map(
            point => {

              const x =
                left
                +
                (
                  (
                    point.timestamp
                    -
                    minTimestamp
                  )
                  /
                  timestampRange
                )
                *
                plotWidth;

              const y =
                top
                +
                (
                  1
                  -
                  (
                    (
                      point.accountValue
                      -
                      minimum
                    )
                    /
                    valueRange
                  )
                )
                *
                plotHeight;

              return {
                ...point,
                x,
                y,
              };
            },
          );

        const linePath =
          buildSmoothPath(
            coordinates,
          );

        const firstCoordinate =
          coordinates[0];

        const lastCoordinate =
          coordinates[
            coordinates.length - 1
          ];

        const areaPath =
          `${linePath} ` +
          `L ${lastCoordinate.x} ${top + plotHeight} ` +
          `L ${firstCoordinate.x} ${top + plotHeight} Z`;

        const horizontalGuides =
          Array.from(
            {
              length: 5,
            },
            (
              _,
              index,
            ) => {

              const ratio =
                index
                /
                4;

              const y =
                top
                +
                ratio
                *
                plotHeight;

              const value =
                maximum
                -
                ratio
                *
                valueRange;

              return {
                y,
                value,
              };
            },
          );

        const labelIndexes =
          Array.from(
            new Set(
              [
                0,
                Math.round(
                  (
                    points.length
                    -
                    1
                  )
                  *
                  0.25,
                ),
                Math.round(
                  (
                    points.length
                    -
                    1
                  )
                  *
                  0.5,
                ),
                Math.round(
                  (
                    points.length
                    -
                    1
                  )
                  *
                  0.75,
                ),
                points.length - 1,
              ],
            ),
          )
          .sort(
            (
              a,
              b,
            ) =>
              a - b,
          );

        return {
          width,
          height,
          left,
          right,
          top,
          bottom,
          plotWidth,
          plotHeight,
          minimum,
          maximum,
          coordinates,
          linePath,
          areaPath,
          horizontalGuides,
          labelIndexes,
        };
      },
      [
        points,
      ],
    );


  const hoveredPoint =
    (
      graph
      &&
      hoveredIndex !== null
      &&
      graph.coordinates[
        hoveredIndex
      ]
    )
      ? graph.coordinates[
          hoveredIndex
        ]
      : null;


  const handlePointerMove =
    (
      event:
        React.PointerEvent<
          SVGSVGElement
        >,
    ) => {

      if (
        !graph
        ||
        graph.coordinates.length
        <
        2
      ) {
        return;
      }

      const bounds =
        event.currentTarget
          .getBoundingClientRect();

      if (
        bounds.width
        <=
        0
      ) {
        return;
      }

      const localX =
        (
          (
            event.clientX
            -
            bounds.left
          )
          /
          bounds.width
        )
        *
        graph.width;

      let nearestIndex =
        0;

      let nearestDistance =
        Number.POSITIVE_INFINITY;

      graph.coordinates.forEach(
        (
          point,
          index,
        ) => {

          const distance =
            Math.abs(
              point.x
              -
              localX,
            );

          if (
            distance
            <
            nearestDistance
          ) {
            nearestDistance =
              distance;

            nearestIndex =
              index;
          }
        },
      );

      setHoveredIndex(
        nearestIndex,
      );
    };


  const changePositive =
    (
      periodChange ?? 0
    )
    >
    0;

  const changeNegative =
    (
      periodChange ?? 0
    )
    <
    0;


  return (
    <section
      className="
        overflow-hidden rounded-[28px]
        border border-white/[0.08]
        bg-[linear-gradient(145deg,rgba(13,22,39,0.96),rgba(5,11,23,0.98))]
        shadow-[0_24px_80px_rgba(0,0,0,0.28)]
      "
    >
      <div
        className="
          border-b border-white/[0.06]
          px-5 py-5
          sm:px-6
          lg:px-7
        "
      >
        <div
          className="
            flex flex-col gap-5
            lg:flex-row
            lg:items-end
            lg:justify-between
          "
        >
          <div>
            <div
              className="
                flex items-center gap-2
                text-[11px] font-semibold
                uppercase tracking-[0.18em]
                text-cyan-300/70
              "
            >
              <span
                className="
                  h-1.5 w-1.5
                  rounded-full
                  bg-cyan-300
                  shadow-[0_0_12px_rgba(103,232,249,0.85)]
                "
              />

              Brokerage history
            </div>

            <h2
              className="
                mt-2 text-lg
                font-semibold
                tracking-[-0.02em]
                text-white
              "
            >
              Portfolio performance
            </h2>

            <p
              className="
                mt-1 max-w-xl text-xs
                leading-5 text-slate-500
              "
            >
              Recorded brokerage account-value observations.
              Historical observations are separate from the current account snapshot.
            </p>
          </div>

          <div
            className="
              inline-flex w-fit
              rounded-xl
              border border-white/[0.07]
              bg-black/20 p-1
            "
          >
            {periods.map(
              item => {

                const active =
                  item === period;

                return (
                  <button
                    key={item}
                    type="button"
                    onClick={() =>
                      setPeriod(item)
                    }
                    className={`
                      min-w-[42px]
                      rounded-lg
                      px-2.5 py-1.5
                      text-[11px]
                      font-semibold
                      transition
                      ${
                        active
                          ? `
                            bg-white/[0.10]
                            text-cyan-200
                            shadow-[inset_0_0_0_1px_rgba(103,232,249,0.16)]
                          `
                          : `
                            text-slate-500
                            hover:bg-white/[0.05]
                            hover:text-slate-300
                          `
                      }
                    `}
                  >
                    {item}
                  </button>
                );
              },
            )}
          </div>
        </div>

        <div
          className="
            mt-6 flex flex-wrap
            items-end gap-x-6
            gap-y-2
          "
        >
          <div>
            <div
              className="
                text-[10px]
                font-medium uppercase
                tracking-[0.14em]
                text-slate-600
              "
            >
              Current snapshot value
            </div>

            <div
              className="
                mt-1 text-3xl
                font-semibold
                tracking-[-0.045em]
                text-white
                sm:text-[34px]
              "
            >
              {money(
                displayValue,
              )}
            </div>
          </div>

          {periodChange !== null && (
            <div
              className={`
                mb-1 rounded-lg
                border px-2.5 py-1.5
                text-xs font-semibold
                ${
                  changePositive
                    ? `
                      border-emerald-400/15
                      bg-emerald-400/[0.07]
                      text-emerald-300
                    `
                    : changeNegative
                      ? `
                        border-rose-400/15
                        bg-rose-400/[0.07]
                        text-rose-300
                      `
                      : `
                        border-white/[0.07]
                        bg-white/[0.04]
                        text-slate-400
                      `
                }
              `}
            >
              {signedMoney(
                periodChange,
              )}

              {periodChangePercent !== null && (
                <span
                  className="
                    ml-1.5 opacity-75
                  "
                >
                  {signedPercent(
                    periodChangePercent,
                  )}
                </span>
              )}

              <span
                className="
                  ml-1.5 font-medium
                  opacity-60
                "
              >
                {period}
              </span>
            </div>
          )}
        </div>
      </div>

      <div
        className="
          px-4 pb-5 pt-4
          sm:px-5
          lg:px-6
        "
      >
        {loading ? (
          <div
            className="
              flex h-[330px]
              items-center justify-center
              rounded-2xl
              border border-white/[0.05]
              bg-black/10
            "
          >
            <div
              className="
                flex items-center gap-3
                text-sm text-slate-500
              "
            >
              <span
                className="
                  h-2 w-2 animate-pulse
                  rounded-full
                  bg-cyan-300/70
                "
              />

              Loading real portfolio history…
            </div>
          </div>
        ) : unavailable ? (
          <div
            className="
              flex h-[330px]
              flex-col items-center
              justify-center
              rounded-2xl
              border border-white/[0.05]
              bg-black/10
              px-6 text-center
            "
          >
            <div
              className="
                mb-3 flex h-10 w-10
                items-center justify-center
                rounded-full
                border border-amber-300/15
                bg-amber-300/[0.05]
                text-lg text-amber-200/70
              "
            >
              !
            </div>

            <p
              className="
                text-sm font-medium
                text-slate-300
              "
            >
              Portfolio history is temporarily unavailable.
            </p>

            <p
              className="
                mt-2 max-w-md
                text-xs leading-5
                text-slate-500
              "
            >
              The read-only brokerage history could not be loaded.
              This does not establish the current connection or account value.
            </p>
          </div>
        ) : points.length < 2 ? (
          <div
            className="
              relative flex h-[190px]
              overflow-hidden
              sm:h-[200px]
              rounded-2xl
              border border-white/[0.05]
              bg-black/10
            "
          >
            <div
              aria-hidden="true"
              className="
                absolute inset-0 opacity-40
                [background-image:linear-gradient(rgba(255,255,255,0.035)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.025)_1px,transparent_1px)]
                [background-size:100%_54px,90px_100%]
              "
            />

            <div
              aria-hidden="true"
              className="
                absolute left-[8%]
                right-[8%] top-1/2
                h-px
                bg-gradient-to-r
                from-transparent
                via-cyan-300/15
                to-transparent
              "
            />

            {points.length === 1 && (
              <div
                aria-hidden="true"
                className="
                  absolute left-1/2 top-1/2
                  -translate-x-1/2
                  -translate-y-1/2
                "
              >
                <div
                  className="
                    absolute left-1/2 top-1/2
                    h-14 w-14
                    -translate-x-1/2
                    -translate-y-1/2
                    animate-pulse rounded-full
                    border border-cyan-300/10
                    bg-cyan-300/[0.03]
                  "
                />

                <div
                  className="
                    h-3 w-3 rounded-full
                    border-2 border-slate-950
                    bg-cyan-300
                    shadow-[0_0_22px_rgba(103,232,249,0.75)]
                  "
                />
              </div>
            )}

            <div
              className="
                relative z-10 m-auto
                flex max-w-lg
                flex-col items-center
                px-5 py-4 text-center
              "
            >
              <div
                className="
                  mb-3 rounded-full
                  border border-cyan-300/10
                  bg-cyan-300/[0.04]
                  px-3 py-1
                  text-[10px] font-semibold
                  uppercase tracking-[0.16em]
                  text-cyan-200/70
                "
              >
                {points.length === 1
                  ? "First observation recorded"
                  : "Awaiting first observation"}
              </div>

              <p
                className="
                  text-base font-semibold
                  tracking-[-0.02em]
                  text-slate-200
                "
              >
                Building your performance history
              </p>

              <p
                className="
                  mt-2 max-w-md
                  text-xs leading-5
                  text-slate-500
                "
              >
                {points.length === 1
                  ? "1 real observation captured. The performance line appears after the next genuine observation."
                  : "The performance line appears after two genuine connected-account observations."}
              </p>

              <div
                className="
                  mt-3 flex items-center
                  gap-2 text-[10px]
                  uppercase tracking-[0.13em]
                  text-slate-600
                "
              >
                <span
                  className="
                    h-1.5 w-1.5
                    rounded-full
                    bg-emerald-300/70
                  "
                />

                Real observations only
              </div>
            </div>
          </div>
        ) : graph ? (
          <div
            className="
              relative overflow-hidden
              rounded-2xl
              border border-white/[0.05]
              bg-black/10
            "
          >
            <svg
              viewBox={
                `0 0 ${graph.width} ${graph.height}`
              }
              preserveAspectRatio="none"
              role="img"
              aria-label={
                `Real portfolio value over ${period}`
              }
              className="
                block h-[330px] w-full
                touch-none
              "
              onPointerMove={
                handlePointerMove
              }
              onPointerLeave={() =>
                setHoveredIndex(
                  null,
                )
              }
            >
              <defs>
                <linearGradient
                  id="portfolioAreaGradient"
                  x1="0"
                  y1="0"
                  x2="0"
                  y2="1"
                >
                  <stop
                    offset="0%"
                    stopColor="#67e8f9"
                    stopOpacity="0.20"
                  />

                  <stop
                    offset="55%"
                    stopColor="#67e8f9"
                    stopOpacity="0.055"
                  />

                  <stop
                    offset="100%"
                    stopColor="#67e8f9"
                    stopOpacity="0"
                  />
                </linearGradient>

                <linearGradient
                  id="portfolioLineGradient"
                  x1="0"
                  y1="0"
                  x2="1"
                  y2="0"
                >
                  <stop
                    offset="0%"
                    stopColor="#38bdf8"
                  />

                  <stop
                    offset="55%"
                    stopColor="#67e8f9"
                  />

                  <stop
                    offset="100%"
                    stopColor="#a78bfa"
                  />
                </linearGradient>

                <filter
                  id="portfolioGlow"
                  x="-30%"
                  y="-30%"
                  width="160%"
                  height="160%"
                >
                  <feGaussianBlur
                    stdDeviation="4"
                    result="blur"
                  />

                  <feMerge>
                    <feMergeNode
                      in="blur"
                    />

                    <feMergeNode
                      in="SourceGraphic"
                    />
                  </feMerge>
                </filter>
              </defs>

              {graph.horizontalGuides.map(
                (
                  guide,
                  index,
                ) => (
                  <g
                    key={
                      `guide-${index}`
                    }
                  >
                    <line
                      x1={graph.left}
                      x2={
                        graph.width
                        -
                        graph.right
                      }
                      y1={guide.y}
                      y2={guide.y}
                      stroke="rgba(148,163,184,0.09)"
                      strokeWidth="1"
                      vectorEffect="non-scaling-stroke"
                    />

                    <text
                      x={
                        graph.left
                        -
                        12
                      }
                      y={
                        guide.y
                        +
                        4
                      }
                      textAnchor="end"
                      fill="rgba(148,163,184,0.48)"
                      fontSize="11"
                    >
                      {compactMoney(
                        guide.value,
                      )}
                    </text>
                  </g>
                ),
              )}

              {graph.labelIndexes.map(
                index => {

                  const point =
                    graph.coordinates[
                      index
                    ];

                  return (
                    <text
                      key={
                        `x-${index}`
                      }
                      x={point.x}
                      y={
                        graph.height
                        -
                        15
                      }
                      textAnchor={
                        index === 0
                          ? "start"
                          : index
                            ===
                            graph.coordinates.length
                            -
                            1
                            ? "end"
                            : "middle"
                      }
                      fill="rgba(148,163,184,0.44)"
                      fontSize="11"
                    >
                      {formatObservationDate(
                        point.observedAt,
                        period,
                      )}
                    </text>
                  );
                },
              )}

              <path
                d={
                  graph.areaPath
                }
                fill="url(#portfolioAreaGradient)"
              />

              <path
                d={
                  graph.linePath
                }
                fill="none"
                stroke="rgba(103,232,249,0.15)"
                strokeWidth="8"
                strokeLinecap="round"
                strokeLinejoin="round"
                vectorEffect="non-scaling-stroke"
                filter="url(#portfolioGlow)"
              />

              <path
                d={
                  graph.linePath
                }
                fill="none"
                stroke="url(#portfolioLineGradient)"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
                vectorEffect="non-scaling-stroke"
              />

              {hoveredPoint && (
                <>
                  <line
                    x1={
                      hoveredPoint.x
                    }
                    x2={
                      hoveredPoint.x
                    }
                    y1={
                      graph.top
                    }
                    y2={
                      graph.top
                      +
                      graph.plotHeight
                    }
                    stroke="rgba(103,232,249,0.32)"
                    strokeWidth="1"
                    strokeDasharray="4 5"
                    vectorEffect="non-scaling-stroke"
                  />

                  <line
                    x1={
                      graph.left
                    }
                    x2={
                      graph.width
                      -
                      graph.right
                    }
                    y1={
                      hoveredPoint.y
                    }
                    y2={
                      hoveredPoint.y
                    }
                    stroke="rgba(103,232,249,0.12)"
                    strokeWidth="1"
                    strokeDasharray="3 6"
                    vectorEffect="non-scaling-stroke"
                  />

                  <circle
                    cx={
                      hoveredPoint.x
                    }
                    cy={
                      hoveredPoint.y
                    }
                    r="9"
                    fill="rgba(103,232,249,0.12)"
                    stroke="none"
                  />

                  <circle
                    cx={
                      hoveredPoint.x
                    }
                    cy={
                      hoveredPoint.y
                    }
                    r="4.5"
                    fill="#67e8f9"
                    stroke="#07111f"
                    strokeWidth="2"
                    vectorEffect="non-scaling-stroke"
                  />
                </>
              )}
            {hoveredPoint && (
              <foreignObject
                x={
                  Math.max(
                    0,
                    Math.min(
                      graph.width - 240,
                      hoveredPoint.x - 120,
                    ),
                  )
                }
                y={
                  Math.max(
                    10,
                    hoveredPoint.y - 140,
                  )
                }
                width="240"
                height="150"
                className="pointer-events-none overflow-visible"
              >
                <div
                  className="
                  pointer-events-none
                  
                  min-w-[190px]
                  
                  rounded-xl
                  border border-white/[0.10]
                  bg-[#08111f]/95
                  px-3.5 py-3
                  shadow-[0_16px_50px_rgba(0,0,0,0.45)]
                  backdrop-blur-xl
                "
                
              >
                <div
                  className="
                    text-[10px]
                    font-medium uppercase
                    tracking-[0.12em]
                    text-slate-500
                  "
                >
                  {formatTooltipDate(
                    hoveredPoint
                      .observedAt,
                  )}
                </div>

                <div
                  className="
                    mt-1 text-base
                    font-semibold
                    tracking-[-0.025em]
                    text-white
                  "
                >
                  {money(
                    hoveredPoint
                      .accountValue,
                  )}
                </div>

                <div
                  className="
                    mt-2 grid grid-cols-2
                    gap-x-4 gap-y-1
                    text-[10px]
                  "
                >
                  <span
                    className="
                      text-slate-600
                    "
                  >
                    Market
                  </span>

                  <span
                    className="
                      text-right text-slate-400
                    "
                  >
                    {money(
                      hoveredPoint
                        .marketValue,
                    )}
                  </span>

                  <span
                    className="
                      text-slate-600
                    "
                  >
                    Cash
                  </span>

                  <span
                    className="
                      text-right text-slate-400
                    "
                  >
                    {money(
                      hoveredPoint
                        .cash,
                    )}
                  </span>

                  <span
                    className="
                      text-slate-600
                    "
                  >
                    Unrealized
                  </span>

                  <span
                    className="
                      text-right text-slate-400
                    "
                  >
                    {money(
                      hoveredPoint
                        .unrealizedGain,
                    )}
                  </span>
                </div>
              </div>
              </foreignObject>
            )}
</svg>

            
            <div
              className="
                pointer-events-none
                absolute bottom-2
                right-3
                text-[9px]
                uppercase
                tracking-[0.12em]
                text-slate-700
              "
            >
              Real observations only
            </div>
          </div>
        ) : null}

        {!loading && !unavailable && (
          <div
            className="
              mt-3 flex flex-wrap
              items-center justify-between
              gap-2 px-1
              text-[10px]
              text-slate-600
            "
          >
            <span>
              {points.length}
              {" "}
              real
              {" "}
              {points.length === 1
                ? "observation"
                : "observations"}
              {" "}
              in {period}
            </span>

            {currentHistoryPoint && (
              <span>
                Latest recorded{" "}
                {formatTooltipDate(
                  currentHistoryPoint
                    .observedAt,
                )}
              </span>
            )}
          </div>
        )}
      </div>
    </section>
  );
}
