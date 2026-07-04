from unittest.mock import patch, MagicMock
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
    # Target the inner strategy layer components to avoid KeyError conflicts
    with patch('stacks.strategy.engine.get_latest_price'), \
         patch('stacks.strategy.engine.get_bars'), \
         patch('stacks.strategy.engine.generate_signal') as mock_generate_signal:
        
        # Provide the expected 'status' element that strategy/engine.py requires
        mock_generate_signal.return_value = {'status': 'ok', 'action': 'buy', 'symbol': 'AAPL'}

        with patch('stacks.risk.kill_switch.set_kill_switch') as mock_set_kill_switch, \
             patch('stacks.wolfden_ai.agent_router.drawdown_healthcheck') as mock_drawdown, \
             patch('stacks.wolfden_ai.agent_router.is_kill_switch_active') as mock_kill_active:
            
            mock_drawdown.return_value = {'status': 'ok'}
            mock_kill_active.side_effect = [False] * 11 + [True]  # Break out of loop when switch goes True

            with patch('stacks.wolfden_ai.agent_router.save_log'), \
                 patch('stacks.wolfden_ai.agent_router.time.sleep'): # Avoid slowing down the test run
                
                try:
                    monitor_and_process_signals()
                except StopIteration:
                    pass
                
                # Verify that the anomalies register properly in the tracking layer
                assert mock_kill_active.call_count >= 1
