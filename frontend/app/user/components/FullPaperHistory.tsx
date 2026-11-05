"use client";

import { useState } from "react";

type RecordValue = Record<string, unknown>;

type Props = {
  orders: unknown[];
  unavailable?: boolean;
  totalRecords?: number;
};

const PAGE_SIZE = 20;

function recordOf(value: unknown): RecordValue {
  return value !== null &&
    typeof value === "object" &&
    !Array.isArray(value)
    ? value as RecordValue
    : {};
}

function stringOf(
  row: RecordValue,
  ...keys: string[]
): string {
  for (const key of keys) {
    const value = row[key];
    if (typeof value === "string" && value.trim()) {
      return value.trim();
    }
    if (typeof value === "number" && Number.isFinite(value)) {
      return String(value);
    }
  }
  return "";
}

function numberOf(value: unknown): number | null {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    return null;
  }
  return value;
}

function displayNumber(
  value: unknown,
  digits = 2,
): string {
  const n = numberOf(value);
  return n === null
    ? "Unavailable"
    : n.toLocaleString("en-CA", {
        minimumFractionDigits: digits,
        maximumFractionDigits: digits,
      });
}

function categoryOf(status: string): string {
  const value = status.toLowerCase();
  if (/executed|filled|complete/.test(value)) return "filled";
  if (/cancel|reject|fail|error/.test(value)) return "closed";
  if (/pending|queued|review/.test(value)) return "pending";
  return "other";
}

function sideOf(value: string): string {
  const side = value.toLowerCase();
  if (side === "buy" || side === "long") return "buy";
  if (side === "sell" || side === "short") return "sell";
  return "other";
}

