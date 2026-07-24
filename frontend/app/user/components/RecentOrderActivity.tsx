"use client";

import {
  Panel,
  StatusBadge,
  StatusMessage,
} from "../../../components/ui";

type UnknownRecord =
  Record<string, unknown>;

type RecentOrderActivityProps = {
  orders: unknown[];
};

function asRecord(
  value: unknown,
): UnknownRecord {
  if (
    typeof value === "object" &&
    value !== null &&
    !Array.isArray(value)
  ) {
    return value as UnknownRecord;
  }

  return {};
}

function readString(
  record: UnknownRecord,
  keys: string[],
  fallback = "",
): string {
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

  return fallback;
}

function readNumber(
  record: UnknownRecord,
  keys: string[],
): number | null {
  for (const key of keys) {
    const value = record[key];

    if (
      typeof value === "number" &&
      Number.isFinite(value)
    ) {
      return value;
    }

    if (
      typeof value === "string" &&
      value.trim()
    ) {
      const parsed = Number(
        value,
      );

      if (
        Number.isFinite(parsed)
      ) {
        return parsed;
      }
    }
  }

  return null;
}

function formatMoney(
  value: number | null,
): string {
  if (value === null) {
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
  ).format(value);
}

function formatQuantity(
  value: number | null,
): string {
  if (value === null) {
    return "—";
  }

  return new Intl.NumberFormat(
    "en-CA",
    {
      maximumFractionDigits: 6,
    },
  ).format(value);
}

function formatTimestamp(
  value: string,
): string {
  if (!value) {
    return "Timestamp unavailable";
  }

  const date = new Date(
    value,
  );

  if (
    Number.isNaN(
      date.getTime(),
    )
  ) {
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

function statusTone(
  status: string,
):
  | "success"
  | "warning"
  | "danger"
  | "info" {
  const normalized =
    status.toLowerCase();

  if (
    normalized.includes("executed") ||
    normalized.includes("filled") ||
    normalized.includes("complete")
  ) {
    return "success";
  }

  if (
    normalized.includes("reject") ||
    normalized.includes("fail") ||
    normalized.includes("error") ||
    normalized.includes("cancel")
  ) {
    return "danger";
  }

  if (
    normalized.includes("pending") ||
    normalized.includes("queued") ||
    normalized.includes("review")
  ) {
    return "warning";
  }

  return "info";
}

export default function RecentOrderActivity({
  orders,
}: RecentOrderActivityProps) {
  const normalizedOrders =
    Array.isArray(orders)
      ? orders
          .map(asRecord)
          .slice(0, 8)
      : [];

  return (
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

          <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-400">
            These records come from the
            currently authenticated
            account&apos;s owner-scoped
            order ledger.
          </p>
        </div>

        <StatusBadge tone="violet">
          {orders.length} total
        </StatusBadge>
      </div>

      <div
        data-testid="recent-order-activity"
        className="p-6"
      >
        {normalizedOrders.length === 0 ? (
          <StatusMessage tone="info">
            No paper orders have been
            recorded for this account yet.
          </StatusMessage>
        ) : (
          <div className="space-y-3">
            {normalizedOrders.map(
              (
                order,
                index,
              ) => {
                const symbol =
                  readString(
                    order,
                    [
                      "symbol",
                      "ticker",
                      "asset_symbol",
                    ],
                    "Unknown",
                  ).toUpperCase();

                const action =
                  readString(
                    order,
                    [
                      "signal",
                      "action",
                      "side",
                      "order_side",
                    ],
                    "order",
                  ).toUpperCase();

                const status =
                  readString(
                    order,
                    [
                      "status",
                      "order_status",
                      "execution_status",
                    ],
                    "recorded",
                  );

                const quantity =
                  readNumber(
                    order,
                    [
                      "shares_quantity",
                      "quantity",
                      "shares",
                      "filled_quantity",
                    ],
                  );

                const price =
                  readNumber(
                    order,
                    [
                      "slippage_price",
                      "execution_price",
                      "fill_price",
                      "price",
                    ],
                  );

                const allocatedCapital =
                  readNumber(
                    order,
                    [
                      "allocated_capital",
                      "notional",
                      "total_value",
                      "total_cost",
                    ],
                  );

                const commission =
                  readNumber(
                    order,
                    [
                      "commission_paid",
                      "commission",
                      "fees",
                      "fee",
                    ],
                  );

                const timestamp =
                  readString(
                    order,
                    [
                      "created_at",
                      "timestamp",
                      "executed_at",
                      "updated_at",
                      "last_updated",
                    ],
                  );

                const identifier =
                  readString(
                    order,
                    [
                      "id",
                      "order_id",
                      "trade_id",
                      "trace_id",
                    ],
                    `${symbol}-${index}`,
                  );

                return (
                  <article
                    key={
                      identifier
                    }
                    className="rounded-2xl border border-white/[0.07] bg-white/[0.025] p-4"
                  >
                    <div className="flex flex-wrap items-start justify-between gap-4">
                      <div>
                        <div className="flex flex-wrap items-center gap-3">
                          <span
                            className={[
                              "rounded-lg px-2.5 py-1 text-xs font-black uppercase tracking-[0.12em]",
                              action === "BUY"
                                ? "bg-emerald-300/[0.12] text-emerald-200"
                                : action === "SELL"
                                  ? "bg-amber-300/[0.12] text-amber-200"
                                  : "bg-cyan-300/[0.1] text-cyan-200",
                            ].join(
                              " ",
                            )}
                          >
                            {action}
                          </span>

                          <h3 className="text-lg font-black text-white">
                            {symbol}
                          </h3>
                        </div>

                        <p className="mt-2 text-xs text-slate-500">
                          {formatTimestamp(
                            timestamp,
                          )}
                        </p>
                      </div>

                      <StatusBadge
                        tone={statusTone(
                          status,
                        )}
                      >
                        {status}
                      </StatusBadge>
                    </div>

                    <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                      <div>
                        <p className="nv-stat-label">
                          Quantity
                        </p>

                        <p className="mt-2 font-black text-white">
                          {formatQuantity(
                            quantity,
                          )}
                        </p>
                      </div>

                      <div>
                        <p className="nv-stat-label">
                          Execution price
                        </p>

                        <p className="mt-2 font-black text-white">
                          {formatMoney(
                            price,
                          )}
                        </p>
                      </div>

                      <div>
                        <p className="nv-stat-label">
                          Allocated capital
                        </p>

                        <p className="mt-2 font-black text-white">
                          {formatMoney(
                            allocatedCapital,
                          )}
                        </p>
                      </div>

                      <div>
                        <p className="nv-stat-label">
                          Fees
                        </p>

                        <p className="mt-2 font-black text-amber-200">
                          {formatMoney(
                            commission,
                          )}
                        </p>
                      </div>
                    </div>
                  </article>
                );
              },
            )}
          </div>
        )}
      </div>

      <div className="flex flex-wrap gap-2 border-t border-white/[0.07] px-6 py-5">
        <StatusBadge tone="info">
          Authenticated read
        </StatusBadge>

        <StatusBadge tone="violet">
          Owner scoped
        </StatusBadge>

        <StatusBadge tone="success">
          Ledger backed
        </StatusBadge>

        <StatusBadge tone="warning">
          Paper execution only
        </StatusBadge>
      </div>
    </Panel>
  );
}
