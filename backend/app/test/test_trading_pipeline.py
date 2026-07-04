from unittest.mock import patch
from stacks.execution.paper_broker import process_portfolio_output
from stacks.wolfden_ai.agent_router import monitor_and_process_signals

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

def test_agent_router_trips_kill_switch():
    with patch('stacks.market_data.price.get_latest_price') as mock_get_latest_price:
        mock_get_latest_price.return_value = {'symbol': 'AAPL', 'price': 150.0}

        with patch('stacks.strategy.engine.generate_strategy_decision') as mock_generate_strategy_decision:
            mock_generate_strategy_decision.side_effect = [{'signal': 'buy', 'symbol': 'AAPL'}] * 12

            with patch('stacks.risk.kill_switch.set_kill_switch') as mock_set_kill_switch, \
                 patch('stacks.execution.paper_broker.drawdown_healthcheck') as mock_drawdown_healthcheck, \
                 patch('stacks.execution.paper_broker.is_kill_switch_active') as mock_is_kill_switch_active:
                
                mock_drawdown_healthcheck.return_value = {'status': 'ok'}
                mock_is_kill_switch_active.return_value = False

                with patch('stacks.execution.paper_broker.save_log') as mock_save_log, \
                     patch('stacks.execution.paper_broker.execute_trade') as mock_execute_trade:
                    
                    for _ in range(12):
                        try:
                            monitor_and_process_signals()
                        except SystemExit as e:
                            if e.code != 0:
                                raise

                # Assert that set_kill_switch(True) is called
                assert mock_set_kill_switch.call_count == 12
                assert mock_set_kill_switch.assert_called_with(True)
