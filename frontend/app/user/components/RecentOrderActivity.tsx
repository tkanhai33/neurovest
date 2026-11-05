"use client";

import { useState } from "react";

import {
  Panel,
  StatusBadge,
  StatusMessage,
} from "../../../components/ui";

type UnknownRecord =
  Record<string, unknown>;

type RecentOrderActivityProps = {
  orders: unknown[];
  unavailable?: boolean;
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
  unavailable = false,
}: RecentOrderActivityProps) {
  // Filters operate only on the eight records supplied to this
  // compact account-history panel. No new API or ledger writes.
  const [orderSearch, setOrderSearch] = useState("");
  const [orderStatusFilter, setOrderStatusFilter] =
    useState("all");
  const [orderSideFilter, setOrderSideFilter] =
    useState("all");

  const normalizedOrders =
    Array.isArray(orders)
      ? orders
          .map(asRecord)
          .slice(0, 8)
      : [];

  const filteredOrders = normalizedOrders.filter((order) => {
    const symbol = readString(
      order,
      ["symbol", "ticker", "asset_symbol"],
    ).toLowerCase();

    const action = readString(
      order,
      ["signal", "action", "side", "order_side"],
    ).toLowerCase();

    const status = readString(
      order,
      ["status", "order_status", "execution_status"],
      "recorded",
    ).toLowerCase();

    const identifier = readString(
      order,
      ["id", "order_id", "trade_id", "trace_id"],
    ).toLowerCase();

    const search = orderSearch.trim().toLowerCase();

    const matchesSearch =
      !search ||
      symbol.includes(search) ||
      action.includes(search) ||
      status.includes(search) ||
      identifier.includes(search);

    const isFilled =
      status.includes("executed") ||
      status.includes("filled") ||
      status.includes("complete");

    const isClosed =
      status.includes("reject") ||
      status.includes("fail") ||
      status.includes("error") ||
      status.includes("cancel");

    const isPending =
      status.includes("pending") ||
      status.includes("queued") ||
      status.includes("review");

    const category = isFilled
      ? "filled"
      : isClosed
        ? "closed"
        : isPending
          ? "pending"
          : "other";

    return (
      matchesSearch &&
      (orderStatusFilter === "all" ||
        orderStatusFilter === category) &&
      (orderSideFilter === "all" ||
        orderSideFilter === action)
    );
  });

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

        <StatusBadge tone={unavailable ? "warning" : "violet"}>
          {unavailable ? "Unavailable" : `${orders.length} total`}
        </StatusBadge>
      </div>

      <div
        data-testid="recent-order-activity"
        className="p-6"
      >
        {!unavailable && normalizedOrders.length > 0 && (
          <div
            data-testid="f8-order-filters"
            className="mb-5 rounded-2xl border border-white/[0.08] bg-white/[0.02] p-4"
          >
            <div className="grid gap-3 md:grid-cols-3">
              <label className="block min-w-0">
                <span className="nv-stat-label">
                  Search recent orders
                </span>
                <input
                  type="search"
                  data-testid="f8-order-search"
                  value={orderSearch}
                  onChange={(event) =>
                    setOrderSearch(event.target.value)
                  }
                  placeholder="Symbol, status, or ID"
                  className="nv-input mt-2 w-full"
                />
              </label>

              <label className="block min-w-0">
                <span className="nv-stat-label">
                  Order status
                </span>
                <select
                  data-testid="f8-order-status"
                  value={orderStatusFilter}
                  onChange={(event) =>
                    setOrderStatusFilter(event.target.value)
                  }
                  className="nv-input mt-2 w-full"
                >
                  <option value="all">All statuses</option>
                  <option value="filled">Filled / executed</option>
                  <option value="pending">Pending / under review</option>
                  <option value="closed">Cancelled / rejected / failed</option>
                  <option value="other">Other recorded statuses</option>
                </select>
              </label>

              <label className="block min-w-0">
                <span className="nv-stat-label">
                  Direction
                </span>
                <select
                  data-testid="f8-order-side"
                  value={orderSideFilter}
                  onChange={(event) =>
                    setOrderSideFilter(event.target.value)
                  }
                  className="nv-input mt-2 w-full"
                >
                  <option value="all">Buy and sell</option>
                  <option value="buy">Buy only</option>
                  <option value="sell">Sell only</option>
                </select>
              </label>
            </div>

            <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
              <p
                data-testid="f8-order-visible-count"
                aria-live="polite"
                className="text-xs text-slate-400"
              >
                Showing {filteredOrders.length} of{" "}
                {normalizedOrders.length} recent records
              </p>
              {(orderSearch ||
                orderStatusFilter !== "all" ||
                orderSideFilter !== "all") && (
                <button
                  type="button"
                  data-testid="f8-order-clear-filters"
                  onClick={() => {
                    setOrderSearch("");
                    setOrderStatusFilter("all");
                    setOrderSideFilter("all");
                  }}
                  className="nv-button nv-button-secondary nv-button-sm"
                >
                  Clear filters
                </button>
              )}
            </div>
            <p className="mt-2 text-xs leading-5 text-slate-500">
              Filtering the eight most recent records shown here.
              This is not a search of the complete order ledger.
            </p>
          </div>
        )}
        {unavailable ? (
          <StatusMessage tone="warning">
            Order history is currently unavailable.
            Please refresh your account to try again.
          </StatusMessage>
        ) : normalizedOrders.length === 0 ? (
          <StatusMessage tone="info">
            No paper orders have been
            recorded for this account yet.
          </StatusMessage>
        ) : filteredOrders.length === 0 ? (
          <StatusMessage tone="info">
            No recent orders match these filters.
            Clear the filters to restore this view.
          </StatusMessage>
        ) : (
          <div className="space-y-3">
            {filteredOrders.map(
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
