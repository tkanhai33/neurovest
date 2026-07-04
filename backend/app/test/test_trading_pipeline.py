import pytest
from unittest.mock import patch, MagicMock

from stacks.market_data.price import get_latest_price
from stacks.strategy.engine import generate_strategy_decision  # Import the correct function
from stacks.risk.drawdown_guard import healthcheck as drawdown_healthcheck
from stacks.risk.kill_switch import set_kill_switch, is_kill_switch_active
from stacks.journal_ledger.ledger import save_log
from stacks.market_data.bars import get_bars  # Import the get_bars function

def test_trading_pipeline_success():
    # Mock the market data service to return a dummy tick
    with patch('stacks.market_data.price.get_latest_price') as mock_get_latest_price:
        mock_get_latest_price.return_value = {'symbol': 'AAPL', 'price': 150.0}

        # Mock the strategy engine to return a dummy decision
        with patch('stacks.strategy.engine.generate_strategy_decision') as mock_generate_strategy_decision:
            mock_generate_strategy_decision.return_value = {'signal': 'buy', 'symbol': 'AAPL'}

            # Mock the risk guards
            with patch('stacks.risk.drawdown_guard.healthcheck') as mock_drawdown_healthcheck, \
                 patch('stacks.risk.kill_switch.is_kill_switch_active') as mock_is_kill_switch_active:
                mock_drawdown_healthcheck.return_value = {'status': 'ok'}
                mock_is_kill_switch_active.return_value = False

                # Mock the journal ledger to save logs
                with patch('stacks.journal_ledger.ledger.save_log') as mock_save_log:

                    # Call the function under test
                    process_portfolio_output([{'symbol': 'AAPL', 'signal': 'sell'}], {'signal': 'buy', 'symbol': 'AAPL'})

                    # Assert that the trade ledger entry is written to journal_ledger/ledger.py with status 'executed'
                    mock_save_log.assert_called_once_with({"symbol": "AAPL", "signal": "buy", "status": "executed"})

def test_trading_pipeline_blocked():
    # Mock the market data service to return a dummy tick
    with patch('stacks.market_data.price.get_latest_price') as mock_get_latest_price:
        mock_get_latest_price.return_value = {'symbol': 'AAPL', 'price': 150.0}

        # Mock the strategy engine to return a dummy decision
        with patch('stacks.strategy.engine.generate_strategy_decision') as mock_generate_strategy_decision:
            mock_generate_strategy_decision.return_value = {'signal': 'buy', 'symbol': 'AAPL'}

            # Mock the risk guards
            with patch('stacks.risk.drawdown_guard.healthcheck') as mock_drawdown_healthcheck, \
                 patch('stacks.risk.kill_switch.is_kill_switch_active') as mock_is_kill_switch_active:
                mock_drawdown_healthcheck.return_value = {'status': 'ok'}
                mock_is_kill_switch_active.return_value = True

                # Mock the journal ledger to save logs
                with patch('stacks.journal_ledger.ledger.save_log') as mock_save_log:

                    # Call the function under test
                    process_portfolio_output([{'symbol': 'AAPL', 'signal': 'sell'}], {'signal': 'buy', 'symbol': 'AAPL'})

                    # Assert that the trade ledger entry is written to journal_ledger/ledger.py with status 'blocked_by_risk'
                    mock_save_log.assert_called_once_with({"symbol": "AAPL", "signal": "buy", "status": "blocked_by_risk"})

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

def execute_trade(symbol: str, signal: str):
    # Placeholder for the actual trade execution logic
    return {"symbol": symbol, "signal": signal, "status": "executed"}

def generate_signal(symbol: str, latest_price: dict, bars: list[dict]):
    # Placeholder for the actual signal generation logic
    return {"symbol": symbol, "signal": "buy"}
