#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(".").resolve()

candidates = [
    ROOT / "frontend/app/page.tsx",
    ROOT / "frontend/src/app/page.tsx",
    ROOT / "app/page.tsx",
    ROOT / "src/app/page.tsx",
]

target = next((p for p in candidates if p.exists()), None)

if not target:
    raise FileNotFoundError("Could not find frontend page.tsx")

text = target.read_text()

component = r'''
function LivePriceCard() {
  const [symbol, setSymbol] = useState("AAPL");
  const [quote, setQuote] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function loadPrice(nextSymbol = symbol) {
    const cleanSymbol = nextSymbol.trim().toUpperCase();

    if (!cleanSymbol) return;

    setLoading(true);

    try {
      const response = await fetch(`http://127.0.0.1:8000/api/v1/market/live-price/${cleanSymbol}`, {
        cache: "no-store",
      });

      const data = await response.json();
      setQuote(data);
    } catch (error) {
      setQuote({
        status: "error",
        symbol: cleanSymbol,
        price: null,
        provider: "frontend",
        error: String(error),
      });
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadPrice("AAPL");
    const timer = setInterval(() => loadPrice(symbol), 30000);
    return () => clearInterval(timer);
  }, []);

  return (
    <section className="rounded-2xl border border-cyan-400/30 bg-slate-950/80 p-5 shadow-[0_0_30px_rgba(34,211,238,0.12)]">
      <div className="mb-4 flex items-center justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-cyan-300">Live Market Price</p>
          <h2 className="mt-1 text-2xl font-bold text-white">
            {quote?.symbol || symbol}
          </h2>
        </div>

        <div className="rounded-full border border-emerald-400/30 px-3 py-1 text-xs text-emerald-300">
          {quote?.status || "idle"}
        </div>
      </div>

      <div className="mb-4 text-4xl font-black text-white">
        {quote?.price ? `$${Number(quote.price).toFixed(2)}` : "—"}
      </div>

      <div className="mb-4 grid grid-cols-2 gap-3 text-sm">
        <div className="rounded-xl bg-slate-900/80 p-3">
          <p className="text-slate-400">Provider</p>
          <p className="font-semibold text-cyan-200">{quote?.provider || "—"}</p>
        </div>

        <div className="rounded-xl bg-slate-900/80 p-3">
          <p className="text-slate-400">Refresh</p>
          <p className="font-semibold text-cyan-200">30s</p>
        </div>
      </div>

      {quote?.error && (
        <p className="mb-3 rounded-xl border border-red-400/30 bg-red-950/40 p-3 text-xs text-red-200">
          {quote.error}
        </p>
      )}

      <div className="flex gap-2">
        <input
          value={symbol}
          onChange={(event) => setSymbol(event.target.value.toUpperCase())}
          className="min-w-0 flex-1 rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-white outline-none focus:border-cyan-400"
          placeholder="AAPL"
        />

        <button
          onClick={() => loadPrice(symbol)}
          disabled={loading}
          className="rounded-xl bg-cyan-400 px-4 py-2 text-sm font-bold text-slate-950 disabled:opacity-60"
        >
          {loading ? "Loading" : "Update"}
        </button>
      </div>
    </section>
  );
}
'''

if "function LivePriceCard()" not in text:
    insert_after = text.find("export default")
    text = text[:insert_after] + component + "\n\n" + text[insert_after:]

# Add component into first main-ish container.
if "<LivePriceCard />" not in text:
    replacements = [
        ("<main", "<main"),
        ("</main>", "      <LivePriceCard />\n    </main>"),
    ]

    if "</main>" in text:
        text = text.replace("</main>", "      <LivePriceCard />\n    </main>", 1)
    else:
        # Safe fallback: append comment if no main exists.
        text += "\n{/* TODO Phase 11B: place <LivePriceCard /> in dashboard layout */}\n"

target.write_text(text)

print(f"patched Phase 11B live price card into {target}")
