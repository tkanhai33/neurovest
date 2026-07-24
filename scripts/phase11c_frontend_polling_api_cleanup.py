#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(".").resolve()
target = ROOT / "frontend/app/page.tsx"

if not target.exists():
    raise FileNotFoundError("Missing frontend/app/page.tsx")

text = target.read_text()

# Replace hardcoded backend URL with relative API path.
text = text.replace(
    "http://127.0.0.1:8000/api/v1/market/live-price/${cleanSymbol}",
    "/api/v1/market/live-price/${cleanSymbol}"
)

# Add safer polling dependency handling if old empty dependency exists.
text = text.replace(
'''  useEffect(() => {
    loadPrice("AAPL");
    const timer = setInterval(() => loadPrice(symbol), 30000);
    return () => clearInterval(timer);
  }, []);
''',
'''  useEffect(() => {
    loadPrice(symbol);

    const timer = setInterval(() => {
      loadPrice(symbol);
    }, 30000);

    return () => clearInterval(timer);
  }, [symbol]);
'''
)

target.write_text(text)
print("patched Phase 11C frontend polling + relative API URL")
