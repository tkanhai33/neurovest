# NEUROVEST GAP EVIDENCE

## FPFP
Gap

STATUS: POSSIBLY IMPLEMENTED

- frontend/next-env.d.ts:1
    /// <reference types="next" />
- frontend/next-env.d.ts:2
    /// <reference types="next/image-types/global" />
- frontend/next-env.d.ts:3
    import "./.next/types/routes.d.ts";
- frontend/next-env.d.ts:4
    
- frontend/next-env.d.ts:5
    // NOTE: This file should not be edited
- frontend/next-env.d.ts:6
    // see https://nextjs.org/docs/app/api-reference/config/typescript for more information.
- frontend/next.config.ts:1
    import type {
- frontend/next.config.ts:2
    NextConfig,
- frontend/next.config.ts:3
    } from "next";
- frontend/next.config.ts:4
    
- frontend/next.config.ts:5
    const isProduction =
- frontend/next.config.ts:6
    process.env.NODE_ENV === "production";
- frontend/next.config.ts:7
    
- frontend/next.config.ts:8
    const contentSecurityPolicy = [
- frontend/next.config.ts:9
    "default-src 'self'",

---

## FP01
No root error.tsx/error.jsx/error.js file was found.

STATUS: POSSIBLY IMPLEMENTED

- frontend/app/layout.tsx:54
    export default function RootLayout({
- backend/app/main.py:45
    # STACK IMPORTS (CORRECT ROOT)
- backend/app/core/cognitive_graph_state.py:12
    ROOT = Path(".").resolve()
- backend/app/core/cognitive_graph_state.py:13
    GRAPH_DIR = ROOT / "runtime" / "graph_history"
- backend/app/core/runtime_firewall_v1.py:5
    ROOT = Path(".").resolve()
- backend/app/core/global_firewall_v1.py:6
    ROOT = Path(".").resolve()
- backend/app/core/global_firewall_v1.py:67
    internal_roots = {
- backend/app/core/global_firewall_v1.py:83
    module_root = fullname.split(".", 1)[0]
- backend/app/core/global_firewall_v1.py:84
    if module_root not in internal_roots:
- backend/app/llm_bridge/cognition_core.py:46
    def _module_name(path: Path, repo_root: Path) -> str:
- backend/app/llm_bridge/cognition_core.py:47
    relative = path.relative_to(repo_root).with_suffix("")
- backend/app/llm_bridge/cognition_core.py:112
    root: str | Path = "backend/app",
- backend/app/llm_bridge/cognition_core.py:114
    repo_root = Path.cwd().resolve()
- backend/app/llm_bridge/cognition_core.py:115
    scan_root = Path(root)
- backend/app/llm_bridge/cognition_core.py:117
    if not scan_root.is_absolute():

---

## FP01
No root loading.tsx/loading.jsx/loading.js file was found.

STATUS: POSSIBLY IMPLEMENTED

- frontend/app/layout.tsx:54
    export default function RootLayout({
- backend/app/main.py:45
    # STACK IMPORTS (CORRECT ROOT)
- backend/app/core/cognitive_graph_state.py:12
    ROOT = Path(".").resolve()
- backend/app/core/cognitive_graph_state.py:13
    GRAPH_DIR = ROOT / "runtime" / "graph_history"
- backend/app/core/runtime_firewall_v1.py:5
    ROOT = Path(".").resolve()
- backend/app/core/global_firewall_v1.py:6
    ROOT = Path(".").resolve()
- backend/app/core/global_firewall_v1.py:67
    internal_roots = {
- backend/app/core/global_firewall_v1.py:83
    module_root = fullname.split(".", 1)[0]
- backend/app/core/global_firewall_v1.py:84
    if module_root not in internal_roots:
- backend/app/llm_bridge/cognition_core.py:46
    def _module_name(path: Path, repo_root: Path) -> str:
- backend/app/llm_bridge/cognition_core.py:47
    relative = path.relative_to(repo_root).with_suffix("")
- backend/app/llm_bridge/cognition_core.py:112
    root: str | Path = "backend/app",
- backend/app/llm_bridge/cognition_core.py:114
    repo_root = Path.cwd().resolve()
- backend/app/llm_bridge/cognition_core.py:115
    scan_root = Path(root)
- backend/app/llm_bridge/cognition_core.py:117
    if not scan_root.is_absolute():

---

## FP02
Registration rate limiting was not conclusively detected.

STATUS: POSSIBLY IMPLEMENTED

- frontend/tests/e2e/09-objective4h-b-broad-prompt-matrix.spec.ts:468
    "registration",
- frontend/tests/e2e/09-objective4h-b-broad-prompt-matrix.spec.ts:470
    "Temporary user registration",
- frontend/tests/e2e/08-objective4g-d-authenticated-live-turn.spec.ts:339
    function buildRegistrationPayload(
- frontend/tests/e2e/08-objective4g-d-authenticated-live-turn.spec.ts:752
    const registrationPayload =
- frontend/tests/e2e/08-objective4g-d-authenticated-live-turn.spec.ts:753
    buildRegistrationPayload(
- frontend/tests/e2e/08-objective4g-d-authenticated-live-turn.spec.ts:762
    const registrationResponse =
- frontend/tests/e2e/08-objective4g-d-authenticated-live-turn.spec.ts:767
    registrationPayload,
- frontend/tests/e2e/08-objective4g-d-authenticated-live-turn.spec.ts:775
    "registration",
- frontend/tests/e2e/08-objective4g-d-authenticated-live-turn.spec.ts:777
    "Temporary user registration",
- frontend/tests/e2e/08-objective4g-d-authenticated-live-turn.spec.ts:782
    registrationResponse.status(),
- frontend/tests/e2e/08-objective4g-d-authenticated-live-turn.spec.ts:787
    `HTTP ${registrationResponse.status()}`,
- frontend/tests/e2e/08-objective4g-d-authenticated-live-turn.spec.ts:794
    registrationResponse.status(),
- frontend/app/register/page.tsx:101
    "Registration is temporarily unavailable.",
- frontend/app/api/auth/register/route.ts:48
    "Registration could not be completed",
- frontend/app/api/auth/register/route.ts:75
    "Registration could not be completed",

---

## FP03
Login rate limiting was not conclusively detected.

STATUS: POSSIBLY IMPLEMENTED

- frontend/proxy.ts:204
    function loginRedirect(
- frontend/proxy.ts:207
    const loginUrl =
- frontend/proxy.ts:210
    loginUrl.pathname = "/login";
- frontend/proxy.ts:211
    loginUrl.search = "";
- frontend/proxy.ts:212
    loginUrl.searchParams.set(
- frontend/proxy.ts:218
    loginUrl,
- frontend/proxy.ts:330
    : "/login";
- frontend/proxy.ts:395
    const loginUrl =
- frontend/proxy.ts:398
    loginUrl.pathname = "/login";
- frontend/proxy.ts:399
    loginUrl.searchParams.set(
- frontend/proxy.ts:405
    loginUrl
- frontend/proxy.ts:456
    : "/login";
- frontend/proxy.ts:475
    return loginRedirect(request);
- frontend/app/page.tsx:120
    href="/login"
- frontend/app/page.tsx:162
    href="/login"

---

## FP04
The exact successful login-to-dashboard redirect was not conclusively detected.

STATUS: POSSIBLY IMPLEMENTED

- frontend/services/portfolioService.ts:141
    last_successful_refresh_at?: string | null;
- frontend/app/components/workspaces/ObservabilityWorkspacePanel.tsx:178
    const successfulRequests = metrics.reduce(
- frontend/app/components/workspaces/ObservabilityWorkspacePanel.tsx:211
    ["Requests OK", String(successfulRequests), "text-emerald-300"],
- backend/app/stacks/portfolio/portfolio_snapshot_lifecycle.py:407
    "last_successful_refresh_at"
- backend/app/stacks/portfolio/portfolio_snapshot_lifecycle.py:497
    "last_successful_refresh_at":
- backend/app/stacks/portfolio/portfolio_snapshot_lifecycle.py:499
    "last_successful_refresh_at"
- backend/app/stacks/portfolio/portfolio_snapshot_lifecycle.py:795
    "last_successful_refresh_at":
- backend/app/stacks/db_runtime/transaction_guard.py:49
    Successful scopes are unchanged. The caller remains responsible for
- backend/app/stacks/db_runtime/transaction_manager.py:68
    Successful execution order:
- backend/app/stacks/db_runtime/tests/test_transaction_guard.py:26
    async def test_guard_does_not_rollback_successful_scope() -> None:
- backend/app/stacks/identity_auth/tests/test_registration.py:15
    async def test_successful_registration():
- backend/app/stacks/identity_auth/tests/test_registration.py:16
    """Test successful registration."""

---

## FP05
No dedicated portfolio page was detected; portfolio currently appears to be embedded in the authenticated dashboard.

STATUS: POSSIBLY IMPLEMENTED

- frontend/app/page.tsx:8
    "Approved market data, portfolio context, historical observations, and strategy signals are brought together through controlled read paths.",
- frontend/app/page.tsx:12
    "Portfolio visibility",
- frontend/app/page.tsx:428
    portfolio mutation, and live trading remain unavailable until
- frontend/app/page.tsx:476
    "Gather approved market, portfolio, and account context.",
- frontend/services/portfolioService.ts:1
    export type PortfolioPosition = {
- frontend/services/portfolioService.ts:24
    export type PortfolioPositionsResponse = {
- frontend/services/portfolioService.ts:32
    positions: PortfolioPosition[];
- frontend/services/portfolioService.ts:45
    export async function getPortfolioPositions(): Promise<PortfolioPositionsResponse> {
- frontend/services/portfolioService.ts:47
    "/api/v1/portfolio/positions",
- frontend/services/portfolioService.ts:73
    : "Portfolio positions could not be loaded.";
- frontend/services/portfolioService.ts:94
    (item): item is PortfolioPosition =>
- frontend/services/portfolioService.ts:123
    // BEGIN NEUROVEST PORTFOLIO SNAPSHOT LIFECYCLE CLIENT
- frontend/services/portfolioService.ts:125
    export type PortfolioSnapshotLifecycle = {
- frontend/services/portfolioService.ts:155
    export async function getPortfolioSnapshotLifecycle(): Promise<PortfolioSnapshotLifecycle> {
- frontend/services/portfolioService.ts:157
    "/api/v1/portfolio/lifecycle",

---

## FP06
No dedicated analytics page was detected; analytics may be embedded in the authenticated dashboard.

STATUS: POSSIBLY IMPLEMENTED

- frontend/tests/e2e/06-dashboard-navigation.spec.ts:124
    test("dashboard, portfolio, and analytics render for a user", async ({
- frontend/tests/e2e/06-dashboard-navigation.spec.ts:310
    const analyticsControl =
- frontend/tests/e2e/06-dashboard-navigation.spec.ts:313
    /analytics|performance|insights/i,
- frontend/tests/e2e/06-dashboard-navigation.spec.ts:317
    analyticsControl,
- frontend/tests/e2e/06-dashboard-navigation.spec.ts:318
    "No visible Analytics, Performance, or Insights navigation control was found",
- frontend/tests/e2e/06-dashboard-navigation.spec.ts:321
    await analyticsControl!.click();
- frontend/tests/e2e/06-dashboard-navigation.spec.ts:331
    "Analytics view",
- frontend/tests/e2e/06-dashboard-navigation.spec.ts:334
    const analyticsText = (
- frontend/tests/e2e/06-dashboard-navigation.spec.ts:339
    analyticsText,
- frontend/tests/e2e/06-dashboard-navigation.spec.ts:340
    "Analytics view does not contain analytics-related content",
- frontend/tests/e2e/06-dashboard-navigation.spec.ts:342
    /analytics|performance|profit|loss|pnl|return|win rate|insight/,
- frontend/tests/e2e/04-backend-connectivity.spec.ts:26
    expect(schema.paths["/api/v1/analytics"]).toBeDefined();
- frontend/app/hooks/useDashboardData.ts:12
    export type AnalyticsSummary = {
- frontend/app/hooks/useDashboardData.ts:22
    const [analytics, setAnalytics] = useState<AnalyticsSummary | null>(null);
- frontend/app/hooks/useDashboardData.ts:29
    const [portfolioResult, analyticsResponse] = await Promise.all([

---

## FP08
No dedicated strategy-analysis page was detected; the strategy surface appears to be embedded in the authenticated dashboard.

STATUS: POSSIBLY IMPLEMENTED

- backend/app/stacks/chat_public/capability_state_registry.py:161
    "Strategy-analysis runtime."

---

## FP09
No dedicated Risk Analysis page was detected; the risk surface appears to be embedded in the authenticated dashboard.

STATUS: POSSIBLY IMPLEMENTED

- frontend/app/layout.tsx:30
    "A locally powered financial intelligence platform built to observe markets, evaluate strategies, enforce risk boundaries, and expose system activity.",
- frontend/app/layout.tsx:36
    "risk governance",
- frontend/app/page.tsx:16
    eyebrow: "Strategy and Risk",
- frontend/app/page.tsx:19
    "Independent strategy and risk systems evaluate decisions before anything can progress toward an execution boundary.",
- frontend/app/page.tsx:22
    "Risk-gate enforcement",
- frontend/app/page.tsx:46
    title: "Risk governed",
- frontend/app/page.tsx:68
    "Risk",
- frontend/app/page.tsx:156
    observe markets, evaluate strategies, enforce risk boundaries,
- frontend/app/page.tsx:182
    ["Risk-governed", "Server-authoritative"],
- frontend/app/page.tsx:437
    "Risk boundaries enforced",
- frontend/app/page.tsx:481
    "Run strategy and risk assessments through controlled services.",
- frontend/services/riskService.ts:1
    export type RiskGate = {
- frontend/services/riskService.ts:10
    export async function getRiskGate(symbol: string): Promise<RiskGate> {
- frontend/services/riskService.ts:18
    gate: "risk",
- frontend/services/riskService.ts:19
    provider: "frontend_risk_service",

---

## FP10
No dedicated market-data page was detected; market data appears to be consumed by authenticated dashboard functions.

STATUS: POSSIBLY IMPLEMENTED

- frontend/app/dashboard/page.tsx:46
    "Market-data services, pricing context, and symbol-level intelligence.",
- backend/app/main.py:731
    # Read-only canonical market-data runtime.
- backend/app/stacks/chat_public/role_overlay_registry.py:131
    "Do not infer tools, permissions, broker access, market-data "
- backend/app/stacks/chat_public/capability_state_registry.py:39
    "Market-data provider registration "
- backend/app/stacks/chat_public/capability_state_registry.py:50
    "Market-data provider selection "
- backend/app/stacks/chat_public/capability_state_registry.py:61
    "Market-data runtime composition."
- backend/app/stacks/chat_public/capability_state_registry.py:71
    "Local yfinance-backed market-data provider."
- backend/app/stacks/chat_public/capability_state_registry.py:91
    "Market-data provider cache."
- backend/app/stacks/identity_auth/route_protection.py:97
    path_template='/api/v1/market-data/historical/{symbol}',
- backend/app/stacks/identity_auth/route_protection.py:102
    path_template='/api/v1/market-data/quote/{symbol}',
- backend/app/stacks/identity_auth/route_protection.py:107
    path_template='/api/v1/market-data/status',
- backend/app/stacks/market_data/provider_registry.py:2
    Canonical in-memory market-data provider registry.
- backend/app/stacks/market_data/api_router.py:2
    Read-only market-data API router.
- backend/app/stacks/market_data/api_router.py:4
    This router exposes canonical market-data DTOs through the shared
- backend/app/stacks/market_data/api_router.py:5
    market-data composition root.

---

## FP11
No direct frontend /api/v1/chat request was detected.

STATUS: POSSIBLY IMPLEMENTED

- frontend/services/chatService.ts:37
    const CHAT_ENDPOINT = "/api/v1/chat";
- frontend/tests/e2e/09-objective4h-b-broad-prompt-matrix.spec.ts:648
    `${frontendBase}/api/v1/chat`,
- frontend/tests/e2e/08-objective4g-d-authenticated-live-turn.spec.ts:950
    "/api/v1/chat",
- frontend/tests/e2e/08-objective4g-d-authenticated-live-turn.spec.ts:969
    `${frontendBase}/api/v1/chat`,
- frontend/tests/e2e/08-objective4g-d-authenticated-live-turn.spec.ts:1246
    `${frontendBase}/api/v1/chat`,
- frontend/tests/e2e/08-objective4g-d-authenticated-live-turn.spec.ts:1409
    `${frontendBase}/api/v1/chat`,
- frontend/app/api/v1/chat/route.ts:21
    "/api/v1/chat",
- backend/app/core/cognitive_graph_state.py:283
    "frontend/app/api/v1/chat/route.ts"
- backend/app/stacks/chat_public/chat_api.py:39
    @router.post("/api/v1/chat")
- backend/app/stacks/identity_auth/route_protection.py:82
    path_template='/api/v1/chat',
- backend/app/stacks/chat_public/tests/test_role_overlay_principal_dependency.py:35
    == "/api/v1/chat"

---

## FP11
Potential automatic order-submission markers were detected and require direct review.

STATUS: POSSIBLY MISSING

---

## FP12
Delete markers were detected and must be reviewed against immutable audit requirements.

STATUS: POSSIBLY IMPLEMENTED

- frontend/services/requestNormalizer.ts:65
    .finally(() => inflight.delete(cacheKey));
- frontend/app/admin/users/page.tsx:50
    | "delete";
- frontend/app/admin/users/page.tsx:192
    case "delete":
- frontend/app/admin/users/page.tsx:229
    case "delete":
- frontend/app/admin/users/page.tsx:234
    "permanently deleted."
- frontend/app/admin/users/page.tsx:337
    deleteConfirmation,
- frontend/app/admin/users/page.tsx:338
    setDeleteConfirmation,
- frontend/app/admin/users/page.tsx:646
    setDeleteConfirmation("");
- frontend/app/admin/users/page.tsx:660
    "delete" &&
- frontend/app/admin/users/page.tsx:661
    deleteConfirmation !==
- frontend/app/admin/users/page.tsx:682
    | "DELETE" = "POST";
- frontend/app/admin/users/page.tsx:702
    case "delete":
- frontend/app/admin/users/page.tsx:703
    method = "DELETE";
- frontend/app/admin/users/page.tsx:780
    "delete"
- frontend/app/admin/users/page.tsx:786
    setDeleteConfirmation("");

---

## FP12
No direct frontend journal or ledger request was detected.

STATUS: POSSIBLY IMPLEMENTED

- backend/app/main.py:4
    from backend.app.stacks.journal_ledger.decision_audit_service import build_decision_audit_service
- backend/app/main.py:5
    from backend.app.stacks.journal_ledger.strategy_decision_audit_adapter import StrategyDecisionAuditAdapter
- backend/app/main.py:54
    from backend.app.stacks.journal_ledger.ledger import (
- backend/app/main.py:281
    node="journal_ledger",
- backend/app/main.py:291
    stack="journal_ledger",
- backend/app/core/cognitive_graph_state.py:55
    "journal_ledger": {
- backend/app/core/cognitive_graph_state.py:57
    "stack": "journal_ledger",
- backend/app/core/cognitive_graph_state.py:527
    "stack": "journal_ledger",
- backend/app/core/cognitive_graph_state.py:530
    "backend/app/stacks/journal_ledger/"
- backend/app/core/cognitive_graph_state.py:936
    "journal_ledger",
- backend/app/core/cognitive_graph_state.py:984
    "journal_ledger",
- backend/app/stacks/portfolio/accounting.py:3
    from backend.app.stacks.journal_ledger.ledger import async_session, OrderHistory
- backend/app/stacks/portfolio/reconciliation.py:7
    from backend.app.stacks.journal_ledger.ledger import (
- backend/app/stacks/execution/paper_broker.py:4
    from backend.app.stacks.journal_ledger.ledger import save_log
- backend/app/stacks/wolfden_ai/observability_boundary.py:5
    journal-ledger persistence, portfolio mutation, execution, broker,

---

## FP12
Update markers were detected and must be reviewed against append-only ledger requirements.

STATUS: POSSIBLY IMPLEMENTED

- frontend/services/chatService.ts:34
    updated_at: string;
- frontend/services/chatService.ts:112
    updated_at:
- frontend/services/chatService.ts:113
    typeof parsed.updated_at === "string"
- frontend/services/chatService.ts:114
    ? parsed.updated_at
- frontend/services/chatService.ts:140
    updated_at: new Date().toISOString(),
- frontend/lib/sessionCookies.ts:87
    .update(
- frontend/services/chat/chatContracts.ts:35
    updated_at: string;
- frontend/services/chat/chatContracts.ts:77
    updated_at: string;
- frontend/services/chat/chatContracts.ts:90
    updated_at: string;
- frontend/services/chat/chatContracts.ts:129
    memory_updates: MemoryFactContract[];
- frontend/app/admin/users/page.tsx:30
    updated_at: string | null;
- frontend/app/admin/users/page.tsx:415
    const updated =
- frontend/app/admin/users/page.tsx:422
    return updated
- frontend/app/admin/users/page.tsx:425
    ...updated,
- frontend/app/admin/users/page.tsx:1069
    "Updated",

---

## FP13
Delivery status or delivery evidence was not detected.

STATUS: POSSIBLY MISSING

---

## FP13
Mark-read or acknowledgement behavior was not detected.

STATUS: POSSIBLY MISSING

---

## FP13
No decorated notification or alert backend route was mapped.

STATUS: POSSIBLY IMPLEMENTED

- backend/app/stacks/chat_public/tests/test_public_chat_controls.py:190
    def test_route_is_decorated_with_public_controls() -> None:

---

## FP13
No direct frontend notification request was detected.

STATUS: POSSIBLY IMPLEMENTED

- frontend/components/RoleAwareWorkspaceNav.tsx:60
    description: "Account, security, billing, notifications, and support",
- frontend/app/user/settings/page.tsx:31
    title: "Notifications",
- frontend/app/user/settings/page.tsx:33
    "Email, SMS, and in-application notification preferences.",
- frontend/app/user/settings/page.tsx:48
    description="Manage your account identity, security, subscription, notifications, and support access."
- frontend/app/user/settings/page.tsx:59
    session, notification, or support records are displayed.
- frontend/app/user/dashboard/page.tsx:1303
    Review account scope, subscription, security, notifications, and preferences.
- backend/app/stacks/notification/base.py:2
    STACK: notification
- backend/app/stacks/notification/base.py:8
    class NotificationContract:
- backend/app/stacks/notification/base.py:10
    Base interface for notification domain.
- backend/app/stacks/notification/base.py:20
    return {"stack": "notification", "status": "unimplemented"}

---

## FP13
Notification creation or emission was not detected.

STATUS: POSSIBLY IMPLEMENTED

- frontend/components/RoleAwareWorkspaceNav.tsx:60
    description: "Account, security, billing, notifications, and support",
- frontend/app/user/settings/page.tsx:31
    title: "Notifications",
- frontend/app/user/settings/page.tsx:33
    "Email, SMS, and in-application notification preferences.",
- frontend/app/user/settings/page.tsx:48
    description="Manage your account identity, security, subscription, notifications, and support access."
- frontend/app/user/settings/page.tsx:59
    session, notification, or support records are displayed.
- frontend/app/user/dashboard/page.tsx:1303
    Review account scope, subscription, security, notifications, and preferences.
- backend/app/stacks/notification/base.py:2
    STACK: notification
- backend/app/stacks/notification/base.py:8
    class NotificationContract:
- backend/app/stacks/notification/base.py:10
    Base interface for notification domain.
- backend/app/stacks/notification/base.py:20
    return {"stack": "notification", "status": "unimplemented"}

---

## FP13
Notification read or list behavior was not detected.

STATUS: POSSIBLY IMPLEMENTED

- frontend/components/RoleAwareWorkspaceNav.tsx:60
    description: "Account, security, billing, notifications, and support",
- frontend/app/user/settings/page.tsx:31
    title: "Notifications",
- frontend/app/user/settings/page.tsx:33
    "Email, SMS, and in-application notification preferences.",
- frontend/app/user/settings/page.tsx:48
    description="Manage your account identity, security, subscription, notifications, and support access."
- frontend/app/user/settings/page.tsx:59
    session, notification, or support records are displayed.
- frontend/app/user/dashboard/page.tsx:1303
    Review account scope, subscription, security, notifications, and preferences.
- backend/app/stacks/notification/base.py:2
    STACK: notification
- backend/app/stacks/notification/base.py:8
    class NotificationContract:
- backend/app/stacks/notification/base.py:10
    Base interface for notification domain.
- backend/app/stacks/notification/base.py:20
    return {"stack": "notification", "status": "unimplemented"}

---

## FP14
User-deletion markers were detected and require direct review.

STATUS: POSSIBLY MISSING

---

## FP15
A dedicated liveness contract was not detected.

STATUS: POSSIBLY MISSING

---

## FP16
Broker connection-portal generation was not detected.

STATUS: POSSIBLY IMPLEMENTED

- frontend/app/page.tsx:247
    ["BROKER", "LOCKED"],
- frontend/app/page.tsx:427
    Authentication remains server-authoritative. Broker execution,
- frontend/app/page.tsx:436
    "Broker execution isolated",
- frontend/app/page.tsx:562
    <p>Broker execution: Disabled</p>
- frontend/tests/e2e/08-objective4g-d-authenticated-live-turn.spec.ts:1514
    /live broker execution is enabled|can place real trades|real order was placed/i
- frontend/app/admin/page.tsx:135
    Administrative controls cannot activate broker execution.
- frontend/app/login/page.tsx:162
    "Broker and live execution disabled",
- frontend/app/dashboard/page.tsx:151
    Broker execution remains locked while simulation and read-only diagnostics are active.
- frontend/app/admin/user-stats/page.tsx:17
    "No broker connection",
- frontend/app/admin/user-stats/page.tsx:25
    "Broker connection",
- frontend/app/admin/user-stats/page.tsx:57
    description="Subscription distribution, account activity, licensing and broker eligibility."
- frontend/app/admin/user-stats/page.tsx:80
    label="Broker Eligible"
- frontend/app/components/layout/DashboardShell.tsx:90
    <p className="text-sm text-slate-300">Broker disabled</p>
- frontend/app/components/workspaces/NeuroWorkspace.tsx:96
    <MetricCard title="Broker" value="Locked" color="text-amber-300" />
- frontend/app/components/workspaces/NeuroWorkspace.tsx:109
    ["Broker Execution", "LOCKED"],

---

## FP16
Broker synchronization state was not detected.

STATUS: POSSIBLY IMPLEMENTED

- frontend/app/page.tsx:247
    ["BROKER", "LOCKED"],
- frontend/app/page.tsx:427
    Authentication remains server-authoritative. Broker execution,
- frontend/app/page.tsx:436
    "Broker execution isolated",
- frontend/app/page.tsx:562
    <p>Broker execution: Disabled</p>
- frontend/tests/e2e/08-objective4g-d-authenticated-live-turn.spec.ts:1514
    /live broker execution is enabled|can place real trades|real order was placed/i
- frontend/app/admin/page.tsx:135
    Administrative controls cannot activate broker execution.
- frontend/app/login/page.tsx:162
    "Broker and live execution disabled",
- frontend/app/dashboard/page.tsx:151
    Broker execution remains locked while simulation and read-only diagnostics are active.
- frontend/app/admin/user-stats/page.tsx:17
    "No broker connection",
- frontend/app/admin/user-stats/page.tsx:25
    "Broker connection",
- frontend/app/admin/user-stats/page.tsx:57
    description="Subscription distribution, account activity, licensing and broker eligibility."
- frontend/app/admin/user-stats/page.tsx:80
    label="Broker Eligible"
- frontend/app/components/layout/DashboardShell.tsx:90
    <p className="text-sm text-slate-300">Broker disabled</p>
- frontend/app/components/workspaces/NeuroWorkspace.tsx:96
    <MetricCard title="Broker" value="Locked" color="text-amber-300" />
- frontend/app/components/workspaces/NeuroWorkspace.tsx:109
    ["Broker Execution", "LOCKED"],

---

## FP16
Explicit encryption for broker secrets was not detected.

STATUS: POSSIBLY MISSING

---

## FP16
No decorated broker or SnapTrade backend route was mapped.

STATUS: POSSIBLY IMPLEMENTED

- backend/app/stacks/chat_public/tests/test_public_chat_controls.py:190
    def test_route_is_decorated_with_public_controls() -> None:

---

## FP16
No direct frontend broker or SnapTrade request was detected.

STATUS: POSSIBLY IMPLEMENTED

- frontend/app/page.tsx:247
    ["BROKER", "LOCKED"],
- frontend/app/page.tsx:427
    Authentication remains server-authoritative. Broker execution,
- frontend/app/page.tsx:436
    "Broker execution isolated",
- frontend/app/page.tsx:562
    <p>Broker execution: Disabled</p>
- frontend/tests/e2e/08-objective4g-d-authenticated-live-turn.spec.ts:1514
    /live broker execution is enabled|can place real trades|real order was placed/i
- frontend/app/admin/page.tsx:135
    Administrative controls cannot activate broker execution.
- frontend/app/login/page.tsx:162
    "Broker and live execution disabled",
- frontend/app/dashboard/page.tsx:151
    Broker execution remains locked while simulation and read-only diagnostics are active.
- frontend/app/admin/user-stats/page.tsx:17
    "No broker connection",
- frontend/app/admin/user-stats/page.tsx:25
    "Broker connection",
- frontend/app/admin/user-stats/page.tsx:57
    description="Subscription distribution, account activity, licensing and broker eligibility."
- frontend/app/admin/user-stats/page.tsx:80
    label="Broker Eligible"
- frontend/app/components/layout/DashboardShell.tsx:90
    <p className="text-sm text-slate-300">Broker disabled</p>
- frontend/app/components/workspaces/NeuroWorkspace.tsx:96
    <MetricCard title="Broker" value="Locked" color="text-amber-300" />
- frontend/app/components/workspaces/NeuroWorkspace.tsx:109
    ["Broker Execution", "LOCKED"],

---

## FP16
Potential broker order-execution functions were detected and require direct call-path review.

STATUS: POSSIBLY MISSING

---

## FP17
A centralized execution gate was not detected.

STATUS: POSSIBLY MISSING

---

## FP17
Explicit operating-mode transition validation was not detected.

STATUS: POSSIBLY MISSING

---

## FP17
LOCKED mode was not detected.

STATUS: POSSIBLY IMPLEMENTED

- frontend/app/page.tsx:247
    ["BROKER", "LOCKED"],
- frontend/services/graphService.ts:5
    | "blocked"
- frontend/tests/e2e/02-auth-boundary.spec.ts:30
    test("unauthenticated dashboard access is blocked", async ({ page }) => {
- frontend/tests/e2e/02-auth-boundary.spec.ts:54
    test("unauthenticated admin access is blocked", async ({ page }) => {
- frontend/services/chat/chatContracts.ts:118
    status: "ok" | "error" | "blocked";
- frontend/app/dashboard/page.tsx:151
    Broker execution remains locked while simulation and read-only diagnostics are active.
- frontend/app/admin/users/page.tsx:894
    detail="Authentication blocked"
- frontend/app/components/layout/DashboardShell.tsx:89
    <p className="mt-2 text-sm text-slate-300">Replay locked</p>
- frontend/app/components/cards/RiskGateCard.tsx:59
    {riskGate?.allowed ? "ALLOWED" : "BLOCKED"}
- frontend/app/components/workspaces/NeuroWorkspace.tsx:96
    <MetricCard title="Broker" value="Locked" color="text-amber-300" />
- frontend/app/components/workspaces/NeuroWorkspace.tsx:109
    ["Broker Execution", "LOCKED"],
- frontend/app/components/workspaces/NeuroWorkspace.tsx:110
    ["Portfolio Mutation", "LOCKED"],
- frontend/app/components/workspaces/GraphWorkspacePanel.tsx:68
    case "blocked":
- frontend/app/components/workspaces/GraphWorkspacePanel.tsx:95
    case "blocked":
- frontend/app/user/dashboard/page.tsx:84
    risk_blocked_percentage?: number;

---

## FP17
No decorated operating-mode or emergency-stop backend route was mapped.

STATUS: POSSIBLY IMPLEMENTED

- backend/app/stacks/chat_public/tests/test_public_chat_controls.py:190
    def test_route_is_decorated_with_public_controls() -> None:

---

## FP17
No direct frontend operating-mode or emergency-stop request was detected.

STATUS: POSSIBLY MISSING

---

## FP17
Operating-mode restart recovery was not detected.

STATUS: POSSIBLY MISSING

---

## FP17
SAFE mode was not detected.

STATUS: POSSIBLY IMPLEMENTED

- frontend/next.config.ts:11
    "script-src 'self' 'unsafe-inline'"
- frontend/next.config.ts:15
    : " 'unsafe-eval'"
- frontend/next.config.ts:18
    "style-src 'self' 'unsafe-inline'",
- frontend/app/page.tsx:39
    const safetyItems = [
- frontend/app/page.tsx:48
    "Frontend requests cannot bypass server-authoritative safety gates.",
- frontend/app/page.tsx:110
    <a href="#safety" className="transition hover:text-white">
- frontend/app/page.tsx:111
    Safety
- frontend/app/page.tsx:270
    {safetyItems.map((item) => (
- frontend/app/page.tsx:301
    safety, and presentation through explicit system boundaries.
- frontend/app/page.tsx:412
    id="safety"
- frontend/app/page.tsx:423
    Safety is part of the architecture.
- frontend/app/page.tsx:550
    <a href="#safety" className="hover:text-white">
- frontend/app/page.tsx:551
    Safety
- frontend/lib/requestSecurity.ts:3
    import { timingSafeEqual } from "node:crypto";
- frontend/lib/requestSecurity.ts:103
    return timingSafeEqual(

---

