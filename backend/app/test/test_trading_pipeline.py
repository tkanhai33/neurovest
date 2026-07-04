from unittest.mock import patch
from stacks.execution.paper_broker import process_portfolio_output

def test_trading_pipeline_success():
    with patch('stacks.market_data.price.get_latest_price') as mock_get_latest_price:
        mock_get_latest_price.return_value = {'symbol': 'AAPL', 'price': 150.0}

        with patch('stacks.strategy.engine.generate_strategy_decision') as mock_generate_strategy_decision:
            mock_generate_strategy_decision.return_value = {'signal': 'buy', 'symbol': 'AAPL'}

            with patch('stacks.execution.paper_broker.drawdown_healthcheck') as mock_drawdown_healthcheck, \
                 patch('stacks.execution.paper_broker.is_kill_switch_active') as mock_is_kill_switch_active:
                
                mock_drawdown_healthcheck.return_value = {'status': 'ok'}
                mock_is_kill_switch_active.return_value = False

                with patch('stacks.execution.paper_broker.save_log') as mock_save_log, \
                     patch('stacks.execution.paper_broker.execute_trade') as mock_execute_trade:
                    
                    mock_execute_trade.return_value = {'symbol': 'AAPL', 'signal': 'buy', 'status': 'executed'}

                    process_portfolio_output([{'symbol': 'AAPL', 'signal': 'sell'}], {'signal': 'buy', 'symbol': 'AAPL'})
                    
                    mock_save_log.assert_any_call({'symbol': 'AAPL', 'signal': 'buy', 'status': 'executed'})

def test_trading_pipeline_blocked():
    with patch('stacks.market_data.price.get_latest_price') as mock_get_latest_price:
        mock_get_latest_price.return_value = {'symbol': 'AAPL', 'price': 150.0}

        with patch('stacks.strategy.engine.generate_strategy_decision') as mock_generate_strategy_decision:
            mock_generate_strategy_decision.return_value = {'signal': 'buy', 'symbol': 'AAPL'}

            with patch('stacks.execution.paper_broker.drawdown_healthcheck') as mock_drawdown_healthcheck, \
                 patch('stacks.execution.paper_broker.is_kill_switch_active') as mock_is_kill_switch_active:
                
                mock_drawdown_healthcheck.return_value = {'status': 'ok'}
                mock_is_kill_switch_active.return_value = True

                with patch('stacks.execution.paper_broker.save_log') as mock_save_log:

                    process_portfolio_output([{'symbol': 'AAPL', 'signal': 'sell'}], {'signal': 'buy', 'symbol': 'AAPL'})
                    
                    mock_save_log.assert_called_once_with({"symbol": "AAPL", "signal": "buy", "status": "blocked_by_risk"})
