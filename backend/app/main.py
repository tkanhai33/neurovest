
from uuid import NAMESPACE_URL, uuid5
from backend.app.stacks.db_runtime.database import async_session
from backend.app.stacks.journal_ledger.decision_audit_service import build_decision_audit_service
from backend.app.stacks.journal_ledger.strategy_decision_audit_adapter import StrategyDecisionAuditAdapter
from backend.app.stacks.db_runtime.database import init_db
from backend.app.stacks.db_runtime.model_registry import register_runtime_models
from backend.app.stacks.risk.risk_service import get_risk_gate_for_api
from backend.app.stacks.strategy.strategy_service import get_strategy_decision_for_api
from backend.app.stacks.portfolio.portfolio_service import get_portfolio_positions_for_api
from backend.app.stacks.identity_auth.api_dependencies import (
    require_authenticated_principal,
)
from backend.app.stacks.identity_auth.contracts import (
    AuthenticatedPrincipal,
)
from backend.app.stacks.market_data.market_data_service import get_live_market_price_for_api
from backend.app.core.global_firewall_v1 import install_global_firewall

# =========================
# ARCHITECTURE FIREWALL BOOTSTRAP (MUST BE FIRST)
# =========================
install_global_firewall()


# =========================
# CORE IMPORTS
# =========================

import json
import asyncio
import subprocess
import re

from contextlib import asynccontextmanager
from typing import Literal

from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select


# =========================
# STACK IMPORTS (CORRECT ROOT)
# =========================

from backend.app.core.cognitive_graph_state import graph_state
from backend.app.core.runtime_trace import (
    create_trace_id,
    emit_runtime_step,
)

from backend.app.stacks.journal_ledger.ledger import (
    async_session,
    OrderHistory,
    PortfolioInventory,
)

from backend.app.stacks.strategy.engine import generate_strategy_decision
from backend.app.stacks.execution.paper_broker import process_portfolio_output

from backend.app.stacks.portfolio.accounting import (
    calculate_live_portfolio_equity,
)
from backend.app.stacks.events.broker import global_event_bus
from backend.app.stacks.portfolio.reconciliation import resolve_reconciliation_owner_id
from backend.app.stacks.portfolio.reconciliation import (
    run_reconciliation_audit,
    start_periodic_reconciliation_daemon,
)


# =========================
# CHAT ROUTER
# =========================

from backend.app.stacks.chat_public.chat_api import router as chat_router
from backend.app.stacks.market_data.api_router import router as market_data_router
from backend.app.stacks.notification.api_router import router as notification_router
from backend.app.stacks.snaptrade.api_router import router as snaptrade_router
from backend.app.stacks.identity_auth.api_router import router as auth_router
from backend.app.stacks.identity_auth.route_protection import enforce_route_policy


# =========================
# CONFIG / STATE
# =========================

TICKER_WATCHLIST = ["AAPL", "NVDA", "TSLA", "MSFT"]

SANDBOX_OVERRIDE_ACTIVE = False
SANDBOX_OVERRIDE_SIGNAL = "hold"

connected_clients = set()


class PaperOrderRequest(BaseModel):
    symbol: str = Field(
        min_length=1,
        max_length=15,
    )

    action: Literal[
        "buy",
        "sell",
    ]

    @field_validator(
        "symbol",
    )
    @classmethod
    def validate_symbol(
        cls,
        value: str,
    ) -> str:
        normalized = str(
            value
        ).strip().upper()

        if not re.fullmatch(
            r"[A-Z0-9][A-Z0-9.\-]{0,14}",
            normalized,
        ):
            raise ValueError(
                "Symbol must contain only letters, numbers, dots, or hyphens."
            )

        return normalized


# =========================
# EVENT BUS HANDLER
# =========================

async def order_event_consumer(event_frame: dict):
    if event_frame.get("event_type") == "TRADE_EXECUTED":
        payload_str = json.dumps(event_frame)

        if connected_clients:
            await asyncio.gather(
                *[client.send_text(payload_str) for client in connected_clients],
                return_exceptions=True,
            )


# =========================
# LIFESPAN
# =========================

