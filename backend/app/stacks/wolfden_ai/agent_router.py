"""DOMAIN_LOGIC_V1 fallback for wolfden_ai."""
from backend.app.stacks.wolfden_ai.local_model_contract import (
    LocalModelInvoker,
    build_local_model_request,
    invoke_approved_local_model,
)


import time
from backend.app.stacks.strategy.engine import generate_strategy_decision
from backend.app.stacks.wolfden_ai.portfolio_output_result_facade import build_portfolio_output_result
from backend.app.stacks.risk.drawdown_guard import healthcheck as drawdown_healthcheck
from backend.app.stacks.risk.kill_switch import set_kill_switch, is_kill_switch_active
from backend.app.stacks.wolfden_ai.observability_boundary import record_wolfden_observation

async def _monitor_and_process_signals_core():
    # Rolling tracker variables
    signal_counts = 0
    start_time = time.time()

    while not is_kill_switch_active():
        try:
            strategy_output = generate_strategy_decision('AAPL')
            signal_counts += 1

            # Simple Anomaly Threshold check
            if time.time() - start_time < 60 and signal_counts > 10:
                print("Anomaly Detected: Signal frequency ceiling breached! Tripping Kill Switch.")
                set_kill_switch(True)
                await record_wolfden_observation({"symbol": "SYSTEM", "signal": "KILL", "status": "ANOMALY_LOOP"})
                break

            # Handle our async risk checks smoothly
            mock_portfolio_equity = 100000.00
            drawdown_status = await drawdown_healthcheck(mock_portfolio_equity)
            if drawdown_status.get("status") != "ok":
                print("Risk Alert: Drawdown limits breached inside monitor thread.")
                break

            mock_matrix = [{'symbol': 'AAPL', 'signal': 'sell'}]
            await build_portfolio_output_result(mock_matrix, strategy_output)

        except Exception as e:
            print(f"Exception Intercepted: {str(e)}")
            set_kill_switch(True)
            break

async def monitor_and_process_signals(
    *args,
    local_model_enabled: bool = False,
    local_model_invoke: LocalModelInvoker | None = None,
    **kwargs,
):
    """
    Preserve the existing Wolfden signal-processing flow.

    Advisory-model invocation remains explicit and disabled
    by default. Model failure, rejection, malformed output,
    or timeout cannot replace or prevent the protected
    Wolfden core path.
    """

    if local_model_enabled:
        request = build_local_model_request(
            args=args,
            kwargs=kwargs,
        )

        invoker = (
            local_model_invoke
            or invoke_approved_local_model
        )

        try:
            await invoker(
                request
            )

        except Exception:
            # A custom injected advisory invoker must never
            # block the protected existing Wolfden core.
            pass

    return await _monitor_and_process_signals_core(
        *args,
        **kwargs,
    )
