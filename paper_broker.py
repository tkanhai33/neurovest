"""AUTO GENERATED RUNTIME FILE"""
from stacks.portfolio.rebalance import execute_trade
from stacks.journal_ledger.ledger import save_log
from stacks.strategy.signal import generate_signal
from stacks.market_data.price import get_latest_price
from stacks.market_data.bars import get_bars
from stacks.risk.drawdown_guard import healthcheck as drawdown_healthcheck
from stacks.risk.kill_switch import is_kill_switch_active
from stacks.portfolio.allocator import calculate_position_size
import random

def healthcheck():
    return {"status": "ok"}

async def process_portfolio_output(portfolio_matrix: list, portfolio_output: dict):
    if not portfolio_output or 'signal' in portfolio_output:
        signal = portfolio_output.get('signal', 'hold')
        symbol = portfolio_output.get('symbol', 'UNKNOWN')

        # Check risk boundaries (synchronous checks)
        mock_portfolio_equity = 100000.00
        drawdown_status = drawdown_healthcheck(mock_portfolio_equity)
        kill_switch_active = is_kill_switch_active()

        if not drawdown_status.get("status") == "ok" or kill_switch_active:
            transaction_status = "blocked_by_risk"
            await save_log({"symbol": symbol, "signal": signal, "status": transaction_status})
            return

        # Calculate position sizing using our integrated allocator module
        sizing_matrix = calculate_position_size(symbol, total_capital=mock_portfolio_equity)
        
        trade_result = execute_trade(symbol, signal)
        
        # Merge allocation metrics into the transaction logging payload
        trade_result["allocated_capital"] = sizing_matrix.get("allocated_capital")
        trade_result["allocation_percentage"] = sizing_matrix.get("allocation_percentage")
        
        # Simulate slippage
        latest_price = get_latest_price(symbol)
        slippage_percentage = random.uniform(0.01, 0.05) / 100
        if signal == 'buy':
            slippage_price = latest_price * (1 + slippage_percentage)
        else:
            slippage_price = latest_price * (1 - slippage_percentage)
        
        # Deduct transaction fees
        commission_fee = 1.00  # Flat fee of $1.00 per trade
        net_filled_capital = sizing_matrix.get("allocated_capital") - commission_fee
        
        # Update trade result with new keys
        trade_result["slippage_price"] = slippage_price
        trade_result["commission_paid"] = commission_fee
        trade_result["net_filled_capital"] = net_filled_capital
        
        await save_log(trade_result)

        # Execute trade loop over positions matrix
        for position in portfolio_matrix:
            if isinstance(position, dict) and position.get('symbol') == symbol and position.get('signal') != signal:
                new_signal = generate_signal(symbol, get_latest_price(symbol), get_bars(symbol))
                execute_trade(symbol, new_signal)
                await save_log(new_signal)
