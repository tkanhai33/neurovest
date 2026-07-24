#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(".").resolve()

# Fix strategy service: engine returns dict, not always awaitable.
p = ROOT / "backend/app/stacks/strategy/strategy_service.py"
text = p.read_text()
text = text.replace(
    "result = await generate_strategy_decision(clean_symbol)",
    """result = generate_strategy_decision(clean_symbol)
        if hasattr(result, "__await__"):
            result = await result"""
)
p.write_text(text)

# Fix risk service: drawdown healthcheck requires current_balance.
p = ROOT / "backend/app/stacks/risk/risk_service.py"
text = p.read_text()
text = text.replace(
    "drawdown = await drawdown_healthcheck()",
    """drawdown = drawdown_healthcheck(100000)
        if hasattr(drawdown, "__await__"):
            drawdown = await drawdown"""
)
p.write_text(text)

print("patched strategy/risk endpoint activation repairs")
