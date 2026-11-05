"use client";

import {
  useMemo,
} from "react";


type PositionLike = {
  symbol?: string | null;
  market_value?: string | number | null;
  shares_quantity?: string | number | null;
};


type Props = {
  positions:
    PositionLike[]
    | null
    | undefined;
};


type AllocationSlice = {
  symbol: string;
  value: number;
  percent: number;
  startAngle: number;
  endAngle: number;
};


const palette = [
  "#67e8f9",
  "#38bdf8",
  "#818cf8",
  "#a78bfa",
  "#c084fc",
  "#22d3ee",
];


function numberValue(
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

  const parsed =
    Number(value);

  return Number.isFinite(parsed)
    ? parsed
    : null;
}


function money(
  value: number,
): string {

  return new Intl.NumberFormat(
    "en-CA",
    {
      style: "currency",
      currency: "CAD",
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    },
  ).format(value);
}


function polar(
  cx: number,
  cy: number,
  radius: number,
  degrees: number,
) {

  const radians =
    (
      degrees - 90
    )
    *
    Math.PI
    /
    180;

  return {
    x:
      cx
      +
      radius
      *
      Math.cos(radians),

    y:
      cy
      +
      radius
      *
      Math.sin(radians),
  };
}


function arc(
  startAngle: number,
  endAngle: number,
): string {

  const cx = 110;
  const cy = 110;
  const radius = 76;

  const start =
    polar(
      cx,
      cy,
      radius,
      endAngle,
    );

  const end =
    polar(
      cx,
      cy,
      radius,
      startAngle,
    );

  const largeArc =
    endAngle - startAngle
    >
    180
      ? 1
      : 0;

  return [
    "M",
    start.x,
    start.y,
    "A",
    radius,
    radius,
    0,
    largeArc,
    0,
    end.x,
    end.y,
  ].join(" ");
}


