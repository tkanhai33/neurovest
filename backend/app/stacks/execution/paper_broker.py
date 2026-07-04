"""AUTO GENERATED RUNTIME FILE"""

from stacks.portfolio.rebalance import execute_trade  # Import the execute_trade function
from stacks.journal_ledger.ledger import save_log  # Import the save_log function
from stacks.strategy.signal import generate_signal
from stacks.market_data.price import get_latest_price
from stacks.market_data.bars import get_bars
from stacks.risk.drawdown_guard import healthcheck as drawdown_healthcheck
from stacks.risk.kill_switch import is_kill_switch_active

def healthcheck():
    return {"status": "ok"}

def process_portfolio_output(portfolio_matrix: dict, portfolio_output: dict):
    if 'signal' in portfolio_output and 'symbol' in portfolio_output:
        signal = portfolio_output['signal']
        symbol = portfolio_output['symbol']

        # Check risk boundaries
        drawdown_status = drawdown_healthcheck()
        kill_switch_active = is_kill_switch_active()

        if not drawdown_status["status"] == "ok" or kill_switch_active:
            transaction_status = "blocked_by_risk"
            save_log({"symbol": symbol, "signal": signal, "status": transaction_status})
            return

        trade_result = execute_trade(symbol, signal)  # Call the execute_trade function
        save_log(trade_result)  # Save the log using journal_ledger/ledger.py
        
        # Execute trade loop
        for position in portfolio_matrix:
            if position['symbol'] == symbol and position['signal'] != signal:
                new_signal = generate_signal(symbol, get_latest_price(symbol), get_bars(symbol))
                execute_trade(symbol, new_signal)
                save_log(new_signal)
