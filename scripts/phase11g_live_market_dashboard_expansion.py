#!/usr/bin/env python3
from pathlib import Path

p = Path("frontend/app/page.tsx")
text = p.read_text()

watchlist_component = r'''
type WatchlistQuote = LiveQuote & {
  symbol: string;
};

const WATCHLIST_SYMBOLS = ["AAPL", "MSFT", "NVDA", "TSLA", "RY.TO", "TD.TO"];

function LiveMarketWatchlist() {
  const [quotes, setQuotes] = useState<Record<string, WatchlistQuote>>({});
  const [loading, setLoading] = useState(false);

  const loadWatchlist = useCallback(async () => {
    setLoading(true);

    try {
      const results = await Promise.all(
        WATCHLIST_SYMBOLS.map(async (symbol) => {
          const response = await fetch(`/api/v1/market/live-price/${symbol}`, {
            cache: "no-store",
          });

          const data = await response.json();

          return [
            symbol,
            {
              symbol,
              ...data,
            },
          ] as const;
        })
      );

      setQuotes(Object.fromEntries(results));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const firstLoad = setTimeout(() => {
      void loadWatchlist();
    }, 0);

    const timer = setInterval(() => {
      void loadWatchlist();
    }, 30000);

    return () => {
      clearTimeout(firstLoad);
      clearInterval(timer);
    };
  }, [loadWatchlist]);

  return (
    <section className="mt-6 rounded-2xl border border-cyan-400/30 bg-slate-950/80 p-5 shadow-[0_0_30px_rgba(34,211,238,0.12)]">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-cyan-300">Live Watchlist</p>
          <h2 className="mt-1 text-2xl font-bold text-white">Market Pulse</h2>
        </div>

        <button
          onClick={() => void loadWatchlist()}
          disabled={loading}
          className="rounded-xl bg-cyan-400 px-4 py-2 text-sm font-bold text-slate-950 disabled:opacity-60"
        >
          {loading ? "Refreshing" : "Refresh"}
        </button>
      </div>

      <div className="grid gap-3 md:grid-cols-3">
        {WATCHLIST_SYMBOLS.map((symbol) => {
          const quote = quotes[symbol];

          return (
            <div key={symbol} className="rounded-xl border border-slate-700 bg-slate-900/80 p-4">
              <div className="flex items-center justify-between">
                <p className="font-bold text-white">{symbol}</p>
                <span className="rounded-full border border-emerald-400/30 px-2 py-1 text-xs text-emerald-300">
                  {quote?.status || "idle"}
                </span>
              </div>

              <p className="mt-3 text-2xl font-black text-white">
                {quote?.price ? `$${Number(quote.price).toFixed(2)}` : "—"}
              </p>

              <p className="mt-2 text-xs text-slate-400">
                Provider: {quote?.provider || "—"}
              </p>
            </div>
          );
        })}
      </div>
    </section>
  );
}
'''

if "function LiveMarketWatchlist()" not in text:
    text = text.replace("export default", watchlist_component + "\n\nexport default")

if "<LiveMarketWatchlist />" not in text:
    text = text.replace("<LivePriceCard />", "<LivePriceCard />\n      <LiveMarketWatchlist />", 1)

p.write_text(text)
print("patched Phase 11G live market watchlist expansion")