@asynccontextmanager
async def lifespan(app: FastAPI):
    daemon_task = None
    register_runtime_models()
    await init_db()

    global_event_bus.subscribe(order_event_consumer)

    reconciliation_owner_id = (
        await resolve_reconciliation_owner_id()
    )

    if reconciliation_owner_id is not None:
        start_periodic_reconciliation_daemon(
            interval_seconds=300,
            user_id=reconciliation_owner_id,
        )
    else:
        print(
            "INFO: periodic reconciliation daemon skipped: "
            "multi-owner runtime requires explicit "
            "owner-scoped reconciliation."
        )

    yield

    if daemon_task is not None:
        daemon_task.cancel()
    global_event_bus.unsubscribe(order_event_consumer)


# =========================
# FASTAPI APP
# =========================

app = FastAPI(lifespan=lifespan)

app.include_router(chat_router)
app.include_router(notification_router)
app.include_router(snaptrade_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# API ROUTES
# =========================


# =========================
# SERVICE LIVENESS
# =========================

@app.get(
    "/health/live",
    tags=["service-health"],
)
async def service_liveness() -> dict[str, object]:
    """
    Dependency-free process liveness contract.

    This endpoint confirms only that the FastAPI process is running
    and capable of serving requests. It intentionally performs no
    database, broker, market-data, Ollama, or external-service checks.
    """

    return {
        "status": "alive",
        "service": "neurovest-backend",
        "live": True,
    }


@app.get("/api/v1/graph/live")
async def get_live_graph():
    return graph_state.snapshot()


@app.get("/api/v1/dashboard/summary")
async def summary(
    principal: AuthenticatedPrincipal = Depends(
        require_authenticated_principal
    ),
):
    global SANDBOX_OVERRIDE_ACTIVE, SANDBOX_OVERRIDE_SIGNAL

    execution_results = []

    active_flag = SANDBOX_OVERRIDE_ACTIVE
    signal_action = SANDBOX_OVERRIDE_SIGNAL

    for symbol in TICKER_WATCHLIST:
        trace_id = create_trace_id("dashboard-scan")
        audit_identity = None

        await emit_runtime_step(
            trace_id=trace_id,
            event_type="STRATEGY_EVALUATION_STARTED",
            node="strategy",
            source="dashboard_summary",
            destination="strategy",
            status="active",
            symbol=symbol,
            message="Dashboard watchlist strategy evaluation started",
            layer="L2",
            stack="strategy",
        )

        if active_flag:
            decision = {
                "symbol": symbol,
                "signal": {
                    "status": "ok",
                    "action": signal_action,
                    "symbol": symbol,
                },
                "status": "rebalanced",
            }
        else:
            correlation_id = uuid5(
                NAMESPACE_URL,
                f"neurovest:dashboard-summary:{trace_id}:{symbol}",
            )

            try:
                async with async_session() as session:
                    audit_service = build_decision_audit_service(
                        session
                    )

                    audit_adapter = StrategyDecisionAuditAdapter(
                        audit_service
                    )

                    audited_decision = (
                        await audit_adapter.produce_and_audit(
                            symbol,
                            idempotency_key=(
                                f"dashboard-summary:{trace_id}:{symbol}"
                            ),
                            correlation_id=correlation_id,
                            actor="neuro",
                            source="backend.app.main.summary",
                        )
                    )

            except Exception as audit_error:
                await emit_runtime_step(
                    trace_id=trace_id,
                    event_type="STRATEGY_AUDIT_REQUIRED_FAILURE",
                    node="journal_ledger",
                    source="backend.app.main.summary",
                    destination="strategy",
                    status="failed",
                    symbol=symbol,
                    message=(
                        "Strategy decision blocked because "
                        "required audit persistence failed"
                    ),
                    layer="L2",
                    stack="journal_ledger",
                )

                execution_results.append(
                    {
                        "symbol": symbol,
                        "status": "audit_required_failure",
                        "classification": (
                            "AUDIT_REQUIRED_FAIL_CLOSED"
                        ),
                        "decision_returned": False,
                        "portfolio_processing": "blocked",
                        "execution": "blocked",
                        "audit": None,
                        "trace_id": trace_id,
                        "error_type": type(
                            audit_error
                        ).__name__,
                    }
                )

                continue

            decision = dict(
                audited_decision.envelope
            )

            audit_identity = {
                "event_id": str(
                    audited_decision.audit_event.draft.event_id
                ),
                "sequence_number": (
                    audited_decision.audit_event.sequence_number
                ),
                "content_hash": (
                    audited_decision.audit_event.content_hash
                ),
                "correlation_id": str(
                    audited_decision.audit_event.draft.correlation_id
                ),
                "event_type": (
                    audited_decision.audit_event.draft.event_type.value
                ),
                "outcome": (
                    audited_decision.audit_event.draft.outcome.value
                ),
            }

        if decision and decision.get("status") == "rebalanced":

            mock_matrix = [
                {"symbol": symbol, "signal": decision.get("signal", "hold")}
            ]

            await emit_runtime_step(
                trace_id=trace_id,
                event_type="STRATEGY_DECISION_COMPLETE",
                node="strategy",
                status="completed",
                symbol=symbol,
                message="Strategy produced a rebalance decision",
                layer="L2",
                stack="strategy",
            )

            await process_portfolio_output(
                mock_matrix,
                decision,
                user_id=principal.subject,
                trace_id=trace_id,
            )

            execution_results.append(
                {
                    "symbol": symbol,
                    "status": "processed",
                    "execution": "paper_broker",
                    "trace_id": trace_id,
                    "audit": audit_identity,
                }
            )
        else:
            await emit_runtime_step(
                trace_id=trace_id,
                event_type="STRATEGY_NO_ACTION",
                node="strategy",
                status="completed",
                symbol=symbol,
                message="Strategy produced no executable action",
                layer="L2",
                stack="strategy",
            )

            execution_results.append(
                {
                    "symbol": symbol,
                    "status": "no_action",
                    "trace_id": trace_id,
                    "audit": audit_identity,
                }
            )

    return {
        "status": "watchlist_scan_complete",
        "results": execution_results,
    }


@app.post("/api/v1/sandbox/signal")
async def set_sandbox_override(action: str):
    global SANDBOX_OVERRIDE_ACTIVE, SANDBOX_OVERRIDE_SIGNAL

    if action.lower() in ["buy", "sell"]:
        SANDBOX_OVERRIDE_ACTIVE = True
        SANDBOX_OVERRIDE_SIGNAL = action.lower()

        return {
            "sandbox_mode": "enabled",
            "forced_action": SANDBOX_OVERRIDE_SIGNAL,
        }

    SANDBOX_OVERRIDE_ACTIVE = False

    return {
        "sandbox_mode": "disabled",
        "info": "Reset to live strategy metrics",
    }


@app.post("/api/v1/sandbox/audit")
async def trigger_sandbox_audit():
    trace_id = create_trace_id("reconciliation")
    results = await run_reconciliation_audit(
        trace_id=trace_id,

        user_id=principal.subject,
    )
    return {
        "sandbox_audit_status": "complete",
        "trace_id": trace_id,
        "log_metrics": results,
    }


@app.post("/api/v1/admin/backup")
async def force_system_backup():
    try:
        result = subprocess.run(
            ["/bin/bash", "/home/tkanhai/Neurovest/backend/scripts/backup_db.sh"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            return {
                "backup_status": "success",
                "message": result.stdout.strip(),
            }

        return {
            "backup_status": "failed",
            "error": result.stderr.strip(),
        }

    except Exception as e:
        return {
            "backup_status": "error",
            "message": str(e),
        }


@app.get("/api/v1/portfolio/valuation")
async def get_authenticated_portfolio_valuation(
    principal: AuthenticatedPrincipal = Depends(
        require_authenticated_principal
    ),
):
    valuation = await calculate_live_portfolio_equity(
        user_id=principal.subject
    )

    return {
        "starting_capital": round(
            float(
                valuation.get(
                    "starting_capital",
                    0.0,
                )
            ),
            2,
        ),
        "current_cash_balance": round(
            float(
                valuation.get(
                    "current_cash_balance",
                    0.0,
                )
            ),
            2,
        ),
        "total_fees_paid": round(
            float(
                valuation.get(
                    "total_fees_paid",
                    0.0,
                )
            ),
            2,
        ),
        "net_liquidation_value": round(
            float(
                valuation.get(
                    "net_liquidation_value",
                    0.0,
                )
            ),
            2,
        ),
        "valuation_basis": "cash_ledger",
        "live_market_marking": False,
        **(
            {
                "error": str(
                    valuation["error"]
                )
            }
            if valuation.get(
                "error"
            )
            else {}
        ),
    }


@app.get("/api/v1/positions")
async def get_active_positions(
    principal: AuthenticatedPrincipal = Depends(
        require_authenticated_principal
    ),
):
    async with async_session() as session:
        result = await session.execute(select(
                PortfolioInventory
            ).where(
                PortfolioInventory.user_id
                == principal.subject
            ))
        positions = result.scalars().all()

        position_list = [
            {
                "id": pos.id,
                "symbol": pos.symbol,
                "shares_quantity": round(pos.shares_quantity, 4),
                "average_entry_price": round(pos.average_entry_price, 2),
                "total_cost_basis": round(pos.total_cost_basis, 2),
                "realized_pnl": round(pos.realized_pnl, 2),
                "last_updated": pos.last_updated.isoformat()
                if pos.last_updated
                else None,
            }
            for pos in positions
        ]

        return {
            "active_exposure_count": len(
                [p for p in position_list if p["shares_quantity"] > 0]
            ),
            "positions": position_list,
        }


@app.get("/api/v1/orders")
async def get_orders(
    principal: AuthenticatedPrincipal = Depends(
        require_authenticated_principal
    ),
):
    async with async_session() as session:
        result = await session.execute(
            select(
                OrderHistory
            ).where(
                OrderHistory.user_id
                == principal.subject
            ).order_by(OrderHistory.id.desc())
        )
        orders = result.scalars().all()

        return {
            "total_records": len(orders),
            "orders": [
                {
                    "id": o.id,
                    "symbol": o.symbol,
                    "signal": o.signal,
                    "status": o.status,
                    "timestamp": o.timestamp.isoformat(),
                }
                for o in orders
            ],
        }


@app.get("/api/v1/analytics")
async def get_analytics(
    principal: AuthenticatedPrincipal = Depends(
        require_authenticated_principal
    ),
):
    async with async_session() as session:
        result = await session.execute(select(
                OrderHistory
            ).where(
                OrderHistory.user_id
                == principal.subject
            ))
        all_records = result.scalars().all()

        total_trades = len(all_records)

        if total_trades == 0:
            return {
                "total_trades_logged": 0,
                "buy_signals_count": 0,
                "sell_signals_count": 0,
                "risk_blocked_percentage": 0.0,
                "execution_success_percentage": 0.0,
            }

        buys = sum(
            1
            for o in all_records
            if o.signal and str(o.signal).lower() in ["buy", "long"]
        )
        sells = sum(
            1
            for o in all_records
            if o.signal and str(o.signal).lower() in ["sell", "short"]
        )
        blocked = sum(1 for o in all_records if o.status == "blocked_by_risk")
        executed = sum(1 for o in all_records if o.status == "executed")

        return {
            "total_trades_logged": total_trades,
            "buy_signals_count": buys,
            "sell_signals_count": sells,
            "risk_blocked_percentage": round(
                (blocked / total_trades) * 100, 2
            ),
            "execution_success_percentage": round(
                (executed / total_trades) * 100, 2
            ),
        }


@app.post("/api/v1/paper/orders")
async def submit_authenticated_paper_order(
    request: PaperOrderRequest,
    principal: AuthenticatedPrincipal = Depends(
        require_authenticated_principal
    ),
):
    trace_id = create_trace_id(
        "authenticated-paper-order"
    )

    symbol = request.symbol
    action = request.action

    portfolio_matrix = [
        {
            "symbol": symbol,
            "signal": action,
        }
    ]

    portfolio_output = {
        "symbol": symbol,
        "signal": action,
        "status": "rebalanced",
        "execution_mode": "paper",
        "source": "authenticated_user_order",
    }

    try:
        await process_portfolio_output(
            portfolio_matrix,
            portfolio_output,
            user_id=principal.subject,
            trace_id=trace_id,
        )
    except ExecutionBlockedError as error:
        raise HTTPException(
            status_code=409,
            detail={
                "status": "blocked",
                "reason": "paper_execution_not_allowed",
                "message": str(error),
                "execution_mode": "paper",
                "live_execution": False,
                "owner_scope": "authenticated_account",
                "trace_id": trace_id,
            },
        ) from error

    return {
        "status": "processed",
        "symbol": symbol,
        "action": action,
        "execution_mode": "paper",
        "live_execution": False,
        "owner_scope": "authenticated_account",
        "trace_id": trace_id,
    }


@app.websocket("/api/v1/stream/orders")
async def websocket_orders_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_clients.remove(websocket)


@app.get("/api/v1/market/live-price/{symbol}")
async def api_live_market_price(symbol: str):
    return await get_live_market_price_for_api(symbol)


@app.get("/api/v1/portfolio/positions")
async def api_portfolio_positions(
    principal: AuthenticatedPrincipal = Depends(
        require_authenticated_principal
    ),
):
    return await get_portfolio_positions_for_api(
        principal
    )


@app.get("/api/v1/strategy/decision/{symbol}")
async def api_strategy_decision(symbol: str):
    return await get_strategy_decision_for_api(symbol)


@app.get("/api/v1/risk/gate/{symbol}")
async def api_risk_gate(symbol: str):
    return await get_risk_gate_for_api(symbol)

# Read-only canonical market-data runtime.
app.include_router(market_data_router)
app.include_router(auth_router)
app.middleware("http")(enforce_route_policy)

# WORKSTREAM 3 STAGE 9D-C2 ADMINISTRATIVE ROUTER START
from backend.app.stacks.identity_auth.admin_read_router import (
    router as administrative_read_router,
)

app.include_router(
    administrative_read_router
)
# WORKSTREAM 3 STAGE 9D-C2 ADMINISTRATIVE ROUTER END

# WORKSTREAM 3 STAGE 9D-C5-B ADMIN MUTATION ROUTER START
from backend.app.stacks.identity_auth.admin_mutation_router import (
    router as administrative_mutation_router,
)

app.include_router(
    administrative_mutation_router
)
# WORKSTREAM 3 STAGE 9D-C5-B ADMIN MUTATION ROUTER END

# BEGIN NEUROVEST AUTHENTICATED OWNER-SCOPED READONLY PORTFOLIO API

from backend.app.spine.L5_api.owned_readonly_portfolio_service import (
    AuthenticatedPortfolioAccessDenied,
    AuthenticatedPortfolioUnavailable,
    build_owned_facade,
    serialize_accounts,
    serialize_balances,
    serialize_overview,
    serialize_positions,
    serialize_symbol_positions,
    serialize_totals,
)


def _owned_portfolio_facade_for_principal(
    principal,
):
    try:
        return build_owned_facade(
            neurovest_user_id=str(
                principal.subject
            ),
        )
    except AuthenticatedPortfolioAccessDenied as error:
        raise HTTPException(
            status_code=403,
            detail=str(
                error
            ),
        ) from error
    except AuthenticatedPortfolioUnavailable as error:
        raise HTTPException(
            status_code=503,
            detail=str(
                error
            ),
        ) from error


@app.get(
    "/api/v1/portfolio/readonly",
    tags=["portfolio"],
)
async def authenticated_owned_portfolio_overview(
    principal: AuthenticatedPrincipal = Depends(require_authenticated_principal),
):
    facade = _owned_portfolio_facade_for_principal(
        principal
    )

    return {
        "status": "ok",
        "read_only": True,
        "paper_only": True,
        "trading_enabled": False,
        "order_operations_enabled": False,
        "overview": serialize_overview(
            facade
        ),
    }


@app.get(
    "/api/v1/portfolio/readonly/accounts",
    tags=["portfolio"],
)
async def authenticated_owned_portfolio_accounts(
    principal: AuthenticatedPrincipal = Depends(require_authenticated_principal),
):
    facade = _owned_portfolio_facade_for_principal(
        principal
    )

    return {
        "status": "ok",
        "read_only": True,
        "accounts": serialize_accounts(
            facade
        ),
    }


@app.get(
    "/api/v1/portfolio/readonly/balances",
    tags=["portfolio"],
)
async def authenticated_owned_portfolio_balances(
    principal: AuthenticatedPrincipal = Depends(require_authenticated_principal),
):
    facade = _owned_portfolio_facade_for_principal(
        principal
    )

    return {
        "status": "ok",
        "read_only": True,
        "balances": serialize_balances(
            facade
        ),
    }


@app.get(
    "/api/v1/portfolio/readonly/positions",
    tags=["portfolio"],
)
async def authenticated_owned_portfolio_positions(
    principal: AuthenticatedPrincipal = Depends(require_authenticated_principal),
):
    facade = _owned_portfolio_facade_for_principal(
        principal
    )

    return {
        "status": "ok",
        "read_only": True,
        "positions": serialize_positions(
            facade
        ),
    }


@app.get(
    "/api/v1/portfolio/readonly/positions/{symbol}",
    tags=["portfolio"],
)
async def authenticated_owned_portfolio_symbol_positions(
    symbol: str,
    principal: AuthenticatedPrincipal = Depends(require_authenticated_principal),
):
    facade = _owned_portfolio_facade_for_principal(
        principal
    )

    return {
        "status": "ok",
        "read_only": True,
        "symbol": symbol.strip().upper(),
        "positions": serialize_symbol_positions(
            facade,
            symbol,
        ),
    }


@app.get(
    "/api/v1/portfolio/readonly/totals",
    tags=["portfolio"],
)
async def authenticated_owned_portfolio_totals(
    principal: AuthenticatedPrincipal = Depends(require_authenticated_principal),
):
    facade = _owned_portfolio_facade_for_principal(
        principal
    )

    return {
        "status": "ok",
        "read_only": True,
        "totals": serialize_totals(
            facade
        ),
    }

# END NEUROVEST AUTHENTICATED OWNER-SCOPED READONLY PORTFOLIO API

# BEGIN NEUROVEST PORTFOLIO SNAPSHOT LIFECYCLE API

from backend.app.stacks.portfolio.portfolio_snapshot_lifecycle import (
    PortfolioRefreshInProgress,
    PortfolioSnapshotLifecycleError,
    get_portfolio_lifecycle,
    refresh_portfolio_snapshot,
)

from backend.app.stacks.execution.execution_control import (
    ExecutionBlockedError,
)


@app.get(
    "/api/v1/portfolio/readonly/lifecycle",
    tags=["portfolio"],
)
async def authenticated_portfolio_snapshot_lifecycle(
    principal: AuthenticatedPrincipal = Depends(
        require_authenticated_principal
    ),
):
    try:
        return get_portfolio_lifecycle(
            neurovest_user_id=str(
                principal.subject
            ),
        )
    except AuthenticatedPortfolioAccessDenied as error:
        raise HTTPException(
            status_code=403,
            detail=str(
                error
            ),
        ) from error
    except PortfolioSnapshotLifecycleError as error:
        raise HTTPException(
            status_code=503,
            detail=str(
                error
            ),
        ) from error


@app.post(
    "/api/v1/portfolio/readonly/refresh",
    tags=["portfolio"],
)
async def authenticated_portfolio_snapshot_refresh(
    principal: AuthenticatedPrincipal = Depends(
        require_authenticated_principal
    ),
):
    try:
        return refresh_portfolio_snapshot(
            neurovest_user_id=str(
                principal.subject
            ),
        )
    except AuthenticatedPortfolioAccessDenied as error:
        raise HTTPException(
            status_code=403,
            detail=str(
                error
            ),
        ) from error
    except PortfolioRefreshInProgress as error:
        raise HTTPException(
            status_code=409,
            detail=str(
                error
            ),
        ) from error
    except PortfolioSnapshotLifecycleError as error:
        raise HTTPException(
            status_code=503,
            detail=str(
                error
            ),
        ) from error

# END NEUROVEST PORTFOLIO SNAPSHOT LIFECYCLE API



