"""AUTO GENERATED RUNTIME FILE"""
from stacks.portfolio.rebalance import execute_trade
from stacks.journal_ledger.ledger import save_log, async_session, OrderHistory
from stacks.strategy.signal import generate_signal
from stacks.market_data.price import get_latest_price
from stacks.market_data.bars import get_bars
from stacks.risk.drawdown_guard import healthcheck as drawdown_healthcheck
from stacks.risk.kill_switch import is_kill_switch_active
from stacks.portfolio.allocator import calculate_position_size

async def healthcheck():
    return {"status": "ok"}

async def process_portfolio_output(portfolio_matrix: list, portfolio_output: dict):
    if not portfolio_output or 'signal' in portfolio_output:
        signal = portfolio_output.get('signal', 'hold')
        symbol = portfolio_output.get('symbol', 'UNKNOWN')

        # Pass a standard base capital parameter to our dynamic drawdown math engine
        mock_portfolio_equity = 100000.00
        drawdown_status = await drawdown_healthcheck(mock_portfolio_equity)
        kill_switch_active = is_kill_switch_active()

        if not drawdown_status.get("status") == "ok" or kill_switch_active:
            transaction_status = "blocked_by_risk"
            await save_log({"symbol": symbol, "signal": signal, "status": transaction_status})
            return

        # Calculate position size
        position_size_payload = calculate_position_size(symbol)
        
        trade_result = execute_trade(symbol, signal, **position_size_payload)
        await save_log(trade_result)

        # Execute trade loop over positions matrix
        for position in portfolio_matrix:
            if isinstance(position, dict) and position.get('symbol') == symbol and position.get('signal') != signal:
                new_signal = generate_signal(symbol, get_latest_price(symbol), get_bars(symbol))
                execute_trade(symbol, new_signal)
                await save_log(new_signal)

async def calculate_position_size(symbol: str, total_capital: float = 100000.0) -> dict:
    side = signal.get("side", "HOLD")
    if side == "BUY":
        # Get the last 5 bars for the symbol
        bars = get_bars(symbol, limit=5)
        
        # Extract closing prices from the bars
        closing_prices = [bar['close'] for bar in bars]
        
        # Calculate price range variance (Max Price minus Min Price)
        if closing_prices:
            price_range_variance = max(closing_prices) - min(closing_prices)
        else:
            price_range_variance = 0
        
        # Scale the position size inversely proportional to the price range variance
        allocation = total_capital * 0.25 / (price_range_variance + 1)  # Adding a small constant to avoid division by zero
        allocation = min(allocation, total_capital * 0.15)  # Enforce hard allocation limit of 15% of total_capital
        
    elif side == "SELL":
        allocation = 0.0
    else:
        allocation = total_capital * 0.05
    
    return {"side": side, "cash_allocated": allocation}
