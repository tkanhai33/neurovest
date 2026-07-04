"""DOMAIN_LOGIC_V1 strategy engine."""

from stacks.market_data.price import get_latest_price
from stacks.market_data.bars import get_bars
from stacks.strategy.signal import generate_signal
from stacks.portfolio.rebalance import rebalance_portfolio  # Import the rebalance function

def generate_strategy_decision(symbol: str) -> dict:
    price = get_latest_price(symbol)
    bars = get_bars(symbol, limit=5)
    signal = generate_signal(symbol, price, bars)
    
    status = signal.get('status', 'not_ok')
    if status == 'ok':
        portfolio_output = rebalance_portfolio(signal)  # Call the rebalance function
        return portfolio_output
    
    return {"symbol": symbol, "signal": signal, "status": status}