function csvCell(value: unknown): string {
  let text = value == null ? "" : String(value);

  // Prevent CSV spreadsheet-formula execution.
  if (/^[\s]*[=+\-@\t\r]/.test(text)) {
    text = "'" + text;
  }

  return '"' + text.replace(/"/g, '""') + '"';
}

export default function FullPaperHistory({
  orders,
  unavailable = false,
  totalRecords,
}: Props) {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [sideFilter, setSideFilter] = useState("all");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [page, setPage] = useState(1);

  const records = Array.isArray(orders)
    ? orders.map(recordOf)
    : [];

  const advertisedTotal =
    typeof totalRecords === "number" &&
    Number.isSafeInteger(totalRecords) &&
    totalRecords >= 0
      ? totalRecords
      : null;

  const complete =
    !unavailable &&
    advertisedTotal !== null &&
    advertisedTotal === records.length;

  const validRange =
    !dateFrom || !dateTo || dateFrom <= dateTo;

  const filtered = validRange ? records.filter(row => {
    const symbol = stringOf(row, "symbol", "ticker");
    const side = stringOf(row, "signal", "action", "side");
    const status = stringOf(row, "status", "order_status");
    const id = stringOf(row, "id", "order_id");
    const timestamp = stringOf(row, "timestamp");

    const query = search.trim().toLowerCase();
    const matchesSearch =
      !query ||
      [symbol, side, status, id].some(value =>
        value.toLowerCase().includes(query),
      );

    const date = /^\d{4}-\d{2}-\d{2}/.test(timestamp)
      ? timestamp.slice(0, 10)
      : "";

    const matchesDates =
      (!dateFrom || (date !== "" && date >= dateFrom)) &&
      (!dateTo || (date !== "" && date <= dateTo));

    return matchesSearch &&
      matchesDates &&
      (statusFilter === "all" ||
        categoryOf(status) === statusFilter) &&
      (sideFilter === "all" ||
        sideOf(side) === sideFilter);
  }) : [];

  const pageCount = Math.max(
    1,
    Math.ceil(filtered.length / PAGE_SIZE),
  );

  const currentPage = Math.min(page, pageCount);

  const visible = filtered.slice(
    (currentPage - 1) * PAGE_SIZE,
    currentPage * PAGE_SIZE,
  );

  const buyCount = filtered.filter(
    row => sideOf(stringOf(row, "signal", "side")) === "buy",
  ).length;

  const sellCount = filtered.filter(
    row => sideOf(stringOf(row, "signal", "side")) === "sell",
  ).length;

  function resetFilters() {
    setSearch("");
    setStatusFilter("all");
    setSideFilter("all");
    setDateFrom("");
    setDateTo("");
    setPage(1);
  }

  function exportCsv() {
    if (!complete || filtered.length === 0 || !validRange) {
      return;
    }

    const headers = [
      "id", "timestamp", "symbol", "direction",
      "status", "quantity", "execution_price",
      "allocated_capital", "commission_paid",
    ];

    const rows = filtered.map(row => [
      stringOf(row, "id"),
      stringOf(row, "timestamp"),
      stringOf(row, "symbol"),
      stringOf(row, "signal", "side"),
      stringOf(row, "status"),
      row.shares_quantity,
      row.slippage_price,
      row.allocated_capital,
      row.commission_paid,
    ]);

    const content = [
      headers.map(csvCell).join(","),
      ...rows.map(row => row.map(csvCell).join(",")),
    ].join("\r\n");

    const blob = new Blob(
      ["\ufeff", content],
      { type: "text/csv;charset=utf-8" },
    );
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");

    anchor.href = url;
    anchor.download = "neurovest-paper-history.csv";
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(url);
  }

  return (
    <section
      data-testid="f10-full-paper-history"
      className="overflow-hidden rounded-[28px] border border-white/[0.08] bg-[#070e1d]"
    >
      <div className="border-b border-white/[0.08] p-5 sm:p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="nv-eyebrow">Paper ledger</p>
            <h3 className="mt-2 text-2xl font-black text-white">
              Complete paper order history
            </h3>
            <p className="mt-2 text-sm leading-6 text-slate-400">
              Read-only records belonging to the authenticated account.
              Brokerage transactions are not included.
            </p>
          </div>
          <span className="rounded-full border border-violet-400/20 px-3 py-1 text-xs font-semibold text-violet-200">
            Simulation only
          </span>
        </div>

        {unavailable ? (
          <p role="alert" className="mt-4 text-sm text-amber-300">
            Paper order history is unavailable.
          </p>
        ) : !complete ? (
          <p role="status" className="mt-4 rounded-xl border border-amber-400/20 p-3 text-sm text-amber-200">
            Completeness not verified. Received {records.length}
            {advertisedTotal !== null
              ? ` of ${advertisedTotal} reported records.`
              : " records; total count unavailable."}
            {" "}CSV export is disabled until the response is complete.
          </p>
        ) : (
          <p className="mt-4 text-sm text-emerald-300">
            Complete API response: {records.length} owner-scoped records.
          </p>
        )}
      </div>

      <div className="p-5 sm:p-6">
        <div className="grid gap-3 md:grid-cols-3">
          <div className="rounded-xl border border-white/[0.08] p-4">
            <p className="text-xs uppercase tracking-widest text-slate-500">
              Matching records
            </p>
            <p className="mt-2 text-2xl font-bold text-white">
              {unavailable ? "—" : filtered.length}
            </p>
          </div>
          <div className="rounded-xl border border-white/[0.08] p-4">
            <p className="text-xs uppercase tracking-widest text-slate-500">
              Buy / long records
            </p>
            <p className="mt-2 text-2xl font-bold text-emerald-300">
              {unavailable ? "—" : buyCount}
            </p>
          </div>
          <div className="rounded-xl border border-white/[0.08] p-4">
            <p className="text-xs uppercase tracking-widest text-slate-500">
              Sell / short records
            </p>
            <p className="mt-2 text-2xl font-bold text-amber-300">
              {unavailable ? "—" : sellCount}
            </p>
          </div>
        </div>

        <div className="mt-5 grid gap-3 md:grid-cols-3">
          <label className="text-xs font-semibold text-slate-400">
            Search symbol, status, or ID
            <input
              data-testid="f10-history-search"
              className="nv-input mt-2 w-full"
              type="search"
              value={search}
              onChange={event => {
                setSearch(event.target.value);
                setPage(1);
              }}
              placeholder="AAPL, executed, 123..."
            />
          </label>

          <label className="text-xs font-semibold text-slate-400">
            Status
            <select
              data-testid="f10-history-status"
              className="nv-input mt-2 w-full"
              value={statusFilter}
              onChange={event => {
                setStatusFilter(event.target.value);
                setPage(1);
              }}
            >
              <option value="all">All statuses</option>
              <option value="filled">Executed / filled</option>
              <option value="pending">Pending</option>
              <option value="closed">Closed / rejected</option>
              <option value="other">Other</option>
            </select>
          </label>

          <label className="text-xs font-semibold text-slate-400">
            Direction
            <select
              data-testid="f10-history-side"
              className="nv-input mt-2 w-full"
              value={sideFilter}
              onChange={event => {
                setSideFilter(event.target.value);
                setPage(1);
              }}
            >
              <option value="all">Buy and sell</option>
              <option value="buy">Buy / long</option>
              <option value="sell">Sell / short</option>
              <option value="other">Other</option>
            </select>
          </label>

          <label className="text-xs font-semibold text-slate-400">
            From date
            <input
              type="date"
              className="nv-input mt-2 w-full"
              value={dateFrom}
              onChange={event => {
                setDateFrom(event.target.value);
                setPage(1);
              }}
            />
          </label>

          <label className="text-xs font-semibold text-slate-400">
            Through date
            <input
              type="date"
              className="nv-input mt-2 w-full"
              value={dateTo}
              onChange={event => {
                setDateTo(event.target.value);
                setPage(1);
              }}
            />
          </label>

          <div className="flex flex-wrap items-end gap-2">
            <button
              type="button"
              onClick={resetFilters}
              className="rounded-xl border border-white/15 px-4 py-3 text-sm text-slate-200"
            >
              Clear filters
            </button>
            <button
              type="button"
              data-testid="f10-history-export"
              onClick={exportCsv}
              disabled={!complete || filtered.length === 0 || !validRange}
              className="rounded-xl bg-cyan-400 px-4 py-3 text-sm font-bold text-slate-950 disabled:opacity-40"
            >
              Export filtered CSV
            </button>
          </div>
        </div>

        {!validRange && (
          <p role="alert" className="mt-4 text-sm text-amber-300">
            The start date must be on or before the end date.
          </p>
        )}

        <p className="mt-5 text-xs leading-5 text-slate-500">
          Showing {visible.length} of {filtered.length} matching records.
          Filters and pagination operate on the full API response,
          not the eight-record Orders preview. CSV includes all
          matching records when response completeness is verified.
          The ledger does not supply an explicit currency field,
          so exported amounts have no assumed currency.
        </p>

        <div className="mt-4 space-y-3" data-testid="f10-history-records">
          {!unavailable && visible.length === 0 && (
            <p className="rounded-xl border border-white/[0.08] p-5 text-sm text-slate-400">
              No paper records match these filters.
            </p>
          )}

          {!unavailable && visible.map((row, index) => {
            const symbol = stringOf(row, "symbol") || "Unknown";
            const side = stringOf(row, "signal", "side") || "Unknown";
            const status = stringOf(row, "status") || "Recorded";
            const timestamp = stringOf(row, "timestamp");

            return (
              <article
                key={`${stringOf(row, "id")}-${index}`}
                className="rounded-2xl border border-white/[0.08] bg-white/[0.025] p-4"
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <h4 className="font-bold text-white">
                    {symbol} · {side.toUpperCase()}
                  </h4>
                  <span className="text-xs font-semibold text-cyan-200">
                    {status}
                  </span>
                </div>

                <p className="mt-2 text-xs text-slate-500">
                  {timestamp || "Timestamp unavailable"}
                  {" · "}
                  Order #{stringOf(row, "id") || "unknown"}
                </p>

                <div className="mt-4 grid gap-3 text-sm sm:grid-cols-4">
                  <div>
                    <p className="text-xs text-slate-500">Quantity</p>
                    <p className="mt-1 font-semibold text-white">
                      {displayNumber(row.shares_quantity, 6)}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-500">Execution price</p>
                    <p className="mt-1 font-semibold text-white">
                      {displayNumber(row.slippage_price, 4)}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-500">Allocated capital</p>
                    <p className="mt-1 font-semibold text-white">
                      {displayNumber(row.allocated_capital)}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-500">Recorded fee</p>
                    <p className="mt-1 font-semibold text-amber-200">
                      {displayNumber(row.commission_paid)}
                    </p>
                  </div>
                </div>
              </article>
            );
          })}
        </div>

        <div className="mt-5 flex flex-wrap items-center justify-between gap-3">
          <p className="text-sm text-slate-400">
            Page {currentPage} of {pageCount}
          </p>
          <div className="flex gap-2">
            <button
              type="button"
              data-testid="f10-history-previous"
              disabled={currentPage <= 1}
              onClick={() => setPage(currentPage - 1)}
              className="rounded-xl border border-white/15 px-4 py-2 text-sm text-white disabled:opacity-35"
            >
              Previous
            </button>
            <button
              type="button"
              data-testid="f10-history-next"
              disabled={currentPage >= pageCount}
              onClick={() => setPage(currentPage + 1)}
              className="rounded-xl border border-white/15 px-4 py-2 text-sm text-white disabled:opacity-35"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