export default function HoldingsAllocationDonut({
  positions,
}: Props) {

  const allocation =
    useMemo(
      () => {

        const holdings =
          (
            Array.isArray(positions)
              ? positions
              : []
          )
          .map(
            position => {

              const value =
                numberValue(
                  position.market_value,
                );

              const symbol =
                String(
                  position.symbol
                  ??
                  "—",
                ).trim();

              return {
                symbol:
                  symbol || "—",

                value,
              };
            },
          )
          .filter(
            (
              holding,
            ): holding is {
              symbol: string;
              value: number;
            } =>
              holding.value
              !==
              null
              &&
              holding.value
              >
              0,
          )
          .sort(
            (
              left,
              right,
            ) =>
              right.value
              -
              left.value,
          );

        const total =
          holdings.reduce(
            (
              sum,
              holding,
            ) =>
              sum
              +
              holding.value,
            0,
          );

        const slices:
          AllocationSlice[] =
          holdings.reduce<AllocationSlice[]>(
            (accumulator, holding) => {

              const percent =
                total > 0
                  ? (
                      holding.value
                      /
                      total
                    )
                    *
                    100
                  : 0;

              const startAngle =
                accumulator.length > 0
                  ? accumulator[accumulator.length - 1].endAngle
                  : 0;

              const endAngle =
                startAngle
                +
                (
                  percent
                  /
                  100
                )
                *
                360;

              accumulator.push({
                symbol:
                  holding.symbol,

                value:
                  holding.value,

                percent,

                startAngle,

                endAngle,
              });

              return accumulator;
            },
            [],
          );

        return {
          total,
          slices,
        };
      },
      [
        positions,
      ],
    );


  return (
    <section
      className="
        h-full
        rounded-[28px]
        border border-white/[0.08]
        bg-[linear-gradient(145deg,rgba(13,22,39,0.96),rgba(5,11,23,0.98))]
        p-5
        shadow-[0_24px_80px_rgba(0,0,0,0.24)]
        sm:p-6
      "
    >
      <div
        className="
          flex items-start
          justify-between
          gap-3
        "
      >
        <div>
          <div
            className="
              text-[10px]
              font-semibold uppercase
              tracking-[0.18em]
              text-violet-300/70
            "
          >
            Allocation
          </div>

          <h2
            className="
              mt-2 text-lg
              font-semibold
              tracking-[-0.02em]
              text-white
            "
          >
            Holdings mix
          </h2>

          <p
            className="
              mt-1 text-xs
              leading-5
              text-slate-500
            "
          >
            Current connected positions by market value.
          </p>
        </div>

        <div
          className="
            rounded-lg
            border border-white/[0.06]
            bg-white/[0.03]
            px-2 py-1
            text-[9px]
            font-semibold uppercase
            tracking-[0.12em]
            text-slate-500
          "
        >
          Real snapshot
        </div>
      </div>

      {allocation.slices.length === 0 ? (
        <div
          className="
            mt-6 flex min-h-[280px]
            items-center justify-center
            rounded-2xl
            border border-white/[0.05]
            bg-black/10
            px-5 text-center
          "
        >
          <div>
            <p
              className="
                text-sm font-medium
                text-slate-300
              "
            >
              No allocation data yet.
            </p>

            <p
              className="
                mt-2 text-xs
                leading-5
                text-slate-500
              "
            >
              Current connected holdings appear here when
              market values are available.
            </p>
          </div>
        </div>
      ) : (
        <>
          <div
            className="
              relative mx-auto
              mt-6 h-[220px]
              w-[220px]
            "
          >
            <svg
              viewBox="0 0 220 220"
              role="img"
              aria-label="Connected holdings allocation by market value"
              className="
                h-full w-full
                overflow-visible
              "
            >
              <circle
                cx="110"
                cy="110"
                r="76"
                fill="none"
                stroke="rgba(255,255,255,0.055)"
                strokeWidth="26"
              />

              {allocation.slices.map(
                (
                  slice,
                  index,
                ) => {

                  const gap =
                    allocation.slices.length > 1
                      ? 1.4
                      : 0;

                  return (
                    <path
                      key={
                        `${slice.symbol}-${index}`
                      }
                      d={
                        arc(
                          slice.startAngle,
                          Math.max(
                            slice.startAngle,
                            slice.endAngle
                            -
                            gap,
                          ),
                        )
                      }
                      fill="none"
                      stroke={
                        palette[
                          index
                          %
                          palette.length
                        ]
                      }
                      strokeWidth="26"
                      strokeLinecap="round"
                    >
                      <title>
                        {slice.symbol}
                        {" · "}
                        {slice.percent.toFixed(1)}
                        %
                        {" · "}
                        {money(slice.value)}
                      </title>
                    </path>
                  );
                },
              )}

              <circle
                cx="110"
                cy="110"
                r="55"
                fill="#08111f"
              />
            </svg>

            <div
              className="
                pointer-events-none
                absolute inset-0
                flex flex-col
                items-center
                justify-center
                text-center
              "
            >
              <span
                className="
                  text-[9px]
                  font-semibold uppercase
                  tracking-[0.14em]
                  text-slate-600
                "
              >
                Invested
              </span>

              <span
                className="
                  mt-1 text-xl
                  font-semibold
                  tracking-[-0.04em]
                  text-white
                "
              >
                {money(
                  allocation.total,
                )}
              </span>

              <span
                className="
                  mt-1 text-[9px]
                  uppercase
                  tracking-[0.10em]
                  text-slate-700
                "
              >
                Market value
              </span>
            </div>
          </div>

          <div
            className="
              mt-5 space-y-2
            "
          >
            {allocation.slices.map(
              (
                slice,
                index,
              ) => (
                <div
                  key={
                    `${slice.symbol}-row-${index}`
                  }
                  className="
                    flex items-center
                    justify-between gap-3
                    rounded-xl
                    border border-white/[0.05]
                    bg-white/[0.025]
                    px-3 py-2.5
                  "
                >
                  <div
                    className="
                      flex min-w-0
                      items-center gap-2.5
                    "
                  >
                    <span
                      className={
                        [
                          "h-2.5 w-2.5",
                          "shrink-0 rounded-full",
                          "nv-allocation-colour-"
                          + (index % palette.length),
                        ].join(" ")
                      }
                    />

                    <span
                      className="
                        truncate text-sm
                        font-medium
                        text-slate-300
                      "
                    >
                      {slice.symbol}
                    </span>
                  </div>

                  <div
                    className="
                      shrink-0 text-right
                    "
                  >
                    <div
                      className="
                        text-sm font-semibold
                        text-slate-200
                      "
                    >
                      {slice.percent.toFixed(1)}%
                    </div>

                    <div
                      className="
                        text-[10px]
                        text-slate-600
                      "
                    >
                      {money(
                        slice.value,
                      )}
                    </div>
                  </div>
                </div>
              ),
            )}
          </div>

          <div
            className="
              mt-4 text-center
              text-[9px]
              font-medium uppercase
              tracking-[0.13em]
              text-slate-700
            "
          >
            No synthetic allocation values
          </div>
        </>
      )}
    </section>
  );
}
