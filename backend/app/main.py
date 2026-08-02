
from uuid import NAMESPACE_URL, uuid5
from backend.app.stacks.db_runtime.database import async_session
from backend.app.stacks.journal_ledger.decision_audit_service import build_decision_audit_service
from backend.app.stacks.journal_ledger.strategy_decision_audit_adapter import StrategyDecisionAuditAdapter
from backend.app.stacks.db_runtime.database import init_db
from backend.app.stacks.db_runtime.model_registry import register_runtime_models
from backend.app.stacks.risk.risk_service import get_risk_gate_for_api
from backend.app.stacks.strategy.strategy_service import get_strategy_decision_for_api
from backend.app.stacks.portfolio.portfolio_service import get_portfolio_positions_for_api
from backend.app.stacks.strategy_candidate_sandbox.L4_runtime_orchestration.bounded_training_runtime import (
    get_training_session,
    get_training_session_for_owner,
    list_training_failures,
    list_training_health,
    list_training_sessions,
    list_training_sessions_for_owner,
    start_bounded_training_session,
    training_runtime_status,
)

from backend.app.stacks.identity_auth.api_dependencies import (
    require_authenticated_principal,
)

from backend.app.stacks.identity_auth.admin_read_dependencies import (
    AdministrativePrincipal,
    require_administrative_principal,
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
                    "allocated_capital": (
                        round(
                            float(o.allocated_capital),
                            2,
                        )
                        if o.allocated_capital is not None
                        else None
                    ),
                    "slippage_price": (
                        round(
                            float(o.slippage_price),
                            4,
                        )
                        if o.slippage_price is not None
                        else None
                    ),
                    "commission_paid": (
                        round(
                            float(o.commission_paid),
                            2,
                        )
                        if o.commission_paid is not None
                        else None
                    ),
                    "shares_quantity": (
                        round(
                            float(o.allocated_capital)
                            / float(o.slippage_price),
                            6,
                        )
                        if (
                            o.allocated_capital is not None
                            and o.slippage_price is not None
                            and float(o.slippage_price) != 0.0
                        )
                        else None
                    ),
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

# BEGIN ADMIN USER STATISTICS ENDPOINT

from datetime import UTC as _admin_stats_UTC
from datetime import datetime as _admin_stats_datetime
from datetime import timedelta as _admin_stats_timedelta

from sqlalchemy import text as _admin_stats_text


@app.get(
    "/api/v1/admin/user-stats",
    tags=["admin"],
)
async def get_administrative_user_statistics(
    principal: AdministrativePrincipal = Depends(
        require_administrative_principal
    ),
):
    """
    Return server-authoritative administrative statistics.

    Sources:
    - identity_users
    - identity_refresh_sessions
    - order_history
    - portfolio_inventory
    - snaptrade_user_credentials

    No broker calls or live execution occur.
    """

    now = _admin_stats_datetime.now(
        _admin_stats_UTC
    )

    last_24_hours = (
        now
        - _admin_stats_timedelta(
            hours=24,
        )
    )

    last_7_days = (
        now
        - _admin_stats_timedelta(
            days=7,
        )
    )

    async with async_session() as session:
        registered_users = int(
            (
                await session.execute(
                    _admin_stats_text(
                        """
                        SELECT COUNT(*)
                        FROM identity_users
                        """
                    )
                )
            ).scalar_one()
        )

        qualification_test_accounts = int(
            (
                await session.execute(
                    _admin_stats_text(
                        """
                        SELECT COUNT(*)
                        FROM identity_users
                        WHERE
                            LOWER(email_normalized)
                                LIKE '%playwright%'
                            OR LOWER(email_normalized)
                                LIKE '%objective%'
                            OR LOWER(email_normalized)
                                LIKE '%qualification%'
                            OR LOWER(email_normalized)
                                LIKE '%simulation%'
                            OR LOWER(email_normalized)
                                LIKE '%launch%'
                            OR LOWER(email_normalized)
                                LIKE '%briefing%'
                            OR LOWER(email_normalized)
                                LIKE '%test%'
                            OR LOWER(email_normalized)
                                LIKE '%example%'
                            OR LOWER(email_normalized)
                                LIKE '%neurovest.local'
                            OR LOWER(email_normalized)
                                LIKE '%qualification.invalid'
                        """
                    )
                )
            ).scalar_one()
        )

        internal_accounts = int(
            (
                await session.execute(
                    _admin_stats_text(
                        """
                        SELECT COUNT(*)
                        FROM identity_users
                        WHERE LOWER(email_normalized)
                            LIKE '%neurovest.com'
                        """
                    )
                )
            ).scalar_one()
        )

        customer_accounts = int(
            (
                await session.execute(
                    _admin_stats_text(
                        """
                        SELECT COUNT(*)
                        FROM identity_users
                        WHERE NOT (
                            LOWER(email_normalized)
                                LIKE '%playwright%'
                            OR LOWER(email_normalized)
                                LIKE '%objective%'
                            OR LOWER(email_normalized)
                                LIKE '%qualification%'
                            OR LOWER(email_normalized)
                                LIKE '%simulation%'
                            OR LOWER(email_normalized)
                                LIKE '%launch%'
                            OR LOWER(email_normalized)
                                LIKE '%briefing%'
                            OR LOWER(email_normalized)
                                LIKE '%test%'
                            OR LOWER(email_normalized)
                                LIKE '%example%'
                            OR LOWER(email_normalized)
                                LIKE '%neurovest.local'
                            OR LOWER(email_normalized)
                                LIKE '%qualification.invalid'
                            OR LOWER(email_normalized)
                                LIKE '%neurovest.com'
                        )
                        """
                    )
                )
            ).scalar_one()
        )


        active_users = int(
            (
                await session.execute(
                    _admin_stats_text(
                        """
                        SELECT COUNT(*)
                        FROM identity_users
                        WHERE is_active IS TRUE
                          AND status = 'active'
                        """
                    )
                )
            ).scalar_one()
        )

        inactive_users = int(
            (
                await session.execute(
                    _admin_stats_text(
                        """
                        SELECT COUNT(*)
                        FROM identity_users
                        WHERE is_active IS NOT TRUE
                           OR status <> 'active'
                        """
                    )
                )
            ).scalar_one()
        )

        password_reset_required = int(
            (
                await session.execute(
                    _admin_stats_text(
                        """
                        SELECT COUNT(*)
                        FROM identity_users
                        WHERE must_change_password
                            IS TRUE
                        """
                    )
                )
            ).scalar_one()
        )

        users_last_24_hours = int(
            (
                await session.execute(
                    _admin_stats_text(
                        """
                        SELECT COUNT(*)
                        FROM identity_users
                        WHERE created_at >= :boundary
                        """
                    ),
                    {
                        "boundary":
                            last_24_hours,
                    },
                )
            ).scalar_one()
        )

        users_last_7_days = int(
            (
                await session.execute(
                    _admin_stats_text(
                        """
                        SELECT COUNT(*)
                        FROM identity_users
                        WHERE created_at >= :boundary
                        """
                    ),
                    {
                        "boundary":
                            last_7_days,
                    },
                )
            ).scalar_one()
        )

        total_sessions = int(
            (
                await session.execute(
                    _admin_stats_text(
                        """
                        SELECT COUNT(*)
                        FROM identity_refresh_sessions
                        """
                    )
                )
            ).scalar_one()
        )

        active_sessions = int(
            (
                await session.execute(
                    _admin_stats_text(
                        """
                        SELECT COUNT(*)
                        FROM identity_refresh_sessions
                        WHERE revoked_at IS NULL
                          AND expires_at > :now
                        """
                    ),
                    {
                        "now": now,
                    },
                )
            ).scalar_one()
        )

        users_with_active_sessions = int(
            (
                await session.execute(
                    _admin_stats_text(
                        """
                        SELECT COUNT(
                            DISTINCT user_id
                        )
                        FROM identity_refresh_sessions
                        WHERE revoked_at IS NULL
                          AND expires_at > :now
                        """
                    ),
                    {
                        "now": now,
                    },
                )
            ).scalar_one()
        )

        paper_order_count = int(
            (
                await session.execute(
                    _admin_stats_text(
                        """
                        SELECT COUNT(*)
                        FROM order_history
                        """
                    )
                )
            ).scalar_one()
        )

        executed_order_count = int(
            (
                await session.execute(
                    _admin_stats_text(
                        """
                        SELECT COUNT(*)
                        FROM order_history
                        WHERE status = 'executed'
                        """
                    )
                )
            ).scalar_one()
        )

        blocked_order_count = int(
            (
                await session.execute(
                    _admin_stats_text(
                        """
                        SELECT COUNT(*)
                        FROM order_history
                        WHERE status = 'blocked_by_risk'
                        """
                    )
                )
            ).scalar_one()
        )

        portfolio_position_count = int(
            (
                await session.execute(
                    _admin_stats_text(
                        """
                        SELECT COUNT(*)
                        FROM portfolio_inventory
                        """
                    )
                )
            ).scalar_one()
        )

        active_position_count = int(
            (
                await session.execute(
                    _admin_stats_text(
                        """
                        SELECT COUNT(*)
                        FROM portfolio_inventory
                        WHERE shares_quantity > 0
                        """
                    )
                )
            ).scalar_one()
        )

        users_with_positions = int(
            (
                await session.execute(
                    _admin_stats_text(
                        """
                        SELECT COUNT(
                            DISTINCT user_id
                        )
                        FROM portfolio_inventory
                        WHERE shares_quantity > 0
                        """
                    )
                )
            ).scalar_one()
        )

        broker_registered_users = int(
            (
                await session.execute(
                    _admin_stats_text(
                        """
                        SELECT COUNT(
                            DISTINCT neurovest_user_id
                        )
                        FROM snaptrade_user_credentials
                        """
                    )
                )
            ).scalar_one()
        )

        role_rows = (
            await session.execute(
                _admin_stats_text(
                    """
                    SELECT
                        role,
                        COUNT(*) AS total
                    FROM identity_users
                    GROUP BY role
                    ORDER BY role
                    """
                )
            )
        ).all()

        tier_rows = (
            await session.execute(
                _admin_stats_text(
                    """
                    SELECT
                        subscription_tier,
                        COUNT(*) AS total
                    FROM identity_users
                    GROUP BY subscription_tier
                    ORDER BY subscription_tier
                    """
                )
            )
        ).all()

        status_rows = (
            await session.execute(
                _admin_stats_text(
                    """
                    SELECT
                        status,
                        COUNT(*) AS total
                    FROM identity_users
                    GROUP BY status
                    ORDER BY status
                    """
                )
            )
        ).all()

    return {
        "status": "ok",
        "generated_at": now.isoformat(),
        "source": (
            "server-authoritative-postgresql"
        ),
        "users": {
            "registered": registered_users,
            "customer_accounts": customer_accounts,
            "internal_accounts": internal_accounts,
            "qualification_test_accounts":
                qualification_test_accounts,
            "active": active_users,
            "inactive": inactive_users,
            "password_reset_required":
                password_reset_required,
            "registered_last_24_hours":
                users_last_24_hours,
            "registered_last_7_days":
                users_last_7_days,
            "with_active_sessions":
                users_with_active_sessions,
            "with_positions":
                users_with_positions,
            "by_role": {
                str(role): int(total)
                for role, total in role_rows
            },
            "by_subscription_tier": {
                str(tier): int(total)
                for tier, total in tier_rows
            },
            "by_status": {
                str(status): int(total)
                for status, total in status_rows
            },
        },
        "sessions": {
            "active": active_sessions,
            "total": total_sessions,
        },
        "paper_trading": {
            "orders": paper_order_count,
            "executed_orders":
                executed_order_count,
            "risk_blocked_orders":
                blocked_order_count,
            "positions":
                portfolio_position_count,
            "active_positions":
                active_position_count,
        },
        "brokerage": {
            "registered_users":
                broker_registered_users,
            "live_execution_enabled":
                False,
        },
        "billing": {
            "configured": False,
            "monthly_revenue": None,
            "display_value":
                "Billing not configured",
            "reason": (
                "No qualified billing or payment "
                "ledger is connected."
            ),
        },
        "boundaries": {
            "paper_and_simulation_only": True,
            "live_broker_trading": False,
            "production_wide_launch": False,
        },
    }


# END ADMIN USER STATISTICS ENDPOINT


# BEGIN BOUNDED TRAINING RUNTIME API


def _training_principal_role(
    principal,
) -> str:
    role = (
        getattr(
            principal,
            "role",
            None,
        )
        or getattr(
            principal,
            "authorization_role",
            None,
        )
    )

    if role:
        return str(
            role
        ).strip().lower()

    claims = getattr(
        principal,
        "claims",
        {},
    )

    if not isinstance(
        claims,
        dict,
    ):
        claims = {}

    return str(
        claims.get(
            "authorization_role"
        )
        or claims.get("role")
        or ""
    ).strip().lower()


def _training_principal_subject(
    principal,
) -> str:
    value = (
        getattr(
            principal,
            "subject",
            None,
        )
        or getattr(
            principal,
            "user_id",
            None,
        )
    )

    if not value:
        claims = getattr(
            principal,
            "claims",
            {},
        )

        if isinstance(
            claims,
            dict,
        ):
            value = (
                claims.get("sub")
                or claims.get(
                    "user_id"
                )
            )

    normalized = str(
        value or ""
    ).strip()

    if not normalized:
        raise HTTPException(
            status_code=401,
            detail=(
                "Authenticated training subject "
                "is unavailable"
            ),
        )

    return normalized


def _training_principal_session(
    principal,
) -> str:
    value = (
        getattr(
            principal,
            "session_id",
            None,
        )
        or getattr(
            principal,
            "token_family_id",
            None,
        )
        or getattr(
            principal,
            "token_id",
            None,
        )
    )

    if not value:
        claims = getattr(
            principal,
            "claims",
            {},
        )

        if isinstance(
            claims,
            dict,
        ):
            value = (
                claims.get(
                    "session_id"
                )
                or claims.get(
                    "session_family_id"
                )
                or claims.get(
                    "family_id"
                )
                or claims.get("sid")
                or claims.get("jti")
            )

    normalized = str(
        value or ""
    ).strip()

    if not normalized:
        raise HTTPException(
            status_code=401,
            detail=(
                "Authenticated training session "
                "is unavailable"
            ),
        )

    return normalized


def _require_developer_training_role(
    principal: AdministrativePrincipal,
) -> str:
    role = _training_principal_role(
        principal
    )

    if role not in {
        "developer",
        "dev",
        "owner",
    }:
        raise HTTPException(
            status_code=403,
            detail=(
                "System-wide training requires "
                "Developer authorization"
            ),
        )

    return role


# ---------------------------------------------------------------------
# USER-SCOPED TRAINING
# ---------------------------------------------------------------------


@app.post(
    "/api/v1/training/runs",
    tags=["training"],
    status_code=202,
)
async def start_authenticated_user_training_run(
    duration_seconds: int = 120,
    universe: str = "canada",
    principal: AuthenticatedPrincipal = Depends(
        require_authenticated_principal
    ),
):
    owner_user_id = (
        _training_principal_subject(
            principal
        )
    )

    owner_session_id = (
        _training_principal_session(
            principal
        )
    )

    try:
        return start_bounded_training_session(
            duration_seconds=duration_seconds,
            universe=universe,
            requested_by=owner_user_id,
            source="authenticated_user_api",
            scope="user",
            owner_user_id=owner_user_id,
            owner_session_id=owner_session_id,
            requested_by_role=(
                _training_principal_role(
                    principal
                )
                or "user"
            ),
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error


@app.get(
    "/api/v1/training/runs",
    tags=["training"],
)
async def list_authenticated_user_training_runs(
    limit: int = 20,
    principal: AuthenticatedPrincipal = Depends(
        require_authenticated_principal
    ),
):
    return {
        "runs":
            list_training_sessions_for_owner(
                owner_user_id=(
                    _training_principal_subject(
                        principal
                    )
                ),
                owner_session_id=(
                    _training_principal_session(
                        principal
                    )
                ),
                limit=limit,
            ),
    }


@app.get(
    "/api/v1/training/runs/{run_id}",
    tags=["training"],
)
async def get_authenticated_user_training_run(
    run_id: str,
    principal: AuthenticatedPrincipal = Depends(
        require_authenticated_principal
    ),
):
    result = get_training_session_for_owner(
        run_id=run_id,
        owner_user_id=(
            _training_principal_subject(
                principal
            )
        ),
        owner_session_id=(
            _training_principal_session(
                principal
            )
        ),
    )

    if result is None:
        # Return 404 so another customer's run existence is not leaked.
        raise HTTPException(
            status_code=404,
            detail=(
                "Training session was not found"
            ),
        )

    return result


# ---------------------------------------------------------------------
# ADMIN OBSERVABILITY — NO START OR MUTATION
# ---------------------------------------------------------------------


@app.get(
    "/api/v1/admin/training/status",
    tags=["admin", "training"],
)
async def administrative_training_runtime_status(
    principal: AdministrativePrincipal = Depends(
        require_administrative_principal
    ),
):
    status = training_runtime_status()

    status[
        "administrative_permissions"
    ] = {
        "view_health": True,
        "view_failures": True,
        "start_training": False,
        "cancel_training": False,
        "modify_training": False,
    }

    return status


@app.get(
    "/api/v1/admin/training/health",
    tags=["admin", "training"],
)
async def administrative_training_health(
    limit: int = 100,
    principal: AdministrativePrincipal = Depends(
        require_administrative_principal
    ),
):
    return {
        "runs":
            list_training_health(
                limit=limit
            ),
    }


@app.get(
    "/api/v1/admin/training/failures",
    tags=["admin", "training"],
)
async def administrative_training_failures(
    limit: int = 100,
    principal: AdministrativePrincipal = Depends(
        require_administrative_principal
    ),
):
    return {
        "failures":
            list_training_failures(
                limit=limit
            ),
    }


# ---------------------------------------------------------------------
# DEVELOPER / OWNER SYSTEM-WIDE TRAINING
# ---------------------------------------------------------------------


@app.post(
    "/api/v1/developer/training/runs",
    tags=["developer", "training"],
    status_code=202,
)
async def start_developer_system_training_run(
    duration_seconds: int = 120,
    universe: str = "canada",
    principal: AdministrativePrincipal = Depends(
        require_administrative_principal
    ),
):
    role = _require_developer_training_role(
        principal
    )

    try:
        return start_bounded_training_session(
            duration_seconds=duration_seconds,
            universe=universe,
            requested_by=(
                _training_principal_subject(
                    principal
                )
            ),
            source="developer_system_api",
            scope="system",
            owner_user_id=None,
            owner_session_id=None,
            requested_by_role=role,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error


@app.get(
    "/api/v1/developer/training/runs",
    tags=["developer", "training"],
)
async def list_developer_training_runs(
    limit: int = 100,
    principal: AdministrativePrincipal = Depends(
        require_administrative_principal
    ),
):
    _require_developer_training_role(
        principal
    )

    return {
        "runs":
            list_training_sessions(
                limit=limit
            ),
    }


@app.get(
    "/api/v1/developer/training/runs/{run_id}",
    tags=["developer", "training"],
)
async def get_developer_training_run(
    run_id: str,
    principal: AdministrativePrincipal = Depends(
        require_administrative_principal
    ),
):
    _require_developer_training_role(
        principal
    )

    result = get_training_session(
        run_id
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Training session was not found"
            ),
        )

    return result


# END BOUNDED TRAINING RUNTIME API

