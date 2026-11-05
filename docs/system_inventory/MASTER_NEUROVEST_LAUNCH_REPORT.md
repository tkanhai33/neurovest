# NEUROVEST MASTER LAUNCH REPORT

Generated: 2026-07-31T18:19:36.350681

## Executive Summary

Function Paths: 17
Critical Functions: 16
Require Verification: 17

---

## Function Status Matrix

| FP | Function | Implementation | Qualification | Importance |
|---:|---|---|---|---|
| 01 | PUBLIC LANDING PAGE | UNVERIFIED | UNVERIFIED | CRITICAL |
| 02 | NEW USER REGISTRATION | UNVERIFIED | UNVERIFIED | CRITICAL |
| 03 | EXISTING USER LOGIN | IMPLEMENTED — SOURCE CONFIRMATION PENDING | UNVERIFIED | CRITICAL |
| 04 | AUTHENTICATED DASHBOARD / POST-LOGIN LANDING | IMPLEMENTED — SOURCE VERIFICATION PENDING | UNVERIFIED | CRITICAL |
| 05 | PORTFOLIO | IMPLEMENTED — SOURCE VERIFICATION PENDING | UNVERIFIED | CRITICAL |
| 06 | ANALYTICS | IMPLEMENTED — SOURCE VERIFICATION PENDING | UNVERIFIED | CRITICAL |
| 07 | PAPER TRADING | IMPLEMENTED — SOURCE VERIFICATION PENDING | UNVERIFIED | CRITICAL |
| 08 | STRATEGY ANALYSIS | IMPLEMENTED — SOURCE VERIFICATION PENDING | UNVERIFIED | CRITICAL |
| 09 | RISK ANALYSIS AND RISK GATE | IMPLEMENTED — SOURCE VERIFICATION PENDING | UNVERIFIED | CRITICAL |
| 10 | MARKET DATA AND LIVE PRICE | IMPLEMENTED — SOURCE VERIFICATION PENDING | UNVERIFIED | CRITICAL |
| 11 | NEURO AI CHAT AND DECISION ENGINE | IMPLEMENTED — SOURCE VERIFICATION PENDING | UNVERIFIED | CRITICAL |
| 12 | JOURNAL, LEDGER, AUDIT, AND EVIDENCE | IMPLEMENTED — SOURCE VERIFICATION PENDING | UNVERIFIED | CRITICAL |
| 13 | NOTIFICATIONS, ALERTS, AND USER MESSAGING | IMPLEMENTED — SOURCE VERIFICATION PENDING | UNVERIFIED | HIGH |
| 14 | ADMIN CONTROL PANEL AND USER MANAGEMENT | IMPLEMENTED — SOURCE VERIFICATION PENDING | UNVERIFIED | CRITICAL |
| 15 | SYSTEM HEALTH, RUNTIME STATUS, AND OBSERVABILITY | IMPLEMENTED — SOURCE VERIFICATION PENDING | UNVERIFIED | CRITICAL |
| 16 | BROKER INTEGRATION, SNAPTRADE, AND ACCOUNT CONNECTIONS | IMPLEMENTED — SOURCE VERIFICATION PENDING | UNVERIFIED | CRITICAL |
| 17 | OPERATING MODES, SAFETY CONTROLS, AND EMERGENCY STOP | IMPLEMENTED — SOURCE VERIFICATION PENDING | UNVERIFIED | CRITICAL |

---

## Critical Function Paths

- FP01 — PUBLIC LANDING PAGE
- FP02 — NEW USER REGISTRATION
- FP03 — EXISTING USER LOGIN
- FP04 — AUTHENTICATED DASHBOARD / POST-LOGIN LANDING
- FP05 — PORTFOLIO
- FP06 — ANALYTICS
- FP07 — PAPER TRADING
- FP08 — STRATEGY ANALYSIS
- FP09 — RISK ANALYSIS AND RISK GATE
- FP10 — MARKET DATA AND LIVE PRICE
- FP11 — NEURO AI CHAT AND DECISION ENGINE
- FP12 — JOURNAL, LEDGER, AUDIT, AND EVIDENCE
- FP14 — ADMIN CONTROL PANEL AND USER MANAGEMENT
- FP15 — SYSTEM HEALTH, RUNTIME STATUS, AND OBSERVABILITY
- FP16 — BROKER INTEGRATION, SNAPTRADE, AND ACCOUNT CONNECTIONS
- FP17 — OPERATING MODES, SAFETY CONTROLS, AND EMERGENCY STOP

---

## Functions Requiring Qualification

- FP01 — PUBLIC LANDING PAGE (UNVERIFIED)
- FP02 — NEW USER REGISTRATION (UNVERIFIED)
- FP03 — EXISTING USER LOGIN (UNVERIFIED)
- FP04 — AUTHENTICATED DASHBOARD / POST-LOGIN LANDING (UNVERIFIED)
- FP05 — PORTFOLIO (UNVERIFIED)
- FP06 — ANALYTICS (UNVERIFIED)
- FP07 — PAPER TRADING (UNVERIFIED)
- FP08 — STRATEGY ANALYSIS (UNVERIFIED)
- FP09 — RISK ANALYSIS AND RISK GATE (UNVERIFIED)
- FP10 — MARKET DATA AND LIVE PRICE (UNVERIFIED)
- FP11 — NEURO AI CHAT AND DECISION ENGINE (UNVERIFIED)
- FP12 — JOURNAL, LEDGER, AUDIT, AND EVIDENCE (UNVERIFIED)
- FP13 — NOTIFICATIONS, ALERTS, AND USER MESSAGING (UNVERIFIED)
- FP14 — ADMIN CONTROL PANEL AND USER MANAGEMENT (UNVERIFIED)
- FP15 — SYSTEM HEALTH, RUNTIME STATUS, AND OBSERVABILITY (UNVERIFIED)
- FP16 — BROKER INTEGRATION, SNAPTRADE, AND ACCOUNT CONNECTIONS (UNVERIFIED)
- FP17 — OPERATING MODES, SAFETY CONTROLS, AND EMERGENCY STOP (UNVERIFIED)

---

# APPENDIX

FUNCTION PATH 01 — PUBLIC LANDING PAGE

Function status

Inventory status: INITIAL SOURCE INVENTORY COMPLETE
Implementation status: UNVERIFIED
Qualification status: UNVERIFIED
Launch importance: CRITICAL
Last verified: SOURCE SCAN REQUIRED FOR FINAL VERDICT
Evidence source: runtime/system_inventory/function_path_01_public_landing_20260729_123731/function_path_01_public_landing_inventory.json

User purpose

What the user is trying to accomplish:
Understand what NeuroVest is and enter the correct registration,
login, or authenticated application flow.

Expected outcome:
The visitor can understand the product, identify its current
capabilities and limitations, and reach the appropriate next page.

Entry point

Browser route: /
Route type: PUBLIC — VERIFY AGAINST MIDDLEWARE
Authentication required: UNVERIFIED
Expected redirect behavior: UNVERIFIED

Frontend page

Page file: frontend/app/page.tsx
Page component: LandingPage
Layout file: frontend/app/layout.tsx
Loading file: UNKNOWN
Error file: UNKNOWN
Not-found file: UNKNOWN

Page metadata

Title: NeuroVest — Controlled Market Intelligence
Description: A locally powered financial intelligence platform built to observe markets, evaluate strategies, enforce risk boundaries, and expose system activity.

Visible page layout

1. A: Platform [frontend/app/page.tsx:104]
2. A: How it works [frontend/app/page.tsx:107]
3. A: Safety [frontend/app/page.tsx:110]
4. A: Architecture [frontend/app/page.tsx:113]
5. A: Explore the platform [frontend/app/page.tsx:171]
6. H2: Guardian intelligence [frontend/app/page.tsx:228]
7. H2: Built to observe, evaluate, and explain. [frontend/app/page.tsx:295]
8. H2: Safety is part of the architecture. [frontend/app/page.tsx:422]
9. H2: Observe. Evaluate. Explain. Record. [frontend/app/page.tsx:466]
10. H2: Your market intelligence should work for you. [frontend/app/page.tsx:517]

Frontend components and local dependencies

- frontend/app/page.tsx (depth=0, client_component=False)

Navigation and calls to action

- / — INTERNAL ROUTE [frontend/app/page.tsx:82]
- #platform — PAGE ANCHOR [frontend/app/page.tsx:104]
- #how-it-works — PAGE ANCHOR [frontend/app/page.tsx:107]
- #safety — PAGE ANCHOR [frontend/app/page.tsx:110]
- #architecture — PAGE ANCHOR [frontend/app/page.tsx:113]
- /login — INTERNAL ROUTE [frontend/app/page.tsx:120]
- /register — INTERNAL ROUTE [frontend/app/page.tsx:127]
- /login — INTERNAL ROUTE [frontend/app/page.tsx:162]
- #platform — PAGE ANCHOR [frontend/app/page.tsx:172]
- /login — INTERNAL ROUTE [frontend/app/page.tsx:365]
- /login — INTERNAL ROUTE [frontend/app/page.tsx:527]
- #platform — PAGE ANCHOR [frontend/app/page.tsx:547]
- #safety — PAGE ANCHOR [frontend/app/page.tsx:550]
- #architecture — PAGE ANCHOR [frontend/app/page.tsx:553]
- /login — INTERNAL ROUTE [frontend/app/page.tsx:556]

Frontend handlers

- LandingPage — function declaration [frontend/app/page.tsx:74]

Backend or runtime dependencies

No runtime data request was identified in the scanned dependency tree.

Middleware and redirects

Middleware file: frontend/proxy.ts
Middleware status: PRESENT
Cookies referenced: neurovest_access
Headers referenced: Cache-Control, host, origin, x-forwarded-host, x-forwarded-proto, x-neurovest-csrf

Page-state inventory

Loading state detected: False
Error state detected: False
Empty state detected: False
Responsive classes detected: True
Accessibility markers detected: True

Tests

- frontend/tests/e2e/03-public-navigation.spec.ts — matched homepage

Current gaps requiring verification

- No root loading.tsx/loading.jsx/loading.js file was found.
- No root error.tsx/error.jsx/error.js file was found.

Function flow graph

[Visitor opens /]
      ↓
[Next.js page: frontend/app/page.tsx]
      ↓
[Imported landing-page components]
      ↓
[Visible navigation and call-to-action controls]
      ↓
[Frontend middleware or proxy, when applicable]
      ↓
[Login / registration / authenticated destination]
      ↓
[Next page rendered]

Final classification

Page status: UNVERIFIED
Function status: UNVERIFIED
Launch blocker: UNVERIFIED

Required manual checks

[ ] Open / in a logged-out browser
[ ] Capture a full-page desktop screenshot
[ ] Capture a full-page mobile screenshot
[ ] Click every navigation link
[ ] Verify login call to action
[ ] Verify registration call to action
[ ] Verify authenticated-user behavior
[ ] Verify all text is current and truthful
[ ] Verify no live-trading claim is displayed
[ ] Verify loading and error behavior
[ ] Verify keyboard navigation
[ ] Verify image alt text
[ ] Verify responsive layout
[ ] Run or create a landing-page Playwright test

---



---

FUNCTION PATH 02 — NEW USER REGISTRATION

Function Status

Inventory Status: INITIAL SOURCE INVENTORY COMPLETE
Implementation Status: UNVERIFIED
Qualification Status: UNVERIFIED
Launch Importance: CRITICAL
Last Updated: VERIFY FROM INVENTORY DATE
Evidence Source: runtime/system_inventory/function_path_02_new_user_registration_20260729_173933/function_path_02_new_user_registration_inventory.json

Purpose

Allow a new visitor to create a NeuroVest account using the
public registration interface.

Expected Outcome

A valid account is created using normalized identity data and a
secure password hash. The user then receives the implemented
registration response and is redirected to the verified next step.

User Journey

Visitor
  → /register
  → registration form
  → frontend validation
  → frontend request or proxy
  → backend registration route
  → duplicate-account check
  → password hashing
  → user persistence
  → registration response
  → login, onboarding, or authenticated destination

Entry Point

Browser Route: /register
Route Type: PUBLIC
Authentication Required: NO — VERIFY MIDDLEWARE
Authenticated-User Redirect: UNVERIFIED

Frontend

Page File: frontend/app/register/page.tsx
Page Component: RegisterPage
Component Type: CLIENT COMPONENT
Layout File: frontend/app/layout.tsx
Loading File: UNKNOWN
Error File: UNKNOWN

Visible Page Layout

1. H1: Create your account. [frontend/app/register/page.tsx:124]
2. P: Join the controlled NeuroVest environment and access market intelligence, portfolio visibility, risk analysis, and Neuro. [frontend/app/register/page.tsx:128]
3. P: New account [frontend/app/register/page.tsx:151]
4. H2: Register for NeuroVest [frontend/app/register/page.tsx:155]
5. LABEL: Email [frontend/app/register/page.tsx:164]
6. LABEL: Password [frontend/app/register/page.tsx:183]
7. P: Use at least 12 characters. [frontend/app/register/page.tsx:201]
8. LABEL: Confirm password [frontend/app/register/page.tsx:207]

Registration Inputs

1. Name=email; Type=email; ID=email; Placeholder=UNKNOWN; AutoComplete=email; Required=True [frontend/app/register/page.tsx:171]
2. Name=password; Type=password; ID=password; Placeholder=UNKNOWN; AutoComplete=new-password; Required=True [frontend/app/register/page.tsx:190]
3. Name=confirmation; Type=password; ID=confirmation; Placeholder=UNKNOWN; AutoComplete=new-password; Required=True [frontend/app/register/page.tsx:214]

Frontend Components and Dependencies

- frontend/app/register/page.tsx (depth=0, client_component=True)

Frontend Handlers

- RegisterPage — function [frontend/app/register/page.tsx:12]
- submit — function [frontend/app/register/page.tsx:21]
- submit — JSX event binding [frontend/app/register/page.tsx:161]

Frontend Validation

- minLength [frontend/app/register/page.tsx:195]
- minLength [frontend/app/register/page.tsx:219]
- password [frontend/app/register/page.tsx:35]
- password [frontend/app/register/page.tsx:36]
- password [frontend/app/register/page.tsx:43]
- password [frontend/app/register/page.tsx:45]
- password [frontend/app/register/page.tsx:64]
- password [frontend/app/register/page.tsx:184]
- password [frontend/app/register/page.tsx:187]
- password [frontend/app/register/page.tsx:191]
- password [frontend/app/register/page.tsx:192]
- password [frontend/app/register/page.tsx:193]
- password [frontend/app/register/page.tsx:194]
- password [frontend/app/register/page.tsx:211]
- password [frontend/app/register/page.tsx:217]
- password [frontend/app/register/page.tsx:218]
- email [frontend/app/register/page.tsx:31]
- email [frontend/app/register/page.tsx:32]
- email [frontend/app/register/page.tsx:63]
- email [frontend/app/register/page.tsx:165]
- email [frontend/app/register/page.tsx:168]
- email [frontend/app/register/page.tsx:172]
- email [frontend/app/register/page.tsx:173]
- email [frontend/app/register/page.tsx:174]
- email [frontend/app/register/page.tsx:175]
- required [frontend/app/register/page.tsx:176]
- required [frontend/app/register/page.tsx:196]
- required [frontend/app/register/page.tsx:220]

Frontend Request Path

- POST "/api/auth/register" via fetch [frontend/app/register/page.tsx:53]

Frontend API or Proxy Files

- frontend/tests/e2e/05-authenticated-user-flow.spec.ts Methods=['GET', 'POST'] Targets=['/auth/register', 'http://127.0.0.1:8000/auth/register']
- frontend/tests/e2e/08-objective4g-d-authenticated-live-turn.spec.ts Methods=['GET', 'POST'] Targets=['${backendBase}/auth/register', '/auth/register']
- frontend/app/api/auth/register/route.ts Methods=['POST'] Targets=['${BACKEND_BASE_URL}/auth/register']

Middleware

Middleware File: frontend/proxy.ts
Middleware Status: PRESENT
Cookies Referenced: neurovest_access
Headers Referenced: Cache-Control, host, origin, x-forwarded-host, x-forwarded-proto, x-neurovest-csrf
Registration Mentions: 0

Backend Route

- POST /register → register_identity [backend/app/stacks/identity_auth/api_router.py:112]
- POST /login → login_identity [backend/app/stacks/identity_auth/api_router.py:157]

Backend Function Path

- register_runtime_models lines 14-28 [backend/app/stacks/db_runtime/model_registry.py] Terms=['register']
- get_registration_api_service lines 63-77 [backend/app/stacks/identity_auth/api_dependencies.py] Terms=['registration', 'commit', 'rollback']
- get_login_api_service lines 80-94 [backend/app/stacks/identity_auth/api_dependencies.py] Terms=['commit', 'rollback']
- require_authenticated_principal lines 97-185 [backend/app/stacks/identity_auth/api_dependencies.py] Terms=['token', 'refresh']
- optional_logout_access_principal lines 188-223 [backend/app/stacks/identity_auth/api_dependencies.py] Terms=['token']
- get_required_password_change_service lines 232-245 [backend/app/stacks/identity_auth/api_dependencies.py] Terms=['password', 'commit', 'rollback', 'refresh']
- register_identity lines 117-154 [backend/app/stacks/identity_auth/api_router.py] Terms=['register', 'registration', 'password', 'email']
- login_identity lines 163-232 [backend/app/stacks/identity_auth/api_router.py] Terms=['password', 'email', 'token', 'refresh']
- change_required_password lines 240-279 [backend/app/stacks/identity_auth/api_router.py] Terms=['password']
- refresh_session lines 287-348 [backend/app/stacks/identity_auth/api_router.py] Terms=['token', 'refresh']
- logout_session lines 356-425 [backend/app/stacks/identity_auth/api_router.py] Terms=['token', 'refresh']
- register lines 62-66 [backend/app/stacks/identity_auth/api_router.py] Terms=['register', 'registration']
- login lines 72-76 [backend/app/stacks/identity_auth/api_router.py] Terms=['token']
- refresh lines 82-87 [backend/app/stacks/identity_auth/api_router.py] Terms=['token', 'refresh']
- logout lines 89-94 [backend/app/stacks/identity_auth/api_router.py] Terms=['token', 'refresh']
- mock_hash_password lines 232-252 [backend/app/stacks/identity_auth/mock_runtime.py] Terms=['password', 'hash']
- mock_verify_password lines 255-266 [backend/app/stacks/identity_auth/mock_runtime.py] Terms=['password', 'hash']
- mock_hash_refresh_token lines 269-284 [backend/app/stacks/identity_auth/mock_runtime.py] Terms=['hash', 'token', 'refresh']
- __init__ lines 47-51 [backend/app/stacks/identity_auth/mock_runtime.py] Terms=['email']
- get_by_email lines 53-59 [backend/app/stacks/identity_auth/mock_runtime.py] Terms=['email']
- create lines 61-86 [backend/app/stacks/identity_auth/mock_runtime.py] Terms=['password', 'hash', 'email']
- __init__ lines 90-95 [backend/app/stacks/identity_auth/mock_runtime.py] Terms=['refresh']
- create lines 97-123 [backend/app/stacks/identity_auth/mock_runtime.py] Terms=['hash', 'token', 'refresh']
- __init__ lines 127-131 [backend/app/stacks/identity_auth/mock_runtime.py] Terms=['commit', 'rollback']
- commit lines 133-139 [backend/app/stacks/identity_auth/mock_runtime.py] Terms=['commit']
- rollback lines 141-142 [backend/app/stacks/identity_auth/mock_runtime.py] Terms=['rollback']
- __init__ lines 146-151 [backend/app/stacks/identity_auth/mock_runtime.py] Terms=['refresh']
- issue_access_token lines 153-190 [backend/app/stacks/identity_auth/mock_runtime.py] Terms=['token']
- issue_refresh_token lines 192-229 [backend/app/stacks/identity_auth/mock_runtime.py] Terms=['token', 'refresh']
- __init__ lines 288-343 [backend/app/stacks/identity_auth/mock_runtime.py] Terms=['registration', 'password', 'hash', 'commit', 'rollback', 'token', 'refresh']
- __init__ lines 20-37 [backend/app/stacks/identity_auth/registration_service.py] Terms=['password', 'hash', 'commit', 'rollback']
- register lines 39-123 [backend/app/stacks/identity_auth/registration_service.py] Terms=['register', 'registration', 'password', 'hash', 'email', 'commit', 'rollback']
- _extract_bearer_credentials lines 283-309 [backend/app/stacks/identity_auth/route_protection.py] Terms=['token']
- _authenticate_with_durable_revocation lines 332-362 [backend/app/stacks/identity_auth/route_protection.py] Terms=['token']
- _load_identity_authorization_state lines 425-447 [backend/app/stacks/identity_auth/route_protection.py] Terms=['password']
- enforce_route_policy lines 450-859 [backend/app/stacks/identity_auth/route_protection.py] Terms=['password']
- _as_identifier lines 137-149 [backend/app/stacks/identity_auth/runtime_adapter.py] Terms=['token']
- build_authentication_runtime lines 273-343 [backend/app/stacks/identity_auth/runtime_adapter.py] Terms=['registration', 'password', 'hash', 'commit', 'rollback', 'token', 'refresh']
- authentication_runtime lines 347-364 [backend/app/stacks/identity_auth/runtime_adapter.py] Terms=['registration', 'commit', 'refresh']
- build_session_lifecycle_runtime lines 367-451 [backend/app/stacks/identity_auth/runtime_adapter.py] Terms=['hash', 'commit', 'rollback', 'token', 'refresh']
- issue_access_token lines 192-230 [backend/app/stacks/identity_auth/runtime_adapter.py] Terms=['token']
- issue_refresh_token lines 232-270 [backend/app/stacks/identity_auth/runtime_adapter.py] Terms=['token', 'refresh']
- runtime_refresh_token_hash lines 304-310 [backend/app/stacks/identity_auth/runtime_adapter.py] Terms=['hash', 'token', 'refresh']
- runtime_validate_refresh_token lines 388-410 [backend/app/stacks/identity_auth/runtime_adapter.py] Terms=['token', 'refresh']
- runtime_hash_refresh_token lines 412-418 [backend/app/stacks/identity_auth/runtime_adapter.py] Terms=['hash', 'token', 'refresh']
- runtime_verify_refresh_token lines 420-428 [backend/app/stacks/identity_auth/runtime_adapter.py] Terms=['hash', 'token', 'refresh']
- issue_access_token lines 96-101 [backend/app/stacks/identity_auth/service_contracts.py] Terms=['token']
- issue_refresh_token lines 103-108 [backend/app/stacks/identity_auth/service_contracts.py] Terms=['token', 'refresh']
- test_registration_api_with_display_name lines 17-28 [backend/app/stacks/identity_auth/tests/test_api.py] Terms=['registration', 'password', 'email']
- test_registration_api_without_display_name lines 32-42 [backend/app/stacks/identity_auth/tests/test_api.py] Terms=['registration', 'password', 'email']
- test_login_api_request lines 46-54 [backend/app/stacks/identity_auth/tests/test_api.py] Terms=['password', 'email']
- build_test_app lines 95-115 [backend/app/stacks/identity_auth/tests/test_api_route_contract.py] Terms=['registration']
- test_registration_contract lines 118-144 [backend/app/stacks/identity_auth/tests/test_api_route_contract.py] Terms=['register', 'registration', 'password', 'email']
- test_registration_failure_is_generic lines 147-179 [backend/app/stacks/identity_auth/tests/test_api_route_contract.py] Terms=['register', 'registration', 'password', 'email']
- test_login_contract lines 182-210 [backend/app/stacks/identity_auth/tests/test_api_route_contract.py] Terms=['password', 'email', 'token', 'refresh']
- test_login_failure_is_generic lines 213-249 [backend/app/stacks/identity_auth/tests/test_api_route_contract.py] Terms=['password', 'email']
- register lines 38-51 [backend/app/stacks/identity_auth/tests/test_api_route_contract.py] Terms=['register', 'registration', 'email']
- login lines 63-92 [backend/app/stacks/identity_auth/tests/test_api_route_contract.py] Terms=['token', 'refresh']
- test_registration_dependency_is_async_generator lines 18-21 [backend/app/stacks/identity_auth/tests/test_api_runtime_binding.py] Terms=['registration']
- test_registration_dependency_contract_annotation lines 30-35 [backend/app/stacks/identity_auth/tests/test_api_runtime_binding.py] Terms=['registration']
- test_runtime_service_types_are_canonical lines 46-55 [backend/app/stacks/identity_auth/tests/test_api_runtime_binding.py] Terms=['registration']
- test_route_policy_inventory lines 51-90 [backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py] Terms=['register']
- test_public_route_requires_no_token lines 93-102 [backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py] Terms=['token']
- test_authenticated_route_rejects_missing_token lines 105-118 [backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py] Terms=['token']
- test_authenticated_route_accepts_principal lines 121-168 [backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py] Terms=['password', 'token']
- test_admin_route_rejects_non_admin lines 171-218 [backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py] Terms=['password', 'token']
- test_admin_route_accepts_server_claim lines 221-268 [backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py] Terms=['password', 'token']
- test_refresh_token_validation_failure_is_unauthorized lines 283-312 [backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py] Terms=['token', 'refresh']
- load_identity_state lines 137-147 [backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py] Terms=['password']
- load_identity_state lines 187-197 [backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py] Terms=['password']
- load_identity_state lines 237-247 [backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py] Terms=['password']
- reject lines 286-291 [backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py] Terms=['token', 'refresh']
- test_auth_router_has_complete_session_lifecycle lines 95-128 [backend/app/stacks/identity_auth/tests/test_canonical_router_inclusion.py] Terms=['register', 'refresh']
- test_controlled_local_registration_and_login lines 131-182 [backend/app/stacks/identity_auth/tests/test_canonical_router_inclusion.py] Terms=['register', 'registration', 'password', 'email', 'token', 'refresh']
- register lines 32-40 [backend/app/stacks/identity_auth/tests/test_canonical_router_inclusion.py] Terms=['register', 'registration', 'email']
- login lines 44-68 [backend/app/stacks/identity_auth/tests/test_canonical_router_inclusion.py] Terms=['token', 'refresh']
- test_registration_with_display_name lines 18-63 [backend/app/stacks/identity_auth/tests/test_display_name.py] Terms=['register', 'registration', 'password', 'hash', 'email', 'commit', 'rollback']
- test_registration_with_trimmed_display_name lines 67-110 [backend/app/stacks/identity_auth/tests/test_display_name.py] Terms=['register', 'registration', 'password', 'hash', 'email', 'commit', 'rollback']
- test_registration_with_empty_display_name lines 114-141 [backend/app/stacks/identity_auth/tests/test_display_name.py] Terms=['register', 'registration', 'password', 'hash', 'email', 'commit', 'rollback']
- test_registration_with_long_display_name lines 145-174 [backend/app/stacks/identity_auth/tests/test_display_name.py] Terms=['register', 'registration', 'password', 'hash', 'email', 'commit', 'rollback']
- test_registration_without_display_name lines 178-221 [backend/app/stacks/identity_auth/tests/test_display_name.py] Terms=['register', 'registration', 'password', 'hash', 'email', 'commit', 'rollback']
- test_session_introspection_includes_display_name lines 225-253 [backend/app/stacks/identity_auth/tests/test_display_name.py] Terms=['password', 'email']
- test_successful_registration lines 15-51 [backend/app/stacks/identity_auth/tests/test_registration.py] Terms=['register', 'registration', 'password', 'hash', 'email', 'commit', 'rollback']
- test_registration_with_existing_email lines 55-85 [backend/app/stacks/identity_auth/tests/test_registration.py] Terms=['register', 'registration', 'password', 'hash', 'email', 'commit', 'rollback']
- test_registration_with_invalid_password lines 89-118 [backend/app/stacks/identity_auth/tests/test_registration.py] Terms=['register', 'registration', 'password', 'hash', 'email', 'commit', 'rollback']
- test_complete_mock_registration_and_login_flow lines 19-74 [backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py] Terms=['register', 'registration', 'password', 'hash', 'email', 'commit', 'rollback', 'token', 'refresh']
- test_duplicate_registration_rolls_back lines 78-103 [backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py] Terms=['register', 'registration', 'password', 'email', 'commit', 'rollback']
- test_unknown_and_wrong_password_share_error lines 107-148 [backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py] Terms=['register', 'registration', 'password', 'email', 'token', 'refresh']
- test_disabled_account_rejected_before_token_issuance lines 152-184 [backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py] Terms=['register', 'registration', 'password', 'email', 'token', 'refresh']
- test_access_token_failure_rolls_back lines 188-216 [backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py] Terms=['register', 'registration', 'password', 'email', 'commit', 'rollback', 'token', 'refresh']
- test_refresh_token_failure_rolls_back lines 220-248 [backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py] Terms=['register', 'registration', 'password', 'email', 'commit', 'rollback', 'token', 'refresh']
- test_refresh_session_failure_rolls_back lines 252-280 [backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py] Terms=['register', 'registration', 'password', 'email', 'commit', 'rollback', 'refresh']
- test_registration_commit_failure_fails_closed lines 284-301 [backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py] Terms=['register', 'registration', 'password', 'email', 'commit', 'rollback']
- test_login_commit_failure_fails_closed lines 305-329 [backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py] Terms=['register', 'registration', 'password', 'email', 'commit', 'rollback']
- build_service lines 21-66 [backend/app/stacks/identity_auth/tests/test_registration_service.py] Terms=['registration', 'password', 'hash', 'email', 'commit', 'rollback']
- test_registration_normalizes_and_hashes_password lines 70-116 [backend/app/stacks/identity_auth/tests/test_registration_service.py] Terms=['register', 'registration', 'password', 'hash', 'email', 'commit', 'rollback', 'token', 'refresh']
- test_duplicate_registration_fails_generically lines 120-140 [backend/app/stacks/identity_auth/tests/test_registration_service.py] Terms=['register', 'registration', 'password', 'hash', 'email', 'commit', 'rollback']
- test_registration_hash_failure_rolls_back lines 144-165 [backend/app/stacks/identity_auth/tests/test_registration_service.py] Terms=['register', 'registration', 'password', 'hash', 'email', 'commit', 'rollback']
- test_empty_password_fails_closed lines 169-187 [backend/app/stacks/identity_auth/tests/test_registration_service.py] Terms=['register', 'registration', 'password', 'email', 'commit', 'rollback']
- test_runtime_construction_is_non_mutating lines 67-93 [backend/app/stacks/identity_auth/tests/test_runtime_adapter.py] Terms=['registration', 'commit', 'rollback']
- test_real_access_and_refresh_token_paths lines 113-151 [backend/app/stacks/identity_auth/tests/test_runtime_adapter.py] Terms=['token', 'refresh']
- __init__ lines 26-28 [backend/app/stacks/identity_auth/tests/test_runtime_adapter.py] Terms=['commit', 'rollback']
- flush lines 38-43 [backend/app/stacks/identity_auth/tests/test_runtime_adapter.py] Terms=['flush']
- test_mock_access_issuer_accepts_and_records_claims lines 19-36 [backend/app/stacks/identity_auth/tests/test_stage4f_mock_identity_contract.py] Terms=['token']
- test_mock_refresh_issuer_accepts_and_records_claims lines 40-57 [backend/app/stacks/identity_auth/tests/test_stage4f_mock_identity_contract.py] Terms=['token', 'refresh']
- test_mock_issuer_signatures_match_claim_contract lines 60-80 [backend/app/stacks/identity_auth/tests/test_stage4f_mock_identity_contract.py] Terms=['token', 'refresh']
- test_mock_registration_result_remains_registration_contract lines 84-106 [backend/app/stacks/identity_auth/tests/test_stage4f_mock_identity_contract.py] Terms=['register', 'registration', 'password', 'email']
- test_mock_registration_login_flow_accepts_claim_propagation lines 110-133 [backend/app/stacks/identity_auth/tests/test_stage4f_mock_identity_contract.py] Terms=['register', 'registration', 'password', 'email', 'token', 'refresh']
- __init__ lines 76-82 [backend/app/stacks/market_data/provider_registry.py] Terms=['register']
- register lines 97-143 [backend/app/stacks/market_data/provider_registry.py] Terms=['register']
- unregister lines 145-162 [backend/app/stacks/market_data/provider_registry.py] Terms=['register']
- get lines 164-192 [backend/app/stacks/market_data/provider_registry.py] Terms=['register']
- set_enabled lines 194-224 [backend/app/stacks/market_data/provider_registry.py] Terms=['register']
- records lines 226-254 [backend/app/stacks/market_data/provider_registry.py] Terms=['register']
- build_market_data_runtime lines 54-95 [backend/app/stacks/market_data/runtime_composition.py] Terms=['register']

Request and Response Schemas

- backend/app/stacks/identity_auth/service_contracts.py
    Class: RegistrationCommand Fields=['display_name', 'email', 'password'] Lines=31-34
    Class: RegisteredIdentity Fields=['email_normalized', 'status', 'user_id'] Lines=38-41
    Class: LoginCommand Fields=['email', 'password'] Lines=45-47
    Class: IssuedServiceToken Fields=['expires_at', 'issued_at', 'token', 'token_id'] Lines=51-55
    Class: AuthenticationTokenPair Fields=['access_expires_at', 'access_token', 'password_change_required', 'refresh_expires_at', 'refresh_token', 'token_type'] Lines=59-65
    Class: ServiceTokenIssuer Fields=[] Lines=93-108
    Class: SessionRefreshCommand Fields=['refresh_token'] Lines=128-129
    Class: SessionLogoutCommand Fields=['refresh_token'] Lines=133-134
    Class: SessionLogoutAllCommand Fields=['user_id'] Lines=138-139
- backend/app/stacks/identity_auth/tests/test_api_route_contract.py
    Class: FakeRegistrationService Fields=[] Lines=29-51
    Class: FakeLoginService Fields=[] Lines=54-92
- backend/app/stacks/identity_auth/tests/test_stage4f_mock_identity_contract.py

Database Models

- backend/app/stacks/chat_public/persistence/chat_models.py
    Class: ChatThreadRecord Fields=['__table_args__', '__tablename__', 'created_at', 'message_count', 'metadata_json', 'status', 'summary', 'thread_id', 'title', 'updated_at', 'user_id'] Lines=53-118
- backend/app/stacks/chat_public/tests/test_aiq005f_general_conversation_model_binding.py
- backend/app/stacks/db_runtime/model_registry.py
- backend/app/stacks/identity_auth/admin_read_api_models.py
    Class: AdministrativeUserSummary Fields=['created_at', 'email', 'is_active', 'model_config', 'must_change_password', 'role', 'status', 'updated_at', 'user_id'] Lines=13-41
    Class: AdministrativeUserDetail Fields=['active_session_count', 'total_session_count'] Lines=44-53
    Class: AdministrativeSessionSummary Fields=['expires_at', 'issued_at', 'model_config', 'replaced', 'revoked_at', 'session_id', 'state', 'user_id'] Lines=56-80
    Class: AdministrativeSessionDetail Fields=['replacement_session_id', 'token_family_id'] Lines=83-87
    Class: AdministrativeUserListResponse Fields=['items', 'limit', 'model_config', 'offset', 'returned'] Lines=90-114
    Class: AdministrativeIntrospectionResponse Fields=['access_mode', 'authorization_source', 'model_config', 'mutations_enabled', 'session_read_model', 'status', 'user_read_model'] Lines=144-157
    Class: AdministrativeAccessTokenRevocationSummary Fields=['created_at', 'expires_at', 'id', 'issued_at', 'reason', 'revoked_at', 'state', 'user_id'] Lines=160-173
    Class: AdministrativeAccessTokenRevocationDetail Fields=[] Lines=176-179
    Class: AdministrativeAccessTokenRevocationListResponse Fields=['limit', 'offset', 'records', 'total'] Lines=182-190
- backend/app/stacks/identity_auth/admin_read_models.py
    Class: AdministrativeReadService Fields=['__slots__'] Lines=277-631
- backend/app/stacks/identity_auth/api_dependencies.py
- backend/app/stacks/identity_auth/api_models.py
    Class: RegistrationApiRequest Fields=['display_name', 'email', 'model_config', 'password'] Lines=10-32
    Class: LoginApiRequest Fields=['email', 'model_config', 'password'] Lines=35-52
    Class: RegistrationApiResponse Fields=['model_config', 'status'] Lines=55-63
    Class: LoginTokenApiResponse Fields=['access_token', 'model_config', 'password_change_required', 'refresh_token', 'token_type'] Lines=66-84
    Class: ChangeRequiredPasswordApiRequest Fields=['current_password', 'model_config', 'new_password'] Lines=87-103
    Class: ChangeRequiredPasswordApiResponse Fields=['model_config', 'revoked_sessions', 'status'] Lines=106-118
    Class: RefreshTokenApiRequest Fields=['model_config', 'refresh_token'] Lines=121-133
    Class: LogoutApiRequest Fields=['model_config', 'refresh_token'] Lines=136-148
    Class: SessionTokenApiResponse Fields=['access_token', 'model_config', 'refresh_token', 'token_type'] Lines=151-167
- backend/app/stacks/identity_auth/api_router.py
    Class: RegistrationApiService Fields=[] Lines=59-66
    Class: LoginApiService Fields=[] Lines=69-76
    Class: SessionLifecycleApiService Fields=[] Lines=79-101
- backend/app/stacks/identity_auth/dev_owner_provisioner.py
    Class: DevOwnerProvisioningResult Fields=['created', 'email', 'must_change_password', 'role', 'temporary_password_valid', 'user_id'] Lines=29-35
- backend/app/stacks/identity_auth/login_service.py
    Class: LoginService Fields=[] Lines=27-236
- backend/app/stacks/identity_auth/mock_runtime.py
    Class: MockIdentityUser Fields=['display_name', 'email_normalized', 'id', 'is_active', 'password_hash', 'role', 'status', 'subscription_tier'] Lines=25-34
    Class: MockRefreshSession Fields=['expires_at', 'issued_at', 'token_hash', 'token_id', 'user_id'] Lines=38-43
    Class: MockIdentityUserRepository Fields=[] Lines=46-86
    Class: MockRefreshSessionRepository Fields=[] Lines=89-123
    Class: MockServiceTokenIssuer Fields=[] Lines=145-229
    Class: MockAuthenticationRuntime Fields=[] Lines=287-343
- backend/app/stacks/identity_auth/models.py
    Class: IdentityUser Fields=['__table_args__', '__tablename__', 'created_at', 'display_name', 'email_normalized', 'id', 'is_active', 'must_change_password', 'password_hash', 'refresh_sessions', 'role', 'status', 'subscription_tier', 'updated_at'] Lines=33-148
    Class: IdentityRefreshSession Fields=['__table_args__', '__tablename__', 'created_at', 'expires_at', 'family_id', 'id', 'issued_at', 'last_used_at', 'replaced_by', 'revoked_at', 'token_hash', 'token_id', 'user', 'user_id'] Lines=151-259
- backend/app/stacks/identity_auth/registration_service.py
    Class: RegistrationService Fields=[] Lines=19-123
- backend/app/stacks/identity_auth/repositories.py
    Class: IdentityUserRepository Fields=[] Lines=72-186
    Class: RefreshSessionRepository Fields=[] Lines=188-375
- backend/app/stacks/identity_auth/route_protection.py
- backend/app/stacks/identity_auth/runtime_adapter.py
    Class: EnvironmentJwtTokenIssuer Fields=[] Lines=183-270
- backend/app/stacks/identity_auth/service_contracts.py
    Class: RegistrationCommand Fields=['display_name', 'email', 'password'] Lines=31-34
    Class: RegisteredIdentity Fields=['email_normalized', 'status', 'user_id'] Lines=38-41
    Class: LoginCommand Fields=['email', 'password'] Lines=45-47
    Class: IssuedServiceToken Fields=['expires_at', 'issued_at', 'token', 'token_id'] Lines=51-55
    Class: AuthenticationTokenPair Fields=['access_expires_at', 'access_token', 'password_change_required', 'refresh_expires_at', 'refresh_token', 'token_type'] Lines=59-65
    Class: ServiceTokenIssuer Fields=[] Lines=93-108
    Class: SessionRefreshCommand Fields=['refresh_token'] Lines=128-129
    Class: SessionLogoutCommand Fields=['refresh_token'] Lines=133-134
    Class: SessionLogoutAllCommand Fields=['user_id'] Lines=138-139
- backend/app/stacks/identity_auth/session_introspection.py
- backend/app/stacks/identity_auth/tests/test_api.py
- backend/app/stacks/identity_auth/tests/test_api_route_contract.py
    Class: FakeRegistrationService Fields=[] Lines=29-51
    Class: FakeLoginService Fields=[] Lines=54-92
- backend/app/stacks/identity_auth/tests/test_api_runtime_binding.py
- backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py
- backend/app/stacks/identity_auth/tests/test_canonical_router_inclusion.py
    Class: QualificationRegistrationService Fields=[] Lines=31-40
    Class: QualificationLoginService Fields=[] Lines=43-68
- backend/app/stacks/identity_auth/tests/test_display_name.py
- backend/app/stacks/identity_auth/tests/test_identity_persistence_models.py
- backend/app/stacks/identity_auth/tests/test_identity_repository.py
- backend/app/stacks/identity_auth/tests/test_login_service.py
- backend/app/stacks/identity_auth/tests/test_registration.py
- backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py
- backend/app/stacks/identity_auth/tests/test_registration_service.py
- backend/app/stacks/identity_auth/tests/test_runtime_adapter.py
- backend/app/stacks/identity_auth/tests/test_session_introspection.py
- backend/app/stacks/identity_auth/tests/test_stage4f_canonical_claim_propagation.py
- backend/app/stacks/identity_auth/tests/test_stage4f_login_refresh_claims.py
- backend/app/stacks/identity_auth/tests/test_stage4f_mock_identity_contract.py
- backend/app/stacks/identity_auth/tests/test_stage9d_c5_k1_session_introspection.py
    Class: FakeIdentityUserRepository Fields=[] Lines=22-29
- backend/app/stacks/journal_ledger/decision_event_model.py

Password Hashing

- backend/app/stacks/identity_auth/dev_owner_provisioner.py
- backend/app/stacks/identity_auth/login_service.py
- backend/app/stacks/identity_auth/mock_runtime.py
- backend/app/stacks/identity_auth/models.py
- backend/app/stacks/identity_auth/registration_service.py
- backend/app/stacks/identity_auth/repositories.py
- backend/app/stacks/identity_auth/runtime_adapter.py
- backend/app/stacks/identity_auth/tests/test_display_name.py
- backend/app/stacks/identity_auth/tests/test_identity_persistence_models.py
- backend/app/stacks/identity_auth/tests/test_identity_repository.py
- backend/app/stacks/identity_auth/tests/test_login_service.py
- backend/app/stacks/identity_auth/tests/test_registration.py
- backend/app/stacks/identity_auth/tests/test_registration_service.py
- backend/app/stacks/identity_auth/tests/test_stage4f_canonical_claim_propagation.py
- backend/app/stacks/identity_auth/tests/test_stage4f_login_refresh_claims.py

Repository and Persistence Files

- backend/app/stacks/chat_public/persistence/chat_models.py
- backend/app/stacks/identity_auth/tests/test_identity_persistence_models.py
- backend/app/stacks/identity_auth/tests/test_identity_repository.py

Registration Response and Redirects

- href → / [frontend/app/register/page.tsx:118]
- href → / [frontend/app/register/page.tsx:248]
- href → /login [frontend/app/register/page.tsx:255]

Page-State Inventory

loading_state_detected: True
error_state_detected: True
success_state_detected: True
responsive_classes_detected: True
accessibility_markers_detected: True
password_visibility_control_detected: False
duplicate_submit_protection_detected: True

Security Controls

password_hashing_detected: True
email_normalization_detected: True
duplicate_user_check_detected: True
transaction_commit_detected: True
transaction_rollback_detected: True
rate_limiting_detected: False
raw_password_logging_risk_detected: False
access_token_creation_detected: True
refresh_token_creation_detected: True

Tests

- backend/app/stacks/chat_public/tests/test_aiq005f_general_conversation_model_binding.py
    test_router_constant_uses_qualified_general_model
    test_ollama_client_registers_qualified_model
    test_greeting_uses_qualified_general_model
    test_small_talk_uses_qualified_general_model
    test_simple_explanation_uses_qualified_general_model
    test_software_debugging_remains_on_coder
    test_live_execution_remains_blocked
- backend/app/stacks/identity_auth/tests/test_api.py
    test_registration_api_with_display_name
    test_registration_api_without_display_name
    test_login_api_request
- backend/app/stacks/identity_auth/tests/test_api_route_contract.py
    test_registration_contract
    test_registration_failure_is_generic
    test_login_contract
    test_login_failure_is_generic
    test_router_is_activated_in_canonical_app
- backend/app/stacks/identity_auth/tests/test_api_runtime_binding.py
    test_registration_dependency_is_async_generator
    test_login_dependency_is_async_generator
    test_registration_dependency_contract_annotation
    test_login_dependency_contract_annotation
    test_runtime_service_types_are_canonical
- backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py
    test_route_policy_inventory
    test_public_route_requires_no_token
    test_authenticated_route_rejects_missing_token
    test_authenticated_route_accepts_principal
    test_admin_route_rejects_non_admin
    test_admin_route_accepts_server_claim
    test_unknown_route_preserves_not_found
    test_refresh_token_validation_failure_is_unauthorized
- backend/app/stacks/identity_auth/tests/test_canonical_router_inclusion.py
    test_canonical_source_includes_auth_router_once
    test_auth_router_has_complete_session_lifecycle
    test_controlled_local_registration_and_login
- backend/app/stacks/identity_auth/tests/test_display_name.py
    test_registration_with_display_name
    test_registration_with_trimmed_display_name
    test_registration_with_empty_display_name
    test_registration_with_long_display_name
    test_registration_without_display_name
    test_session_introspection_includes_display_name
- backend/app/stacks/identity_auth/tests/test_registration.py
    test_successful_registration
    test_registration_with_existing_email
    test_registration_with_invalid_password
- backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py
    test_complete_mock_registration_and_login_flow
    test_duplicate_registration_rolls_back
    test_unknown_and_wrong_password_share_error
    test_disabled_account_rejected_before_token_issuance
    test_access_token_failure_rolls_back
    test_refresh_token_failure_rolls_back
    test_refresh_session_failure_rolls_back
    test_registration_commit_failure_fails_closed
    test_login_commit_failure_fails_closed
- backend/app/stacks/identity_auth/tests/test_registration_service.py
    test_registration_normalizes_and_hashes_password
    test_duplicate_registration_fails_generically
    test_registration_hash_failure_rolls_back
    test_empty_password_fails_closed
- backend/app/stacks/identity_auth/tests/test_runtime_adapter.py
    test_runtime_construction_is_non_mutating
    test_runtime_fails_closed_without_secret
    test_real_access_and_refresh_token_paths
- backend/app/stacks/identity_auth/tests/test_stage4f_mock_identity_contract.py
    test_mock_access_issuer_accepts_and_records_claims
    test_mock_refresh_issuer_accepts_and_records_claims
    test_mock_issuer_signatures_match_claim_contract
    test_mock_registration_result_remains_registration_contract
    test_mock_registration_login_flow_accepts_claim_propagation
- backend/app/stacks/market_data/tests/test_provider_runtime.py
    test_registry_registers_and_selects_by_priority
    test_registry_rejects_duplicate_name
    test_registry_ignores_disabled_provider
    test_cache_returns_unexpired_value
    test_cache_expires_value
    test_cache_evicts_least_recently_used
    test_market_session_classification
    test_market_session_rejects_naive_datetime
    test_router_uses_highest_priority_provider
    test_router_falls_back_after_provider_failure
    test_router_fails_closed_when_all_providers_fail
    test_router_quote_cache_prevents_second_provider_call
    test_router_returns_canonical_historical_result
- backend/app/stacks/market_data/tests/test_runtime_composition.py
    test_production_runtime_constructs_without_network
    test_runtime_components_are_shared
    test_read_only_routes_are_declared
    test_status_endpoint_is_network_free
    test_quote_endpoint_uses_shared_router
    test_historical_endpoint_uses_shared_router
    test_invalid_historical_range_fails_closed
- backend/app/stacks/market_data/tests/test_stage8_runtime_qualification.py
    test_quote_cache_prevents_repeated_provider_call
    test_quote_cache_expiry_forces_refresh
    test_use_cache_false_always_calls_provider
    test_router_falls_back_after_quote_failure
    test_router_falls_back_after_historical_failure
    test_router_fails_closed_when_every_provider_fails
    test_api_translates_provider_failure_to_503
    test_api_rejects_invalid_historical_range
    test_status_endpoint_does_not_call_provider
- backend/app/stacks/portfolio/tests/test_authenticated_paper_order_api.py
    test_paper_order_route_policy_is_authenticated
    test_paper_order_route_is_registered
    test_paper_order_normalizes_symbol
    test_paper_order_rejects_invalid_symbol
    test_paper_order_rejects_invalid_action
    test_paper_order_propagates_authenticated_owner
    test_two_orders_keep_owners_separate
- backend/app/stacks/portfolio/tests/test_authenticated_portfolio_valuation_api.py
    test_portfolio_valuation_policy_is_authenticated
    test_portfolio_valuation_route_is_registered
    test_portfolio_valuation_propagates_owner
    test_portfolio_valuation_keeps_owners_separate
- backend/app/test/test_stage8e_runtime_instrumentation.py
    test_stage8e_architecture_nodes_are_registered
    test_runtime_trace_supports_stage8d_metrics
    test_chat_runtime_contains_required_operational_stages
    test_route_policy_emits_security_events
    test_frontend_preserves_playback_and_exposes_metrics
    test_global_event_bus_remains_canonical
- frontend/tests/e2e/04-backend-connectivity.spec.ts
    backend documentation endpoint is reachable
    backend OpenAPI contract is reachable
    protected backend route rejects anonymous request
- frontend/tests/e2e/05-authenticated-user-flow.spec.ts
    register, login, persist session, and logout
    /
    /
- frontend/tests/e2e/06-dashboard-navigation.spec.ts
    /
    dashboard, portfolio, and analytics render for a user
- frontend/tests/e2e/07-neuro-welcome-briefing.spec.ts
    authenticated user can view, close, and reopen the briefing
    /
- frontend/tests/e2e/08-objective4g-d-authenticated-live-turn.spec.ts
    /
    qualifies authenticated math, RAG, verification, and replay
- frontend/tests/e2e/09-objective4h-b-broad-prompt-matrix.spec.ts
    qualifies broad authenticated cognitive behavior

Current Gaps Requiring Verification

- Registration rate limiting was not conclusively detected.

Function Flow Graph

[Visitor]
      ↓
[Browser route /register]
      ↓
[Frontend page: frontend/app/register/page.tsx]
      ↓
[Registration form and frontend validation]
      ↓
[Submit handler]
      ↓
[Frontend service or API proxy]
      ↓
[POST backend registration route]
      ↓
[Request-schema validation]
      ↓
[Email normalization]
      ↓
[Duplicate-account check]
      ↓
[Password hashing]
      ↓
[User repository and database transaction]
      ↓
[Registration response]
      ↓
[Login, onboarding, or authenticated destination]

Launch Dependency

Required Before Launch: YES

Blocks:
- New-user onboarding
- Account creation
- First-time access
- Controlled early-user launch

Depends On:
- Public routing
- Frontend form validation
- Authentication API
- Identity service
- Password hashing
- Database persistence
- Error handling

Manual Verification Checklist

[ ] Open /register while logged out
[ ] Open /register while authenticated
[ ] Verify all visible fields and labels
[ ] Verify valid registration
[ ] Verify invalid email rejection
[ ] Verify weak-password rejection
[ ] Verify password-confirmation behavior
[ ] Verify duplicate-email rejection
[ ] Verify duplicate-submit protection
[ ] Verify loading state
[ ] Verify success state
[ ] Verify backend failure state
[ ] Verify no raw password appears in logs
[ ] Verify password is stored only as a secure hash
[ ] Verify database rollback on failure
[ ] Verify post-registration redirect
[ ] Verify keyboard navigation
[ ] Verify screen-reader labels
[ ] Verify desktop layout
[ ] Verify mobile layout
[ ] Run registration Playwright test

Final Verdict

Function Exists: YES
Frontend Complete: UNVERIFIED
Frontend Connected: UNVERIFIED
Middleware Connected: UNVERIFIED
Backend Complete: UNVERIFIED
Database Connected: UNVERIFIED
Password Hashing Verified: UNVERIFIED
Duplicate Protection Verified: UNVERIFIED
Error Handling Complete: UNVERIFIED
Tests Passing: UNVERIFIED
Live Verification Complete: NO

Overall Status: PARTIALLY INVENTORIED

Launch Classification: CRITICAL

Required Next Action:
Review this source inventory, then run a controlled registration
verification using a temporary account and prove the complete
frontend-to-database-to-response path.

---



---

FUNCTION PATH 03 — EXISTING USER LOGIN

Function Status

Inventory Status: INITIAL INVENTORY COMPLETE
Implementation Status: IMPLEMENTED — SOURCE CONFIRMATION PENDING
Qualification Status: UNVERIFIED
Launch Importance: CRITICAL
Last Updated: 2026-07-29
Evidence Source: runtime/system_inventory/function_path_03_existing_user_login_20260729_233128/function_path_03_existing_user_login_inventory.json

Purpose

The Existing User Login function allows a registered NeuroVest user
to authenticate using their stored account credentials.

Its purpose is to:

- Present the login form.
- Collect the user's email and password.
- Validate the submitted login information.
- Submit the credentials to the identity-auth backend.
- Normalize the submitted email address.
- Locate the existing user account.
- Verify the submitted password against the stored password hash.
- Verify that the account is allowed to authenticate.
- Create a short-lived access token.
- Create or rotate the refresh-session state.
- Return the implemented session cookies or authentication response.
- Redirect the authenticated user to the correct application page.

User Journey

Internet
      │
      ▼
Browser
      │
      ▼
GET /login
      │
      ▼
Next.js
      │
      ▼
frontend/proxy.ts
      │
      ▼
frontend/app/layout.tsx
      │
      ▼
frontend/app/login/page.tsx
      │
      ▼
LoginPage()
      │
      ▼
Login Form
      │
      ├────────► Email
      └────────► Password
                     │
                     ▼
              Frontend Validation
                     │
                     ▼
                Submit Handler
                     │
                     ▼
           Frontend Login Request
                     │
                     ▼
              POST /auth/login
                     │
                     ▼
              login_identity()
                     │
                     ├────────► Email Normalization
                     ├────────► User Lookup
                     ├────────► Password Verification
                     ├────────► Account-State Validation
                     ├────────► Access Token Creation
                     ├────────► Refresh Session Creation
                     └────────► Cookie or Token Response
                                      │
                                      ▼
                             Authenticated Redirect

Entry Point

Browser Route

/login

Route Type

PUBLIC

Authentication Required

NO

Expected Redirect

UNVERIFIED

Authenticated Users

UNVERIFIED

Frontend

Page File

frontend/app/login/page.tsx

Component

LoginPage

Component Type

Client Component

Layout

frontend/app/layout.tsx

Middleware

frontend/proxy.ts

Loading File

UNKNOWN

Error Page

UNKNOWN

404 Page

UNKNOWN

Visible Layout

H1

Welcome back.

Source: frontend/app/login/page.tsx:147

P

Sign in to access the controlled dashboard, runtime graph, and read-only intelligence systems.

Source: frontend/app/login/page.tsx:151

P

Secure access

Source: frontend/app/login/page.tsx:176

H2

Sign in to NeuroVest

Source: frontend/app/login/page.tsx:180

LABEL

Email

Source: frontend/app/login/page.tsx:189

LABEL

Password

Source: frontend/app/login/page.tsx:208

Login Inputs

Input 1

Name: email

Type: email

ID: email

Placeholder: UNKNOWN

AutoComplete: email

Required: True

Source: frontend/app/login/page.tsx:196

Input 2

Name: password

Type: password

ID: password

Placeholder: UNKNOWN

AutoComplete: current-password

Required: True

Source: frontend/app/login/page.tsx:215

Frontend Components

Root Component

LoginPage()

Location

frontend/app/login/page.tsx

Dependency Inventory

Frontend files traced: 1

Import edges detected: 3

frontend/app/login/page.tsx
Depth: 0; Client component: True

Frontend Forms

Submit Handler: submit
HTML Action: UNKNOWN
HTML Method: UNKNOWN
Source: frontend/app/login/page.tsx:184

Frontend Handlers

clearPrivateBrowserCaches
Type: function
Source: frontend/app/login/page.tsx:17

LoginPage
Type: function
Source: frontend/app/login/page.tsx:24

submit
Type: function
Source: frontend/app/login/page.tsx:33

submit
Type: JSX event binding
Source: frontend/app/login/page.tsx:186

Frontend Validation

email — frontend/app/login/page.tsx:53
email — frontend/app/login/page.tsx:54
email — frontend/app/login/page.tsx:190
email — frontend/app/login/page.tsx:193
email — frontend/app/login/page.tsx:197
email — frontend/app/login/page.tsx:198
email — frontend/app/login/page.tsx:199
email — frontend/app/login/page.tsx:200
password — frontend/app/login/page.tsx:56
password — frontend/app/login/page.tsx:57
password — frontend/app/login/page.tsx:105
password — frontend/app/login/page.tsx:120
password — frontend/app/login/page.tsx:121
password — frontend/app/login/page.tsx:209
password — frontend/app/login/page.tsx:212
password — frontend/app/login/page.tsx:216
password — frontend/app/login/page.tsx:217
password — frontend/app/login/page.tsx:218
password — frontend/app/login/page.tsx:219
required — frontend/app/login/page.tsx:201
required — frontend/app/login/page.tsx:220
trim — frontend/app/login/page.tsx:76

Frontend Event Flow

Existing user opens /login

↓

Login page renders

↓

User enters email and password

↓

Frontend validation runs

↓

Invalid input
    → Submission blocked
    → Validation feedback displayed

Valid input
    → Submit handler runs
    → Duplicate submission is prevented
    → Login request is sent

↓

Backend response received

↓

Successful authentication
    → Access and refresh state processed
    → Frontend session state updated
    → Authenticated redirect occurs

Failed authentication
    → Error response translated
    → Login form remains available
    → User receives failure feedback

Frontend Request

POST "/api/auth/login"
Request Type: fetch
Credentials Mode: UNKNOWN
Source: frontend/app/login/page.tsx:44

Frontend Authentication and Proxy Files

frontend/proxy.ts
Methods: ['GET']
Targets: ['/login']
Cookies: ['neurovest_access', 'neurovest_csrf', 'neurovest_session']
Credentials Include: False

frontend/lib/backendAuth.ts
Methods: ['POST']
Targets: []
Cookies: []
Credentials Include: False

frontend/lib/sessionCookies.ts
Methods: ['GET']
Targets: []
Cookies: ['neurovest_access', 'neurovest_csrf', 'neurovest_preference_scope', 'neurovest_refresh', 'neurovest_session']
Credentials Include: False

frontend/tests/e2e/02-auth-boundary.spec.ts
Methods: []
Targets: ['/login', '/login/']
Cookies: []
Credentials Include: False

frontend/tests/e2e/05-authenticated-user-flow.spec.ts
Methods: ['GET', 'POST']
Targets: ['/auth/login', '/login']
Cookies: []
Credentials Include: False

frontend/tests/e2e/08-objective4g-d-authenticated-live-turn.spec.ts
Methods: ['GET', 'POST']
Targets: ['${frontendBase}/login', '/login']
Cookies: ['neurovest_csrf']
Credentials Include: False

frontend/app/login/page.tsx
Methods: ['GET', 'POST']
Targets: ['/api/auth/login']
Cookies: ['neurovest_chat_thread_v1', 'neurovest_request_metrics_v1']
Credentials Include: False

frontend/app/admin/sessions/page.tsx
Methods: []
Targets: []
Cookies: []
Credentials Include: False

frontend/app/components/auth/LogoutButton.tsx
Methods: ['POST']
Targets: ['/login']
Cookies: ['neurovest_chat_thread_v1', 'neurovest_request_metrics_v1']
Credentials Include: False

frontend/app/api/auth/register/route.ts
Methods: ['POST']
Targets: []
Cookies: []
Credentials Include: False

frontend/app/api/auth/session/route.ts
Methods: ['GET']
Targets: []
Cookies: []
Credentials Include: False

frontend/app/api/auth/change-password/route.ts
Methods: ['POST']
Targets: ['/login']
Cookies: []
Credentials Include: False

frontend/app/api/auth/logout/route.ts
Methods: ['POST']
Targets: ['/login']
Cookies: []
Credentials Include: False

frontend/app/api/auth/login/route.ts
Methods: ['GET', 'POST']
Targets: ['${BACKEND_BASE_URL}/auth/login']
Cookies: []
Credentials Include: False

Frontend Storage and Cookie Markers

No direct browser storage or document-cookie operation was identified in the login dependency tree.

Navigation and Redirects

href → / [frontend/app/login/page.tsx:141]
href → / [frontend/app/login/page.tsx:248]
href → /register [frontend/app/login/page.tsx:255]

Middleware

File

frontend/proxy.ts

Observed

PRESENT

Known Cookies

neurovest_access
neurovest_csrf
neurovest_session

Known Headers

Cache-Control
host
origin
x-forwarded-host
x-forwarded-proto
x-neurovest-csrf

Login Mentions

15

Authentication Logic

UNVERIFIED

Redirect Logic

UNVERIFIED

Backend Route

POST /login

Route Function

login_identity

Route File

backend/app/stacks/identity_auth/api_router.py

Source Line

157

Detected Security Markers

Depends, access_token, refresh_token

POST /change-required-password

Route Function

change_required_password

Route File

backend/app/stacks/identity_auth/api_router.py

Source Line

235

Detected Security Markers

Depends, access_token, refresh_token

POST /refresh

Route Function

refresh_session

Route File

backend/app/stacks/identity_auth/api_router.py

Source Line

282

Detected Security Markers

Depends, access_token, refresh_token

POST /logout

Route Function

logout_session

Route File

backend/app/stacks/identity_auth/api_router.py

Source Line

351

Detected Security Markers

Depends, access_token, refresh_token

POST /logout-all

Route Function

logout_all_sessions

Route File

backend/app/stacks/identity_auth/api_router.py

Source Line

428

Detected Security Markers

Depends

GET /introspection

Route Function

session_introspection

Route File

backend/app/stacks/identity_auth/api_router.py

Source Line

487

Detected Security Markers

Depends

GET /api/v1/analytics

Route Function

analytics

Route File

backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py

Source Line

24

Detected Security Markers

NONE IDENTIFIED

POST /api/v1/admin/backup

Route Function

admin_backup

Route File

backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py

Source Line

32

Detected Security Markers

NONE IDENTIFIED

GET /api/v1/market-data/status

Route Function

market_status

Route File

backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py

Source Line

40

Detected Security Markers

NONE IDENTIFIED

Backend Function Path

_generate_temporary_password
File: backend/app/stacks/identity_auth/admin_mutation_service.py
Lines: 106-125
Matched Terms: password
Calls: ''.join, any, c.isdigit, c.islower, c.isupper, range, secrets.choice

__init__
File: backend/app/stacks/identity_auth/admin_mutation_service.py
Lines: 155-160
Matched Terms: session
Calls: NONE EXTRACTED

_load_target
File: backend/app/stacks/identity_auth/admin_mutation_service.py
Lines: 162-183
Matched Terms: session
Calls: HTTPException, result.scalar_one_or_none, select, select(IdentityUser).where, self._session.execute

_revoke_refresh_sessions
File: backend/app/stacks/identity_auth/admin_mutation_service.py
Lines: 236-263
Matched Terms: session
Calls: IdentityRefreshSession.revoked_at.is_, datetime.now, int, self._session.execute, update, update(IdentityRefreshSession).where, update(IdentityRefreshSession).where(IdentityRefreshSession.user_id == user_id).where, update(IdentityRefreshSession).where(IdentityRefreshSession.user_id == user_id).where(IdentityRefreshSession.revoked_at.is_(None)).values

_audit
File: backend/app/stacks/identity_auth/admin_mutation_service.py
Lines: 265-280
Matched Terms: audit
Calls: logger.info

require_password_reset
File: backend/app/stacks/identity_auth/admin_mutation_service.py
Lines: 282-328
Matched Terms: password, session, audit, commit, rollback
Calls: AdministrativeMutationResponse, self._assert_target_mutable, self._audit, self._authorize_actor, self._load_target, self._revoke_refresh_sessions, self._session.commit, self._session.rollback

issue_temporary_password
File: backend/app/stacks/identity_auth/admin_mutation_service.py
Lines: 330-385
Matched Terms: password, session, audit, commit, rollback
Calls: AdministrativeTemporaryPasswordResponse, _generate_temporary_password, hash_password, self._assert_target_mutable, self._audit, self._authorize_actor, self._load_target, self._revoke_refresh_sessions, self._session.commit, self._session.rollback

disable_account
File: backend/app/stacks/identity_auth/admin_mutation_service.py
Lines: 387-434
Matched Terms: session, audit, commit, rollback
Calls: AdministrativeMutationResponse, _set_status, self._assert_target_mutable, self._audit, self._authorize_actor, self._load_target, self._revoke_refresh_sessions, self._session.commit, self._session.rollback

enable_account
File: backend/app/stacks/identity_auth/admin_mutation_service.py
Lines: 436-477
Matched Terms: session, audit, commit, rollback
Calls: AdministrativeMutationResponse, _set_status, self._assert_target_mutable, self._audit, self._authorize_actor, self._load_target, self._session.commit, self._session.rollback

delete_account
File: backend/app/stacks/identity_auth/admin_mutation_service.py
Lines: 479-536
Matched Terms: session, revocation, audit, commit, rollback
Calls: AdministrativeDeleteResponse, delete, delete(IdentityAccessTokenRevocation).where, delete(IdentityRefreshSession).where, self._assert_target_mutable, self._audit, self._authorize_actor, self._load_target, self._session.commit, self._session.delete, self._session.execute, self._session.rollback

register_identity
File: backend/app/stacks/identity_auth/api_router.py
Lines: 117-154
Matched Terms: password, email
Calls: Depends, HTTPException, RegistrationApiResponse, RegistrationCommand, isinstance, router.post, service.register

login_identity
File: backend/app/stacks/identity_auth/api_router.py
Lines: 163-232
Matched Terms: login, authenticate, password, email, access_token, refresh_token
Calls: Depends, HTTPException, LoginCommand, LoginTokenApiResponse, isinstance, result.token_type.lower, router.post, service.login

change_required_password
File: backend/app/stacks/identity_auth/api_router.py
Lines: 240-279
Matched Terms: authenticate, password, session
Calls: ChangeRequiredPasswordApiResponse, Depends, HTTPException, getattr, isinstance, router.post, service.replace_required_password

refresh_session
File: backend/app/stacks/identity_auth/api_router.py
Lines: 287-348
Matched Terms: authenticate, access_token, refresh_token, session
Calls: Depends, HTTPException, SessionTokenApiResponse, isinstance, result.token_type.lower, router.post, service.refresh

logout_session
File: backend/app/stacks/identity_auth/api_router.py
Lines: 356-425
Matched Terms: access_token, refresh_token, session
Calls: Depends, HTTPException, SessionActionApiResponse, datetime.fromtimestamp, getattr, isinstance, router.post, service.logout

logout_all_sessions
File: backend/app/stacks/identity_auth/api_router.py
Lines: 433-484
Matched Terms: authenticate, session, revocation
Calls: Depends, HTTPException, LogoutAllApiResponse, getattr, isinstance, router.post, service.logout_all

session_introspection
File: backend/app/stacks/identity_auth/api_router.py
Lines: 492-496
Matched Terms: authenticate, session
Calls: Depends, get_session_introspection, router.get

login
File: backend/app/stacks/identity_auth/api_router.py
Lines: 72-76
Matched Terms: login
Calls: NONE EXTRACTED

refresh
File: backend/app/stacks/identity_auth/api_router.py
Lines: 82-87
Matched Terms: refresh_token
Calls: NONE EXTRACTED

logout
File: backend/app/stacks/identity_auth/api_router.py
Lines: 89-94
Matched Terms: refresh_token
Calls: NONE EXTRACTED

__post_init__
File: backend/app/stacks/identity_auth/contracts.py
Lines: 21-43
Matched Terms: access_token, refresh_token
Calls: ValueError

__post_init__
File: backend/app/stacks/identity_auth/contracts.py
Lines: 61-93
Matched Terms: access_token, refresh_token
Calls: MappingProxyType, ValueError, dict, object.__setattr__

provision_dev_owner
File: backend/app/stacks/identity_auth/dev_owner_provisioner.py
Lines: 38-105
Matched Terms: verify_password, password, email, session, commit
Calls: DevOwnerProvisioningResult, IdentityUserRepository, async_session, engine.dispose, hash_password, repository.create, repository.get_by_email, repository.update_identity_security_state, repository.update_password_hash, session.commit, session.refresh, verify_password

__init__
File: backend/app/stacks/identity_auth/login_service.py
Lines: 28-70
Matched Terms: verify_password, password, refresh_token, session, commit, rollback
Calls: ValueError

login
File: backend/app/stacks/identity_auth/login_service.py
Lines: 72-227
Matched Terms: login, verify_password, password, email, access_token, refresh_token, session, commit, rollback
Calls: AuthenticationRejectedError, AuthenticationTokenPair, bool, canonical_role_value, getattr, isinstance, normalize_email, normalize_subscription_tier, self._commit, self._hash_refresh_token, self._perform_dummy_verification, self._refresh_session_repository.create, self._rollback, self._token_issuer.issue_access_token, self._token_issuer.issue_refresh_token, self._user_repository.get_by_email, self._verify_password

_perform_dummy_verification
File: backend/app/stacks/identity_auth/login_service.py
Lines: 229-236
Matched Terms: verify_password, password
Calls: self._verify_password

mock_hash_password
File: backend/app/stacks/identity_auth/mock_runtime.py
Lines: 232-252
Matched Terms: password
Calls: ('mock-password-pepper:' + password).encode, ValueError, hashlib.sha256, hashlib.sha256(('mock-password-pepper:' + password).encode('utf-8')).hexdigest

mock_verify_password
File: backend/app/stacks/identity_auth/mock_runtime.py
Lines: 255-266
Matched Terms: verify_password, password
Calls: hmac.compare_digest, mock_hash_password

mock_hash_refresh_token
File: backend/app/stacks/identity_auth/mock_runtime.py
Lines: 269-284
Matched Terms: refresh_token
Calls: ('mock-refresh-pepper:' + token).encode, ValueError, hashlib.sha256, hashlib.sha256(('mock-refresh-pepper:' + token).encode('utf-8')).hexdigest

__init__
File: backend/app/stacks/identity_auth/mock_runtime.py
Lines: 47-51
Matched Terms: email
Calls: NONE EXTRACTED

get_by_email
File: backend/app/stacks/identity_auth/mock_runtime.py
Lines: 53-59
Matched Terms: email
Calls: self.users_by_email.get

create
File: backend/app/stacks/identity_auth/mock_runtime.py
Lines: 61-86
Matched Terms: password, email
Calls: MockIdentityUser, RuntimeError, str, uuid4

__init__
File: backend/app/stacks/identity_auth/mock_runtime.py
Lines: 90-95
Matched Terms: session
Calls: NONE EXTRACTED

create
File: backend/app/stacks/identity_auth/mock_runtime.py
Lines: 97-123
Matched Terms: session
Calls: MockRefreshSession, RuntimeError, self.sessions.append

__init__
File: backend/app/stacks/identity_auth/mock_runtime.py
Lines: 127-131
Matched Terms: commit, rollback
Calls: NONE EXTRACTED

commit
File: backend/app/stacks/identity_auth/mock_runtime.py
Lines: 133-139
Matched Terms: commit
Calls: RuntimeError

rollback
File: backend/app/stacks/identity_auth/mock_runtime.py
Lines: 141-142
Matched Terms: rollback
Calls: NONE EXTRACTED

issue_access_token
File: backend/app/stacks/identity_auth/mock_runtime.py
Lines: 153-190
Matched Terms: access_token
Calls: IssuedServiceToken, RuntimeError, datetime.now, dict, timedelta

issue_refresh_token
File: backend/app/stacks/identity_auth/mock_runtime.py
Lines: 192-229
Matched Terms: refresh_token
Calls: IssuedServiceToken, RuntimeError, datetime.now, dict, timedelta

__init__
File: backend/app/stacks/identity_auth/mock_runtime.py
Lines: 288-343
Matched Terms: login, verify_password, password, refresh_token, session, commit, rollback
Calls: LoginService, MockIdentityUserRepository, MockRefreshSessionRepository, MockServiceTokenIssuer, MockTransactionBoundary, RegistrationService, mock_hash_password

validate_replacement_password
File: backend/app/stacks/identity_auth/password_change_service.py
Lines: 32-55
Matched Terms: password
Calls: PasswordChangeRejectedError, all, bool, isinstance, len, re.search

__init__
File: backend/app/stacks/identity_auth/password_change_service.py
Lines: 59-70
Matched Terms: session, commit, rollback
Calls: NONE EXTRACTED

replace_required_password
File: backend/app/stacks/identity_auth/password_change_service.py
Lines: 72-169
Matched Terms: verify_password, password, session, commit, rollback
Calls: PasswordChangeRejectedError, PasswordChangeResult, datetime.now, hash_password, isinstance, self._commit, self._refresh_repository.revoke_all_for_user, self._rollback, self._user_repository.get_by_id, self._user_repository.update_identity_security_state, self._user_repository.update_password_hash, validate_replacement_password, verify_password

_derive
File: backend/app/stacks/identity_auth/passwords.py
Lines: 22-53
Matched Terms: password
Calls: TypeError, ValueError, hashlib.scrypt, isinstance, password.encode

hash_password
File: backend/app/stacks/identity_auth/passwords.py
Lines: 56-92
Matched Terms: password
Calls: _derive, base64.urlsafe_b64encode, base64.urlsafe_b64encode(derived).decode, base64.urlsafe_b64encode(salt).decode, os.urandom

verify_password
File: backend/app/stacks/identity_auth/passwords.py
Lines: 95-174
Matched Terms: verify_password, password
Calls: InvalidPasswordHashError, _derive, base64.urlsafe_b64decode, encoded_hash.split, hash_text.encode, hmac.compare_digest, int, salt_text.encode

hash_refresh_token
File: backend/app/stacks/identity_auth/refresh_token_hashing.py
Lines: 7-35
Matched Terms: refresh_token
Calls: ValueError, hmac.new, hmac.new(pepper, token.encode('utf-8'), hashlib.sha256).hexdigest, isinstance, len, token.encode

verify_refresh_token_hash
File: backend/app/stacks/identity_auth/refresh_token_hashing.py
Lines: 38-52
Matched Terms: refresh_token
Calls: hash_refresh_token, hmac.compare_digest

__init__
File: backend/app/stacks/identity_auth/registration_service.py
Lines: 20-37
Matched Terms: password, commit, rollback
Calls: NONE EXTRACTED

register
File: backend/app/stacks/identity_auth/registration_service.py
Lines: 39-123
Matched Terms: password, email, commit, rollback
Calls: RegisteredIdentity, RegistrationRejectedError, command.display_name.strip, isinstance, len, normalize_email, self._commit, self._hash_password, self._rollback, self._user_repository.create, self._user_repository.get_by_email

__init__
File: backend/app/stacks/identity_auth/repositories.py
Lines: 73-77
Matched Terms: session
Calls: NONE EXTRACTED

create
File: backend/app/stacks/identity_auth/repositories.py
Lines: 79-117
Matched Terms: password, email, session
Calls: IdentityUser, ValueError, bool, normalize_email, normalize_identity_role, self._session.add, self._session.flush

get_by_id
File: backend/app/stacks/identity_auth/repositories.py
Lines: 119-126
Matched Terms: session
Calls: self._session.get

get_by_email
File: backend/app/stacks/identity_auth/repositories.py
Lines: 128-145
Matched Terms: email, session
Calls: (await self._session.execute(statement)).scalar_one_or_none, normalize_email, select, select(IdentityUser).where, self._session.execute

update_identity_security_state
File: backend/app/stacks/identity_auth/repositories.py
Lines: 147-166
Matched Terms: password, session
Calls: bool, normalize_identity_role, self._session.flush

update_password_hash
File: backend/app/stacks/identity_auth/repositories.py
Lines: 168-186
Matched Terms: password, session
Calls: ValueError, isinstance, self._session.flush

__init__
File: backend/app/stacks/identity_auth/repositories.py
Lines: 196-200
Matched Terms: session
Calls: NONE EXTRACTED

create
File: backend/app/stacks/identity_auth/repositories.py
Lines: 202-247
Matched Terms: session
Calls: ValueError, _IdentityRefreshSession, _refresh_uuid4, self._session.add, self._session.flush, str

get_by_token_id
File: backend/app/stacks/identity_auth/repositories.py
Lines: 249-274
Matched Terms: session
Calls: (await self._session.execute(statement)).scalar_one_or_none, _refresh_select, _refresh_select(_IdentityRefreshSession).where, self._session.execute, statement.with_for_update

revoke
File: backend/app/stacks/identity_auth/repositories.py
Lines: 276-287
Matched Terms: session
Calls: self._session.flush

revoke_family
File: backend/app/stacks/identity_auth/repositories.py
Lines: 289-318
Matched Terms: session
Calls: _IdentityRefreshSession.revoked_at.is_, _refresh_update, _refresh_update(_IdentityRefreshSession).where, _refresh_update(_IdentityRefreshSession).where(_IdentityRefreshSession.family_id == family_id).where, _refresh_update(_IdentityRefreshSession).where(_IdentityRefreshSession.family_id == family_id).where(_IdentityRefreshSession.revoked_at.is_(None)).values, int, self._session.execute

revoke_all_for_user
File: backend/app/stacks/identity_auth/repositories.py
Lines: 320-349
Matched Terms: session
Calls: _IdentityRefreshSession.revoked_at.is_, _refresh_update, _refresh_update(_IdentityRefreshSession).where, _refresh_update(_IdentityRefreshSession).where(_IdentityRefreshSession.user_id == user_id).where, _refresh_update(_IdentityRefreshSession).where(_IdentityRefreshSession.user_id == user_id).where(_IdentityRefreshSession.revoked_at.is_(None)).values, int, self._session.execute

delete_expired
File: backend/app/stacks/identity_auth/repositories.py
Lines: 351-375
Matched Terms: session
Calls: _refresh_datetime.now, _refresh_delete, _refresh_delete(_IdentityRefreshSession).where, int, self._session.execute

_unauthorized
File: backend/app/stacks/identity_auth/route_protection.py
Lines: 254-267
Matched Terms: authenticate
Calls: JSONResponse

_authenticate_request
File: backend/app/stacks/identity_auth/route_protection.py
Lines: 312-328
Matched Terms: authenticate, revocation
Calls: _authenticate_with_durable_revocation, _extract_bearer_credentials

_authenticate_with_durable_revocation
File: backend/app/stacks/identity_auth/route_protection.py
Lines: 332-362
Matched Terms: authenticate, session, revocation
Calls: AccessTokenRevocationRepository, async_session, authenticate_bearer_credentials, getattr, repository.is_revoked

_load_identity_authorization_state
File: backend/app/stacks/identity_auth/route_protection.py
Lines: 425-447
Matched Terms: password, session
Calls: IdentityUserRepository, async_session, repository.get_by_id

enforce_route_policy
File: backend/app/stacks/identity_auth/route_protection.py
Lines: 450-859
Matched Terms: authenticate, password
Calls: _authenticate_request, _forbidden, _load_identity_authorization_state, _principal_roles, _unauthorized, bool, call_next, create_trace_id, emit_runtime_step, finish, getattr, identity_state.get, perf_counter, request.headers.get, resolve_route_policy, str

build_authentication_runtime
File: backend/app/stacks/identity_auth/runtime_adapter.py
Lines: 273-343
Matched Terms: login, verify_password, password, refresh_token, session, commit, rollback
Calls: EnvironmentJwtTokenIssuer, IdentityUserRepository, LoginService, RefreshSessionRepository, RegistrationService, hash_password, hash_refresh_token, load_jwt_secret

authentication_runtime
File: backend/app/stacks/identity_auth/runtime_adapter.py
Lines: 347-364
Matched Terms: login, session, commit
Calls: async_session, build_authentication_runtime

build_session_lifecycle_runtime
File: backend/app/stacks/identity_auth/runtime_adapter.py
Lines: 367-451
Matched Terms: refresh_token, session, revocation, commit, rollback
Calls: AccessTokenRevocationRepository, EnvironmentJwtTokenIssuer, IdentityUserRepository, RefreshSessionRepository, RefreshSessionService, SessionLifecycleService, ValidatedRefreshIdentity, _as_identifier, _claim_value, hash_refresh_token, load_jwt_secret, validate_refresh_token, verify_refresh_token_hash

session_lifecycle_runtime
File: backend/app/stacks/identity_auth/runtime_adapter.py
Lines: 455-461
Matched Terms: session
Calls: async_session, build_session_lifecycle_runtime

issue_access_token
File: backend/app/stacks/identity_auth/runtime_adapter.py
Lines: 192-230
Matched Terms: access_token
Calls: IssuedServiceToken, _as_datetime, _as_identifier, _claim_value, issue_access_token, validate_access_token

issue_refresh_token
File: backend/app/stacks/identity_auth/runtime_adapter.py
Lines: 232-270
Matched Terms: refresh_token
Calls: IssuedServiceToken, _as_datetime, _as_identifier, _claim_value, issue_refresh_token, validate_refresh_token

runtime_refresh_token_hash
File: backend/app/stacks/identity_auth/runtime_adapter.py
Lines: 304-310
Matched Terms: refresh_token
Calls: hash_refresh_token

runtime_validate_refresh_token
File: backend/app/stacks/identity_auth/runtime_adapter.py
Lines: 388-410
Matched Terms: refresh_token
Calls: ValidatedRefreshIdentity, _as_identifier, _claim_value, validate_refresh_token

runtime_hash_refresh_token
File: backend/app/stacks/identity_auth/runtime_adapter.py
Lines: 412-418
Matched Terms: refresh_token
Calls: hash_refresh_token

runtime_verify_refresh_token
File: backend/app/stacks/identity_auth/runtime_adapter.py
Lines: 420-428
Matched Terms: refresh_token
Calls: verify_refresh_token_hash

issue_access_token
File: backend/app/stacks/identity_auth/service_contracts.py
Lines: 96-101
Matched Terms: access_token
Calls: NONE EXTRACTED

issue_refresh_token
File: backend/app/stacks/identity_auth/service_contracts.py
Lines: 103-108
Matched Terms: refresh_token
Calls: NONE EXTRACTED

__init__
File: backend/app/stacks/identity_auth/session_lifecycle_service.py
Lines: 96-139
Matched Terms: refresh_token, session, revocation, commit, rollback
Calls: NONE EXTRACTED

_validated_record
File: backend/app/stacks/identity_auth/session_lifecycle_service.py
Lines: 141-196
Matched Terms: refresh_token, session
Calls: SessionLifecycleRejectedError, isinstance, self._refresh_repository.get_by_token_id, self._validate_refresh_token, self._verify_refresh_token

refresh
File: backend/app/stacks/identity_auth/session_lifecycle_service.py
Lines: 198-333
Matched Terms: access_token, refresh_token, session, commit, rollback
Calls: AuthenticationTokenPair, SessionLifecycleRejectedError, canonical_role_value, normalize_subscription_tier, self._commit, self._hash_refresh_token, self._refresh_service.rotate, self._rollback, self._token_issuer.issue_access_token, self._token_issuer.issue_refresh_token, self._user_repository.get_by_id, self._validated_record

logout
File: backend/app/stacks/identity_auth/session_lifecycle_service.py
Lines: 335-389
Matched Terms: access_token, refresh_token, session, revocation, commit, rollback
Calls: SessionLifecycleRejectedError, self._access_revocation_repository.revoke, self._commit, self._refresh_service.logout, self._rollback, self._validated_record

logout_all
File: backend/app/stacks/identity_auth/session_lifecycle_service.py
Lines: 391-425
Matched Terms: session, commit, rollback
Calls: SessionLifecycleRejectedError, isinstance, self._commit, self._refresh_service.revoke_all, self._rollback

cleanup_expired
File: backend/app/stacks/identity_auth/session_lifecycle_service.py
Lines: 427-448
Matched Terms: session, commit, rollback
Calls: SessionLifecycleRejectedError, self._commit, self._refresh_service.cleanup_expired, self._rollback

test_missing_bearer_credentials_are_unauthorized
File: backend/app/stacks/identity_auth/tests/test_api_dependency.py
Lines: 35-43
Matched Terms: authenticate
Calls: authenticate_bearer_credentials, pytest.raises

test_wrong_scheme_is_unauthorized
File: backend/app/stacks/identity_auth/tests/test_api_dependency.py
Lines: 46-59
Matched Terms: authenticate
Calls: HTTPAuthorizationCredentials, authenticate_bearer_credentials, pytest.raises

test_valid_access_token_returns_principal
File: backend/app/stacks/identity_auth/tests/test_api_dependency.py
Lines: 62-82
Matched Terms: authenticate, access_token
Calls: HTTPAuthorizationCredentials, authenticate_bearer_credentials, issue_access_token

test_refresh_token_is_rejected_by_api_dependency
File: backend/app/stacks/identity_auth/tests/test_api_dependency.py
Lines: 85-102
Matched Terms: authenticate, refresh_token
Calls: HTTPAuthorizationCredentials, authenticate_bearer_credentials, issue_refresh_token, pytest.raises

test_malformed_token_is_unauthorized
File: backend/app/stacks/identity_auth/tests/test_api_dependency.py
Lines: 105-118
Matched Terms: authenticate
Calls: HTTPAuthorizationCredentials, authenticate_bearer_credentials, pytest.raises

build_test_app
File: backend/app/stacks/identity_auth/tests/test_api_route_contract.py
Lines: 95-115
Matched Terms: login
Calls: FastAPI, app.include_router

test_registration_contract
File: backend/app/stacks/identity_auth/tests/test_api_route_contract.py
Lines: 118-144
Matched Terms: password, email
Calls: FakeRegistrationService, RegistrationCommand, TestClient, build_test_app, client.post, response.json

test_registration_failure_is_generic
File: backend/app/stacks/identity_auth/tests/test_api_route_contract.py
Lines: 147-179
Matched Terms: password, email
Calls: FakeRegistrationService, RuntimeError, TestClient, build_test_app, client.post, response.json

test_login_contract
File: backend/app/stacks/identity_auth/tests/test_api_route_contract.py
Lines: 182-210
Matched Terms: login, password, email, access_token, refresh_token
Calls: FakeLoginService, LoginCommand, TestClient, build_test_app, client.post, response.json

test_login_failure_is_generic
File: backend/app/stacks/identity_auth/tests/test_api_route_contract.py
Lines: 213-249
Matched Terms: login, authenticate, password, email
Calls: FakeLoginService, RuntimeError, TestClient, build_test_app, client.post, response.json

register
File: backend/app/stacks/identity_auth/tests/test_api_route_contract.py
Lines: 38-51
Matched Terms: email
Calls: RegisteredIdentity, command.email.lower

login
File: backend/app/stacks/identity_auth/tests/test_api_route_contract.py
Lines: 63-92
Matched Terms: login, access_token, refresh_token
Calls: AuthenticationTokenPair, datetime.now, timedelta

test_route_policy_inventory
File: backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py
Lines: 51-90
Matched Terms: login, authenticate
Calls: route_protection.resolve_route_policy

test_authenticated_route_rejects_missing_token
File: backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py
Lines: 105-118
Matched Terms: authenticate
Calls: TestClient, build_test_app, client.get

test_authenticated_route_accepts_principal
File: backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py
Lines: 121-168
Matched Terms: authenticate, password
Calls: SimpleNamespace, TestClient, build_test_app, client.get, monkeypatch.setattr

test_admin_route_rejects_non_admin
File: backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py
Lines: 171-218
Matched Terms: authenticate, password
Calls: SimpleNamespace, TestClient, build_test_app, client.post, monkeypatch.setattr

test_admin_route_accepts_server_claim
File: backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py
Lines: 221-268
Matched Terms: authenticate, password
Calls: SimpleNamespace, TestClient, build_test_app, client.post, monkeypatch.setattr

test_refresh_token_validation_failure_is_unauthorized
File: backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py
Lines: 283-312
Matched Terms: authenticate, refresh_token
Calls: RuntimeError, TestClient, build_test_app, client.get, monkeypatch.setattr

load_identity_state
File: backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py
Lines: 137-147
Matched Terms: password
Calls: NONE EXTRACTED

load_identity_state
File: backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py
Lines: 187-197
Matched Terms: password
Calls: NONE EXTRACTED

load_identity_state
File: backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py
Lines: 237-247
Matched Terms: password
Calls: NONE EXTRACTED

test_auth_router_has_complete_session_lifecycle
File: backend/app/stacks/identity_auth/tests/test_canonical_router_inclusion.py
Lines: 95-128
Matched Terms: login, session
Calls: NONE EXTRACTED

test_controlled_local_registration_and_login
File: backend/app/stacks/identity_auth/tests/test_canonical_router_inclusion.py
Lines: 131-182
Matched Terms: login, password, email, access_token, refresh_token
Calls: FastAPI, QualificationLoginService, QualificationRegistrationService, TestClient, app.include_router, client.post, login.json

register
File: backend/app/stacks/identity_auth/tests/test_canonical_router_inclusion.py
Lines: 32-40
Matched Terms: email
Calls: RegisteredIdentity, command.email.lower

login
File: backend/app/stacks/identity_auth/tests/test_canonical_router_inclusion.py
Lines: 44-68
Matched Terms: login, access_token, refresh_token
Calls: AuthenticationTokenPair, datetime.now, timedelta

test_registration_with_display_name
File: backend/app/stacks/identity_auth/tests/test_display_name.py
Lines: 18-63
Matched Terms: password, email, commit, rollback
Calls: AsyncMock, MagicMock, RegistrationCommand, RegistrationService, mock_user_repo.create.assert_called_once_with, service.register

test_registration_with_trimmed_display_name
File: backend/app/stacks/identity_auth/tests/test_display_name.py
Lines: 67-110
Matched Terms: password, email, commit, rollback
Calls: AsyncMock, MagicMock, RegistrationCommand, RegistrationService, mock_user_repo.create.assert_called_once_with, service.register

test_registration_with_empty_display_name
File: backend/app/stacks/identity_auth/tests/test_display_name.py
Lines: 114-141
Matched Terms: password, email, commit, rollback
Calls: AsyncMock, MagicMock, RegistrationCommand, RegistrationService, pytest.raises, service.register, str

test_registration_with_long_display_name
File: backend/app/stacks/identity_auth/tests/test_display_name.py
Lines: 145-174
Matched Terms: password, email, commit, rollback
Calls: AsyncMock, MagicMock, RegistrationCommand, RegistrationService, pytest.raises, service.register, str

test_registration_without_display_name
File: backend/app/stacks/identity_auth/tests/test_display_name.py
Lines: 178-221
Matched Terms: password, email, commit, rollback
Calls: AsyncMock, MagicMock, RegistrationCommand, RegistrationService, mock_user_repo.create.assert_called_once_with, service.register

test_session_introspection_includes_display_name
File: backend/app/stacks/identity_auth/tests/test_display_name.py
Lines: 225-253
Matched Terms: password, email, session
Calls: AsyncMock, MagicMock, get_session_introspection

test_identity_user_schema_contract
File: backend/app/stacks/identity_auth/tests/test_identity_persistence_models.py
Lines: 20-36
Matched Terms: password, email
Calls: inspect

test_refresh_session_schema_contract
File: backend/app/stacks/identity_auth/tests/test_identity_persistence_models.py
Lines: 39-59
Matched Terms: session
Calls: inspect

test_email_normalization_is_canonical
File: backend/app/stacks/identity_auth/tests/test_identity_persistence_models.py
Lines: 62-65
Matched Terms: email
Calls: normalize_email

test_refresh_token_hash_never_contains_raw_token
File: backend/app/stacks/identity_auth/tests/test_identity_persistence_models.py
Lines: 68-92
Matched Terms: refresh_token
Calls: hash_refresh_token, verify_refresh_token_hash

test_user_repository_normalizes_email
File: backend/app/stacks/identity_auth/tests/test_identity_repository.py
Lines: 17-50
Matched Terms: password, email, session
Calls: AsyncMock, IdentityUserRepository, Mock, isinstance, repository.create, session.add.assert_called_once_with, session.flush.assert_awaited_once

test_user_repository_rejects_empty_hash
File: backend/app/stacks/identity_auth/tests/test_identity_repository.py
Lines: 54-65
Matched Terms: password, email
Calls: IdentityUserRepository, Mock, pytest.raises, repository.create

build_service
File: backend/app/stacks/identity_auth/tests/test_login_service.py
Lines: 45-109
Matched Terms: login, verify_password, password, email, access_token, refresh_token, session, commit, rollback
Calls: AsyncMock, LoginService, Mock, issued

active_user
File: backend/app/stacks/identity_auth/tests/test_login_service.py
Lines: 112-122
Matched Terms: password, email
Calls: SimpleNamespace

test_valid_login_issues_separate_tokens_and_session
File: backend/app/stacks/identity_auth/tests/test_login_service.py
Lines: 126-200
Matched Terms: login, verify_password, password, email, access_token, refresh_token, session, commit, rollback
Calls: LoginCommand, active_user, build_service, commit.assert_awaited_once, created.values, hash_refresh_token.assert_called_once_with, refresh_repository.create.assert_awaited_once, rollback.assert_not_awaited, service.login, token_issuer.issue_access_token.assert_awaited_once_with, token_issuer.issue_refresh_token.assert_awaited_once_with, user_repository.get_by_email.assert_awaited_once_with, verify_password.assert_called_once_with

test_unknown_user_and_wrong_password_share_error
File: backend/app/stacks/identity_auth/tests/test_login_service.py
Lines: 204-249
Matched Terms: login, password, email
Calls: LoginCommand, active_user, build_service, pytest.raises, str, unknown_service.login, unknown_verify.assert_called_once_with, wrong_service.login

test_disabled_account_fails_closed
File: backend/app/stacks/identity_auth/tests/test_login_service.py
Lines: 253-288
Matched Terms: login, password, email, access_token, commit, rollback
Calls: LoginCommand, active_user, build_service, commit.assert_not_awaited, pytest.raises, refresh_repository.create.assert_not_awaited, rollback.assert_awaited_once, service.login, token_issuer.issue_access_token.assert_not_awaited

test_inactive_status_fails_closed
File: backend/app/stacks/identity_auth/tests/test_login_service.py
Lines: 292-317
Matched Terms: login, password, email, access_token, commit, rollback
Calls: LoginCommand, active_user, build_service, commit.assert_not_awaited, pytest.raises, rollback.assert_awaited_once, service.login, token_issuer.issue_access_token.assert_not_awaited

test_refresh_session_failure_rolls_back
File: backend/app/stacks/identity_auth/tests/test_login_service.py
Lines: 321-351
Matched Terms: login, password, email, session, commit, rollback
Calls: LoginCommand, RuntimeError, active_user, build_service, commit.assert_not_awaited, pytest.raises, rollback.assert_awaited_once, service.login

test_identical_tokens_fail_closed
File: backend/app/stacks/identity_auth/tests/test_login_service.py
Lines: 355-392
Matched Terms: login, password, email, access_token, refresh_token, commit, rollback
Calls: LoginCommand, active_user, build_service, commit.assert_not_awaited, issued, pytest.raises, refresh_repository.create.assert_not_awaited, rollback.assert_awaited_once, service.login

test_password_hash_is_salted_and_not_plaintext
File: backend/app/stacks/identity_auth/tests/test_password_boundary.py
Lines: 15-30
Matched Terms: password
Calls: first.startswith, hash_password

test_password_verification_accepts_correct_password
File: backend/app/stacks/identity_auth/tests/test_password_boundary.py
Lines: 33-41
Matched Terms: verify_password, password
Calls: hash_password, verify_password

test_password_verification_rejects_wrong_password
File: backend/app/stacks/identity_auth/tests/test_password_boundary.py
Lines: 44-52
Matched Terms: verify_password, password
Calls: hash_password, verify_password

test_empty_password_is_rejected
File: backend/app/stacks/identity_auth/tests/test_password_boundary.py
Lines: 55-61
Matched Terms: password
Calls: hash_password, pytest.raises

test_malformed_password_hash_is_rejected
File: backend/app/stacks/identity_auth/tests/test_password_boundary.py
Lines: 64-71
Matched Terms: verify_password, password
Calls: pytest.raises, verify_password

test_refresh_rotation_revokes_previous_token
File: backend/app/stacks/identity_auth/tests/test_refresh_rotation.py
Lines: 37-79
Matched Terms: access_token, refresh_token, revocation
Calls: InMemoryTokenRevocationStore, issue_refresh_token, pytest.raises, rotate_refresh_token, validate_access_token, validate_refresh_token

test_refresh_token_cannot_be_rotated_twice
File: backend/app/stacks/identity_auth/tests/test_refresh_rotation.py
Lines: 82-103
Matched Terms: refresh_token, revocation
Calls: InMemoryTokenRevocationStore, issue_refresh_token, pytest.raises, rotate_refresh_token

test_complete_mock_registration_and_login_flow
File: backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py
Lines: 19-74
Matched Terms: login, password, email, access_token, refresh_token, session, commit, rollback
Calls: LoginCommand, MockAuthenticationRuntime, RegistrationCommand, len, mock_hash_refresh_token, result.access_token.startswith, result.refresh_token.startswith, runtime.login.login, runtime.registration.register

test_duplicate_registration_rolls_back
File: backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py
Lines: 78-103
Matched Terms: password, email, commit, rollback
Calls: MockAuthenticationRuntime, RegistrationCommand, len, pytest.raises, runtime.registration.register

test_unknown_and_wrong_password_share_error
File: backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py
Lines: 107-148
Matched Terms: login, password, email, session
Calls: LoginCommand, MockAuthenticationRuntime, RegistrationCommand, len, pytest.raises, runtime.login.login, runtime.registration.register, str

test_disabled_account_rejected_before_token_issuance
File: backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py
Lines: 152-184
Matched Terms: login, password, email, session
Calls: LoginCommand, MockAuthenticationRuntime, RegistrationCommand, len, pytest.raises, runtime.login.login, runtime.registration.register

test_access_token_failure_rolls_back
File: backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py
Lines: 188-216
Matched Terms: login, password, email, access_token, session, commit, rollback
Calls: LoginCommand, MockAuthenticationRuntime, RegistrationCommand, len, pytest.raises, runtime.login.login, runtime.registration.register

test_refresh_token_failure_rolls_back
File: backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py
Lines: 220-248
Matched Terms: login, password, email, refresh_token, session, commit, rollback
Calls: LoginCommand, MockAuthenticationRuntime, RegistrationCommand, len, pytest.raises, runtime.login.login, runtime.registration.register

test_refresh_session_failure_rolls_back
File: backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py
Lines: 252-280
Matched Terms: login, password, email, session, commit, rollback
Calls: LoginCommand, MockAuthenticationRuntime, RegistrationCommand, len, pytest.raises, runtime.login.login, runtime.registration.register

test_registration_commit_failure_fails_closed
File: backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py
Lines: 284-301
Matched Terms: password, email, commit, rollback
Calls: MockAuthenticationRuntime, RegistrationCommand, pytest.raises, runtime.registration.register

test_login_commit_failure_fails_closed
File: backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py
Lines: 305-329
Matched Terms: login, password, email, commit, rollback
Calls: LoginCommand, MockAuthenticationRuntime, RegistrationCommand, pytest.raises, runtime.login.login, runtime.registration.register

build_service
File: backend/app/stacks/identity_auth/tests/test_registration_service.py
Lines: 21-66
Matched Terms: password, email, commit, rollback
Calls: AsyncMock, Mock, RegistrationService, SimpleNamespace

test_registration_normalizes_and_hashes_password
File: backend/app/stacks/identity_auth/tests/test_registration_service.py
Lines: 70-116
Matched Terms: password, email, access_token, refresh_token, commit, rollback
Calls: RegistrationCommand, build_service, commit.assert_awaited_once, hasattr, hash_password.assert_called_once_with, repository.create.assert_awaited_once_with, repository.get_by_email.assert_awaited_once_with, rollback.assert_not_awaited, service.register

test_duplicate_registration_fails_generically
File: backend/app/stacks/identity_auth/tests/test_registration_service.py
Lines: 120-140
Matched Terms: password, email, commit, rollback
Calls: RegistrationCommand, build_service, commit.assert_not_awaited, hash_password.assert_not_called, object, pytest.raises, rollback.assert_awaited_once, service.register

test_registration_hash_failure_rolls_back
File: backend/app/stacks/identity_auth/tests/test_registration_service.py
Lines: 144-165
Matched Terms: password, email, commit, rollback
Calls: RegistrationCommand, RuntimeError, build_service, commit.assert_not_awaited, pytest.raises, rollback.assert_awaited_once, service.register

test_empty_password_fails_closed
File: backend/app/stacks/identity_auth/tests/test_registration_service.py
Lines: 169-187
Matched Terms: password, email, commit, rollback
Calls: RegistrationCommand, build_service, commit.assert_not_awaited, pytest.raises, repository.create.assert_not_awaited, rollback.assert_awaited_once, service.register

test_runtime_construction_is_non_mutating
File: backend/app/stacks/identity_auth/tests/test_runtime_adapter.py
Lines: 67-93
Matched Terms: login, session, commit, rollback
Calls: FakeSession, build_authentication_runtime, install_controlled_secret, isinstance, session.commit.assert_not_awaited, session.rollback.assert_not_awaited

test_runtime_fails_closed_without_secret
File: backend/app/stacks/identity_auth/tests/test_runtime_adapter.py
Lines: 96-109
Matched Terms: session
Calls: FakeSession, build_authentication_runtime, monkeypatch.delenv, pytest.raises

test_real_access_and_refresh_token_paths
File: backend/app/stacks/identity_auth/tests/test_runtime_adapter.py
Lines: 113-151
Matched Terms: access_token, refresh_token
Calls: EnvironmentJwtTokenIssuer, install_controlled_secret, issuer.issue_access_token, issuer.issue_refresh_token

__init__
File: backend/app/stacks/identity_auth/tests/test_runtime_adapter.py
Lines: 26-28
Matched Terms: commit, rollback
Calls: AsyncMock

token_pair
File: backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
Lines: 38-59
Matched Terms: access_token, refresh_token
Calls: AuthenticationTokenPair, datetime.now, timedelta

build_app
File: backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
Lines: 100-129
Matched Terms: authenticate, session
Calls: FastAPI, app.include_router, app.middleware, app.middleware('http')

test_lifecycle_route_policy_inventory
File: backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
Lines: 132-155
Matched Terms: authenticate
Calls: route_protection.resolve_route_policy

test_refresh_returns_rotated_pair
File: backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
Lines: 158-184
Matched Terms: access_token, refresh_token
Calls: FakeLifecycleService, TestClient, build_app, client.post, response.json

test_logout_revokes_current_refresh_session
File: backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
Lines: 187-211
Matched Terms: refresh_token, session
Calls: FakeLifecycleService, TestClient, build_app, client.post, response.json

test_refresh_rejection_is_unauthorized
File: backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
Lines: 214-244
Matched Terms: authenticate, refresh_token, session
Calls: RejectingService, SessionLifecycleRejectedError, TestClient, build_app, client.post

test_logout_rejection_is_unauthorized
File: backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
Lines: 247-273
Matched Terms: refresh_token, session
Calls: RejectingService, SessionLifecycleRejectedError, TestClient, build_app, client.post

test_logout_all_uses_access_principal_subject
File: backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
Lines: 276-341
Matched Terms: authenticate, password, session
Calls: FakeLifecycleService, SimpleNamespace, TestClient, app.on_event, build_app, client.post, engine.dispose, monkeypatch.setattr, response.json

test_logout_all_rejects_missing_access_token
File: backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
Lines: 344-357
Matched Terms: access_token
Calls: FakeLifecycleService, TestClient, build_app, client.post

test_refresh_request_forbids_extra_fields
File: backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
Lines: 360-377
Matched Terms: refresh_token
Calls: FakeLifecycleService, TestClient, build_app, client.post

test_logout_request_forbids_extra_fields
File: backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
Lines: 380-397
Matched Terms: refresh_token
Calls: FakeLifecycleService, TestClient, build_app, client.post

refresh
File: backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
Lines: 68-77
Matched Terms: refresh_token
Calls: self.refreshed.append, token_pair

logout
File: backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
Lines: 79-86
Matched Terms: refresh_token
Calls: self.logged_out.append

load_identity_state
File: backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
Lines: 293-303
Matched Terms: password
Calls: NONE EXTRACTED

refresh
File: backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
Lines: 218-225
Matched Terms: refresh_token, session
Calls: SessionLifecycleRejectedError

logout
File: backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
Lines: 251-258
Matched Terms: refresh_token, session
Calls: SessionLifecycleRejectedError

active_user
File: backend/app/stacks/identity_auth/tests/test_stage4f_canonical_claim_propagation.py
Lines: 41-55
Matched Terms: password, email
Calls: SimpleNamespace

test_login_issues_canonical_role_and_tier_claims
File: backend/app/stacks/identity_auth/tests/test_stage4f_canonical_claim_propagation.py
Lines: 59-116
Matched Terms: login, verify_password, password, email, access_token, refresh_token, session, commit, rollback
Calls: AsyncMock, LoginCommand, LoginService, Mock, active_user, issued, issuer.issue_access_token.assert_awaited_once_with, issuer.issue_refresh_token.assert_awaited_once_with, service.login

test_login_rejects_invalid_stored_role
File: backend/app/stacks/identity_auth/tests/test_stage4f_canonical_claim_propagation.py
Lines: 120-154
Matched Terms: login, verify_password, password, email, access_token, refresh_token, session, commit, rollback
Calls: AsyncMock, LoginCommand, LoginService, Mock, active_user, issuer.issue_access_token.assert_not_awaited, pytest.raises, service.login

test_refresh_uses_current_user_claims
File: backend/app/stacks/identity_auth/tests/test_stage4f_canonical_claim_propagation.py
Lines: 158-238
Matched Terms: access_token, refresh_token, session, commit, rollback
Calls: AsyncMock, Mock, SessionLifecycleService, SimpleNamespace, ValidatedRefreshIdentity, active_user, issued, issuer.issue_access_token.assert_awaited_once_with, issuer.issue_refresh_token.assert_awaited_once_with, service.refresh, user_repository.get_by_id.assert_awaited_once_with

test_refresh_rejects_missing_current_user
File: backend/app/stacks/identity_auth/tests/test_stage4f_canonical_claim_propagation.py
Lines: 242-291
Matched Terms: access_token, refresh_token, session, commit, rollback
Calls: AsyncMock, Mock, SessionLifecycleService, SimpleNamespace, ValidatedRefreshIdentity, issuer.issue_access_token.assert_not_awaited, issuer.issue_refresh_token.assert_not_awaited, pytest.raises, service.refresh

test_environment_issuer_signatures_accept_extra_claims
File: backend/app/stacks/identity_auth/tests/test_stage4f_environment_token_issuer_contract.py
Lines: 33-48
Matched Terms: access_token, refresh_token
Calls: getattr, inspect.signature

test_environment_access_issuer_forwards_claims
File: backend/app/stacks/identity_auth/tests/test_stage4f_environment_token_issuer_contract.py
Lines: 52-75
Matched Terms: access_token
Calls: EnvironmentJwtTokenIssuer, issuer.issue_access_token, validate_access_token

test_environment_refresh_issuer_forwards_claims
File: backend/app/stacks/identity_auth/tests/test_stage4f_environment_token_issuer_contract.py
Lines: 79-102
Matched Terms: refresh_token
Calls: EnvironmentJwtTokenIssuer, issuer.issue_refresh_token, validate_refresh_token

test_login_forwards_canonical_claims_to_both_tokens
File: backend/app/stacks/identity_auth/tests/test_stage4f_login_refresh_claims.py
Lines: 40-114
Matched Terms: login, verify_password, password, email, access_token, refresh_token, session, commit, rollback
Calls: AsyncMock, LoginCommand, LoginService, Mock, SimpleNamespace, issued, service.login, token_issuer.issue_access_token.assert_awaited_once_with, token_issuer.issue_refresh_token.assert_awaited_once_with

test_mock_access_issuer_accepts_and_records_claims
File: backend/app/stacks/identity_auth/tests/test_stage4f_mock_identity_contract.py
Lines: 19-36
Matched Terms: access_token
Calls: MockServiceTokenIssuer, issuer.issue_access_token

test_mock_refresh_issuer_accepts_and_records_claims
File: backend/app/stacks/identity_auth/tests/test_stage4f_mock_identity_contract.py
Lines: 40-57
Matched Terms: refresh_token
Calls: MockServiceTokenIssuer, issuer.issue_refresh_token

test_mock_issuer_signatures_match_claim_contract
File: backend/app/stacks/identity_auth/tests/test_stage4f_mock_identity_contract.py
Lines: 60-80
Matched Terms: access_token, refresh_token
Calls: getattr, inspect.signature

test_mock_registration_result_remains_registration_contract
File: backend/app/stacks/identity_auth/tests/test_stage4f_mock_identity_contract.py
Lines: 84-106
Matched Terms: password, email
Calls: MockAuthenticationRuntime, RegistrationCommand, hasattr, runtime.registration.register

test_mock_registration_login_flow_accepts_claim_propagation
File: backend/app/stacks/identity_auth/tests/test_stage4f_mock_identity_contract.py
Lines: 110-133
Matched Terms: login, password, email, access_token, refresh_token
Calls: LoginCommand, MockAuthenticationRuntime, RegistrationCommand, runtime.login.login, runtime.registration.register

test_rotated_refresh_token_receives_canonical_claims
File: backend/app/stacks/identity_auth/tests/test_stage4f_rotated_refresh_claims.py
Lines: 36-123
Matched Terms: access_token, refresh_token, session, revocation, commit, rollback
Calls: AsyncMock, Mock, SessionLifecycleService, SimpleNamespace, ValidatedRefreshIdentity, issued, service.refresh, token_issuer.issue_access_token.assert_awaited_once_with, token_issuer.issue_refresh_token.assert_awaited_once_with

test_revocation_model_exposes_only_safe_fields
File: backend/app/stacks/identity_auth/tests/test_stage5b_a_durable_revocation_repository.py
Lines: 19-52
Matched Terms: password, access_token, refresh_token, revocation
Calls: NONE EXTRACTED

test_revocation_token_id_is_unique
File: backend/app/stacks/identity_auth/tests/test_stage5b_a_durable_revocation_repository.py
Lines: 55-72
Matched Terms: revocation
Calls: tuple

test_repository_rejects_invalid_identifiers
File: backend/app/stacks/identity_auth/tests/test_stage5b_a_durable_revocation_repository.py
Lines: 96-126
Matched Terms: session, revocation
Calls: AccessTokenRevocationRepository, SessionStub, datetime.now, pytest.mark.parametrize, pytest.raises, repository.revoke, timedelta

test_repository_rejects_invalid_lifetime
File: backend/app/stacks/identity_auth/tests/test_stage5b_a_durable_revocation_repository.py
Lines: 130-152
Matched Terms: session, revocation
Calls: AccessTokenRevocationRepository, SessionStub, datetime.now, pytest.raises, repository.revoke

test_logout_persists_access_and_refresh_revocation_before_commit
File: backend/app/stacks/identity_auth/tests/test_stage5b_b_durable_bearer_logout.py
Lines: 20-104
Matched Terms: access_token, refresh_token, session, revocation, commit, rollback
Calls: AsyncMock, Mock, SessionLifecycleService, SimpleNamespace, ValidatedRefreshIdentity, access_repository.revoke.assert_awaited_once, datetime.now, events.append, rollback.assert_not_awaited, service.logout, timedelta

test_logout_rolls_back_both_revocations_on_failure
File: backend/app/stacks/identity_auth/tests/test_stage5b_b_durable_bearer_logout.py
Lines: 108-166
Matched Terms: access_token, refresh_token, session, revocation, commit, rollback
Calls: AsyncMock, Mock, RuntimeError, SessionLifecycleService, SimpleNamespace, ValidatedRefreshIdentity, access_repository.revoke.assert_awaited_once, commit.assert_not_awaited, datetime.now, pytest.raises, rollback.assert_awaited_once, service.logout, timedelta

test_logout_rejects_access_refresh_subject_mismatch
File: backend/app/stacks/identity_auth/tests/test_stage5b_b_durable_bearer_logout.py
Lines: 170-224
Matched Terms: access_token, refresh_token, session, revocation, commit, rollback
Calls: AsyncMock, Mock, SessionLifecycleService, SimpleNamespace, ValidatedRefreshIdentity, access_repository.revoke.assert_not_awaited, commit.assert_not_awaited, datetime.now, pytest.raises, refresh_service.logout.assert_not_awaited, rollback.assert_awaited_once, service.logout, timedelta

commit
File: backend/app/stacks/identity_auth/tests/test_stage5b_b_durable_bearer_logout.py
Lines: 48-49
Matched Terms: commit
Calls: events.append

test_revocation_routes_are_get_only
File: backend/app/stacks/identity_auth/tests/test_stage5b_c_revocation_observability_cleanup.py
Lines: 28-58
Matched Terms: revocation
Calls: isinstance, set

test_revocation_summary_exposes_no_jti
File: backend/app/stacks/identity_auth/tests/test_stage5b_c_revocation_observability_cleanup.py
Lines: 61-107
Matched Terms: password, access_token, refresh_token, revocation
Calls: AdministrativeReadService._revocation_summary, SimpleNamespace, datetime.now, datetime.now(UTC).replace, summary.model_dump, timedelta

test_cleanup_service_commits_success
File: backend/app/stacks/identity_auth/tests/test_stage5b_c_revocation_observability_cleanup.py
Lines: 111-134
Matched Terms: session, revocation, commit, rollback
Calls: AccessTokenRevocationCleanupService, AsyncMock, Mock, service._repository.cleanup_expired.assert_awaited_once, service.cleanup_expired, session.commit.assert_awaited_once, session.rollback.assert_not_awaited

test_cleanup_service_rolls_back_failure
File: backend/app/stacks/identity_auth/tests/test_stage5b_c_revocation_observability_cleanup.py
Lines: 138-160
Matched Terms: session, revocation, commit, rollback
Calls: AccessTokenRevocationCleanupService, AsyncMock, Mock, RuntimeError, pytest.raises, service.cleanup_expired, session.commit.assert_not_awaited, session.rollback.assert_awaited_once

test_replacement_password_policy_rejects_weak_values
File: backend/app/stacks/identity_auth/tests/test_stage9d_b_forced_password_change.py
Lines: 98-106
Matched Terms: password
Calls: pytest.mark.parametrize, pytest.raises, validate_replacement_password

test_replacement_password_policy_accepts_strong_value
File: backend/app/stacks/identity_auth/tests/test_stage9d_b_forced_password_change.py
Lines: 109-112
Matched Terms: password
Calls: validate_replacement_password

test_required_password_change_updates_hash_and_revokes_sessions
File: backend/app/stacks/identity_auth/tests/test_stage9d_b_forced_password_change.py
Lines: 116-168
Matched Terms: verify_password, password, session, commit, rollback
Calls: FakeRefreshRepository, FakeUser, FakeUserRepository, RequiredPasswordChangeService, hash_password, service.replace_required_password, verify_password

test_wrong_temporary_password_fails_closed
File: backend/app/stacks/identity_auth/tests/test_stage9d_b_forced_password_change.py
Lines: 172-213
Matched Terms: password, commit, rollback
Calls: FakeRefreshRepository, FakeUser, FakeUserRepository, RequiredPasswordChangeService, hash_password, pytest.raises, service.replace_required_password

update_password_hash
File: backend/app/stacks/identity_auth/tests/test_stage9d_b_forced_password_change.py
Lines: 47-54
Matched Terms: password
Calls: NONE EXTRACTED

update_identity_security_state
File: backend/app/stacks/identity_auth/tests/test_stage9d_b_forced_password_change.py
Lines: 56-71
Matched Terms: password
Calls: NONE EXTRACTED

commit
File: backend/app/stacks/identity_auth/tests/test_stage9d_b_forced_password_change.py
Lines: 133-135
Matched Terms: commit
Calls: NONE EXTRACTED

rollback
File: backend/app/stacks/identity_auth/tests/test_stage9d_b_forced_password_change.py
Lines: 137-139
Matched Terms: rollback
Calls: NONE EXTRACTED

commit
File: backend/app/stacks/identity_auth/tests/test_stage9d_b_forced_password_change.py
Lines: 189-190
Matched Terms: commit
Calls: NONE EXTRACTED

rollback
File: backend/app/stacks/identity_auth/tests/test_stage9d_b_forced_password_change.py
Lines: 192-193
Matched Terms: rollback
Calls: NONE EXTRACTED

test_session_models_expose_no_secrets
File: backend/app/stacks/identity_auth/tests/test_stage9d_c2_admin_read_models.py
Lines: 55-67
Matched Terms: session
Calls: model_fields

test_admin_routes_are_get_only
File: backend/app/stacks/identity_auth/tests/test_stage9d_c2_admin_read_models.py
Lines: 70-137
Matched Terms: session
Calls: app.openapi, isinstance, method.lower, schema.get, set

test_admin_dependency_is_database_authoritative
File: backend/app/stacks/identity_auth/tests/test_stage9d_c2_admin_read_models.py
Lines: 141-151
Matched Terms: password
Calls: inspect.getsource

test_read_service_does_not_serialize_secret_fields
File: backend/app/stacks/identity_auth/tests/test_stage9d_c2_admin_read_models.py
Lines: 154-168
Matched Terms: password, access_token, refresh_token
Calls: inspect.getsource

test_openapi_contains_only_expected_admin_methods
File: backend/app/stacks/identity_auth/tests/test_stage9d_c2_admin_read_models.py
Lines: 171-214
Matched Terms: session
Calls: app.openapi, operation.lower

test_no_password_reset_route_added_in_c2
File: backend/app/stacks/identity_auth/tests/test_stage9d_c2_admin_read_models.py
Lines: 217-270
Matched Terms: password
Calls: any, app.openapi, isinstance, operation.lower, schema.get

test_missing_secret_fails_closed
File: backend/app/stacks/identity_auth/tests/test_token_contract.py
Lines: 75-89
Matched Terms: access_token
Calls: issue_access_token, monkeypatch.delenv, pytest.raises

test_access_token_round_trip
File: backend/app/stacks/identity_auth/tests/test_token_contract.py
Lines: 92-110
Matched Terms: access_token
Calls: issue_access_token, validate_access_token

test_refresh_token_is_not_accepted_as_access
File: backend/app/stacks/identity_auth/tests/test_token_contract.py
Lines: 113-125
Matched Terms: access_token, refresh_token
Calls: issue_refresh_token, pytest.raises, validate_access_token

test_access_token_is_not_accepted_as_refresh
File: backend/app/stacks/identity_auth/tests/test_token_contract.py
Lines: 128-140
Matched Terms: access_token, refresh_token
Calls: issue_access_token, pytest.raises, validate_refresh_token

test_token_pair_uses_separate_tokens
File: backend/app/stacks/identity_auth/tests/test_token_contract.py
Lines: 143-159
Matched Terms: access_token, refresh_token
Calls: issue_token_pair, validate_access_token, validate_refresh_token

test_expired_token_is_rejected
File: backend/app/stacks/identity_auth/tests/test_token_contract.py
Lines: 162-181
Matched Terms: access_token, refresh_token
Calls: JWTPolicy, issue_access_token, pytest.raises, validate_access_token

test_not_before_claim_is_enforced
File: backend/app/stacks/identity_auth/tests/test_token_contract.py
Lines: 184-196
Matched Terms: access_token
Calls: issue_access_token, pytest.raises, validate_access_token

test_tampered_payload_is_rejected
File: backend/app/stacks/identity_auth/tests/test_token_contract.py
Lines: 199-230
Matched Terms: access_token
Calls: _b64url_decode, _replace_payload, issue_access_token, json.loads, pytest.raises, token.split, validate_access_token

test_wrong_issuer_is_rejected
File: backend/app/stacks/identity_auth/tests/test_token_contract.py
Lines: 233-250
Matched Terms: access_token
Calls: JWTPolicy, issue_access_token, pytest.raises, validate_access_token

test_wrong_audience_is_rejected
File: backend/app/stacks/identity_auth/tests/test_token_contract.py
Lines: 253-270
Matched Terms: access_token
Calls: JWTPolicy, issue_access_token, pytest.raises, validate_access_token

test_malformed_token_is_rejected
File: backend/app/stacks/identity_auth/tests/test_token_contract.py
Lines: 273-280
Matched Terms: access_token
Calls: pytest.raises, validate_access_token

test_reserved_claims_cannot_be_overridden
File: backend/app/stacks/identity_auth/tests/test_token_contract.py
Lines: 283-293
Matched Terms: access_token
Calls: issue_access_token, pytest.raises

issue_token
File: backend/app/stacks/identity_auth/tokens.py
Lines: 157-219
Matched Terms: access_token, refresh_token
Calls: ValueError, _encode, dict, dict(extra_claims or {}).items, int, load_jwt_secret, time.time, uuid.uuid4

issue_access_token
File: backend/app/stacks/identity_auth/tokens.py
Lines: 222-235
Matched Terms: access_token
Calls: issue_token

issue_refresh_token
File: backend/app/stacks/identity_auth/tokens.py
Lines: 238-251
Matched Terms: refresh_token
Calls: issue_token

issue_token_pair
File: backend/app/stacks/identity_auth/tokens.py
Lines: 254-274
Matched Terms: access_token, refresh_token
Calls: TokenPair, issue_access_token, issue_refresh_token

validate_token
File: backend/app/stacks/identity_auth/tokens.py
Lines: 277-548
Matched Terms: access_token, refresh_token, revocation
Calls: ', '.join, ExpiredTokenError, InvalidTokenError, RevokedTokenError, TokenClaims, TokenNotYetValidError, ValueError, _b64url_decode, _sign, f'{encoded_header}.{encoded_payload}'.encode, hmac.compare_digest, int, isinstance, json.loads, len, load_jwt_secret, payload.items, revocation_store.is_revoked, set, sorted, time.time, token.split

validate_access_token
File: backend/app/stacks/identity_auth/tokens.py
Lines: 551-567
Matched Terms: access_token, revocation
Calls: validate_token

validate_refresh_token
File: backend/app/stacks/identity_auth/tokens.py
Lines: 570-586
Matched Terms: refresh_token, revocation
Calls: validate_token

rotate_refresh_token
File: backend/app/stacks/identity_auth/tokens.py
Lines: 589-614
Matched Terms: refresh_token, revocation
Calls: issue_token_pair, revocation_store.revoke, validate_refresh_token

Request and Response Schemas

backend/app/stacks/identity_auth/contracts.py

Class: JWTPolicy
Fields: ['access_token_seconds', 'algorithm', 'audience', 'clock_skew_seconds', 'issuer', 'refresh_token_seconds']
Lines: 13-43

Class: TokenClaims
Fields: ['audience', 'expires_at', 'extra', 'issued_at', 'issuer', 'not_before', 'subject', 'token_id', 'token_type']
Lines: 50-93

Class: TokenPair
Fields: ['access_token', 'refresh_token', 'token_scheme']
Lines: 97-100

Class: AuthenticatedPrincipal
Fields: ['claims', 'expires_at', 'issued_at', 'subject', 'token_id']
Lines: 104-120

backend/app/stacks/identity_auth/service_contracts.py

Class: RegistrationCommand
Fields: ['display_name', 'email', 'password']
Lines: 31-34

Class: RegisteredIdentity
Fields: ['email_normalized', 'status', 'user_id']
Lines: 38-41

Class: LoginCommand
Fields: ['email', 'password']
Lines: 45-47

Class: IssuedServiceToken
Fields: ['expires_at', 'issued_at', 'token', 'token_id']
Lines: 51-55

Class: AuthenticationTokenPair
Fields: ['access_expires_at', 'access_token', 'password_change_required', 'refresh_expires_at', 'refresh_token', 'token_type']
Lines: 59-65

Class: ServiceTokenIssuer
Fields: []
Lines: 93-108

Class: SessionRefreshCommand
Fields: ['refresh_token']
Lines: 128-129

Class: SessionLogoutCommand
Fields: ['refresh_token']
Lines: 133-134

Class: SessionLogoutAllCommand
Fields: ['user_id']
Lines: 138-139

backend/app/stacks/market_data/dto.py

Class: MarketSessionState
Fields: ['AFTER_HOURS', 'CLOSED', 'OPEN', 'PRE_MARKET', 'UNKNOWN']
Lines: 27-32

Class: MarketQuote
Fields: ['ask', 'bid', 'currency', 'delayed', 'metadata', 'observed_at', 'previous_close', 'price', 'provider', 'session', 'symbol', 'volume']
Lines: 160-270

backend/app/stacks/market_data/tests/test_provider_contract.py

Class: ContractFixtureProvider
Fields: []
Lines: 23-99

backend/app/stacks/identity_auth/tests/test_api_route_contract.py

Class: FakeRegistrationService
Fields: []
Lines: 29-51

Class: FakeLoginService
Fields: []
Lines: 54-92

Database Models

backend/app/stacks/identity_auth/access_token_revocation_cleanup_service.py

Class: AccessTokenRevocationCleanupService
Fields: []
Lines: 14-51

backend/app/stacks/identity_auth/mock_runtime.py

Class: MockIdentityUser
Fields: ['display_name', 'email_normalized', 'id', 'is_active', 'password_hash', 'role', 'status', 'subscription_tier']
Lines: 25-34

Class: MockRefreshSession
Fields: ['expires_at', 'issued_at', 'token_hash', 'token_id', 'user_id']
Lines: 38-43

Class: MockIdentityUserRepository
Fields: []
Lines: 46-86

Class: MockRefreshSessionRepository
Fields: []
Lines: 89-123

Class: MockServiceTokenIssuer
Fields: []
Lines: 145-229

Class: MockAuthenticationRuntime
Fields: []
Lines: 287-343

backend/app/stacks/identity_auth/admin_read_api_models.py

Class: AdministrativeUserSummary
Fields: ['created_at', 'email', 'is_active', 'model_config', 'must_change_password', 'role', 'status', 'updated_at', 'user_id']
Lines: 13-41

Class: AdministrativeUserDetail
Fields: ['active_session_count', 'total_session_count']
Lines: 44-53

Class: AdministrativeSessionSummary
Fields: ['expires_at', 'issued_at', 'model_config', 'replaced', 'revoked_at', 'session_id', 'state', 'user_id']
Lines: 56-80

Class: AdministrativeSessionDetail
Fields: ['replacement_session_id', 'token_family_id']
Lines: 83-87

Class: AdministrativeUserListResponse
Fields: ['items', 'limit', 'model_config', 'offset', 'returned']
Lines: 90-114

Class: AdministrativeSessionListResponse
Fields: ['items', 'limit', 'model_config', 'offset', 'returned']
Lines: 117-141

Class: AdministrativeIntrospectionResponse
Fields: ['access_mode', 'authorization_source', 'model_config', 'mutations_enabled', 'session_read_model', 'status', 'user_read_model']
Lines: 144-157

Class: AdministrativeAccessTokenRevocationSummary
Fields: ['created_at', 'expires_at', 'id', 'issued_at', 'reason', 'revoked_at', 'state', 'user_id']
Lines: 160-173

Class: AdministrativeAccessTokenRevocationDetail
Fields: []
Lines: 176-179

Class: AdministrativeAccessTokenRevocationListResponse
Fields: ['limit', 'offset', 'records', 'total']
Lines: 182-190

backend/app/stacks/identity_auth/contracts.py

Class: JWTPolicy
Fields: ['access_token_seconds', 'algorithm', 'audience', 'clock_skew_seconds', 'issuer', 'refresh_token_seconds']
Lines: 13-43

Class: TokenClaims
Fields: ['audience', 'expires_at', 'extra', 'issued_at', 'issuer', 'not_before', 'subject', 'token_id', 'token_type']
Lines: 50-93

Class: TokenPair
Fields: ['access_token', 'refresh_token', 'token_scheme']
Lines: 97-100

Class: AuthenticatedPrincipal
Fields: ['claims', 'expires_at', 'issued_at', 'subject', 'token_id']
Lines: 104-120

backend/app/stacks/identity_auth/api_router.py

Class: LoginApiService
Fields: []
Lines: 69-76

Class: SessionLifecycleApiService
Fields: []
Lines: 79-101

backend/app/stacks/identity_auth/password_change_service.py

Class: PasswordChangeRejectedError
Fields: []
Lines: 18-19

Class: PasswordChangeResult
Fields: ['changed_at', 'revoked_sessions', 'user_id']
Lines: 26-29

Class: RequiredPasswordChangeService
Fields: []
Lines: 58-169

backend/app/stacks/identity_auth/admin_mutation_service.py

Class: AdministrativeUserMutationService
Fields: []
Lines: 154-536

backend/app/stacks/identity_auth/models.py

Class: IdentityUser
Fields: ['__table_args__', '__tablename__', 'created_at', 'display_name', 'email_normalized', 'id', 'is_active', 'must_change_password', 'password_hash', 'refresh_sessions', 'role', 'status', 'subscription_tier', 'updated_at']
Lines: 33-148

Class: IdentityRefreshSession
Fields: ['__table_args__', '__tablename__', 'created_at', 'expires_at', 'family_id', 'id', 'issued_at', 'last_used_at', 'replaced_by', 'revoked_at', 'token_hash', 'token_id', 'user', 'user_id']
Lines: 151-259

backend/app/stacks/identity_auth/admin_read_dependencies.py

Class: AdministrativePrincipal
Fields: ['role', 'user_id']
Lines: 51-53

backend/app/stacks/identity_auth/admin_read_models.py

Class: AdministrativeReadService
Fields: ['__slots__']
Lines: 277-631

backend/app/stacks/identity_auth/authorization_policy.py

Class: AuthorizationRole
Fields: ['ADMIN', 'DEVELOPER', 'USER']
Lines: 9-12

backend/app/stacks/identity_auth/service_contracts.py

Class: RegistrationCommand
Fields: ['display_name', 'email', 'password']
Lines: 31-34

Class: RegisteredIdentity
Fields: ['email_normalized', 'status', 'user_id']
Lines: 38-41

Class: LoginCommand
Fields: ['email', 'password']
Lines: 45-47

Class: IssuedServiceToken
Fields: ['expires_at', 'issued_at', 'token', 'token_id']
Lines: 51-55

Class: AuthenticationTokenPair
Fields: ['access_expires_at', 'access_token', 'password_change_required', 'refresh_expires_at', 'refresh_token', 'token_type']
Lines: 59-65

Class: ServiceTokenIssuer
Fields: []
Lines: 93-108

Class: SessionRefreshCommand
Fields: ['refresh_token']
Lines: 128-129

Class: SessionLogoutCommand
Fields: ['refresh_token']
Lines: 133-134

Class: SessionLogoutAllCommand
Fields: ['user_id']
Lines: 138-139

backend/app/stacks/identity_auth/dev_owner_provisioner.py

Class: DevOwnerProvisioningResult
Fields: ['created', 'email', 'must_change_password', 'role', 'temporary_password_valid', 'user_id']
Lines: 29-35

backend/app/stacks/identity_auth/session_lifecycle_service.py

Class: SessionLifecycleRejectedError
Fields: []
Lines: 42-45

Class: ValidatedRefreshIdentity
Fields: ['subject', 'token_id']
Lines: 49-51

Class: SessionLifecycleService
Fields: []
Lines: 95-448

backend/app/stacks/identity_auth/access_token_revocation_models.py

Class: IdentityAccessTokenRevocation
Fields: ['__table_args__', '__tablename__', 'created_at', 'expires_at', 'id', 'issued_at', 'reason', 'revoked_at', 'token_id', 'user_id']
Lines: 30-112

backend/app/stacks/identity_auth/session_service.py

Class: RefreshSessionError
Fields: []
Lines: 19-20

Class: RefreshSessionNotFoundError
Fields: []
Lines: 23-26

Class: RefreshSessionExpiredError
Fields: []
Lines: 29-32

Class: RefreshTokenReuseDetectedError
Fields: []
Lines: 35-38

Class: RotationResult
Fields: ['family_id', 'previous_token_id', 'replacement_token_id']
Lines: 42-45

Class: RefreshSessionService
Fields: []
Lines: 48-174

backend/app/stacks/identity_auth/admin_mutation_api_models.py

Class: AdministrativeMutationResponse
Fields: ['action', 'sessions_revoked', 'status', 'user_id']
Lines: 6-13

Class: AdministrativeTemporaryPasswordResponse
Fields: ['must_change_password', 'temporary_password']
Lines: 16-22

Class: AdministrativeDeleteResponse
Fields: ['action', 'deleted', 'status', 'user_id']
Lines: 25-29

backend/app/stacks/identity_auth/api_models.py

Class: RegistrationApiRequest
Fields: ['display_name', 'email', 'model_config', 'password']
Lines: 10-32

Class: LoginApiRequest
Fields: ['email', 'model_config', 'password']
Lines: 35-52

Class: LoginTokenApiResponse
Fields: ['access_token', 'model_config', 'password_change_required', 'refresh_token', 'token_type']
Lines: 66-84

Class: ChangeRequiredPasswordApiRequest
Fields: ['current_password', 'model_config', 'new_password']
Lines: 87-103

Class: ChangeRequiredPasswordApiResponse
Fields: ['model_config', 'revoked_sessions', 'status']
Lines: 106-118

Class: RefreshTokenApiRequest
Fields: ['model_config', 'refresh_token']
Lines: 121-133

Class: LogoutApiRequest
Fields: ['model_config', 'refresh_token']
Lines: 136-148

Class: SessionTokenApiResponse
Fields: ['access_token', 'model_config', 'refresh_token', 'token_type']
Lines: 151-167

Class: SessionActionApiResponse
Fields: ['model_config', 'status']
Lines: 170-178

Class: LogoutAllApiResponse
Fields: ['model_config', 'revoked_sessions', 'status']
Lines: 181-193

backend/app/stacks/identity_auth/runtime_adapter.py

Class: EnvironmentJwtTokenIssuer
Fields: []
Lines: 183-270

backend/app/stacks/identity_auth/repositories.py

Class: IdentityUserRepository
Fields: []
Lines: 72-186

Class: RefreshSessionRepository
Fields: []
Lines: 188-375

backend/app/stacks/identity_auth/access_token_revocation_repository.py

Class: AccessTokenRevocationRepository
Fields: []
Lines: 40-377

backend/app/stacks/identity_auth/login_service.py

Class: LoginService
Fields: []
Lines: 27-236

backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py

Class: FakeLifecycleService
Fields: []
Lines: 62-97

Class: RejectingService
Fields: []
Lines: 215-225

Class: RejectingService
Fields: []
Lines: 248-258

backend/app/stacks/identity_auth/tests/test_stage9d_b_forced_password_change.py

Class: FakeUser
Fields: ['id', 'is_active', 'must_change_password', 'password_hash', 'role', 'status']
Lines: 21-27

Class: FakeUserRepository
Fields: []
Lines: 30-71

Class: FakeRefreshRepository
Fields: []
Lines: 74-85

backend/app/stacks/identity_auth/tests/test_stage9d_c5_k1_session_introspection.py

Class: FakeIdentityUserRepository
Fields: []
Lines: 22-29

backend/app/stacks/identity_auth/tests/test_runtime_adapter.py

Class: FakeSession
Fields: []
Lines: 25-51

backend/app/stacks/identity_auth/tests/test_stage5b_a_durable_revocation_repository.py

Class: SessionStub
Fields: []
Lines: 101-102

Class: SessionStub
Fields: []
Lines: 131-132

backend/app/stacks/identity_auth/tests/test_api_route_contract.py

Class: FakeRegistrationService
Fields: []
Lines: 29-51

Class: FakeLoginService
Fields: []
Lines: 54-92

backend/app/stacks/identity_auth/tests/test_canonical_router_inclusion.py

Class: QualificationRegistrationService
Fields: []
Lines: 31-40

Class: QualificationLoginService
Fields: []
Lines: 43-68

Password Verification Files

backend/app/stacks/identity_auth/admin_mutation_service.py
backend/app/stacks/identity_auth/dev_owner_provisioner.py
backend/app/stacks/identity_auth/login_service.py
backend/app/stacks/identity_auth/mock_runtime.py
backend/app/stacks/identity_auth/models.py
backend/app/stacks/identity_auth/password_change_service.py
backend/app/stacks/identity_auth/passwords.py
backend/app/stacks/identity_auth/repositories.py
backend/app/stacks/identity_auth/runtime_adapter.py
backend/app/stacks/identity_auth/tests/test_display_name.py
backend/app/stacks/identity_auth/tests/test_identity_persistence_models.py
backend/app/stacks/identity_auth/tests/test_identity_repository.py
backend/app/stacks/identity_auth/tests/test_login_service.py
backend/app/stacks/identity_auth/tests/test_password_boundary.py
backend/app/stacks/identity_auth/tests/test_registration_service.py
backend/app/stacks/identity_auth/tests/test_stage4f_canonical_claim_propagation.py
backend/app/stacks/identity_auth/tests/test_stage4f_login_refresh_claims.py
backend/app/stacks/identity_auth/tests/test_stage5b_a_durable_revocation_repository.py
backend/app/stacks/identity_auth/tests/test_stage5b_c_revocation_observability_cleanup.py
backend/app/stacks/identity_auth/tests/test_stage9d_b_forced_password_change.py
backend/app/stacks/identity_auth/tests/test_stage9d_c2_admin_read_models.py

Token Files

backend/app/stacks/identity_auth/access_token_revocation_cleanup_service.py
backend/app/stacks/identity_auth/access_token_revocation_models.py
backend/app/stacks/identity_auth/access_token_revocation_repository.py
backend/app/stacks/identity_auth/admin_mutation_service.py
backend/app/stacks/identity_auth/admin_read_dependencies.py
backend/app/stacks/identity_auth/admin_read_models.py
backend/app/stacks/identity_auth/admin_read_router.py
backend/app/stacks/identity_auth/api_dependencies.py
backend/app/stacks/identity_auth/api_models.py
backend/app/stacks/identity_auth/api_router.py
backend/app/stacks/identity_auth/contracts.py
backend/app/stacks/identity_auth/dependencies.py
backend/app/stacks/identity_auth/login_service.py
backend/app/stacks/identity_auth/mock_runtime.py
backend/app/stacks/identity_auth/refresh_token_hashing.py
backend/app/stacks/identity_auth/route_protection.py
backend/app/stacks/identity_auth/runtime_adapter.py
backend/app/stacks/identity_auth/service_contracts.py
backend/app/stacks/identity_auth/session_lifecycle_service.py
backend/app/stacks/identity_auth/tests/test_api_dependency.py
backend/app/stacks/identity_auth/tests/test_api_route_contract.py
backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py
backend/app/stacks/identity_auth/tests/test_canonical_router_inclusion.py
backend/app/stacks/identity_auth/tests/test_identity_persistence_models.py
backend/app/stacks/identity_auth/tests/test_login_service.py
backend/app/stacks/identity_auth/tests/test_refresh_rotation.py
backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py
backend/app/stacks/identity_auth/tests/test_registration_service.py
backend/app/stacks/identity_auth/tests/test_runtime_adapter.py
backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
backend/app/stacks/identity_auth/tests/test_stage4f_canonical_claim_propagation.py
backend/app/stacks/identity_auth/tests/test_stage4f_environment_token_issuer_contract.py
backend/app/stacks/identity_auth/tests/test_stage4f_login_refresh_claims.py
backend/app/stacks/identity_auth/tests/test_stage4f_mock_identity_contract.py
backend/app/stacks/identity_auth/tests/test_stage4f_rotated_refresh_claims.py
backend/app/stacks/identity_auth/tests/test_stage5b_a_durable_revocation_repository.py
backend/app/stacks/identity_auth/tests/test_stage5b_b_durable_bearer_logout.py
backend/app/stacks/identity_auth/tests/test_stage5b_c_revocation_observability_cleanup.py
backend/app/stacks/identity_auth/tests/test_stage9d_c2_admin_read_models.py
backend/app/stacks/identity_auth/tests/test_token_contract.py
backend/app/stacks/identity_auth/tokens.py

Session Files

backend/app/stacks/identity_auth/access_token_revocation_cleanup_service.py
backend/app/stacks/identity_auth/access_token_revocation_models.py
backend/app/stacks/identity_auth/access_token_revocation_repository.py
backend/app/stacks/identity_auth/admin_mutation_service.py
backend/app/stacks/identity_auth/admin_read_api_models.py
backend/app/stacks/identity_auth/admin_read_dependencies.py
backend/app/stacks/identity_auth/admin_read_models.py
backend/app/stacks/identity_auth/admin_read_router.py
backend/app/stacks/identity_auth/api_dependencies.py
backend/app/stacks/identity_auth/api_router.py
backend/app/stacks/identity_auth/dependencies.py
backend/app/stacks/identity_auth/login_service.py
backend/app/stacks/identity_auth/mock_runtime.py
backend/app/stacks/identity_auth/models.py
backend/app/stacks/identity_auth/route_protection.py
backend/app/stacks/identity_auth/runtime_adapter.py
backend/app/stacks/identity_auth/session_lifecycle_service.py
backend/app/stacks/identity_auth/tests/test_identity_persistence_models.py
backend/app/stacks/identity_auth/tests/test_login_service.py
backend/app/stacks/identity_auth/tests/test_refresh_rotation.py
backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py
backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
backend/app/stacks/identity_auth/tests/test_stage4f_canonical_claim_propagation.py
backend/app/stacks/identity_auth/tests/test_stage4f_login_refresh_claims.py
backend/app/stacks/identity_auth/tests/test_stage4f_rotated_refresh_claims.py
backend/app/stacks/identity_auth/tests/test_stage4f_session_lifecycle_runtime_wiring.py
backend/app/stacks/identity_auth/tests/test_stage5b_a_durable_revocation_repository.py
backend/app/stacks/identity_auth/tests/test_stage5b_b_durable_bearer_logout.py
backend/app/stacks/identity_auth/tests/test_stage5b_c_revocation_observability_cleanup.py
backend/app/stacks/identity_auth/tests/test_stage9d_c2_admin_read_models.py
backend/app/stacks/identity_auth/tokens.py

Cookie Files

No backend cookie-setting file was conclusively identified.

Repository and Persistence Files

backend/app/stacks/chat_public/conversation_store.py
backend/app/stacks/identity_auth/access_token_revocation_repository.py
backend/app/stacks/identity_auth/tests/test_identity_persistence_models.py
backend/app/stacks/identity_auth/tests/test_identity_repository.py
backend/app/stacks/identity_auth/tests/test_refresh_session_persistence.py
backend/app/stacks/identity_auth/tests/test_stage5b_a_durable_revocation_repository.py
backend/app/stacks/journal_ledger/decision_event_repository.py
backend/app/stacks/journal_ledger/tests/test_decision_event_repository.py

Security

email_normalization_detected

True

password_verification_detected

True

access_token_creation_detected

True

refresh_token_creation_detected

True

refresh_token_hashing_detected

True

raw_refresh_persistence_risk_detected

False

cookie_setting_detected

False

httponly_detected

False

secure_cookie_detected

False

samesite_detected

False

disabled_account_check_detected

True

locked_account_check_detected

True

rate_limiting_detected

False

csrf_detected

False

audit_logging_detected

True

last_login_update_detected

False

commit_detected

True

rollback_detected

True

raw_password_logging_risk_detected

False

Loading Behaviour

loading_state_detected

True

error_state_detected

True

success_state_detected

False

duplicate_submit_protection_detected

True

password_visibility_control_detected

False

remember_me_detected

False

return_url_detected

True

responsive_classes_detected

True

accessibility_markers_detected

True

Failure Paths

Unknown Email

UNVERIFIED

Incorrect Password

UNVERIFIED

Disabled Account

UNVERIFIED

Locked Account

UNVERIFIED

Rate-Limited Login

UNVERIFIED

Database Failure

UNVERIFIED

Token Creation Failure

UNVERIFIED

Cookie Creation Failure

UNVERIFIED

Network Failure

Frontend error state detected

Repeated Submission

Duplicate-submit protection detected

Tests

backend/app/stacks/identity_auth/tests/test_api.py

test_registration_api_with_display_name
test_registration_api_without_display_name
test_login_api_request

backend/app/stacks/identity_auth/tests/test_api_route_contract.py

test_registration_contract
test_registration_failure_is_generic
test_login_contract
test_login_failure_is_generic
test_router_is_activated_in_canonical_app

backend/app/stacks/identity_auth/tests/test_api_runtime_binding.py

test_registration_dependency_is_async_generator
test_login_dependency_is_async_generator
test_registration_dependency_contract_annotation
test_login_dependency_contract_annotation
test_runtime_service_types_are_canonical

backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py

test_route_policy_inventory
test_public_route_requires_no_token
test_authenticated_route_rejects_missing_token
test_authenticated_route_accepts_principal
test_admin_route_rejects_non_admin
test_admin_route_accepts_server_claim
test_unknown_route_preserves_not_found
test_refresh_token_validation_failure_is_unauthorized

backend/app/stacks/identity_auth/tests/test_canonical_router_inclusion.py

test_canonical_source_includes_auth_router_once
test_auth_router_has_complete_session_lifecycle
test_controlled_local_registration_and_login

backend/app/stacks/identity_auth/tests/test_login_service.py

test_valid_login_issues_separate_tokens_and_session
test_unknown_user_and_wrong_password_share_error
test_disabled_account_fails_closed
test_inactive_status_fails_closed
test_refresh_session_failure_rolls_back
test_identical_tokens_fail_closed

backend/app/stacks/identity_auth/tests/test_refresh_session_persistence.py

test_rotation_preserves_family_and_revokes_old
test_reuse_revokes_entire_family
test_logout_is_idempotent

backend/app/stacks/identity_auth/tests/test_registration.py

test_successful_registration
test_registration_with_existing_email
test_registration_with_invalid_password

backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py

test_complete_mock_registration_and_login_flow
test_duplicate_registration_rolls_back
test_unknown_and_wrong_password_share_error
test_disabled_account_rejected_before_token_issuance
test_access_token_failure_rolls_back
test_refresh_token_failure_rolls_back
test_refresh_session_failure_rolls_back
test_registration_commit_failure_fails_closed
test_login_commit_failure_fails_closed

backend/app/stacks/identity_auth/tests/test_runtime_adapter.py

test_runtime_construction_is_non_mutating
test_runtime_fails_closed_without_secret
test_real_access_and_refresh_token_paths

backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py

test_lifecycle_route_policy_inventory
test_refresh_returns_rotated_pair
test_logout_revokes_current_refresh_session
test_refresh_rejection_is_unauthorized
test_logout_rejection_is_unauthorized
test_logout_all_uses_access_principal_subject
test_logout_all_rejects_missing_access_token
test_refresh_request_forbids_extra_fields
test_logout_request_forbids_extra_fields

backend/app/stacks/identity_auth/tests/test_stage4f_canonical_claim_propagation.py

test_login_issues_canonical_role_and_tier_claims
test_login_rejects_invalid_stored_role
test_refresh_uses_current_user_claims
test_refresh_rejects_missing_current_user

backend/app/stacks/identity_auth/tests/test_stage4f_login_refresh_claims.py

test_login_forwards_canonical_claims_to_both_tokens

backend/app/stacks/identity_auth/tests/test_stage4f_mock_identity_contract.py

test_mock_access_issuer_accepts_and_records_claims
test_mock_refresh_issuer_accepts_and_records_claims
test_mock_issuer_signatures_match_claim_contract
test_mock_registration_result_remains_registration_contract
test_mock_registration_login_flow_accepts_claim_propagation

backend/app/stacks/identity_auth/tests/test_stage5b_a_durable_revocation_repository.py

test_revocation_model_exposes_only_safe_fields
test_revocation_token_id_is_unique
test_repository_rejects_invalid_identifiers
test_repository_rejects_invalid_lifetime

backend/app/stacks/identity_auth/tests/test_stage5b_b_durable_bearer_logout.py

test_logout_persists_access_and_refresh_revocation_before_commit
test_logout_rolls_back_both_revocations_on_failure
test_logout_rejects_access_refresh_subject_mismatch

backend/app/stacks/identity_auth/tests/test_stage5b_c_revocation_observability_cleanup.py

test_revocation_routes_are_get_only
test_revocation_summary_exposes_no_jti
test_cleanup_service_commits_success
test_cleanup_service_rolls_back_failure

frontend/tests/e2e/02-auth-boundary.spec.ts

login page loads with usable form controls
unauthenticated dashboard access is blocked
unauthenticated admin access is blocked

frontend/tests/e2e/03-public-navigation.spec.ts

homepage renders without browser errors
login page has no empty document
unknown route displays a controlled response

frontend/tests/e2e/04-backend-connectivity.spec.ts

backend documentation endpoint is reachable
backend OpenAPI contract is reachable
protected backend route rejects anonymous request

frontend/tests/e2e/05-authenticated-user-flow.spec.ts

register, login, persist session, and logout
/
/

frontend/tests/e2e/06-dashboard-navigation.spec.ts

/
dashboard, portfolio, and analytics render for a user

frontend/tests/e2e/07-neuro-welcome-briefing.spec.ts

authenticated user can view, close, and reopen the briefing
/

frontend/tests/e2e/08-objective4g-d-authenticated-live-turn.spec.ts

/
qualifies authenticated math, RAG, verification, and replay

frontend/tests/e2e/09-objective4h-b-broad-prompt-matrix.spec.ts

qualifies broad authenticated cognitive behavior

Manual Verification Checklist

[ ] Open /login while logged out

[ ] Open /login while authenticated

[ ] Verify the exact page heading and explanatory text

[ ] Record all input names, IDs, types, and autocomplete values

[ ] Verify successful existing-user login

[ ] Verify incorrect-password rejection

[ ] Verify unknown-email rejection

[ ] Verify disabled-account rejection

[ ] Verify locked-account behavior

[ ] Verify email normalization

[ ] Verify duplicate-submit protection

[ ] Verify loading state

[ ] Verify error state

[ ] Verify access-token claims

[ ] Verify access-token expiry

[ ] Verify refresh-token creation

[ ] Verify refresh-token hash persistence

[ ] Verify no raw refresh token is persisted

[ ] Verify cookie names

[ ] Verify HttpOnly cookie flags

[ ] Verify Secure cookie flags

[ ] Verify SameSite cookie flags

[ ] Verify successful redirect destination

[ ] Verify return URL handling

[ ] Verify authenticated-user redirect away from /login

[ ] Verify no raw password appears in frontend logs

[ ] Verify no raw password appears in backend logs

[ ] Verify login rate limiting

[ ] Verify login audit event

[ ] Verify last-login update

[ ] Verify keyboard navigation

[ ] Verify password-manager autocomplete

[ ] Verify screen-reader labels

[ ] Verify desktop layout

[ ] Verify tablet layout

[ ] Verify mobile layout

[ ] Run existing-user Playwright login flow

Current Gaps

Login rate limiting was not conclusively detected.

FUNCTION FLOW GRAPH

Internet
      │
      ▼
Browser
      │
      ▼
GET /login
      │
      ▼
Next.js Router
      │
      ▼
frontend/proxy.ts
      │
      ▼
frontend/app/layout.tsx
      │
      ▼
frontend/app/login/page.tsx
      │
      ▼
LoginPage Component
      │
      ├────────► Email Input
      ├────────► Password Input
      ├────────► Password Visibility Control
      ├────────► Registration Link
      ├────────► Error Feedback
      └────────► Login Button
                         │
                         ▼
                  Submit Handler
                         │
                         ▼
              Frontend Login Request
                         │
                         ▼
              Frontend API / Proxy
                         │
                         ▼
                  POST /auth/login
                         │
                         ▼
                   login_identity()
                         │
                         ▼
                  Normalize Email
                         │
                         ▼
                    Find User
                         │
             ┌───────────┴────────────┐
             │                        │
             ▼                        ▼
       User Not Found             User Found
             │                        │
             ▼                        ▼
     Authentication Error       Verify Password
                                      │
                          ┌───────────┴───────────┐
                          │                       │
                          ▼                       ▼
                    Incorrect                 Correct
                    Password                 Password
                          │                       │
                          ▼                       ▼
                 Authentication Error   Validate Account State
                                                  │
                                      ┌───────────┴───────────┐
                                      │                       │
                                      ▼                       ▼
                                  Rejected                  Allowed
                                      │                       │
                                      ▼                       ▼
                              Authentication Error   Create Access Token
                                                              │
                                                              ▼
                                                    Create Refresh State
                                                              │
                                                              ▼
                                                       Persist Token Hash
                                                              │
                                                              ▼
                                                       Set Session Cookies
                                                              │
                                                              ▼
                                                        Login Response
                                                              │
                                                              ▼
                                                   Frontend Session Update
                                                              │
                                                              ▼
                                                  Authenticated Destination

Repository Files

Frontend

frontend/app/login/page.tsx
frontend/app/layout.tsx
frontend/proxy.ts

Authentication Frontend Files

frontend/proxy.ts
frontend/lib/backendAuth.ts
frontend/lib/sessionCookies.ts
frontend/tests/e2e/02-auth-boundary.spec.ts
frontend/tests/e2e/05-authenticated-user-flow.spec.ts
frontend/tests/e2e/08-objective4g-d-authenticated-live-turn.spec.ts
frontend/app/login/page.tsx
frontend/app/admin/sessions/page.tsx
frontend/app/components/auth/LogoutButton.tsx
frontend/app/api/auth/register/route.ts
frontend/app/api/auth/session/route.ts
frontend/app/api/auth/change-password/route.ts
frontend/app/api/auth/logout/route.ts
frontend/app/api/auth/login/route.ts

Backend

backend/app/stacks/identity_auth/api_router.py
backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py

Password Verification

backend/app/stacks/identity_auth/admin_mutation_service.py
backend/app/stacks/identity_auth/dev_owner_provisioner.py
backend/app/stacks/identity_auth/login_service.py
backend/app/stacks/identity_auth/mock_runtime.py
backend/app/stacks/identity_auth/models.py
backend/app/stacks/identity_auth/password_change_service.py
backend/app/stacks/identity_auth/passwords.py
backend/app/stacks/identity_auth/repositories.py
backend/app/stacks/identity_auth/runtime_adapter.py
backend/app/stacks/identity_auth/tests/test_display_name.py
backend/app/stacks/identity_auth/tests/test_identity_persistence_models.py
backend/app/stacks/identity_auth/tests/test_identity_repository.py
backend/app/stacks/identity_auth/tests/test_login_service.py
backend/app/stacks/identity_auth/tests/test_password_boundary.py
backend/app/stacks/identity_auth/tests/test_registration_service.py
backend/app/stacks/identity_auth/tests/test_stage4f_canonical_claim_propagation.py
backend/app/stacks/identity_auth/tests/test_stage4f_login_refresh_claims.py
backend/app/stacks/identity_auth/tests/test_stage5b_a_durable_revocation_repository.py
backend/app/stacks/identity_auth/tests/test_stage5b_c_revocation_observability_cleanup.py
backend/app/stacks/identity_auth/tests/test_stage9d_b_forced_password_change.py
backend/app/stacks/identity_auth/tests/test_stage9d_c2_admin_read_models.py

Tokens

backend/app/stacks/identity_auth/access_token_revocation_cleanup_service.py
backend/app/stacks/identity_auth/access_token_revocation_models.py
backend/app/stacks/identity_auth/access_token_revocation_repository.py
backend/app/stacks/identity_auth/admin_mutation_service.py
backend/app/stacks/identity_auth/admin_read_dependencies.py
backend/app/stacks/identity_auth/admin_read_models.py
backend/app/stacks/identity_auth/admin_read_router.py
backend/app/stacks/identity_auth/api_dependencies.py
backend/app/stacks/identity_auth/api_models.py
backend/app/stacks/identity_auth/api_router.py
backend/app/stacks/identity_auth/contracts.py
backend/app/stacks/identity_auth/dependencies.py
backend/app/stacks/identity_auth/login_service.py
backend/app/stacks/identity_auth/mock_runtime.py
backend/app/stacks/identity_auth/refresh_token_hashing.py
backend/app/stacks/identity_auth/route_protection.py
backend/app/stacks/identity_auth/runtime_adapter.py
backend/app/stacks/identity_auth/service_contracts.py
backend/app/stacks/identity_auth/session_lifecycle_service.py
backend/app/stacks/identity_auth/tests/test_api_dependency.py
backend/app/stacks/identity_auth/tests/test_api_route_contract.py
backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py
backend/app/stacks/identity_auth/tests/test_canonical_router_inclusion.py
backend/app/stacks/identity_auth/tests/test_identity_persistence_models.py
backend/app/stacks/identity_auth/tests/test_login_service.py
backend/app/stacks/identity_auth/tests/test_refresh_rotation.py
backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py
backend/app/stacks/identity_auth/tests/test_registration_service.py
backend/app/stacks/identity_auth/tests/test_runtime_adapter.py
backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
backend/app/stacks/identity_auth/tests/test_stage4f_canonical_claim_propagation.py
backend/app/stacks/identity_auth/tests/test_stage4f_environment_token_issuer_contract.py
backend/app/stacks/identity_auth/tests/test_stage4f_login_refresh_claims.py
backend/app/stacks/identity_auth/tests/test_stage4f_mock_identity_contract.py
backend/app/stacks/identity_auth/tests/test_stage4f_rotated_refresh_claims.py
backend/app/stacks/identity_auth/tests/test_stage5b_a_durable_revocation_repository.py
backend/app/stacks/identity_auth/tests/test_stage5b_b_durable_bearer_logout.py
backend/app/stacks/identity_auth/tests/test_stage5b_c_revocation_observability_cleanup.py
backend/app/stacks/identity_auth/tests/test_stage9d_c2_admin_read_models.py
backend/app/stacks/identity_auth/tests/test_token_contract.py
backend/app/stacks/identity_auth/tokens.py

Refresh Sessions

backend/app/stacks/identity_auth/access_token_revocation_cleanup_service.py
backend/app/stacks/identity_auth/access_token_revocation_models.py
backend/app/stacks/identity_auth/access_token_revocation_repository.py
backend/app/stacks/identity_auth/admin_mutation_service.py
backend/app/stacks/identity_auth/admin_read_api_models.py
backend/app/stacks/identity_auth/admin_read_dependencies.py
backend/app/stacks/identity_auth/admin_read_models.py
backend/app/stacks/identity_auth/admin_read_router.py
backend/app/stacks/identity_auth/api_dependencies.py
backend/app/stacks/identity_auth/api_router.py
backend/app/stacks/identity_auth/dependencies.py
backend/app/stacks/identity_auth/login_service.py
backend/app/stacks/identity_auth/mock_runtime.py
backend/app/stacks/identity_auth/models.py
backend/app/stacks/identity_auth/route_protection.py
backend/app/stacks/identity_auth/runtime_adapter.py
backend/app/stacks/identity_auth/session_lifecycle_service.py
backend/app/stacks/identity_auth/tests/test_identity_persistence_models.py
backend/app/stacks/identity_auth/tests/test_login_service.py
backend/app/stacks/identity_auth/tests/test_refresh_rotation.py
backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py
backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
backend/app/stacks/identity_auth/tests/test_stage4f_canonical_claim_propagation.py
backend/app/stacks/identity_auth/tests/test_stage4f_login_refresh_claims.py
backend/app/stacks/identity_auth/tests/test_stage4f_rotated_refresh_claims.py
backend/app/stacks/identity_auth/tests/test_stage4f_session_lifecycle_runtime_wiring.py
backend/app/stacks/identity_auth/tests/test_stage5b_a_durable_revocation_repository.py
backend/app/stacks/identity_auth/tests/test_stage5b_b_durable_bearer_logout.py
backend/app/stacks/identity_auth/tests/test_stage5b_c_revocation_observability_cleanup.py
backend/app/stacks/identity_auth/tests/test_stage9d_c2_admin_read_models.py
backend/app/stacks/identity_auth/tokens.py

Cookies

No canonical cookie file isolated.

Repositories

backend/app/stacks/chat_public/conversation_store.py
backend/app/stacks/identity_auth/access_token_revocation_repository.py
backend/app/stacks/identity_auth/tests/test_identity_persistence_models.py
backend/app/stacks/identity_auth/tests/test_identity_repository.py
backend/app/stacks/identity_auth/tests/test_refresh_session_persistence.py
backend/app/stacks/identity_auth/tests/test_stage5b_a_durable_revocation_repository.py
backend/app/stacks/journal_ledger/decision_event_repository.py
backend/app/stacks/journal_ledger/tests/test_decision_event_repository.py

Tests

backend/app/stacks/identity_auth/tests/test_api.py
backend/app/stacks/identity_auth/tests/test_api_route_contract.py
backend/app/stacks/identity_auth/tests/test_api_runtime_binding.py
backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py
backend/app/stacks/identity_auth/tests/test_canonical_router_inclusion.py
backend/app/stacks/identity_auth/tests/test_login_service.py
backend/app/stacks/identity_auth/tests/test_refresh_session_persistence.py
backend/app/stacks/identity_auth/tests/test_registration.py
backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py
backend/app/stacks/identity_auth/tests/test_runtime_adapter.py
backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
backend/app/stacks/identity_auth/tests/test_stage4f_canonical_claim_propagation.py
backend/app/stacks/identity_auth/tests/test_stage4f_login_refresh_claims.py
backend/app/stacks/identity_auth/tests/test_stage4f_mock_identity_contract.py
backend/app/stacks/identity_auth/tests/test_stage5b_a_durable_revocation_repository.py
backend/app/stacks/identity_auth/tests/test_stage5b_b_durable_bearer_logout.py
backend/app/stacks/identity_auth/tests/test_stage5b_c_revocation_observability_cleanup.py
frontend/tests/e2e/02-auth-boundary.spec.ts
frontend/tests/e2e/03-public-navigation.spec.ts
frontend/tests/e2e/04-backend-connectivity.spec.ts
frontend/tests/e2e/05-authenticated-user-flow.spec.ts
frontend/tests/e2e/06-dashboard-navigation.spec.ts
frontend/tests/e2e/07-neuro-welcome-briefing.spec.ts
frontend/tests/e2e/08-objective4g-d-authenticated-live-turn.spec.ts
frontend/tests/e2e/09-objective4h-b-broad-prompt-matrix.spec.ts

Evidence

runtime/system_inventory/function_path_03_existing_user_login_20260729_233128/function_path_03_existing_user_login_inventory.json
runtime/system_inventory/function_path_03_existing_user_login_20260729_233128/function_path_03_copy_paste_section.txt
runtime/system_inventory/function_path_03_existing_user_login_20260729_233128/source

Launch Dependency

Required Before Launch

YES

Blocks

Existing-user access

Authenticated dashboard entry

Portfolio access

Neuro chat access

Session refresh

Administrative access

Developer access

Controlled early-user launch

Depends On

Public routing

Login page rendering

Frontend validation

Frontend authentication service

Frontend proxy or API boundary

Identity-auth backend route

Credential verification

Account-state validation

Access-token creation

Refresh-session creation

Cookie handling

Database persistence

Error handling

Authenticated redirect

FINAL VERDICT

Function Exists: YES

Frontend Complete: UNVERIFIED

Frontend Connected: UNVERIFIED

Middleware Present: YES

Backend Route Present: YES

Password Verification: DETECTED

Access Token Creation: DETECTED

Refresh Token Creation: DETECTED

Cookie Handling: UNVERIFIED

Rate Limiting: NOT CONCLUSIVELY DETECTED

Relevant Tests: PRESENT

Live Verification: NOT COMPLETE

Launch Ready: UNVERIFIED

Overall Classification

PARTIALLY VERIFIED

Launch Classification

CRITICAL

Existing User Login must be fully verified before launch because
every protected NeuroVest function depends on successful and secure
authentication of an existing account.

---



---

FUNCTION PATH 04 — AUTHENTICATED DASHBOARD / POST-LOGIN LANDING

Function Status

Inventory Status: INITIAL INVENTORY COMPLETE
Implementation Status: IMPLEMENTED — SOURCE VERIFICATION PENDING
Qualification Status: UNVERIFIED
Launch Importance: CRITICAL
Last Updated: 2026-07-29
Evidence Source: runtime/system_inventory/function_path_04_authenticated_dashboard_20260730_015256/function_path_04_authenticated_dashboard_inventory.json

Purpose

The Authenticated Dashboard is the primary application page reached
after a registered user successfully logs into NeuroVest.

Its purpose is to:

- Confirm that the user has a valid authenticated session.
- Protect the dashboard from anonymous access.
- Redirect unauthenticated visitors to login.
- Present the user's primary NeuroVest application state.
- Load user-owned portfolio and position information.
- Present analytics, account state, or market information.
- Present the Neuro welcome briefing or chat entry point.
- Provide navigation to other protected application functions.
- Display loading, empty, partial-failure, and error states.

User Journey

Existing User Login
      │
      ▼
Successful Authentication
      │
      ▼
Access and Refresh Session Established
      │
      ▼
Authenticated Redirect
      │
      ▼
GET /user/dashboard
      │
      ▼
frontend/proxy.ts
      │
      ▼
Session and Route Protection
      │
      ├────────► Invalid or Missing Session
      │                    │
      │                    ▼
      │                 /login
      │
      └────────► Valid Session
                           │
                           ▼
frontend/app/user/layout.tsx
                           │
                           ▼
frontend/app/user/dashboard/page.tsx
                           │
                           ▼
UserDashboardPage()
                           │
                           ├────────► Portfolio Summary
                           ├────────► Positions
                           ├────────► Analytics
                           ├────────► Account State
                           ├────────► Neuro Briefing
                           ├────────► Navigation
                           └────────► Chat Entry Point

Entry Point

Browser Route

/user/dashboard

Route Type

AUTHENTICATED

Authentication Required

YES

Expected Post-Login Redirect

UNVERIFIED

Unauthenticated Redirect

UNVERIFIED

Frontend

Page File

frontend/app/user/dashboard/page.tsx

Component

UserDashboardPage

Component Type

Client Component

Layout

frontend/app/user/layout.tsx

Middleware

frontend/proxy.ts

Loading File

UNKNOWN

Error Page

UNKNOWN

404 Page

UNKNOWN

Other Dashboard Pages Detected

frontend/app/admin/user-dashboard/page.tsx
frontend/app/dashboard/page.tsx
frontend/app/user/dashboard/page.tsx

Visible Layout

BUTTON

} disabled= className="nv-button nv-button-primary nv-button-lg" >

Source: frontend/app/user/dashboard/page.tsx:539

P

Total portfolio value

Source: frontend/app/user/dashboard/page.tsx:567

P

Holdings snapshot

Source: frontend/app/user/dashboard/page.tsx:644

H2

Your current positions

Source: frontend/app/user/dashboard/page.tsx:648

BUTTON

} className="nv-button nv-button-secondary" > View portfolio

Source: frontend/app/user/dashboard/page.tsx:653

SPAN

shares

Source: frontend/app/user/dashboard/page.tsx:685

SPAN

Cost basis

Source: frontend/app/user/dashboard/page.tsx:699

P

Recent activity

Source: frontend/app/user/dashboard/page.tsx:712

H2

Latest account orders

Source: frontend/app/user/dashboard/page.tsx:716

BUTTON

} className="nv-button nv-button-secondary" > View history

Source: frontend/app/user/dashboard/page.tsx:721

P

Markets

Source: frontend/app/user/dashboard/page.tsx:743

H2

Prices and market intelligence

Source: frontend/app/user/dashboard/page.tsx:747

P

Read-only quotes, watchlists, active symbols, and market context.

Source: frontend/app/user/dashboard/page.tsx:751

P

Portfolio

Source: frontend/app/user/dashboard/page.tsx:770

H2

Holdings and account performance

Source: frontend/app/user/dashboard/page.tsx:774

P

Review valuation, cost basis, exposure, realized results, and analytics.

Source: frontend/app/user/dashboard/page.tsx:778

P

Portfolio valuation

Source: frontend/app/user/dashboard/page.tsx:794

H2

Capital and account value

Source: frontend/app/user/dashboard/page.tsx:798

P

Cash is reconstructed from this account's authenticated order ledger. Open positions are currently valued at cost basis until qualified live market marking is added.

Source: frontend/app/user/dashboard/page.tsx:802

P

Starting capital

Source: frontend/app/user/dashboard/page.tsx:819

P

Available cash

Source: frontend/app/user/dashboard/page.tsx:831

P

Deployed at cost

Source: frontend/app/user/dashboard/page.tsx:843

P

Account value at cost

Source: frontend/app/user/dashboard/page.tsx:855

P

Fees paid

Source: frontend/app/user/dashboard/page.tsx:867

P

Capital utilization: %

Source: frontend/app/user/dashboard/page.tsx:894

P

Your portfolio

Source: frontend/app/user/dashboard/page.tsx:914

H2

Personal paper positions

Source: frontend/app/user/dashboard/page.tsx:918

P

Updated

Source: frontend/app/user/dashboard/page.tsx:953

P

Shares

Source: frontend/app/user/dashboard/page.tsx:979

P

Average entry

Source: frontend/app/user/dashboard/page.tsx:990

P

Cost basis

Source: frontend/app/user/dashboard/page.tsx:1001

P

Account analytics

Source: frontend/app/user/dashboard/page.tsx:1025

H2

Simulation activity

Source: frontend/app/user/dashboard/page.tsx:1029

P

Total realized P/L

Source: frontend/app/user/dashboard/page.tsx:1102

P

= 0 ? "text-emerald-300" : "text-amber-300", ].join(" ")} >

Source: frontend/app/user/dashboard/page.tsx:1106

P

Orders

Source: frontend/app/user/dashboard/page.tsx:1127

H2

Paper order entry

Source: frontend/app/user/dashboard/page.tsx:1131

P

Submit simulated buy and sell orders through the qualified paper pipeline.

Source: frontend/app/user/dashboard/page.tsx:1135

P

History

Source: frontend/app/user/dashboard/page.tsx:1156

H2

Account activity and order records

Source: frontend/app/user/dashboard/page.tsx:1160

P

Review owner-scoped paper orders and recorded execution activity.

Source: frontend/app/user/dashboard/page.tsx:1164

P

Recent activity

Source: frontend/app/user/dashboard/page.tsx:1184

H2

Account order history

Source: frontend/app/user/dashboard/page.tsx:1188

P

Strategies

Source: frontend/app/user/dashboard/page.tsx:1267

H2

Strategy decisions and signals

Source: frontend/app/user/dashboard/page.tsx:1271

P

Inspect current read-only decisions, confidence, and strategy provider output.

Source: frontend/app/user/dashboard/page.tsx:1275

P

Options

Source: frontend/app/user/dashboard/page.tsx:1294

H2

Account settings and protection

Source: frontend/app/user/dashboard/page.tsx:1298

P

Review account scope, subscription, security, notifications, and preferences.

Source: frontend/app/user/dashboard/page.tsx:1302

P

Account protection

Source: frontend/app/user/dashboard/page.tsx:1322

H2

Authenticated paper-trading account

Source: frontend/app/user/dashboard/page.tsx:1326

P

Orders, positions, and analytics are scoped to the currently authenticated account. Paper orders pass through NeuroVest risk, accounting, execution, and ledger boundaries without enabling a live broker.

Source: frontend/app/user/dashboard/page.tsx:1330

P

Role

Source: frontend/app/user/dashboard/page.tsx:1357

P

Subscription

Source: frontend/app/user/dashboard/page.tsx:1367

P

Account status

Source: frontend/app/user/dashboard/page.tsx:1377

P

Execution mode

Source: frontend/app/user/dashboard/page.tsx:1387

P

Paper only

Source: frontend/app/user/dashboard/page.tsx:1391

SPAN

Personal investing workspace

Source: frontend/app/user/dashboard/page.tsx:1421

SPAN

Owner scoped · Paper trading · Read-only market data · No live execution

Source: frontend/app/user/dashboard/page.tsx:1425

P

Live Watchlist

Source: frontend/app/components/workspaces/MarketWorkspace.tsx:73

H2

Market Pulse

Source: frontend/app/components/workspaces/MarketWorkspace.tsx:74

BUTTON

void loadWatchlist()} disabled= className="rounded-xl bg-cyan-400 px-4 py-2 text-sm font-bold text-slate-950 disabled:opacity-60" >

Source: frontend/app/components/workspaces/MarketWorkspace.tsx:77

P

{quote?.price ? `$$ ` : "—"}

Source: frontend/app/components/workspaces/MarketWorkspace.tsx:100

P

Provider:

Source: frontend/app/components/workspaces/MarketWorkspace.tsx:104

P

Market

Source: frontend/app/components/workspaces/MarketWorkspace.tsx:124

H2

Market Intelligence

Source: frontend/app/components/workspaces/MarketWorkspace.tsx:125

P

Read-only watchlist, live quote refresh, active universe, and replay-focused CAD symbols.

Source: frontend/app/components/workspaces/MarketWorkspace.tsx:126

P

Training Universe

Source: frontend/app/components/workspaces/MarketWorkspace.tsx:150

H3

Replay Symbol Groups

Source: frontend/app/components/workspaces/MarketWorkspace.tsx:151

P

Train More

Source: frontend/app/components/workspaces/MarketWorkspace.tsx:155

P

CNR.TO

Source: frontend/app/components/workspaces/MarketWorkspace.tsx:156

P

Positive weighted replay reward.

Source: frontend/app/components/workspaces/MarketWorkspace.tsx:157

P

Watchlist

Source: frontend/app/components/workspaces/MarketWorkspace.tsx:161

P

ENB.TO · VFV.TO · VUN.TO

Source: frontend/app/components/workspaces/MarketWorkspace.tsx:162

P

Included in filtered replay universe.

Source: frontend/app/components/workspaces/MarketWorkspace.tsx:163

P

Excluded From Replay

Source: frontend/app/components/workspaces/MarketWorkspace.tsx:167

P

SHOP.TO · ATZ.TO · BNS.TO

Source: frontend/app/components/workspaces/MarketWorkspace.tsx:168

P

Excluded due to current strategy underperformance.

Source: frontend/app/components/workspaces/MarketWorkspace.tsx:169

P

Neuro strategies

Source: frontend/app/user/dashboard/UserStrategiesWorkspace.tsx:324

H3

Strategies used for your account

Source: frontend/app/user/dashboard/UserStrategiesWorkspace.tsx:328

P

Strategy names and usage totals are reconstructed from this account's recorded decision and order activity.

Source: frontend/app/user/dashboard/UserStrategiesWorkspace.tsx:332

P

No historical strategy identifiers are recorded yet.

Source: frontend/app/user/dashboard/UserStrategiesWorkspace.tsx:349

P

Neuro can still provide current strategy decisions below, but per-strategy usage counts require the order or decision ledger to store a strategy name, strategy identifier, or provider value.

Source: frontend/app/user/dashboard/UserStrategiesWorkspace.tsx:353

P

Used for this account

Source: frontend/app/user/dashboard/UserStrategiesWorkspace.tsx:375

SPAN

uses

Source: frontend/app/user/dashboard/UserStrategiesWorkspace.tsx:389

P

% of recorded strategy activity

Source: frontend/app/user/dashboard/UserStrategiesWorkspace.tsx:408

P

Strategy history

Source: frontend/app/user/dashboard/UserStrategiesWorkspace.tsx:422

H3

Recent Neuro strategy activity

Source: frontend/app/user/dashboard/UserStrategiesWorkspace.tsx:426

P

The latest account records that identify the strategy or strategy provider used by Neuro.

Source: frontend/app/user/dashboard/UserStrategiesWorkspace.tsx:430

P

No strategy-specific history is available for this account yet.

Source: frontend/app/user/dashboard/UserStrategiesWorkspace.tsx:446

P

Current decision

Source: frontend/app/user/dashboard/UserStrategiesWorkspace.tsx:529

H3

Inspect a live strategy signal

Source: frontend/app/user/dashboard/UserStrategiesWorkspace.tsx:533

P

Enter a symbol to inspect Neuro's current read-only strategy decision and confidence.

Source: frontend/app/user/dashboard/UserStrategiesWorkspace.tsx:537

P

Investing workspace

Source: frontend/app/user/dashboard/UserWorkspaceNavigation.tsx:23

H2

Your account

Source: frontend/app/user/dashboard/UserWorkspaceNavigation.tsx:27

P

Portfolio, markets, orders, history, strategies, and account options.

Source: frontend/app/user/dashboard/UserWorkspaceNavigation.tsx:31

BUTTON

} className= >

Source: frontend/app/user/dashboard/UserWorkspaceNavigation.tsx:49

P

Neuro Chat

Source: frontend/app/components/chat/FloatingChatWidget.tsx:122

H2

Assistant

Source: frontend/app/components/chat/FloatingChatWidget.tsx:126

BUTTON

setOpen(false) } className="nv-button nv-button-secondary nv-button-sm" > Close

Source: frontend/app/components/chat/FloatingChatWidget.tsx:132

LABEL

Message Neuro

Source: frontend/app/components/chat/FloatingChatWidget.tsx:182

BUTTON

void send() } disabled= className="nv-button nv-button-primary nv-button-md mt-3 w-full" >

Source: frontend/app/components/chat/FloatingChatWidget.tsx:210

BUTTON

setOpen( (value) => !value, ) } aria-expanded= aria-label= className="group relative flex min-h-[72px] items-center rounded-full border-2 border-cyan-300 bg-[linear-gradient(135deg,rgba(4,20,32,0.98),rgba(6,30,40,0.98))] pr-7 text-white shadow-[0_0_34px_rgba(34,211,238,0.48)] transition duration-200 hover:-translate-y-1 hover:shadow-[0_0_48px_rgba(34,211,238,0.68)]" > Chat

Source: frontend/app/components/chat/FloatingChatWidget.tsx:225

SPAN

{change ? `$ $ $ ($ $ %)` : "—"}

Source: frontend/app/components/ticker/MarketTickerBanner.tsx:274

P

Paper trading

Source: frontend/app/user/components/PaperOrderPanel.tsx:206

H2

Submit a simulated order

Source: frontend/app/user/components/PaperOrderPanel.tsx:210

P

Orders use NeuroVest's authenticated paper-execution, risk, accounting, and ledger pipeline. No live broker order is created.

Source: frontend/app/user/components/PaperOrderPanel.tsx:214

LABEL

Market symbol

Source: frontend/app/user/components/PaperOrderPanel.tsx:234

P

Examples: AAPL, MSFT, BRK.B

Source: frontend/app/user/components/PaperOrderPanel.tsx:262

BUTTON

} className= >

Source: frontend/app/user/components/PaperOrderPanel.tsx:288

LABEL

} className="mt-1 h-4 w-4 accent-cyan-400" /> I understand this is a simulated paper order and cannot place a live-money broker trade.

Source: frontend/app/user/components/PaperOrderPanel.tsx:337

P

Trace:

Source: frontend/app/user/components/PaperOrderPanel.tsx:385

BUTTON

{submitting ? "Processing paper order…" : `Submit $ order`}

Source: frontend/app/user/components/PaperOrderPanel.tsx:408

P

Recent activity

Source: frontend/app/user/components/RecentOrderActivity.tsx:205

H2

Account order history

Source: frontend/app/user/components/RecentOrderActivity.tsx:209

P

These records come from the currently authenticated account's owner-scoped order ledger.

Source: frontend/app/user/components/RecentOrderActivity.tsx:213

P

Quantity

Source: frontend/app/user/components/RecentOrderActivity.tsx:392

P

Execution price

Source: frontend/app/user/components/RecentOrderActivity.tsx:404

P

Allocated capital

Source: frontend/app/user/components/RecentOrderActivity.tsx:416

P

Fees

Source: frontend/app/user/components/RecentOrderActivity.tsx:428

BUTTON

Open Neuro briefing

Source: frontend/app/user/components/NeuroWelcomeBriefing.tsx:234

BUTTON

×

Source: frontend/app/user/components/NeuroWelcomeBriefing.tsx:259

P

Neuro account briefing

Source: frontend/app/user/components/NeuroWelcomeBriefing.tsx:299

H2

, .

Source: frontend/app/user/components/NeuroWelcomeBriefing.tsx:303

P

Your authenticated paper-trading workspace is ready. Portfolio records, order activity, account valuation, and analytics remain isolated to your account.

Source: frontend/app/user/components/NeuroWelcomeBriefing.tsx:313

P

Account

Source: frontend/app/user/components/NeuroWelcomeBriefing.tsx:321

P

Subscription

Source: frontend/app/user/components/NeuroWelcomeBriefing.tsx:332

P

Execution mode

Source: frontend/app/user/components/NeuroWelcomeBriefing.tsx:343

P

Paper only

Source: frontend/app/user/components/NeuroWelcomeBriefing.tsx:347

P

Current protection

Source: frontend/app/user/components/NeuroWelcomeBriefing.tsx:353

P

Owner isolated

Source: frontend/app/user/components/NeuroWelcomeBriefing.tsx:357

P

Neuro status

Source: frontend/app/user/components/NeuroWelcomeBriefing.tsx:364

P

No live-money broker order can be placed from this workspace. All trading actions remain simulated, authenticated, risk gated, and recorded to the account-scoped ledger.

Source: frontend/app/user/components/NeuroWelcomeBriefing.tsx:368

LABEL

} className="mt-1 h-4 w-4 accent-cyan-400" /> Don't show this briefing automatically again. You can still reopen it from the workspace.

Source: frontend/app/user/components/NeuroWelcomeBriefing.tsx:376

BUTTON

Enter workspace

Source: frontend/app/user/components/NeuroWelcomeBriefing.tsx:395

P

Strategy Decision

Source: frontend/app/components/cards/StrategyDecisionCard.tsx:56

P

Confidence

Source: frontend/app/components/cards/StrategyDecisionCard.tsx:71

P

Provider

Source: frontend/app/components/cards/StrategyDecisionCard.tsx:76

BUTTON

void loadDecision(symbol)} disabled= className="rounded-xl bg-violet-400 px-4 py-2 text-sm font-bold text-slate-950 disabled:opacity-60" >

Source: frontend/app/components/cards/StrategyDecisionCard.tsx:95

Frontend Components

Root Component

UserDashboardPage()

Location

frontend/app/user/dashboard/page.tsx

Dependency Inventory

Frontend files traced: 22

Import edges detected: 44

Rendered Components

T [frontend/app/user/dashboard/page.tsx:176]
T [frontend/app/user/dashboard/page.tsx:179]
DashboardState [frontend/app/user/dashboard/page.tsx:191]
UserWorkspaceId [frontend/app/user/dashboard/page.tsx:207]
SessionPayload [frontend/app/user/dashboard/page.tsx:290]
PositionsPayload [frontend/app/user/dashboard/page.tsx:317]
OrdersPayload [frontend/app/user/dashboard/page.tsx:325]
AnalyticsPayload [frontend/app/user/dashboard/page.tsx:333]
PortfolioValuationPayload [frontend/app/user/dashboard/page.tsx:339]
WorkspacePage [frontend/app/user/dashboard/page.tsx:525]
PageHeader [frontend/app/user/dashboard/page.tsx:529]
StatusBadge [frontend/app/user/dashboard/page.tsx:534]
UserWorkspaceNavigation [frontend/app/user/dashboard/page.tsx:555]
UserWorkspaceRouter [frontend/app/user/dashboard/page.tsx:561]
StatusBadge [frontend/app/user/dashboard/page.tsx:576]
StatusBadge [frontend/app/user/dashboard/page.tsx:580]
StatusBadge [frontend/app/user/dashboard/page.tsx:584]
NeuroWelcomeBriefing [frontend/app/user/dashboard/page.tsx:591]
MarketTickerBanner [frontend/app/user/dashboard/page.tsx:597]
StatCard [frontend/app/user/dashboard/page.tsx:604]
StatCard [frontend/app/user/dashboard/page.tsx:612]
StatCard [frontend/app/user/dashboard/page.tsx:620]
StatCard [frontend/app/user/dashboard/page.tsx:628]
StatusMessage [frontend/app/user/dashboard/page.tsx:665]
RecentOrderActivity [frontend/app/user/dashboard/page.tsx:732]
StatusBadge [frontend/app/user/dashboard/page.tsx:756]
MarketWorkspace [frontend/app/user/dashboard/page.tsx:761]
StatusBadge [frontend/app/user/dashboard/page.tsx:783]
Panel [frontend/app/user/dashboard/page.tsx:788]
StatusBadge [frontend/app/user/dashboard/page.tsx:809]
StatusBadge [frontend/app/user/dashboard/page.tsx:881]
StatusBadge [frontend/app/user/dashboard/page.tsx:885]
StatusBadge [frontend/app/user/dashboard/page.tsx:889]
Panel [frontend/app/user/dashboard/page.tsx:908]
StatusBadge [frontend/app/user/dashboard/page.tsx:923]
StatusMessage [frontend/app/user/dashboard/page.tsx:933]
StatusBadge [frontend/app/user/dashboard/page.tsx:961]
Panel [frontend/app/user/dashboard/page.tsx:1019]
StatusBadge [frontend/app/user/dashboard/page.tsx:1034]
StatusBadge [frontend/app/user/dashboard/page.tsx:1140]
PaperOrderPanel [frontend/app/user/dashboard/page.tsx:1145]
StatusBadge [frontend/app/user/dashboard/page.tsx:1169]
RecentOrderActivity [frontend/app/user/dashboard/page.tsx:1174]
Panel [frontend/app/user/dashboard/page.tsx:1178]
StatusBadge [frontend/app/user/dashboard/page.tsx:1193]
StatusMessage [frontend/app/user/dashboard/page.tsx:1203]
StatusBadge [frontend/app/user/dashboard/page.tsx:1280]
UserStrategiesWorkspace [frontend/app/user/dashboard/page.tsx:1285]
Link [frontend/app/user/dashboard/page.tsx:1307]
Panel [frontend/app/user/dashboard/page.tsx:1315]
StatusBadge [frontend/app/user/dashboard/page.tsx:1338]
StatusBadge [frontend/app/user/dashboard/page.tsx:1398]
StatusBadge [frontend/app/user/dashboard/page.tsx:1402]
StatusBadge [frontend/app/user/dashboard/page.tsx:1406]
StatusBadge [frontend/app/user/dashboard/page.tsx:1410]
FloatingChatWidget [frontend/app/user/dashboard/page.tsx:1431]
Record [frontend/app/components/workspaces/MarketWorkspace.tsx:46]
LiveMarketWatchlist [frontend/app/components/workspaces/MarketWorkspace.tsx:147]
StatusBadge [frontend/app/user/dashboard/UserStrategiesWorkspace.tsx:339]
Panel [frontend/app/user/dashboard/UserStrategiesWorkspace.tsx:345]
Panel [frontend/app/user/dashboard/UserStrategiesWorkspace.tsx:364]
StatusBadge [frontend/app/user/dashboard/UserStrategiesWorkspace.tsx:436]
Panel [frontend/app/user/dashboard/UserStrategiesWorkspace.tsx:442]
Panel [frontend/app/user/dashboard/UserStrategiesWorkspace.tsx:452]
StatusBadge [frontend/app/user/dashboard/UserStrategiesWorkspace.tsx:504]
StatusBadge [frontend/app/user/dashboard/UserStrategiesWorkspace.tsx:543]
StrategyDecisionCard [frontend/app/user/dashboard/UserStrategiesWorkspace.tsx:548]
UserWorkspaceId [frontend/app/user/dashboard/UserWorkspaceRouter.tsx:31]
ChatMessage [frontend/app/components/chat/FloatingChatWidget.tsx:26]
Image [frontend/app/components/chat/FloatingChatWidget.tsx:112]
Image [frontend/app/components/chat/FloatingChatWidget.tsx:241]
TickerItem [frontend/app/components/ticker/MarketTickerBanner.tsx:186]
PaperOrderAction [frontend/app/user/components/PaperOrderPanel.tsx:55]
PaperOrderResponse [frontend/app/user/components/PaperOrderPanel.tsx:81]
HTMLFormElement [frontend/app/user/components/PaperOrderPanel.tsx:107]
Panel [frontend/app/user/components/PaperOrderPanel.tsx:200]
StatusBadge [frontend/app/user/components/PaperOrderPanel.tsx:223]
StatusMessage [frontend/app/user/components/PaperOrderPanel.tsx:366]
StatusMessage [frontend/app/user/components/PaperOrderPanel.tsx:377]
StatusBadge [frontend/app/user/components/PaperOrderPanel.tsx:395]
StatusBadge [frontend/app/user/components/PaperOrderPanel.tsx:399]
StatusBadge [frontend/app/user/components/PaperOrderPanel.tsx:403]
Panel [frontend/app/user/components/RecentOrderActivity.tsx:199]
StatusBadge [frontend/app/user/components/RecentOrderActivity.tsx:221]
StatusMessage [frontend/app/user/components/RecentOrderActivity.tsx:231]
StatusBadge [frontend/app/user/components/RecentOrderActivity.tsx:381]
StatusBadge [frontend/app/user/components/RecentOrderActivity.tsx:448]
StatusBadge [frontend/app/user/components/RecentOrderActivity.tsx:452]
StatusBadge [frontend/app/user/components/RecentOrderActivity.tsx:456]
StatusBadge [frontend/app/user/components/RecentOrderActivity.tsx:460]
Image [frontend/app/user/components/NeuroWelcomeBriefing.tsx:274]
StatusBadge [frontend/app/user/components/NeuroWelcomeBriefing.tsx:284]
StatusBadge [frontend/app/user/components/NeuroWelcomeBriefing.tsx:288]
StatusBadge [frontend/app/user/components/NeuroWelcomeBriefing.tsx:292]
PageContainer [frontend/components/app-shell/WorkspacePage.tsx:35]
LiveQuote [frontend/services/marketService.ts:16]
Record [frontend/services/marketService.ts:52]
PortfolioPositionsResponse [frontend/services/portfolioService.ts:45]
PortfolioSnapshotLifecycle [frontend/services/portfolioService.ts:155]
PortfolioSnapshotLifecycle [frontend/services/portfolioService.ts:188]
StrategyDecision [frontend/app/components/cards/StrategyDecisionCard.tsx:12]
ThreadedChatResponse [frontend/services/chatService.ts:20]
StoredChatThread [frontend/services/chatService.ts:97]
ChatResponsePayload [frontend/services/chatService.ts:163]
HTMLElement [frontend/components/ui/PageContainer.tsx:7]
StrategyDecision [frontend/services/strategyService.ts:11]

Frontend Handlers

formatMoney
Type: function
Source: frontend/app/user/dashboard/page.tsx:119

formatNumber
Type: function
Source: frontend/app/user/dashboard/page.tsx:137

formatDate
Type: function
Source: frontend/app/user/dashboard/page.tsx:154

UserDashboardPage
Type: function
Source: frontend/app/user/dashboard/page.tsx:187

() => { void loadDashboard(true);
Type: JSX event binding
Source: frontend/app/user/dashboard/page.tsx:541

setActiveWorkspace
Type: JSX event binding
Source: frontend/app/user/dashboard/page.tsx:557

() => { setActiveWorkspace("portfolio");
Type: JSX event binding
Source: frontend/app/user/dashboard/page.tsx:655

() => { setActiveWorkspace("history");
Type: JSX event binding
Source: frontend/app/user/dashboard/page.tsx:723

LiveMarketWatchlist
Type: function
Source: frontend/app/components/workspaces/MarketWorkspace.tsx:45

MarketWorkspace
Type: function
Source: frontend/app/components/workspaces/MarketWorkspace.tsx:115

() => void loadWatchlist()
Type: JSX event binding
Source: frontend/app/components/workspaces/MarketWorkspace.tsx:79

asRecord
Type: function
Source: frontend/app/user/dashboard/UserStrategiesWorkspace.tsx:76

readString
Type: function
Source: frontend/app/user/dashboard/UserStrategiesWorkspace.tsx:90

normalizeLabel
Type: function
Source: frontend/app/user/dashboard/UserStrategiesWorkspace.tsx:115

resolveStrategyName
Type: function
Source: frontend/app/user/dashboard/UserStrategiesWorkspace.tsx:129

resolveActivity
Type: function
Source: frontend/app/user/dashboard/UserStrategiesWorkspace.tsx:153

formatTimestamp
Type: function
Source: frontend/app/user/dashboard/UserStrategiesWorkspace.tsx:190

UserStrategiesWorkspace
Type: function
Source: frontend/app/user/dashboard/UserStrategiesWorkspace.tsx:216

UserWorkspaceNavigation
Type: function
Source: frontend/app/user/dashboard/UserWorkspaceNavigation.tsx:15

() => { onChange(workspace.id);
Type: JSX event binding
Source: frontend/app/user/dashboard/UserWorkspaceNavigation.tsx:55

UserWorkspaceRouter
Type: function
Source: frontend/app/user/dashboard/UserWorkspaceRouter.tsx:20

FloatingChatWidget
Type: function
Source: frontend/app/components/chat/FloatingChatWidget.tsx:18

() => setOpen(false)
Type: JSX event binding
Source: frontend/app/components/chat/FloatingChatWidget.tsx:134

(event) => setMessage( event.target.value, )
Type: JSX event binding
Source: frontend/app/components/chat/FloatingChatWidget.tsx:192

(event) => { if ( event.key === "Enter" && !event.shiftKey ) { event.preventDefault(); void send();
Type: JSX event binding
Source: frontend/app/components/chat/FloatingChatWidget.tsx:197

() => void send()
Type: JSX event binding
Source: frontend/app/components/chat/FloatingChatWidget.tsx:212

() => setOpen( (value) => !value, )
Type: JSX event binding
Source: frontend/app/components/chat/FloatingChatWidget.tsx:227

finiteNumber
Type: function
Source: frontend/app/components/ticker/MarketTickerBanner.tsx:51

referenceOpen
Type: function
Source: frontend/app/components/ticker/MarketTickerBanner.tsx:64

priceChange
Type: function
Source: frontend/app/components/ticker/MarketTickerBanner.tsx:83

displayPrice
Type: function
Source: frontend/app/components/ticker/MarketTickerBanner.tsx:113

MarketTickerBanner
Type: function
Source: frontend/app/components/ticker/MarketTickerBanner.tsx:136

PaperOrderPanel
Type: function
Source: frontend/app/user/components/PaperOrderPanel.tsx:43

submitOrder
Type: function
Source: frontend/app/user/components/PaperOrderPanel.tsx:106

submitOrder
Type: JSX event binding
Source: frontend/app/user/components/PaperOrderPanel.tsx:229

(event) => { setSymbol( event.target.value .toUpperCase(), ); setError(null); setResult(null);
Type: JSX event binding
Source: frontend/app/user/components/PaperOrderPanel.tsx:249

() => { setAction( candidate, ); setError( null, ); setResult( null, );
Type: JSX event binding
Source: frontend/app/user/components/PaperOrderPanel.tsx:296

( event, ) => { setConfirmation( event.target .checked, ); setError(null);
Type: JSX event binding
Source: frontend/app/user/components/PaperOrderPanel.tsx:343

asRecord
Type: function
Source: frontend/app/user/components/RecentOrderActivity.tsx:16

readString
Type: function
Source: frontend/app/user/components/RecentOrderActivity.tsx:30

readNumber
Type: function
Source: frontend/app/user/components/RecentOrderActivity.tsx:56

formatMoney
Type: function
Source: frontend/app/user/components/RecentOrderActivity.tsx:89

formatQuantity
Type: function
Source: frontend/app/user/components/RecentOrderActivity.tsx:107

formatTimestamp
Type: function
Source: frontend/app/user/components/RecentOrderActivity.tsx:122

statusTone
Type: function
Source: frontend/app/user/components/RecentOrderActivity.tsx:150

RecentOrderActivity
Type: function
Source: frontend/app/user/components/RecentOrderActivity.tsx:188

cleanName
Type: function
Source: frontend/app/user/components/NeuroWelcomeBriefing.tsx:39

emailPrefix
Type: function
Source: frontend/app/user/components/NeuroWelcomeBriefing.tsx:56

formatDisplayName
Type: function
Source: frontend/app/user/components/NeuroWelcomeBriefing.tsx:74

greetingForHour
Type: function
Source: frontend/app/user/components/NeuroWelcomeBriefing.tsx:89

NeuroWelcomeBriefing
Type: function
Source: frontend/app/user/components/NeuroWelcomeBriefing.tsx:103

closeBriefing
Type: function
Source: frontend/app/user/components/NeuroWelcomeBriefing.tsx:204

reopenBriefing
Type: function
Source: frontend/app/user/components/NeuroWelcomeBriefing.tsx:224

reopenBriefing
Type: JSX event binding
Source: frontend/app/user/components/NeuroWelcomeBriefing.tsx:236

closeBriefing
Type: JSX event binding
Source: frontend/app/user/components/NeuroWelcomeBriefing.tsx:262

(event) => { setDoNotShowAgain( event.target.checked, );
Type: JSX event binding
Source: frontend/app/user/components/NeuroWelcomeBriefing.tsx:380

closeBriefing
Type: JSX event binding
Source: frontend/app/user/components/NeuroWelcomeBriefing.tsx:397

PageHeader
Type: function
Source: frontend/components/app-shell/PageHeader.tsx:13

WorkspacePage
Type: function
Source: frontend/components/app-shell/WorkspacePage.tsx:21

getLivePrice
Type: function
Source: frontend/services/marketService.ts:14

getLivePrices
Type: function
Source: frontend/services/marketService.ts:50

isRecord
Type: function
Source: frontend/services/portfolioService.ts:35

getPortfolioPositions
Type: function
Source: frontend/services/portfolioService.ts:45

getPortfolioSnapshotLifecycle
Type: function
Source: frontend/services/portfolioService.ts:155

refreshPortfolioSnapshot
Type: function
Source: frontend/services/portfolioService.ts:188

StrategyDecisionCard
Type: function
Source: frontend/app/components/cards/StrategyDecisionCard.tsx:10

(event) => setSymbol(event.target.value.toUpperCase())
Type: JSX event binding
Source: frontend/app/components/cards/StrategyDecisionCard.tsx:90

() => void loadDecision(symbol)
Type: JSX event binding
Source: frontend/app/components/cards/StrategyDecisionCard.tsx:97

canUseStorage
Type: function
Source: frontend/services/chatService.ts:42

createClientMessageId
Type: function
Source: frontend/services/chatService.ts:49

createChatMessage
Type: function
Source: frontend/services/chatService.ts:64

getStoredChatThread
Type: function
Source: frontend/services/chatService.ts:79

storeChatThread
Type: function
Source: frontend/services/chatService.ts:126

clearStoredChatThread
Type: function
Source: frontend/services/chatService.ts:151

sendChatMessage
Type: function
Source: frontend/services/chatService.ts:161

normalizeChatReply
Type: function
Source: frontend/services/chatService.ts:233

normalizeChatMeta
Type: function
Source: frontend/services/chatService.ts:281

readCsrfToken
Type: function
Source: frontend/lib/clientCsrf.ts:4

csrfHeaders
Type: function
Source: frontend/lib/clientCsrf.ts:28

PageContainer
Type: function
Source: frontend/components/ui/PageContainer.tsx:14

getStrategyDecision
Type: function
Source: frontend/services/strategyService.ts:11

Login-to-Dashboard Redirect

The successful login redirect was not conclusively detected.

Frontend Event Flow

User successfully logs in

↓

Frontend receives authentication response

↓

Session cookies or authentication state are installed

↓

Frontend redirects to authenticated dashboard

↓

Middleware validates protected-route access

↓

Dashboard page renders

↓

Frontend services request user-owned data

↓

Backend validates authentication and ownership

↓

Portfolio, positions, analytics, account state, and briefing data return

↓

Dashboard components update

↓

User sees authenticated application state

Frontend Requests

GET "/api/auth/session"
Request Type: fetch
Credentials Mode: include
Source: frontend/app/user/dashboard/page.tsx:232

POST "/api/v1/paper/orders"
Request Type: fetch
Credentials Mode: include
Source: frontend/app/user/components/PaperOrderPanel.tsx:130

GET OR DYNAMIC `/api/v1/market/live-price/${encodeURIComponent(
      cleanSymbol,
    )}`
Request Type: fetch
Credentials Mode: UNKNOWN
Source: frontend/services/marketService.ts:31

GET "/api/v1/portfolio/positions"
Request Type: fetch
Credentials Mode: include
Source: frontend/services/portfolioService.ts:46

POST "/api/v1/portfolio/refresh"
Request Type: fetch
Credentials Mode: include
Source: frontend/services/portfolioService.ts:189

GET OR DYNAMIC `/api/v1/strategy/decision/${cleanSymbol}`
Request Type: fetch
Credentials Mode: UNKNOWN
Source: frontend/services/strategyService.ts:25

Frontend Service and API Files

frontend/proxy.ts
Methods: ['GET']
Targets: ['/dashboard', '/dashboard/', '/dashboard/:path*', '/user/dashboard']
Credentials Include: False

frontend/services/riskService.ts
Methods: []
Targets: []
Credentials Include: False

frontend/services/graphService.ts
Methods: []
Targets: []
Credentials Include: False

frontend/services/marketService.ts
Methods: []
Targets: []
Credentials Include: False

frontend/services/chatService.ts
Methods: ['POST']
Targets: []
Credentials Include: False

frontend/services/strategyService.ts
Methods: []
Targets: []
Credentials Include: False

frontend/services/backendHealthService.ts
Methods: []
Targets: []
Credentials Include: False

frontend/services/portfolioService.ts
Methods: ['GET', 'POST']
Targets: ['/api/v1/portfolio/lifecycle', '/api/v1/portfolio/positions', '/api/v1/portfolio/refresh']
Credentials Include: True

frontend/lib/sessionCookies.ts
Methods: ['GET']
Targets: []
Credentials Include: False

frontend/tests/e2e/06-dashboard-navigation.spec.ts
Methods: ['GET', 'POST']
Targets: ['/dashboard', '/user/dashboard']
Credentials Include: False

frontend/tests/e2e/07-neuro-welcome-briefing.spec.ts
Methods: ['GET', 'POST']
Targets: ['/api/auth/session', '/dashboard', '/user/dashboard']
Credentials Include: False

frontend/services/chat/chatContracts.ts
Methods: []
Targets: []
Credentials Include: False

frontend/app/hooks/useDashboardData.ts
Methods: []
Targets: []
Credentials Include: False

frontend/app/dashboard/layout.tsx
Methods: []
Targets: []
Credentials Include: False

frontend/app/dashboard/page.tsx
Methods: []
Targets: []
Credentials Include: False

frontend/app/admin/sessions/page.tsx
Methods: []
Targets: []
Credentials Include: False

frontend/app/admin/user-dashboard/page.tsx
Methods: []
Targets: ['/user/dashboard']
Credentials Include: False

frontend/app/components/layout/DashboardShell.tsx
Methods: []
Targets: []
Credentials Include: False

frontend/app/api/admin/users/route.ts
Methods: ['GET']
Targets: []
Credentials Include: False

frontend/app/api/admin/users/[userId]/route.ts
Methods: ['DELETE', 'GET']
Targets: []
Credentials Include: False

frontend/app/api/admin/users/[userId]/require-password-reset/route.ts
Methods: ['POST']
Targets: []
Credentials Include: False

frontend/app/api/admin/users/[userId]/enable/route.ts
Methods: ['POST']
Targets: []
Credentials Include: False

frontend/app/api/admin/users/[userId]/disable/route.ts
Methods: ['POST']
Targets: []
Credentials Include: False

frontend/app/api/admin/users/[userId]/temporary-password/route.ts
Methods: ['POST']
Targets: []
Credentials Include: False

frontend/app/api/auth/session/route.ts
Methods: ['GET']
Targets: []
Credentials Include: False

frontend/app/api/auth/change-password/route.ts
Methods: ['POST']
Targets: []
Credentials Include: False

frontend/app/api/auth/logout/route.ts
Methods: ['POST']
Targets: []
Credentials Include: False

frontend/app/api/auth/login/route.ts
Methods: ['GET', 'POST']
Targets: ['/dashboard', '/user/dashboard']
Credentials Include: False

frontend/app/api/v1/chat/route.ts
Methods: ['POST']
Targets: []
Credentials Include: False

frontend/app/api/v1/analytics/route.ts
Methods: ['GET']
Targets: ['/api/v1/analytics']
Credentials Include: False

frontend/app/api/v1/positions/route.ts
Methods: ['GET']
Targets: ['/api/v1/positions']
Credentials Include: False

frontend/app/api/v1/orders/route.ts
Methods: ['GET']
Targets: []
Credentials Include: False

frontend/app/api/v1/graph/live/route.ts
Methods: ['GET']
Targets: []
Credentials Include: False

frontend/app/api/v1/risk/gate/[symbol]/route.ts
Methods: ['GET']
Targets: []
Credentials Include: False

frontend/app/api/v1/paper/orders/route.ts
Methods: ['GET', 'POST']
Targets: []
Credentials Include: False

frontend/app/api/v1/market/live-price/[symbol]/route.ts
Methods: ['GET']
Targets: []
Credentials Include: False

frontend/app/api/v1/portfolio/lifecycle/route.ts
Methods: ['GET']
Targets: ['/api/v1/portfolio/readonly/lifecycle']
Credentials Include: False

frontend/app/api/v1/portfolio/valuation/route.ts
Methods: ['GET']
Targets: ['/api/v1/portfolio/valuation']
Credentials Include: False

frontend/app/api/v1/portfolio/positions/route.ts
Methods: ['GET']
Targets: ['/api/v1/portfolio/readonly/positions']
Credentials Include: False

frontend/app/api/v1/portfolio/refresh/route.ts
Methods: ['POST']
Targets: ['/api/v1/portfolio/readonly/refresh']
Credentials Include: False

frontend/app/api/v1/strategy/decision/[symbol]/route.ts
Methods: ['GET']
Targets: []
Credentials Include: False

frontend/app/user/components/NeuroWelcomeBriefing.tsx
Methods: []
Targets: []
Credentials Include: False

frontend/app/user/dashboard/userWorkspaceTypes.ts
Methods: []
Targets: []
Credentials Include: False

frontend/app/user/dashboard/page.tsx
Methods: ['GET']
Targets: ['/api/auth/session', '/api/v1/analytics', '/api/v1/portfolio/valuation', '/api/v1/positions', '/login?next=/user/dashboard']
Credentials Include: True

frontend/app/user/dashboard/UserWorkspaceNavigation.tsx
Methods: []
Targets: []
Credentials Include: False

frontend/app/user/dashboard/UserWorkspaceRouter.tsx
Methods: []
Targets: []
Credentials Include: False

Navigation and Redirects

href → /user/settings [frontend/app/user/dashboard/page.tsx:1308]

Middleware

File

frontend/proxy.ts

Observed

PRESENT

Dashboard Mentions

14

Known Cookies

neurovest_access
neurovest_csrf
neurovest_session

Known Headers

Cache-Control
host
origin
x-forwarded-host
x-forwarded-proto
x-neurovest-csrf

Protection Markers

/login, access, authenticated, pathname, protected, redirect, session

Authentication Logic

DETECTED

Unauthenticated Redirect

UNVERIFIED

Backend Routes

GET /api/v1/graph/live

Function

get_live_graph

File

backend/app/main.py

Source Line

204

Security and Domain Markers

Depends, authenticated, owner, session

GET /api/v1/dashboard/summary

Function

summary

File

backend/app/main.py

Source Line

209

Security and Domain Markers

Depends, authenticated, session

POST /api/v1/sandbox/signal

Function

set_sandbox_override

File

backend/app/main.py

Source Line

399

Security and Domain Markers

Depends, authenticated, portfolio, user_id

POST /api/v1/sandbox/audit

Function

trigger_sandbox_audit

File

backend/app/main.py

Source Line

420

Security and Domain Markers

Depends, authenticated, portfolio, user_id

POST /api/v1/admin/backup

Function

force_system_backup

File

backend/app/main.py

Source Line

435

Security and Domain Markers

Depends, authenticated, portfolio, user_id

GET /api/v1/portfolio/valuation

Function

get_authenticated_portfolio_valuation

File

backend/app/main.py

Source Line

462

Security and Domain Markers

Depends, authenticated, portfolio, position, session, user_id

GET /api/v1/positions

Function

get_active_positions

File

backend/app/main.py

Source Line

525

Security and Domain Markers

Depends, authenticated, portfolio, position, session, user_id

GET /api/v1/orders

Function

get_orders

File

backend/app/main.py

Source Line

563

Security and Domain Markers

Depends, analytics, authenticated, position, session, user_id

GET /api/v1/analytics

Function

get_analytics

File

backend/app/main.py

Source Line

595

Security and Domain Markers

Depends, analytics, authenticated, session, user_id

POST /api/v1/paper/orders

Function

submit_authenticated_paper_order

File

backend/app/main.py

Source Line

647

Security and Domain Markers

Depends, authenticated, owner, portfolio, position, user_id

GET /api/v1/market/live-price/{symbol}

Function

api_live_market_price

File

backend/app/main.py

Source Line

706

Security and Domain Markers

Depends, authenticated, owner, portfolio, position, user_id

GET /api/v1/portfolio/positions

Function

api_portfolio_positions

File

backend/app/main.py

Source Line

711

Security and Domain Markers

Depends, authenticated, owner, portfolio, position, user_id

GET /api/v1/strategy/decision/{symbol}

Function

api_strategy_decision

File

backend/app/main.py

Source Line

722

Security and Domain Markers

Depends, authenticated, owner, portfolio, position, user_id

GET /api/v1/risk/gate/{symbol}

Function

api_risk_gate

File

backend/app/main.py

Source Line

727

Security and Domain Markers

Depends, authenticated, owner, portfolio, position, user_id

GET /api/v1/portfolio/readonly

Function

authenticated_owned_portfolio_overview

File

backend/app/main.py

Source Line

796

Security and Domain Markers

Depends, authenticated, portfolio, position, read_only, user_id

GET /api/v1/portfolio/readonly/accounts

Function

authenticated_owned_portfolio_accounts

File

backend/app/main.py

Source Line

819

Security and Domain Markers

Depends, authenticated, portfolio, position, read_only

GET /api/v1/portfolio/readonly/balances

Function

authenticated_owned_portfolio_balances

File

backend/app/main.py

Source Line

839

Security and Domain Markers

Depends, authenticated, owner, portfolio, position, read_only

GET /api/v1/portfolio/readonly/positions

Function

authenticated_owned_portfolio_positions

File

backend/app/main.py

Source Line

859

Security and Domain Markers

Depends, authenticated, owner, portfolio, position, read_only

GET /api/v1/portfolio/readonly/positions/{symbol}

Function

authenticated_owned_portfolio_symbol_positions

File

backend/app/main.py

Source Line

879

Security and Domain Markers

Depends, authenticated, owner, portfolio, position, read_only, user_id

GET /api/v1/portfolio/readonly/totals

Function

authenticated_owned_portfolio_totals

File

backend/app/main.py

Source Line

902

Security and Domain Markers

Depends, authenticated, owner, portfolio, position, read_only, user_id

GET /api/v1/portfolio/readonly/lifecycle

Function

authenticated_portfolio_snapshot_lifecycle

File

backend/app/main.py

Source Line

933

Security and Domain Markers

Depends, authenticated, owner, portfolio, read_only, user_id

POST /api/v1/portfolio/readonly/refresh

Function

authenticated_portfolio_snapshot_refresh

File

backend/app/main.py

Source Line

964

Security and Domain Markers

Depends, authenticated, portfolio, user_id

POST /api/v1/chat

Function

chat_endpoint

File

backend/app/stacks/chat_public/chat_api.py

Source Line

39

Security and Domain Markers

Depends, authenticated

POST /{user_id}/require-password-reset

Function

require_password_reset

File

backend/app/stacks/identity_auth/admin_mutation_router.py

Source Line

30

Security and Domain Markers

Depends, user_id

POST /{user_id}/temporary-password

Function

issue_temporary_password

File

backend/app/stacks/identity_auth/admin_mutation_router.py

Source Line

49

Security and Domain Markers

Depends, user_id

GET /introspection

Function

administrative_introspection

File

backend/app/stacks/identity_auth/admin_read_router.py

Source Line

43

Security and Domain Markers

Depends, authorization, read_only, session, user_id

GET /users

Function

list_administrative_users

File

backend/app/stacks/identity_auth/admin_read_router.py

Source Line

66

Security and Domain Markers

Depends, authorization, read_only, session, user_id

GET /users/{user_id}

Function

get_administrative_user

File

backend/app/stacks/identity_auth/admin_read_router.py

Source Line

95

Security and Domain Markers

Depends, session, user_id

GET /sessions

Function

list_administrative_sessions

File

backend/app/stacks/identity_auth/admin_read_router.py

Source Line

125

Security and Domain Markers

Depends, session, user_id

GET /sessions/{session_id}

Function

get_administrative_session

File

backend/app/stacks/identity_auth/admin_read_router.py

Source Line

170

Security and Domain Markers

Depends, session, user_id

GET /access-token-revocations

Function

list_access_token_revocations

File

backend/app/stacks/identity_auth/admin_read_router.py

Source Line

200

Security and Domain Markers

Depends, session, user_id

POST /register

Function

register_identity

File

backend/app/stacks/identity_auth/api_router.py

Source Line

112

Security and Domain Markers

Depends, session, user_id

POST /login

Function

login_identity

File

backend/app/stacks/identity_auth/api_router.py

Source Line

157

Security and Domain Markers

Depends

POST /change-required-password

Function

change_required_password

File

backend/app/stacks/identity_auth/api_router.py

Source Line

235

Security and Domain Markers

Depends, authenticated, session, user_id

POST /refresh

Function

refresh_session

File

backend/app/stacks/identity_auth/api_router.py

Source Line

282

Security and Domain Markers

Depends, session, user_id

POST /logout

Function

logout_session

File

backend/app/stacks/identity_auth/api_router.py

Source Line

351

Security and Domain Markers

Depends, session, user_id

POST /logout-all

Function

logout_all_sessions

File

backend/app/stacks/identity_auth/api_router.py

Source Line

428

Security and Domain Markers

Depends, authenticated, session, user_id

GET /introspection

Function

session_introspection

File

backend/app/stacks/identity_auth/api_router.py

Source Line

487

Security and Domain Markers

Depends, authenticated, session

GET /api/v1/analytics

Function

analytics

File

backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py

Source Line

24

Security and Domain Markers

analytics, authenticated

POST /api/v1/admin/backup

Function

admin_backup

File

backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py

Source Line

32

Security and Domain Markers

analytics, authenticated

GET /api/v1/market-data/status

Function

market_status

File

backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py

Source Line

40

Security and Domain Markers

analytics, authenticated

GET /status

Function

market_data_status

File

backend/app/stacks/market_data/api_router.py

Source Line

102

Security and Domain Markers

position, read_only, session

GET /quote/{symbol}

Function

market_data_quote

File

backend/app/stacks/market_data/api_router.py

Source Line

168

Security and Domain Markers

session

GET /historical/{symbol}

Function

market_data_historical

File

backend/app/stacks/market_data/api_router.py

Source Line

203

Security and Domain Markers

NONE IDENTIFIED

Backend Function Path

_reconcile_declared_node_ownership
File: backend/app/core/cognitive_graph_state.py
Lines: 1406-1465
Matched Terms: owner
Calls: NODE_ARCHITECTURE.items, dict, ownership.get

load_snapshot
File: backend/app/core/cognitive_graph_state.py
Lines: 1481-1536
Matched Terms: owner
Calls: SNAPSHOT_FILE.exists, SNAPSHOT_FILE.read_text, data.get, data.get('edges', {}).items, defaultdict, event.get, int, json.loads, key.split, len, max, print, self._reconcile_declared_node_ownership

activate_node
File: backend/app/core/cognitive_graph_state.py
Lines: 1568-1709
Matched Terms: user_id, owner
Calls: NODE_ARCHITECTURE.get, dict, int, known_ownership.get, meta.get, new_trace_id, now, payload.get, self._architecture_for, self._next_sequence, self._store_event, self._store_flow_step, self.node_meta.get, self.save_snapshot, str, update_metric_contract

_materialize_edge_endpoint
File: backend/app/core/cognitive_graph_state.py
Lines: 1711-1826
Matched Terms: owner
Calls: NODE_ARCHITECTURE.get, current_meta.setdefault, dict, known_ownership.get, self._architecture_for, self.node_meta.get

activate_edge
File: backend/app/core/cognitive_graph_state.py
Lines: 1828-1972
Matched Terms: user_id
Calls: any, dict, edge_metrics.update, new_trace_id, now, payload.get, self._architecture_for, self._materialize_edge_endpoint, self._next_sequence, self._store_event, self._store_flow_step, self.edge_meta.get, self.save_snapshot, str, update_metric_contract

snapshot
File: backend/app/core/cognitive_graph_state.py
Lines: 2032-2355
Matched Terms: owner
Calls: NODE_ARCHITECTURE.get, NODE_ARCHITECTURE.items, bool, canonical_ownership.get, destination_ownership.get, dict, existing.update, int, len, materialized_edge_meta.get, materialized_node_meta.get, materialized_node_meta.values, meta.get, now, ownership.get, self.edge_activity.items, self.edge_meta.items, self.node_meta.items, self.node_state.items, self.recent_trace_groups, source_ownership.get, sum

emit_runtime_step
File: backend/app/core/runtime_trace.py
Lines: 20-84
Matched Terms: user_id
Calls: dict, global_event_bus.emit

lifespan
File: backend/app/main.py
Lines: 150-175
Matched Terms: user_id, owner
Calls: daemon_task.cancel, global_event_bus.subscribe, global_event_bus.unsubscribe, init_db, print, register_runtime_models, resolve_reconciliation_owner_id, start_periodic_reconciliation_daemon

summary
File: backend/app/main.py
Lines: 210-396
Matched Terms: dashboard, portfolio, session, user_id
Calls: Depends, StrategyDecisionAuditAdapter, app.get, async_session, audit_adapter.produce_and_audit, build_decision_audit_service, create_trace_id, decision.get, dict, emit_runtime_step, execution_results.append, process_portfolio_output, str, type, uuid5

trigger_sandbox_audit
File: backend/app/main.py
Lines: 421-432
Matched Terms: user_id
Calls: app.post, create_trace_id, run_reconciliation_audit

get_authenticated_portfolio_valuation
File: backend/app/main.py
Lines: 463-522
Matched Terms: portfolio, user_id
Calls: Depends, app.get, calculate_live_portfolio_equity, float, round, str, valuation.get

get_active_positions
File: backend/app/main.py
Lines: 526-560
Matched Terms: portfolio, position, session, user_id
Calls: Depends, app.get, async_session, len, pos.last_updated.isoformat, result.scalars, result.scalars().all, round, select, select(PortfolioInventory).where, session.execute

get_orders
File: backend/app/main.py
Lines: 564-592
Matched Terms: session, user_id
Calls: Depends, OrderHistory.id.desc, app.get, async_session, len, o.timestamp.isoformat, result.scalars, result.scalars().all, select, select(OrderHistory).where, select(OrderHistory).where(OrderHistory.user_id == principal.subject).order_by, session.execute

get_analytics
File: backend/app/main.py
Lines: 596-644
Matched Terms: analytics, session, user_id
Calls: Depends, app.get, async_session, len, result.scalars, result.scalars().all, round, select, select(OrderHistory).where, session.execute, str, str(o.signal).lower, sum

submit_authenticated_paper_order
File: backend/app/main.py
Lines: 648-691
Matched Terms: portfolio, user_id, owner
Calls: Depends, app.post, create_trace_id, process_portfolio_output

api_portfolio_positions
File: backend/app/main.py
Lines: 712-719
Matched Terms: portfolio, position
Calls: Depends, app.get, get_portfolio_positions_for_api

_owned_portfolio_facade_for_principal
File: backend/app/main.py
Lines: 771-793
Matched Terms: portfolio, user_id
Calls: HTTPException, build_owned_facade, str

authenticated_owned_portfolio_overview
File: backend/app/main.py
Lines: 800-816
Matched Terms: portfolio, read_only
Calls: Depends, _owned_portfolio_facade_for_principal, app.get, serialize_overview

authenticated_owned_portfolio_accounts
File: backend/app/main.py
Lines: 823-836
Matched Terms: portfolio, read_only
Calls: Depends, _owned_portfolio_facade_for_principal, app.get, serialize_accounts

authenticated_owned_portfolio_balances
File: backend/app/main.py
Lines: 843-856
Matched Terms: portfolio, read_only
Calls: Depends, _owned_portfolio_facade_for_principal, app.get, serialize_balances

authenticated_owned_portfolio_positions
File: backend/app/main.py
Lines: 863-876
Matched Terms: portfolio, position, read_only
Calls: Depends, _owned_portfolio_facade_for_principal, app.get, serialize_positions

authenticated_owned_portfolio_symbol_positions
File: backend/app/main.py
Lines: 883-899
Matched Terms: portfolio, position, read_only
Calls: Depends, _owned_portfolio_facade_for_principal, app.get, serialize_symbol_positions, symbol.strip, symbol.strip().upper

authenticated_owned_portfolio_totals
File: backend/app/main.py
Lines: 906-919
Matched Terms: portfolio, read_only
Calls: Depends, _owned_portfolio_facade_for_principal, app.get, serialize_totals

authenticated_portfolio_snapshot_lifecycle
File: backend/app/main.py
Lines: 937-961
Matched Terms: portfolio, user_id
Calls: Depends, HTTPException, app.get, get_portfolio_lifecycle, str

authenticated_portfolio_snapshot_refresh
File: backend/app/main.py
Lines: 968-999
Matched Terms: portfolio, user_id
Calls: Depends, HTTPException, app.post, refresh_portfolio_snapshot, str

find_latest_normalized_portfolio
File: backend/app/spine/L5_api/owned_readonly_portfolio_service.py
Lines: 45-64
Matched Terms: portfolio
Calls: AuthenticatedPortfolioUnavailable, Path, Path('runtime/snaptrade_integration').glob, path.stat, sorted

build_owned_snapshot
File: backend/app/spine/L5_api/owned_readonly_portfolio_service.py
Lines: 99-291
Matched Terms: portfolio, position, user_id, owner
Calls: AuthenticatedPortfolioAccessDenied, AuthenticatedPortfolioUnavailable, Path, ReadOnlyPortfolioTotals, _sum_optional, filter_owned_accounts, find_latest_normalized_portfolio, ingest_normalized_portfolio, len, replace, set, sorted, str, str(neurovest_user_id).strip, sum, tuple

build_owned_facade
File: backend/app/spine/L5_api/owned_readonly_portfolio_service.py
Lines: 294-310
Matched Terms: portfolio, user_id, owner
Calls: ReadOnlyPortfolioFacade, build_owned_snapshot

serialize_overview
File: backend/app/spine/L5_api/owned_readonly_portfolio_service.py
Lines: 355-362
Matched Terms: portfolio
Calls: _json_safe, asdict, facade.get_overview

serialize_accounts
File: backend/app/spine/L5_api/owned_readonly_portfolio_service.py
Lines: 365-375
Matched Terms: portfolio
Calls: _json_safe, asdict, facade.list_accounts

serialize_positions
File: backend/app/spine/L5_api/owned_readonly_portfolio_service.py
Lines: 378-388
Matched Terms: portfolio, position
Calls: _json_safe, asdict, facade.list_positions

serialize_symbol_positions
File: backend/app/spine/L5_api/owned_readonly_portfolio_service.py
Lines: 391-404
Matched Terms: portfolio, position
Calls: _json_safe, asdict, facade.find_positions_by_symbol

serialize_balances
File: backend/app/spine/L5_api/owned_readonly_portfolio_service.py
Lines: 407-423
Matched Terms: portfolio
Calls: _json_safe, asdict, facade.list_balances

serialize_totals
File: backend/app/spine/L5_api/owned_readonly_portfolio_service.py
Lines: 426-433
Matched Terms: portfolio
Calls: _json_safe, asdict, facade.get_totals

_required_arguments
File: backend/app/stacks/chat_public/capability_state_registry.py
Lines: 251-270
Matched Terms: position
Calls: inspect.signature, signature.parameters.values

build_capability_registry
File: backend/app/stacks/chat_public/capability_state_registry.py
Lines: 473-533
Matched Terms: read_only
Calls: asdict, inspect_capability, len, sum

detect_chat_intent
File: backend/app/stacks/chat_public/chat_intent_regex.py
Lines: 236-392
Matched Terms: portfolio
Calls: COMMAND_PATTERNS.items, ChatIntent, SOFTWARE_DEBUG_REQUEST_PATTERN.search, _extract_symbol, match.group, match.group(2).upper, message.strip, pattern.search

run_chat_turn
File: backend/app/stacks/chat_public/chat_runtime.py
Lines: 385-1586
Matched Terms: read_only
Calls: '\n- '.join, (math_bundle.result or {}).get, ChatRequest, ChatRequest.model_validate, ChatResponse, ToolEvidence, _ensure_approved_retrieval_citation, _find_existing_assistant_reply, _response_message, assemble_chat_context, assistant_content.encode, bool, citation.get, conversation_store.add_tool_evidence, conversation_store.append_message, conversation_store.get_conversation_state, conversation_store.get_message_by_client_id, conversation_store.get_or_create_thread, create_trace_id, current_turn_evidence.append, detect_chat_intent, dict, emit_runtime_step, evaluate_live_math, handle_chat_message, isinstance, kwargs.get, kwargs.pop, len, list, perf_counter, render_role_overlay, request.message.encode, resolve_principal_overlay, resolve_role_overlay, response.model_dump, retrieve_live_evidence, route_cognitive_request, runtime_result.get, runtime_result['response'].get, str, str(citation.get('citation', '')).strip, update_summary_memory, verification_result.as_dict, verify_response, violation.as_dict

route_cognitive_request
File: backend/app/stacks/chat_public/cognitive_model_router.py
Lines: 184-340
Matched Terms: portfolio
Calls: CognitiveRoutingDecision, _matches, bool, getattr, str, str(getattr(intent, 'family', 'GENERAL') or 'GENERAL').upper, str(message).strip

_build_intent_overlay
File: backend/app/stacks/chat_public/context/context_assembler.py
Lines: 163-529
Matched Terms: dashboard
Calls: _bounded, _compact_json, _safe_loader, bool, component_overlay.get, dashboard.get, dependency_graph.get, dict, isinstance, len, load_repo_context, metadata.get, repo_component_hotspots, repo_hotspots, sections.append, sections.extend, str, str(metadata.get('family', 'GENERAL')).upper

assemble_chat_context
File: backend/app/stacks/chat_public/context/context_assembler.py
Lines: 532-662
Matched Terms: portfolio, position
Calls: AssembledChatContext, _bounded, _build_intent_overlay, _clean_text, _compact_json, _format_evidence, _format_memories, _format_recent_messages, compose_prompt, conversation_store.load_context_bundle, dict, len, sections.insert

extract_portfolio_context
File: backend/app/stacks/chat_public/context/context_assembler.py
Lines: 700-754
Matched Terms: portfolio
Calls: _clean_text, float, match.group, match.group(1).replace, match.group(2).upper, pattern.search, re.compile

build_summary
File: backend/app/stacks/chat_public/context/context_assembler.py
Lines: 802-882
Matched Terms: portfolio
Calls: ' '.join, ', '.join, _bounded, _clean_text, active_strategy.get, deduplicated.append, portfolio_context.get, remembered_terms.items, sorted, summary_lines.append

update_summary_memory
File: backend/app/stacks/chat_public/context/context_assembler.py
Lines: 885-1004
Matched Terms: portfolio
Calls: ConversationState, MemoryFact, build_summary, conversation_store.get_conversation_state, conversation_store.upsert_conversation_state, conversation_store.upsert_memory_fact, dict, extract_portfolio_context, extract_remembered_terms, extract_strategy_context, extracted_terms.items

architecture_dashboard
File: backend/app/stacks/chat_public/context_loader.py
Lines: 639-649
Matched Terms: dashboard
Calls: ARCHITECTURE_DASHBOARD_TXT.exists, ARCHITECTURE_DASHBOARD_TXT.read_text, _load_json, bool, data.get, data.get('architecture_health', {}).get

_thread_contract
File: backend/app/stacks/chat_public/conversation_store.py
Lines: 50-63
Matched Terms: user_id
Calls: ChatThread, dict

_state_contract
File: backend/app/stacks/chat_public/conversation_store.py
Lines: 95-121
Matched Terms: portfolio
Calls: ConversationState, dict, list

create_thread
File: backend/app/stacks/chat_public/conversation_store.py
Lines: 160-222
Matched Terms: portfolio, session, user_id
Calls: ChatThread, ChatThreadRecord, ConversationStateRecord, async_session, self.get_thread, session.add, session.begin, session.rollback

get_thread
File: backend/app/stacks/chat_public/conversation_store.py
Lines: 224-237
Matched Terms: session
Calls: _thread_contract, async_session, session.get

get_or_create_thread
File: backend/app/stacks/chat_public/conversation_store.py
Lines: 252-271
Matched Terms: user_id
Calls: self.create_thread, self.get_thread

append_message
File: backend/app/stacks/chat_public/conversation_store.py
Lines: 273-411
Matched Terms: portfolio, session
Calls: ChatMessage, ChatMessageRecord, ConversationStateRecord, LookupError, ValueError, async_session, content.strip, int, list, self.get_message, self.get_message_by_client_id, self.require_thread, session.add, session.begin, session.get, utc_now

get_message
File: backend/app/stacks/chat_public/conversation_store.py
Lines: 413-426
Matched Terms: session
Calls: _message_contract, async_session, session.get

get_message_by_client_id
File: backend/app/stacks/chat_public/conversation_store.py
Lines: 428-452
Matched Terms: session
Calls: _message_contract, async_session, result.scalar_one_or_none, select, select(ChatMessageRecord).where, select(ChatMessageRecord).where(ChatMessageRecord.thread_id == thread_id, ChatMessageRecord.client_message_id == client_message_id).limit, session.execute

list_messages
File: backend/app/stacks/chat_public/conversation_store.py
Lines: 454-492
Matched Terms: session
Calls: ChatMessageRecord.created_at.asc, ChatMessageRecord.created_at.desc, ChatMessageRecord.message_id.asc, _message_contract, async_session, int, max, min, result.scalars, result.scalars().all, select, select(ChatMessageRecord).where, select(ChatMessageRecord).where(ChatMessageRecord.thread_id == thread_id).order_by, select(ChatMessageRecord).where(ChatMessageRecord.thread_id == thread_id).order_by(ordering, ChatMessageRecord.message_id.asc()).limit, session.execute

get_conversation_state
File: backend/app/stacks/chat_public/conversation_store.py
Lines: 494-511
Matched Terms: session
Calls: ConversationState, _state_contract, async_session, self.require_thread, session.get

upsert_conversation_state
File: backend/app/stacks/chat_public/conversation_store.py
Lines: 513-580
Matched Terms: portfolio, session
Calls: ConversationStateRecord, async_session, dict, hasattr, self.get_conversation_state, self.require_thread, session.add, session.begin, session.get, task.model_dump, utc_now

upsert_memory_fact
File: backend/app/stacks/chat_public/conversation_store.py
Lines: 582-650
Matched Terms: session
Calls: MemoryFactRecord, MemoryFactRecord.updated_at.desc, RuntimeError, async_session, dict, result.scalar_one_or_none, select, select(MemoryFactRecord).where, select(MemoryFactRecord).where(MemoryFactRecord.thread_id == memory.thread_id, MemoryFactRecord.key == memory.key, MemoryFactRecord.status == 'active').order_by, select(MemoryFactRecord).where(MemoryFactRecord.thread_id == memory.thread_id, MemoryFactRecord.key == memory.key, MemoryFactRecord.status == 'active').order_by(MemoryFactRecord.updated_at.desc()).limit, self.get_memory_fact, self.require_thread, session.add, session.begin, session.execute, utc_now

get_memory_fact
File: backend/app/stacks/chat_public/conversation_store.py
Lines: 652-679
Matched Terms: session
Calls: MemoryFactRecord.updated_at.desc, _memory_contract, async_session, result.scalar_one_or_none, select, select(MemoryFactRecord).where, select(MemoryFactRecord).where(MemoryFactRecord.thread_id == thread_id, MemoryFactRecord.key == key, MemoryFactRecord.status == 'active').order_by, select(MemoryFactRecord).where(MemoryFactRecord.thread_id == thread_id, MemoryFactRecord.key == key, MemoryFactRecord.status == 'active').order_by(MemoryFactRecord.updated_at.desc()).limit, session.execute

list_memory_facts
File: backend/app/stacks/chat_public/conversation_store.py
Lines: 681-714
Matched Terms: session
Calls: MemoryFactRecord.updated_at.desc, _memory_contract, async_session, int, max, min, result.scalars, result.scalars().all, select, select(MemoryFactRecord).where, session.execute, statement.order_by, statement.order_by(MemoryFactRecord.updated_at.desc()).limit, statement.where

retract_memory_fact
File: backend/app/stacks/chat_public/conversation_store.py
Lines: 716-749
Matched Terms: session
Calls: MemoryFactRecord.updated_at.desc, async_session, result.scalar_one_or_none, select, select(MemoryFactRecord).where, select(MemoryFactRecord).where(MemoryFactRecord.thread_id == thread_id, MemoryFactRecord.key == key, MemoryFactRecord.status == 'active').order_by, select(MemoryFactRecord).where(MemoryFactRecord.thread_id == thread_id, MemoryFactRecord.key == key, MemoryFactRecord.status == 'active').order_by(MemoryFactRecord.updated_at.desc()).limit, session.begin, session.execute, utc_now

add_tool_evidence
File: backend/app/stacks/chat_public/conversation_store.py
Lines: 751-775
Matched Terms: session
Calls: ToolEvidenceRecord, async_session, self.require_thread, session.add, session.begin

list_tool_evidence
File: backend/app/stacks/chat_public/conversation_store.py
Lines: 777-804
Matched Terms: session
Calls: ToolEvidenceRecord.observed_at.desc, _evidence_contract, async_session, int, max, min, result.scalars, result.scalars().all, select, select(ToolEvidenceRecord).where, select(ToolEvidenceRecord).where(ToolEvidenceRecord.thread_id == thread_id).order_by, select(ToolEvidenceRecord).where(ToolEvidenceRecord.thread_id == thread_id).order_by(ToolEvidenceRecord.observed_at.desc()).limit, session.execute

archive_thread
File: backend/app/stacks/chat_public/conversation_store.py
Lines: 806-827
Matched Terms: session
Calls: LookupError, async_session, self.require_thread, session.begin, session.get, utc_now

delete_thread_for_testing
File: backend/app/stacks/chat_public/conversation_store.py
Lines: 868-913
Matched Terms: session
Calls: async_session, delete, delete(ChatMessageRecord).where, delete(ChatThreadRecord).where, delete(ConversationStateRecord).where, delete(MemoryFactRecord).where, delete(ToolEvidenceRecord).where, session.begin, session.execute

healthcheck
File: backend/app/stacks/chat_public/conversation_store.py
Lines: 915-939
Matched Terms: session
Calls: async_session, select, select(ChatThreadRecord.thread_id).limit, session.execute, type

build_developer_response
File: backend/app/stacks/chat_public/developer_response_builder.py
Lines: 105-463
Matched Terms: dashboard, portfolio, read_only
Calls: ', '.join, '; '.join, _bullet_lines, _hotspot_names, _integer, _safe_load, architecture.get, bool, capability_registry.get, capability_summary_lines, component_overlay.get, dependency_graph.get, isinstance, len, limitations.append, load_repo_context, missing_evidence.append, proven.append, repo.get, repo_component_hotspots, repo_hotspots

_position_size
File: backend/app/stacks/chat_public/math_tools/engine.py
Lines: 746-839
Matched Terms: position
Calls: MathToolError, _decimal, _positive, _success, abs, arguments.get, bool, exact_quantity.to_integral_value

_portfolio_weights
File: backend/app/stacks/chat_public/math_tools/engine.py
Lines: 842-902
Matched Terms: portfolio, position
Calls: ','.join, MathToolError, _sequence, _success, any, arguments.get, format, len, sum, tuple

_extract_position_size
File: backend/app/stacks/chat_public/math_tools/live_math.py
Lines: 224-279
Matched Terms: portfolio, position
Calls: ExtractedMathRequest, MathToolRequest, _clean_number, match.group, pattern.search, re.compile

ask_ollama
File: backend/app/stacks/chat_public/ollama_chat_client.py
Lines: 46-80
Matched Terms: portfolio
Calls: data.get, data.get('message', {}).get, data.get('message', {}).get('content', '').strip, get_chat_time_context, json.dumps, json.dumps(payload).encode, json.loads, resolve_runtime_model, response.read, response.read().decode, urllib.request.Request, urllib.request.urlopen

build_retrieval_prompt_section
File: backend/app/stacks/chat_public/rag/live_retrieval.py
Lines: 121-204
Matched Terms: authorization
Calls: '\n'.join, _bounded, enumerate, len, lines.append, result.metadata.get, str, sum

build_from_paths
File: backend/app/stacks/chat_public/rag/local_index.py
Lines: 564-1006
Matched Terms: read_only
Calls: '\n'.join, KnowledgeChunk, Path, Path(path).resolve, RuntimeError, candidate.relative_to, candidate.relative_to(root).as_posix, candidate.relative_to(root).as_posix().startswith, candidate.stat, candidate.stem.replace, candidate.stem.replace('_', ' ').replace, candidate.stem.replace('_', ' ').replace('-', ' ').strip, candidate.stem.replace('_', ' ').replace('-', ' ').strip().title, candidate.suffix.lower, candidate.suffix.lower().lstrip, chunk.as_dict, chunk_text, chunks.append, chunks.sort, contains_prompt_injection, contains_secret, datetime.now, datetime.now(UTC).isoformat, document_ids.add, embedding_vectors.extend, enumerate, extract_source_sections, is_allowed_source, len, min, prepared.append, print, range, rejected.append, relative.lower, relative.startswith, root.resolve, section.get, seen_content_hashes.add, self.embedding_client.embed, self.save_atomic, set, sha256_text, sorted, stable_chunk_id, stable_document_id, str, zip

_safe_boundary_replacement
File: backend/app/stacks/chat_public/response_verification.py
Lines: 604-610
Matched Terms: portfolio
Calls: NONE EXTRACTED

normalize_overlay_role
File: backend/app/stacks/chat_public/role_overlay_registry.py
Lines: 174-195
Matched Terms: authorization
Calls: _ROLE_ALIASES.get, _clean_value, isinstance

resolve_principal_overlay
File: backend/app/stacks/chat_public/role_overlay_registry.py
Lines: 259-299
Matched Terms: authorization
Calls: _first_claim, getattr, isinstance, resolve_role_overlay

render_role_overlay
File: backend/app/stacks/chat_public/role_overlay_registry.py
Lines: 302-361
Matched Terms: authorization
Calls: '\n'.join, lines.append, lines.extend, str

role_overlays
File: backend/app/stacks/chat_public/role_overlay_registry.py
Lines: 364-368
Matched Terms: authorization
Calls: NONE EXTRACTED

test_user_overlay_remains_user_despite_developer_claim
File: backend/app/stacks/chat_public/tests/test_authenticated_role_truth_boundary.py
Lines: 27-46
Matched Terms: authorization
Calls: '\n\n'.join, render_role_overlay, resolve_role_overlay

test_developer_overlay_requires_server_supplied_developer_role
File: backend/app/stacks/chat_public/tests/test_authenticated_role_truth_boundary.py
Lines: 49-59
Matched Terms: authorization
Calls: render_role_overlay, resolve_role_overlay

test_registry_is_read_only_and_complete
File: backend/app/stacks/chat_public/tests/test_capability_state_registry.py
Lines: 14-24
Matched Terms: read_only
Calls: build_capability_registry, len

test_decision_serializes_complete_contract
File: backend/app/stacks/chat_public/tests/test_cognitive_model_router.py
Lines: 162-189
Matched Terms: portfolio
Calls: decision.as_dict, intent, isinstance, route_cognitive_request, set

test_position_size_uses_math_without_retrieval
File: backend/app/stacks/chat_public/tests/test_cognitive_model_router.py
Lines: 270-285
Matched Terms: portfolio, position
Calls: intent, route_cognitive_request

test_conversation_memory_avoids_retrieval
File: backend/app/stacks/chat_public/tests/test_cognitive_model_router.py
Lines: 302-315
Matched Terms: portfolio
Calls: intent, pytest.mark.parametrize, route_cognitive_request

test_explicit_retrieval_requests_remain_enabled
File: backend/app/stacks/chat_public/tests/test_cognitive_model_router.py
Lines: 328-340
Matched Terms: portfolio
Calls: intent, pytest.mark.parametrize, route_cognitive_request

test_strategy_family_retains_retrieval_contract
File: backend/app/stacks/chat_public/tests/test_cognitive_model_router.py
Lines: 345-357
Matched Terms: portfolio
Calls: intent, route_cognitive_request

test_market_and_portfolio_family_do_not_force_retrieval
File: backend/app/stacks/chat_public/tests/test_cognitive_model_router.py
Lines: 398-417
Matched Terms: portfolio
Calls: intent, pytest.mark.parametrize, route_cognitive_request

test_router_never_exposes_execution_authority
File: backend/app/stacks/chat_public/tests/test_cognitive_model_router.py
Lines: 420-439
Matched Terms: user_id
Calls: forbidden.isdisjoint, intent, route_cognitive_request, route_cognitive_request('Build a strategy.', intent=intent(family='STRATEGY')).as_dict

test_registry_is_explicit_and_complete
File: backend/app/stacks/chat_public/tests/test_deterministic_math_engine.py
Lines: 44-61
Matched Terms: portfolio, position
Calls: supported_operations

test_position_size
File: backend/app/stacks/chat_public/tests/test_deterministic_math_engine.py
Lines: 239-269
Matched Terms: position
Calls: Decimal, calculate, decimal_value

test_portfolio_weights
File: backend/app/stacks/chat_public/tests/test_deterministic_math_engine.py
Lines: 272-295
Matched Terms: portfolio
Calls: Decimal, calculate, decimal_value

test_serialized_result_contains_no_float_values
File: backend/app/stacks/chat_public/tests/test_deterministic_math_engine.py
Lines: 582-603
Matched Terms: read_only
Calls: calculate, result.as_serializable

test_position_size_uses_whole_units
File: backend/app/stacks/chat_public/tests/test_live_math_runtime_integration.py
Lines: 133-152
Matched Terms: position
Calls: evaluate_live_math

test_ambiguous_math_fails_controlled
File: backend/app/stacks/chat_public/tests/test_live_math_runtime_integration.py
Lines: 167-182
Matched Terms: portfolio
Calls: evaluate_live_math

result
File: backend/app/stacks/chat_public/tests/test_live_rag_activation.py
Lines: 72-104
Matched Terms: portfolio
Calls: RetrievalResult

test_strategy_family_requests_retrieval
File: backend/app/stacks/chat_public/tests/test_live_rag_activation.py
Lines: 107-118
Matched Terms: portfolio
Calls: FakeIntent, route_cognitive_request

test_semantic_retrieval_ranks_relevant_chunk_first
File: backend/app/stacks/chat_public/tests/test_local_rag_index.py
Lines: 247-307
Matched Terms: portfolio, owner
Calls: FakeEmbeddingClient, LocalKnowledgeIndex, cake.write_text, docs.mkdir, index.build_from_paths, index.retrieve, owner.write_text, results[0].citation.startswith, trading.write_text

test_index_contract_contains_no_execution_authority
File: backend/app/stacks/chat_public/tests/test_local_rag_index.py
Lines: 349-388
Matched Terms: user_id
Calls: FakeEmbeddingClient, LocalKnowledgeIndex, docs.mkdir, forbidden.isdisjoint, index.build_from_paths, source.write_text

embed
File: backend/app/stacks/chat_public/tests/test_local_rag_index.py
Lines: 25-83
Matched Terms: owner
Calls: EmbeddingBatch, normalized.append, sum, text.lower, tuple, vectors.append

test_public_chat_contract_accepts_valid_text
File: backend/app/stacks/chat_public/tests/test_public_chat_controls.py
Lines: 29-32
Matched Terms: portfolio
Calls: validate_public_chat_text

test_payload_boundary_safety_uses_only_payload
File: backend/app/stacks/chat_public/tests/test_public_chat_controls.py
Lines: 377-414
Matched Terms: portfolio
Calls: AnonymousSlidingWindowLimiter, Dependency, Payload, enforce_public_chat_controls, payload.model_dump, wrapped

model_dump
File: backend/app/stacks/chat_public/tests/test_public_chat_controls.py
Lines: 379-384
Matched Terms: portfolio
Calls: NONE EXTRACTED

test_position_size_result_passes
File: backend/app/stacks/chat_public/tests/test_response_verification.py
Lines: 145-163
Matched Terms: position
Calls: evaluate_live_math, no_retrieval, verify_response

_fake_bundle
File: backend/app/stacks/chat_public/tests/test_role_overlay_injection.py
Lines: 48-59
Matched Terms: portfolio
Calls: SimpleNamespace

test_role_overlay_is_inserted_in_correct_order
File: backend/app/stacks/chat_public/tests/test_role_overlay_injection.py
Lines: 62-99
Matched Terms: authorization
Calls: AsyncMock, _fake_bundle, asyncio.run, context_assembler.assemble_chat_context, monkeypatch.setattr, render_role_overlay, resolve_role_overlay, result.prompt.index

test_unknown_role_fails_closed_to_user_overlay
File: backend/app/stacks/chat_public/tests/test_role_overlay_injection.py
Lines: 204-221
Matched Terms: authorization
Calls: render_role_overlay, resolve_role_overlay

test_every_canonical_role_has_an_overlay
File: backend/app/stacks/chat_public/tests/test_role_overlay_registry.py
Lines: 28-38
Matched Terms: authorization
Calls: isinstance, role_overlays, set

test_role_aliases_use_canonical_roles
File: backend/app/stacks/chat_public/tests/test_role_overlay_registry.py
Lines: 66-70
Matched Terms: authorization
Calls: normalize_overlay_role, pytest.mark.parametrize

test_unknown_role_fails_closed_to_user
File: backend/app/stacks/chat_public/tests/test_role_overlay_registry.py
Lines: 73-84
Matched Terms: authorization
Calls: normalize_overlay_role

test_principal_claims_resolve_role_and_tier
File: backend/app/stacks/chat_public/tests/test_role_overlay_registry.py
Lines: 111-140
Matched Terms: authorization
Calls: AuthenticatedPrincipal, iter, next, resolve_principal_overlay

test_missing_claims_fail_closed_to_user
File: backend/app/stacks/chat_public/tests/test_role_overlay_registry.py
Lines: 143-159
Matched Terms: authorization
Calls: AuthenticatedPrincipal, resolve_principal_overlay

test_overlay_is_conversational_not_authoritative
File: backend/app/stacks/chat_public/tests/test_role_overlay_registry.py
Lines: 162-178
Matched Terms: authorization
Calls: render_role_overlay, resolve_role_overlay

test_overlay_models_are_immutable
File: backend/app/stacks/chat_public/tests/test_role_overlay_registry.py
Lines: 181-191
Matched Terms: authorization
Calls: pytest.raises, resolve_role_overlay

test_role_overlay_registry_is_immutable
File: backend/app/stacks/chat_public/tests/test_role_overlay_registry.py
Lines: 194-204
Matched Terms: authorization
Calls: pytest.raises, role_overlays

test_owner_alias_resolves_to_developer_not_new_role
File: backend/app/stacks/chat_public/tests/test_role_overlay_registry.py
Lines: 225-235
Matched Terms: owner, authorization
Calls: resolve_role_overlay

get_chat_time_context
File: backend/app/stacks/chat_public/time_context.py
Lines: 9-25
Matched Terms: session
Calls: datetime.now, tsx_now.replace, tsx_now.strftime, tsx_now.weekday, user_now.strftime

init_db
File: backend/app/stacks/db_runtime/database.py
Lines: 86-101
Matched Terms: position
Calls: connection.run_sync, engine.begin

test_guard_does_not_rollback_successful_scope
File: backend/app/stacks/db_runtime/tests/test_transaction_guard.py
Lines: 26-35
Matched Terms: session
Calls: FakeSession, transaction_guard

test_guard_rolls_back_write_failure_and_reraises
File: backend/app/stacks/db_runtime/tests/test_transaction_guard.py
Lines: 39-53
Matched Terms: session
Calls: FakeSession, RuntimeError, pytest.raises, transaction_guard

test_guard_rolls_back_commit_failure_and_reraises
File: backend/app/stacks/db_runtime/tests/test_transaction_guard.py
Lines: 57-75
Matched Terms: session
Calls: CommitFailure, FakeSession, pytest.raises, transaction_guard

test_guard_rolls_back_cancellation
File: backend/app/stacks/db_runtime/tests/test_transaction_guard.py
Lines: 79-95
Matched Terms: session
Calls: Cancellation, FakeSession, pytest.raises, transaction_guard

test_legacy_market_schema_remains_isolated
File: backend/app/stacks/db_runtime/tests/test_transaction_guard.py
Lines: 229-251
Matched Terms: session
Calls: Path, Path('backend/app/stacks/db_model/market_schema.py').read_text

test_success_executes_flush_then_commit
File: backend/app/stacks/db_runtime/tests/test_transaction_manager.py
Lines: 71-101
Matched Terms: session
Calls: FakeSession, TransactionManager, active_session.events.append, manager.execute

test_operation_failure_rolls_back_and_reraises
File: backend/app/stacks/db_runtime/tests/test_transaction_manager.py
Lines: 105-138
Matched Terms: session
Calls: FakeSession, RuntimeError, TransactionManager, active_session.events.append, manager.execute, pytest.raises

test_flush_failure_rolls_back_and_reraises
File: backend/app/stacks/db_runtime/tests/test_transaction_manager.py
Lines: 142-175
Matched Terms: session
Calls: FakeSession, TransactionManager, active_session.events.append, manager.execute, pytest.raises

test_commit_failure_rolls_back_and_reraises
File: backend/app/stacks/db_runtime/tests/test_transaction_manager.py
Lines: 179-212
Matched Terms: session
Calls: FakeSession, TransactionManager, active_session.events.append, manager.execute, pytest.raises

test_non_callable_operation_is_rejected
File: backend/app/stacks/db_runtime/tests/test_transaction_manager.py
Lines: 216-229
Matched Terms: session
Calls: FakeSession, TransactionManager, manager.execute, pytest.raises

operation
File: backend/app/stacks/db_runtime/tests/test_transaction_manager.py
Lines: 78-87
Matched Terms: session
Calls: active_session.events.append

operation
File: backend/app/stacks/db_runtime/tests/test_transaction_manager.py
Lines: 112-121
Matched Terms: session
Calls: RuntimeError, active_session.events.append

operation
File: backend/app/stacks/db_runtime/tests/test_transaction_manager.py
Lines: 151-158
Matched Terms: session
Calls: active_session.events.append

operation
File: backend/app/stacks/db_runtime/tests/test_transaction_manager.py
Lines: 188-195
Matched Terms: session
Calls: active_session.events.append

__init__
File: backend/app/stacks/db_runtime/transaction_manager.py
Lines: 82-86
Matched Terms: session
Calls: NONE EXTRACTED

session
File: backend/app/stacks/db_runtime/transaction_manager.py
Lines: 89-92
Matched Terms: session
Calls: NONE EXTRACTED

execute
File: backend/app/stacks/db_runtime/transaction_manager.py
Lines: 94-117
Matched Terms: session
Calls: TypeError, callable, operation, self._session.commit, self._session.flush, transaction_guard

process_portfolio_output
File: backend/app/stacks/execution/paper_broker.py
Lines: 21-227
Matched Terms: portfolio, position, user_id
Calls: ValueError, calculate_live_portfolio_equity, calculate_position_size, create_trace_id, drawdown_healthcheck, drawdown_status.get, emit_runtime_step, equity_matrix.get, execute_trade, float, generate_signal, get_bars, get_latest_price, get_live_market_price, is_kill_switch_active, isinstance, live_feed.get, portfolio_output.get, position.get, random.uniform, raw_output_signal.get, save_log, sizing_matrix.get, str, str(signal).lower, str(user_id).strip, trade_result.get

get_positions_snapshot
File: backend/app/stacks/execution/paper_broker.py
Lines: 231-250
Matched Terms: portfolio, position, user_id
Calls: ValueError, str, str(user_id).strip

__init__
File: backend/app/stacks/identity_auth/access_token_revocation_cleanup_service.py
Lines: 22-31
Matched Terms: session
Calls: AccessTokenRevocationRepository

cleanup_expired
File: backend/app/stacks/identity_auth/access_token_revocation_cleanup_service.py
Lines: 33-51
Matched Terms: session
Calls: self._repository.cleanup_expired, self._session.commit, self._session.rollback

__init__
File: backend/app/stacks/identity_auth/access_token_revocation_repository.py
Lines: 48-52
Matched Terms: session
Calls: NONE EXTRACTED

revoke
File: backend/app/stacks/identity_auth/access_token_revocation_repository.py
Lines: 54-146
Matched Terms: session, user_id
Calls: IdentityAccessTokenRevocation, ValueError, _normalize_datetime, _utc_now_naive, len, reason.strip, self._session.add, self._session.flush, self.get_by_token_id, token_id.strip, user_id.strip

get_by_token_id
File: backend/app/stacks/identity_auth/access_token_revocation_repository.py
Lines: 148-168
Matched Terms: session
Calls: result.scalar_one_or_none, select, select(IdentityAccessTokenRevocation).where, self._session.execute, token_id.strip

cleanup_expired
File: backend/app/stacks/identity_auth/access_token_revocation_repository.py
Lines: 197-229
Matched Terms: session
Calls: _normalize_datetime, _utc_now_naive, delete, delete(IdentityAccessTokenRevocation).where, getattr, int, self._session.execute, self._session.flush

list_records
File: backend/app/stacks/identity_auth/access_token_revocation_repository.py
Lines: 232-355
Matched Terms: session, user_id
Calls: IdentityAccessTokenRevocation.id.desc, IdentityAccessTokenRevocation.revoked_at.desc, ValueError, _normalize_datetime, _utc_now_naive, count_result.scalar_one, count_statement.where, filters.append, func.count, int, list, list_result.scalars, list_result.scalars().all, list_statement.where, select, select(IdentityAccessTokenRevocation).order_by, select(IdentityAccessTokenRevocation).order_by(IdentityAccessTokenRevocation.revoked_at.desc(), IdentityAccessTokenRevocation.id.desc()).offset, select(IdentityAccessTokenRevocation).order_by(IdentityAccessTokenRevocation.revoked_at.desc(), IdentityAccessTokenRevocation.id.desc()).offset(offset).limit, select(func.count()).select_from, self._session.execute, state.strip, state.strip().lower, user_id.strip

get_by_id
File: backend/app/stacks/identity_auth/access_token_revocation_repository.py
Lines: 357-377
Matched Terms: session
Calls: result.scalar_one_or_none, revocation_id.strip, select, select(IdentityAccessTokenRevocation).where, self._session.execute

get_administrative_user_mutation_service
File: backend/app/stacks/identity_auth/admin_mutation_dependencies.py
Lines: 13-20
Matched Terms: session
Calls: AdministrativeUserMutationService, async_session

require_password_reset
File: backend/app/stacks/identity_auth/admin_mutation_router.py
Lines: 34-46
Matched Terms: user_id
Calls: Depends, router.post, service.require_password_reset

issue_temporary_password
File: backend/app/stacks/identity_auth/admin_mutation_router.py
Lines: 55-67
Matched Terms: user_id
Calls: Depends, router.post, service.issue_temporary_password

disable_account
File: backend/app/stacks/identity_auth/admin_mutation_router.py
Lines: 74-86
Matched Terms: user_id
Calls: Depends, router.post, service.disable_account

enable_account
File: backend/app/stacks/identity_auth/admin_mutation_router.py
Lines: 93-105
Matched Terms: user_id
Calls: Depends, router.post, service.enable_account

delete_account
File: backend/app/stacks/identity_auth/admin_mutation_router.py
Lines: 112-124
Matched Terms: user_id
Calls: Depends, router.delete, service.delete_account

_principal_subject
File: backend/app/stacks/identity_auth/admin_mutation_service.py
Lines: 61-79
Matched Terms: user_id
Calls: HTTPException, getattr, str

__init__
File: backend/app/stacks/identity_auth/admin_mutation_service.py
Lines: 155-160
Matched Terms: session
Calls: NONE EXTRACTED

_load_target
File: backend/app/stacks/identity_auth/admin_mutation_service.py
Lines: 162-183
Matched Terms: session, user_id
Calls: HTTPException, result.scalar_one_or_none, select, select(IdentityUser).where, self._session.execute

_assert_target_mutable
File: backend/app/stacks/identity_auth/admin_mutation_service.py
Lines: 208-234
Matched Terms: owner
Calls: HTTPException, _normalized_role, getattr, str

_revoke_refresh_sessions
File: backend/app/stacks/identity_auth/admin_mutation_service.py
Lines: 236-263
Matched Terms: session, user_id
Calls: IdentityRefreshSession.revoked_at.is_, datetime.now, int, self._session.execute, update, update(IdentityRefreshSession).where, update(IdentityRefreshSession).where(IdentityRefreshSession.user_id == user_id).where, update(IdentityRefreshSession).where(IdentityRefreshSession.user_id == user_id).where(IdentityRefreshSession.revoked_at.is_(None)).values

_audit
File: backend/app/stacks/identity_auth/admin_mutation_service.py
Lines: 265-280
Matched Terms: user_id
Calls: logger.info

require_password_reset
File: backend/app/stacks/identity_auth/admin_mutation_service.py
Lines: 282-328
Matched Terms: session, user_id
Calls: AdministrativeMutationResponse, self._assert_target_mutable, self._audit, self._authorize_actor, self._load_target, self._revoke_refresh_sessions, self._session.commit, self._session.rollback

issue_temporary_password
File: backend/app/stacks/identity_auth/admin_mutation_service.py
Lines: 330-385
Matched Terms: session, user_id
Calls: AdministrativeTemporaryPasswordResponse, _generate_temporary_password, hash_password, self._assert_target_mutable, self._audit, self._authorize_actor, self._load_target, self._revoke_refresh_sessions, self._session.commit, self._session.rollback

disable_account
File: backend/app/stacks/identity_auth/admin_mutation_service.py
Lines: 387-434
Matched Terms: session, user_id
Calls: AdministrativeMutationResponse, _set_status, self._assert_target_mutable, self._audit, self._authorize_actor, self._load_target, self._revoke_refresh_sessions, self._session.commit, self._session.rollback

enable_account
File: backend/app/stacks/identity_auth/admin_mutation_service.py
Lines: 436-477
Matched Terms: session, user_id
Calls: AdministrativeMutationResponse, _set_status, self._assert_target_mutable, self._audit, self._authorize_actor, self._load_target, self._session.commit, self._session.rollback

delete_account
File: backend/app/stacks/identity_auth/admin_mutation_service.py
Lines: 479-536
Matched Terms: session, user_id
Calls: AdministrativeDeleteResponse, delete, delete(IdentityAccessTokenRevocation).where, delete(IdentityRefreshSession).where, self._assert_target_mutable, self._audit, self._authorize_actor, self._load_target, self._session.commit, self._session.delete, self._session.execute, self._session.rollback

administrative_database_session
File: backend/app/stacks/identity_auth/admin_read_dependencies.py
Lines: 56-60
Matched Terms: session
Calls: async_session

require_administrative_principal
File: backend/app/stacks/identity_auth/admin_read_dependencies.py
Lines: 63-204
Matched Terms: session, user_id, authorization
Calls: AccessTokenRevocationRepository, AdministrativePrincipal, Depends, HTTPException, authenticate_bearer_credentials, bool, canonical_role_value, getattr, is_administrative_role, result.scalar_one_or_none, revocation_repository.is_revoked, select, select(IdentityUser).where, session.execute, str, str(getattr(principal, 'subject', '')).strip, str(getattr(user, 'role', '')).strip, str(getattr(user, 'role', '')).strip().lower

get_administrative_read_service
File: backend/app/stacks/identity_auth/admin_read_dependencies.py
Lines: 207-214
Matched Terms: session
Calls: AdministrativeReadService, Depends

_session_identifier
File: backend/app/stacks/identity_auth/admin_read_models.py
Lines: 65-86
Matched Terms: session
Calls: RuntimeError, _string_value, getattr

_session_family_identifier
File: backend/app/stacks/identity_auth/admin_read_models.py
Lines: 89-107
Matched Terms: session
Calls: _string_value, getattr

_replacement_identifier
File: backend/app/stacks/identity_auth/admin_read_models.py
Lines: 110-129
Matched Terms: session
Calls: _string_value, getattr

_session_state
File: backend/app/stacks/identity_auth/admin_read_models.py
Lines: 132-170
Matched Terms: session
Calls: _datetime_value, _replacement_identifier, datetime.now, getattr

_user_summary
File: backend/app/stacks/identity_auth/admin_read_models.py
Lines: 173-227
Matched Terms: user_id
Calls: AdministrativeUserSummary, _datetime_value, _string_value, bool, getattr

_session_summary
File: backend/app/stacks/identity_auth/admin_read_models.py
Lines: 230-274
Matched Terms: session, user_id
Calls: AdministrativeSessionSummary, _datetime_value, _replacement_identifier, _session_identifier, _session_state, _string_value, getattr

__init__
File: backend/app/stacks/identity_auth/admin_read_models.py
Lines: 282-286
Matched Terms: session
Calls: NONE EXTRACTED

list_users
File: backend/app/stacks/identity_auth/admin_read_models.py
Lines: 288-329
Matched Terms: session
Calls: AdministrativeUserListResponse, IdentityUser.email_normalized.asc, _user_summary, len, result.scalars, result.scalars().all, select, select(IdentityUser).order_by, select(IdentityUser).order_by(IdentityUser.email_normalized.asc()).offset, select(IdentityUser).order_by(IdentityUser.email_normalized.asc()).offset(offset).limit, self._session.execute, tuple

get_user
File: backend/app/stacks/identity_auth/admin_read_models.py
Lines: 331-408
Matched Terms: session, user_id
Calls: AdministrativeUserDetail, IdentityRefreshSession.revoked_at.is_, _user_summary, active_result.scalar_one, datetime.now, func.count, int, result.scalar_one_or_none, select, select(IdentityUser).where, select(func.count()).select_from, select(func.count()).select_from(IdentityRefreshSession).where, self._session.execute, summary.model_dump, total_result.scalar_one

list_sessions
File: backend/app/stacks/identity_auth/admin_read_models.py
Lines: 410-468
Matched Terms: session, user_id
Calls: AdministrativeSessionListResponse, IdentityRefreshSession.issued_at.desc, _session_summary, len, result.scalars, result.scalars().all, select, self._session.execute, statement.order_by, statement.order_by(IdentityRefreshSession.issued_at.desc()).offset, statement.order_by(IdentityRefreshSession.issued_at.desc()).offset(offset).limit, statement.where, tuple

get_session
File: backend/app/stacks/identity_auth/admin_read_models.py
Lines: 470-516
Matched Terms: session
Calls: AdministrativeSessionDetail, _replacement_identifier, _session_family_identifier, _session_summary, getattr, result.scalar_one_or_none, select, select(IdentityRefreshSession).where, self._session.execute, summary.model_dump

_revocation_summary
File: backend/app/stacks/identity_auth/admin_read_models.py
Lines: 559-574
Matched Terms: user_id
Calls: AdministrativeAccessTokenRevocationSummary, cls._revocation_state

list_access_token_revocations
File: backend/app/stacks/identity_auth/admin_read_models.py
Lines: 576-607
Matched Terms: session, user_id
Calls: AccessTokenRevocationRepository, AdministrativeAccessTokenRevocationListResponse, repository.list_records, self._revocation_summary

get_access_token_revocation
File: backend/app/stacks/identity_auth/admin_read_models.py
Lines: 609-631
Matched Terms: session
Calls: AccessTokenRevocationRepository, AdministrativeAccessTokenRevocationDetail, repository.get_by_id, self._revocation_summary, summary.model_dump

administrative_introspection
File: backend/app/stacks/identity_auth/admin_read_router.py
Lines: 49-63
Matched Terms: session, authorization, read_only
Calls: AdministrativeIntrospectionResponse, Depends, router.get

get_administrative_user
File: backend/app/stacks/identity_auth/admin_read_router.py
Lines: 101-122
Matched Terms: user_id
Calls: Depends, HTTPException, router.get, service.get_user

list_administrative_sessions
File: backend/app/stacks/identity_auth/admin_read_router.py
Lines: 131-167
Matched Terms: session, user_id
Calls: Depends, Query, router.get, service.list_sessions

get_administrative_session
File: backend/app/stacks/identity_auth/admin_read_router.py
Lines: 176-197
Matched Terms: session
Calls: Depends, HTTPException, router.get, service.get_session

list_access_token_revocations
File: backend/app/stacks/identity_auth/admin_read_router.py
Lines: 206-237
Matched Terms: user_id
Calls: Depends, Query, router.get, service.list_access_token_revocations

get_registration_api_service
File: backend/app/stacks/identity_auth/api_dependencies.py
Lines: 63-77
Matched Terms: session
Calls: authentication_runtime

get_login_api_service
File: backend/app/stacks/identity_auth/api_dependencies.py
Lines: 80-94
Matched Terms: session
Calls: authentication_runtime

require_authenticated_principal
File: backend/app/stacks/identity_auth/api_dependencies.py
Lines: 97-185
Matched Terms: session, authorization
Calls: AccessTokenRevocationRepository, Depends, HTTPException, async_session, authenticate_bearer_credentials, getattr, repository.is_revoked

optional_logout_access_principal
File: backend/app/stacks/identity_auth/api_dependencies.py
Lines: 188-223
Matched Terms: authorization
Calls: Depends, HTTPException, authenticate_bearer_credentials

get_session_lifecycle_api_service
File: backend/app/stacks/identity_auth/api_dependencies.py
Lines: 226-230
Matched Terms: session
Calls: session_lifecycle_runtime

get_required_password_change_service
File: backend/app/stacks/identity_auth/api_dependencies.py
Lines: 232-245
Matched Terms: session
Calls: IdentityUserRepository, RefreshSessionRepository, RequiredPasswordChangeService, async_session

get_session_repository
File: backend/app/stacks/identity_auth/api_dependencies.py
Lines: 248-250
Matched Terms: session
Calls: IdentityUserRepository, async_session

change_required_password
File: backend/app/stacks/identity_auth/api_router.py
Lines: 240-279
Matched Terms: session, user_id
Calls: ChangeRequiredPasswordApiResponse, Depends, HTTPException, getattr, isinstance, router.post, service.replace_required_password

refresh_session
File: backend/app/stacks/identity_auth/api_router.py
Lines: 287-348
Matched Terms: session
Calls: Depends, HTTPException, SessionTokenApiResponse, isinstance, result.token_type.lower, router.post, service.refresh

logout_session
File: backend/app/stacks/identity_auth/api_router.py
Lines: 356-425
Matched Terms: session, user_id
Calls: Depends, HTTPException, SessionActionApiResponse, datetime.fromtimestamp, getattr, isinstance, router.post, service.logout

logout_all_sessions
File: backend/app/stacks/identity_auth/api_router.py
Lines: 433-484
Matched Terms: session, user_id
Calls: Depends, HTTPException, LogoutAllApiResponse, getattr, isinstance, router.post, service.logout_all

session_introspection
File: backend/app/stacks/identity_auth/api_router.py
Lines: 492-496
Matched Terms: session
Calls: Depends, get_session_introspection, router.get

logout_all
File: backend/app/stacks/identity_auth/api_router.py
Lines: 96-101
Matched Terms: user_id
Calls: NONE EXTRACTED

normalize_role
File: backend/app/stacks/identity_auth/authorization_policy.py
Lines: 120-134
Matched Terms: authorization
Calls: ROLE_ALIASES.get, isinstance, value.strip, value.strip().lower

authorize
File: backend/app/stacks/identity_auth/authorization_policy.py
Lines: 232-292
Matched Terms: authorization
Calls: AuthorizationDecision, frozenset, has_permission, isinstance, normalize_role, permission.strip, permissions_for_role, required.add, set

authenticate_bearer_credentials
File: backend/app/stacks/identity_auth/dependencies.py
Lines: 31-81
Matched Terms: authorization
Calls: AuthenticatedPrincipal, HTTPException, credentials.scheme.lower, validate_access_token

require_authenticated_principal
File: backend/app/stacks/identity_auth/dependencies.py
Lines: 84-92
Matched Terms: authorization
Calls: authenticate_bearer_credentials

provision_dev_owner
File: backend/app/stacks/identity_auth/dev_owner_provisioner.py
Lines: 38-105
Matched Terms: session, user_id, owner
Calls: DevOwnerProvisioningResult, IdentityUserRepository, async_session, engine.dispose, hash_password, repository.create, repository.get_by_email, repository.update_identity_security_state, repository.update_password_hash, session.commit, session.refresh, verify_password

__init__
File: backend/app/stacks/identity_auth/login_service.py
Lines: 28-70
Matched Terms: session
Calls: ValueError

login
File: backend/app/stacks/identity_auth/login_service.py
Lines: 72-227
Matched Terms: session, user_id, authorization
Calls: AuthenticationRejectedError, AuthenticationTokenPair, bool, canonical_role_value, getattr, isinstance, normalize_email, normalize_subscription_tier, self._commit, self._hash_refresh_token, self._perform_dummy_verification, self._refresh_session_repository.create, self._rollback, self._token_issuer.issue_access_token, self._token_issuer.issue_refresh_token, self._user_repository.get_by_email, self._verify_password

__init__
File: backend/app/stacks/identity_auth/mock_runtime.py
Lines: 90-95
Matched Terms: session
Calls: NONE EXTRACTED

create
File: backend/app/stacks/identity_auth/mock_runtime.py
Lines: 97-123
Matched Terms: session, user_id
Calls: MockRefreshSession, RuntimeError, self.sessions.append

__init__
File: backend/app/stacks/identity_auth/mock_runtime.py
Lines: 288-343
Matched Terms: session
Calls: LoginService, MockIdentityUserRepository, MockRefreshSessionRepository, MockServiceTokenIssuer, MockTransactionBoundary, RegistrationService, mock_hash_password

__init__
File: backend/app/stacks/identity_auth/password_change_service.py
Lines: 59-70
Matched Terms: session
Calls: NONE EXTRACTED

replace_required_password
File: backend/app/stacks/identity_auth/password_change_service.py
Lines: 72-169
Matched Terms: session, user_id
Calls: PasswordChangeRejectedError, PasswordChangeResult, datetime.now, hash_password, isinstance, self._commit, self._refresh_repository.revoke_all_for_user, self._rollback, self._user_repository.get_by_id, self._user_repository.update_identity_security_state, self._user_repository.update_password_hash, validate_replacement_password, verify_password

register
File: backend/app/stacks/identity_auth/registration_service.py
Lines: 39-123
Matched Terms: user_id
Calls: RegisteredIdentity, RegistrationRejectedError, command.display_name.strip, isinstance, len, normalize_email, self._commit, self._hash_password, self._rollback, self._user_repository.create, self._user_repository.get_by_email

__init__
File: backend/app/stacks/identity_auth/repositories.py
Lines: 73-77
Matched Terms: session
Calls: NONE EXTRACTED

create
File: backend/app/stacks/identity_auth/repositories.py
Lines: 79-117
Matched Terms: session
Calls: IdentityUser, ValueError, bool, normalize_email, normalize_identity_role, self._session.add, self._session.flush

get_by_id
File: backend/app/stacks/identity_auth/repositories.py
Lines: 119-126
Matched Terms: session, user_id
Calls: self._session.get

get_by_email
File: backend/app/stacks/identity_auth/repositories.py
Lines: 128-145
Matched Terms: session
Calls: (await self._session.execute(statement)).scalar_one_or_none, normalize_email, select, select(IdentityUser).where, self._session.execute

update_identity_security_state
File: backend/app/stacks/identity_auth/repositories.py
Lines: 147-166
Matched Terms: session
Calls: bool, normalize_identity_role, self._session.flush

update_password_hash
File: backend/app/stacks/identity_auth/repositories.py
Lines: 168-186
Matched Terms: session
Calls: ValueError, isinstance, self._session.flush

__init__
File: backend/app/stacks/identity_auth/repositories.py
Lines: 196-200
Matched Terms: session
Calls: NONE EXTRACTED

create
File: backend/app/stacks/identity_auth/repositories.py
Lines: 202-247
Matched Terms: session, user_id
Calls: ValueError, _IdentityRefreshSession, _refresh_uuid4, self._session.add, self._session.flush, str

get_by_token_id
File: backend/app/stacks/identity_auth/repositories.py
Lines: 249-274
Matched Terms: session
Calls: (await self._session.execute(statement)).scalar_one_or_none, _refresh_select, _refresh_select(_IdentityRefreshSession).where, self._session.execute, statement.with_for_update

revoke
File: backend/app/stacks/identity_auth/repositories.py
Lines: 276-287
Matched Terms: session
Calls: self._session.flush

revoke_family
File: backend/app/stacks/identity_auth/repositories.py
Lines: 289-318
Matched Terms: session
Calls: _IdentityRefreshSession.revoked_at.is_, _refresh_update, _refresh_update(_IdentityRefreshSession).where, _refresh_update(_IdentityRefreshSession).where(_IdentityRefreshSession.family_id == family_id).where, _refresh_update(_IdentityRefreshSession).where(_IdentityRefreshSession.family_id == family_id).where(_IdentityRefreshSession.revoked_at.is_(None)).values, int, self._session.execute

revoke_all_for_user
File: backend/app/stacks/identity_auth/repositories.py
Lines: 320-349
Matched Terms: session, user_id
Calls: _IdentityRefreshSession.revoked_at.is_, _refresh_update, _refresh_update(_IdentityRefreshSession).where, _refresh_update(_IdentityRefreshSession).where(_IdentityRefreshSession.user_id == user_id).where, _refresh_update(_IdentityRefreshSession).where(_IdentityRefreshSession.user_id == user_id).where(_IdentityRefreshSession.revoked_at.is_(None)).values, int, self._session.execute

delete_expired
File: backend/app/stacks/identity_auth/repositories.py
Lines: 351-375
Matched Terms: session
Calls: _refresh_datetime.now, _refresh_delete, _refresh_delete(_IdentityRefreshSession).where, int, self._session.execute

_extract_bearer_credentials
File: backend/app/stacks/identity_auth/route_protection.py
Lines: 283-309
Matched Terms: authorization
Calls: HTTPAuthorizationCredentials, authorization.partition, request.headers.get, scheme.lower, token.strip

_authenticate_with_durable_revocation
File: backend/app/stacks/identity_auth/route_protection.py
Lines: 332-362
Matched Terms: session, authorization
Calls: AccessTokenRevocationRepository, async_session, authenticate_bearer_credentials, getattr, repository.is_revoked

_load_identity_authorization_state
File: backend/app/stacks/identity_auth/route_protection.py
Lines: 425-447
Matched Terms: session, user_id, authorization
Calls: IdentityUserRepository, async_session, repository.get_by_id

enforce_route_policy
File: backend/app/stacks/identity_auth/route_protection.py
Lines: 450-859
Matched Terms: user_id, owner, authorization
Calls: _authenticate_request, _forbidden, _load_identity_authorization_state, _principal_roles, _unauthorized, bool, call_next, create_trace_id, emit_runtime_step, finish, getattr, identity_state.get, perf_counter, request.headers.get, resolve_route_policy, str

finish
File: backend/app/stacks/identity_auth/route_protection.py
Lines: 525-565
Matched Terms: user_id, authorization
Calls: emit_runtime_step, perf_counter

build_authentication_runtime
File: backend/app/stacks/identity_auth/runtime_adapter.py
Lines: 273-343
Matched Terms: session
Calls: EnvironmentJwtTokenIssuer, IdentityUserRepository, LoginService, RefreshSessionRepository, RegistrationService, hash_password, hash_refresh_token, load_jwt_secret

authentication_runtime
File: backend/app/stacks/identity_auth/runtime_adapter.py
Lines: 347-364
Matched Terms: session
Calls: async_session, build_authentication_runtime

build_session_lifecycle_runtime
File: backend/app/stacks/identity_auth/runtime_adapter.py
Lines: 367-451
Matched Terms: session
Calls: AccessTokenRevocationRepository, EnvironmentJwtTokenIssuer, IdentityUserRepository, RefreshSessionRepository, RefreshSessionService, SessionLifecycleService, ValidatedRefreshIdentity, _as_identifier, _claim_value, hash_refresh_token, load_jwt_secret, validate_refresh_token, verify_refresh_token_hash

session_lifecycle_runtime
File: backend/app/stacks/identity_auth/runtime_adapter.py
Lines: 455-461
Matched Terms: session
Calls: async_session, build_session_lifecycle_runtime

get_session_introspection
File: backend/app/stacks/identity_auth/session_introspection.py
Lines: 16-52
Matched Terms: session, user_id
Calls: HTTPException, any, canonical_role_value, list, normalize_subscription_tier, permissions_for_role, session_repo.get_by_id

__init__
File: backend/app/stacks/identity_auth/session_lifecycle_service.py
Lines: 96-139
Matched Terms: session
Calls: NONE EXTRACTED

_validated_record
File: backend/app/stacks/identity_auth/session_lifecycle_service.py
Lines: 141-196
Matched Terms: session, user_id
Calls: SessionLifecycleRejectedError, isinstance, self._refresh_repository.get_by_token_id, self._validate_refresh_token, self._verify_refresh_token

refresh
File: backend/app/stacks/identity_auth/session_lifecycle_service.py
Lines: 198-333
Matched Terms: session, authorization
Calls: AuthenticationTokenPair, SessionLifecycleRejectedError, canonical_role_value, normalize_subscription_tier, self._commit, self._hash_refresh_token, self._refresh_service.rotate, self._rollback, self._token_issuer.issue_access_token, self._token_issuer.issue_refresh_token, self._user_repository.get_by_id, self._validated_record

logout
File: backend/app/stacks/identity_auth/session_lifecycle_service.py
Lines: 335-389
Matched Terms: session, user_id
Calls: SessionLifecycleRejectedError, self._access_revocation_repository.revoke, self._commit, self._refresh_service.logout, self._rollback, self._validated_record

logout_all
File: backend/app/stacks/identity_auth/session_lifecycle_service.py
Lines: 391-425
Matched Terms: session, user_id
Calls: SessionLifecycleRejectedError, isinstance, self._commit, self._refresh_service.revoke_all, self._rollback

cleanup_expired
File: backend/app/stacks/identity_auth/session_lifecycle_service.py
Lines: 427-448
Matched Terms: session
Calls: SessionLifecycleRejectedError, self._commit, self._refresh_service.cleanup_expired, self._rollback

__init__
File: backend/app/stacks/identity_auth/session_service.py
Lines: 49-59
Matched Terms: session
Calls: RefreshSessionRepository

rotate
File: backend/app/stacks/identity_auth/session_service.py
Lines: 61-127
Matched Terms: session, user_id
Calls: RefreshSessionExpiredError, RefreshSessionNotFoundError, RefreshTokenReuseDetectedError, RotationResult, datetime.now, self._repository.create, self._repository.get_by_token_id, self._repository.revoke, self._repository.revoke_family

revoke_all
File: backend/app/stacks/identity_auth/session_service.py
Lines: 152-164
Matched Terms: user_id
Calls: datetime.now, self._repository.revoke_all_for_user

test_wrong_scheme_is_unauthorized
File: backend/app/stacks/identity_auth/tests/test_api_dependency.py
Lines: 46-59
Matched Terms: authorization
Calls: HTTPAuthorizationCredentials, authenticate_bearer_credentials, pytest.raises

test_valid_access_token_returns_principal
File: backend/app/stacks/identity_auth/tests/test_api_dependency.py
Lines: 62-82
Matched Terms: authorization
Calls: HTTPAuthorizationCredentials, authenticate_bearer_credentials, issue_access_token

test_refresh_token_is_rejected_by_api_dependency
File: backend/app/stacks/identity_auth/tests/test_api_dependency.py
Lines: 85-102
Matched Terms: authorization
Calls: HTTPAuthorizationCredentials, authenticate_bearer_credentials, issue_refresh_token, pytest.raises

test_malformed_token_is_unauthorized
File: backend/app/stacks/identity_auth/tests/test_api_dependency.py
Lines: 105-118
Matched Terms: authorization
Calls: HTTPAuthorizationCredentials, authenticate_bearer_credentials, pytest.raises

register
File: backend/app/stacks/identity_auth/tests/test_api_route_contract.py
Lines: 38-51
Matched Terms: user_id
Calls: RegisteredIdentity, command.email.lower

build_test_app
File: backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py
Lines: 15-48
Matched Terms: analytics
Calls: FastAPI, app.get, app.middleware, app.middleware('http'), app.post

test_route_policy_inventory
File: backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py
Lines: 51-90
Matched Terms: analytics
Calls: route_protection.resolve_route_policy

test_authenticated_route_rejects_missing_token
File: backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py
Lines: 105-118
Matched Terms: analytics
Calls: TestClient, build_test_app, client.get

test_authenticated_route_accepts_principal
File: backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py
Lines: 121-168
Matched Terms: analytics, user_id, authorization
Calls: SimpleNamespace, TestClient, build_test_app, client.get, monkeypatch.setattr

test_admin_route_rejects_non_admin
File: backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py
Lines: 171-218
Matched Terms: user_id, authorization
Calls: SimpleNamespace, TestClient, build_test_app, client.post, monkeypatch.setattr

test_admin_route_accepts_server_claim
File: backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py
Lines: 221-268
Matched Terms: user_id, authorization
Calls: SimpleNamespace, TestClient, build_test_app, client.post, monkeypatch.setattr

test_refresh_token_validation_failure_is_unauthorized
File: backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py
Lines: 283-312
Matched Terms: analytics, authorization
Calls: RuntimeError, TestClient, build_test_app, client.get, monkeypatch.setattr

analytics
File: backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py
Lines: 27-30
Matched Terms: analytics
Calls: app.get

load_identity_state
File: backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py
Lines: 137-147
Matched Terms: user_id
Calls: NONE EXTRACTED

load_identity_state
File: backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py
Lines: 187-197
Matched Terms: user_id
Calls: NONE EXTRACTED

load_identity_state
File: backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py
Lines: 237-247
Matched Terms: user_id
Calls: NONE EXTRACTED

test_auth_router_has_complete_session_lifecycle
File: backend/app/stacks/identity_auth/tests/test_canonical_router_inclusion.py
Lines: 95-128
Matched Terms: session
Calls: NONE EXTRACTED

register
File: backend/app/stacks/identity_auth/tests/test_canonical_router_inclusion.py
Lines: 32-40
Matched Terms: user_id
Calls: RegisteredIdentity, command.email.lower

test_registration_with_display_name
File: backend/app/stacks/identity_auth/tests/test_display_name.py
Lines: 18-63
Matched Terms: user_id
Calls: AsyncMock, MagicMock, RegistrationCommand, RegistrationService, mock_user_repo.create.assert_called_once_with, service.register

test_registration_with_trimmed_display_name
File: backend/app/stacks/identity_auth/tests/test_display_name.py
Lines: 67-110
Matched Terms: user_id
Calls: AsyncMock, MagicMock, RegistrationCommand, RegistrationService, mock_user_repo.create.assert_called_once_with, service.register

test_registration_without_display_name
File: backend/app/stacks/identity_auth/tests/test_display_name.py
Lines: 178-221
Matched Terms: user_id
Calls: AsyncMock, MagicMock, RegistrationCommand, RegistrationService, mock_user_repo.create.assert_called_once_with, service.register

test_session_introspection_includes_display_name
File: backend/app/stacks/identity_auth/tests/test_display_name.py
Lines: 225-253
Matched Terms: session
Calls: AsyncMock, MagicMock, get_session_introspection

test_refresh_session_schema_contract
File: backend/app/stacks/identity_auth/tests/test_identity_persistence_models.py
Lines: 39-59
Matched Terms: session, user_id
Calls: inspect

test_user_repository_normalizes_email
File: backend/app/stacks/identity_auth/tests/test_identity_repository.py
Lines: 17-50
Matched Terms: session
Calls: AsyncMock, IdentityUserRepository, Mock, isinstance, repository.create, session.add.assert_called_once_with, session.flush.assert_awaited_once

build_service
File: backend/app/stacks/identity_auth/tests/test_login_service.py
Lines: 45-109
Matched Terms: session
Calls: AsyncMock, LoginService, Mock, issued

active_user
File: backend/app/stacks/identity_auth/tests/test_login_service.py
Lines: 112-122
Matched Terms: owner
Calls: SimpleNamespace

test_valid_login_issues_separate_tokens_and_session
File: backend/app/stacks/identity_auth/tests/test_login_service.py
Lines: 126-200
Matched Terms: session, user_id, authorization
Calls: LoginCommand, active_user, build_service, commit.assert_awaited_once, created.values, hash_refresh_token.assert_called_once_with, refresh_repository.create.assert_awaited_once, rollback.assert_not_awaited, service.login, token_issuer.issue_access_token.assert_awaited_once_with, token_issuer.issue_refresh_token.assert_awaited_once_with, user_repository.get_by_email.assert_awaited_once_with, verify_password.assert_called_once_with

test_refresh_session_failure_rolls_back
File: backend/app/stacks/identity_auth/tests/test_login_service.py
Lines: 321-351
Matched Terms: session
Calls: LoginCommand, RuntimeError, active_user, build_service, commit.assert_not_awaited, pytest.raises, rollback.assert_awaited_once, service.login

test_valid_principal_is_returned
File: backend/app/stacks/identity_auth/tests/test_protected_principal_dependency.py
Lines: 38-64
Matched Terms: authorization
Calls: HTTPAuthorizationCredentials, SimpleNamespace, api_dependencies.require_authenticated_principal, monkeypatch.setattr

test_invalid_credentials_are_generic
File: backend/app/stacks/identity_auth/tests/test_protected_principal_dependency.py
Lines: 68-105
Matched Terms: authorization
Calls: HTTPAuthorizationCredentials, RuntimeError, api_dependencies.require_authenticated_principal, monkeypatch.setattr, pytest.raises

make_record
File: backend/app/stacks/identity_auth/tests/test_refresh_session_persistence.py
Lines: 18-50
Matched Terms: session, user_id
Calls: IdentityRefreshSession, datetime.now, timedelta

test_rotation_preserves_family_and_revokes_old
File: backend/app/stacks/identity_auth/tests/test_refresh_session_persistence.py
Lines: 54-99
Matched Terms: session
Calls: AsyncMock, Mock, RefreshSessionService, datetime.now, make_record, service._repository.revoke.assert_awaited_once, service.rotate, timedelta

test_reuse_revokes_entire_family
File: backend/app/stacks/identity_auth/tests/test_refresh_session_persistence.py
Lines: 103-142
Matched Terms: session
Calls: AsyncMock, Mock, RefreshSessionService, datetime.now, make_record, pytest.raises, service._repository.revoke_family.assert_awaited_once, service.rotate, timedelta

test_logout_is_idempotent
File: backend/app/stacks/identity_auth/tests/test_refresh_session_persistence.py
Lines: 146-163
Matched Terms: session
Calls: AsyncMock, Mock, RefreshSessionService, service._repository.revoke.assert_not_awaited, service.logout

test_successful_registration
File: backend/app/stacks/identity_auth/tests/test_registration.py
Lines: 15-51
Matched Terms: user_id
Calls: AsyncMock, MagicMock, RegistrationCommand, RegistrationService, service.register

test_complete_mock_registration_and_login_flow
File: backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py
Lines: 19-74
Matched Terms: session, user_id
Calls: LoginCommand, MockAuthenticationRuntime, RegistrationCommand, len, mock_hash_refresh_token, result.access_token.startswith, result.refresh_token.startswith, runtime.login.login, runtime.registration.register

test_unknown_and_wrong_password_share_error
File: backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py
Lines: 107-148
Matched Terms: session
Calls: LoginCommand, MockAuthenticationRuntime, RegistrationCommand, len, pytest.raises, runtime.login.login, runtime.registration.register, str

test_disabled_account_rejected_before_token_issuance
File: backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py
Lines: 152-184
Matched Terms: session
Calls: LoginCommand, MockAuthenticationRuntime, RegistrationCommand, len, pytest.raises, runtime.login.login, runtime.registration.register

test_access_token_failure_rolls_back
File: backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py
Lines: 188-216
Matched Terms: session
Calls: LoginCommand, MockAuthenticationRuntime, RegistrationCommand, len, pytest.raises, runtime.login.login, runtime.registration.register

test_refresh_token_failure_rolls_back
File: backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py
Lines: 220-248
Matched Terms: session
Calls: LoginCommand, MockAuthenticationRuntime, RegistrationCommand, len, pytest.raises, runtime.login.login, runtime.registration.register

test_refresh_session_failure_rolls_back
File: backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py
Lines: 252-280
Matched Terms: session
Calls: LoginCommand, MockAuthenticationRuntime, RegistrationCommand, len, pytest.raises, runtime.login.login, runtime.registration.register

test_registration_normalizes_and_hashes_password
File: backend/app/stacks/identity_auth/tests/test_registration_service.py
Lines: 70-116
Matched Terms: user_id
Calls: RegistrationCommand, build_service, commit.assert_awaited_once, hasattr, hash_password.assert_called_once_with, repository.create.assert_awaited_once_with, repository.get_by_email.assert_awaited_once_with, rollback.assert_not_awaited, service.register

test_runtime_construction_is_non_mutating
File: backend/app/stacks/identity_auth/tests/test_runtime_adapter.py
Lines: 67-93
Matched Terms: session
Calls: FakeSession, build_authentication_runtime, install_controlled_secret, isinstance, session.commit.assert_not_awaited, session.rollback.assert_not_awaited

test_runtime_fails_closed_without_secret
File: backend/app/stacks/identity_auth/tests/test_runtime_adapter.py
Lines: 96-109
Matched Terms: session
Calls: FakeSession, build_authentication_runtime, monkeypatch.delenv, pytest.raises

test_session_introspection_with_display_name
File: backend/app/stacks/identity_auth/tests/test_session_introspection.py
Lines: 9-37
Matched Terms: session, user_id
Calls: AsyncMock, MagicMock, get_session_introspection

test_session_introspection_without_display_name
File: backend/app/stacks/identity_auth/tests/test_session_introspection.py
Lines: 41-63
Matched Terms: session
Calls: AsyncMock, MagicMock, get_session_introspection

build_app
File: backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
Lines: 100-129
Matched Terms: session
Calls: FastAPI, app.include_router, app.middleware, app.middleware('http')

test_logout_revokes_current_refresh_session
File: backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
Lines: 187-211
Matched Terms: session
Calls: FakeLifecycleService, TestClient, build_app, client.post, response.json

test_refresh_rejection_is_unauthorized
File: backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
Lines: 214-244
Matched Terms: session
Calls: RejectingService, SessionLifecycleRejectedError, TestClient, build_app, client.post

test_logout_rejection_is_unauthorized
File: backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
Lines: 247-273
Matched Terms: session
Calls: RejectingService, SessionLifecycleRejectedError, TestClient, build_app, client.post

test_logout_all_uses_access_principal_subject
File: backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
Lines: 276-341
Matched Terms: session, user_id, authorization
Calls: FakeLifecycleService, SimpleNamespace, TestClient, app.on_event, build_app, client.post, engine.dispose, monkeypatch.setattr, response.json

test_logout_request_forbids_extra_fields
File: backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
Lines: 380-397
Matched Terms: user_id
Calls: FakeLifecycleService, TestClient, build_app, client.post

logout_all
File: backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
Lines: 88-97
Matched Terms: user_id
Calls: self.logout_all_users.append

load_identity_state
File: backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
Lines: 293-303
Matched Terms: user_id
Calls: NONE EXTRACTED

refresh
File: backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
Lines: 218-225
Matched Terms: session
Calls: SessionLifecycleRejectedError

logout
File: backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
Lines: 251-258
Matched Terms: session
Calls: SessionLifecycleRejectedError

active_user
File: backend/app/stacks/identity_auth/tests/test_stage4f_canonical_claim_propagation.py
Lines: 41-55
Matched Terms: owner
Calls: SimpleNamespace

test_login_issues_canonical_role_and_tier_claims
File: backend/app/stacks/identity_auth/tests/test_stage4f_canonical_claim_propagation.py
Lines: 59-116
Matched Terms: session, authorization
Calls: AsyncMock, LoginCommand, LoginService, Mock, active_user, issued, issuer.issue_access_token.assert_awaited_once_with, issuer.issue_refresh_token.assert_awaited_once_with, service.login

test_login_rejects_invalid_stored_role
File: backend/app/stacks/identity_auth/tests/test_stage4f_canonical_claim_propagation.py
Lines: 120-154
Matched Terms: session
Calls: AsyncMock, LoginCommand, LoginService, Mock, active_user, issuer.issue_access_token.assert_not_awaited, pytest.raises, service.login

test_refresh_uses_current_user_claims
File: backend/app/stacks/identity_auth/tests/test_stage4f_canonical_claim_propagation.py
Lines: 158-238
Matched Terms: session, current_user, user_id, authorization
Calls: AsyncMock, Mock, SessionLifecycleService, SimpleNamespace, ValidatedRefreshIdentity, active_user, issued, issuer.issue_access_token.assert_awaited_once_with, issuer.issue_refresh_token.assert_awaited_once_with, service.refresh, user_repository.get_by_id.assert_awaited_once_with

test_refresh_rejects_missing_current_user
File: backend/app/stacks/identity_auth/tests/test_stage4f_canonical_claim_propagation.py
Lines: 242-291
Matched Terms: session, current_user, user_id
Calls: AsyncMock, Mock, SessionLifecycleService, SimpleNamespace, ValidatedRefreshIdentity, issuer.issue_access_token.assert_not_awaited, issuer.issue_refresh_token.assert_not_awaited, pytest.raises, service.refresh

test_environment_access_issuer_forwards_claims
File: backend/app/stacks/identity_auth/tests/test_stage4f_environment_token_issuer_contract.py
Lines: 52-75
Matched Terms: owner, authorization
Calls: EnvironmentJwtTokenIssuer, issuer.issue_access_token, validate_access_token

test_environment_refresh_issuer_forwards_claims
File: backend/app/stacks/identity_auth/tests/test_stage4f_environment_token_issuer_contract.py
Lines: 79-102
Matched Terms: owner, authorization
Calls: EnvironmentJwtTokenIssuer, issuer.issue_refresh_token, validate_refresh_token

test_login_forwards_canonical_claims_to_both_tokens
File: backend/app/stacks/identity_auth/tests/test_stage4f_login_refresh_claims.py
Lines: 40-114
Matched Terms: session, owner, authorization
Calls: AsyncMock, LoginCommand, LoginService, Mock, SimpleNamespace, issued, service.login, token_issuer.issue_access_token.assert_awaited_once_with, token_issuer.issue_refresh_token.assert_awaited_once_with

test_mock_access_issuer_accepts_and_records_claims
File: backend/app/stacks/identity_auth/tests/test_stage4f_mock_identity_contract.py
Lines: 19-36
Matched Terms: authorization
Calls: MockServiceTokenIssuer, issuer.issue_access_token

test_mock_refresh_issuer_accepts_and_records_claims
File: backend/app/stacks/identity_auth/tests/test_stage4f_mock_identity_contract.py
Lines: 40-57
Matched Terms: authorization
Calls: MockServiceTokenIssuer, issuer.issue_refresh_token

test_mock_registration_result_remains_registration_contract
File: backend/app/stacks/identity_auth/tests/test_stage4f_mock_identity_contract.py
Lines: 84-106
Matched Terms: user_id
Calls: MockAuthenticationRuntime, RegistrationCommand, hasattr, runtime.registration.register

test_rotated_refresh_token_receives_canonical_claims
File: backend/app/stacks/identity_auth/tests/test_stage4f_rotated_refresh_claims.py
Lines: 36-123
Matched Terms: session, user_id, owner, authorization
Calls: AsyncMock, Mock, SessionLifecycleService, SimpleNamespace, ValidatedRefreshIdentity, issued, service.refresh, token_issuer.issue_access_token.assert_awaited_once_with, token_issuer.issue_refresh_token.assert_awaited_once_with

test_session_lifecycle_runtime_builds_user_repository
File: backend/app/stacks/identity_auth/tests/test_stage4f_session_lifecycle_runtime_wiring.py
Lines: 10-56
Matched Terms: session
Calls: Mock, build_session_lifecycle_runtime, patch, refresh_repository_type.assert_called_once_with, revocation_repository_type.assert_called_once_with, user_repository_type.assert_called_once_with

test_session_lifecycle_runtime_uses_one_shared_session
File: backend/app/stacks/identity_auth/tests/test_stage4f_session_lifecycle_runtime_wiring.py
Lines: 59-103
Matched Terms: session
Calls: Mock, build_session_lifecycle_runtime, patch

test_revocation_model_exposes_only_safe_fields
File: backend/app/stacks/identity_auth/tests/test_stage5b_a_durable_revocation_repository.py
Lines: 19-52
Matched Terms: user_id
Calls: NONE EXTRACTED

test_repository_rejects_invalid_identifiers
File: backend/app/stacks/identity_auth/tests/test_stage5b_a_durable_revocation_repository.py
Lines: 96-126
Matched Terms: session, user_id
Calls: AccessTokenRevocationRepository, SessionStub, datetime.now, pytest.mark.parametrize, pytest.raises, repository.revoke, timedelta

test_repository_rejects_invalid_lifetime
File: backend/app/stacks/identity_auth/tests/test_stage5b_a_durable_revocation_repository.py
Lines: 130-152
Matched Terms: session, user_id
Calls: AccessTokenRevocationRepository, SessionStub, datetime.now, pytest.raises, repository.revoke

test_logout_persists_access_and_refresh_revocation_before_commit
File: backend/app/stacks/identity_auth/tests/test_stage5b_b_durable_bearer_logout.py
Lines: 20-104
Matched Terms: session, user_id
Calls: AsyncMock, Mock, SessionLifecycleService, SimpleNamespace, ValidatedRefreshIdentity, access_repository.revoke.assert_awaited_once, datetime.now, events.append, rollback.assert_not_awaited, service.logout, timedelta

test_logout_rolls_back_both_revocations_on_failure
File: backend/app/stacks/identity_auth/tests/test_stage5b_b_durable_bearer_logout.py
Lines: 108-166
Matched Terms: session, user_id
Calls: AsyncMock, Mock, RuntimeError, SessionLifecycleService, SimpleNamespace, ValidatedRefreshIdentity, access_repository.revoke.assert_awaited_once, commit.assert_not_awaited, datetime.now, pytest.raises, rollback.assert_awaited_once, service.logout, timedelta

test_logout_rejects_access_refresh_subject_mismatch
File: backend/app/stacks/identity_auth/tests/test_stage5b_b_durable_bearer_logout.py
Lines: 170-224
Matched Terms: session, user_id
Calls: AsyncMock, Mock, SessionLifecycleService, SimpleNamespace, ValidatedRefreshIdentity, access_repository.revoke.assert_not_awaited, commit.assert_not_awaited, datetime.now, pytest.raises, refresh_service.logout.assert_not_awaited, rollback.assert_awaited_once, service.logout, timedelta

test_revocation_summary_exposes_no_jti
File: backend/app/stacks/identity_auth/tests/test_stage5b_c_revocation_observability_cleanup.py
Lines: 61-107
Matched Terms: user_id
Calls: AdministrativeReadService._revocation_summary, SimpleNamespace, datetime.now, datetime.now(UTC).replace, summary.model_dump, timedelta

test_cleanup_service_commits_success
File: backend/app/stacks/identity_auth/tests/test_stage5b_c_revocation_observability_cleanup.py
Lines: 111-134
Matched Terms: session
Calls: AccessTokenRevocationCleanupService, AsyncMock, Mock, service._repository.cleanup_expired.assert_awaited_once, service.cleanup_expired, session.commit.assert_awaited_once, session.rollback.assert_not_awaited

test_cleanup_service_rolls_back_failure
File: backend/app/stacks/identity_auth/tests/test_stage5b_c_revocation_observability_cleanup.py
Lines: 138-160
Matched Terms: session
Calls: AccessTokenRevocationCleanupService, AsyncMock, Mock, RuntimeError, pytest.raises, service.cleanup_expired, session.commit.assert_not_awaited, session.rollback.assert_awaited_once

test_identity_role_contract_is_canonical
File: backend/app/stacks/identity_auth/tests/test_stage9d_a_identity_schema.py
Lines: 33-42
Matched Terms: owner
Calls: normalize_identity_role

test_required_password_change_updates_hash_and_revokes_sessions
File: backend/app/stacks/identity_auth/tests/test_stage9d_b_forced_password_change.py
Lines: 116-168
Matched Terms: session, user_id
Calls: FakeRefreshRepository, FakeUser, FakeUserRepository, RequiredPasswordChangeService, hash_password, service.replace_required_password, verify_password

test_wrong_temporary_password_fails_closed
File: backend/app/stacks/identity_auth/tests/test_stage9d_b_forced_password_change.py
Lines: 172-213
Matched Terms: user_id
Calls: FakeRefreshRepository, FakeUser, FakeUserRepository, RequiredPasswordChangeService, hash_password, pytest.raises, service.replace_required_password

get_by_id
File: backend/app/stacks/identity_auth/tests/test_stage9d_b_forced_password_change.py
Lines: 37-45
Matched Terms: user_id
Calls: NONE EXTRACTED

revoke_all_for_user
File: backend/app/stacks/identity_auth/tests/test_stage9d_b_forced_password_change.py
Lines: 78-85
Matched Terms: user_id
Calls: NONE EXTRACTED

test_session_models_expose_no_secrets
File: backend/app/stacks/identity_auth/tests/test_stage9d_c2_admin_read_models.py
Lines: 55-67
Matched Terms: session
Calls: model_fields

test_admin_routes_are_get_only
File: backend/app/stacks/identity_auth/tests/test_stage9d_c2_admin_read_models.py
Lines: 70-137
Matched Terms: session, user_id
Calls: app.openapi, isinstance, method.lower, schema.get, set

test_openapi_contains_only_expected_admin_methods
File: backend/app/stacks/identity_auth/tests/test_stage9d_c2_admin_read_models.py
Lines: 171-214
Matched Terms: session, user_id
Calls: app.openapi, operation.lower

test_no_password_reset_route_added_in_c2
File: backend/app/stacks/identity_auth/tests/test_stage9d_c2_admin_read_models.py
Lines: 217-270
Matched Terms: user_id
Calls: any, app.openapi, isinstance, operation.lower, schema.get

test_admin_mutation_routes_are_exact
File: backend/app/stacks/identity_auth/tests/test_stage9d_c5_b_admin_user_mutations.py
Lines: 18-47
Matched Terms: user_id
Calls: isinstance, set

test_protected_roles_denied
File: backend/app/stacks/identity_auth/tests/test_stage9d_c5_b_admin_user_mutations.py
Lines: 71-91
Matched Terms: session
Calls: AdministrativeUserMutationService, SimpleNamespace, pytest.mark.parametrize, pytest.raises, service._assert_target_mutable

test_self_mutation_denied
File: backend/app/stacks/identity_auth/tests/test_stage9d_c5_b_admin_user_mutations.py
Lines: 94-112
Matched Terms: session
Calls: AdministrativeUserMutationService, SimpleNamespace, pytest.raises, service._assert_target_mutable

test_canonical_roles
File: backend/app/stacks/identity_auth/tests/test_stage9d_c5_i_authorization_policy.py
Lines: 16-24
Matched Terms: authorization
Calls: NONE EXTRACTED

test_owner_normalizes_to_developer
File: backend/app/stacks/identity_auth/tests/test_stage9d_c5_i_authorization_policy.py
Lines: 49-56
Matched Terms: owner, authorization
Calls: canonical_role_value, normalize_role

test_administrative_roles
File: backend/app/stacks/identity_auth/tests/test_stage9d_c5_i_authorization_policy.py
Lines: 59-66
Matched Terms: owner, authorization
Calls: is_administrative_role

test_dangerous_permissions_remain_separate
File: backend/app/stacks/identity_auth/tests/test_stage9d_c5_i_authorization_policy.py
Lines: 110-119
Matched Terms: owner
Calls: has_permission

test_authorization_decisions_fail_closed
File: backend/app/stacks/identity_auth/tests/test_stage9d_c5_i_authorization_policy.py
Lines: 122-150
Matched Terms: authorization
Calls: authorize, frozenset

test_role_and_tier_remain_separate
File: backend/app/stacks/identity_auth/tests/test_stage9d_c5_j1_subscription_tier.py
Lines: 71-81
Matched Terms: authorization
Calls: NONE EXTRACTED

test_no_tier_grants_broker_live
File: backend/app/stacks/identity_auth/tests/test_stage9d_c5_j1_subscription_tier.py
Lines: 84-100
Matched Terms: owner, authorization
Calls: has_permission

identity_user
File: backend/app/stacks/identity_auth/tests/test_stage9d_c5_k1_session_introspection.py
Lines: 32-50
Matched Terms: user_id
Calls: SimpleNamespace

test_canonical_router_contains_introspection_route
File: backend/app/stacks/identity_auth/tests/test_stage9d_c5_k1_session_introspection.py
Lines: 53-65
Matched Terms: session
Calls: isinstance, len

test_introspection_uses_principal_subject
File: backend/app/stacks/identity_auth/tests/test_stage9d_c5_k1_session_introspection.py
Lines: 87-106
Matched Terms: session, user_id
Calls: FakeIdentityUserRepository, SimpleNamespace, identity_user, session_introspection

test_missing_identity_fails_closed
File: backend/app/stacks/identity_auth/tests/test_stage9d_c5_k1_session_introspection.py
Lines: 110-119
Matched Terms: session
Calls: FakeIdentityUserRepository, get_session_introspection, pytest.raises

test_inactive_identity_fails_closed
File: backend/app/stacks/identity_auth/tests/test_stage9d_c5_k1_session_introspection.py
Lines: 123-136
Matched Terms: session
Calls: FakeIdentityUserRepository, get_session_introspection, identity_user, pytest.raises

test_disabled_identity_fails_closed
File: backend/app/stacks/identity_auth/tests/test_stage9d_c5_k1_session_introspection.py
Lines: 140-153
Matched Terms: session
Calls: FakeIdentityUserRepository, get_session_introspection, identity_user, pytest.raises

__init__
File: backend/app/stacks/identity_auth/tests/test_stage9d_c5_k1_session_introspection.py
Lines: 23-25
Matched Terms: user_id
Calls: NONE EXTRACTED

get_by_id
File: backend/app/stacks/identity_auth/tests/test_stage9d_c5_k1_session_introspection.py
Lines: 27-29
Matched Terms: user_id
Calls: NONE EXTRACTED

build_decision_audit_service
File: backend/app/stacks/journal_ledger/decision_audit_service.py
Lines: 141-154
Matched Terms: session
Calls: DecisionAuditService, DecisionEventRepository

__init__
File: backend/app/stacks/journal_ledger/decision_event_repository.py
Lines: 131-141
Matched Terms: session
Calls: TransactionManager, cast

session
File: backend/app/stacks/journal_ledger/decision_event_repository.py
Lines: 144-147
Matched Terms: session
Calls: NONE EXTRACTED

append
File: backend/app/stacks/journal_ledger/decision_event_repository.py
Lines: 149-298
Matched Terms: session
Calls: DecisionEventRecord, DecisionEventRepositoryError, PersistedDecisionEvent, TypeError, cast, datetime.now, dict, draft.content_hash, effective_recorded_at.astimezone, effective_recorded_at.utcoffset, isinstance, self._acquire_append_lock, self._ensure_unique, self._latest_record, self._transactions.execute, session.add, str

get_by_event_id
File: backend/app/stacks/journal_ledger/decision_event_repository.py
Lines: 300-327
Matched Terms: session
Calls: cast, result.scalar_one_or_none, select, select(DecisionEventRecord).where, self._session.execute, self._to_contract, str

get_by_idempotency_key
File: backend/app/stacks/journal_ledger/decision_event_repository.py
Lines: 329-361
Matched Terms: session
Calls: ValueError, cast, idempotency_key.strip, result.scalar_one_or_none, select, select(DecisionEventRecord).where, self._session.execute, self._to_contract

latest
File: backend/app/stacks/journal_ledger/decision_event_repository.py
Lines: 363-379
Matched Terms: session
Calls: cast, self._latest_record, self._to_contract

list_recent
File: backend/app/stacks/journal_ledger/decision_event_repository.py
Lines: 381-445
Matched Terms: session
Calls: DecisionEventRepositoryError, ValueError, all_method, callable, cast, desc, getattr, isinstance, result.scalars, select, select(DecisionEventRecord).order_by, select(DecisionEventRecord).order_by(desc(DecisionEventRecord.sequence_number)).limit, self._session.execute, self._to_contract, tuple

_acquire_append_lock
File: backend/app/stacks/journal_ledger/decision_event_repository.py
Lines: 447-497
Matched Terms: session
Calls: isinstance, self._session.get_bind, session.execute, text

_ensure_unique
File: backend/app/stacks/journal_ledger/decision_event_repository.py
Lines: 499-531
Matched Terms: session
Calls: DuplicateDecisionEventError, result.scalar_one_or_none, select, select(DecisionEventRecord).where, session.execute, str

_latest_record
File: backend/app/stacks/journal_ledger/decision_event_repository.py
Lines: 533-572
Matched Terms: session
Calls: cast, desc, result.scalar_one_or_none, select, select(DecisionEventRecord).order_by, select(DecisionEventRecord).order_by(desc(DecisionEventRecord.sequence_number)).limit, session.execute, statement.with_for_update

operation
File: backend/app/stacks/journal_ledger/decision_event_repository.py
Lines: 185-294
Matched Terms: session
Calls: DecisionEventRecord, PersistedDecisionEvent, cast, dict, draft.content_hash, self._acquire_append_lock, self._ensure_unique, self._latest_record, session.add, str

save_log
File: backend/app/stacks/journal_ledger/ledger.py
Lines: 57-177
Matched Terms: portfolio, position, session, user_id, owner
Calls: OrderHistory, PortfolioInventory, ValueError, async_session, emit_runtime_step, float, isinstance, max, print, raw_signal.get, res.scalar, select, select(PortfolioInventory).where, session.add, session.begin, session.execute, session.flush, signal_str.lower, str, str(user_id).strip, trade_result.get

_normalize_portfolio_read_user_id
File: backend/app/stacks/journal_ledger/ledger.py
Lines: 179-191
Matched Terms: portfolio, user_id
Calls: ValueError, str, str(user_id).strip

read_max_allocated_capital
File: backend/app/stacks/journal_ledger/ledger.py
Lines: 194-230
Matched Terms: portfolio, session, user_id
Calls: _normalize_portfolio_read_user_id, async_session, float, func.max, result.scalar_one_or_none, select, select(func.max(OrderHistory.allocated_capital)).where, session.execute

_validate_envelope
File: backend/app/stacks/journal_ledger/strategy_decision_audit_adapter.py
Lines: 300-388
Matched Terms: portfolio
Calls: ', '.join, TypeError, ValueError, envelope.get, isinstance, set, sorted, symbol.strip, symbol.strip().upper

make_draft
File: backend/app/stacks/journal_ledger/tests/test_decision_event_contract.py
Lines: 41-70
Matched Terms: position
Calls: DecisionEventDraft

test_first_append_allocates_sequence_one
File: backend/app/stacks/journal_ledger/tests/test_decision_event_repository.py
Lines: 211-272
Matched Terms: session
Calls: DecisionEventRepository, FakeResult, FakeSession, draft.content_hash, isinstance, len, make_draft, repository.append, str, timedelta

test_second_append_links_previous_hash
File: backend/app/stacks/journal_ledger/tests/test_decision_event_repository.py
Lines: 276-364
Matched Terms: session
Calls: DecisionEventRecord, DecisionEventRepository, FakeResult, FakeSession, UUID, isinstance, make_draft, repository.append, str, timedelta

test_duplicate_is_rejected_before_insert
File: backend/app/stacks/journal_ledger/tests/test_decision_event_repository.py
Lines: 368-430
Matched Terms: session
Calls: DecisionEventRecord, DecisionEventRepository, FakeResult, FakeSession, make_draft, pytest.raises, repository.append, str, timedelta

test_commit_failure_rolls_back
File: backend/app/stacks/journal_ledger/tests/test_decision_event_repository.py
Lines: 434-467
Matched Terms: session
Calls: DecisionEventRepository, FakeResult, FakeSession, make_draft, pytest.raises, repository.append, timedelta

test_append_rejects_naive_recorded_at
File: backend/app/stacks/journal_ledger/tests/test_decision_event_repository.py
Lines: 497-521
Matched Terms: session
Calls: DecisionEventRepository, FakeSession, datetime, make_draft, pytest.raises, repository.append

build_envelope
File: backend/app/stacks/journal_ledger/tests/test_strategy_decision_audit_adapter.py
Lines: 22-46
Matched Terms: portfolio
Calls: NONE EXTRACTED

test_produce_and_audit_delegates_to_service
File: backend/app/stacks/journal_ledger/tests/test_strategy_decision_audit_adapter.py
Lines: 50-204
Matched Terms: position
Calls: AsyncMock, StrategyDecisionAuditAdapter, adapter.produce_and_audit, build_envelope, datetime, isinstance, len, object, service.append.assert_awaited_once, uuid4

build_symbol_dataset_manifest
File: backend/app/stacks/learning_research/L3_service_facade/bulk_historical_data_downloader.py
Lines: 58-88
Matched Terms: read_only
Calls: asset_group.upper, datetime.now, datetime.now(UTC).isoformat, symbol.replace, symbol.replace('.', '_').replace, symbol.replace('.', '_').replace('^', '').replace, symbol.replace('.', '_').replace('^', '').replace('=', '_').replace

add_research
File: backend/app/stacks/learning_research/research_loader.py
Lines: 6-19
Matched Terms: session
Calls: ResearchData, async_session, session.add, session.commit, transaction_guard

market_data_status
File: backend/app/stacks/market_data/api_router.py
Lines: 103-165
Matched Terms: position, session, read_only
Calls: get_market_data_runtime, jsonable_encoder, router.get, runtime.cache.stats, runtime.registry.records, runtime.session.now

healthcheck
File: backend/app/stacks/market_data/market_session.py
Lines: 166-178
Matched Terms: session
Calls: MarketSessionService, MarketSessionService().now

state_at
File: backend/app/stacks/market_data/market_session.py
Lines: 67-73
Matched Terms: session
Calls: self.snapshot_at

snapshot_at
File: backend/app/stacks/market_data/market_session.py
Lines: 75-154
Matched Terms: session
Calls: MarketSessionSnapshot, ValueError, exchange_time.time, exchange_time.time().replace, exchange_time.weekday, normalized.astimezone, observed_at.astimezone

now
File: backend/app/stacks/market_data/market_session.py
Lines: 156-163
Matched Terms: session
Calls: datetime.now, self.snapshot_at

build_market_data_runtime
File: backend/app/stacks/market_data/runtime_composition.py
Lines: 54-95
Matched Terms: session
Calls: MarketDataCache[tuple[object, ...], object], MarketDataRuntime, MarketSessionService, ProviderRegistry, ProviderRouter, YFinanceProvider, registry.register

get_quote
File: backend/app/stacks/market_data/tests/test_provider_contract.py
Lines: 45-62
Matched Terms: session
Calls: MarketQuote, datetime.now

test_market_session_classification
File: backend/app/stacks/market_data/tests/test_provider_runtime.py
Lines: 365-373
Matched Terms: session
Calls: MarketSessionService, datetime, pytest.mark.parametrize, service.state_at

test_market_session_rejects_naive_datetime
File: backend/app/stacks/market_data/tests/test_provider_runtime.py
Lines: 376-385
Matched Terms: session
Calls: MarketSessionService, datetime.now, pytest.raises, service.state_at

test_read_only_routes_are_declared
File: backend/app/stacks/market_data/tests/test_runtime_composition.py
Lines: 152-171
Matched Terms: read_only
Calls: NONE EXTRACTED

test_status_endpoint_is_network_free
File: backend/app/stacks/market_data/tests/test_runtime_composition.py
Lines: 174-205
Matched Terms: read_only
Calls: FastAPI, TestClient, app.include_router, build_fixture_runtime, client.get, response.json, set_market_data_runtime_for_testing

build_runtime
File: backend/app/stacks/market_data/tests/test_stage8_runtime_qualification.py
Lines: 159-201
Matched Terms: session
Calls: MarketDataCache[tuple[object, ...], object], MarketDataRuntime, MarketSessionService, ProviderRegistry, ProviderRouter, enumerate, registry.register

test_status_endpoint_does_not_call_provider
File: backend/app/stacks/market_data/tests/test_stage8_runtime_qualification.py
Lines: 510-559
Matched Terms: read_only
Calls: ControlledProvider, FastAPI, TestClient, app.include_router, build_runtime, client.get, response.json, set_market_data_runtime_for_testing

test_mapping_quote_is_normalized
File: backend/app/stacks/market_data/tests/test_yfinance_provider.py
Lines: 109-137
Matched Terms: session
Calls: fixture_provider, provider.get_quote

load_full_history
File: backend/app/stacks/market_data/yfinance_ingestor.py
Lines: 12-35
Matched Terms: session
Calls: StockHistory, async_session, df.iterrows, idx.to_pydatetime, session.add, session.commit, ticker.history, transaction_guard, yf.Ticker

update_live_price
File: backend/app/stacks/market_data/yfinance_ingestor.py
Lines: 42-58
Matched Terms: session
Calls: StockLive, async_session, datetime.utcnow, session.commit, session.merge, transaction_guard, yf.Ticker

_load_default_quote_loader
File: backend/app/stacks/market_data/yfinance_provider.py
Lines: 76-201
Matched Terms: position
Calls: YFinanceDependencyError, YFinanceQuoteError, datetime.now, fast_info.get, float, history['Close'].dropna, len, ticker.history, ticker.info.get, yf.Ticker

_session_state
File: backend/app/stacks/market_data/yfinance_provider.py
Lines: 340-370
Matched Terms: session
Calls: aliases.get, isinstance, str, str(value or '').strip, str(value or '').strip().lower

_normalize_quote_payload
File: backend/app/stacks/market_data/yfinance_provider.py
Lines: 373-557
Matched Terms: session
Calls: MarketQuote, YFinanceNormalizationError, _aware_datetime, _finite_float, _first_present, _session_state, bool, datetime.now, float, isinstance, normalize_symbol, str, str(_first_present(payload, ('currency', 'currency_code'), default='USD')).strip, str(_first_present(payload, ('currency', 'currency_code'), default='USD')).strip().upper, str(_first_present(payload, ('provider', 'source'), default='yfinance')).strip, type

_normalize_portfolio_read_user_id
File: backend/app/stacks/portfolio/accounting.py
Lines: 7-19
Matched Terms: portfolio, user_id
Calls: ValueError, str, str(user_id).strip

calculate_live_portfolio_equity
File: backend/app/stacks/portfolio/accounting.py
Lines: 22-74
Matched Terms: portfolio, position, session, user_id
Calls: _normalize_portfolio_read_user_id, async_session, float, order.signal.lower, result.scalars, result.scalars().all, select, select(OrderHistory).where, session.execute, str

calculate_position_size
File: backend/app/stacks/portfolio/allocator.py
Lines: 4-40
Matched Terms: position
Calls: float, get_bars, max, min, str

health
File: backend/app/stacks/portfolio/base.py
Lines: 19-20
Matched Terms: portfolio
Calls: NONE EXTRACTED

__init__
File: backend/app/stacks/portfolio/facades/readonly_portfolio_facade.py
Lines: 80-165
Matched Terms: portfolio, position
Calls: MappingProxyType, ReadOnlyPortfolioFacadeError, ReadOnlySymbolPosition, object.__setattr__, position.symbol.upper, positions_by_symbol.items, positions_by_symbol.setdefault, positions_by_symbol.setdefault(symbol, []).append, self._validate_snapshot, sorted, tuple

_validate_snapshot
File: backend/app/stacks/portfolio/facades/readonly_portfolio_facade.py
Lines: 168-264
Matched Terms: portfolio, position, read_only
Calls: ReadOnlyPortfolioFacadeError, isinstance, len, sum

snapshot
File: backend/app/stacks/portfolio/facades/readonly_portfolio_facade.py
Lines: 267-270
Matched Terms: portfolio
Calls: NONE EXTRACTED

get_overview
File: backend/app/stacks/portfolio/facades/readonly_portfolio_facade.py
Lines: 272-310
Matched Terms: portfolio, position, read_only
Calls: ReadOnlyPortfolioOverview, tuple

list_accounts
File: backend/app/stacks/portfolio/facades/readonly_portfolio_facade.py
Lines: 312-387
Matched Terms: portfolio, position
Calls: ReadOnlyPortfolioAccountSummary, len, sorted, summaries.append, tuple

get_account
File: backend/app/stacks/portfolio/facades/readonly_portfolio_facade.py
Lines: 389-406
Matched Terms: portfolio
Calls: ReadOnlyPortfolioFacadeError, account_id_hash.strip, account_id_hash.strip().lower, self._accounts_by_hash.get

list_positions
File: backend/app/stacks/portfolio/facades/readonly_portfolio_facade.py
Lines: 408-429
Matched Terms: position
Calls: positions.extend, sorted, tuple

find_positions_by_symbol
File: backend/app/stacks/portfolio/facades/readonly_portfolio_facade.py
Lines: 431-450
Matched Terms: portfolio, position
Calls: ReadOnlyPortfolioFacadeError, self._positions_by_symbol.get, symbol.strip, symbol.strip().upper

get_totals
File: backend/app/stacks/portfolio/facades/readonly_portfolio_facade.py
Lines: 489-492
Matched Terms: portfolio
Calls: NONE EXTRACTED

get_symbol_index
File: backend/app/stacks/portfolio/facades/readonly_portfolio_facade.py
Lines: 494-502
Matched Terms: position
Calls: NONE EXTRACTED

_principal_subject
File: backend/app/stacks/portfolio/portfolio_service.py
Lines: 9-25
Matched Terms: portfolio
Calls: ValueError, getattr, str, str(getattr(principal, 'subject', '')).strip

get_portfolio_positions_for_api
File: backend/app/stacks/portfolio/portfolio_service.py
Lines: 28-46
Matched Terms: portfolio, position, user_id, owner
Calls: _principal_subject, get_positions_snapshot

owner_hash
File: backend/app/stacks/portfolio/portfolio_snapshot_lifecycle.py
Lines: 59-75
Matched Terms: portfolio, user_id, owner
Calls: AuthenticatedPortfolioAccessDenied, hashlib.sha256, hashlib.sha256(normalized.encode('utf-8')).hexdigest, normalized.encode, str, str(neurovest_user_id).strip

owner_refresh_lock
File: backend/app/stacks/portfolio/portfolio_snapshot_lifecycle.py
Lines: 221-257
Matched Terms: portfolio, owner
Calls: PortfolioRefreshInProgress, fcntl.flock, lock_file.fileno, lock_path.open, owner_directory.mkdir

_owner_directory
File: backend/app/stacks/portfolio/portfolio_snapshot_lifecycle.py
Lines: 260-269
Matched Terms: user_id, owner
Calls: owner_hash

_metadata_path
File: backend/app/stacks/portfolio/portfolio_snapshot_lifecycle.py
Lines: 272-278
Matched Terms: owner
Calls: NONE EXTRACTED

_active_path
File: backend/app/stacks/portfolio/portfolio_snapshot_lifecycle.py
Lines: 281-287
Matched Terms: owner
Calls: NONE EXTRACTED

_history_directory
File: backend/app/stacks/portfolio/portfolio_snapshot_lifecycle.py
Lines: 290-296
Matched Terms: owner
Calls: NONE EXTRACTED

get_portfolio_lifecycle
File: backend/app/stacks/portfolio/portfolio_snapshot_lifecycle.py
Lines: 369-544
Matched Terms: portfolio, user_id, owner, read_only
Calls: _active_path, _freshness, _history_directory, _metadata_path, _owner_directory, _read_json, active_path.is_file, datetime.fromisoformat, history_directory.glob, history_directory.is_dir, int, isinstance, len, list, metadata.get, promoted_at.astimezone, promoted_at.replace, sha256_file, stale_after.total_seconds, utc_now

refresh_portfolio_snapshot
File: backend/app/stacks/portfolio/portfolio_snapshot_lifecycle.py
Lines: 574-879
Matched Terms: portfolio, user_id, owner, read_only
Calls: Path, PortfolioSnapshotLifecycleError, _active_path, _history_directory, _metadata_path, _owner_directory, _read_json, _retain_history, active_path.is_file, active_path.read_text, asdict, atomic_write_json, build_owned_snapshot, candidate['snapshot'].get, current_time.isoformat, current_time.strftime, failed_metadata.get, failed_metadata.update, find_latest_normalized_portfolio, get_portfolio_lifecycle, hashlib.sha256, hashlib.sha256(str(qualified_source).encode('utf-8')).hexdigest, int, json.loads, max, metadata.update, owner_hash, owner_refresh_lock, qualified_source.is_file, refreshed_metadata.get, refreshed_metadata.update, sha256_file, str, str(qualified_source).encode, type, utc_now

load_active_owner_snapshot
File: backend/app/stacks/portfolio/portfolio_snapshot_lifecycle.py
Lines: 882-905
Matched Terms: portfolio, user_id, owner
Calls: PortfolioSnapshotLifecycleError, _active_path, _owner_directory, _read_json

rebalance_portfolio
File: backend/app/stacks/portfolio/rebalance.py
Lines: 3-12
Matched Terms: portfolio
Calls: isinstance, signal.get, signal.get('signal', {}).get

_normalize_reconciliation_user_id
File: backend/app/stacks/portfolio/reconciliation.py
Lines: 14-26
Matched Terms: user_id, owner
Calls: ValueError, str, str(user_id).strip

resolve_reconciliation_owner_id
File: backend/app/stacks/portfolio/reconciliation.py
Lines: 29-91
Matched Terms: portfolio, session, user_id, owner
Calls: OrderHistory.user_id.is_not, PortfolioInventory.user_id.is_not, async_session, inventory_result.scalars, inventory_result.scalars().all, iter, len, next, order_result.scalars, order_result.scalars().all, select, select(OrderHistory.user_id).where, select(OrderHistory.user_id).where(OrderHistory.user_id.is_not(None)).distinct, select(PortfolioInventory.user_id).where, select(PortfolioInventory.user_id).where(PortfolioInventory.user_id.is_not(None)).distinct, session.execute, str, str(owner_id).strip

run_reconciliation_audit
File: backend/app/stacks/portfolio/reconciliation.py
Lines: 94-331
Matched Terms: portfolio, position, session, user_id, owner
Calls: _normalize_reconciliation_user_id, abs, async_session, audit_results['details'].append, emit_runtime_step, float, inventory_result.scalars, inventory_result.scalars().all, max, order_result.scalars, order_result.scalars().all, select, select(OrderHistory).where, select(PortfolioInventory).where, session.begin, session.execute, session.flush, str, str(order.signal).lower

start_periodic_reconciliation_daemon
File: backend/app/stacks/portfolio/reconciliation.py
Lines: 334-364
Matched Terms: portfolio, user_id, owner
Calls: _normalize_reconciliation_user_id, asyncio.sleep, print, run_reconciliation_audit

latest_snapshot
File: backend/app/stacks/portfolio/tests/test_authenticated_owned_readonly_portfolio_api.py
Lines: 20-39
Matched Terms: portfolio
Calls: Path, Path('runtime/snaptrade_integration').glob, path.stat, pytest.skip, sorted

configured_owner
File: backend/app/stacks/portfolio/tests/test_authenticated_owned_readonly_portfolio_api.py
Lines: 42-68
Matched Terms: portfolio, owner
Calls: Path, Path('runtime/dev_auth/snaptrade_portfolio_owner_bindings.json').read_text, iter, json.loads, len, next, pytest.skip, registry.get

test_configured_owner_receives_two_accounts
File: backend/app/stacks/portfolio/tests/test_authenticated_owned_readonly_portfolio_api.py
Lines: 71-107
Matched Terms: position, user_id, owner, read_only
Calls: build_owned_facade, configured_owner, latest_snapshot, serialize_overview

test_unbound_user_is_denied
File: backend/app/stacks/portfolio/tests/test_authenticated_owned_readonly_portfolio_api.py
Lines: 110-119
Matched Terms: portfolio, user_id
Calls: build_owned_facade, latest_snapshot, pytest.raises

test_empty_principal_subject_is_denied
File: backend/app/stacks/portfolio/tests/test_authenticated_owned_readonly_portfolio_api.py
Lines: 122-129
Matched Terms: portfolio, user_id
Calls: build_owned_facade, latest_snapshot, pytest.raises

test_owner_receives_only_bound_account_hashes
File: backend/app/stacks/portfolio/tests/test_authenticated_owned_readonly_portfolio_api.py
Lines: 132-164
Matched Terms: portfolio, user_id, owner
Calls: Path, Path('runtime/dev_auth/snaptrade_portfolio_owner_bindings.json').read_text, build_owned_facade, configured_owner, json.loads, latest_snapshot, serialize_accounts, set

test_read_views_are_normalized
File: backend/app/stacks/portfolio/tests/test_authenticated_owned_readonly_portfolio_api.py
Lines: 167-213
Matched Terms: position, user_id, owner
Calls: all, build_owned_facade, configured_owner, isinstance, latest_snapshot, len, serialize_accounts, serialize_balances, serialize_positions, serialize_totals

test_symbol_lookup_is_owner_scoped
File: backend/app/stacks/portfolio/tests/test_authenticated_owned_readonly_portfolio_api.py
Lines: 216-236
Matched Terms: position, user_id, owner
Calls: all, build_owned_facade, configured_owner, latest_snapshot, serialize_symbol_positions

test_no_raw_account_identifier_fields_are_returned
File: backend/app/stacks/portfolio/tests/test_authenticated_owned_readonly_portfolio_api.py
Lines: 239-273
Matched Terms: position, user_id, owner
Calls: build_owned_facade, configured_owner, json.dumps, json.dumps({'accounts': serialize_accounts(facade), 'balances': serialize_balances(facade), 'positions': serialize_positions(facade)}).lower, latest_snapshot, serialize_accounts, serialize_balances, serialize_positions

test_service_records_no_network_or_database_activity
File: backend/app/stacks/portfolio/tests/test_authenticated_owned_readonly_portfolio_api.py
Lines: 276-287
Matched Terms: user_id, owner
Calls: build_owned_facade, configured_owner, latest_snapshot

test_paper_order_propagates_authenticated_owner
File: backend/app/stacks/portfolio/tests/test_authenticated_paper_order_api.py
Lines: 92-151
Matched Terms: portfolio, user_id, owner
Calls: AsyncMock, SimpleNamespace, main.PaperOrderRequest, main.submit_authenticated_paper_order, monkeypatch.setattr, processor.assert_awaited_once_with

test_two_orders_keep_owners_separate
File: backend/app/stacks/portfolio/tests/test_authenticated_paper_order_api.py
Lines: 155-227
Matched Terms: portfolio, user_id, owner
Calls: AsyncMock, SimpleNamespace, main.PaperOrderRequest, main.submit_authenticated_paper_order, monkeypatch.setattr

make_principal
File: backend/app/stacks/portfolio/tests/test_authenticated_portfolio_read_boundary.py
Lines: 15-25
Matched Terms: portfolio
Calls: AuthenticatedPrincipal

test_portfolio_service_passes_principal_subject
File: backend/app/stacks/portfolio/tests/test_authenticated_portfolio_read_boundary.py
Lines: 29-71
Matched Terms: portfolio, position, user_id
Calls: make_principal, monkeypatch.setattr, portfolio_service.get_portfolio_positions_for_api

test_portfolio_service_rejects_empty_subject
File: backend/app/stacks/portfolio/tests/test_authenticated_portfolio_read_boundary.py
Lines: 75-91
Matched Terms: portfolio, position
Calls: AuthenticatedPrincipal, portfolio_service.get_portfolio_positions_for_api, pytest.raises

test_paper_snapshot_rejects_empty_user_id
File: backend/app/stacks/portfolio/tests/test_authenticated_portfolio_read_boundary.py
Lines: 95-106
Matched Terms: position, user_id
Calls: get_positions_snapshot, pytest.raises

test_paper_snapshot_is_explicitly_account_scoped
File: backend/app/stacks/portfolio/tests/test_authenticated_portfolio_read_boundary.py
Lines: 110-125
Matched Terms: position, user_id
Calls: get_positions_snapshot

fake_snapshot
File: backend/app/stacks/portfolio/tests/test_authenticated_portfolio_read_boundary.py
Lines: 34-46
Matched Terms: position, user_id
Calls: NONE EXTRACTED

test_accounting_rejects_empty_owner
File: backend/app/stacks/portfolio/tests/test_authenticated_portfolio_read_isolation.py
Lines: 74-81
Matched Terms: portfolio, user_id, owner
Calls: calculate_live_portfolio_equity, pytest.raises

test_ledger_read_rejects_empty_owner
File: backend/app/stacks/portfolio/tests/test_authenticated_portfolio_read_isolation.py
Lines: 85-92
Matched Terms: user_id, owner
Calls: pytest.raises, read_max_allocated_capital

test_position_route_is_authenticated_and_scoped
File: backend/app/stacks/portfolio/tests/test_authenticated_portfolio_read_isolation.py
Lines: 95-109
Matched Terms: portfolio, position, user_id
Calls: function_source

test_orders_route_is_authenticated_and_scoped
File: backend/app/stacks/portfolio/tests/test_authenticated_portfolio_read_isolation.py
Lines: 112-126
Matched Terms: user_id
Calls: function_source

test_analytics_route_is_authenticated_and_scoped
File: backend/app/stacks/portfolio/tests/test_authenticated_portfolio_read_isolation.py
Lines: 129-143
Matched Terms: analytics, user_id
Calls: function_source

test_accounting_is_owner_scoped
File: backend/app/stacks/portfolio/tests/test_authenticated_portfolio_read_isolation.py
Lines: 146-155
Matched Terms: portfolio, user_id, owner
Calls: function_source

test_max_allocation_is_owner_scoped
File: backend/app/stacks/portfolio/tests/test_authenticated_portfolio_read_isolation.py
Lines: 158-167
Matched Terms: user_id, owner
Calls: function_source

test_risk_propagates_owner
File: backend/app/stacks/portfolio/tests/test_authenticated_portfolio_read_isolation.py
Lines: 170-179
Matched Terms: user_id, owner
Calls: function_source

test_execution_propagates_owner
File: backend/app/stacks/portfolio/tests/test_authenticated_portfolio_read_isolation.py
Lines: 182-196
Matched Terms: portfolio, user_id, owner
Calls: function_source

test_portfolio_valuation_policy_is_authenticated
File: backend/app/stacks/portfolio/tests/test_authenticated_portfolio_valuation_api.py
Lines: 15-22
Matched Terms: portfolio
Calls: resolve_route_policy

test_portfolio_valuation_route_is_registered
File: backend/app/stacks/portfolio/tests/test_authenticated_portfolio_valuation_api.py
Lines: 25-45
Matched Terms: portfolio
Calls: getattr, len, set

test_portfolio_valuation_propagates_owner
File: backend/app/stacks/portfolio/tests/test_authenticated_portfolio_valuation_api.py
Lines: 49-84
Matched Terms: portfolio, user_id, owner
Calls: AsyncMock, SimpleNamespace, accounting.assert_awaited_once_with, main.get_authenticated_portfolio_valuation, monkeypatch.setattr

test_portfolio_valuation_keeps_owners_separate
File: backend/app/stacks/portfolio/tests/test_authenticated_portfolio_valuation_api.py
Lines: 88-137
Matched Terms: portfolio, user_id, owner
Calls: AsyncMock, SimpleNamespace, main.get_authenticated_portfolio_valuation, monkeypatch.setattr

test_paper_execution_rejects_empty_user_id
File: backend/app/stacks/portfolio/tests/test_execution_ownership_propagation.py
Lines: 17-29
Matched Terms: portfolio, user_id
Calls: paper_broker.process_portfolio_output, pytest.raises

test_ledger_rejects_empty_user_id
File: backend/app/stacks/portfolio/tests/test_execution_ownership_propagation.py
Lines: 33-45
Matched Terms: user_id
Calls: ledger.save_log, pytest.raises

test_all_paper_broker_save_log_calls_propagate_user_id
File: backend/app/stacks/portfolio/tests/test_execution_ownership_propagation.py
Lines: 48-79
Matched Terms: user_id
Calls: Path, ast.parse, ast.walk, calls.append, isinstance, path.read_text

test_ledger_inventory_lookup_is_account_scoped
File: backend/app/stacks/portfolio/tests/test_execution_ownership_propagation.py
Lines: 82-102
Matched Terms: portfolio, user_id
Calls: Path, Path('backend/app/stacks/journal_ledger/ledger.py').read_text

test_order_history_write_is_account_scoped
File: backend/app/stacks/portfolio/tests/test_execution_ownership_propagation.py
Lines: 105-129
Matched Terms: session, user_id
Calls: Path, Path('backend/app/stacks/journal_ledger/ledger.py').read_text, text.index

test_ambiguous_owner_resolution_returns_none
File: backend/app/stacks/portfolio/tests/test_multi_owner_reconciliation_startup.py
Lines: 66-85
Matched Terms: session, owner
Calls: FakeSession, monkeypatch.setattr, reconciliation.resolve_reconciliation_owner_id

test_single_owner_resolution_returns_owner
File: backend/app/stacks/portfolio/tests/test_multi_owner_reconciliation_startup.py
Lines: 89-108
Matched Terms: session, owner
Calls: FakeSession, monkeypatch.setattr, reconciliation.resolve_reconciliation_owner_id

test_empty_owner_resolution_returns_none
File: backend/app/stacks/portfolio/tests/test_multi_owner_reconciliation_startup.py
Lines: 112-130
Matched Terms: session, owner
Calls: FakeSession, monkeypatch.setattr, reconciliation.resolve_reconciliation_owner_id

test_lifespan_guards_legacy_reconciliation_daemon
File: backend/app/stacks/portfolio/tests/test_multi_owner_reconciliation_startup.py
Lines: 133-151
Matched Terms: user_id, owner
Calls: inspect.getsource

test_lifespan_does_not_inline_owner_resolution
File: backend/app/stacks/portfolio/tests/test_multi_owner_reconciliation_startup.py
Lines: 154-162
Matched Terms: user_id, owner
Calls: inspect.getsource

__aenter__
File: backend/app/stacks/portfolio/tests/test_multi_owner_reconciliation_startup.py
Lines: 37-40
Matched Terms: session
Calls: NONE EXTRACTED

test_orm_enforces_owned_rows
File: backend/app/stacks/portfolio/tests/test_ownership_schema_enforcement.py
Lines: 19-71
Matched Terms: portfolio, user_id
Calls: LEDGER.read_text, ast.parse, ast.unparse, ast.walk, isinstance

test_live_database_enforces_owned_rows
File: backend/app/stacks/portfolio/tests/test_ownership_schema_enforcement.py
Lines: 75-133
Matched Terms: portfolio, user_id, owner
Calls: connection.run_sync, engine.connect, inspect, inspector.get_columns, inspector.get_unique_constraints, next

inspect_schema
File: backend/app/stacks/portfolio/tests/test_ownership_schema_enforcement.py
Lines: 77-91
Matched Terms: portfolio
Calls: inspect, inspector.get_columns, inspector.get_unique_constraints

configured_owner
File: backend/app/stacks/portfolio/tests/test_portfolio_snapshot_lifecycle.py
Lines: 27-50
Matched Terms: owner
Calls: OWNER_REGISTRY.read_text, document.get, iter, json.loads, len, next, pytest.skip

latest_qualified_snapshot
File: backend/app/stacks/portfolio/tests/test_portfolio_snapshot_lifecycle.py
Lines: 53-72
Matched Terms: portfolio
Calls: Path, Path('runtime/snaptrade_integration').glob, path.stat, pytest.skip, sorted

test_refresh_promotes_owner_scoped_snapshot_atomically
File: backend/app/stacks/portfolio/tests/test_portfolio_snapshot_lifecycle.py
Lines: 75-133
Matched Terms: portfolio, user_id, owner, read_only
Calls: configured_owner, latest_qualified_snapshot, load_active_owner_snapshot, refresh_portfolio_snapshot

test_second_refresh_preserves_last_known_good
File: backend/app/stacks/portfolio/tests/test_portfolio_snapshot_lifecycle.py
Lines: 136-174
Matched Terms: portfolio, user_id, owner
Calls: (owner_directories[0] / 'history').glob, configured_owner, latest_qualified_snapshot, len, list, path.is_dir, refresh_portfolio_snapshot, tmp_path.iterdir

test_failed_refresh_keeps_active_snapshot
File: backend/app/stacks/portfolio/tests/test_portfolio_snapshot_lifecycle.py
Lines: 177-227
Matched Terms: portfolio, user_id, owner
Calls: configured_owner, get_portfolio_lifecycle, latest_qualified_snapshot, load_active_owner_snapshot, pytest.raises, refresh_portfolio_snapshot

test_staleness_is_reported
File: backend/app/stacks/portfolio/tests/test_portfolio_snapshot_lifecycle.py
Lines: 230-271
Matched Terms: portfolio, user_id, owner
Calls: configured_owner, datetime, get_portfolio_lifecycle, latest_qualified_snapshot, refresh_portfolio_snapshot, timedelta

test_retention_is_bounded
File: backend/app/stacks/portfolio/tests/test_portfolio_snapshot_lifecycle.py
Lines: 274-310
Matched Terms: portfolio, user_id, owner
Calls: configured_owner, datetime, get_portfolio_lifecycle, latest_qualified_snapshot, range, refresh_portfolio_snapshot, timedelta

test_unbound_user_refresh_is_denied
File: backend/app/stacks/portfolio/tests/test_portfolio_snapshot_lifecycle.py
Lines: 313-325
Matched Terms: portfolio, user_id
Calls: latest_qualified_snapshot, pytest.raises, refresh_portfolio_snapshot

test_lifecycle_contains_no_raw_owner_id
File: backend/app/stacks/portfolio/tests/test_portfolio_snapshot_lifecycle.py
Lines: 328-346
Matched Terms: portfolio, user_id, owner
Calls: configured_owner, get_portfolio_lifecycle, json.dumps, latest_qualified_snapshot, refresh_portfolio_snapshot

qualified_snapshot_path
File: backend/app/stacks/portfolio/tests/test_readonly_portfolio_facade.py
Lines: 18-37
Matched Terms: portfolio
Calls: Path, Path('runtime/snaptrade_integration').glob, path.stat, pytest.skip, sorted

build_facade
File: backend/app/stacks/portfolio/tests/test_readonly_portfolio_facade.py
Lines: 40-47
Matched Terms: portfolio
Calls: ReadOnlyPortfolioFacade, ingest_normalized_portfolio, qualified_snapshot_path

test_facade_overview
File: backend/app/stacks/portfolio/tests/test_readonly_portfolio_facade.py
Lines: 50-71
Matched Terms: position, read_only
Calls: build_facade, build_facade().get_overview, set

test_lists_account_summaries
File: backend/app/stacks/portfolio/tests/test_readonly_portfolio_facade.py
Lines: 74-100
Matched Terms: position
Calls: all, build_facade, facade.list_accounts, len, sum

test_get_account_by_hash
File: backend/app/stacks/portfolio/tests/test_readonly_portfolio_facade.py
Lines: 103-118
Matched Terms: read_only
Calls: build_facade, facade.get_account, facade.list_accounts

test_unknown_account_is_rejected
File: backend/app/stacks/portfolio/tests/test_readonly_portfolio_facade.py
Lines: 121-129
Matched Terms: portfolio
Calls: build_facade, facade.get_account, pytest.raises

test_lists_all_positions
File: backend/app/stacks/portfolio/tests/test_readonly_portfolio_facade.py
Lines: 132-154
Matched Terms: position, read_only
Calls: all, build_facade, build_facade().list_positions, len

test_symbol_lookup_is_normalized
File: backend/app/stacks/portfolio/tests/test_readonly_portfolio_facade.py
Lines: 165-180
Matched Terms: position
Calls: all, build_facade, build_facade().find_positions_by_symbol, pytest.mark.parametrize

test_unknown_symbol_returns_empty_tuple
File: backend/app/stacks/portfolio/tests/test_readonly_portfolio_facade.py
Lines: 183-191
Matched Terms: position
Calls: build_facade, build_facade().find_positions_by_symbol

test_empty_symbol_is_rejected
File: backend/app/stacks/portfolio/tests/test_readonly_portfolio_facade.py
Lines: 194-203
Matched Terms: portfolio, position
Calls: build_facade, build_facade().find_positions_by_symbol, pytest.raises

test_account_summary_is_immutable
File: backend/app/stacks/portfolio/tests/test_readonly_portfolio_facade.py
Lines: 238-244
Matched Terms: position
Calls: build_facade, build_facade().list_accounts, pytest.raises

test_symbol_result_is_immutable
File: backend/app/stacks/portfolio/tests/test_readonly_portfolio_facade.py
Lines: 247-258
Matched Terms: position
Calls: build_facade, build_facade().find_positions_by_symbol, pytest.raises

test_facade_has_no_mutation_methods
File: backend/app/stacks/portfolio/tests/test_readonly_portfolio_facade.py
Lines: 270-300
Matched Terms: portfolio
Calls: dir, name.lower, name.startswith, set

test_facade_source_has_no_provider_import
File: backend/app/stacks/portfolio/tests/test_readonly_portfolio_facade.py
Lines: 303-378
Matched Terms: portfolio
Calls: Path, ast.parse, ast.walk, imported_module.split, imported_module.startswith, isinstance, source_path.read_text, str, violations.append

test_reconciliation_rejects_empty_owner
File: backend/app/stacks/portfolio/tests/test_reconciliation_ownership_isolation.py
Lines: 87-94
Matched Terms: user_id, owner
Calls: pytest.raises, run_reconciliation_audit

test_daemon_rejects_empty_owner_before_loop
File: backend/app/stacks/portfolio/tests/test_reconciliation_ownership_isolation.py
Lines: 98-106
Matched Terms: user_id, owner
Calls: pytest.raises, start_periodic_reconciliation_daemon

test_reconciliation_inventory_query_is_owner_scoped
File: backend/app/stacks/portfolio/tests/test_reconciliation_ownership_isolation.py
Lines: 109-133
Matched Terms: portfolio, user_id, owner
Calls: RECONCILIATION_PATH.read_text, _function, ast.parse, ast.unparse

test_reconciliation_order_query_is_owner_and_symbol_scoped
File: backend/app/stacks/portfolio/tests/test_reconciliation_ownership_isolation.py
Lines: 136-165
Matched Terms: position, user_id, owner
Calls: RECONCILIATION_PATH.read_text, _function, ast.parse, ast.unparse

test_daemon_propagates_owner_to_each_audit
File: backend/app/stacks/portfolio/tests/test_reconciliation_ownership_isolation.py
Lines: 168-199
Matched Terms: user_id, owner
Calls: RECONCILIATION_PATH.read_text, _calls, _function, ast.parse, ast.unparse, keywords.get, len

test_main_propagates_owner_to_both_runtime_callers
File: backend/app/stacks/portfolio/tests/test_reconciliation_ownership_isolation.py
Lines: 202-283
Matched Terms: user_id, owner
Calls: MAIN_PATH.read_text, _calls, ast.parse, ast.unparse, audit_keywords.get, daemon_keywords.get, len

test_risk_imports_no_ledger_internals
File: backend/app/stacks/risk/tests/test_drawdown_guard_ledger_boundary.py
Lines: 126-133
Matched Terms: session
Calls: RISK_FILE.read_text

test_healthcheck_preserves_none_contract
File: backend/app/stacks/risk/tests/test_drawdown_guard_ledger_boundary.py
Lines: 161-182
Matched Terms: user_id, owner
Calls: drawdown_guard.healthcheck, monkeypatch.setattr

test_healthcheck_uses_scalar_facade
File: backend/app/stacks/risk/tests/test_drawdown_guard_ledger_boundary.py
Lines: 186-222
Matched Terms: user_id, owner
Calls: drawdown_guard.healthcheck, monkeypatch.setattr, pytest.approx

test_ledger_owns_read_query
File: backend/app/stacks/risk/tests/test_drawdown_guard_ledger_boundary.py
Lines: 225-237
Matched Terms: session
Calls: LEDGER_FILE.read_text

test_read_facade_exposes_no_session_or_model
File: backend/app/stacks/risk/tests/test_drawdown_guard_ledger_boundary.py
Lines: 240-268
Matched Terms: session
Calls: LEDGER_FILE.read_text, ast.parse, ast.unparse, ast.walk, isinstance, len, str

fake_read
File: backend/app/stacks/risk/tests/test_drawdown_guard_ledger_boundary.py
Lines: 164-169
Matched Terms: user_id, owner
Calls: NONE EXTRACTED

fake_read
File: backend/app/stacks/risk/tests/test_drawdown_guard_ledger_boundary.py
Lines: 191-200
Matched Terms: user_id, owner
Calls: NONE EXTRACTED

_require_mapping
File: backend/app/stacks/snaptrade/application/normalized_portfolio_ingestion.py
Lines: 28-41
Matched Terms: portfolio
Calls: ReadOnlyPortfolioIngestionError, isinstance

_require_list
File: backend/app/stacks/snaptrade/application/normalized_portfolio_ingestion.py
Lines: 44-57
Matched Terms: portfolio
Calls: ReadOnlyPortfolioIngestionError, isinstance

_decimal_or_none
File: backend/app/stacks/snaptrade/application/normalized_portfolio_ingestion.py
Lines: 60-95
Matched Terms: portfolio
Calls: Decimal, ReadOnlyPortfolioIngestionError, isinstance, result.is_finite, str

_require_sha256
File: backend/app/stacks/snaptrade/application/normalized_portfolio_ingestion.py
Lines: 98-123
Matched Terms: portfolio
Calls: ReadOnlyPortfolioIngestionError, int, isinstance, len

_optional_text
File: backend/app/stacks/snaptrade/application/normalized_portfolio_ingestion.py
Lines: 126-142
Matched Terms: portfolio
Calls: ReadOnlyPortfolioIngestionError, isinstance, value.strip

_require_text
File: backend/app/stacks/snaptrade/application/normalized_portfolio_ingestion.py
Lines: 145-159
Matched Terms: portfolio
Calls: ReadOnlyPortfolioIngestionError, _optional_text

_validate_locked_boundary
File: backend/app/stacks/snaptrade/application/normalized_portfolio_ingestion.py
Lines: 162-219
Matched Terms: portfolio, read_only
Calls: ReadOnlyPortfolioIngestionError, document.get

_parse_position
File: backend/app/stacks/snaptrade/application/normalized_portfolio_ingestion.py
Lines: 285-416
Matched Terms: portfolio, position, read_only
Calls: ReadOnlyPortfolioIngestionError, ReadOnlyPosition, _decimal_or_none, _optional_text, _require_mapping, _require_sha256, _require_text, _require_text(item.get('symbol'), label='position symbol').upper, item.get

_parse_account
File: backend/app/stacks/snaptrade/application/normalized_portfolio_ingestion.py
Lines: 419-565
Matched Terms: portfolio, position, read_only
Calls: ReadOnlyPortfolioAccount, ReadOnlyPortfolioIngestionError, _decimal_or_none, _optional_text, _parse_balance, _parse_position, _require_list, _require_mapping, _require_sha256, _require_text, bool, enumerate, item.get, len, tuple

ingest_normalized_portfolio
File: backend/app/stacks/snaptrade/application/normalized_portfolio_ingestion.py
Lines: 568-817
Matched Terms: portfolio, position, read_only
Calls: Path, ReadOnlyPortfolioIngestionError, ReadOnlyPortfolioSnapshot, ReadOnlyPortfolioTotals, _decimal_or_none, _parse_account, _require_list, _require_mapping, _require_sha256, _require_text, _validate_locked_boundary, bool, calculated_fields_raw.items, document.get, enumerate, int, json.loads, len, path.read_text, seen_accounts.add, set, source_evidence_raw.items, str, sum, totals_raw.get, tuple

_normalize_user_id
File: backend/app/stacks/snaptrade/application/portfolio_owner_binding.py
Lines: 77-89
Matched Terms: portfolio, user_id, owner
Calls: PortfolioOwnerBindingError, str, str(value).strip

_require_sha256
File: backend/app/stacks/snaptrade/application/portfolio_owner_binding.py
Lines: 92-120
Matched Terms: portfolio, owner
Calls: PortfolioOwnerBindingError, int, isinstance, len, value.strip, value.strip().lower

hash_account_identifier
File: backend/app/stacks/snaptrade/application/portfolio_owner_binding.py
Lines: 123-137
Matched Terms: portfolio, owner
Calls: PortfolioOwnerBindingError, account_identifier.strip, hashlib.sha256, hashlib.sha256(normalized.encode('utf-8')).hexdigest, normalized.encode

load_portfolio_owner_binding_registry
File: backend/app/stacks/snaptrade/application/portfolio_owner_binding.py
Lines: 140-274
Matched Terms: portfolio, user_id, owner
Calls: MappingProxyType, Path, PortfolioOwnerBinding, PortfolioOwnerBindingError, PortfolioOwnerBindingRegistry, _normalize_user_id, _require_sha256, claimed_account_hashes.get, document.get, isinstance, json.loads, len, raw_bindings.items, registry_path.is_file, registry_path.read_text, set, sorted, tuple

resolve_owned_account_hashes
File: backend/app/stacks/snaptrade/application/portfolio_owner_binding.py
Lines: 277-290
Matched Terms: portfolio, user_id, owner
Calls: load_portfolio_owner_binding_registry, registry.resolve

filter_owned_accounts
File: backend/app/stacks/snaptrade/application/portfolio_owner_binding.py
Lines: 293-328
Matched Terms: portfolio, user_id, owner
Calls: PortfolioOwnerBindingError, _require_sha256, resolve_owned_account_hashes, set, sorted, tuple

resolve
File: backend/app/stacks/snaptrade/application/portfolio_owner_binding.py
Lines: 56-74
Matched Terms: portfolio, user_id, owner
Calls: PortfolioOwnerBindingNotFound, _normalize_user_id, self.bindings.get

qualified_snapshot_path
File: backend/app/stacks/snaptrade/tests/test_normalized_portfolio_ingestion.py
Lines: 15-34
Matched Terms: portfolio
Calls: Path, Path('runtime/snaptrade_integration').glob, path.stat, pytest.skip, sorted

write_mutated
File: backend/app/stacks/snaptrade/tests/test_normalized_portfolio_ingestion.py
Lines: 45-64
Matched Terms: portfolio
Calls: json.dumps, target.write_text

test_ingests_qualified_snapshot
File: backend/app/stacks/snaptrade/tests/test_normalized_portfolio_ingestion.py
Lines: 67-118
Matched Terms: portfolio, position, read_only
Calls: all, ingest_normalized_portfolio, qualified_snapshot_path, set

test_contract_is_immutable
File: backend/app/stacks/snaptrade/tests/test_normalized_portfolio_ingestion.py
Lines: 121-129
Matched Terms: portfolio
Calls: ingest_normalized_portfolio, pytest.raises, qualified_snapshot_path

test_rejects_unsafe_top_level_flags
File: backend/app/stacks/snaptrade/tests/test_normalized_portfolio_ingestion.py
Lines: 164-183
Matched Terms: portfolio
Calls: ingest_normalized_portfolio, load_source, pytest.mark.parametrize, pytest.raises, write_mutated

test_rejects_wrong_schema
File: backend/app/stacks/snaptrade/tests/test_normalized_portfolio_ingestion.py
Lines: 186-203
Matched Terms: portfolio
Calls: ingest_normalized_portfolio, load_source, pytest.raises, write_mutated

test_rejects_wrong_schema_version
File: backend/app/stacks/snaptrade/tests/test_normalized_portfolio_ingestion.py
Lines: 206-223
Matched Terms: portfolio
Calls: ingest_normalized_portfolio, load_source, pytest.raises, write_mutated

test_rejects_raw_account_identifier
File: backend/app/stacks/snaptrade/tests/test_normalized_portfolio_ingestion.py
Lines: 226-245
Matched Terms: portfolio
Calls: ingest_normalized_portfolio, load_source, pytest.raises, write_mutated

test_rejects_position_count_drift
File: backend/app/stacks/snaptrade/tests/test_normalized_portfolio_ingestion.py
Lines: 248-265
Matched Terms: portfolio, position
Calls: ingest_normalized_portfolio, load_source, pytest.raises, write_mutated

test_does_not_import_snaptrade_sdk
File: backend/app/stacks/snaptrade/tests/test_normalized_portfolio_ingestion.py
Lines: 268-278
Matched Terms: portfolio
Calls: Path, Path(adapter.__file__).read_text

write_registry
File: backend/app/stacks/snaptrade/tests/test_portfolio_owner_binding.py
Lines: 18-44
Matched Terms: portfolio, owner
Calls: json.dumps, path.write_text

test_empty_registry_fails_closed
File: backend/app/stacks/snaptrade/tests/test_portfolio_owner_binding.py
Lines: 47-61
Matched Terms: portfolio, user_id, owner
Calls: pytest.raises, resolve_owned_account_hashes, write_registry

test_resolves_only_authenticated_owner
File: backend/app/stacks/snaptrade/tests/test_portfolio_owner_binding.py
Lines: 64-99
Matched Terms: user_id, owner
Calls: hash_account_identifier, resolve_owned_account_hashes, write_registry

test_rejects_cross_owner_account_reuse
File: backend/app/stacks/snaptrade/tests/test_portfolio_owner_binding.py
Lines: 102-127
Matched Terms: portfolio, owner
Calls: hash_account_identifier, load_portfolio_owner_binding_registry, pytest.raises, write_registry

test_filters_snapshot_accounts_to_owner
File: backend/app/stacks/snaptrade/tests/test_portfolio_owner_binding.py
Lines: 130-159
Matched Terms: user_id, owner
Calls: filter_owned_accounts, hash_account_identifier, write_registry

test_rejects_binding_to_absent_snapshot_account
File: backend/app/stacks/snaptrade/tests/test_portfolio_owner_binding.py
Lines: 162-192
Matched Terms: portfolio, user_id, owner
Calls: filter_owned_accounts, hash_account_identifier, pytest.raises, write_registry

test_rejects_empty_user_id
File: backend/app/stacks/snaptrade/tests/test_portfolio_owner_binding.py
Lines: 203-219
Matched Terms: portfolio, user_id, owner
Calls: pytest.mark.parametrize, pytest.raises, resolve_owned_account_hashes, write_registry

generate_strategy_decision
File: backend/app/stacks/strategy/engine.py
Lines: 8-102
Matched Terms: portfolio
Calls: float, generate_signal, get_bars, get_latest_price, isinstance, portfolio_output.get, rebalance_portfolio, str, str(action).upper, strategy_signal.get

executor_status
File: backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/dev_command_read_only_executor.py
Lines: 25-37
Matched Terms: read_only
Calls: NONE EXTRACTED

preview_dev_command
File: backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/dev_command_read_only_executor.py
Lines: 40-57
Matched Terms: read_only
Calls: executor_status

extract_learning_features
File: backend/app/stacks/strategy_candidate_sandbox/learning_feature_extractor.py
Lines: 62-100
Matched Terms: position
Calls: _num, all, row.get

build_qwen_read_only_response_contract
File: backend/app/stacks/strategy_candidate_sandbox/qwen_context_response_contract.py
Lines: 21-40
Matched Terms: read_only
Calls: context.get, isinstance

validate_qwen_read_only_response_contract
File: backend/app/stacks/strategy_candidate_sandbox/qwen_context_response_contract.py
Lines: 43-60
Matched Terms: read_only
Calls: all, bool, checks.values, isinstance, len, payload.get

build_qwen_read_only_architecture_context
File: backend/app/stacks/strategy_candidate_sandbox/qwen_read_only_architecture_context.py
Lines: 20-52
Matched Terms: read_only
Calls: QWEN_CONTEXT_LOCKS.copy, architecture_inspection.get, handoff_bundle.get, isinstance

validate_qwen_read_only_architecture_context
File: backend/app/stacks/strategy_candidate_sandbox/qwen_read_only_architecture_context.py
Lines: 55-80
Matched Terms: read_only
Calls: all, checks.values, isinstance, locks.get, payload.get

build_qwen_summary_gate
File: backend/app/stacks/strategy_candidate_sandbox/qwen_read_only_architecture_summary_gate.py
Lines: 22-50
Matched Terms: read_only
Calls: SUMMARY_GATE_LOCKS.copy, context.get, context_artifact.get, isinstance, sample.get, sample_response_artifact.get

validate_qwen_summary_gate
File: backend/app/stacks/strategy_candidate_sandbox/qwen_read_only_architecture_summary_gate.py
Lines: 53-79
Matched Terms: read_only
Calls: all, checks.values, gate.get, isinstance, locks.get

inspect_architecture_artifacts
File: backend/app/stacks/strategy_candidate_sandbox/safe_read_only_architecture_inspector.py
Lines: 18-56
Matched Terms: read_only
Calls: READ_ONLY_LOCKS.copy, all, isinstance, len, runtime_trace.get, step.get, wiregraph.get

validate_architecture_inspection
File: backend/app/stacks/strategy_candidate_sandbox/safe_read_only_architecture_inspector.py
Lines: 59-86
Matched Terms: read_only
Calls: all, checks.values, gates.get, isinstance, payload.get, payload.get('read_only_locks', {}).values, trace_locks.get

_monitor_and_process_signals_core
File: backend/app/stacks/wolfden_ai/agent_router.py
Lines: 16-46
Matched Terms: portfolio
Calls: build_portfolio_output_result, drawdown_healthcheck, drawdown_status.get, generate_strategy_decision, is_kill_switch_active, print, record_wolfden_observation, set_kill_switch, str, time.time

record_wolfden_observation
File: backend/app/stacks/wolfden_ai/observability_boundary.py
Lines: 174-234
Matched Terms: portfolio
Calls: WolfdenObservation, _LOGGER.info, _freeze_value, enumerate, kwargs.items, kwargs.pop, observation.to_dict, payload_items.extend, sorted, str, str(event_name_value).strip, tuple

as_read_only_mapping
File: backend/app/stacks/wolfden_ai/observability_boundary.py
Lines: 142-147
Matched Terms: read_only
Calls: MappingProxyType, self.to_dict

build_portfolio_output_result
File: backend/app/stacks/wolfden_ai/portfolio_output_result_facade.py
Lines: 188-228
Matched Terms: portfolio
Calls: WolfdenPortfolioOutputResult, _freeze_value, enumerate, kwargs.items, payload_items.extend, sorted, str, tuple

__post_init__
File: backend/app/stacks/wolfden_ai/portfolio_output_result_facade.py
Lines: 109-135
Matched Terms: portfolio
Calls: ValueError, self.status.strip

as_read_only_mapping
File: backend/app/stacks/wolfden_ai/portfolio_output_result_facade.py
Lines: 155-160
Matched Terms: read_only
Calls: MappingProxyType, self.to_dict

test_valid_structured_output_is_parsed
File: backend/app/stacks/wolfden_ai/tests/test_local_model_binding.py
Lines: 101-107
Matched Terms: position
Calls: parse_local_model_output

test_boundary_owns_no_persistence_or_execution
File: backend/app/stacks/wolfden_ai/tests/test_observability_boundary.py
Lines: 270-314
Matched Terms: portfolio
Calls: _calls, _imports, any, call.split, module.lower

test_result_is_immutable
File: backend/app/stacks/wolfden_ai/tests/test_portfolio_output_result_facade.py
Lines: 115-123
Matched Terms: portfolio
Calls: build_portfolio_output_result, pytest.raises

test_result_is_non_executable
File: backend/app/stacks/wolfden_ai/tests/test_portfolio_output_result_facade.py
Lines: 126-135
Matched Terms: portfolio
Calls: build_portfolio_output_result

test_result_rejects_executable_state
File: backend/app/stacks/wolfden_ai/tests/test_portfolio_output_result_facade.py
Lines: 138-150
Matched Terms: portfolio
Calls: WolfdenPortfolioOutputResult, pytest.raises

test_payload_is_deeply_frozen
File: backend/app/stacks/wolfden_ai/tests/test_portfolio_output_result_facade.py
Lines: 153-183
Matched Terms: portfolio
Calls: build_portfolio_output_result, dict, original['symbols'].append

test_result_has_serializable_mapping_contract
File: backend/app/stacks/wolfden_ai/tests/test_portfolio_output_result_facade.py
Lines: 186-204
Matched Terms: portfolio
Calls: build_portfolio_output_result, dict, result.to_dict

test_agent_router_uses_wolfden_facade_only
File: backend/app/stacks/wolfden_ai/tests/test_portfolio_output_result_facade.py
Lines: 207-219
Matched Terms: portfolio
Calls: _imports

test_wolfden_owns_no_execution_or_mutation_capability
File: backend/app/stacks/wolfden_ai/tests/test_portfolio_output_result_facade.py
Lines: 222-296
Matched Terms: portfolio
Calls: WOLFDEN_ROOT.rglob, _calls, _imports, any, call.split, forbidden_calls.append, forbidden_imports.append, module.split, path.name.startswith, path.relative_to, path.relative_to(ROOT).as_posix, sorted

test_security_metrics_count_unauthorized_and_forbidden
File: backend/app/test/test_graph_event_metrics.py
Lines: 97-146
Matched Terms: authorization
Calls: isolated_state, state.activate_node

test_edge_metrics_are_aggregated
File: backend/app/test/test_graph_event_metrics.py
Lines: 149-202
Matched Terms: dashboard, analytics
Calls: isolated_state, state.activate_edge

test_stage8e_architecture_nodes_are_registered
File: backend/app/test/test_stage8e_runtime_instrumentation.py
Lines: 18-39
Matched Terms: authorization
Calls: expected.items

test_route_policy_emits_security_events
File: backend/app/test/test_stage8e_runtime_instrumentation.py
Lines: 99-115
Matched Terms: authorization
Calls: Path, Path('backend/app/stacks/identity_auth/route_protection.py').read_text

test_all_layers_have_declared_nodes
File: backend/app/test/test_stage8f_graph_materialization.py
Lines: 27-44
Matched Terms: owner
Calls: NODE_ARCHITECTURE.values, ownership.get

test_required_facades_are_declared_in_l3
File: backend/app/test/test_stage8f_graph_materialization.py
Lines: 47-67
Matched Terms: portfolio
Calls: NONE EXTRACTED

test_frontend_workspaces_and_proxies_are_declared
File: backend/app/test/test_stage8f_graph_materialization.py
Lines: 70-95
Matched Terms: dashboard, portfolio
Calls: NONE EXTRACTED

test_historical_nodes_have_explicit_ownership
File: backend/app/test/test_stage8f_historical_node_assignment.py
Lines: 45-60
Matched Terms: owner
Calls: EXPECTED.items

_lookup_modules
File: backend/app/test/test_trading_pipeline.py
Lines: 102-128
Matched Terms: owner
Calls: _optional_modules, inspect.getmodule, isinstance, modules.append, owner.__dict__.values

test_trading_pipeline_success
File: backend/app/test/test_trading_pipeline.py
Lines: 174-319
Matched Terms: portfolio, user_id
Calls: AsyncMock, ExitStack, MagicMock, _assert_isolated_output, _patch_symbol_everywhere, capsys.readouterr, process_portfolio_output

test_trading_pipeline_blocked
File: backend/app/test/test_trading_pipeline.py
Lines: 323-436
Matched Terms: portfolio, user_id
Calls: AsyncMock, ExitStack, MagicMock, _assert_isolated_output, _patch_symbol_everywhere, any, capsys.readouterr, isinstance, payload.get, process_portfolio_output

test_agent_router_trips_kill_switch
File: backend/app/test/test_trading_pipeline.py
Lines: 440-646
Matched Terms: portfolio, owner
Calls: AsyncMock, ExitStack, MagicMock, _assert_isolated_output, _patch_symbol_everywhere, asyncio.wait_for, capsys.readouterr, hasattr, inspect.getmodule, monitor_and_process_signals, patch.object, stack.enter_context

Repository and Persistence Files

backend/app/stacks/chat_public/conversation_store.py
backend/app/stacks/chat_public/persistence/chat_models.py
backend/app/stacks/identity_auth/access_token_revocation_repository.py
backend/app/stacks/identity_auth/tests/test_identity_persistence_models.py
backend/app/stacks/identity_auth/tests/test_refresh_session_persistence.py
backend/app/stacks/identity_auth/tests/test_stage5b_a_durable_revocation_repository.py
backend/app/stacks/journal_ledger/decision_event_repository.py

Database Model Files

backend/app/stacks/chat_public/cognitive_model_router.py
backend/app/stacks/chat_public/persistence/chat_models.py
backend/app/stacks/chat_public/tests/test_cognitive_model_router.py
backend/app/stacks/db_runtime/model_registry.py
backend/app/stacks/identity_auth/__init__.py
backend/app/stacks/identity_auth/access_token_revocation_models.py
backend/app/stacks/identity_auth/access_token_revocation_repository.py
backend/app/stacks/identity_auth/admin_mutation_api_models.py
backend/app/stacks/identity_auth/admin_mutation_router.py
backend/app/stacks/identity_auth/admin_mutation_service.py
backend/app/stacks/identity_auth/admin_read_api_models.py
backend/app/stacks/identity_auth/admin_read_dependencies.py
backend/app/stacks/identity_auth/admin_read_models.py
backend/app/stacks/identity_auth/admin_read_router.py
backend/app/stacks/identity_auth/api_router.py
backend/app/stacks/identity_auth/authorization_policy.py
backend/app/stacks/identity_auth/dev_owner_provisioner.py
backend/app/stacks/identity_auth/login_service.py
backend/app/stacks/identity_auth/migrations/stage9d_a_identity_schema.py
backend/app/stacks/identity_auth/mock_runtime.py
backend/app/stacks/identity_auth/models.py
backend/app/stacks/identity_auth/password_change_service.py
backend/app/stacks/identity_auth/registration_service.py
backend/app/stacks/identity_auth/repositories.py
backend/app/stacks/identity_auth/revocation.py
backend/app/stacks/identity_auth/route_protection.py
backend/app/stacks/identity_auth/service_contracts.py
backend/app/stacks/identity_auth/session_introspection.py
backend/app/stacks/identity_auth/session_lifecycle_service.py
backend/app/stacks/identity_auth/session_service.py
backend/app/stacks/identity_auth/tests/test_api_route_contract.py
backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py
backend/app/stacks/identity_auth/tests/test_canonical_router_inclusion.py
backend/app/stacks/identity_auth/tests/test_display_name.py
backend/app/stacks/identity_auth/tests/test_identity_persistence_models.py
backend/app/stacks/identity_auth/tests/test_login_service.py
backend/app/stacks/identity_auth/tests/test_refresh_session_persistence.py
backend/app/stacks/identity_auth/tests/test_registration.py
backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py
backend/app/stacks/identity_auth/tests/test_registration_service.py
backend/app/stacks/identity_auth/tests/test_session_introspection.py
backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
backend/app/stacks/identity_auth/tests/test_stage4f_canonical_claim_propagation.py
backend/app/stacks/identity_auth/tests/test_stage4f_environment_token_issuer_contract.py
backend/app/stacks/identity_auth/tests/test_stage4f_login_refresh_claims.py
backend/app/stacks/identity_auth/tests/test_stage4f_mock_identity_contract.py
backend/app/stacks/identity_auth/tests/test_stage4f_rotated_refresh_claims.py
backend/app/stacks/identity_auth/tests/test_stage5b_a_durable_revocation_repository.py
backend/app/stacks/identity_auth/tests/test_stage5b_b_durable_bearer_logout.py
backend/app/stacks/identity_auth/tests/test_stage5b_c_revocation_observability_cleanup.py
backend/app/stacks/identity_auth/tests/test_stage9d_a_identity_schema.py
backend/app/stacks/identity_auth/tests/test_stage9d_b_forced_password_change.py
backend/app/stacks/identity_auth/tests/test_stage9d_c2_admin_read_models.py
backend/app/stacks/identity_auth/tests/test_stage9d_c5_b_admin_user_mutations.py
backend/app/stacks/identity_auth/tests/test_stage9d_c5_i_authorization_policy.py
backend/app/stacks/identity_auth/tests/test_stage9d_c5_j1_subscription_tier.py
backend/app/stacks/identity_auth/tests/test_stage9d_c5_k1_session_introspection.py
backend/app/stacks/journal_ledger/decision_event_model.py
backend/app/stacks/portfolio/read_models/readonly_portfolio_snapshot.py
backend/app/stacks/snaptrade/contracts/readonly_models.py
backend/app/stacks/wolfden_ai/tests/test_local_model_binding.py

Facade and Service Files

backend/app/spine/L5_api/owned_readonly_portfolio_service.py
backend/app/stacks/chat_public/tests/test_conversation_service_boundary.py
backend/app/stacks/identity_auth/admin_mutation_service.py
backend/app/stacks/identity_auth/login_service.py
backend/app/stacks/identity_auth/password_change_service.py
backend/app/stacks/identity_auth/registration_service.py
backend/app/stacks/identity_auth/service_contracts.py
backend/app/stacks/identity_auth/session_lifecycle_service.py
backend/app/stacks/identity_auth/session_service.py
backend/app/stacks/identity_auth/tests/test_login_service.py
backend/app/stacks/identity_auth/tests/test_registration_service.py
backend/app/stacks/journal_ledger/decision_audit_service.py
backend/app/stacks/portfolio/dashboard_service.py
backend/app/stacks/portfolio/facades/readonly_portfolio_facade.py
backend/app/stacks/portfolio/portfolio_service.py
backend/app/stacks/portfolio/tests/test_readonly_portfolio_facade.py
backend/app/stacks/wolfden_ai/portfolio_output_result_facade.py
backend/app/stacks/wolfden_ai/tests/test_portfolio_output_result_facade.py

Provider Files

backend/app/stacks/market_data/provider_contract.py
backend/app/stacks/market_data/provider_registry.py
backend/app/stacks/market_data/yfinance_provider.py
backend/app/stacks/snaptrade/providers/mock_provider.py

Security

authentication_markers_detected

True

unauthorized_redirect_detected

False

ownership_markers_detected

True

authorization_markers_detected

True

role_markers_detected

True

read_only_markers_detected

True

csrf_markers_detected

True

rate_limit_markers_detected

True

Loading Behaviour

loading_state_detected

True

error_state_detected

True

empty_state_detected

True

retry_detected

True

stale_data_marker_detected

True

responsive_classes_detected

True

accessibility_markers_detected

True

Failure Paths

Missing Session

Expected: redirect to /login

Status: UNVERIFIED

Expired Access Token

Expected: refresh recovery or redirect to login

Status: UNVERIFIED

Revoked Session

Expected: deny dashboard access

Status: UNVERIFIED

Wrong User Ownership

Expected: no cross-user portfolio or account data

Status: UNVERIFIED

Backend Unavailable

Dashboard error state detected

Empty Portfolio

Empty state detected

Partial Data Failure

UNVERIFIED

Provider Failure

UNVERIFIED

Tests

backend/app/stacks/chat_public/tests/test_authenticated_role_truth_boundary.py

test_system_prompt_rejects_conversational_role_elevation
test_user_overlay_remains_user_despite_developer_claim
test_developer_overlay_requires_server_supplied_developer_role
test_local_evidence_requires_explicit_server_permission
test_authenticated_developer_wording_triggers_developer_intent
test_user_wording_alone_does_not_grant_local_evidence
test_authenticated_developer_permission_uses_local_evidence

backend/app/stacks/chat_public/tests/test_chat_intent_regex.py

test_detect_chat_intent_v2_metadata_and_legacy_compatibility
test_developer_pronoun_i_is_not_detected_as_ticker
test_market_symbol_is_preserved
test_blocked_live_execution_remains_fail_closed
test_chat_intent_legacy_constructor_remains_valid

backend/app/stacks/chat_public/tests/test_cognitive_model_router.py

test_routing_decision_is_immutable
test_general_greeting_uses_fast_model
test_analysis_and_strategy_use_reason_model
test_code_work_uses_code_model
test_math_declares_deterministic_tool_requirement
test_current_or_account_data_declares_retrieval
test_decision_serializes_complete_contract
test_exact_authenticated_math_prompt_requires_deterministic_tool
test_exact_authenticated_research_prompt_requires_retrieval
test_common_math_phrasing_requires_deterministic_tool
test_local_research_phrasing_requires_retrieval
test_position_size_uses_math_without_retrieval
test_conversation_memory_avoids_retrieval
test_explicit_retrieval_requests_remain_enabled
test_strategy_family_retains_retrieval_contract
test_market_and_portfolio_family_do_not_force_retrieval
test_router_never_exposes_execution_authority

backend/app/stacks/chat_public/tests/test_deterministic_math_engine.py

test_registry_is_explicit_and_complete
test_exact_decimal_arithmetic
test_percentage_of
test_percent_change
test_simple_return
test_compound_return
test_cagr
test_expected_value
test_risk_reward
test_position_size
test_portfolio_weights
test_descriptive_statistics
test_sharpe_ratio_is_deterministic
test_sortino_ratio_is_deterministic
test_maximum_drawdown
test_trade_statistics
test_invalid_inputs_fail_closed
test_unsupported_operation_fails_closed
test_sequence_boundary_is_enforced
test_non_finite_or_invalid_values_are_rejected
test_serialized_result_contains_no_float_values
test_math_engine_has_no_execution_or_network_authority

backend/app/stacks/chat_public/tests/test_live_math_runtime_integration.py

test_supported_math_requests_are_extracted
test_percentage_result_is_exact
test_cagr_result_is_deterministic
test_position_size_uses_whole_units
test_unrequested_math_does_not_execute
test_ambiguous_math_fails_controlled
test_division_by_zero_returns_error_evidence
test_runtime_contains_math_integration
test_live_math_has_no_arbitrary_execution

backend/app/stacks/chat_public/tests/test_live_rag_activation.py

test_strategy_family_requests_retrieval
test_retrieval_is_not_called_when_not_requested
test_retrieval_filters_injection_chunks_and_bounds_top_k
test_prompt_contains_page_aware_citation
test_prompt_respects_total_character_boundary
test_retrieval_failure_returns_controlled_bundle
test_chat_runtime_contains_live_rag_integration
test_live_rag_module_does_not_enable_execution

backend/app/stacks/chat_public/tests/test_local_rag_index.py

test_chunking_is_deterministic
test_chunking_rejects_invalid_overlap
test_stable_identifiers_are_repeatable
test_source_policy_rejects_secrets_and_runtime
test_prompt_injection_is_detected
test_ingestion_deduplicates_identical_content
test_semantic_retrieval_ranks_relevant_chunk_first
test_no_result_behavior_is_controlled
test_index_contract_contains_no_execution_authority

backend/app/stacks/chat_public/tests/test_public_chat_controls.py

test_public_chat_contract_accepts_valid_text
test_public_chat_contract_rejects_empty_text
test_public_chat_contract_rejects_oversized_text
test_public_chat_safety_denies_restricted_action
test_public_chat_safety_allows_general_discussion
test_public_chat_timeout_maps_to_504
test_public_chat_dependency_failure_maps_to_503
test_public_chat_rate_limit_maps_to_429
test_public_chat_safety_denial_maps_to_403
test_route_is_decorated_with_public_controls
test_public_control_wrapper_preserves_signature
test_payload_boundary_ignores_injected_dependencies
test_payload_boundary_rejects_oversized_payload
test_payload_boundary_rejects_empty_payload
test_payload_boundary_safety_uses_only_payload
test_payload_boundary_still_rejects_restricted_payload
test_missing_payload_argument_fails_closed
test_configured_payload_wrapper_preserves_signature
test_chat_route_configures_payload_argument

backend/app/stacks/chat_public/tests/test_role_overlay_injection.py

test_role_overlay_is_inserted_in_correct_order
test_no_overlay_path_remains_supported
test_chat_api_passes_principal_to_runtime
test_runtime_passes_overlay_and_intent_metadata
test_unknown_role_fails_closed_to_user_overlay
test_deterministic_developer_path_remains_grounded

backend/app/stacks/db_runtime/tests/test_transaction_guard.py

test_guard_does_not_rollback_successful_scope
test_guard_rolls_back_write_failure_and_reraises
test_guard_rolls_back_commit_failure_and_reraises
test_guard_rolls_back_cancellation
test_approved_write_path_uses_transaction_guard
test_legacy_market_schema_remains_isolated

backend/app/stacks/db_runtime/tests/test_transaction_manager.py

test_success_executes_flush_then_commit
test_operation_failure_rolls_back_and_reraises
test_flush_failure_rolls_back_and_reraises
test_commit_failure_rolls_back_and_reraises
test_non_callable_operation_is_rejected

backend/app/stacks/identity_auth/tests/test_api_dependency.py

test_missing_bearer_credentials_are_unauthorized
test_wrong_scheme_is_unauthorized
test_valid_access_token_returns_principal
test_refresh_token_is_rejected_by_api_dependency
test_malformed_token_is_unauthorized

backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py

test_route_policy_inventory
test_public_route_requires_no_token
test_authenticated_route_rejects_missing_token
test_authenticated_route_accepts_principal
test_admin_route_rejects_non_admin
test_admin_route_accepts_server_claim
test_unknown_route_preserves_not_found
test_refresh_token_validation_failure_is_unauthorized

backend/app/stacks/identity_auth/tests/test_canonical_router_inclusion.py

test_canonical_source_includes_auth_router_once
test_auth_router_has_complete_session_lifecycle
test_controlled_local_registration_and_login

backend/app/stacks/identity_auth/tests/test_display_name.py

test_registration_with_display_name
test_registration_with_trimmed_display_name
test_registration_with_empty_display_name
test_registration_with_long_display_name
test_registration_without_display_name
test_session_introspection_includes_display_name

backend/app/stacks/identity_auth/tests/test_identity_persistence_models.py

test_identity_user_schema_contract
test_refresh_session_schema_contract
test_email_normalization_is_canonical
test_refresh_token_hash_never_contains_raw_token

backend/app/stacks/identity_auth/tests/test_identity_repository.py

test_user_repository_normalizes_email
test_user_repository_rejects_empty_hash

backend/app/stacks/identity_auth/tests/test_login_service.py

test_valid_login_issues_separate_tokens_and_session
test_unknown_user_and_wrong_password_share_error
test_disabled_account_fails_closed
test_inactive_status_fails_closed
test_refresh_session_failure_rolls_back
test_identical_tokens_fail_closed

backend/app/stacks/identity_auth/tests/test_refresh_session_persistence.py

test_rotation_preserves_family_and_revokes_old
test_reuse_revokes_entire_family
test_logout_is_idempotent

backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py

test_complete_mock_registration_and_login_flow
test_duplicate_registration_rolls_back
test_unknown_and_wrong_password_share_error
test_disabled_account_rejected_before_token_issuance
test_access_token_failure_rolls_back
test_refresh_token_failure_rolls_back
test_refresh_session_failure_rolls_back
test_registration_commit_failure_fails_closed
test_login_commit_failure_fails_closed

backend/app/stacks/identity_auth/tests/test_runtime_adapter.py

test_runtime_construction_is_non_mutating
test_runtime_fails_closed_without_secret
test_real_access_and_refresh_token_paths

backend/app/stacks/identity_auth/tests/test_session_introspection.py

test_session_introspection_with_display_name
test_session_introspection_without_display_name

backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py

test_lifecycle_route_policy_inventory
test_refresh_returns_rotated_pair
test_logout_revokes_current_refresh_session
test_refresh_rejection_is_unauthorized
test_logout_rejection_is_unauthorized
test_logout_all_uses_access_principal_subject
test_logout_all_rejects_missing_access_token
test_refresh_request_forbids_extra_fields
test_logout_request_forbids_extra_fields

backend/app/stacks/identity_auth/tests/test_stage4f_canonical_claim_propagation.py

test_login_issues_canonical_role_and_tier_claims
test_login_rejects_invalid_stored_role
test_refresh_uses_current_user_claims
test_refresh_rejects_missing_current_user

backend/app/stacks/identity_auth/tests/test_stage4f_login_refresh_claims.py

test_login_forwards_canonical_claims_to_both_tokens

backend/app/stacks/identity_auth/tests/test_stage4f_rotated_refresh_claims.py

test_rotated_refresh_token_receives_canonical_claims

backend/app/stacks/identity_auth/tests/test_stage4f_session_lifecycle_runtime_wiring.py

test_session_lifecycle_runtime_builds_user_repository
test_session_lifecycle_runtime_uses_one_shared_session

backend/app/stacks/identity_auth/tests/test_stage5b_a_durable_revocation_repository.py

test_revocation_model_exposes_only_safe_fields
test_revocation_token_id_is_unique
test_repository_rejects_invalid_identifiers
test_repository_rejects_invalid_lifetime

backend/app/stacks/identity_auth/tests/test_stage5b_b_durable_bearer_logout.py

test_logout_persists_access_and_refresh_revocation_before_commit
test_logout_rolls_back_both_revocations_on_failure
test_logout_rejects_access_refresh_subject_mismatch

backend/app/stacks/identity_auth/tests/test_stage5b_c_revocation_observability_cleanup.py

test_revocation_routes_are_get_only
test_revocation_summary_exposes_no_jti
test_cleanup_service_commits_success
test_cleanup_service_rolls_back_failure

backend/app/stacks/identity_auth/tests/test_stage9d_b_forced_password_change.py

test_replacement_password_policy_rejects_weak_values
test_replacement_password_policy_accepts_strong_value
test_required_password_change_updates_hash_and_revokes_sessions
test_wrong_temporary_password_fails_closed

backend/app/stacks/identity_auth/tests/test_stage9d_c2_admin_read_models.py

test_user_models_expose_no_secrets
test_session_models_expose_no_secrets
test_admin_routes_are_get_only
test_admin_dependency_is_database_authoritative
test_read_service_does_not_serialize_secret_fields
test_openapi_contains_only_expected_admin_methods
test_no_password_reset_route_added_in_c2

backend/app/stacks/identity_auth/tests/test_stage9d_c5_b_admin_user_mutations.py

test_admin_mutation_routes_are_exact
test_temporary_password_policy
test_protected_roles_denied
test_self_mutation_denied

backend/app/stacks/identity_auth/tests/test_stage9d_c5_k1_session_introspection.py

test_canonical_router_contains_introspection_route
test_introspection_route_policy_is_authenticated
test_introspection_uses_principal_subject
test_missing_identity_fails_closed
test_inactive_identity_fails_closed
test_disabled_identity_fails_closed

backend/app/stacks/journal_ledger/tests/test_decision_event_repository.py

test_first_append_allocates_sequence_one
test_second_append_links_previous_hash
test_duplicate_is_rejected_before_insert
test_commit_failure_rolls_back
test_repository_exposes_no_mutation_methods
test_append_rejects_naive_recorded_at

backend/app/stacks/journal_ledger/tests/test_strategy_decision_audit_adapter.py

test_produce_and_audit_delegates_to_service
test_missing_envelope_field_fails_before_append
test_symbol_mismatch_fails_before_append
test_invalid_confidence_fails_before_append
test_naive_occurred_at_is_rejected
test_adapter_exposes_no_mutation_or_execution_methods

backend/app/stacks/market_data/tests/test_provider_contract.py

test_symbol_normalization
test_empty_symbol_rejected
test_quote_normalizes_fields
test_naive_quote_timestamp_rejected
test_invalid_ohlc_rejected
test_request_date_order_enforced
test_result_requires_matching_symbol
test_fixture_satisfies_protocol
test_fixture_returns_canonical_quote
test_fixture_returns_canonical_bars

backend/app/stacks/market_data/tests/test_provider_runtime.py

test_registry_registers_and_selects_by_priority
test_registry_rejects_duplicate_name
test_registry_ignores_disabled_provider
test_cache_returns_unexpired_value
test_cache_expires_value
test_cache_evicts_least_recently_used
test_market_session_classification
test_market_session_rejects_naive_datetime
test_router_uses_highest_priority_provider
test_router_falls_back_after_provider_failure
test_router_fails_closed_when_all_providers_fail
test_router_quote_cache_prevents_second_provider_call
test_router_returns_canonical_historical_result

backend/app/stacks/market_data/tests/test_stage8_runtime_qualification.py

test_quote_cache_prevents_repeated_provider_call
test_quote_cache_expiry_forces_refresh
test_use_cache_false_always_calls_provider
test_router_falls_back_after_quote_failure
test_router_falls_back_after_historical_failure
test_router_fails_closed_when_every_provider_fails
test_api_translates_provider_failure_to_503
test_api_rejects_invalid_historical_range
test_status_endpoint_does_not_call_provider

backend/app/stacks/market_data/tests/test_yfinance_provider.py

test_module_import_does_not_require_yfinance
test_wrapper_satisfies_provider_contract
test_capabilities_are_declared
test_numeric_quote_is_normalized
test_mapping_quote_is_normalized
test_quote_symbol_mismatch_fails
test_quote_loader_failure_is_translated
test_historical_mapping_is_normalized
test_historical_rows_are_sorted
test_historical_limit_is_applied
test_historical_loader_failure_is_translated
test_healthcheck_does_not_load_dependencies

backend/app/stacks/portfolio/tests/test_authenticated_owned_readonly_portfolio_api.py

test_configured_owner_receives_two_accounts
test_unbound_user_is_denied
test_empty_principal_subject_is_denied
test_owner_receives_only_bound_account_hashes
test_read_views_are_normalized
test_symbol_lookup_is_owner_scoped
test_no_raw_account_identifier_fields_are_returned
test_service_records_no_network_or_database_activity

backend/app/stacks/portfolio/tests/test_authenticated_paper_order_api.py

test_paper_order_route_policy_is_authenticated
test_paper_order_route_is_registered
test_paper_order_normalizes_symbol
test_paper_order_rejects_invalid_symbol
test_paper_order_rejects_invalid_action
test_paper_order_propagates_authenticated_owner
test_two_orders_keep_owners_separate

backend/app/stacks/portfolio/tests/test_authenticated_portfolio_read_boundary.py

test_portfolio_service_passes_principal_subject
test_portfolio_service_rejects_empty_subject
test_paper_snapshot_rejects_empty_user_id
test_paper_snapshot_is_explicitly_account_scoped

backend/app/stacks/portfolio/tests/test_authenticated_portfolio_read_isolation.py

test_accounting_rejects_empty_owner
test_ledger_read_rejects_empty_owner
test_position_route_is_authenticated_and_scoped
test_orders_route_is_authenticated_and_scoped
test_analytics_route_is_authenticated_and_scoped
test_accounting_is_owner_scoped
test_max_allocation_is_owner_scoped
test_risk_propagates_owner
test_execution_propagates_owner

backend/app/stacks/portfolio/tests/test_authenticated_portfolio_valuation_api.py

test_portfolio_valuation_policy_is_authenticated
test_portfolio_valuation_route_is_registered
test_portfolio_valuation_propagates_owner
test_portfolio_valuation_keeps_owners_separate

backend/app/stacks/portfolio/tests/test_execution_ownership_propagation.py

test_paper_execution_rejects_empty_user_id
test_ledger_rejects_empty_user_id
test_all_paper_broker_save_log_calls_propagate_user_id
test_ledger_inventory_lookup_is_account_scoped
test_order_history_write_is_account_scoped

backend/app/stacks/portfolio/tests/test_multi_owner_reconciliation_startup.py

test_ambiguous_owner_resolution_returns_none
test_single_owner_resolution_returns_owner
test_empty_owner_resolution_returns_none
test_lifespan_guards_legacy_reconciliation_daemon
test_lifespan_does_not_inline_owner_resolution

backend/app/stacks/portfolio/tests/test_ownership_schema_enforcement.py

test_orm_enforces_owned_rows
test_live_database_enforces_owned_rows

backend/app/stacks/portfolio/tests/test_portfolio_snapshot_lifecycle.py

test_refresh_promotes_owner_scoped_snapshot_atomically
test_second_refresh_preserves_last_known_good
test_failed_refresh_keeps_active_snapshot
test_staleness_is_reported
test_retention_is_bounded
test_unbound_user_refresh_is_denied
test_lifecycle_contains_no_raw_owner_id

backend/app/stacks/portfolio/tests/test_readonly_portfolio_facade.py

test_facade_overview
test_lists_account_summaries
test_get_account_by_hash
test_unknown_account_is_rejected
test_lists_all_positions
test_symbol_lookup_is_normalized
test_unknown_symbol_returns_empty_tuple
test_empty_symbol_is_rejected
test_lists_balances
test_totals_are_provider_neutral
test_overview_is_immutable
test_account_summary_is_immutable
test_symbol_result_is_immutable
test_symbol_index_is_not_mutable
test_facade_has_no_mutation_methods
test_facade_source_has_no_provider_import

backend/app/stacks/portfolio/tests/test_reconciliation_ownership_isolation.py

test_reconciliation_rejects_empty_owner
test_daemon_rejects_empty_owner_before_loop
test_reconciliation_inventory_query_is_owner_scoped
test_reconciliation_order_query_is_owner_and_symbol_scoped
test_daemon_propagates_owner_to_each_audit
test_main_propagates_owner_to_both_runtime_callers

backend/app/stacks/risk/tests/test_drawdown_guard_ledger_boundary.py

test_risk_owns_no_persistence_import
test_risk_imports_no_ledger_internals
test_risk_calls_only_read_facade
test_healthcheck_preserves_none_contract
test_healthcheck_uses_scalar_facade
test_ledger_owns_read_query
test_read_facade_exposes_no_session_or_model

backend/app/stacks/snaptrade/tests/test_normalized_portfolio_ingestion.py

test_ingests_qualified_snapshot
test_contract_is_immutable
test_rejects_unsafe_top_level_flags
test_rejects_wrong_schema
test_rejects_wrong_schema_version
test_rejects_raw_account_identifier
test_rejects_position_count_drift
test_does_not_import_snaptrade_sdk

backend/app/stacks/snaptrade/tests/test_portfolio_owner_binding.py

test_empty_registry_fails_closed
test_resolves_only_authenticated_owner
test_rejects_cross_owner_account_reuse
test_filters_snapshot_accounts_to_owner
test_rejects_binding_to_absent_snapshot_account
test_rejects_empty_user_id
test_registry_contains_no_raw_account_ids

backend/app/stacks/wolfden_ai/tests/test_observability_boundary.py

test_observation_is_immutable
test_observation_is_non_persistent
test_observation_rejects_persistent_state
test_observation_rejects_mutation_request
test_payload_is_deeply_frozen
test_standard_logging_is_used
test_agent_router_uses_observability_boundary
test_boundary_owns_no_persistence_or_execution
test_journal_ledger_and_execution_are_preserved

backend/app/stacks/wolfden_ai/tests/test_portfolio_output_result_facade.py

test_result_is_immutable
test_result_is_non_executable
test_result_rejects_executable_state
test_payload_is_deeply_frozen
test_result_has_serializable_mapping_contract
test_agent_router_uses_wolfden_facade_only
test_wolfden_owns_no_execution_or_mutation_capability

backend/app/test/test_graph_event_metrics.py

test_node_metrics_aggregate_latency_and_success
test_security_metrics_count_unauthorized_and_forbidden
test_edge_metrics_are_aggregated
test_snapshot_advertises_metric_contract_version_two

backend/app/test/test_stage8f_graph_materialization.py

test_all_layers_have_declared_nodes
test_required_facades_are_declared_in_l3
test_frontend_workspaces_and_proxies_are_declared
test_snapshot_materializes_declared_topology_without_events
test_real_node_activation_overrides_declared_state
test_real_edge_materializes_both_endpoints
test_declared_edge_becomes_observed_without_losing_relation
test_stage8f_preserves_version_two_contract

backend/app/test/test_stage8f_historical_node_assignment.py

test_historical_nodes_have_explicit_ownership
test_historical_nodes_do_not_materialize_as_unassigned
test_graph_contains_no_unassigned_nodes
test_contract_version_two_is_preserved

backend/app/test/test_trading_pipeline.py

test_trading_pipeline_success
test_trading_pipeline_blocked
test_agent_router_trips_kill_switch

frontend/tests/e2e/02-auth-boundary.spec.ts

login page loads with usable form controls
unauthenticated dashboard access is blocked
unauthenticated admin access is blocked

frontend/tests/e2e/03-public-navigation.spec.ts

homepage renders without browser errors
login page has no empty document
unknown route displays a controlled response

frontend/tests/e2e/04-backend-connectivity.spec.ts

backend documentation endpoint is reachable
backend OpenAPI contract is reachable
protected backend route rejects anonymous request

frontend/tests/e2e/05-authenticated-user-flow.spec.ts

register, login, persist session, and logout
/
/

frontend/tests/e2e/06-dashboard-navigation.spec.ts

/
dashboard, portfolio, and analytics render for a user

frontend/tests/e2e/07-neuro-welcome-briefing.spec.ts

authenticated user can view, close, and reopen the briefing
/

frontend/tests/e2e/08-objective4g-d-authenticated-live-turn.spec.ts

/
qualifies authenticated math, RAG, verification, and replay

frontend/tests/e2e/09-objective4h-b-broad-prompt-matrix.spec.ts

qualifies broad authenticated cognitive behavior

Manual Verification Checklist

[ ] Login with a valid existing user

[ ] Record the exact successful redirect destination

[ ] Open the dashboard directly with a valid session

[ ] Open the dashboard without a session

[ ] Open the dashboard with an expired access token

[ ] Verify refresh-session recovery

[ ] Open the dashboard with a revoked session

[ ] Verify the exact dashboard heading and visible layout

[ ] Verify every navigation item

[ ] Verify account identity and role display

[ ] Verify portfolio summary

[ ] Verify positions data

[ ] Verify analytics data

[ ] Verify market-data sections

[ ] Verify risk sections

[ ] Verify Neuro welcome briefing

[ ] Verify Neuro chat entry point

[ ] Verify loading state

[ ] Verify empty-portfolio state

[ ] Verify backend failure state

[ ] Verify partial data failure

[ ] Verify provider failure

[ ] Verify retry and refresh controls

[ ] Verify stale-data or last-updated indicators

[ ] Verify standard user cannot access admin pages

[ ] Verify standard user cannot access developer context

[ ] Verify user A cannot access user B data

[ ] Verify browser refresh preserves the session

[ ] Verify browser back-button behavior after logout

[ ] Verify desktop layout

[ ] Verify tablet layout

[ ] Verify mobile layout

[ ] Verify keyboard navigation

[ ] Verify screen-reader labels

[ ] Run authenticated dashboard Playwright tests

[ ] Capture desktop and mobile screenshots

Current Gaps

The exact successful login-to-dashboard redirect was not conclusively detected.

FUNCTION FLOW GRAPH

Existing User
      │
      ▼
Successful Login
      │
      ▼
Authentication Response
      │
      ▼
Session Cookie / Access State
      │
      ▼
Authenticated Redirect
      │
      ▼
GET /user/dashboard
      │
      ▼
frontend/proxy.ts
      │
      ▼
Validate Session
      │
      ├────────► Invalid Session
      │                 │
      │                 ▼
      │              /login
      │
      └────────► Valid Session
                        │
                        ▼
frontend/app/user/layout.tsx
                        │
                        ▼
frontend/app/user/dashboard/page.tsx
                        │
                        ▼
UserDashboardPage Component
                        │
                        ├────────► Navigation
                        ├────────► Account Summary
                        ├────────► Portfolio Value
                        ├────────► Positions
                        ├────────► Analytics
                        ├────────► Market Information
                        ├────────► Risk Information
                        ├────────► Neuro Briefing
                        └────────► Neuro Chat
                                         │
                                         ▼
                              Frontend Services / API Proxies
                                         │
                                         ▼
                               Authenticated Backend Routes
                                         │
                                         ▼
                              Authentication and Authorization
                                         │
                                         ▼
                                  Ownership Enforcement
                                         │
                                         ▼
                              Facades / Services / Repositories
                                         │
                                         ▼
                              Database and Provider Read Results
                                         │
                                         ▼
                                 Normalized API Responses
                                         │
                                         ▼
                                Frontend Component State
                                         │
                                         ▼
                                Rendered User Dashboard

Repository Files

Frontend

frontend/app/user/dashboard/page.tsx
frontend/app/user/layout.tsx
frontend/proxy.ts

Frontend Service and API Files

frontend/proxy.ts
frontend/services/riskService.ts
frontend/services/graphService.ts
frontend/services/marketService.ts
frontend/services/chatService.ts
frontend/services/strategyService.ts
frontend/services/backendHealthService.ts
frontend/services/portfolioService.ts
frontend/lib/sessionCookies.ts
frontend/tests/e2e/06-dashboard-navigation.spec.ts
frontend/tests/e2e/07-neuro-welcome-briefing.spec.ts
frontend/services/chat/chatContracts.ts
frontend/app/hooks/useDashboardData.ts
frontend/app/dashboard/layout.tsx
frontend/app/dashboard/page.tsx
frontend/app/admin/sessions/page.tsx
frontend/app/admin/user-dashboard/page.tsx
frontend/app/components/layout/DashboardShell.tsx
frontend/app/api/admin/users/route.ts
frontend/app/api/admin/users/[userId]/route.ts
frontend/app/api/admin/users/[userId]/require-password-reset/route.ts
frontend/app/api/admin/users/[userId]/enable/route.ts
frontend/app/api/admin/users/[userId]/disable/route.ts
frontend/app/api/admin/users/[userId]/temporary-password/route.ts
frontend/app/api/auth/session/route.ts
frontend/app/api/auth/change-password/route.ts
frontend/app/api/auth/logout/route.ts
frontend/app/api/auth/login/route.ts
frontend/app/api/v1/chat/route.ts
frontend/app/api/v1/analytics/route.ts
frontend/app/api/v1/positions/route.ts
frontend/app/api/v1/orders/route.ts
frontend/app/api/v1/graph/live/route.ts
frontend/app/api/v1/risk/gate/[symbol]/route.ts
frontend/app/api/v1/paper/orders/route.ts
frontend/app/api/v1/market/live-price/[symbol]/route.ts
frontend/app/api/v1/portfolio/lifecycle/route.ts
frontend/app/api/v1/portfolio/valuation/route.ts
frontend/app/api/v1/portfolio/positions/route.ts
frontend/app/api/v1/portfolio/refresh/route.ts
frontend/app/api/v1/strategy/decision/[symbol]/route.ts
frontend/app/user/components/NeuroWelcomeBriefing.tsx
frontend/app/user/dashboard/userWorkspaceTypes.ts
frontend/app/user/dashboard/page.tsx
frontend/app/user/dashboard/UserWorkspaceNavigation.tsx
frontend/app/user/dashboard/UserWorkspaceRouter.tsx

Backend Routes

backend/app/main.py
backend/app/stacks/chat_public/chat_api.py
backend/app/stacks/identity_auth/admin_mutation_router.py
backend/app/stacks/identity_auth/admin_read_router.py
backend/app/stacks/identity_auth/api_router.py
backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py
backend/app/stacks/market_data/api_router.py

Facades and Services

backend/app/spine/L5_api/owned_readonly_portfolio_service.py
backend/app/stacks/chat_public/tests/test_conversation_service_boundary.py
backend/app/stacks/identity_auth/admin_mutation_service.py
backend/app/stacks/identity_auth/login_service.py
backend/app/stacks/identity_auth/password_change_service.py
backend/app/stacks/identity_auth/registration_service.py
backend/app/stacks/identity_auth/service_contracts.py
backend/app/stacks/identity_auth/session_lifecycle_service.py
backend/app/stacks/identity_auth/session_service.py
backend/app/stacks/identity_auth/tests/test_login_service.py
backend/app/stacks/identity_auth/tests/test_registration_service.py
backend/app/stacks/journal_ledger/decision_audit_service.py
backend/app/stacks/portfolio/dashboard_service.py
backend/app/stacks/portfolio/facades/readonly_portfolio_facade.py
backend/app/stacks/portfolio/portfolio_service.py
backend/app/stacks/portfolio/tests/test_readonly_portfolio_facade.py
backend/app/stacks/wolfden_ai/portfolio_output_result_facade.py
backend/app/stacks/wolfden_ai/tests/test_portfolio_output_result_facade.py

Repositories

backend/app/stacks/chat_public/conversation_store.py
backend/app/stacks/chat_public/persistence/chat_models.py
backend/app/stacks/identity_auth/access_token_revocation_repository.py
backend/app/stacks/identity_auth/tests/test_identity_persistence_models.py
backend/app/stacks/identity_auth/tests/test_refresh_session_persistence.py
backend/app/stacks/identity_auth/tests/test_stage5b_a_durable_revocation_repository.py
backend/app/stacks/journal_ledger/decision_event_repository.py

Models

backend/app/stacks/chat_public/cognitive_model_router.py
backend/app/stacks/chat_public/persistence/chat_models.py
backend/app/stacks/chat_public/tests/test_cognitive_model_router.py
backend/app/stacks/db_runtime/model_registry.py
backend/app/stacks/identity_auth/__init__.py
backend/app/stacks/identity_auth/access_token_revocation_models.py
backend/app/stacks/identity_auth/access_token_revocation_repository.py
backend/app/stacks/identity_auth/admin_mutation_api_models.py
backend/app/stacks/identity_auth/admin_mutation_router.py
backend/app/stacks/identity_auth/admin_mutation_service.py
backend/app/stacks/identity_auth/admin_read_api_models.py
backend/app/stacks/identity_auth/admin_read_dependencies.py
backend/app/stacks/identity_auth/admin_read_models.py
backend/app/stacks/identity_auth/admin_read_router.py
backend/app/stacks/identity_auth/api_router.py
backend/app/stacks/identity_auth/authorization_policy.py
backend/app/stacks/identity_auth/dev_owner_provisioner.py
backend/app/stacks/identity_auth/login_service.py
backend/app/stacks/identity_auth/migrations/stage9d_a_identity_schema.py
backend/app/stacks/identity_auth/mock_runtime.py
backend/app/stacks/identity_auth/models.py
backend/app/stacks/identity_auth/password_change_service.py
backend/app/stacks/identity_auth/registration_service.py
backend/app/stacks/identity_auth/repositories.py
backend/app/stacks/identity_auth/revocation.py
backend/app/stacks/identity_auth/route_protection.py
backend/app/stacks/identity_auth/service_contracts.py
backend/app/stacks/identity_auth/session_introspection.py
backend/app/stacks/identity_auth/session_lifecycle_service.py
backend/app/stacks/identity_auth/session_service.py
backend/app/stacks/identity_auth/tests/test_api_route_contract.py
backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py
backend/app/stacks/identity_auth/tests/test_canonical_router_inclusion.py
backend/app/stacks/identity_auth/tests/test_display_name.py
backend/app/stacks/identity_auth/tests/test_identity_persistence_models.py
backend/app/stacks/identity_auth/tests/test_login_service.py
backend/app/stacks/identity_auth/tests/test_refresh_session_persistence.py
backend/app/stacks/identity_auth/tests/test_registration.py
backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py
backend/app/stacks/identity_auth/tests/test_registration_service.py
backend/app/stacks/identity_auth/tests/test_session_introspection.py
backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
backend/app/stacks/identity_auth/tests/test_stage4f_canonical_claim_propagation.py
backend/app/stacks/identity_auth/tests/test_stage4f_environment_token_issuer_contract.py
backend/app/stacks/identity_auth/tests/test_stage4f_login_refresh_claims.py
backend/app/stacks/identity_auth/tests/test_stage4f_mock_identity_contract.py
backend/app/stacks/identity_auth/tests/test_stage4f_rotated_refresh_claims.py
backend/app/stacks/identity_auth/tests/test_stage5b_a_durable_revocation_repository.py
backend/app/stacks/identity_auth/tests/test_stage5b_b_durable_bearer_logout.py
backend/app/stacks/identity_auth/tests/test_stage5b_c_revocation_observability_cleanup.py
backend/app/stacks/identity_auth/tests/test_stage9d_a_identity_schema.py
backend/app/stacks/identity_auth/tests/test_stage9d_b_forced_password_change.py
backend/app/stacks/identity_auth/tests/test_stage9d_c2_admin_read_models.py
backend/app/stacks/identity_auth/tests/test_stage9d_c5_b_admin_user_mutations.py
backend/app/stacks/identity_auth/tests/test_stage9d_c5_i_authorization_policy.py
backend/app/stacks/identity_auth/tests/test_stage9d_c5_j1_subscription_tier.py
backend/app/stacks/identity_auth/tests/test_stage9d_c5_k1_session_introspection.py
backend/app/stacks/journal_ledger/decision_event_model.py
backend/app/stacks/portfolio/read_models/readonly_portfolio_snapshot.py
backend/app/stacks/snaptrade/contracts/readonly_models.py
backend/app/stacks/wolfden_ai/tests/test_local_model_binding.py

Providers

backend/app/stacks/market_data/provider_contract.py
backend/app/stacks/market_data/provider_registry.py
backend/app/stacks/market_data/yfinance_provider.py
backend/app/stacks/snaptrade/providers/mock_provider.py

Tests

backend/app/stacks/chat_public/tests/test_authenticated_role_truth_boundary.py
backend/app/stacks/chat_public/tests/test_chat_intent_regex.py
backend/app/stacks/chat_public/tests/test_cognitive_model_router.py
backend/app/stacks/chat_public/tests/test_deterministic_math_engine.py
backend/app/stacks/chat_public/tests/test_live_math_runtime_integration.py
backend/app/stacks/chat_public/tests/test_live_rag_activation.py
backend/app/stacks/chat_public/tests/test_local_rag_index.py
backend/app/stacks/chat_public/tests/test_public_chat_controls.py
backend/app/stacks/chat_public/tests/test_role_overlay_injection.py
backend/app/stacks/db_runtime/tests/test_transaction_guard.py
backend/app/stacks/db_runtime/tests/test_transaction_manager.py
backend/app/stacks/identity_auth/tests/test_api_dependency.py
backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py
backend/app/stacks/identity_auth/tests/test_canonical_router_inclusion.py
backend/app/stacks/identity_auth/tests/test_display_name.py
backend/app/stacks/identity_auth/tests/test_identity_persistence_models.py
backend/app/stacks/identity_auth/tests/test_identity_repository.py
backend/app/stacks/identity_auth/tests/test_login_service.py
backend/app/stacks/identity_auth/tests/test_refresh_session_persistence.py
backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py
backend/app/stacks/identity_auth/tests/test_runtime_adapter.py
backend/app/stacks/identity_auth/tests/test_session_introspection.py
backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
backend/app/stacks/identity_auth/tests/test_stage4f_canonical_claim_propagation.py
backend/app/stacks/identity_auth/tests/test_stage4f_login_refresh_claims.py
backend/app/stacks/identity_auth/tests/test_stage4f_rotated_refresh_claims.py
backend/app/stacks/identity_auth/tests/test_stage4f_session_lifecycle_runtime_wiring.py
backend/app/stacks/identity_auth/tests/test_stage5b_a_durable_revocation_repository.py
backend/app/stacks/identity_auth/tests/test_stage5b_b_durable_bearer_logout.py
backend/app/stacks/identity_auth/tests/test_stage5b_c_revocation_observability_cleanup.py
backend/app/stacks/identity_auth/tests/test_stage9d_b_forced_password_change.py
backend/app/stacks/identity_auth/tests/test_stage9d_c2_admin_read_models.py
backend/app/stacks/identity_auth/tests/test_stage9d_c5_b_admin_user_mutations.py
backend/app/stacks/identity_auth/tests/test_stage9d_c5_k1_session_introspection.py
backend/app/stacks/journal_ledger/tests/test_decision_event_repository.py
backend/app/stacks/journal_ledger/tests/test_strategy_decision_audit_adapter.py
backend/app/stacks/market_data/tests/test_provider_contract.py
backend/app/stacks/market_data/tests/test_provider_runtime.py
backend/app/stacks/market_data/tests/test_stage8_runtime_qualification.py
backend/app/stacks/market_data/tests/test_yfinance_provider.py
backend/app/stacks/portfolio/tests/test_authenticated_owned_readonly_portfolio_api.py
backend/app/stacks/portfolio/tests/test_authenticated_paper_order_api.py
backend/app/stacks/portfolio/tests/test_authenticated_portfolio_read_boundary.py
backend/app/stacks/portfolio/tests/test_authenticated_portfolio_read_isolation.py
backend/app/stacks/portfolio/tests/test_authenticated_portfolio_valuation_api.py
backend/app/stacks/portfolio/tests/test_execution_ownership_propagation.py
backend/app/stacks/portfolio/tests/test_multi_owner_reconciliation_startup.py
backend/app/stacks/portfolio/tests/test_ownership_schema_enforcement.py
backend/app/stacks/portfolio/tests/test_portfolio_snapshot_lifecycle.py
backend/app/stacks/portfolio/tests/test_readonly_portfolio_facade.py
backend/app/stacks/portfolio/tests/test_reconciliation_ownership_isolation.py
backend/app/stacks/risk/tests/test_drawdown_guard_ledger_boundary.py
backend/app/stacks/snaptrade/tests/test_normalized_portfolio_ingestion.py
backend/app/stacks/snaptrade/tests/test_portfolio_owner_binding.py
backend/app/stacks/wolfden_ai/tests/test_observability_boundary.py
backend/app/stacks/wolfden_ai/tests/test_portfolio_output_result_facade.py
backend/app/test/test_graph_event_metrics.py
backend/app/test/test_stage8f_graph_materialization.py
backend/app/test/test_stage8f_historical_node_assignment.py
backend/app/test/test_trading_pipeline.py
frontend/tests/e2e/02-auth-boundary.spec.ts
frontend/tests/e2e/03-public-navigation.spec.ts
frontend/tests/e2e/04-backend-connectivity.spec.ts
frontend/tests/e2e/05-authenticated-user-flow.spec.ts
frontend/tests/e2e/06-dashboard-navigation.spec.ts
frontend/tests/e2e/07-neuro-welcome-briefing.spec.ts
frontend/tests/e2e/08-objective4g-d-authenticated-live-turn.spec.ts
frontend/tests/e2e/09-objective4h-b-broad-prompt-matrix.spec.ts

Evidence

runtime/system_inventory/function_path_04_authenticated_dashboard_20260730_015256/function_path_04_authenticated_dashboard_inventory.json
runtime/system_inventory/function_path_04_authenticated_dashboard_20260730_015256/function_path_04_copy_paste_section.txt
runtime/system_inventory/function_path_04_authenticated_dashboard_20260730_015256/source

Launch Dependency

Required Before Launch

YES

Blocks

Authenticated application access

Portfolio viewing

Position viewing

Analytics

Neuro briefing

Neuro chat

Settings

Paper trading

Controlled early-user launch

Depends On

Existing-user login

Session validation

Access-token handling

Refresh-session recovery

Frontend middleware

Authenticated API proxies

Backend authentication

Authorization

Ownership isolation

Portfolio services

Database connectivity

Market-data providers

Error handling

FINAL VERDICT

Function Exists: YES

Frontend Complete: UNVERIFIED

Login Redirect Connected: UNVERIFIED

Middleware Present: YES

Authentication Protection: DETECTED

Unauthenticated Redirect: UNVERIFIED

Backend Routes Present: YES

Ownership Enforcement: DETECTED

Authorization: DETECTED

Read-Only Boundaries: DETECTED

Loading State: DETECTED

Error State: DETECTED

Empty State: DETECTED

Relevant Tests: PRESENT

Live Verification: NOT COMPLETE

Launch Ready: UNVERIFIED

Overall Classification

PARTIALLY VERIFIED

Launch Classification

CRITICAL

The authenticated dashboard must be fully verified before launch
because it is the first protected application surface reached by
standard users and provides access to nearly every core NeuroVest
feature.

---



---

FUNCTION PATH 05 — PORTFOLIO

Function Status

Inventory Status: INITIAL INVENTORY COMPLETE
Implementation Status: IMPLEMENTED — SOURCE VERIFICATION PENDING
Qualification Status: UNVERIFIED
Launch Importance: CRITICAL
Last Updated: 2026-07-30
Evidence Source: runtime/system_inventory/function_path_05_portfolio_20260730_142919/function_path_05_portfolio_inventory.json

Purpose

The Portfolio function presents the authenticated user's owned
accounts, balances, positions, valuations, refresh state, and
portfolio-derived information.

Its purpose is to:

- Require an authenticated user session.
- Load only portfolio data owned by the authenticated user.
- Retrieve portfolio accounts, balances, positions, and totals.
- Calculate or retrieve portfolio valuation.
- Present cost basis, market value, and gain or loss information.
- Support controlled portfolio refresh operations.
- Distinguish stored, provider, stale, and unavailable data.
- Present loading, empty, retry, and failure states.
- Prevent cross-user access to portfolio information.
- Remain read-only except for controlled refresh or paper operations.

User Journey

Authenticated User
      │
      ▼
GET /user/dashboard
      │
      ▼
frontend/proxy.ts
      │
      ▼
Authentication and Route Protection
      │
      ├────────► Invalid Session
      │                 │
      │                 ▼
      │              /login
      │
      └────────► Valid Session
                        │
                        ▼
frontend/app/user/dashboard/page.tsx
                        │
                        ▼
UserDashboardPage()
                        │
                        ▼
               Portfolio Data Requests
                        │
          ┌─────────────┼─────────────┐
          │             │             │
          ▼             ▼             ▼
       Accounts      Balances      Positions
          │             │             │
          └─────────────┼─────────────┘
                        │
                        ▼
                  Portfolio Totals
                        │
                        ▼
                   Valuation State
                        │
                        ├────────► Empty State
                        ├────────► Loading State
                        ├────────► Stale State
                        ├────────► Error State
                        └────────► Refresh

Entry Point

Browser Route

/user/dashboard

Dedicated Portfolio Page

UNKNOWN

Dashboard Portfolio Surface

frontend/app/user/dashboard/page.tsx

Selected Entry File

frontend/app/user/dashboard/page.tsx

Route Type

AUTHENTICATED

Authentication Required

YES

Frontend

Root Component

UserDashboardPage

Component Type

Client Component

Layout

frontend/app/user/layout.tsx

Middleware

frontend/proxy.ts

Loading File

UNKNOWN

Error Page

UNKNOWN

404 Page

UNKNOWN

Portfolio Pages Detected

No dedicated portfolio page detected.

Visible Layout

P

Total portfolio value

Source: frontend/app/user/dashboard/page.tsx:567

P

Holdings snapshot

Source: frontend/app/user/dashboard/page.tsx:644

H2

Your current positions

Source: frontend/app/user/dashboard/page.tsx:648

BUTTON

} className="nv-button nv-button-secondary" > View portfolio

Source: frontend/app/user/dashboard/page.tsx:653

SPAN

Cost basis

Source: frontend/app/user/dashboard/page.tsx:699

P

Portfolio

Source: frontend/app/user/dashboard/page.tsx:770

P

Review valuation, cost basis, exposure, realized results, and analytics.

Source: frontend/app/user/dashboard/page.tsx:778

P

Portfolio valuation

Source: frontend/app/user/dashboard/page.tsx:794

H2

Capital and account value

Source: frontend/app/user/dashboard/page.tsx:798

P

Cash is reconstructed from this account's authenticated order ledger. Open positions are currently valued at cost basis until qualified live market marking is added.

Source: frontend/app/user/dashboard/page.tsx:802

P

Account value at cost

Source: frontend/app/user/dashboard/page.tsx:855

P

Your portfolio

Source: frontend/app/user/dashboard/page.tsx:914

H2

Personal paper positions

Source: frontend/app/user/dashboard/page.tsx:918

P

Cost basis

Source: frontend/app/user/dashboard/page.tsx:1001

P

Total realized P/L

Source: frontend/app/user/dashboard/page.tsx:1102

P

Orders, positions, and analytics are scoped to the currently authenticated account. Paper orders pass through NeuroVest risk, accounting, execution, and ledger boundaries without enabling a live broker.

Source: frontend/app/user/dashboard/page.tsx:1330

P

Read-only watchlist, live quote refresh, active universe, and replay-focused CAD symbols.

Source: frontend/app/components/workspaces/MarketWorkspace.tsx:126

P

Portfolio, markets, orders, history, strategies, and account options.

Source: frontend/app/user/dashboard/UserWorkspaceNavigation.tsx:31

P

Your authenticated paper-trading workspace is ready. Portfolio records, order activity, account valuation, and analytics remain isolated to your account.

Source: frontend/app/user/components/NeuroWelcomeBriefing.tsx:313

LABEL

} className="mt-1 h-4 w-4 accent-cyan-400" /> Don't show this briefing automatically again. You can still reopen it from the workspace.

Source: frontend/app/user/components/NeuroWelcomeBriefing.tsx:376

Frontend Components

T [frontend/app/user/dashboard/page.tsx:176]
T [frontend/app/user/dashboard/page.tsx:179]
DashboardState [frontend/app/user/dashboard/page.tsx:191]
UserWorkspaceId [frontend/app/user/dashboard/page.tsx:207]
SessionPayload [frontend/app/user/dashboard/page.tsx:290]
PositionsPayload [frontend/app/user/dashboard/page.tsx:317]
OrdersPayload [frontend/app/user/dashboard/page.tsx:325]
AnalyticsPayload [frontend/app/user/dashboard/page.tsx:333]
PortfolioValuationPayload [frontend/app/user/dashboard/page.tsx:339]
WorkspacePage [frontend/app/user/dashboard/page.tsx:525]
PageHeader [frontend/app/user/dashboard/page.tsx:529]
StatusBadge [frontend/app/user/dashboard/page.tsx:534]
UserWorkspaceNavigation [frontend/app/user/dashboard/page.tsx:555]
UserWorkspaceRouter [frontend/app/user/dashboard/page.tsx:561]
StatusBadge [frontend/app/user/dashboard/page.tsx:576]
StatCard [frontend/app/user/dashboard/page.tsx:604]
StatCard [frontend/app/user/dashboard/page.tsx:612]
StatusMessage [frontend/app/user/dashboard/page.tsx:665]
StatusBadge [frontend/app/user/dashboard/page.tsx:756]
MarketWorkspace [frontend/app/user/dashboard/page.tsx:761]
StatusBadge [frontend/app/user/dashboard/page.tsx:783]
Panel [frontend/app/user/dashboard/page.tsx:788]
StatusBadge [frontend/app/user/dashboard/page.tsx:809]
Panel [frontend/app/user/dashboard/page.tsx:908]
StatusBadge [frontend/app/user/dashboard/page.tsx:923]
StatusMessage [frontend/app/user/dashboard/page.tsx:933]
StatusBadge [frontend/app/user/dashboard/page.tsx:961]
UserWorkspaceId [frontend/app/user/dashboard/UserWorkspaceRouter.tsx:31]
PortfolioPositionsResponse [frontend/services/portfolioService.ts:45]
PortfolioSnapshotLifecycle [frontend/services/portfolioService.ts:155]
PortfolioSnapshotLifecycle [frontend/services/portfolioService.ts:188]

Frontend Handlers

formatMoney
Type: function
Source: frontend/app/user/dashboard/page.tsx:119

formatNumber
Type: function
Source: frontend/app/user/dashboard/page.tsx:137

formatDate
Type: function
Source: frontend/app/user/dashboard/page.tsx:154

UserDashboardPage
Type: function
Source: frontend/app/user/dashboard/page.tsx:187

LiveMarketWatchlist
Type: function
Source: frontend/app/components/workspaces/MarketWorkspace.tsx:45

MarketWorkspace
Type: function
Source: frontend/app/components/workspaces/MarketWorkspace.tsx:115

UserWorkspaceNavigation
Type: function
Source: frontend/app/user/dashboard/UserWorkspaceNavigation.tsx:15

UserWorkspaceRouter
Type: function
Source: frontend/app/user/dashboard/UserWorkspaceRouter.tsx:20

cleanName
Type: function
Source: frontend/app/user/components/NeuroWelcomeBriefing.tsx:39

emailPrefix
Type: function
Source: frontend/app/user/components/NeuroWelcomeBriefing.tsx:56

formatDisplayName
Type: function
Source: frontend/app/user/components/NeuroWelcomeBriefing.tsx:74

greetingForHour
Type: function
Source: frontend/app/user/components/NeuroWelcomeBriefing.tsx:89

NeuroWelcomeBriefing
Type: function
Source: frontend/app/user/components/NeuroWelcomeBriefing.tsx:103

closeBriefing
Type: function
Source: frontend/app/user/components/NeuroWelcomeBriefing.tsx:204

isRecord
Type: function
Source: frontend/services/portfolioService.ts:35

getPortfolioPositions
Type: function
Source: frontend/services/portfolioService.ts:45

getPortfolioSnapshotLifecycle
Type: function
Source: frontend/services/portfolioService.ts:155

refreshPortfolioSnapshot
Type: function
Source: frontend/services/portfolioService.ts:188

Frontend Requests

GET "/api/auth/session"
Request Type: fetch
Credentials Mode: include
Source: frontend/app/user/dashboard/page.tsx:232

GET "/api/v1/portfolio/positions"
Request Type: fetch
Credentials Mode: include
Source: frontend/services/portfolioService.ts:46

POST "/api/v1/portfolio/refresh"
Request Type: fetch
Credentials Mode: include
Source: frontend/services/portfolioService.ts:189

Frontend Service and API Files

frontend/services/portfolioService.ts
Methods: ['GET', 'POST']
Targets: ['/api/v1/portfolio/lifecycle', '/api/v1/portfolio/positions', '/api/v1/portfolio/refresh']
Credentials Include: True

frontend/services/chat/chatContracts.ts
Methods: []
Targets: []
Credentials Include: False

frontend/app/components/cards/PositionsPanel.tsx
Methods: []
Targets: []
Credentials Include: False

frontend/app/api/auth/register/route.ts
Methods: ['POST']
Targets: []
Credentials Include: False

frontend/app/api/auth/session/route.ts
Methods: ['GET']
Targets: []
Credentials Include: False

frontend/app/api/auth/logout/route.ts
Methods: ['POST']
Targets: []
Credentials Include: False

frontend/app/api/auth/login/route.ts
Methods: ['GET', 'POST']
Targets: []
Credentials Include: False

frontend/app/api/v1/positions/route.ts
Methods: ['GET']
Targets: ['/api/v1/positions']
Credentials Include: False

frontend/app/api/v1/portfolio/lifecycle/route.ts
Methods: ['GET']
Targets: ['/api/v1/portfolio/readonly/lifecycle']
Credentials Include: False

frontend/app/api/v1/portfolio/valuation/route.ts
Methods: ['GET']
Targets: ['/api/v1/portfolio/valuation']
Credentials Include: False

frontend/app/api/v1/portfolio/positions/route.ts
Methods: ['GET']
Targets: ['/api/v1/portfolio/readonly/positions']
Credentials Include: False

frontend/app/api/v1/portfolio/refresh/route.ts
Methods: ['POST']
Targets: ['/api/v1/portfolio/readonly/refresh']
Credentials Include: False

Frontend Event Flow

User opens the portfolio surface

↓

Frontend verifies authenticated session

↓

Portfolio request begins

↓

Loading state displayed

↓

Backend validates authentication

↓

Backend derives authenticated ownership scope

↓

Portfolio service loads accounts, balances, positions, and totals

↓

Valuation and gain or loss information is normalized

↓

Portfolio response returns

↓

No owned positions
    → Empty portfolio state

Owned positions available
    → Position and valuation components render

Request failure
    → Portfolio error state
    → Retry or refresh remains available where safe

Middleware

File

frontend/proxy.ts

Status

PRESENT

Portfolio Mentions

0

Known Cookies

neurovest_access
neurovest_csrf
neurovest_session

Known Headers

Cache-Control
host
origin
x-forwarded-host
x-forwarded-proto
x-neurovest-csrf

Protection Markers

/login, access, authenticated, csrf, pathname, protected, redirect, session

Backend Routes

GET /api/v1/graph/live

Function

get_live_graph

File

backend/app/main.py

Source Line

204

Markers

Depends, authenticated, balance, owner, snapshot, valuation

GET /api/v1/dashboard/summary

Function

summary

File

backend/app/main.py

Source Line

209

Markers

Depends, authenticated, balance, snapshot, valuation

POST /api/v1/sandbox/signal

Function

set_sandbox_override

File

backend/app/main.py

Source Line

399

Markers

Depends, authenticated, balance, portfolio, user_id, valuation

POST /api/v1/sandbox/audit

Function

trigger_sandbox_audit

File

backend/app/main.py

Source Line

420

Markers

Depends, authenticated, balance, portfolio, user_id, valuation

POST /api/v1/admin/backup

Function

force_system_backup

File

backend/app/main.py

Source Line

435

Markers

Depends, authenticated, balance, portfolio, position, user_id, valuation

GET /api/v1/portfolio/valuation

Function

get_authenticated_portfolio_valuation

File

backend/app/main.py

Source Line

462

Markers

Depends, authenticated, balance, portfolio, position, user_id, valuation

GET /api/v1/positions

Function

get_active_positions

File

backend/app/main.py

Source Line

525

Markers

Depends, authenticated, portfolio, position, user_id, valuation

GET /api/v1/orders

Function

get_orders

File

backend/app/main.py

Source Line

563

Markers

Depends, authenticated, position, user_id

GET /api/v1/analytics

Function

get_analytics

File

backend/app/main.py

Source Line

595

Markers

Depends, authenticated, balance, portfolio, user_id

POST /api/v1/paper/orders

Function

submit_authenticated_paper_order

File

backend/app/main.py

Source Line

647

Markers

Depends, authenticated, balance, owner, portfolio, position, user_id

GET /api/v1/market/live-price/{symbol}

Function

api_live_market_price

File

backend/app/main.py

Source Line

706

Markers

Depends, authenticated, balance, owner, portfolio, position, readonly, user_id

GET /api/v1/portfolio/positions

Function

api_portfolio_positions

File

backend/app/main.py

Source Line

711

Markers

Depends, authenticated, balance, owner, portfolio, position, readonly, user_id

GET /api/v1/strategy/decision/{symbol}

Function

api_strategy_decision

File

backend/app/main.py

Source Line

722

Markers

Depends, authenticated, balance, owner, portfolio, position, readonly, user_id

GET /api/v1/risk/gate/{symbol}

Function

api_risk_gate

File

backend/app/main.py

Source Line

727

Markers

Depends, authenticated, balance, owner, portfolio, position, read_only, readonly, user_id

GET /api/v1/portfolio/readonly

Function

authenticated_owned_portfolio_overview

File

backend/app/main.py

Source Line

796

Markers

Depends, authenticated, balance, portfolio, position, read_only, readonly, user_id

GET /api/v1/portfolio/readonly/accounts

Function

authenticated_owned_portfolio_accounts

File

backend/app/main.py

Source Line

819

Markers

Depends, authenticated, balance, owner, portfolio, position, read_only, readonly

GET /api/v1/portfolio/readonly/balances

Function

authenticated_owned_portfolio_balances

File

backend/app/main.py

Source Line

839

Markers

Depends, authenticated, balance, owner, portfolio, position, read_only, readonly, refresh, snapshot

GET /api/v1/portfolio/readonly/positions

Function

authenticated_owned_portfolio_positions

File

backend/app/main.py

Source Line

859

Markers

Depends, authenticated, balance, owner, portfolio, position, read_only, readonly, refresh, snapshot, user_id

GET /api/v1/portfolio/readonly/positions/{symbol}

Function

authenticated_owned_portfolio_symbol_positions

File

backend/app/main.py

Source Line

879

Markers

Depends, authenticated, balance, owner, portfolio, position, read_only, readonly, refresh, snapshot, user_id

GET /api/v1/portfolio/readonly/totals

Function

authenticated_owned_portfolio_totals

File

backend/app/main.py

Source Line

902

Markers

Depends, authenticated, owner, portfolio, position, read_only, readonly, refresh, snapshot, user_id

GET /api/v1/portfolio/readonly/lifecycle

Function

authenticated_portfolio_snapshot_lifecycle

File

backend/app/main.py

Source Line

933

Markers

Depends, authenticated, owner, portfolio, read_only, readonly, refresh, snapshot, user_id

POST /api/v1/portfolio/readonly/refresh

Function

authenticated_portfolio_snapshot_refresh

File

backend/app/main.py

Source Line

964

Markers

Depends, authenticated, portfolio, readonly, refresh, snapshot, user_id

POST /register

Function

register_identity

File

backend/app/stacks/identity_auth/api_router.py

Source Line

112

Markers

Depends, refresh, user_id

POST /login

Function

login_identity

File

backend/app/stacks/identity_auth/api_router.py

Source Line

157

Markers

Depends, authenticated, refresh

POST /change-required-password

Function

change_required_password

File

backend/app/stacks/identity_auth/api_router.py

Source Line

235

Markers

Depends, authenticated, refresh, user_id

POST /refresh

Function

refresh_session

File

backend/app/stacks/identity_auth/api_router.py

Source Line

282

Markers

Depends, refresh, user_id

POST /logout

Function

logout_session

File

backend/app/stacks/identity_auth/api_router.py

Source Line

351

Markers

Depends, authenticated, refresh, user_id

POST /logout-all

Function

logout_all_sessions

File

backend/app/stacks/identity_auth/api_router.py

Source Line

428

Markers

Depends, authenticated, refresh, user_id

GET /status

Function

market_data_status

File

backend/app/stacks/market_data/api_router.py

Source Line

102

Markers

position, read_only

Backend Function Path

graph_ws
File: backend/app/api/graph_ws.py
Lines: 11-21
Matched Terms: snapshot
Calls: asyncio.sleep, connected.add, connected.remove, graph_state.snapshot, router.websocket, ws.accept, ws.send_json

__init__
File: backend/app/core/cognitive_graph_state.py
Lines: 1362-1380
Matched Terms: snapshot
Calls: RLock, defaultdict, self.load_snapshot

save_snapshot
File: backend/app/core/cognitive_graph_state.py
Lines: 1467-1479
Matched Terms: snapshot
Calls: SNAPSHOT_FILE.with_suffix, json.dumps, self.snapshot, temporary.replace, temporary.write_text

load_snapshot
File: backend/app/core/cognitive_graph_state.py
Lines: 1481-1536
Matched Terms: snapshot
Calls: SNAPSHOT_FILE.exists, SNAPSHOT_FILE.read_text, data.get, data.get('edges', {}).items, defaultdict, event.get, int, json.loads, key.split, len, max, print, self._reconcile_declared_node_ownership

activate_node
File: backend/app/core/cognitive_graph_state.py
Lines: 1568-1709
Matched Terms: snapshot
Calls: NODE_ARCHITECTURE.get, dict, int, known_ownership.get, meta.get, new_trace_id, now, payload.get, self._architecture_for, self._next_sequence, self._store_event, self._store_flow_step, self.node_meta.get, self.save_snapshot, str, update_metric_contract

activate_edge
File: backend/app/core/cognitive_graph_state.py
Lines: 1828-1972
Matched Terms: snapshot
Calls: any, dict, edge_metrics.update, new_trace_id, now, payload.get, self._architecture_for, self._materialize_edge_endpoint, self._next_sequence, self._store_event, self._store_flow_step, self.edge_meta.get, self.save_snapshot, str, update_metric_contract

snapshot
File: backend/app/core/cognitive_graph_state.py
Lines: 2032-2355
Matched Terms: snapshot
Calls: NODE_ARCHITECTURE.get, NODE_ARCHITECTURE.items, bool, canonical_ownership.get, destination_ownership.get, dict, existing.update, int, len, materialized_edge_meta.get, materialized_node_meta.get, materialized_node_meta.values, meta.get, now, ownership.get, self.edge_activity.items, self.edge_meta.items, self.node_meta.items, self.node_state.items, self.recent_trace_groups, source_ownership.get, sum

request_architecture_plan
File: backend/app/llm_bridge/cognition_core.py
Lines: 736-961
Matched Terms: gain
Calls: '; '.join, '\n- '.join, '\nYou are NeuroVest\'s repository architecture planner.\n\nYou receive verified evidence from the current repository.\n\nCritical, degraded, unstable, or high-risk evidence is a reason to\nproduce a remediation plan. It is never a reason to reject planning.\n\nTARGET RULES:\n- Select targets only by target_id.\n- Valid target IDs are listed in candidate_targets.\n- Never write or invent a repository path.\n- Never use a path in findings, ordered_steps, or simulation expectations.\n- Python will resolve target IDs into verified paths after your response.\n- Do not return an error object.\n- Keep safe_to_apply false because no patch has been generated or tested.\n\nProduce one focused remediation sequence for the highest-value subsystem.\n\nReturn JSON only with this exact structure:\n{\n  "goal": "string",\n  "current_state": ["string"],\n  "findings": [\n    {\n      "severity": "critical|high|medium|low",\n      "target_id": "T01",\n      "evidence": "string"\n    }\n  ],\n  "ordered_steps": [\n    {\n      "step": 1,\n      "action": "inspect|test|refactor|move|split|wire|remove",\n      "target_id": "T01",\n      "reason": "string",\n      "expected_effect": "string",\n      "verification": ["command or check"]\n    }\n  ],\n  "simulation_expectations": {\n    "target_ids": ["T01"],\n    "acceptable_affected_ratio": 0.25,\n    "required_checks": ["string"]\n  },\n  "safe_to_apply": false,\n  "apply_reason": "string"\n}\n'.strip, '\nYour previous response failed validation:\n\n- {errors}\n\nReturn the complete JSON plan again.\n\nUse only target IDs listed in candidate_targets.\nNever write repository paths.\nDo not invent target IDs.\nKeep safe_to_apply false.\nDo not return an error object.\n'.format, '\nYour previous response failed validation:\n\n- {errors}\n\nReturn the complete JSON plan again.\n\nUse only target IDs listed in candidate_targets.\nNever write repository paths.\nDo not invent target IDs.\nKeep safe_to_apply false.\nDo not return an error object.\n'.format(errors='\n- '.join(first_errors)).strip, ValueError, _extract_json_object, _ollama_json_request, _resolve_planner_target_ids, _validate_architecture_plan, analysis.get, call_planner, candidate_evidence.append, content.strip, enumerate, isinstance, item.get, json.dumps, messages.append, response.get, response.get('message', {}).get, select_ollama_model, set, str, target_map.values, zip

get_live_graph
File: backend/app/main.py
Lines: 205-206
Matched Terms: snapshot
Calls: app.get, graph_state.snapshot

summary
File: backend/app/main.py
Lines: 210-396
Matched Terms: balance, portfolio, valuation
Calls: Depends, StrategyDecisionAuditAdapter, app.get, async_session, audit_adapter.produce_and_audit, build_decision_audit_service, create_trace_id, decision.get, dict, emit_runtime_step, execution_results.append, process_portfolio_output, str, type, uuid5

get_authenticated_portfolio_valuation
File: backend/app/main.py
Lines: 463-522
Matched Terms: balance, portfolio, valuation
Calls: Depends, app.get, calculate_live_portfolio_equity, float, round, str, valuation.get

get_active_positions
File: backend/app/main.py
Lines: 526-560
Matched Terms: cost_basis, portfolio, position, positions, realized
Calls: Depends, app.get, async_session, len, pos.last_updated.isoformat, result.scalars, result.scalars().all, round, select, select(PortfolioInventory).where, session.execute

submit_authenticated_paper_order
File: backend/app/main.py
Lines: 648-691
Matched Terms: balance, portfolio
Calls: Depends, app.post, create_trace_id, process_portfolio_output

api_portfolio_positions
File: backend/app/main.py
Lines: 712-719
Matched Terms: portfolio, position, positions
Calls: Depends, app.get, get_portfolio_positions_for_api

_owned_portfolio_facade_for_principal
File: backend/app/main.py
Lines: 771-793
Matched Terms: portfolio
Calls: HTTPException, build_owned_facade, str

authenticated_owned_portfolio_overview
File: backend/app/main.py
Lines: 800-816
Matched Terms: portfolio
Calls: Depends, _owned_portfolio_facade_for_principal, app.get, serialize_overview

authenticated_owned_portfolio_accounts
File: backend/app/main.py
Lines: 823-836
Matched Terms: portfolio
Calls: Depends, _owned_portfolio_facade_for_principal, app.get, serialize_accounts

authenticated_owned_portfolio_balances
File: backend/app/main.py
Lines: 843-856
Matched Terms: balance, balances, portfolio
Calls: Depends, _owned_portfolio_facade_for_principal, app.get, serialize_balances

authenticated_owned_portfolio_positions
File: backend/app/main.py
Lines: 863-876
Matched Terms: portfolio, position, positions
Calls: Depends, _owned_portfolio_facade_for_principal, app.get, serialize_positions

authenticated_owned_portfolio_symbol_positions
File: backend/app/main.py
Lines: 883-899
Matched Terms: portfolio, position, positions
Calls: Depends, _owned_portfolio_facade_for_principal, app.get, serialize_symbol_positions, symbol.strip, symbol.strip().upper

authenticated_owned_portfolio_totals
File: backend/app/main.py
Lines: 906-919
Matched Terms: portfolio
Calls: Depends, _owned_portfolio_facade_for_principal, app.get, serialize_totals

authenticated_portfolio_snapshot_lifecycle
File: backend/app/main.py
Lines: 937-961
Matched Terms: portfolio, snapshot
Calls: Depends, HTTPException, app.get, get_portfolio_lifecycle, str

authenticated_portfolio_snapshot_refresh
File: backend/app/main.py
Lines: 968-999
Matched Terms: portfolio, refresh, snapshot
Calls: Depends, HTTPException, app.post, refresh_portfolio_snapshot, str

find_latest_normalized_portfolio
File: backend/app/spine/L5_api/owned_readonly_portfolio_service.py
Lines: 45-64
Matched Terms: portfolio, snapshot
Calls: AuthenticatedPortfolioUnavailable, Path, Path('runtime/snaptrade_integration').glob, path.stat, sorted

build_owned_snapshot
File: backend/app/spine/L5_api/owned_readonly_portfolio_service.py
Lines: 99-291
Matched Terms: balance, balances, cost_basis, gain, portfolio, position, positions, realized, snapshot, unrealized
Calls: AuthenticatedPortfolioAccessDenied, AuthenticatedPortfolioUnavailable, Path, ReadOnlyPortfolioTotals, _sum_optional, filter_owned_accounts, find_latest_normalized_portfolio, ingest_normalized_portfolio, len, replace, set, sorted, str, str(neurovest_user_id).strip, sum, tuple

build_owned_facade
File: backend/app/spine/L5_api/owned_readonly_portfolio_service.py
Lines: 294-310
Matched Terms: portfolio, snapshot
Calls: ReadOnlyPortfolioFacade, build_owned_snapshot

serialize_overview
File: backend/app/spine/L5_api/owned_readonly_portfolio_service.py
Lines: 355-362
Matched Terms: portfolio
Calls: _json_safe, asdict, facade.get_overview

serialize_accounts
File: backend/app/spine/L5_api/owned_readonly_portfolio_service.py
Lines: 365-375
Matched Terms: portfolio
Calls: _json_safe, asdict, facade.list_accounts

serialize_positions
File: backend/app/spine/L5_api/owned_readonly_portfolio_service.py
Lines: 378-388
Matched Terms: portfolio, position, positions
Calls: _json_safe, asdict, facade.list_positions

serialize_symbol_positions
File: backend/app/spine/L5_api/owned_readonly_portfolio_service.py
Lines: 391-404
Matched Terms: portfolio, position, positions
Calls: _json_safe, asdict, facade.find_positions_by_symbol

serialize_balances
File: backend/app/spine/L5_api/owned_readonly_portfolio_service.py
Lines: 407-423
Matched Terms: balance, balances, portfolio
Calls: _json_safe, asdict, facade.list_balances

serialize_totals
File: backend/app/spine/L5_api/owned_readonly_portfolio_service.py
Lines: 426-433
Matched Terms: portfolio
Calls: _json_safe, asdict, facade.get_totals

_required_arguments
File: backend/app/stacks/chat_public/capability_state_registry.py
Lines: 251-270
Matched Terms: position
Calls: inspect.signature, signature.parameters.values

detect_chat_intent
File: backend/app/stacks/chat_public/chat_intent_regex.py
Lines: 236-392
Matched Terms: portfolio, valuation
Calls: COMMAND_PATTERNS.items, ChatIntent, SOFTWARE_DEBUG_REQUEST_PATTERN.search, _extract_symbol, match.group, match.group(2).upper, message.strip, pattern.search

handle_chat_message
File: backend/app/stacks/chat_public/chat_runtime.py
Lines: 159-360
Matched Terms: valuation
Calls: ask_ollama, build_developer_response, capture_strategy_proposal, detect_chat_intent, route_cognitive_request, routing_decision.as_dict, str, type

run_chat_turn
File: backend/app/stacks/chat_public/chat_runtime.py
Lines: 385-1586
Matched Terms: valuation
Calls: '\n- '.join, (math_bundle.result or {}).get, ChatRequest, ChatRequest.model_validate, ChatResponse, ToolEvidence, _ensure_approved_retrieval_citation, _find_existing_assistant_reply, _response_message, assemble_chat_context, assistant_content.encode, bool, citation.get, conversation_store.add_tool_evidence, conversation_store.append_message, conversation_store.get_conversation_state, conversation_store.get_message_by_client_id, conversation_store.get_or_create_thread, create_trace_id, current_turn_evidence.append, detect_chat_intent, dict, emit_runtime_step, evaluate_live_math, handle_chat_message, isinstance, kwargs.get, kwargs.pop, len, list, perf_counter, render_role_overlay, request.message.encode, resolve_principal_overlay, resolve_role_overlay, response.model_dump, retrieve_live_evidence, route_cognitive_request, runtime_result.get, runtime_result['response'].get, str, str(citation.get('citation', '')).strip, update_summary_memory, verification_result.as_dict, verify_response, violation.as_dict

route_cognitive_request
File: backend/app/stacks/chat_public/cognitive_model_router.py
Lines: 184-340
Matched Terms: portfolio
Calls: CognitiveRoutingDecision, _matches, bool, getattr, str, str(getattr(intent, 'family', 'GENERAL') or 'GENERAL').upper, str(message).strip

_build_intent_overlay
File: backend/app/stacks/chat_public/context/context_assembler.py
Lines: 163-529
Matched Terms: snapshot, valuation
Calls: _bounded, _compact_json, _safe_loader, bool, component_overlay.get, dashboard.get, dependency_graph.get, dict, isinstance, len, load_repo_context, metadata.get, repo_component_hotspots, repo_hotspots, sections.append, sections.extend, str, str(metadata.get('family', 'GENERAL')).upper

assemble_chat_context
File: backend/app/stacks/chat_public/context/context_assembler.py
Lines: 532-662
Matched Terms: gain, portfolio, position
Calls: AssembledChatContext, _bounded, _build_intent_overlay, _clean_text, _compact_json, _format_evidence, _format_memories, _format_recent_messages, compose_prompt, conversation_store.load_context_bundle, dict, len, sections.insert

extract_portfolio_context
File: backend/app/stacks/chat_public/context/context_assembler.py
Lines: 700-754
Matched Terms: portfolio
Calls: _clean_text, float, match.group, match.group(1).replace, match.group(2).upper, pattern.search, re.compile

build_summary
File: backend/app/stacks/chat_public/context/context_assembler.py
Lines: 802-882
Matched Terms: portfolio
Calls: ' '.join, ', '.join, _bounded, _clean_text, active_strategy.get, deduplicated.append, portfolio_context.get, remembered_terms.items, sorted, summary_lines.append

update_summary_memory
File: backend/app/stacks/chat_public/context/context_assembler.py
Lines: 885-1004
Matched Terms: portfolio
Calls: ConversationState, MemoryFact, build_summary, conversation_store.get_conversation_state, conversation_store.upsert_conversation_state, conversation_store.upsert_memory_fact, dict, extract_portfolio_context, extract_remembered_terms, extract_strategy_context, extracted_terms.items

_state_contract
File: backend/app/stacks/chat_public/conversation_store.py
Lines: 95-121
Matched Terms: portfolio
Calls: ConversationState, dict, list

create_thread
File: backend/app/stacks/chat_public/conversation_store.py
Lines: 160-222
Matched Terms: portfolio
Calls: ChatThread, ChatThreadRecord, ConversationStateRecord, async_session, self.get_thread, session.add, session.begin, session.rollback

append_message
File: backend/app/stacks/chat_public/conversation_store.py
Lines: 273-411
Matched Terms: portfolio
Calls: ChatMessage, ChatMessageRecord, ConversationStateRecord, LookupError, ValueError, async_session, content.strip, int, list, self.get_message, self.get_message_by_client_id, self.require_thread, session.add, session.begin, session.get, utc_now

upsert_conversation_state
File: backend/app/stacks/chat_public/conversation_store.py
Lines: 513-580
Matched Terms: portfolio
Calls: ConversationStateRecord, async_session, dict, hasattr, self.get_conversation_state, self.require_thread, session.add, session.begin, session.get, task.model_dump, utc_now

build_developer_response
File: backend/app/stacks/chat_public/developer_response_builder.py
Lines: 105-463
Matched Terms: portfolio, refresh, valuation
Calls: ', '.join, '; '.join, _bullet_lines, _hotspot_names, _integer, _safe_load, architecture.get, bool, capability_registry.get, capability_summary_lines, component_overlay.get, dependency_graph.get, isinstance, len, limitations.append, load_repo_context, missing_evidence.append, proven.append, repo.get, repo_component_hotspots, repo_hotspots

_position_size
File: backend/app/stacks/chat_public/math_tools/engine.py
Lines: 746-839
Matched Terms: position
Calls: MathToolError, _decimal, _positive, _success, abs, arguments.get, bool, exact_quantity.to_integral_value

_portfolio_weights
File: backend/app/stacks/chat_public/math_tools/engine.py
Lines: 842-902
Matched Terms: portfolio, position
Calls: ','.join, MathToolError, _sequence, _success, any, arguments.get, format, len, sum, tuple

_trade_statistics
File: backend/app/stacks/chat_public/math_tools/engine.py
Lines: 1188-1312
Matched Terms: loss
Calls: Decimal, _mean, _sequence, _success, abs, arguments.get, len, sum, tuple

_extract_position_size
File: backend/app/stacks/chat_public/math_tools/live_math.py
Lines: 224-279
Matched Terms: portfolio, position
Calls: ExtractedMathRequest, MathToolRequest, _clean_number, match.group, pattern.search, re.compile

ask_ollama
File: backend/app/stacks/chat_public/ollama_chat_client.py
Lines: 46-80
Matched Terms: portfolio
Calls: data.get, data.get('message', {}).get, data.get('message', {}).get('content', '').strip, get_chat_time_context, json.dumps, json.dumps(payload).encode, json.loads, resolve_runtime_model, response.read, response.read().decode, urllib.request.Request, urllib.request.urlopen

compose_prompt
File: backend/app/stacks/chat_public/prompt_composer.py
Lines: 26-75
Matched Terms: position
Calls: '\n\n'.join, PromptComposition, TypeError, ValueError, bounder, isinstance, len, str, tuple

_safe_citation_replacement
File: backend/app/stacks/chat_public/response_verification.py
Lines: 552-601
Matched Terms: gain
Calls: '\n'.join, citation.get, lines.append, str

_safe_boundary_replacement
File: backend/app/stacks/chat_public/response_verification.py
Lines: 604-610
Matched Terms: portfolio
Calls: NONE EXTRACTED

test_financial_strategy_intent_remains_eligible
File: backend/app/stacks/chat_public/tests/test_aiq004d3_runtime_branch_repairs.py
Lines: 143-161
Matched Terms: loss
Calls: capture_strategy_proposal, patch

test_drawdown_guard_is_not_called_without_balance
File: backend/app/stacks/chat_public/tests/test_capability_state_registry.py
Lines: 51-69
Matched Terms: balance
Calls: build_capability_registry, len

test_developer_response_contains_capability_state
File: backend/app/stacks/chat_public/tests/test_capability_state_registry.py
Lines: 87-96
Matched Terms: valuation
Calls: build_developer_response

test_developer_capabilities_remain_grounded
File: backend/app/stacks/chat_public/tests/test_capability_state_registry.py
Lines: 99-107
Matched Terms: valuation
Calls: build_developer_response, build_developer_response(subtype='self_evaluation').lower

test_developer_pronoun_i_is_not_detected_as_ticker
File: backend/app/stacks/chat_public/tests/test_chat_intent_regex.py
Lines: 107-115
Matched Terms: valuation
Calls: detect_chat_intent

test_decision_serializes_complete_contract
File: backend/app/stacks/chat_public/tests/test_cognitive_model_router.py
Lines: 162-189
Matched Terms: portfolio
Calls: decision.as_dict, intent, isinstance, route_cognitive_request, set

test_position_size_uses_math_without_retrieval
File: backend/app/stacks/chat_public/tests/test_cognitive_model_router.py
Lines: 270-285
Matched Terms: account value, portfolio, position
Calls: intent, route_cognitive_request

test_conversation_memory_avoids_retrieval
File: backend/app/stacks/chat_public/tests/test_cognitive_model_router.py
Lines: 302-315
Matched Terms: portfolio
Calls: intent, pytest.mark.parametrize, route_cognitive_request

test_explicit_retrieval_requests_remain_enabled
File: backend/app/stacks/chat_public/tests/test_cognitive_model_router.py
Lines: 328-340
Matched Terms: portfolio
Calls: intent, pytest.mark.parametrize, route_cognitive_request

test_strategy_family_retains_retrieval_contract
File: backend/app/stacks/chat_public/tests/test_cognitive_model_router.py
Lines: 345-357
Matched Terms: portfolio
Calls: intent, route_cognitive_request

test_market_and_portfolio_family_do_not_force_retrieval
File: backend/app/stacks/chat_public/tests/test_cognitive_model_router.py
Lines: 398-417
Matched Terms: portfolio
Calls: intent, pytest.mark.parametrize, route_cognitive_request

test_registry_is_explicit_and_complete
File: backend/app/stacks/chat_public/tests/test_deterministic_math_engine.py
Lines: 44-61
Matched Terms: portfolio, position
Calls: supported_operations

test_position_size
File: backend/app/stacks/chat_public/tests/test_deterministic_math_engine.py
Lines: 239-269
Matched Terms: position
Calls: Decimal, calculate, decimal_value

test_portfolio_weights
File: backend/app/stacks/chat_public/tests/test_deterministic_math_engine.py
Lines: 272-295
Matched Terms: portfolio
Calls: Decimal, calculate, decimal_value

test_general_conversation_does_not_load_developer_overlay
File: backend/app/stacks/chat_public/tests/test_developer_context_overlay.py
Lines: 18-31
Matched Terms: snapshot
Calls: section_map

test_self_evaluation_adds_grounded_developer_requirements
File: backend/app/stacks/chat_public/tests/test_developer_context_overlay.py
Lines: 34-56
Matched Terms: valuation
Calls: section_map, sections['SELF-REFLECTION MODE'].lower

test_developer_repo_and_architecture_context_are_bounded
File: backend/app/stacks/chat_public/tests/test_developer_context_overlay.py
Lines: 81-110
Matched Terms: snapshot, valuation
Calls: len, section_map

test_developer_response_is_structured
File: backend/app/stacks/chat_public/tests/test_developer_response_builder.py
Lines: 14-22
Matched Terms: valuation
Calls: build_developer_response

test_developer_response_does_not_claim_unverified_tests
File: backend/app/stacks/chat_public/tests/test_developer_response_builder.py
Lines: 25-32
Matched Terms: valuation
Calls: build_developer_response, build_developer_response(subtype='self_evaluation').lower

test_position_size_uses_whole_units
File: backend/app/stacks/chat_public/tests/test_live_math_runtime_integration.py
Lines: 133-152
Matched Terms: account value, position
Calls: evaluate_live_math

test_ambiguous_math_fails_controlled
File: backend/app/stacks/chat_public/tests/test_live_math_runtime_integration.py
Lines: 167-182
Matched Terms: portfolio
Calls: evaluate_live_math

result
File: backend/app/stacks/chat_public/tests/test_live_rag_activation.py
Lines: 72-104
Matched Terms: portfolio
Calls: RetrievalResult

test_strategy_family_requests_retrieval
File: backend/app/stacks/chat_public/tests/test_live_rag_activation.py
Lines: 107-118
Matched Terms: portfolio
Calls: FakeIntent, route_cognitive_request

test_runtime_verification_occurs_before_persistence
File: backend/app/stacks/chat_public/tests/test_live_response_verification.py
Lines: 100-127
Matched Terms: position
Calls: inspect.getsource, source.find

test_semantic_retrieval_ranks_relevant_chunk_first
File: backend/app/stacks/chat_public/tests/test_local_rag_index.py
Lines: 247-307
Matched Terms: portfolio
Calls: FakeEmbeddingClient, LocalKnowledgeIndex, cake.write_text, docs.mkdir, index.build_from_paths, index.retrieve, owner.write_text, results[0].citation.startswith, trading.write_text

test_prompt_composition_is_immutable
File: backend/app/stacks/chat_public/tests/test_prompt_composer.py
Lines: 154-164
Matched Terms: position
Calls: PromptComposition, pytest.raises

test_public_chat_contract_accepts_valid_text
File: backend/app/stacks/chat_public/tests/test_public_chat_controls.py
Lines: 29-32
Matched Terms: portfolio
Calls: validate_public_chat_text

test_payload_boundary_safety_uses_only_payload
File: backend/app/stacks/chat_public/tests/test_public_chat_controls.py
Lines: 377-414
Matched Terms: portfolio
Calls: AnonymousSlidingWindowLimiter, Dependency, Payload, enforce_public_chat_controls, payload.model_dump, wrapped

model_dump
File: backend/app/stacks/chat_public/tests/test_public_chat_controls.py
Lines: 379-384
Matched Terms: portfolio
Calls: NONE EXTRACTED

test_position_size_result_passes
File: backend/app/stacks/chat_public/tests/test_response_verification.py
Lines: 145-163
Matched Terms: account value, position
Calls: evaluate_live_math, no_retrieval, verify_response

_fake_bundle
File: backend/app/stacks/chat_public/tests/test_role_overlay_injection.py
Lines: 48-59
Matched Terms: portfolio
Calls: SimpleNamespace

init_db
File: backend/app/stacks/db_runtime/database.py
Lines: 86-101
Matched Terms: position
Calls: connection.run_sync, engine.begin

process_portfolio_output
File: backend/app/stacks/execution/paper_broker.py
Lines: 21-227
Matched Terms: balance, portfolio, position, positions, valuation
Calls: ValueError, calculate_live_portfolio_equity, calculate_position_size, create_trace_id, drawdown_healthcheck, drawdown_status.get, emit_runtime_step, equity_matrix.get, execute_trade, float, generate_signal, get_bars, get_latest_price, get_live_market_price, is_kill_switch_active, isinstance, live_feed.get, portfolio_output.get, position.get, random.uniform, raw_output_signal.get, save_log, sizing_matrix.get, str, str(signal).lower, str(user_id).strip, trade_result.get

get_positions_snapshot
File: backend/app/stacks/execution/paper_broker.py
Lines: 231-250
Matched Terms: portfolio, position, positions, snapshot
Calls: ValueError, str, str(user_id).strip

_revoke_refresh_sessions
File: backend/app/stacks/identity_auth/admin_mutation_service.py
Lines: 236-263
Matched Terms: refresh
Calls: IdentityRefreshSession.revoked_at.is_, datetime.now, int, self._session.execute, update, update(IdentityRefreshSession).where, update(IdentityRefreshSession).where(IdentityRefreshSession.user_id == user_id).where, update(IdentityRefreshSession).where(IdentityRefreshSession.user_id == user_id).where(IdentityRefreshSession.revoked_at.is_(None)).values

require_password_reset
File: backend/app/stacks/identity_auth/admin_mutation_service.py
Lines: 282-328
Matched Terms: refresh
Calls: AdministrativeMutationResponse, self._assert_target_mutable, self._audit, self._authorize_actor, self._load_target, self._revoke_refresh_sessions, self._session.commit, self._session.rollback

issue_temporary_password
File: backend/app/stacks/identity_auth/admin_mutation_service.py
Lines: 330-385
Matched Terms: refresh
Calls: AdministrativeTemporaryPasswordResponse, _generate_temporary_password, hash_password, self._assert_target_mutable, self._audit, self._authorize_actor, self._load_target, self._revoke_refresh_sessions, self._session.commit, self._session.rollback

disable_account
File: backend/app/stacks/identity_auth/admin_mutation_service.py
Lines: 387-434
Matched Terms: refresh
Calls: AdministrativeMutationResponse, _set_status, self._assert_target_mutable, self._audit, self._authorize_actor, self._load_target, self._revoke_refresh_sessions, self._session.commit, self._session.rollback

delete_account
File: backend/app/stacks/identity_auth/admin_mutation_service.py
Lines: 479-536
Matched Terms: refresh
Calls: AdministrativeDeleteResponse, delete, delete(IdentityAccessTokenRevocation).where, delete(IdentityRefreshSession).where, self._assert_target_mutable, self._audit, self._authorize_actor, self._load_target, self._session.commit, self._session.delete, self._session.execute, self._session.rollback

_session_identifier
File: backend/app/stacks/identity_auth/admin_read_models.py
Lines: 65-86
Matched Terms: refresh
Calls: RuntimeError, _string_value, getattr

_session_family_identifier
File: backend/app/stacks/identity_auth/admin_read_models.py
Lines: 89-107
Matched Terms: refresh
Calls: _string_value, getattr

_replacement_identifier
File: backend/app/stacks/identity_auth/admin_read_models.py
Lines: 110-129
Matched Terms: refresh
Calls: _string_value, getattr

_session_state
File: backend/app/stacks/identity_auth/admin_read_models.py
Lines: 132-170
Matched Terms: refresh
Calls: _datetime_value, _replacement_identifier, datetime.now, getattr

_session_summary
File: backend/app/stacks/identity_auth/admin_read_models.py
Lines: 230-274
Matched Terms: refresh
Calls: AdministrativeSessionSummary, _datetime_value, _replacement_identifier, _session_identifier, _session_state, _string_value, getattr

get_user
File: backend/app/stacks/identity_auth/admin_read_models.py
Lines: 331-408
Matched Terms: refresh
Calls: AdministrativeUserDetail, IdentityRefreshSession.revoked_at.is_, _user_summary, active_result.scalar_one, datetime.now, func.count, int, result.scalar_one_or_none, select, select(IdentityUser).where, select(func.count()).select_from, select(func.count()).select_from(IdentityRefreshSession).where, self._session.execute, summary.model_dump, total_result.scalar_one

list_sessions
File: backend/app/stacks/identity_auth/admin_read_models.py
Lines: 410-468
Matched Terms: refresh
Calls: AdministrativeSessionListResponse, IdentityRefreshSession.issued_at.desc, _session_summary, len, result.scalars, result.scalars().all, select, self._session.execute, statement.order_by, statement.order_by(IdentityRefreshSession.issued_at.desc()).offset, statement.order_by(IdentityRefreshSession.issued_at.desc()).offset(offset).limit, statement.where, tuple

get_session
File: backend/app/stacks/identity_auth/admin_read_models.py
Lines: 470-516
Matched Terms: refresh
Calls: AdministrativeSessionDetail, _replacement_identifier, _session_family_identifier, _session_summary, getattr, result.scalar_one_or_none, select, select(IdentityRefreshSession).where, self._session.execute, summary.model_dump

require_authenticated_principal
File: backend/app/stacks/identity_auth/api_dependencies.py
Lines: 97-185
Matched Terms: refresh
Calls: AccessTokenRevocationRepository, Depends, HTTPException, async_session, authenticate_bearer_credentials, getattr, repository.is_revoked

get_required_password_change_service
File: backend/app/stacks/identity_auth/api_dependencies.py
Lines: 232-245
Matched Terms: refresh
Calls: IdentityUserRepository, RefreshSessionRepository, RequiredPasswordChangeService, async_session

login_identity
File: backend/app/stacks/identity_auth/api_router.py
Lines: 163-232
Matched Terms: refresh
Calls: Depends, HTTPException, LoginCommand, LoginTokenApiResponse, isinstance, result.token_type.lower, router.post, service.login

refresh_session
File: backend/app/stacks/identity_auth/api_router.py
Lines: 287-348
Matched Terms: refresh
Calls: Depends, HTTPException, SessionTokenApiResponse, isinstance, result.token_type.lower, router.post, service.refresh

logout_session
File: backend/app/stacks/identity_auth/api_router.py
Lines: 356-425
Matched Terms: refresh
Calls: Depends, HTTPException, SessionActionApiResponse, datetime.fromtimestamp, getattr, isinstance, router.post, service.logout

refresh
File: backend/app/stacks/identity_auth/api_router.py
Lines: 82-87
Matched Terms: refresh
Calls: NONE EXTRACTED

logout
File: backend/app/stacks/identity_auth/api_router.py
Lines: 89-94
Matched Terms: refresh
Calls: NONE EXTRACTED

__post_init__
File: backend/app/stacks/identity_auth/contracts.py
Lines: 21-43
Matched Terms: refresh
Calls: ValueError

__post_init__
File: backend/app/stacks/identity_auth/contracts.py
Lines: 61-93
Matched Terms: refresh
Calls: MappingProxyType, ValueError, dict, object.__setattr__

provision_dev_owner
File: backend/app/stacks/identity_auth/dev_owner_provisioner.py
Lines: 38-105
Matched Terms: refresh
Calls: DevOwnerProvisioningResult, IdentityUserRepository, async_session, engine.dispose, hash_password, repository.create, repository.get_by_email, repository.update_identity_security_state, repository.update_password_hash, session.commit, session.refresh, verify_password

__init__
File: backend/app/stacks/identity_auth/login_service.py
Lines: 28-70
Matched Terms: refresh
Calls: ValueError

login
File: backend/app/stacks/identity_auth/login_service.py
Lines: 72-227
Matched Terms: refresh
Calls: AuthenticationRejectedError, AuthenticationTokenPair, bool, canonical_role_value, getattr, isinstance, normalize_email, normalize_subscription_tier, self._commit, self._hash_refresh_token, self._perform_dummy_verification, self._refresh_session_repository.create, self._rollback, self._token_issuer.issue_access_token, self._token_issuer.issue_refresh_token, self._user_repository.get_by_email, self._verify_password

mock_hash_refresh_token
File: backend/app/stacks/identity_auth/mock_runtime.py
Lines: 269-284
Matched Terms: refresh
Calls: ('mock-refresh-pepper:' + token).encode, ValueError, hashlib.sha256, hashlib.sha256(('mock-refresh-pepper:' + token).encode('utf-8')).hexdigest

__init__
File: backend/app/stacks/identity_auth/mock_runtime.py
Lines: 90-95
Matched Terms: refresh
Calls: NONE EXTRACTED

create
File: backend/app/stacks/identity_auth/mock_runtime.py
Lines: 97-123
Matched Terms: refresh
Calls: MockRefreshSession, RuntimeError, self.sessions.append

__init__
File: backend/app/stacks/identity_auth/mock_runtime.py
Lines: 146-151
Matched Terms: refresh
Calls: NONE EXTRACTED

issue_refresh_token
File: backend/app/stacks/identity_auth/mock_runtime.py
Lines: 192-229
Matched Terms: refresh
Calls: IssuedServiceToken, RuntimeError, datetime.now, dict, timedelta

__init__
File: backend/app/stacks/identity_auth/mock_runtime.py
Lines: 288-343
Matched Terms: refresh
Calls: LoginService, MockIdentityUserRepository, MockRefreshSessionRepository, MockServiceTokenIssuer, MockTransactionBoundary, RegistrationService, mock_hash_password

__init__
File: backend/app/stacks/identity_auth/password_change_service.py
Lines: 59-70
Matched Terms: refresh
Calls: NONE EXTRACTED

replace_required_password
File: backend/app/stacks/identity_auth/password_change_service.py
Lines: 72-169
Matched Terms: refresh
Calls: PasswordChangeRejectedError, PasswordChangeResult, datetime.now, hash_password, isinstance, self._commit, self._refresh_repository.revoke_all_for_user, self._rollback, self._user_repository.get_by_id, self._user_repository.update_identity_security_state, self._user_repository.update_password_hash, validate_replacement_password, verify_password

hash_refresh_token
File: backend/app/stacks/identity_auth/refresh_token_hashing.py
Lines: 7-35
Matched Terms: refresh
Calls: ValueError, hmac.new, hmac.new(pepper, token.encode('utf-8'), hashlib.sha256).hexdigest, isinstance, len, token.encode

verify_refresh_token_hash
File: backend/app/stacks/identity_auth/refresh_token_hashing.py
Lines: 38-52
Matched Terms: refresh
Calls: hash_refresh_token, hmac.compare_digest

create
File: backend/app/stacks/identity_auth/repositories.py
Lines: 202-247
Matched Terms: refresh
Calls: ValueError, _IdentityRefreshSession, _refresh_uuid4, self._session.add, self._session.flush, str

get_by_token_id
File: backend/app/stacks/identity_auth/repositories.py
Lines: 249-274
Matched Terms: refresh
Calls: (await self._session.execute(statement)).scalar_one_or_none, _refresh_select, _refresh_select(_IdentityRefreshSession).where, self._session.execute, statement.with_for_update

revoke
File: backend/app/stacks/identity_auth/repositories.py
Lines: 276-287
Matched Terms: refresh
Calls: self._session.flush

revoke_family
File: backend/app/stacks/identity_auth/repositories.py
Lines: 289-318
Matched Terms: refresh
Calls: _IdentityRefreshSession.revoked_at.is_, _refresh_update, _refresh_update(_IdentityRefreshSession).where, _refresh_update(_IdentityRefreshSession).where(_IdentityRefreshSession.family_id == family_id).where, _refresh_update(_IdentityRefreshSession).where(_IdentityRefreshSession.family_id == family_id).where(_IdentityRefreshSession.revoked_at.is_(None)).values, int, self._session.execute

revoke_all_for_user
File: backend/app/stacks/identity_auth/repositories.py
Lines: 320-349
Matched Terms: refresh
Calls: _IdentityRefreshSession.revoked_at.is_, _refresh_update, _refresh_update(_IdentityRefreshSession).where, _refresh_update(_IdentityRefreshSession).where(_IdentityRefreshSession.user_id == user_id).where, _refresh_update(_IdentityRefreshSession).where(_IdentityRefreshSession.user_id == user_id).where(_IdentityRefreshSession.revoked_at.is_(None)).values, int, self._session.execute

delete_expired
File: backend/app/stacks/identity_auth/repositories.py
Lines: 351-375
Matched Terms: refresh
Calls: _refresh_datetime.now, _refresh_delete, _refresh_delete(_IdentityRefreshSession).where, int, self._session.execute

build_authentication_runtime
File: backend/app/stacks/identity_auth/runtime_adapter.py
Lines: 273-343
Matched Terms: refresh
Calls: EnvironmentJwtTokenIssuer, IdentityUserRepository, LoginService, RefreshSessionRepository, RegistrationService, hash_password, hash_refresh_token, load_jwt_secret

authentication_runtime
File: backend/app/stacks/identity_auth/runtime_adapter.py
Lines: 347-364
Matched Terms: refresh
Calls: async_session, build_authentication_runtime

build_session_lifecycle_runtime
File: backend/app/stacks/identity_auth/runtime_adapter.py
Lines: 367-451
Matched Terms: refresh
Calls: AccessTokenRevocationRepository, EnvironmentJwtTokenIssuer, IdentityUserRepository, RefreshSessionRepository, RefreshSessionService, SessionLifecycleService, ValidatedRefreshIdentity, _as_identifier, _claim_value, hash_refresh_token, load_jwt_secret, validate_refresh_token, verify_refresh_token_hash

issue_refresh_token
File: backend/app/stacks/identity_auth/runtime_adapter.py
Lines: 232-270
Matched Terms: refresh
Calls: IssuedServiceToken, _as_datetime, _as_identifier, _claim_value, issue_refresh_token, validate_refresh_token

runtime_refresh_token_hash
File: backend/app/stacks/identity_auth/runtime_adapter.py
Lines: 304-310
Matched Terms: refresh
Calls: hash_refresh_token

runtime_validate_refresh_token
File: backend/app/stacks/identity_auth/runtime_adapter.py
Lines: 388-410
Matched Terms: refresh
Calls: ValidatedRefreshIdentity, _as_identifier, _claim_value, validate_refresh_token

runtime_hash_refresh_token
File: backend/app/stacks/identity_auth/runtime_adapter.py
Lines: 412-418
Matched Terms: refresh
Calls: hash_refresh_token

runtime_verify_refresh_token
File: backend/app/stacks/identity_auth/runtime_adapter.py
Lines: 420-428
Matched Terms: refresh
Calls: verify_refresh_token_hash

issue_refresh_token
File: backend/app/stacks/identity_auth/service_contracts.py
Lines: 103-108
Matched Terms: refresh
Calls: NONE EXTRACTED

__init__
File: backend/app/stacks/identity_auth/session_lifecycle_service.py
Lines: 96-139
Matched Terms: refresh
Calls: NONE EXTRACTED

_validated_record
File: backend/app/stacks/identity_auth/session_lifecycle_service.py
Lines: 141-196
Matched Terms: refresh
Calls: SessionLifecycleRejectedError, isinstance, self._refresh_repository.get_by_token_id, self._validate_refresh_token, self._verify_refresh_token

refresh
File: backend/app/stacks/identity_auth/session_lifecycle_service.py
Lines: 198-333
Matched Terms: refresh
Calls: AuthenticationTokenPair, SessionLifecycleRejectedError, canonical_role_value, normalize_subscription_tier, self._commit, self._hash_refresh_token, self._refresh_service.rotate, self._rollback, self._token_issuer.issue_access_token, self._token_issuer.issue_refresh_token, self._user_repository.get_by_id, self._validated_record

logout
File: backend/app/stacks/identity_auth/session_lifecycle_service.py
Lines: 335-389
Matched Terms: refresh
Calls: SessionLifecycleRejectedError, self._access_revocation_repository.revoke, self._commit, self._refresh_service.logout, self._rollback, self._validated_record

logout_all
File: backend/app/stacks/identity_auth/session_lifecycle_service.py
Lines: 391-425
Matched Terms: refresh
Calls: SessionLifecycleRejectedError, isinstance, self._commit, self._refresh_service.revoke_all, self._rollback

cleanup_expired
File: backend/app/stacks/identity_auth/session_lifecycle_service.py
Lines: 427-448
Matched Terms: refresh
Calls: SessionLifecycleRejectedError, self._commit, self._refresh_service.cleanup_expired, self._rollback

__init__
File: backend/app/stacks/identity_auth/session_service.py
Lines: 49-59
Matched Terms: refresh
Calls: RefreshSessionRepository

rotate
File: backend/app/stacks/identity_auth/session_service.py
Lines: 61-127
Matched Terms: refresh
Calls: RefreshSessionExpiredError, RefreshSessionNotFoundError, RefreshTokenReuseDetectedError, RotationResult, datetime.now, self._repository.create, self._repository.get_by_token_id, self._repository.revoke, self._repository.revoke_family

test_refresh_token_is_rejected_by_api_dependency
File: backend/app/stacks/identity_auth/tests/test_api_dependency.py
Lines: 85-102
Matched Terms: refresh
Calls: HTTPAuthorizationCredentials, authenticate_bearer_credentials, issue_refresh_token, pytest.raises

test_login_contract
File: backend/app/stacks/identity_auth/tests/test_api_route_contract.py
Lines: 182-210
Matched Terms: refresh
Calls: FakeLoginService, LoginCommand, TestClient, build_test_app, client.post, response.json

login
File: backend/app/stacks/identity_auth/tests/test_api_route_contract.py
Lines: 63-92
Matched Terms: refresh
Calls: AuthenticationTokenPair, datetime.now, timedelta

test_refresh_token_validation_failure_is_unauthorized
File: backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py
Lines: 283-312
Matched Terms: refresh
Calls: RuntimeError, TestClient, build_test_app, client.get, monkeypatch.setattr

reject
File: backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py
Lines: 286-291
Matched Terms: refresh
Calls: RuntimeError

test_auth_router_has_complete_session_lifecycle
File: backend/app/stacks/identity_auth/tests/test_canonical_router_inclusion.py
Lines: 95-128
Matched Terms: refresh
Calls: NONE EXTRACTED

test_controlled_local_registration_and_login
File: backend/app/stacks/identity_auth/tests/test_canonical_router_inclusion.py
Lines: 131-182
Matched Terms: refresh
Calls: FastAPI, QualificationLoginService, QualificationRegistrationService, TestClient, app.include_router, client.post, login.json

login
File: backend/app/stacks/identity_auth/tests/test_canonical_router_inclusion.py
Lines: 44-68
Matched Terms: refresh
Calls: AuthenticationTokenPair, datetime.now, timedelta

test_refresh_session_schema_contract
File: backend/app/stacks/identity_auth/tests/test_identity_persistence_models.py
Lines: 39-59
Matched Terms: refresh
Calls: inspect

test_refresh_token_hash_never_contains_raw_token
File: backend/app/stacks/identity_auth/tests/test_identity_persistence_models.py
Lines: 68-92
Matched Terms: refresh
Calls: hash_refresh_token, verify_refresh_token_hash

build_service
File: backend/app/stacks/identity_auth/tests/test_login_service.py
Lines: 45-109
Matched Terms: refresh
Calls: AsyncMock, LoginService, Mock, issued

test_valid_login_issues_separate_tokens_and_session
File: backend/app/stacks/identity_auth/tests/test_login_service.py
Lines: 126-200
Matched Terms: refresh
Calls: LoginCommand, active_user, build_service, commit.assert_awaited_once, created.values, hash_refresh_token.assert_called_once_with, refresh_repository.create.assert_awaited_once, rollback.assert_not_awaited, service.login, token_issuer.issue_access_token.assert_awaited_once_with, token_issuer.issue_refresh_token.assert_awaited_once_with, user_repository.get_by_email.assert_awaited_once_with, verify_password.assert_called_once_with

test_disabled_account_fails_closed
File: backend/app/stacks/identity_auth/tests/test_login_service.py
Lines: 253-288
Matched Terms: refresh
Calls: LoginCommand, active_user, build_service, commit.assert_not_awaited, pytest.raises, refresh_repository.create.assert_not_awaited, rollback.assert_awaited_once, service.login, token_issuer.issue_access_token.assert_not_awaited

test_refresh_session_failure_rolls_back
File: backend/app/stacks/identity_auth/tests/test_login_service.py
Lines: 321-351
Matched Terms: refresh
Calls: LoginCommand, RuntimeError, active_user, build_service, commit.assert_not_awaited, pytest.raises, rollback.assert_awaited_once, service.login

test_identical_tokens_fail_closed
File: backend/app/stacks/identity_auth/tests/test_login_service.py
Lines: 355-392
Matched Terms: refresh
Calls: LoginCommand, active_user, build_service, commit.assert_not_awaited, issued, pytest.raises, refresh_repository.create.assert_not_awaited, rollback.assert_awaited_once, service.login

test_refresh_rotation_revokes_previous_token
File: backend/app/stacks/identity_auth/tests/test_refresh_rotation.py
Lines: 37-79
Matched Terms: refresh
Calls: InMemoryTokenRevocationStore, issue_refresh_token, pytest.raises, rotate_refresh_token, validate_access_token, validate_refresh_token

test_refresh_token_cannot_be_rotated_twice
File: backend/app/stacks/identity_auth/tests/test_refresh_rotation.py
Lines: 82-103
Matched Terms: refresh
Calls: InMemoryTokenRevocationStore, issue_refresh_token, pytest.raises, rotate_refresh_token

make_record
File: backend/app/stacks/identity_auth/tests/test_refresh_session_persistence.py
Lines: 18-50
Matched Terms: refresh
Calls: IdentityRefreshSession, datetime.now, timedelta

test_rotation_preserves_family_and_revokes_old
File: backend/app/stacks/identity_auth/tests/test_refresh_session_persistence.py
Lines: 54-99
Matched Terms: refresh
Calls: AsyncMock, Mock, RefreshSessionService, datetime.now, make_record, service._repository.revoke.assert_awaited_once, service.rotate, timedelta

test_reuse_revokes_entire_family
File: backend/app/stacks/identity_auth/tests/test_refresh_session_persistence.py
Lines: 103-142
Matched Terms: refresh
Calls: AsyncMock, Mock, RefreshSessionService, datetime.now, make_record, pytest.raises, service._repository.revoke_family.assert_awaited_once, service.rotate, timedelta

test_logout_is_idempotent
File: backend/app/stacks/identity_auth/tests/test_refresh_session_persistence.py
Lines: 146-163
Matched Terms: refresh
Calls: AsyncMock, Mock, RefreshSessionService, service._repository.revoke.assert_not_awaited, service.logout

test_complete_mock_registration_and_login_flow
File: backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py
Lines: 19-74
Matched Terms: refresh
Calls: LoginCommand, MockAuthenticationRuntime, RegistrationCommand, len, mock_hash_refresh_token, result.access_token.startswith, result.refresh_token.startswith, runtime.login.login, runtime.registration.register

test_unknown_and_wrong_password_share_error
File: backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py
Lines: 107-148
Matched Terms: refresh
Calls: LoginCommand, MockAuthenticationRuntime, RegistrationCommand, len, pytest.raises, runtime.login.login, runtime.registration.register, str

test_disabled_account_rejected_before_token_issuance
File: backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py
Lines: 152-184
Matched Terms: refresh
Calls: LoginCommand, MockAuthenticationRuntime, RegistrationCommand, len, pytest.raises, runtime.login.login, runtime.registration.register

test_access_token_failure_rolls_back
File: backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py
Lines: 188-216
Matched Terms: refresh
Calls: LoginCommand, MockAuthenticationRuntime, RegistrationCommand, len, pytest.raises, runtime.login.login, runtime.registration.register

test_refresh_token_failure_rolls_back
File: backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py
Lines: 220-248
Matched Terms: refresh
Calls: LoginCommand, MockAuthenticationRuntime, RegistrationCommand, len, pytest.raises, runtime.login.login, runtime.registration.register

test_refresh_session_failure_rolls_back
File: backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py
Lines: 252-280
Matched Terms: refresh
Calls: LoginCommand, MockAuthenticationRuntime, RegistrationCommand, len, pytest.raises, runtime.login.login, runtime.registration.register

test_registration_normalizes_and_hashes_password
File: backend/app/stacks/identity_auth/tests/test_registration_service.py
Lines: 70-116
Matched Terms: refresh
Calls: RegistrationCommand, build_service, commit.assert_awaited_once, hasattr, hash_password.assert_called_once_with, repository.create.assert_awaited_once_with, repository.get_by_email.assert_awaited_once_with, rollback.assert_not_awaited, service.register

test_real_access_and_refresh_token_paths
File: backend/app/stacks/identity_auth/tests/test_runtime_adapter.py
Lines: 113-151
Matched Terms: refresh
Calls: EnvironmentJwtTokenIssuer, install_controlled_secret, issuer.issue_access_token, issuer.issue_refresh_token

token_pair
File: backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
Lines: 38-59
Matched Terms: refresh
Calls: AuthenticationTokenPair, datetime.now, timedelta

test_lifecycle_route_policy_inventory
File: backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
Lines: 132-155
Matched Terms: refresh
Calls: route_protection.resolve_route_policy

test_refresh_returns_rotated_pair
File: backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
Lines: 158-184
Matched Terms: refresh
Calls: FakeLifecycleService, TestClient, build_app, client.post, response.json

test_logout_revokes_current_refresh_session
File: backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
Lines: 187-211
Matched Terms: refresh
Calls: FakeLifecycleService, TestClient, build_app, client.post, response.json

test_refresh_rejection_is_unauthorized
File: backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
Lines: 214-244
Matched Terms: refresh
Calls: RejectingService, SessionLifecycleRejectedError, TestClient, build_app, client.post

test_logout_rejection_is_unauthorized
File: backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
Lines: 247-273
Matched Terms: refresh
Calls: RejectingService, SessionLifecycleRejectedError, TestClient, build_app, client.post

test_refresh_request_forbids_extra_fields
File: backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
Lines: 360-377
Matched Terms: refresh
Calls: FakeLifecycleService, TestClient, build_app, client.post

test_logout_request_forbids_extra_fields
File: backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
Lines: 380-397
Matched Terms: refresh
Calls: FakeLifecycleService, TestClient, build_app, client.post

__init__
File: backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
Lines: 63-66
Matched Terms: refresh
Calls: NONE EXTRACTED

refresh
File: backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
Lines: 68-77
Matched Terms: refresh
Calls: self.refreshed.append, token_pair

logout
File: backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
Lines: 79-86
Matched Terms: refresh
Calls: self.logged_out.append

refresh
File: backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
Lines: 218-225
Matched Terms: refresh
Calls: SessionLifecycleRejectedError

logout
File: backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
Lines: 251-258
Matched Terms: refresh
Calls: SessionLifecycleRejectedError

test_login_issues_canonical_role_and_tier_claims
File: backend/app/stacks/identity_auth/tests/test_stage4f_canonical_claim_propagation.py
Lines: 59-116
Matched Terms: refresh
Calls: AsyncMock, LoginCommand, LoginService, Mock, active_user, issued, issuer.issue_access_token.assert_awaited_once_with, issuer.issue_refresh_token.assert_awaited_once_with, service.login

test_login_rejects_invalid_stored_role
File: backend/app/stacks/identity_auth/tests/test_stage4f_canonical_claim_propagation.py
Lines: 120-154
Matched Terms: refresh
Calls: AsyncMock, LoginCommand, LoginService, Mock, active_user, issuer.issue_access_token.assert_not_awaited, pytest.raises, service.login

test_refresh_uses_current_user_claims
File: backend/app/stacks/identity_auth/tests/test_stage4f_canonical_claim_propagation.py
Lines: 158-238
Matched Terms: refresh
Calls: AsyncMock, Mock, SessionLifecycleService, SimpleNamespace, ValidatedRefreshIdentity, active_user, issued, issuer.issue_access_token.assert_awaited_once_with, issuer.issue_refresh_token.assert_awaited_once_with, service.refresh, user_repository.get_by_id.assert_awaited_once_with

test_refresh_rejects_missing_current_user
File: backend/app/stacks/identity_auth/tests/test_stage4f_canonical_claim_propagation.py
Lines: 242-291
Matched Terms: refresh
Calls: AsyncMock, Mock, SessionLifecycleService, SimpleNamespace, ValidatedRefreshIdentity, issuer.issue_access_token.assert_not_awaited, issuer.issue_refresh_token.assert_not_awaited, pytest.raises, service.refresh

test_environment_issuer_signatures_accept_extra_claims
File: backend/app/stacks/identity_auth/tests/test_stage4f_environment_token_issuer_contract.py
Lines: 33-48
Matched Terms: refresh
Calls: getattr, inspect.signature

test_environment_refresh_issuer_forwards_claims
File: backend/app/stacks/identity_auth/tests/test_stage4f_environment_token_issuer_contract.py
Lines: 79-102
Matched Terms: refresh
Calls: EnvironmentJwtTokenIssuer, issuer.issue_refresh_token, validate_refresh_token

test_login_forwards_canonical_claims_to_both_tokens
File: backend/app/stacks/identity_auth/tests/test_stage4f_login_refresh_claims.py
Lines: 40-114
Matched Terms: refresh
Calls: AsyncMock, LoginCommand, LoginService, Mock, SimpleNamespace, issued, service.login, token_issuer.issue_access_token.assert_awaited_once_with, token_issuer.issue_refresh_token.assert_awaited_once_with

test_mock_refresh_issuer_accepts_and_records_claims
File: backend/app/stacks/identity_auth/tests/test_stage4f_mock_identity_contract.py
Lines: 40-57
Matched Terms: refresh
Calls: MockServiceTokenIssuer, issuer.issue_refresh_token

test_mock_issuer_signatures_match_claim_contract
File: backend/app/stacks/identity_auth/tests/test_stage4f_mock_identity_contract.py
Lines: 60-80
Matched Terms: refresh
Calls: getattr, inspect.signature

test_mock_registration_login_flow_accepts_claim_propagation
File: backend/app/stacks/identity_auth/tests/test_stage4f_mock_identity_contract.py
Lines: 110-133
Matched Terms: refresh
Calls: LoginCommand, MockAuthenticationRuntime, RegistrationCommand, runtime.login.login, runtime.registration.register

test_rotated_refresh_token_receives_canonical_claims
File: backend/app/stacks/identity_auth/tests/test_stage4f_rotated_refresh_claims.py
Lines: 36-123
Matched Terms: refresh
Calls: AsyncMock, Mock, SessionLifecycleService, SimpleNamespace, ValidatedRefreshIdentity, issued, service.refresh, token_issuer.issue_access_token.assert_awaited_once_with, token_issuer.issue_refresh_token.assert_awaited_once_with

test_session_lifecycle_runtime_builds_user_repository
File: backend/app/stacks/identity_auth/tests/test_stage4f_session_lifecycle_runtime_wiring.py
Lines: 10-56
Matched Terms: refresh
Calls: Mock, build_session_lifecycle_runtime, patch, refresh_repository_type.assert_called_once_with, revocation_repository_type.assert_called_once_with, user_repository_type.assert_called_once_with

test_session_lifecycle_runtime_uses_one_shared_session
File: backend/app/stacks/identity_auth/tests/test_stage4f_session_lifecycle_runtime_wiring.py
Lines: 59-103
Matched Terms: refresh
Calls: Mock, build_session_lifecycle_runtime, patch

test_revocation_model_exposes_only_safe_fields
File: backend/app/stacks/identity_auth/tests/test_stage5b_a_durable_revocation_repository.py
Lines: 19-52
Matched Terms: refresh
Calls: NONE EXTRACTED

test_logout_persists_access_and_refresh_revocation_before_commit
File: backend/app/stacks/identity_auth/tests/test_stage5b_b_durable_bearer_logout.py
Lines: 20-104
Matched Terms: refresh
Calls: AsyncMock, Mock, SessionLifecycleService, SimpleNamespace, ValidatedRefreshIdentity, access_repository.revoke.assert_awaited_once, datetime.now, events.append, rollback.assert_not_awaited, service.logout, timedelta

test_logout_rolls_back_both_revocations_on_failure
File: backend/app/stacks/identity_auth/tests/test_stage5b_b_durable_bearer_logout.py
Lines: 108-166
Matched Terms: refresh
Calls: AsyncMock, Mock, RuntimeError, SessionLifecycleService, SimpleNamespace, ValidatedRefreshIdentity, access_repository.revoke.assert_awaited_once, commit.assert_not_awaited, datetime.now, pytest.raises, rollback.assert_awaited_once, service.logout, timedelta

test_logout_rejects_access_refresh_subject_mismatch
File: backend/app/stacks/identity_auth/tests/test_stage5b_b_durable_bearer_logout.py
Lines: 170-224
Matched Terms: refresh
Calls: AsyncMock, Mock, SessionLifecycleService, SimpleNamespace, ValidatedRefreshIdentity, access_repository.revoke.assert_not_awaited, commit.assert_not_awaited, datetime.now, pytest.raises, refresh_service.logout.assert_not_awaited, rollback.assert_awaited_once, service.logout, timedelta

test_revocation_summary_exposes_no_jti
File: backend/app/stacks/identity_auth/tests/test_stage5b_c_revocation_observability_cleanup.py
Lines: 61-107
Matched Terms: refresh
Calls: AdministrativeReadService._revocation_summary, SimpleNamespace, datetime.now, datetime.now(UTC).replace, summary.model_dump, timedelta

test_required_password_change_updates_hash_and_revokes_sessions
File: backend/app/stacks/identity_auth/tests/test_stage9d_b_forced_password_change.py
Lines: 116-168
Matched Terms: refresh
Calls: FakeRefreshRepository, FakeUser, FakeUserRepository, RequiredPasswordChangeService, hash_password, service.replace_required_password, verify_password

test_wrong_temporary_password_fails_closed
File: backend/app/stacks/identity_auth/tests/test_stage9d_b_forced_password_change.py
Lines: 172-213
Matched Terms: refresh
Calls: FakeRefreshRepository, FakeUser, FakeUserRepository, RequiredPasswordChangeService, hash_password, pytest.raises, service.replace_required_password

test_read_service_does_not_serialize_secret_fields
File: backend/app/stacks/identity_auth/tests/test_stage9d_c2_admin_read_models.py
Lines: 154-168
Matched Terms: refresh
Calls: inspect.getsource

test_refresh_token_is_not_accepted_as_access
File: backend/app/stacks/identity_auth/tests/test_token_contract.py
Lines: 113-125
Matched Terms: refresh
Calls: issue_refresh_token, pytest.raises, validate_access_token

test_access_token_is_not_accepted_as_refresh
File: backend/app/stacks/identity_auth/tests/test_token_contract.py
Lines: 128-140
Matched Terms: refresh
Calls: issue_access_token, pytest.raises, validate_refresh_token

test_token_pair_uses_separate_tokens
File: backend/app/stacks/identity_auth/tests/test_token_contract.py
Lines: 143-159
Matched Terms: refresh
Calls: issue_token_pair, validate_access_token, validate_refresh_token

test_expired_token_is_rejected
File: backend/app/stacks/identity_auth/tests/test_token_contract.py
Lines: 162-181
Matched Terms: refresh
Calls: JWTPolicy, issue_access_token, pytest.raises, validate_access_token

test_reserved_claims_cannot_be_overridden
File: backend/app/stacks/identity_auth/tests/test_token_contract.py
Lines: 283-293
Matched Terms: refresh
Calls: issue_access_token, pytest.raises

issue_token
File: backend/app/stacks/identity_auth/tokens.py
Lines: 157-219
Matched Terms: refresh
Calls: ValueError, _encode, dict, dict(extra_claims or {}).items, int, load_jwt_secret, time.time, uuid.uuid4

issue_refresh_token
File: backend/app/stacks/identity_auth/tokens.py
Lines: 238-251
Matched Terms: refresh
Calls: issue_token

issue_token_pair
File: backend/app/stacks/identity_auth/tokens.py
Lines: 254-274
Matched Terms: refresh
Calls: TokenPair, issue_access_token, issue_refresh_token

validate_token
File: backend/app/stacks/identity_auth/tokens.py
Lines: 277-548
Matched Terms: refresh
Calls: ', '.join, ExpiredTokenError, InvalidTokenError, RevokedTokenError, TokenClaims, TokenNotYetValidError, ValueError, _b64url_decode, _sign, f'{encoded_header}.{encoded_payload}'.encode, hmac.compare_digest, int, isinstance, json.loads, len, load_jwt_secret, payload.items, revocation_store.is_revoked, set, sorted, time.time, token.split

validate_refresh_token
File: backend/app/stacks/identity_auth/tokens.py
Lines: 570-586
Matched Terms: refresh
Calls: validate_token

rotate_refresh_token
File: backend/app/stacks/identity_auth/tokens.py
Lines: 589-614
Matched Terms: refresh
Calls: issue_token_pair, revocation_store.revoke, validate_refresh_token

save_log
File: backend/app/stacks/journal_ledger/ledger.py
Lines: 57-177
Matched Terms: cost_basis, portfolio, position, realized
Calls: OrderHistory, PortfolioInventory, ValueError, async_session, emit_runtime_step, float, isinstance, max, print, raw_signal.get, res.scalar, select, select(PortfolioInventory).where, session.add, session.begin, session.execute, session.flush, signal_str.lower, str, str(user_id).strip, trade_result.get

_normalize_portfolio_read_user_id
File: backend/app/stacks/journal_ledger/ledger.py
Lines: 179-191
Matched Terms: portfolio
Calls: ValueError, str, str(user_id).strip

read_max_allocated_capital
File: backend/app/stacks/journal_ledger/ledger.py
Lines: 194-230
Matched Terms: portfolio
Calls: _normalize_portfolio_read_user_id, async_session, float, func.max, result.scalar_one_or_none, select, select(func.max(OrderHistory.allocated_capital)).where, session.execute

_validate_envelope
File: backend/app/stacks/journal_ledger/strategy_decision_audit_adapter.py
Lines: 300-388
Matched Terms: portfolio
Calls: ', '.join, TypeError, ValueError, envelope.get, isinstance, set, sorted, symbol.strip, symbol.strip().upper

make_draft
File: backend/app/stacks/journal_ledger/tests/test_decision_event_contract.py
Lines: 41-70
Matched Terms: position
Calls: DecisionEventDraft

build_envelope
File: backend/app/stacks/journal_ledger/tests/test_strategy_decision_audit_adapter.py
Lines: 22-46
Matched Terms: balance, portfolio
Calls: NONE EXTRACTED

test_produce_and_audit_delegates_to_service
File: backend/app/stacks/journal_ledger/tests/test_strategy_decision_audit_adapter.py
Lines: 50-204
Matched Terms: position
Calls: AsyncMock, StrategyDecisionAuditAdapter, adapter.produce_and_audit, build_envelope, datetime, isinstance, len, object, service.append.assert_awaited_once, uuid4

market_data_status
File: backend/app/stacks/market_data/api_router.py
Lines: 103-165
Matched Terms: position
Calls: get_market_data_runtime, jsonable_encoder, router.get, runtime.cache.stats, runtime.registry.records, runtime.session.now

_fetch_yf_snapshot
File: backend/app/stacks/market_data/feed.py
Lines: 9-42
Matched Terms: snapshot
Calls: ValueError, fast_info.get, float, ticker.history, type, yf.Ticker

get_live_market_price
File: backend/app/stacks/market_data/feed.py
Lines: 44-47
Matched Terms: snapshot
Calls: asyncio.get_event_loop, loop.run_in_executor

healthcheck
File: backend/app/stacks/market_data/market_session.py
Lines: 166-178
Matched Terms: snapshot
Calls: MarketSessionService, MarketSessionService().now

state_at
File: backend/app/stacks/market_data/market_session.py
Lines: 67-73
Matched Terms: snapshot
Calls: self.snapshot_at

snapshot_at
File: backend/app/stacks/market_data/market_session.py
Lines: 75-154
Matched Terms: snapshot
Calls: MarketSessionSnapshot, ValueError, exchange_time.time, exchange_time.time().replace, exchange_time.weekday, normalized.astimezone, observed_at.astimezone

now
File: backend/app/stacks/market_data/market_session.py
Lines: 156-163
Matched Terms: snapshot
Calls: datetime.now, self.snapshot_at

test_quote_cache_expiry_forces_refresh
File: backend/app/stacks/market_data/tests/test_stage8_runtime_qualification.py
Lines: 233-261
Matched Terms: refresh
Calls: ControlledProvider, build_runtime, runtime.cache.stats, runtime.router.get_quote, time.sleep

_load_default_quote_loader
File: backend/app/stacks/market_data/yfinance_provider.py
Lines: 76-201
Matched Terms: position
Calls: YFinanceDependencyError, YFinanceQuoteError, datetime.now, fast_info.get, float, history['Close'].dropna, len, ticker.history, ticker.info.get, yf.Ticker

_normalize_portfolio_read_user_id
File: backend/app/stacks/portfolio/accounting.py
Lines: 7-19
Matched Terms: portfolio
Calls: ValueError, str, str(user_id).strip

calculate_live_portfolio_equity
File: backend/app/stacks/portfolio/accounting.py
Lines: 22-74
Matched Terms: balance, balances, portfolio, position
Calls: _normalize_portfolio_read_user_id, async_session, float, order.signal.lower, result.scalars, result.scalars().all, select, select(OrderHistory).where, session.execute, str

calculate_position_size
File: backend/app/stacks/portfolio/allocator.py
Lines: 4-40
Matched Terms: position
Calls: float, get_bars, max, min, str

health
File: backend/app/stacks/portfolio/base.py
Lines: 19-20
Matched Terms: portfolio
Calls: NONE EXTRACTED

calculate_summary
File: backend/app/stacks/portfolio/dashboard_service.py
Lines: 10-45
Matched Terms: balance, valuation
Calls: Decimal, float, sanitized_tx_history.append, self._to_fin_decimal, tx.get, tx.get('type', '').lower

__init__
File: backend/app/stacks/portfolio/facades/readonly_portfolio_facade.py
Lines: 80-165
Matched Terms: portfolio, position, positions, snapshot
Calls: MappingProxyType, ReadOnlyPortfolioFacadeError, ReadOnlySymbolPosition, object.__setattr__, position.symbol.upper, positions_by_symbol.items, positions_by_symbol.setdefault, positions_by_symbol.setdefault(symbol, []).append, self._validate_snapshot, sorted, tuple

_validate_snapshot
File: backend/app/stacks/portfolio/facades/readonly_portfolio_facade.py
Lines: 168-264
Matched Terms: balance, balances, portfolio, position, positions, snapshot
Calls: ReadOnlyPortfolioFacadeError, isinstance, len, sum

snapshot
File: backend/app/stacks/portfolio/facades/readonly_portfolio_facade.py
Lines: 267-270
Matched Terms: portfolio, snapshot
Calls: NONE EXTRACTED

get_overview
File: backend/app/stacks/portfolio/facades/readonly_portfolio_facade.py
Lines: 272-310
Matched Terms: balance, portfolio, position, snapshot
Calls: ReadOnlyPortfolioOverview, tuple

list_accounts
File: backend/app/stacks/portfolio/facades/readonly_portfolio_facade.py
Lines: 312-387
Matched Terms: balance, balances, cost_basis, gain, portfolio, position, positions, realized, snapshot, unrealized
Calls: ReadOnlyPortfolioAccountSummary, len, sorted, summaries.append, tuple

get_account
File: backend/app/stacks/portfolio/facades/readonly_portfolio_facade.py
Lines: 389-406
Matched Terms: portfolio
Calls: ReadOnlyPortfolioFacadeError, account_id_hash.strip, account_id_hash.strip().lower, self._accounts_by_hash.get

list_positions
File: backend/app/stacks/portfolio/facades/readonly_portfolio_facade.py
Lines: 408-429
Matched Terms: position, positions
Calls: positions.extend, sorted, tuple

find_positions_by_symbol
File: backend/app/stacks/portfolio/facades/readonly_portfolio_facade.py
Lines: 431-450
Matched Terms: portfolio, position, positions
Calls: ReadOnlyPortfolioFacadeError, self._positions_by_symbol.get, symbol.strip, symbol.strip().upper

list_balances
File: backend/app/stacks/portfolio/facades/readonly_portfolio_facade.py
Lines: 452-487
Matched Terms: balance, balances, snapshot
Calls: balances.append, sorted, tuple

get_totals
File: backend/app/stacks/portfolio/facades/readonly_portfolio_facade.py
Lines: 489-492
Matched Terms: portfolio, snapshot
Calls: NONE EXTRACTED

get_symbol_index
File: backend/app/stacks/portfolio/facades/readonly_portfolio_facade.py
Lines: 494-502
Matched Terms: position, positions
Calls: NONE EXTRACTED

_principal_subject
File: backend/app/stacks/portfolio/portfolio_service.py
Lines: 9-25
Matched Terms: portfolio
Calls: ValueError, getattr, str, str(getattr(principal, 'subject', '')).strip

get_portfolio_positions_for_api
File: backend/app/stacks/portfolio/portfolio_service.py
Lines: 28-46
Matched Terms: portfolio, position, positions, snapshot
Calls: _principal_subject, get_positions_snapshot

owner_hash
File: backend/app/stacks/portfolio/portfolio_snapshot_lifecycle.py
Lines: 59-75
Matched Terms: portfolio
Calls: AuthenticatedPortfolioAccessDenied, hashlib.sha256, hashlib.sha256(normalized.encode('utf-8')).hexdigest, normalized.encode, str, str(neurovest_user_id).strip

owner_refresh_lock
File: backend/app/stacks/portfolio/portfolio_snapshot_lifecycle.py
Lines: 221-257
Matched Terms: portfolio, refresh
Calls: PortfolioRefreshInProgress, fcntl.flock, lock_file.fileno, lock_path.open, owner_directory.mkdir

get_portfolio_lifecycle
File: backend/app/stacks/portfolio/portfolio_snapshot_lifecycle.py
Lines: 369-544
Matched Terms: portfolio, refresh, snapshot
Calls: _active_path, _freshness, _history_directory, _metadata_path, _owner_directory, _read_json, active_path.is_file, datetime.fromisoformat, history_directory.glob, history_directory.is_dir, int, isinstance, len, list, metadata.get, promoted_at.astimezone, promoted_at.replace, sha256_file, stale_after.total_seconds, utc_now

_retain_history
File: backend/app/stacks/portfolio/portfolio_snapshot_lifecycle.py
Lines: 547-571
Matched Terms: snapshot
Calls: history_directory.glob, history_directory.mkdir, path.stat, path.unlink, sorted

refresh_portfolio_snapshot
File: backend/app/stacks/portfolio/portfolio_snapshot_lifecycle.py
Lines: 574-879
Matched Terms: portfolio, refresh, snapshot
Calls: Path, PortfolioSnapshotLifecycleError, _active_path, _history_directory, _metadata_path, _owner_directory, _read_json, _retain_history, active_path.is_file, active_path.read_text, asdict, atomic_write_json, build_owned_snapshot, candidate['snapshot'].get, current_time.isoformat, current_time.strftime, failed_metadata.get, failed_metadata.update, find_latest_normalized_portfolio, get_portfolio_lifecycle, hashlib.sha256, hashlib.sha256(str(qualified_source).encode('utf-8')).hexdigest, int, json.loads, max, metadata.update, owner_hash, owner_refresh_lock, qualified_source.is_file, refreshed_metadata.get, refreshed_metadata.update, sha256_file, str, str(qualified_source).encode, type, utc_now

load_active_owner_snapshot
File: backend/app/stacks/portfolio/portfolio_snapshot_lifecycle.py
Lines: 882-905
Matched Terms: portfolio, snapshot
Calls: PortfolioSnapshotLifecycleError, _active_path, _owner_directory, _read_json

rebalance_portfolio
File: backend/app/stacks/portfolio/rebalance.py
Lines: 3-12
Matched Terms: balance, portfolio
Calls: isinstance, signal.get, signal.get('signal', {}).get

resolve_reconciliation_owner_id
File: backend/app/stacks/portfolio/reconciliation.py
Lines: 29-91
Matched Terms: portfolio
Calls: OrderHistory.user_id.is_not, PortfolioInventory.user_id.is_not, async_session, inventory_result.scalars, inventory_result.scalars().all, iter, len, next, order_result.scalars, order_result.scalars().all, select, select(OrderHistory.user_id).where, select(OrderHistory.user_id).where(OrderHistory.user_id.is_not(None)).distinct, select(PortfolioInventory.user_id).where, select(PortfolioInventory.user_id).where(PortfolioInventory.user_id.is_not(None)).distinct, session.execute, str, str(owner_id).strip

run_reconciliation_audit
File: backend/app/stacks/portfolio/reconciliation.py
Lines: 94-331
Matched Terms: cost_basis, gain, portfolio, position, positions
Calls: _normalize_reconciliation_user_id, abs, async_session, audit_results['details'].append, emit_runtime_step, float, inventory_result.scalars, inventory_result.scalars().all, max, order_result.scalars, order_result.scalars().all, select, select(OrderHistory).where, select(PortfolioInventory).where, session.begin, session.execute, session.flush, str, str(order.signal).lower

start_periodic_reconciliation_daemon
File: backend/app/stacks/portfolio/reconciliation.py
Lines: 334-364
Matched Terms: portfolio
Calls: _normalize_reconciliation_user_id, asyncio.sleep, print, run_reconciliation_audit

latest_snapshot
File: backend/app/stacks/portfolio/tests/test_authenticated_owned_readonly_portfolio_api.py
Lines: 20-39
Matched Terms: portfolio, snapshot
Calls: Path, Path('runtime/snaptrade_integration').glob, path.stat, pytest.skip, sorted

configured_owner
File: backend/app/stacks/portfolio/tests/test_authenticated_owned_readonly_portfolio_api.py
Lines: 42-68
Matched Terms: portfolio
Calls: Path, Path('runtime/dev_auth/snaptrade_portfolio_owner_bindings.json').read_text, iter, json.loads, len, next, pytest.skip, registry.get

test_configured_owner_receives_two_accounts
File: backend/app/stacks/portfolio/tests/test_authenticated_owned_readonly_portfolio_api.py
Lines: 71-107
Matched Terms: balance, position, snapshot
Calls: build_owned_facade, configured_owner, latest_snapshot, serialize_overview

test_unbound_user_is_denied
File: backend/app/stacks/portfolio/tests/test_authenticated_owned_readonly_portfolio_api.py
Lines: 110-119
Matched Terms: portfolio, snapshot
Calls: build_owned_facade, latest_snapshot, pytest.raises

test_empty_principal_subject_is_denied
File: backend/app/stacks/portfolio/tests/test_authenticated_owned_readonly_portfolio_api.py
Lines: 122-129
Matched Terms: portfolio, snapshot
Calls: build_owned_facade, latest_snapshot, pytest.raises

test_owner_receives_only_bound_account_hashes
File: backend/app/stacks/portfolio/tests/test_authenticated_owned_readonly_portfolio_api.py
Lines: 132-164
Matched Terms: portfolio, snapshot
Calls: Path, Path('runtime/dev_auth/snaptrade_portfolio_owner_bindings.json').read_text, build_owned_facade, configured_owner, json.loads, latest_snapshot, serialize_accounts, set

test_read_views_are_normalized
File: backend/app/stacks/portfolio/tests/test_authenticated_owned_readonly_portfolio_api.py
Lines: 167-213
Matched Terms: balance, balances, position, positions, snapshot
Calls: all, build_owned_facade, configured_owner, isinstance, latest_snapshot, len, serialize_accounts, serialize_balances, serialize_positions, serialize_totals

test_symbol_lookup_is_owner_scoped
File: backend/app/stacks/portfolio/tests/test_authenticated_owned_readonly_portfolio_api.py
Lines: 216-236
Matched Terms: position, positions, snapshot
Calls: all, build_owned_facade, configured_owner, latest_snapshot, serialize_symbol_positions

test_no_raw_account_identifier_fields_are_returned
File: backend/app/stacks/portfolio/tests/test_authenticated_owned_readonly_portfolio_api.py
Lines: 239-273
Matched Terms: balance, balances, position, positions, snapshot
Calls: build_owned_facade, configured_owner, json.dumps, json.dumps({'accounts': serialize_accounts(facade), 'balances': serialize_balances(facade), 'positions': serialize_positions(facade)}).lower, latest_snapshot, serialize_accounts, serialize_balances, serialize_positions

test_service_records_no_network_or_database_activity
File: backend/app/stacks/portfolio/tests/test_authenticated_owned_readonly_portfolio_api.py
Lines: 276-287
Matched Terms: snapshot
Calls: build_owned_facade, configured_owner, latest_snapshot

test_paper_order_propagates_authenticated_owner
File: backend/app/stacks/portfolio/tests/test_authenticated_paper_order_api.py
Lines: 92-151
Matched Terms: balance, portfolio
Calls: AsyncMock, SimpleNamespace, main.PaperOrderRequest, main.submit_authenticated_paper_order, monkeypatch.setattr, processor.assert_awaited_once_with

test_two_orders_keep_owners_separate
File: backend/app/stacks/portfolio/tests/test_authenticated_paper_order_api.py
Lines: 155-227
Matched Terms: portfolio
Calls: AsyncMock, SimpleNamespace, main.PaperOrderRequest, main.submit_authenticated_paper_order, monkeypatch.setattr

make_principal
File: backend/app/stacks/portfolio/tests/test_authenticated_portfolio_read_boundary.py
Lines: 15-25
Matched Terms: portfolio
Calls: AuthenticatedPrincipal

test_portfolio_service_passes_principal_subject
File: backend/app/stacks/portfolio/tests/test_authenticated_portfolio_read_boundary.py
Lines: 29-71
Matched Terms: portfolio, position, positions, snapshot
Calls: make_principal, monkeypatch.setattr, portfolio_service.get_portfolio_positions_for_api

test_portfolio_service_rejects_empty_subject
File: backend/app/stacks/portfolio/tests/test_authenticated_portfolio_read_boundary.py
Lines: 75-91
Matched Terms: portfolio, position, positions
Calls: AuthenticatedPrincipal, portfolio_service.get_portfolio_positions_for_api, pytest.raises

test_paper_snapshot_rejects_empty_user_id
File: backend/app/stacks/portfolio/tests/test_authenticated_portfolio_read_boundary.py
Lines: 95-106
Matched Terms: position, positions, snapshot
Calls: get_positions_snapshot, pytest.raises

test_paper_snapshot_is_explicitly_account_scoped
File: backend/app/stacks/portfolio/tests/test_authenticated_portfolio_read_boundary.py
Lines: 110-125
Matched Terms: position, positions, snapshot
Calls: get_positions_snapshot

fake_snapshot
File: backend/app/stacks/portfolio/tests/test_authenticated_portfolio_read_boundary.py
Lines: 34-46
Matched Terms: position, positions, snapshot
Calls: NONE EXTRACTED

test_accounting_rejects_empty_owner
File: backend/app/stacks/portfolio/tests/test_authenticated_portfolio_read_isolation.py
Lines: 74-81
Matched Terms: portfolio
Calls: calculate_live_portfolio_equity, pytest.raises

test_position_route_is_authenticated_and_scoped
File: backend/app/stacks/portfolio/tests/test_authenticated_portfolio_read_isolation.py
Lines: 95-109
Matched Terms: portfolio, position, positions
Calls: function_source

test_accounting_is_owner_scoped
File: backend/app/stacks/portfolio/tests/test_authenticated_portfolio_read_isolation.py
Lines: 146-155
Matched Terms: portfolio
Calls: function_source

test_execution_propagates_owner
File: backend/app/stacks/portfolio/tests/test_authenticated_portfolio_read_isolation.py
Lines: 182-196
Matched Terms: portfolio
Calls: function_source

test_portfolio_valuation_policy_is_authenticated
File: backend/app/stacks/portfolio/tests/test_authenticated_portfolio_valuation_api.py
Lines: 15-22
Matched Terms: portfolio, valuation
Calls: resolve_route_policy

test_portfolio_valuation_route_is_registered
File: backend/app/stacks/portfolio/tests/test_authenticated_portfolio_valuation_api.py
Lines: 25-45
Matched Terms: portfolio, valuation
Calls: getattr, len, set

test_portfolio_valuation_propagates_owner
File: backend/app/stacks/portfolio/tests/test_authenticated_portfolio_valuation_api.py
Lines: 49-84
Matched Terms: balance, portfolio, valuation
Calls: AsyncMock, SimpleNamespace, accounting.assert_awaited_once_with, main.get_authenticated_portfolio_valuation, monkeypatch.setattr

test_portfolio_valuation_keeps_owners_separate
File: backend/app/stacks/portfolio/tests/test_authenticated_portfolio_valuation_api.py
Lines: 88-137
Matched Terms: balance, portfolio, valuation
Calls: AsyncMock, SimpleNamespace, main.get_authenticated_portfolio_valuation, monkeypatch.setattr

test_paper_execution_rejects_empty_user_id
File: backend/app/stacks/portfolio/tests/test_execution_ownership_propagation.py
Lines: 17-29
Matched Terms: portfolio
Calls: paper_broker.process_portfolio_output, pytest.raises

test_ledger_inventory_lookup_is_account_scoped
File: backend/app/stacks/portfolio/tests/test_execution_ownership_propagation.py
Lines: 82-102
Matched Terms: portfolio
Calls: Path, Path('backend/app/stacks/journal_ledger/ledger.py').read_text

test_orm_enforces_owned_rows
File: backend/app/stacks/portfolio/tests/test_ownership_schema_enforcement.py
Lines: 19-71
Matched Terms: portfolio
Calls: LEDGER.read_text, ast.parse, ast.unparse, ast.walk, isinstance

test_live_database_enforces_owned_rows
File: backend/app/stacks/portfolio/tests/test_ownership_schema_enforcement.py
Lines: 75-133
Matched Terms: portfolio
Calls: connection.run_sync, engine.connect, inspect, inspector.get_columns, inspector.get_unique_constraints, next

inspect_schema
File: backend/app/stacks/portfolio/tests/test_ownership_schema_enforcement.py
Lines: 77-91
Matched Terms: portfolio
Calls: inspect, inspector.get_columns, inspector.get_unique_constraints

latest_qualified_snapshot
File: backend/app/stacks/portfolio/tests/test_portfolio_snapshot_lifecycle.py
Lines: 53-72
Matched Terms: portfolio, snapshot
Calls: Path, Path('runtime/snaptrade_integration').glob, path.stat, pytest.skip, sorted

test_refresh_promotes_owner_scoped_snapshot_atomically
File: backend/app/stacks/portfolio/tests/test_portfolio_snapshot_lifecycle.py
Lines: 75-133
Matched Terms: portfolio, refresh, snapshot
Calls: configured_owner, latest_qualified_snapshot, load_active_owner_snapshot, refresh_portfolio_snapshot

test_second_refresh_preserves_last_known_good
File: backend/app/stacks/portfolio/tests/test_portfolio_snapshot_lifecycle.py
Lines: 136-174
Matched Terms: portfolio, refresh, snapshot
Calls: (owner_directories[0] / 'history').glob, configured_owner, latest_qualified_snapshot, len, list, path.is_dir, refresh_portfolio_snapshot, tmp_path.iterdir

test_failed_refresh_keeps_active_snapshot
File: backend/app/stacks/portfolio/tests/test_portfolio_snapshot_lifecycle.py
Lines: 177-227
Matched Terms: portfolio, refresh, snapshot
Calls: configured_owner, get_portfolio_lifecycle, latest_qualified_snapshot, load_active_owner_snapshot, pytest.raises, refresh_portfolio_snapshot

test_staleness_is_reported
File: backend/app/stacks/portfolio/tests/test_portfolio_snapshot_lifecycle.py
Lines: 230-271
Matched Terms: portfolio, refresh, snapshot
Calls: configured_owner, datetime, get_portfolio_lifecycle, latest_qualified_snapshot, refresh_portfolio_snapshot, timedelta

test_retention_is_bounded
File: backend/app/stacks/portfolio/tests/test_portfolio_snapshot_lifecycle.py
Lines: 274-310
Matched Terms: portfolio, refresh, snapshot
Calls: configured_owner, datetime, get_portfolio_lifecycle, latest_qualified_snapshot, range, refresh_portfolio_snapshot, timedelta

test_unbound_user_refresh_is_denied
File: backend/app/stacks/portfolio/tests/test_portfolio_snapshot_lifecycle.py
Lines: 313-325
Matched Terms: portfolio, refresh, snapshot
Calls: latest_qualified_snapshot, pytest.raises, refresh_portfolio_snapshot

test_lifecycle_contains_no_raw_owner_id
File: backend/app/stacks/portfolio/tests/test_portfolio_snapshot_lifecycle.py
Lines: 328-346
Matched Terms: portfolio, refresh, snapshot
Calls: configured_owner, get_portfolio_lifecycle, json.dumps, latest_qualified_snapshot, refresh_portfolio_snapshot

qualified_snapshot_path
File: backend/app/stacks/portfolio/tests/test_readonly_portfolio_facade.py
Lines: 18-37
Matched Terms: portfolio, snapshot
Calls: Path, Path('runtime/snaptrade_integration').glob, path.stat, pytest.skip, sorted

build_facade
File: backend/app/stacks/portfolio/tests/test_readonly_portfolio_facade.py
Lines: 40-47
Matched Terms: portfolio, snapshot
Calls: ReadOnlyPortfolioFacade, ingest_normalized_portfolio, qualified_snapshot_path

test_facade_overview
File: backend/app/stacks/portfolio/tests/test_readonly_portfolio_facade.py
Lines: 50-71
Matched Terms: balance, position
Calls: build_facade, build_facade().get_overview, set

test_lists_account_summaries
File: backend/app/stacks/portfolio/tests/test_readonly_portfolio_facade.py
Lines: 74-100
Matched Terms: balance, position
Calls: all, build_facade, facade.list_accounts, len, sum

test_unknown_account_is_rejected
File: backend/app/stacks/portfolio/tests/test_readonly_portfolio_facade.py
Lines: 121-129
Matched Terms: portfolio
Calls: build_facade, facade.get_account, pytest.raises

test_lists_all_positions
File: backend/app/stacks/portfolio/tests/test_readonly_portfolio_facade.py
Lines: 132-154
Matched Terms: position, positions
Calls: all, build_facade, build_facade().list_positions, len

test_symbol_lookup_is_normalized
File: backend/app/stacks/portfolio/tests/test_readonly_portfolio_facade.py
Lines: 165-180
Matched Terms: position, positions
Calls: all, build_facade, build_facade().find_positions_by_symbol, pytest.mark.parametrize

test_unknown_symbol_returns_empty_tuple
File: backend/app/stacks/portfolio/tests/test_readonly_portfolio_facade.py
Lines: 183-191
Matched Terms: position, positions
Calls: build_facade, build_facade().find_positions_by_symbol

test_empty_symbol_is_rejected
File: backend/app/stacks/portfolio/tests/test_readonly_portfolio_facade.py
Lines: 194-203
Matched Terms: portfolio, position, positions
Calls: build_facade, build_facade().find_positions_by_symbol, pytest.raises

test_lists_balances
File: backend/app/stacks/portfolio/tests/test_readonly_portfolio_facade.py
Lines: 206-218
Matched Terms: balance, balances
Calls: all, build_facade, build_facade().list_balances, len

test_totals_are_provider_neutral
File: backend/app/stacks/portfolio/tests/test_readonly_portfolio_facade.py
Lines: 221-226
Matched Terms: snapshot
Calls: build_facade, facade.get_totals

test_account_summary_is_immutable
File: backend/app/stacks/portfolio/tests/test_readonly_portfolio_facade.py
Lines: 238-244
Matched Terms: position
Calls: build_facade, build_facade().list_accounts, pytest.raises

test_symbol_result_is_immutable
File: backend/app/stacks/portfolio/tests/test_readonly_portfolio_facade.py
Lines: 247-258
Matched Terms: position, positions
Calls: build_facade, build_facade().find_positions_by_symbol, pytest.raises

test_facade_has_no_mutation_methods
File: backend/app/stacks/portfolio/tests/test_readonly_portfolio_facade.py
Lines: 270-300
Matched Terms: portfolio
Calls: dir, name.lower, name.startswith, set

test_facade_source_has_no_provider_import
File: backend/app/stacks/portfolio/tests/test_readonly_portfolio_facade.py
Lines: 303-378
Matched Terms: portfolio
Calls: Path, ast.parse, ast.walk, imported_module.split, imported_module.startswith, isinstance, source_path.read_text, str, violations.append

test_reconciliation_inventory_query_is_owner_scoped
File: backend/app/stacks/portfolio/tests/test_reconciliation_ownership_isolation.py
Lines: 109-133
Matched Terms: portfolio
Calls: RECONCILIATION_PATH.read_text, _function, ast.parse, ast.unparse

test_reconciliation_order_query_is_owner_and_symbol_scoped
File: backend/app/stacks/portfolio/tests/test_reconciliation_ownership_isolation.py
Lines: 136-165
Matched Terms: position
Calls: RECONCILIATION_PATH.read_text, _function, ast.parse, ast.unparse

healthcheck
File: backend/app/stacks/risk/drawdown_guard.py
Lines: 8-25
Matched Terms: balance
Calls: float, max, print, read_max_allocated_capital, str

calculate_exposure
File: backend/app/stacks/risk/exposure.py
Lines: 4-8
Matched Terms: position, positions
Calls: abs, float, len, p.get

get_account_snapshot
File: backend/app/stacks/snaptrade/adapters/readonly_adapter.py
Lines: 21-32
Matched Terms: snapshot
Calls: RuntimeError

_require_mapping
File: backend/app/stacks/snaptrade/application/normalized_portfolio_ingestion.py
Lines: 28-41
Matched Terms: portfolio
Calls: ReadOnlyPortfolioIngestionError, isinstance

_require_list
File: backend/app/stacks/snaptrade/application/normalized_portfolio_ingestion.py
Lines: 44-57
Matched Terms: portfolio
Calls: ReadOnlyPortfolioIngestionError, isinstance

_decimal_or_none
File: backend/app/stacks/snaptrade/application/normalized_portfolio_ingestion.py
Lines: 60-95
Matched Terms: portfolio
Calls: Decimal, ReadOnlyPortfolioIngestionError, isinstance, result.is_finite, str

_require_sha256
File: backend/app/stacks/snaptrade/application/normalized_portfolio_ingestion.py
Lines: 98-123
Matched Terms: portfolio
Calls: ReadOnlyPortfolioIngestionError, int, isinstance, len

_optional_text
File: backend/app/stacks/snaptrade/application/normalized_portfolio_ingestion.py
Lines: 126-142
Matched Terms: portfolio
Calls: ReadOnlyPortfolioIngestionError, isinstance, value.strip

_require_text
File: backend/app/stacks/snaptrade/application/normalized_portfolio_ingestion.py
Lines: 145-159
Matched Terms: portfolio
Calls: ReadOnlyPortfolioIngestionError, _optional_text

_validate_locked_boundary
File: backend/app/stacks/snaptrade/application/normalized_portfolio_ingestion.py
Lines: 162-219
Matched Terms: portfolio
Calls: ReadOnlyPortfolioIngestionError, document.get

_parse_balance
File: backend/app/stacks/snaptrade/application/normalized_portfolio_ingestion.py
Lines: 222-282
Matched Terms: balance, balances
Calls: ReadOnlyBalance, _decimal_or_none, _optional_text, _require_mapping, item.get

_parse_position
File: backend/app/stacks/snaptrade/application/normalized_portfolio_ingestion.py
Lines: 285-416
Matched Terms: cost_basis, gain, portfolio, position, positions, realized, unrealized
Calls: ReadOnlyPortfolioIngestionError, ReadOnlyPosition, _decimal_or_none, _optional_text, _require_mapping, _require_sha256, _require_text, _require_text(item.get('symbol'), label='position symbol').upper, item.get

_parse_account
File: backend/app/stacks/snaptrade/application/normalized_portfolio_ingestion.py
Lines: 419-565
Matched Terms: balance, balances, cost_basis, gain, portfolio, position, positions, realized, unrealized
Calls: ReadOnlyPortfolioAccount, ReadOnlyPortfolioIngestionError, _decimal_or_none, _optional_text, _parse_balance, _parse_position, _require_list, _require_mapping, _require_sha256, _require_text, bool, enumerate, item.get, len, tuple

ingest_normalized_portfolio
File: backend/app/stacks/snaptrade/application/normalized_portfolio_ingestion.py
Lines: 568-817
Matched Terms: balance, balances, cost_basis, gain, portfolio, position, positions, realized, snapshot, unrealized
Calls: Path, ReadOnlyPortfolioIngestionError, ReadOnlyPortfolioSnapshot, ReadOnlyPortfolioTotals, _decimal_or_none, _parse_account, _require_list, _require_mapping, _require_sha256, _require_text, _validate_locked_boundary, bool, calculated_fields_raw.items, document.get, enumerate, int, json.loads, len, path.read_text, seen_accounts.add, set, source_evidence_raw.items, str, sum, totals_raw.get, tuple

_normalize_user_id
File: backend/app/stacks/snaptrade/application/portfolio_owner_binding.py
Lines: 77-89
Matched Terms: portfolio
Calls: PortfolioOwnerBindingError, str, str(value).strip

_require_sha256
File: backend/app/stacks/snaptrade/application/portfolio_owner_binding.py
Lines: 92-120
Matched Terms: portfolio
Calls: PortfolioOwnerBindingError, int, isinstance, len, value.strip, value.strip().lower

hash_account_identifier
File: backend/app/stacks/snaptrade/application/portfolio_owner_binding.py
Lines: 123-137
Matched Terms: portfolio
Calls: PortfolioOwnerBindingError, account_identifier.strip, hashlib.sha256, hashlib.sha256(normalized.encode('utf-8')).hexdigest, normalized.encode

load_portfolio_owner_binding_registry
File: backend/app/stacks/snaptrade/application/portfolio_owner_binding.py
Lines: 140-274
Matched Terms: portfolio
Calls: MappingProxyType, Path, PortfolioOwnerBinding, PortfolioOwnerBindingError, PortfolioOwnerBindingRegistry, _normalize_user_id, _require_sha256, claimed_account_hashes.get, document.get, isinstance, json.loads, len, raw_bindings.items, registry_path.is_file, registry_path.read_text, set, sorted, tuple

resolve_owned_account_hashes
File: backend/app/stacks/snaptrade/application/portfolio_owner_binding.py
Lines: 277-290
Matched Terms: portfolio
Calls: load_portfolio_owner_binding_registry, registry.resolve

filter_owned_accounts
File: backend/app/stacks/snaptrade/application/portfolio_owner_binding.py
Lines: 293-328
Matched Terms: portfolio, snapshot
Calls: PortfolioOwnerBindingError, _require_sha256, resolve_owned_account_hashes, set, sorted, tuple

resolve
File: backend/app/stacks/snaptrade/application/portfolio_owner_binding.py
Lines: 56-74
Matched Terms: portfolio
Calls: PortfolioOwnerBindingNotFound, _normalize_user_id, self.bindings.get

get_account_snapshot
File: backend/app/stacks/snaptrade/contracts/readonly_provider.py
Lines: 10-13
Matched Terms: snapshot
Calls: NONE EXTRACTED

account_snapshot
File: backend/app/stacks/snaptrade/facade/snaptrade_readonly_facade.py
Lines: 15-16
Matched Terms: snapshot
Calls: self.provider.get_account_snapshot

get_account_snapshot
File: backend/app/stacks/snaptrade/providers/disabled_provider.py
Lines: 8-13
Matched Terms: snapshot
Calls: RuntimeError

get_account_snapshot
File: backend/app/stacks/snaptrade/providers/mock_provider.py
Lines: 10-23
Matched Terms: balance, balances, position, positions, snapshot
Calls: SnapTradeAccountSnapshot, SnapTradeBalanceSnapshot

qualified_snapshot_path
File: backend/app/stacks/snaptrade/tests/test_normalized_portfolio_ingestion.py
Lines: 15-34
Matched Terms: portfolio, snapshot
Calls: Path, Path('runtime/snaptrade_integration').glob, path.stat, pytest.skip, sorted

load_source
File: backend/app/stacks/snaptrade/tests/test_normalized_portfolio_ingestion.py
Lines: 37-42
Matched Terms: snapshot
Calls: json.loads, qualified_snapshot_path, qualified_snapshot_path().read_text

write_mutated
File: backend/app/stacks/snaptrade/tests/test_normalized_portfolio_ingestion.py
Lines: 45-64
Matched Terms: portfolio
Calls: json.dumps, target.write_text

test_ingests_qualified_snapshot
File: backend/app/stacks/snaptrade/tests/test_normalized_portfolio_ingestion.py
Lines: 67-118
Matched Terms: balance, portfolio, position, positions, snapshot
Calls: all, ingest_normalized_portfolio, qualified_snapshot_path, set

test_contract_is_immutable
File: backend/app/stacks/snaptrade/tests/test_normalized_portfolio_ingestion.py
Lines: 121-129
Matched Terms: portfolio, snapshot
Calls: ingest_normalized_portfolio, pytest.raises, qualified_snapshot_path

test_rejects_unsafe_top_level_flags
File: backend/app/stacks/snaptrade/tests/test_normalized_portfolio_ingestion.py
Lines: 164-183
Matched Terms: portfolio
Calls: ingest_normalized_portfolio, load_source, pytest.mark.parametrize, pytest.raises, write_mutated

test_rejects_wrong_schema
File: backend/app/stacks/snaptrade/tests/test_normalized_portfolio_ingestion.py
Lines: 186-203
Matched Terms: portfolio
Calls: ingest_normalized_portfolio, load_source, pytest.raises, write_mutated

test_rejects_wrong_schema_version
File: backend/app/stacks/snaptrade/tests/test_normalized_portfolio_ingestion.py
Lines: 206-223
Matched Terms: portfolio
Calls: ingest_normalized_portfolio, load_source, pytest.raises, write_mutated

test_rejects_raw_account_identifier
File: backend/app/stacks/snaptrade/tests/test_normalized_portfolio_ingestion.py
Lines: 226-245
Matched Terms: portfolio
Calls: ingest_normalized_portfolio, load_source, pytest.raises, write_mutated

test_rejects_position_count_drift
File: backend/app/stacks/snaptrade/tests/test_normalized_portfolio_ingestion.py
Lines: 248-265
Matched Terms: portfolio, position
Calls: ingest_normalized_portfolio, load_source, pytest.raises, write_mutated

test_does_not_import_snaptrade_sdk
File: backend/app/stacks/snaptrade/tests/test_normalized_portfolio_ingestion.py
Lines: 268-278
Matched Terms: portfolio
Calls: Path, Path(adapter.__file__).read_text

write_registry
File: backend/app/stacks/snaptrade/tests/test_portfolio_owner_binding.py
Lines: 18-44
Matched Terms: portfolio
Calls: json.dumps, path.write_text

test_empty_registry_fails_closed
File: backend/app/stacks/snaptrade/tests/test_portfolio_owner_binding.py
Lines: 47-61
Matched Terms: portfolio
Calls: pytest.raises, resolve_owned_account_hashes, write_registry

test_rejects_cross_owner_account_reuse
File: backend/app/stacks/snaptrade/tests/test_portfolio_owner_binding.py
Lines: 102-127
Matched Terms: portfolio
Calls: hash_account_identifier, load_portfolio_owner_binding_registry, pytest.raises, write_registry

test_filters_snapshot_accounts_to_owner
File: backend/app/stacks/snaptrade/tests/test_portfolio_owner_binding.py
Lines: 130-159
Matched Terms: snapshot
Calls: filter_owned_accounts, hash_account_identifier, write_registry

test_rejects_binding_to_absent_snapshot_account
File: backend/app/stacks/snaptrade/tests/test_portfolio_owner_binding.py
Lines: 162-192
Matched Terms: portfolio, snapshot
Calls: filter_owned_accounts, hash_account_identifier, pytest.raises, write_registry

test_rejects_empty_user_id
File: backend/app/stacks/snaptrade/tests/test_portfolio_owner_binding.py
Lines: 203-219
Matched Terms: portfolio
Calls: pytest.mark.parametrize, pytest.raises, resolve_owned_account_hashes, write_registry

generate_strategy_decision
File: backend/app/stacks/strategy/engine.py
Lines: 8-102
Matched Terms: balance, portfolio
Calls: float, generate_signal, get_bars, get_latest_price, isinstance, portfolio_output.get, rebalance_portfolio, str, str(action).upper, strategy_signal.get

generate_signal
File: backend/app/stacks/strategy/signal.py
Lines: 11-48
Matched Terms: gain, loss
Calls: abs, action.upper, float, len, np.diff, np.mean, np.where, round

extract_learning_features
File: backend/app/stacks/strategy_candidate_sandbox/learning_feature_extractor.py
Lines: 62-100
Matched Terms: position
Calls: _num, all, row.get

build_empty_replay_metrics_contract
File: backend/app/stacks/strategy_candidate_sandbox/replay_metrics_contract.py
Lines: 42-72
Matched Terms: loss
Calls: SAFETY_LOCKS.copy

generate_bar_only_metrics
File: backend/app/stacks/strategy_candidate_sandbox/replay_metrics_generator.py
Lines: 28-102
Matched Terms: loss
Calls: SAFETY_LOCKS.copy, _num, bar.get, closes.append, isinstance, len, math.sqrt, range, returns.append, sum

build_locked_risk_gate
File: backend/app/stacks/strategy_candidate_sandbox/risk_gate_contract.py
Lines: 29-52
Matched Terms: position
Calls: SAFETY_LOCKS.copy

validate_unsafe_passed_risk_gate_is_rejected
File: backend/app/stacks/strategy_candidate_sandbox/risk_gate_validator.py
Lines: 34-60
Matched Terms: position
Calls: SAFETY_LOCKS.copy, SAFETY_LOCKS.values, all, checks.values, dict, unsafe.get, validate_risk_gate_locked, validation.get

_monitor_and_process_signals_core
File: backend/app/stacks/wolfden_ai/agent_router.py
Lines: 16-46
Matched Terms: portfolio
Calls: build_portfolio_output_result, drawdown_healthcheck, drawdown_status.get, generate_strategy_decision, is_kill_switch_active, print, record_wolfden_observation, set_kill_switch, str, time.time

record_wolfden_observation
File: backend/app/stacks/wolfden_ai/observability_boundary.py
Lines: 174-234
Matched Terms: portfolio
Calls: WolfdenObservation, _LOGGER.info, _freeze_value, enumerate, kwargs.items, kwargs.pop, observation.to_dict, payload_items.extend, sorted, str, str(event_name_value).strip, tuple

build_portfolio_output_result
File: backend/app/stacks/wolfden_ai/portfolio_output_result_facade.py
Lines: 188-228
Matched Terms: portfolio
Calls: WolfdenPortfolioOutputResult, _freeze_value, enumerate, kwargs.items, payload_items.extend, sorted, str, tuple

__post_init__
File: backend/app/stacks/wolfden_ai/portfolio_output_result_facade.py
Lines: 109-135
Matched Terms: portfolio
Calls: ValueError, self.status.strip

test_valid_structured_output_is_parsed
File: backend/app/stacks/wolfden_ai/tests/test_local_model_binding.py
Lines: 101-107
Matched Terms: position
Calls: parse_local_model_output

test_boundary_owns_no_persistence_or_execution
File: backend/app/stacks/wolfden_ai/tests/test_observability_boundary.py
Lines: 270-314
Matched Terms: portfolio
Calls: _calls, _imports, any, call.split, module.lower

test_result_is_immutable
File: backend/app/stacks/wolfden_ai/tests/test_portfolio_output_result_facade.py
Lines: 115-123
Matched Terms: portfolio
Calls: build_portfolio_output_result, pytest.raises

test_result_is_non_executable
File: backend/app/stacks/wolfden_ai/tests/test_portfolio_output_result_facade.py
Lines: 126-135
Matched Terms: portfolio
Calls: build_portfolio_output_result

test_result_rejects_executable_state
File: backend/app/stacks/wolfden_ai/tests/test_portfolio_output_result_facade.py
Lines: 138-150
Matched Terms: portfolio
Calls: WolfdenPortfolioOutputResult, pytest.raises

test_payload_is_deeply_frozen
File: backend/app/stacks/wolfden_ai/tests/test_portfolio_output_result_facade.py
Lines: 153-183
Matched Terms: portfolio
Calls: build_portfolio_output_result, dict, original['symbols'].append

test_result_has_serializable_mapping_contract
File: backend/app/stacks/wolfden_ai/tests/test_portfolio_output_result_facade.py
Lines: 186-204
Matched Terms: portfolio
Calls: build_portfolio_output_result, dict, result.to_dict

test_agent_router_uses_wolfden_facade_only
File: backend/app/stacks/wolfden_ai/tests/test_portfolio_output_result_facade.py
Lines: 207-219
Matched Terms: portfolio
Calls: _imports

test_wolfden_owns_no_execution_or_mutation_capability
File: backend/app/stacks/wolfden_ai/tests/test_portfolio_output_result_facade.py
Lines: 222-296
Matched Terms: portfolio
Calls: WOLFDEN_ROOT.rglob, _calls, _imports, any, call.split, forbidden_calls.append, forbidden_imports.append, module.split, path.name.startswith, path.relative_to, path.relative_to(ROOT).as_posix, sorted

isolated_state
File: backend/app/test/test_graph_event_metrics.py
Lines: 8-22
Matched Terms: snapshot
Calls: CognitiveGraphState, state.edge_activity.clear, state.edge_meta.clear, state.last_events.clear, state.node_meta.clear, state.node_state.clear, state.recent_flows.clear

test_snapshot_advertises_metric_contract_version_two
File: backend/app/test/test_graph_event_metrics.py
Lines: 205-229
Matched Terms: snapshot
Calls: isolated_state, state.snapshot

isolated_state
File: backend/app/test/test_stage8f_graph_materialization.py
Lines: 10-24
Matched Terms: snapshot
Calls: CognitiveGraphState, state.edge_activity.clear, state.edge_meta.clear, state.last_events.clear, state.node_meta.clear, state.node_state.clear, state.recent_flows.clear

test_required_facades_are_declared_in_l3
File: backend/app/test/test_stage8f_graph_materialization.py
Lines: 47-67
Matched Terms: portfolio
Calls: NONE EXTRACTED

test_frontend_workspaces_and_proxies_are_declared
File: backend/app/test/test_stage8f_graph_materialization.py
Lines: 70-95
Matched Terms: portfolio
Calls: NONE EXTRACTED

test_snapshot_materializes_declared_topology_without_events
File: backend/app/test/test_stage8f_graph_materialization.py
Lines: 98-146
Matched Terms: snapshot
Calls: all, isolated_state, len, snapshot['edges'].values, snapshot['node_meta'].values, state.snapshot

test_real_node_activation_overrides_declared_state
File: backend/app/test/test_stage8f_graph_materialization.py
Lines: 149-188
Matched Terms: snapshot
Calls: isolated_state, state.activate_node, state.snapshot

test_real_edge_materializes_both_endpoints
File: backend/app/test/test_stage8f_graph_materialization.py
Lines: 191-240
Matched Terms: snapshot
Calls: isolated_state, state.activate_edge, state.snapshot

test_declared_edge_becomes_observed_without_losing_relation
File: backend/app/test/test_stage8f_graph_materialization.py
Lines: 243-277
Matched Terms: snapshot
Calls: isolated_state, state.activate_edge, state.snapshot

test_stage8f_preserves_version_two_contract
File: backend/app/test/test_stage8f_graph_materialization.py
Lines: 280-308
Matched Terms: snapshot
Calls: isolated_state, isolated_state().snapshot

test_historical_nodes_do_not_materialize_as_unassigned
File: backend/app/test/test_stage8f_historical_node_assignment.py
Lines: 63-89
Matched Terms: snapshot
Calls: EXPECTED.items, graph_state.snapshot

test_graph_contains_no_unassigned_nodes
File: backend/app/test/test_stage8f_historical_node_assignment.py
Lines: 92-107
Matched Terms: snapshot
Calls: graph_state.snapshot, meta.get, set, snapshot['node_meta'].items

test_contract_version_two_is_preserved
File: backend/app/test/test_stage8f_historical_node_assignment.py
Lines: 110-126
Matched Terms: snapshot
Calls: graph_state.snapshot

test_trading_pipeline_success
File: backend/app/test/test_trading_pipeline.py
Lines: 174-319
Matched Terms: balance, portfolio
Calls: AsyncMock, ExitStack, MagicMock, _assert_isolated_output, _patch_symbol_everywhere, capsys.readouterr, process_portfolio_output

test_trading_pipeline_blocked
File: backend/app/test/test_trading_pipeline.py
Lines: 323-436
Matched Terms: balance, portfolio
Calls: AsyncMock, ExitStack, MagicMock, _assert_isolated_output, _patch_symbol_everywhere, any, capsys.readouterr, isinstance, payload.get, process_portfolio_output

test_agent_router_trips_kill_switch
File: backend/app/test/test_trading_pipeline.py
Lines: 440-646
Matched Terms: portfolio
Calls: AsyncMock, ExitStack, MagicMock, _assert_isolated_output, _patch_symbol_everywhere, asyncio.wait_for, capsys.readouterr, hasattr, inspect.getmodule, monitor_and_process_signals, patch.object, stack.enter_context

Repository and Persistence Files

backend/app/stacks/chat_public/conversation_store.py
backend/app/stacks/chat_public/persistence/chat_models.py
backend/app/stacks/identity_auth/tests/test_identity_persistence_models.py
backend/app/stacks/identity_auth/tests/test_refresh_session_persistence.py
backend/app/stacks/identity_auth/tests/test_stage5b_a_durable_revocation_repository.py
backend/app/stacks/journal_ledger/decision_event_repository.py

Database Model Files

backend/app/stacks/chat_public/cognitive_model_router.py
backend/app/stacks/chat_public/persistence/chat_models.py
backend/app/stacks/chat_public/tests/test_cognitive_model_router.py
backend/app/stacks/db_runtime/model_registry.py
backend/app/stacks/identity_auth/__init__.py
backend/app/stacks/identity_auth/access_token_revocation_models.py
backend/app/stacks/identity_auth/admin_mutation_service.py
backend/app/stacks/identity_auth/admin_read_models.py
backend/app/stacks/identity_auth/api_dependencies.py
backend/app/stacks/identity_auth/api_models.py
backend/app/stacks/identity_auth/api_router.py
backend/app/stacks/identity_auth/authorization_policy.py
backend/app/stacks/identity_auth/contracts.py
backend/app/stacks/identity_auth/dev_owner_provisioner.py
backend/app/stacks/identity_auth/login_service.py
backend/app/stacks/identity_auth/mock_runtime.py
backend/app/stacks/identity_auth/models.py
backend/app/stacks/identity_auth/password_change_service.py
backend/app/stacks/identity_auth/refresh_token_hashing.py
backend/app/stacks/identity_auth/repositories.py
backend/app/stacks/identity_auth/route_protection.py
backend/app/stacks/identity_auth/runtime_adapter.py
backend/app/stacks/identity_auth/service_contracts.py
backend/app/stacks/identity_auth/session_lifecycle_service.py
backend/app/stacks/identity_auth/session_service.py
backend/app/stacks/identity_auth/tests/test_api_dependency.py
backend/app/stacks/identity_auth/tests/test_api_route_contract.py
backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py
backend/app/stacks/identity_auth/tests/test_canonical_router_inclusion.py
backend/app/stacks/identity_auth/tests/test_identity_persistence_models.py
backend/app/stacks/identity_auth/tests/test_login_service.py
backend/app/stacks/identity_auth/tests/test_refresh_rotation.py
backend/app/stacks/identity_auth/tests/test_refresh_session_persistence.py
backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py
backend/app/stacks/identity_auth/tests/test_registration_service.py
backend/app/stacks/identity_auth/tests/test_runtime_adapter.py
backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
backend/app/stacks/identity_auth/tests/test_stage4f_canonical_claim_propagation.py
backend/app/stacks/identity_auth/tests/test_stage4f_environment_token_issuer_contract.py
backend/app/stacks/identity_auth/tests/test_stage4f_login_refresh_claims.py
backend/app/stacks/identity_auth/tests/test_stage4f_mock_identity_contract.py
backend/app/stacks/identity_auth/tests/test_stage4f_rotated_refresh_claims.py
backend/app/stacks/identity_auth/tests/test_stage4f_session_lifecycle_runtime_wiring.py
backend/app/stacks/identity_auth/tests/test_stage5b_a_durable_revocation_repository.py
backend/app/stacks/identity_auth/tests/test_stage5b_b_durable_bearer_logout.py
backend/app/stacks/identity_auth/tests/test_stage5b_c_revocation_observability_cleanup.py
backend/app/stacks/identity_auth/tests/test_stage9d_b_forced_password_change.py
backend/app/stacks/identity_auth/tests/test_stage9d_c2_admin_read_models.py
backend/app/stacks/identity_auth/tests/test_token_contract.py
backend/app/stacks/identity_auth/tokens.py
backend/app/stacks/journal_ledger/decision_event_model.py
backend/app/stacks/portfolio/read_models/readonly_portfolio_snapshot.py
backend/app/stacks/snaptrade/contracts/readonly_models.py
backend/app/stacks/wolfden_ai/tests/test_local_model_binding.py

Request and Response Schema Files

backend/app/schemas/dashboard.py
backend/app/stacks/chat_public/contracts/chat_contracts.py
backend/app/stacks/chat_public/developer_response_builder.py
backend/app/stacks/chat_public/math_tools/contracts.py
backend/app/stacks/chat_public/response_verification.py
backend/app/stacks/chat_public/tests/test_developer_response_builder.py
backend/app/stacks/chat_public/tests/test_live_response_verification.py
backend/app/stacks/chat_public/tests/test_response_verification.py
backend/app/stacks/identity_auth/contracts.py
backend/app/stacks/identity_auth/service_contracts.py
backend/app/stacks/identity_auth/tests/test_api_route_contract.py
backend/app/stacks/identity_auth/tests/test_stage4f_environment_token_issuer_contract.py
backend/app/stacks/identity_auth/tests/test_stage4f_mock_identity_contract.py
backend/app/stacks/identity_auth/tests/test_token_contract.py
backend/app/stacks/journal_ledger/tests/test_decision_event_contract.py
backend/app/stacks/market_data/dto.py
backend/app/stacks/market_data/provider_contract.py
backend/app/stacks/portfolio/tests/test_ownership_schema_enforcement.py
backend/app/stacks/snaptrade/contracts/readonly_models.py
backend/app/stacks/snaptrade/contracts/readonly_provider.py
backend/app/stacks/strategy_candidate_sandbox/exit_signal_rule_contract.py
backend/app/stacks/strategy_candidate_sandbox/replay_metrics_contract.py
backend/app/stacks/strategy_candidate_sandbox/risk_gate_contract.py
backend/app/stacks/strategy_candidate_sandbox/training_observability_contract.py

Service Files

backend/app/spine/L5_api/owned_readonly_portfolio_service.py
backend/app/stacks/identity_auth/admin_mutation_service.py
backend/app/stacks/identity_auth/login_service.py
backend/app/stacks/identity_auth/password_change_service.py
backend/app/stacks/identity_auth/service_contracts.py
backend/app/stacks/identity_auth/session_lifecycle_service.py
backend/app/stacks/identity_auth/session_service.py
backend/app/stacks/identity_auth/tests/test_login_service.py
backend/app/stacks/identity_auth/tests/test_registration_service.py
backend/app/stacks/portfolio/dashboard_service.py
backend/app/stacks/portfolio/portfolio_service.py

Facade Files

backend/app/stacks/journal_ledger/decision_audit_query_facade.py
backend/app/stacks/portfolio/facades/readonly_portfolio_facade.py
backend/app/stacks/portfolio/tests/test_readonly_portfolio_facade.py
backend/app/stacks/snaptrade/facade/snaptrade_readonly_facade.py
backend/app/stacks/wolfden_ai/portfolio_output_result_facade.py
backend/app/stacks/wolfden_ai/tests/test_portfolio_output_result_facade.py

Provider Files

backend/app/stacks/market_data/provider_contract.py
backend/app/stacks/market_data/provider_registry.py
backend/app/stacks/market_data/yfinance_provider.py
backend/app/stacks/snaptrade/contracts/readonly_provider.py
backend/app/stacks/snaptrade/providers/disabled_provider.py
backend/app/stacks/snaptrade/providers/mock_provider.py

Snapshot Files

backend/app/stacks/portfolio/portfolio_snapshot_lifecycle.py
backend/app/stacks/portfolio/read_models/readonly_portfolio_snapshot.py
backend/app/stacks/portfolio/tests/test_portfolio_snapshot_lifecycle.py

Security

authentication_markers_detected

True

authorization_markers_detected

True

ownership_markers_detected

True

read_only_markers_detected

True

csrf_markers_detected

False

rate_limit_markers_detected

True

commit_markers_detected

True

rollback_markers_detected

True

account_scope_markers_detected

True

symbol_normalization_detected

True

Loading Behaviour

loading_state_detected

True

error_state_detected

True

empty_state_detected

True

refresh_state_detected

True

retry_state_detected

False

stale_state_detected

True

last_updated_detected

False

responsive_layout_detected

True

accessibility_markers_detected

True

Failure Paths

Missing Session

Expected: deny portfolio access and redirect to login.

Status: UNVERIFIED

Expired Session

Expected: refresh recovery or login redirect.

Status: UNVERIFIED

Cross-User Portfolio Request

Expected: deny access and return no other user's data.

Status: OWNERSHIP MARKERS DETECTED — LIVE TEST REQUIRED

Empty Portfolio

Empty state detected

Portfolio Provider Failure

Expected: show unavailable or stale data state.

Status: UNVERIFIED

Database Failure

Error state detected

Refresh Failure

Refresh state detected

Partial Position Failure

UNVERIFIED

Tests

backend/app/stacks/chat_public/tests/test_aiq004d3_runtime_branch_repairs.py

test_software_debugging_reaches_coder_generation
test_explicit_developer_review_remains_deterministic
test_http_is_not_extracted_as_a_symbol
test_real_uppercase_ticker_can_still_be_extracted
test_nonfinancial_intent_never_creates_strategy_candidate
test_financial_strategy_intent_remains_eligible

backend/app/stacks/chat_public/tests/test_capability_state_registry.py

test_registry_is_read_only_and_complete
test_registry_uses_declared_state_categories
test_drawdown_guard_is_not_called_without_balance
test_registry_summary_is_grounded_in_rows
test_developer_response_contains_capability_state
test_developer_capabilities_remain_grounded
test_unverified_adapter_and_async_states_require_attention

backend/app/stacks/chat_public/tests/test_chat_intent_regex.py

test_detect_chat_intent_v2_metadata_and_legacy_compatibility
test_developer_pronoun_i_is_not_detected_as_ticker
test_market_symbol_is_preserved
test_blocked_live_execution_remains_fail_closed
test_chat_intent_legacy_constructor_remains_valid

backend/app/stacks/chat_public/tests/test_cognitive_model_router.py

test_routing_decision_is_immutable
test_general_greeting_uses_fast_model
test_analysis_and_strategy_use_reason_model
test_code_work_uses_code_model
test_math_declares_deterministic_tool_requirement
test_current_or_account_data_declares_retrieval
test_decision_serializes_complete_contract
test_exact_authenticated_math_prompt_requires_deterministic_tool
test_exact_authenticated_research_prompt_requires_retrieval
test_common_math_phrasing_requires_deterministic_tool
test_local_research_phrasing_requires_retrieval
test_position_size_uses_math_without_retrieval
test_conversation_memory_avoids_retrieval
test_explicit_retrieval_requests_remain_enabled
test_strategy_family_retains_retrieval_contract
test_market_and_portfolio_family_do_not_force_retrieval
test_router_never_exposes_execution_authority

backend/app/stacks/chat_public/tests/test_deterministic_math_engine.py

test_registry_is_explicit_and_complete
test_exact_decimal_arithmetic
test_percentage_of
test_percent_change
test_simple_return
test_compound_return
test_cagr
test_expected_value
test_risk_reward
test_position_size
test_portfolio_weights
test_descriptive_statistics
test_sharpe_ratio_is_deterministic
test_sortino_ratio_is_deterministic
test_maximum_drawdown
test_trade_statistics
test_invalid_inputs_fail_closed
test_unsupported_operation_fails_closed
test_sequence_boundary_is_enforced
test_non_finite_or_invalid_values_are_rejected
test_serialized_result_contains_no_float_values
test_math_engine_has_no_execution_or_network_authority

backend/app/stacks/chat_public/tests/test_developer_context_overlay.py

test_general_conversation_does_not_load_developer_overlay
test_self_evaluation_adds_grounded_developer_requirements
test_architecture_mode_adds_architecture_review_rules
test_developer_repo_and_architecture_context_are_bounded

backend/app/stacks/chat_public/tests/test_developer_response_builder.py

test_developer_response_is_structured
test_developer_response_does_not_claim_unverified_tests
test_developer_runtime_bypasses_ollama
test_developer_claim_without_permission_uses_ollama
test_general_conversation_still_uses_ollama

backend/app/stacks/chat_public/tests/test_live_math_runtime_integration.py

test_supported_math_requests_are_extracted
test_percentage_result_is_exact
test_cagr_result_is_deterministic
test_position_size_uses_whole_units
test_unrequested_math_does_not_execute
test_ambiguous_math_fails_controlled
test_division_by_zero_returns_error_evidence
test_runtime_contains_math_integration
test_live_math_has_no_arbitrary_execution

backend/app/stacks/chat_public/tests/test_live_rag_activation.py

test_strategy_family_requests_retrieval
test_retrieval_is_not_called_when_not_requested
test_retrieval_filters_injection_chunks_and_bounds_top_k
test_prompt_contains_page_aware_citation
test_prompt_respects_total_character_boundary
test_retrieval_failure_returns_controlled_bundle
test_chat_runtime_contains_live_rag_integration
test_live_rag_module_does_not_enable_execution

backend/app/stacks/chat_public/tests/test_live_response_verification.py

test_verifier_replaces_missing_math_result
test_verifier_preserves_exact_math_result
test_verifier_replaces_live_execution_claim
test_runtime_verification_occurs_before_persistence
test_runtime_emits_verification_event
test_runtime_persists_verification_evidence
test_runtime_exposes_verification_metadata

backend/app/stacks/chat_public/tests/test_local_rag_index.py

test_chunking_is_deterministic
test_chunking_rejects_invalid_overlap
test_stable_identifiers_are_repeatable
test_source_policy_rejects_secrets_and_runtime
test_prompt_injection_is_detected
test_ingestion_deduplicates_identical_content
test_semantic_retrieval_ranks_relevant_chunk_first
test_no_result_behavior_is_controlled
test_index_contract_contains_no_execution_authority

backend/app/stacks/chat_public/tests/test_prompt_composer.py

test_composer_preserves_existing_section_delimiter
test_composer_uses_supplied_existing_bounder
test_composer_reports_character_metadata
test_composer_materializes_iterables_once
test_composer_rejects_invalid_limit
test_composer_rejects_non_string_bounder_result
test_prompt_composition_is_immutable

backend/app/stacks/chat_public/tests/test_public_chat_controls.py

test_public_chat_contract_accepts_valid_text
test_public_chat_contract_rejects_empty_text
test_public_chat_contract_rejects_oversized_text
test_public_chat_safety_denies_restricted_action
test_public_chat_safety_allows_general_discussion
test_public_chat_timeout_maps_to_504
test_public_chat_dependency_failure_maps_to_503
test_public_chat_rate_limit_maps_to_429
test_public_chat_safety_denial_maps_to_403
test_route_is_decorated_with_public_controls
test_public_control_wrapper_preserves_signature
test_payload_boundary_ignores_injected_dependencies
test_payload_boundary_rejects_oversized_payload
test_payload_boundary_rejects_empty_payload
test_payload_boundary_safety_uses_only_payload
test_payload_boundary_still_rejects_restricted_payload
test_missing_payload_argument_fails_closed
test_configured_payload_wrapper_preserves_signature
test_chat_route_configures_payload_argument

backend/app/stacks/chat_public/tests/test_response_verification.py

test_ordinary_response_passes
test_exact_math_result_passes
test_decimal_equivalent_math_result_passes
test_missing_math_result_is_repaired
test_position_size_result_passes
test_allowed_citation_passes
test_missing_required_citation_is_repaired
test_unapproved_citation_is_repaired
test_live_execution_claim_fails_closed
test_safe_live_execution_denial_passes
test_empty_response_fails_closed
test_result_serialization_is_structured
test_verifier_has_no_external_authority

backend/app/stacks/chat_public/tests/test_role_overlay_injection.py

test_role_overlay_is_inserted_in_correct_order
test_no_overlay_path_remains_supported
test_chat_api_passes_principal_to_runtime
test_runtime_passes_overlay_and_intent_metadata
test_unknown_role_fails_closed_to_user_overlay
test_deterministic_developer_path_remains_grounded

backend/app/stacks/identity_auth/tests/test_api_dependency.py

test_missing_bearer_credentials_are_unauthorized
test_wrong_scheme_is_unauthorized
test_valid_access_token_returns_principal
test_refresh_token_is_rejected_by_api_dependency
test_malformed_token_is_unauthorized

backend/app/stacks/identity_auth/tests/test_api_route_contract.py

test_registration_contract
test_registration_failure_is_generic
test_login_contract
test_login_failure_is_generic
test_router_is_activated_in_canonical_app

backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py

test_route_policy_inventory
test_public_route_requires_no_token
test_authenticated_route_rejects_missing_token
test_authenticated_route_accepts_principal
test_admin_route_rejects_non_admin
test_admin_route_accepts_server_claim
test_unknown_route_preserves_not_found
test_refresh_token_validation_failure_is_unauthorized

backend/app/stacks/identity_auth/tests/test_canonical_router_inclusion.py

test_canonical_source_includes_auth_router_once
test_auth_router_has_complete_session_lifecycle
test_controlled_local_registration_and_login

backend/app/stacks/identity_auth/tests/test_identity_persistence_models.py

test_identity_user_schema_contract
test_refresh_session_schema_contract
test_email_normalization_is_canonical
test_refresh_token_hash_never_contains_raw_token

backend/app/stacks/identity_auth/tests/test_login_service.py

test_valid_login_issues_separate_tokens_and_session
test_unknown_user_and_wrong_password_share_error
test_disabled_account_fails_closed
test_inactive_status_fails_closed
test_refresh_session_failure_rolls_back
test_identical_tokens_fail_closed

backend/app/stacks/identity_auth/tests/test_refresh_rotation.py

test_refresh_rotation_revokes_previous_token
test_refresh_token_cannot_be_rotated_twice

backend/app/stacks/identity_auth/tests/test_refresh_session_persistence.py

test_rotation_preserves_family_and_revokes_old
test_reuse_revokes_entire_family
test_logout_is_idempotent

backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py

test_complete_mock_registration_and_login_flow
test_duplicate_registration_rolls_back
test_unknown_and_wrong_password_share_error
test_disabled_account_rejected_before_token_issuance
test_access_token_failure_rolls_back
test_refresh_token_failure_rolls_back
test_refresh_session_failure_rolls_back
test_registration_commit_failure_fails_closed
test_login_commit_failure_fails_closed

backend/app/stacks/identity_auth/tests/test_registration_service.py

test_registration_normalizes_and_hashes_password
test_duplicate_registration_fails_generically
test_registration_hash_failure_rolls_back
test_empty_password_fails_closed

backend/app/stacks/identity_auth/tests/test_runtime_adapter.py

test_runtime_construction_is_non_mutating
test_runtime_fails_closed_without_secret
test_real_access_and_refresh_token_paths

backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py

test_lifecycle_route_policy_inventory
test_refresh_returns_rotated_pair
test_logout_revokes_current_refresh_session
test_refresh_rejection_is_unauthorized
test_logout_rejection_is_unauthorized
test_logout_all_uses_access_principal_subject
test_logout_all_rejects_missing_access_token
test_refresh_request_forbids_extra_fields
test_logout_request_forbids_extra_fields

backend/app/stacks/identity_auth/tests/test_stage4f_canonical_claim_propagation.py

test_login_issues_canonical_role_and_tier_claims
test_login_rejects_invalid_stored_role
test_refresh_uses_current_user_claims
test_refresh_rejects_missing_current_user

backend/app/stacks/identity_auth/tests/test_stage4f_environment_token_issuer_contract.py

test_environment_issuer_signatures_accept_extra_claims
test_environment_access_issuer_forwards_claims
test_environment_refresh_issuer_forwards_claims

backend/app/stacks/identity_auth/tests/test_stage4f_login_refresh_claims.py

test_login_forwards_canonical_claims_to_both_tokens

backend/app/stacks/identity_auth/tests/test_stage4f_mock_identity_contract.py

test_mock_access_issuer_accepts_and_records_claims
test_mock_refresh_issuer_accepts_and_records_claims
test_mock_issuer_signatures_match_claim_contract
test_mock_registration_result_remains_registration_contract
test_mock_registration_login_flow_accepts_claim_propagation

backend/app/stacks/identity_auth/tests/test_stage4f_rotated_refresh_claims.py

test_rotated_refresh_token_receives_canonical_claims

backend/app/stacks/identity_auth/tests/test_stage4f_session_lifecycle_runtime_wiring.py

test_session_lifecycle_runtime_builds_user_repository
test_session_lifecycle_runtime_uses_one_shared_session

backend/app/stacks/identity_auth/tests/test_stage5b_a_durable_revocation_repository.py

test_revocation_model_exposes_only_safe_fields
test_revocation_token_id_is_unique
test_repository_rejects_invalid_identifiers
test_repository_rejects_invalid_lifetime

backend/app/stacks/identity_auth/tests/test_stage5b_b_durable_bearer_logout.py

test_logout_persists_access_and_refresh_revocation_before_commit
test_logout_rolls_back_both_revocations_on_failure
test_logout_rejects_access_refresh_subject_mismatch

backend/app/stacks/identity_auth/tests/test_stage5b_c_revocation_observability_cleanup.py

test_revocation_routes_are_get_only
test_revocation_summary_exposes_no_jti
test_cleanup_service_commits_success
test_cleanup_service_rolls_back_failure

backend/app/stacks/identity_auth/tests/test_stage9d_b_forced_password_change.py

test_replacement_password_policy_rejects_weak_values
test_replacement_password_policy_accepts_strong_value
test_required_password_change_updates_hash_and_revokes_sessions
test_wrong_temporary_password_fails_closed

backend/app/stacks/identity_auth/tests/test_stage9d_c2_admin_read_models.py

test_user_models_expose_no_secrets
test_session_models_expose_no_secrets
test_admin_routes_are_get_only
test_admin_dependency_is_database_authoritative
test_read_service_does_not_serialize_secret_fields
test_openapi_contains_only_expected_admin_methods
test_no_password_reset_route_added_in_c2

backend/app/stacks/identity_auth/tests/test_token_contract.py

test_missing_secret_fails_closed
test_access_token_round_trip
test_refresh_token_is_not_accepted_as_access
test_access_token_is_not_accepted_as_refresh
test_token_pair_uses_separate_tokens
test_expired_token_is_rejected
test_not_before_claim_is_enforced
test_tampered_payload_is_rejected
test_wrong_issuer_is_rejected
test_wrong_audience_is_rejected
test_malformed_token_is_rejected
test_reserved_claims_cannot_be_overridden

backend/app/stacks/journal_ledger/tests/test_decision_event_contract.py

test_draft_normalizes_and_freezes_contract
test_canonical_hash_is_deterministic
test_payload_key_order_does_not_change_hash
test_naive_datetime_is_rejected
test_invalid_confidence_is_rejected
test_first_persisted_event_requires_no_previous_hash
test_non_first_event_requires_previous_hash
test_content_hash_mismatch_is_rejected
test_chain_link_requires_contiguous_sequence_and_hash

backend/app/stacks/journal_ledger/tests/test_strategy_decision_audit_adapter.py

test_produce_and_audit_delegates_to_service
test_missing_envelope_field_fails_before_append
test_symbol_mismatch_fails_before_append
test_invalid_confidence_fails_before_append
test_naive_occurred_at_is_rejected
test_adapter_exposes_no_mutation_or_execution_methods

backend/app/stacks/market_data/tests/test_runtime_composition.py

test_production_runtime_constructs_without_network
test_runtime_components_are_shared
test_read_only_routes_are_declared
test_status_endpoint_is_network_free
test_quote_endpoint_uses_shared_router
test_historical_endpoint_uses_shared_router
test_invalid_historical_range_fails_closed

backend/app/stacks/market_data/tests/test_stage8_runtime_qualification.py

test_quote_cache_prevents_repeated_provider_call
test_quote_cache_expiry_forces_refresh
test_use_cache_false_always_calls_provider
test_router_falls_back_after_quote_failure
test_router_falls_back_after_historical_failure
test_router_fails_closed_when_every_provider_fails
test_api_translates_provider_failure_to_503
test_api_rejects_invalid_historical_range
test_status_endpoint_does_not_call_provider

backend/app/stacks/portfolio/tests/test_authenticated_owned_readonly_portfolio_api.py

test_configured_owner_receives_two_accounts
test_unbound_user_is_denied
test_empty_principal_subject_is_denied
test_owner_receives_only_bound_account_hashes
test_read_views_are_normalized
test_symbol_lookup_is_owner_scoped
test_no_raw_account_identifier_fields_are_returned
test_service_records_no_network_or_database_activity

backend/app/stacks/portfolio/tests/test_authenticated_paper_order_api.py

test_paper_order_route_policy_is_authenticated
test_paper_order_route_is_registered
test_paper_order_normalizes_symbol
test_paper_order_rejects_invalid_symbol
test_paper_order_rejects_invalid_action
test_paper_order_propagates_authenticated_owner
test_two_orders_keep_owners_separate

backend/app/stacks/portfolio/tests/test_authenticated_portfolio_read_boundary.py

test_portfolio_service_passes_principal_subject
test_portfolio_service_rejects_empty_subject
test_paper_snapshot_rejects_empty_user_id
test_paper_snapshot_is_explicitly_account_scoped

backend/app/stacks/portfolio/tests/test_authenticated_portfolio_read_isolation.py

test_accounting_rejects_empty_owner
test_ledger_read_rejects_empty_owner
test_position_route_is_authenticated_and_scoped
test_orders_route_is_authenticated_and_scoped
test_analytics_route_is_authenticated_and_scoped
test_accounting_is_owner_scoped
test_max_allocation_is_owner_scoped
test_risk_propagates_owner
test_execution_propagates_owner

backend/app/stacks/portfolio/tests/test_authenticated_portfolio_valuation_api.py

test_portfolio_valuation_policy_is_authenticated
test_portfolio_valuation_route_is_registered
test_portfolio_valuation_propagates_owner
test_portfolio_valuation_keeps_owners_separate

backend/app/stacks/portfolio/tests/test_execution_ownership_propagation.py

test_paper_execution_rejects_empty_user_id
test_ledger_rejects_empty_user_id
test_all_paper_broker_save_log_calls_propagate_user_id
test_ledger_inventory_lookup_is_account_scoped
test_order_history_write_is_account_scoped

backend/app/stacks/portfolio/tests/test_multi_owner_reconciliation_startup.py

test_ambiguous_owner_resolution_returns_none
test_single_owner_resolution_returns_owner
test_empty_owner_resolution_returns_none
test_lifespan_guards_legacy_reconciliation_daemon
test_lifespan_does_not_inline_owner_resolution

backend/app/stacks/portfolio/tests/test_ownership_schema_enforcement.py

test_orm_enforces_owned_rows
test_live_database_enforces_owned_rows

backend/app/stacks/portfolio/tests/test_portfolio_snapshot_lifecycle.py

test_refresh_promotes_owner_scoped_snapshot_atomically
test_second_refresh_preserves_last_known_good
test_failed_refresh_keeps_active_snapshot
test_staleness_is_reported
test_retention_is_bounded
test_unbound_user_refresh_is_denied
test_lifecycle_contains_no_raw_owner_id

backend/app/stacks/portfolio/tests/test_readonly_portfolio_facade.py

test_facade_overview
test_lists_account_summaries
test_get_account_by_hash
test_unknown_account_is_rejected
test_lists_all_positions
test_symbol_lookup_is_normalized
test_unknown_symbol_returns_empty_tuple
test_empty_symbol_is_rejected
test_lists_balances
test_totals_are_provider_neutral
test_overview_is_immutable
test_account_summary_is_immutable
test_symbol_result_is_immutable
test_symbol_index_is_not_mutable
test_facade_has_no_mutation_methods
test_facade_source_has_no_provider_import

backend/app/stacks/portfolio/tests/test_reconciliation_ownership_isolation.py

test_reconciliation_rejects_empty_owner
test_daemon_rejects_empty_owner_before_loop
test_reconciliation_inventory_query_is_owner_scoped
test_reconciliation_order_query_is_owner_and_symbol_scoped
test_daemon_propagates_owner_to_each_audit
test_main_propagates_owner_to_both_runtime_callers

backend/app/stacks/snaptrade/tests/test_normalized_portfolio_ingestion.py

test_ingests_qualified_snapshot
test_contract_is_immutable
test_rejects_unsafe_top_level_flags
test_rejects_wrong_schema
test_rejects_wrong_schema_version
test_rejects_raw_account_identifier
test_rejects_position_count_drift
test_does_not_import_snaptrade_sdk

backend/app/stacks/snaptrade/tests/test_portfolio_owner_binding.py

test_empty_registry_fails_closed
test_resolves_only_authenticated_owner
test_rejects_cross_owner_account_reuse
test_filters_snapshot_accounts_to_owner
test_rejects_binding_to_absent_snapshot_account
test_rejects_empty_user_id
test_registry_contains_no_raw_account_ids

backend/app/stacks/wolfden_ai/tests/test_local_model_binding.py

test_request_contract_is_immutable
test_response_contract_is_immutable
test_response_contract_has_failure_status
test_valid_plain_output_is_normalized
test_valid_structured_output_is_parsed
test_invalid_output_fails_closed
test_oversized_output_fails_closed
test_dangerous_text_cannot_unlock_capability
test_approved_adapter_uses_timeout_bridge
test_internal_timeout_maps_to_rejection
test_adapter_exception_maps_to_rejection
test_non_string_adapter_output_maps_to_rejection
test_default_wrapper_preserves_core_behavior
test_model_failure_cannot_block_core
test_rejected_response_cannot_block_core
test_agent_wrapper_has_failure_guard
test_contract_owns_timeout_and_parser
test_contract_owns_no_mutation_capability

backend/app/stacks/wolfden_ai/tests/test_observability_boundary.py

test_observation_is_immutable
test_observation_is_non_persistent
test_observation_rejects_persistent_state
test_observation_rejects_mutation_request
test_payload_is_deeply_frozen
test_standard_logging_is_used
test_agent_router_uses_observability_boundary
test_boundary_owns_no_persistence_or_execution
test_journal_ledger_and_execution_are_preserved

backend/app/stacks/wolfden_ai/tests/test_portfolio_output_result_facade.py

test_result_is_immutable
test_result_is_non_executable
test_result_rejects_executable_state
test_payload_is_deeply_frozen
test_result_has_serializable_mapping_contract
test_agent_router_uses_wolfden_facade_only
test_wolfden_owns_no_execution_or_mutation_capability

backend/app/test/test_graph_event_metrics.py

test_node_metrics_aggregate_latency_and_success
test_security_metrics_count_unauthorized_and_forbidden
test_edge_metrics_are_aggregated
test_snapshot_advertises_metric_contract_version_two

backend/app/test/test_stage8f_graph_materialization.py

test_all_layers_have_declared_nodes
test_required_facades_are_declared_in_l3
test_frontend_workspaces_and_proxies_are_declared
test_snapshot_materializes_declared_topology_without_events
test_real_node_activation_overrides_declared_state
test_real_edge_materializes_both_endpoints
test_declared_edge_becomes_observed_without_losing_relation
test_stage8f_preserves_version_two_contract

backend/app/test/test_stage8f_historical_node_assignment.py

test_historical_nodes_have_explicit_ownership
test_historical_nodes_do_not_materialize_as_unassigned
test_graph_contains_no_unassigned_nodes
test_contract_version_two_is_preserved

backend/app/test/test_trading_pipeline.py

test_trading_pipeline_success
test_trading_pipeline_blocked
test_agent_router_trips_kill_switch

frontend/tests/e2e/04-backend-connectivity.spec.ts

backend documentation endpoint is reachable
backend OpenAPI contract is reachable
protected backend route rejects anonymous request

frontend/tests/e2e/06-dashboard-navigation.spec.ts

/
dashboard, portfolio, and analytics render for a user

frontend/tests/e2e/09-objective4h-b-broad-prompt-matrix.spec.ts

qualifies broad authenticated cognitive behavior

Manual Verification Checklist

[ ] Open the portfolio surface with a valid session

[ ] Open the portfolio surface without a session

[ ] Verify expired-session recovery

[ ] Verify revoked-session rejection

[ ] Record the exact portfolio route

[ ] Record every portfolio heading and visible panel

[ ] Verify portfolio account selection

[ ] Verify account ownership

[ ] Verify balances

[ ] Verify positions

[ ] Verify position symbol

[ ] Verify position quantity

[ ] Verify average entry price

[ ] Verify cost basis

[ ] Verify current market value

[ ] Verify unrealized gain or loss

[ ] Verify realized gain or loss where supported

[ ] Verify total portfolio value

[ ] Verify cash balance

[ ] Verify empty portfolio state

[ ] Verify loading state

[ ] Verify error state

[ ] Verify retry behavior

[ ] Verify stale-data state

[ ] Verify last-updated timestamp

[ ] Verify manual refresh

[ ] Verify refresh loading state

[ ] Verify refresh failure

[ ] Verify provider-unavailable behavior

[ ] Verify database-unavailable behavior

[ ] Verify malformed symbol handling

[ ] Verify user A cannot access user B portfolio

[ ] Verify user A cannot access user B balances

[ ] Verify user A cannot access user B positions

[ ] Verify user-supplied account IDs cannot bypass ownership

[ ] Verify read-only routes do not mutate portfolio state

[ ] Verify refresh mutates only authorized snapshot state

[ ] Verify no live broker order is created

[ ] Verify desktop layout

[ ] Verify tablet layout

[ ] Verify mobile layout

[ ] Verify keyboard navigation

[ ] Verify table headers and screen-reader labels

[ ] Run portfolio unit tests

[ ] Run portfolio API tests

[ ] Run portfolio ownership-isolation tests

[ ] Run portfolio browser tests

[ ] Capture desktop screenshots

[ ] Capture mobile screenshots

Current Gaps

No dedicated portfolio page was detected; portfolio currently appears to be embedded in the authenticated dashboard.

FUNCTION FLOW GRAPH

Authenticated User
      │
      ▼
GET /user/dashboard
      │
      ▼
frontend/proxy.ts
      │
      ▼
Session Validation
      │
      ├────────► Invalid Session
      │                 │
      │                 ▼
      │              /login
      │
      └────────► Valid Session
                        │
                        ▼
frontend/app/user/dashboard/page.tsx
                        │
                        ▼
UserDashboardPage Component
                        │
                        ▼
              Portfolio Service Requests
                        │
            ┌───────────┼───────────┐
            │           │           │
            ▼           ▼           ▼
         Accounts    Balances    Positions
            │           │           │
            └───────────┼───────────┘
                        │
                        ▼
            Authenticated Backend Routes
                        │
                        ▼
            Authentication and Authorization
                        │
                        ▼
                 Ownership Scope
                        │
                        ▼
              Portfolio Facade / Service
                        │
                        ▼
              Repository / Provider Reads
                        │
                        ▼
                 Database Models
                        │
                        ▼
        Accounts + Balances + Positions + Totals
                        │
                        ▼
              Valuation and Gain/Loss
                        │
                        ▼
              Normalized API Response
                        │
          ┌─────────────┼─────────────┐
          │             │             │
          ▼             ▼             ▼
       Loading       Success        Failure
          │             │             │
          └─────────────┼─────────────┘
                        │
                        ▼
              Rendered Portfolio State

Repository Files

Frontend

frontend/app/user/dashboard/page.tsx
UNKNOWN
frontend/app/user/dashboard/page.tsx
frontend/app/user/layout.tsx
frontend/proxy.ts

Frontend Services

frontend/services/portfolioService.ts
frontend/services/chat/chatContracts.ts
frontend/app/components/cards/PositionsPanel.tsx
frontend/app/api/auth/register/route.ts
frontend/app/api/auth/session/route.ts
frontend/app/api/auth/logout/route.ts
frontend/app/api/auth/login/route.ts
frontend/app/api/v1/positions/route.ts
frontend/app/api/v1/portfolio/lifecycle/route.ts
frontend/app/api/v1/portfolio/valuation/route.ts
frontend/app/api/v1/portfolio/positions/route.ts
frontend/app/api/v1/portfolio/refresh/route.ts

Backend Routes

backend/app/main.py
backend/app/stacks/identity_auth/api_router.py
backend/app/stacks/market_data/api_router.py

Services

backend/app/spine/L5_api/owned_readonly_portfolio_service.py
backend/app/stacks/identity_auth/admin_mutation_service.py
backend/app/stacks/identity_auth/login_service.py
backend/app/stacks/identity_auth/password_change_service.py
backend/app/stacks/identity_auth/service_contracts.py
backend/app/stacks/identity_auth/session_lifecycle_service.py
backend/app/stacks/identity_auth/session_service.py
backend/app/stacks/identity_auth/tests/test_login_service.py
backend/app/stacks/identity_auth/tests/test_registration_service.py
backend/app/stacks/portfolio/dashboard_service.py
backend/app/stacks/portfolio/portfolio_service.py

Facades

backend/app/stacks/journal_ledger/decision_audit_query_facade.py
backend/app/stacks/portfolio/facades/readonly_portfolio_facade.py
backend/app/stacks/portfolio/tests/test_readonly_portfolio_facade.py
backend/app/stacks/snaptrade/facade/snaptrade_readonly_facade.py
backend/app/stacks/wolfden_ai/portfolio_output_result_facade.py
backend/app/stacks/wolfden_ai/tests/test_portfolio_output_result_facade.py

Repositories

backend/app/stacks/chat_public/conversation_store.py
backend/app/stacks/chat_public/persistence/chat_models.py
backend/app/stacks/identity_auth/tests/test_identity_persistence_models.py
backend/app/stacks/identity_auth/tests/test_refresh_session_persistence.py
backend/app/stacks/identity_auth/tests/test_stage5b_a_durable_revocation_repository.py
backend/app/stacks/journal_ledger/decision_event_repository.py

Models

backend/app/stacks/chat_public/cognitive_model_router.py
backend/app/stacks/chat_public/persistence/chat_models.py
backend/app/stacks/chat_public/tests/test_cognitive_model_router.py
backend/app/stacks/db_runtime/model_registry.py
backend/app/stacks/identity_auth/__init__.py
backend/app/stacks/identity_auth/access_token_revocation_models.py
backend/app/stacks/identity_auth/admin_mutation_service.py
backend/app/stacks/identity_auth/admin_read_models.py
backend/app/stacks/identity_auth/api_dependencies.py
backend/app/stacks/identity_auth/api_models.py
backend/app/stacks/identity_auth/api_router.py
backend/app/stacks/identity_auth/authorization_policy.py
backend/app/stacks/identity_auth/contracts.py
backend/app/stacks/identity_auth/dev_owner_provisioner.py
backend/app/stacks/identity_auth/login_service.py
backend/app/stacks/identity_auth/mock_runtime.py
backend/app/stacks/identity_auth/models.py
backend/app/stacks/identity_auth/password_change_service.py
backend/app/stacks/identity_auth/refresh_token_hashing.py
backend/app/stacks/identity_auth/repositories.py
backend/app/stacks/identity_auth/route_protection.py
backend/app/stacks/identity_auth/runtime_adapter.py
backend/app/stacks/identity_auth/service_contracts.py
backend/app/stacks/identity_auth/session_lifecycle_service.py
backend/app/stacks/identity_auth/session_service.py
backend/app/stacks/identity_auth/tests/test_api_dependency.py
backend/app/stacks/identity_auth/tests/test_api_route_contract.py
backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py
backend/app/stacks/identity_auth/tests/test_canonical_router_inclusion.py
backend/app/stacks/identity_auth/tests/test_identity_persistence_models.py
backend/app/stacks/identity_auth/tests/test_login_service.py
backend/app/stacks/identity_auth/tests/test_refresh_rotation.py
backend/app/stacks/identity_auth/tests/test_refresh_session_persistence.py
backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py
backend/app/stacks/identity_auth/tests/test_registration_service.py
backend/app/stacks/identity_auth/tests/test_runtime_adapter.py
backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
backend/app/stacks/identity_auth/tests/test_stage4f_canonical_claim_propagation.py
backend/app/stacks/identity_auth/tests/test_stage4f_environment_token_issuer_contract.py
backend/app/stacks/identity_auth/tests/test_stage4f_login_refresh_claims.py
backend/app/stacks/identity_auth/tests/test_stage4f_mock_identity_contract.py
backend/app/stacks/identity_auth/tests/test_stage4f_rotated_refresh_claims.py
backend/app/stacks/identity_auth/tests/test_stage4f_session_lifecycle_runtime_wiring.py
backend/app/stacks/identity_auth/tests/test_stage5b_a_durable_revocation_repository.py
backend/app/stacks/identity_auth/tests/test_stage5b_b_durable_bearer_logout.py
backend/app/stacks/identity_auth/tests/test_stage5b_c_revocation_observability_cleanup.py
backend/app/stacks/identity_auth/tests/test_stage9d_b_forced_password_change.py
backend/app/stacks/identity_auth/tests/test_stage9d_c2_admin_read_models.py
backend/app/stacks/identity_auth/tests/test_token_contract.py
backend/app/stacks/identity_auth/tokens.py
backend/app/stacks/journal_ledger/decision_event_model.py
backend/app/stacks/portfolio/read_models/readonly_portfolio_snapshot.py
backend/app/stacks/snaptrade/contracts/readonly_models.py
backend/app/stacks/wolfden_ai/tests/test_local_model_binding.py

Providers

backend/app/stacks/market_data/provider_contract.py
backend/app/stacks/market_data/provider_registry.py
backend/app/stacks/market_data/yfinance_provider.py
backend/app/stacks/snaptrade/contracts/readonly_provider.py
backend/app/stacks/snaptrade/providers/disabled_provider.py
backend/app/stacks/snaptrade/providers/mock_provider.py

Tests

backend/app/stacks/chat_public/tests/test_aiq004d3_runtime_branch_repairs.py
backend/app/stacks/chat_public/tests/test_capability_state_registry.py
backend/app/stacks/chat_public/tests/test_chat_intent_regex.py
backend/app/stacks/chat_public/tests/test_cognitive_model_router.py
backend/app/stacks/chat_public/tests/test_deterministic_math_engine.py
backend/app/stacks/chat_public/tests/test_developer_context_overlay.py
backend/app/stacks/chat_public/tests/test_developer_response_builder.py
backend/app/stacks/chat_public/tests/test_live_math_runtime_integration.py
backend/app/stacks/chat_public/tests/test_live_rag_activation.py
backend/app/stacks/chat_public/tests/test_live_response_verification.py
backend/app/stacks/chat_public/tests/test_local_rag_index.py
backend/app/stacks/chat_public/tests/test_prompt_composer.py
backend/app/stacks/chat_public/tests/test_public_chat_controls.py
backend/app/stacks/chat_public/tests/test_response_verification.py
backend/app/stacks/chat_public/tests/test_role_overlay_injection.py
backend/app/stacks/identity_auth/tests/test_api_dependency.py
backend/app/stacks/identity_auth/tests/test_api_route_contract.py
backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py
backend/app/stacks/identity_auth/tests/test_canonical_router_inclusion.py
backend/app/stacks/identity_auth/tests/test_identity_persistence_models.py
backend/app/stacks/identity_auth/tests/test_login_service.py
backend/app/stacks/identity_auth/tests/test_refresh_rotation.py
backend/app/stacks/identity_auth/tests/test_refresh_session_persistence.py
backend/app/stacks/identity_auth/tests/test_registration_login_mock_runtime.py
backend/app/stacks/identity_auth/tests/test_registration_service.py
backend/app/stacks/identity_auth/tests/test_runtime_adapter.py
backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
backend/app/stacks/identity_auth/tests/test_stage4f_canonical_claim_propagation.py
backend/app/stacks/identity_auth/tests/test_stage4f_environment_token_issuer_contract.py
backend/app/stacks/identity_auth/tests/test_stage4f_login_refresh_claims.py
backend/app/stacks/identity_auth/tests/test_stage4f_mock_identity_contract.py
backend/app/stacks/identity_auth/tests/test_stage4f_rotated_refresh_claims.py
backend/app/stacks/identity_auth/tests/test_stage4f_session_lifecycle_runtime_wiring.py
backend/app/stacks/identity_auth/tests/test_stage5b_a_durable_revocation_repository.py
backend/app/stacks/identity_auth/tests/test_stage5b_b_durable_bearer_logout.py
backend/app/stacks/identity_auth/tests/test_stage5b_c_revocation_observability_cleanup.py
backend/app/stacks/identity_auth/tests/test_stage9d_b_forced_password_change.py
backend/app/stacks/identity_auth/tests/test_stage9d_c2_admin_read_models.py
backend/app/stacks/identity_auth/tests/test_token_contract.py
backend/app/stacks/journal_ledger/tests/test_decision_event_contract.py
backend/app/stacks/journal_ledger/tests/test_strategy_decision_audit_adapter.py
backend/app/stacks/market_data/tests/test_runtime_composition.py
backend/app/stacks/market_data/tests/test_stage8_runtime_qualification.py
backend/app/stacks/portfolio/tests/test_authenticated_owned_readonly_portfolio_api.py
backend/app/stacks/portfolio/tests/test_authenticated_paper_order_api.py
backend/app/stacks/portfolio/tests/test_authenticated_portfolio_read_boundary.py
backend/app/stacks/portfolio/tests/test_authenticated_portfolio_read_isolation.py
backend/app/stacks/portfolio/tests/test_authenticated_portfolio_valuation_api.py
backend/app/stacks/portfolio/tests/test_execution_ownership_propagation.py
backend/app/stacks/portfolio/tests/test_multi_owner_reconciliation_startup.py
backend/app/stacks/portfolio/tests/test_ownership_schema_enforcement.py
backend/app/stacks/portfolio/tests/test_portfolio_snapshot_lifecycle.py
backend/app/stacks/portfolio/tests/test_readonly_portfolio_facade.py
backend/app/stacks/portfolio/tests/test_reconciliation_ownership_isolation.py
backend/app/stacks/snaptrade/tests/test_normalized_portfolio_ingestion.py
backend/app/stacks/snaptrade/tests/test_portfolio_owner_binding.py
backend/app/stacks/wolfden_ai/tests/test_local_model_binding.py
backend/app/stacks/wolfden_ai/tests/test_observability_boundary.py
backend/app/stacks/wolfden_ai/tests/test_portfolio_output_result_facade.py
backend/app/test/test_graph_event_metrics.py
backend/app/test/test_stage8f_graph_materialization.py
backend/app/test/test_stage8f_historical_node_assignment.py
backend/app/test/test_trading_pipeline.py
frontend/tests/e2e/04-backend-connectivity.spec.ts
frontend/tests/e2e/06-dashboard-navigation.spec.ts
frontend/tests/e2e/09-objective4h-b-broad-prompt-matrix.spec.ts

Evidence

runtime/system_inventory/function_path_05_portfolio_20260730_142919/function_path_05_portfolio_inventory.json
runtime/system_inventory/function_path_05_portfolio_20260730_142919/function_path_05_copy_paste_section.txt
runtime/system_inventory/function_path_05_portfolio_20260730_142919/source

Launch Dependency

Required Before Launch

YES

Blocks

Portfolio visibility

Position visibility

Portfolio valuation

Portfolio refresh

Strategy context

Risk calculations

Analytics

Paper-order ownership

Neuro portfolio explanations

Controlled early-user launch

Depends On

Existing-user login

Authenticated session validation

Frontend middleware

Portfolio API routes

Authorization

Ownership isolation

Portfolio services

Repositories

Database models

Market-data prices

Provider availability

Refresh and snapshot lifecycle

Loading and failure states

FINAL VERDICT

Function Exists: YES

Dedicated Portfolio Page: NOT DETECTED

Dashboard Portfolio Surface: YES

Frontend Connected: DETECTED

Middleware Present: YES

Backend Routes Present: YES

Authentication: DETECTED

Authorization: DETECTED

Ownership Isolation: DETECTED

Read-Only Boundaries: DETECTED

Loading State: DETECTED

Error State: DETECTED

Empty State: DETECTED

Refresh State: DETECTED

Relevant Tests: PRESENT

Cross-User Isolation Test: NOT COMPLETE

Live Verification: NOT COMPLETE

Launch Ready: UNVERIFIED

Overall Classification

PARTIALLY VERIFIED

Launch Classification

CRITICAL

The Portfolio function must be fully verified before launch because
portfolio ownership, valuation, strategy context, analytics, risk,
paper trading, and Neuro explanations depend on accurate and isolated
portfolio state.

---



---

FUNCTION PATH 06 — ANALYTICS

Function Status

Inventory Status: INITIAL INVENTORY COMPLETE
Implementation Status: IMPLEMENTED — SOURCE VERIFICATION PENDING
Qualification Status: UNVERIFIED
Launch Importance: CRITICAL
Last Updated: 2026-07-30
Evidence Source: runtime/system_inventory/function_path_06_analytics_20260730_191127/function_path_06_analytics_inventory.json

Purpose

The Analytics function presents calculated performance, portfolio,
market, strategy, risk, and account metrics for the authenticated user.

Its purpose is to:

- Require an authenticated user session.
- Calculate analytics from authorized user-owned data.
- Present returns, gains, losses, allocation, exposure, and performance.
- Use normalized portfolio and market-data inputs.
- Distinguish verified calculations from estimates or unavailable data.
- Prevent cross-user analytics access.
- Present loading, empty, stale, and failure states.
- Preserve read-only behavior.

User Journey

Authenticated User
      │
      ▼
GET /user/dashboard
      │
      ▼
frontend/proxy.ts
      │
      ▼
frontend/app/user/dashboard/page.tsx
      │
      ▼
Analytics Components
      │
      ▼
Authenticated Analytics Request
      │
      ▼
Authentication and Ownership
      │
      ▼
Portfolio + Market + Strategy Inputs
      │
      ▼
Deterministic Analytics Calculations
      │
      ▼
Normalized Analytics Response
      │
      ▼
Rendered Analytics State

Entry Point

Browser Route

/user/dashboard

Dedicated Analytics Page

UNKNOWN

Dashboard Analytics Surface

frontend/app/user/dashboard/page.tsx

Selected Entry File

frontend/app/user/dashboard/page.tsx

Route Type

AUTHENTICATED

Authentication Required

YES

Frontend Requests

GET OR DYNAMIC `/api/v1/market/live-price/${encodeURIComponent(
      cleanSymbol,
    )}`
Source: frontend/services/marketService.ts:31

GET "/api/v1/portfolio/positions"
Source: frontend/services/portfolioService.ts:46

GET OR DYNAMIC `${BACKEND_BASE_URL}${normalizedPath}`,
    requestInit
  );

  if (response.status !== 401) {
    return response;
  }

  if (!refreshToken) {
    await clearBrowserTokens();
    return unauthorizedResponse();
  }

  const replacement =
    await refreshBrowserSession(refreshToken);

  if (!replacement) {
    return unauthorizedResponse();
  }

  response = await fetch(
    `${BACKEND_BASE_URL}${normalizedPath}`
Source: frontend/lib/backendAuth.ts:135

GET OR DYNAMIC `${API}/analytics`
Source: frontend/app/hooks/useDashboardData.ts:31

GET "/api/admin/users"
Source: frontend/app/admin/users/page.tsx:369

GET `/api/admin/users/${
            encodeURIComponent(
              user.user_id,
            )
          }`
Source: frontend/app/admin/users/page.tsx:475

GET "/api/auth/session"
Source: frontend/app/user/dashboard/page.tsx:232

Backend Routes

GET /api/v1/graph/live
Function: get_live_graph
File: backend/app/main.py:204
Markers: Depends, authenticated, owner

GET /api/v1/dashboard/summary
Function: summary
File: backend/app/main.py:209
Markers: Depends, authenticated

POST /api/v1/sandbox/signal
Function: set_sandbox_override
File: backend/app/main.py:399
Markers: Depends, authenticated, portfolio, user_id

POST /api/v1/sandbox/audit
Function: trigger_sandbox_audit
File: backend/app/main.py:420
Markers: Depends, authenticated, market, portfolio, user_id

POST /api/v1/admin/backup
Function: force_system_backup
File: backend/app/main.py:435
Markers: Depends, authenticated, market, portfolio, position, user_id

GET /api/v1/portfolio/valuation
Function: get_authenticated_portfolio_valuation
File: backend/app/main.py:462
Markers: Depends, authenticated, market, portfolio, position, user_id

GET /api/v1/positions
Function: get_active_positions
File: backend/app/main.py:525
Markers: Depends, authenticated, market, portfolio, position, user_id

GET /api/v1/orders
Function: get_orders
File: backend/app/main.py:563
Markers: Depends, authenticated, position, user_id

GET /api/v1/analytics
Function: get_analytics
File: backend/app/main.py:595
Markers: Depends, authenticated, portfolio, user_id

POST /api/v1/paper/orders
Function: submit_authenticated_paper_order
File: backend/app/main.py:647
Markers: Depends, authenticated, market, owner, portfolio, position, user_id

GET /api/v1/market/live-price/{symbol}
Function: api_live_market_price
File: backend/app/main.py:706
Markers: Depends, authenticated, market, owner, portfolio, position, user_id

GET /api/v1/portfolio/positions
Function: api_portfolio_positions
File: backend/app/main.py:711
Markers: Depends, authenticated, market, owner, portfolio, position, user_id

GET /api/v1/strategy/decision/{symbol}
Function: api_strategy_decision
File: backend/app/main.py:722
Markers: Depends, authenticated, market, owner, portfolio, position, user_id

GET /api/v1/risk/gate/{symbol}
Function: api_risk_gate
File: backend/app/main.py:727
Markers: Depends, authenticated, market, owner, portfolio, position, read_only, user_id

GET /api/v1/portfolio/readonly
Function: authenticated_owned_portfolio_overview
File: backend/app/main.py:796
Markers: Depends, authenticated, portfolio, position, read_only, user_id

GET /api/v1/portfolio/readonly/accounts
Function: authenticated_owned_portfolio_accounts
File: backend/app/main.py:819
Markers: Depends, authenticated, owner, portfolio, position, read_only

GET /api/v1/portfolio/readonly/balances
Function: authenticated_owned_portfolio_balances
File: backend/app/main.py:839
Markers: Depends, authenticated, owner, portfolio, position, read_only

GET /api/v1/portfolio/readonly/positions
Function: authenticated_owned_portfolio_positions
File: backend/app/main.py:859
Markers: Depends, authenticated, owner, portfolio, position, read_only, user_id

GET /api/v1/portfolio/readonly/positions/{symbol}
Function: authenticated_owned_portfolio_symbol_positions
File: backend/app/main.py:879
Markers: Depends, authenticated, owner, portfolio, position, read_only, user_id

GET /api/v1/portfolio/readonly/totals
Function: authenticated_owned_portfolio_totals
File: backend/app/main.py:902
Markers: Depends, authenticated, owner, portfolio, position, read_only, user_id

GET /api/v1/portfolio/readonly/lifecycle
Function: authenticated_portfolio_snapshot_lifecycle
File: backend/app/main.py:933
Markers: Depends, authenticated, owner, portfolio, read_only, user_id

POST /api/v1/portfolio/readonly/refresh
Function: authenticated_portfolio_snapshot_refresh
File: backend/app/main.py:964
Markers: Depends, authenticated, portfolio, user_id

POST /api/v1/chat
Function: chat_endpoint
File: backend/app/stacks/chat_public/chat_api.py:39
Markers: Depends, authenticated

POST /register
Function: register_identity
File: backend/app/stacks/identity_auth/api_router.py:112
Markers: Depends, user_id

POST /login
Function: login_identity
File: backend/app/stacks/identity_auth/api_router.py:157
Markers: Depends, authenticated

POST /change-required-password
Function: change_required_password
File: backend/app/stacks/identity_auth/api_router.py:235
Markers: Depends, authenticated, user_id

POST /refresh
Function: refresh_session
File: backend/app/stacks/identity_auth/api_router.py:282
Markers: Depends, user_id

POST /logout
Function: logout_session
File: backend/app/stacks/identity_auth/api_router.py:351
Markers: Depends, authenticated, user_id

POST /logout-all
Function: logout_all_sessions
File: backend/app/stacks/identity_auth/api_router.py:428
Markers: Depends, authenticated, user_id

GET /introspection
Function: session_introspection
File: backend/app/stacks/identity_auth/api_router.py:487
Markers: Depends, authenticated

GET /introspection
Function: administrative_introspection
File: backend/app/stacks/identity_auth/admin_read_router.py:43
Markers: Depends, authorization, read_only, user_id

GET /users
Function: list_administrative_users
File: backend/app/stacks/identity_auth/admin_read_router.py:66
Markers: Depends, authorization, read_only, user_id

GET /users/{user_id}
Function: get_administrative_user
File: backend/app/stacks/identity_auth/admin_read_router.py:95
Markers: Depends, user_id

GET /sessions
Function: list_administrative_sessions
File: backend/app/stacks/identity_auth/admin_read_router.py:125
Markers: Depends, user_id

GET /sessions/{session_id}
Function: get_administrative_session
File: backend/app/stacks/identity_auth/admin_read_router.py:170
Markers: Depends, user_id

GET /access-token-revocations
Function: list_access_token_revocations
File: backend/app/stacks/identity_auth/admin_read_router.py:200
Markers: Depends, user_id

GET /access-token-revocations/{revocation_id}
Function: get_access_token_revocation
File: backend/app/stacks/identity_auth/admin_read_router.py:240
Markers: Depends, user_id

POST /{user_id}/require-password-reset
Function: require_password_reset
File: backend/app/stacks/identity_auth/admin_mutation_router.py:30
Markers: Depends, user_id

POST /{user_id}/temporary-password
Function: issue_temporary_password
File: backend/app/stacks/identity_auth/admin_mutation_router.py:49
Markers: Depends, user_id

POST /{user_id}/disable
Function: disable_account
File: backend/app/stacks/identity_auth/admin_mutation_router.py:70
Markers: Depends, user_id

POST /{user_id}/enable
Function: enable_account
File: backend/app/stacks/identity_auth/admin_mutation_router.py:89
Markers: Depends, user_id

DELETE /{user_id}
Function: delete_account
File: backend/app/stacks/identity_auth/admin_mutation_router.py:108
Markers: Depends, user_id

GET /status
Function: market_data_status
File: backend/app/stacks/market_data/api_router.py:102
Markers: market, position, read_only

GET /quote/{symbol}
Function: market_data_quote
File: backend/app/stacks/market_data/api_router.py:168
Markers: market

GET /historical/{symbol}
Function: market_data_historical
File: backend/app/stacks/market_data/api_router.py:203
Markers: market

GET /api/v1/analytics
Function: analytics
File: backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py:24
Markers: authenticated, market, user_id

POST /api/v1/admin/backup
Function: admin_backup
File: backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py:32
Markers: authenticated, market, user_id

GET /api/v1/market-data/status
Function: market_status
File: backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py:40
Markers: authenticated, market, user_id

Security

authentication_markers_detected

True

authorization_markers_detected

True

ownership_markers_detected

True

portfolio_scope_detected

True

read_only_markers_detected

True

csrf_markers_detected

True

rate_limit_markers_detected

True

deterministic_calculation_markers_detected

True

Loading Behaviour

loading_state_detected

True

error_state_detected

True

empty_state_detected

True

refresh_state_detected

True

retry_state_detected

False

stale_state_detected

True

last_updated_detected

False

responsive_layout_detected

True

accessibility_markers_detected

True

Failure Paths

Missing Session: UNVERIFIED

Expired Session: UNVERIFIED

Cross-User Analytics Request: LIVE TEST REQUIRED

Empty Portfolio Inputs: UNVERIFIED

Market Data Failure: UNVERIFIED

Calculation Failure: UNVERIFIED

Partial Analytics Result: UNVERIFIED

Tests

backend/app/stacks/chat_public/tests/test_aiq004d2_developer_debug_routing.py

test_fastapi_http_500_routes_to_developer_context
test_python_traceback_routes_to_developer_context
test_market_data_api_request_preserves_market_routing
test_generic_endpoint_question_does_not_force_debug_routing
test_live_trade_request_remains_blocked_before_debug_routing

backend/app/stacks/chat_public/tests/test_aiq004d3_runtime_branch_repairs.py

test_software_debugging_reaches_coder_generation
test_explicit_developer_review_remains_deterministic
test_http_is_not_extracted_as_a_symbol
test_real_uppercase_ticker_can_still_be_extracted
test_nonfinancial_intent_never_creates_strategy_candidate
test_financial_strategy_intent_remains_eligible

backend/app/stacks/chat_public/tests/test_aiq004d_generic_response_contract.py

test_prompt_requires_direct_completion
test_prompt_requires_explicit_count_completion
test_prompt_requires_every_requested_component
test_prompt_requires_generic_factual_honesty
test_prompt_contains_no_aiq_domain_contamination
test_prompt_does_not_modify_execution_policy

backend/app/stacks/chat_public/tests/test_aiq005f_general_conversation_model_binding.py

test_router_constant_uses_qualified_general_model
test_ollama_client_registers_qualified_model
test_greeting_uses_qualified_general_model
test_small_talk_uses_qualified_general_model
test_simple_explanation_uses_qualified_general_model
test_software_debugging_remains_on_coder
test_live_execution_remains_blocked

backend/app/stacks/chat_public/tests/test_authenticated_role_truth_boundary.py

test_system_prompt_rejects_conversational_role_elevation
test_user_overlay_remains_user_despite_developer_claim
test_developer_overlay_requires_server_supplied_developer_role
test_local_evidence_requires_explicit_server_permission
test_authenticated_developer_wording_triggers_developer_intent
test_user_wording_alone_does_not_grant_local_evidence
test_authenticated_developer_permission_uses_local_evidence

backend/app/stacks/chat_public/tests/test_capability_state_registry.py

test_registry_is_read_only_and_complete
test_registry_uses_declared_state_categories
test_drawdown_guard_is_not_called_without_balance
test_registry_summary_is_grounded_in_rows
test_developer_response_contains_capability_state
test_developer_capabilities_remain_grounded
test_unverified_adapter_and_async_states_require_attention

backend/app/stacks/chat_public/tests/test_cognitive_model_profiles.py

test_fast_profile_is_canonical
test_reason_profile_is_canonical
test_code_and_fallback_profiles_remain_separate
test_general_request_routes_to_neuro_fast
test_strategy_request_routes_to_neuro_reason
test_developer_request_still_routes_to_code_model
test_model_profiles_do_not_grant_execution_authority
test_profile_files_are_plain_text_contracts

backend/app/stacks/chat_public/tests/test_cognitive_model_router.py

test_routing_decision_is_immutable
test_general_greeting_uses_fast_model
test_analysis_and_strategy_use_reason_model
test_code_work_uses_code_model
test_math_declares_deterministic_tool_requirement
test_current_or_account_data_declares_retrieval
test_decision_serializes_complete_contract
test_exact_authenticated_math_prompt_requires_deterministic_tool
test_exact_authenticated_research_prompt_requires_retrieval
test_common_math_phrasing_requires_deterministic_tool
test_local_research_phrasing_requires_retrieval
test_position_size_uses_math_without_retrieval
test_conversation_memory_avoids_retrieval
test_explicit_retrieval_requests_remain_enabled
test_strategy_family_retains_retrieval_contract
test_market_and_portfolio_family_do_not_force_retrieval
test_router_never_exposes_execution_authority

backend/app/stacks/chat_public/tests/test_conversation_service_boundary.py

test_service_exports_existing_store_symbols
test_service_has_no_direct_persistence_imports
test_route_owners_do_not_import_store_or_persistence
test_external_production_consumers_do_not_import_store

backend/app/stacks/chat_public/tests/test_deterministic_math_engine.py

test_registry_is_explicit_and_complete
test_exact_decimal_arithmetic
test_percentage_of
test_percent_change
test_simple_return
test_compound_return
test_cagr
test_expected_value
test_risk_reward
test_position_size
test_portfolio_weights
test_descriptive_statistics
test_sharpe_ratio_is_deterministic
test_sortino_ratio_is_deterministic
test_maximum_drawdown
test_trade_statistics
test_invalid_inputs_fail_closed
test_unsupported_operation_fails_closed
test_sequence_boundary_is_enforced
test_non_finite_or_invalid_values_are_rejected
test_serialized_result_contains_no_float_values
test_math_engine_has_no_execution_or_network_authority

backend/app/stacks/chat_public/tests/test_developer_context_overlay.py

test_general_conversation_does_not_load_developer_overlay
test_self_evaluation_adds_grounded_developer_requirements
test_architecture_mode_adds_architecture_review_rules
test_developer_repo_and_architecture_context_are_bounded

backend/app/stacks/chat_public/tests/test_developer_response_builder.py

test_developer_response_is_structured
test_developer_response_does_not_claim_unverified_tests
test_developer_runtime_bypasses_ollama
test_developer_claim_without_permission_uses_ollama
test_general_conversation_still_uses_ollama

backend/app/stacks/chat_public/tests/test_live_math_runtime_integration.py

test_supported_math_requests_are_extracted
test_percentage_result_is_exact
test_cagr_result_is_deterministic
test_position_size_uses_whole_units
test_unrequested_math_does_not_execute
test_ambiguous_math_fails_controlled
test_division_by_zero_returns_error_evidence
test_runtime_contains_math_integration
test_live_math_has_no_arbitrary_execution

backend/app/stacks/chat_public/tests/test_live_rag_activation.py

test_strategy_family_requests_retrieval
test_retrieval_is_not_called_when_not_requested
test_retrieval_filters_injection_chunks_and_bounds_top_k
test_prompt_contains_page_aware_citation
test_prompt_respects_total_character_boundary
test_retrieval_failure_returns_controlled_bundle
test_chat_runtime_contains_live_rag_integration
test_live_rag_module_does_not_enable_execution

backend/app/stacks/chat_public/tests/test_live_response_verification.py

test_verifier_replaces_missing_math_result
test_verifier_preserves_exact_math_result
test_verifier_replaces_live_execution_claim
test_runtime_verification_occurs_before_persistence
test_runtime_emits_verification_event
test_runtime_persists_verification_evidence
test_runtime_exposes_verification_metadata

backend/app/stacks/chat_public/tests/test_local_rag_index.py

test_chunking_is_deterministic
test_chunking_rejects_invalid_overlap
test_stable_identifiers_are_repeatable
test_source_policy_rejects_secrets_and_runtime
test_prompt_injection_is_detected
test_ingestion_deduplicates_identical_content
test_semantic_retrieval_ranks_relevant_chunk_first
test_no_result_behavior_is_controlled
test_index_contract_contains_no_execution_authority

backend/app/stacks/chat_public/tests/test_pdf_rag_ingestion.py

test_research_pdf_is_allowlisted
test_downloads_pdf_is_not_allowlisted
test_pdf_extraction_returns_page_metadata
test_scanned_or_blank_pdf_returns_no_text
test_discovery_contains_all_research_pdfs
test_pdf_chunks_keep_source_and_page_metadata
test_srrn_pdf_has_extractable_text

backend/app/stacks/chat_public/tests/test_prompt_composer.py

test_composer_preserves_existing_section_delimiter
test_composer_uses_supplied_existing_bounder
test_composer_reports_character_metadata
test_composer_materializes_iterables_once
test_composer_rejects_invalid_limit
test_composer_rejects_non_string_bounder_result
test_prompt_composition_is_immutable

backend/app/stacks/chat_public/tests/test_public_chat_controls.py

test_public_chat_contract_accepts_valid_text
test_public_chat_contract_rejects_empty_text
test_public_chat_contract_rejects_oversized_text
test_public_chat_safety_denies_restricted_action
test_public_chat_safety_allows_general_discussion
test_public_chat_timeout_maps_to_504
test_public_chat_dependency_failure_maps_to_503
test_public_chat_rate_limit_maps_to_429
test_public_chat_safety_denial_maps_to_403
test_route_is_decorated_with_public_controls
test_public_control_wrapper_preserves_signature
test_payload_boundary_ignores_injected_dependencies
test_payload_boundary_rejects_oversized_payload
test_payload_boundary_rejects_empty_payload
test_payload_boundary_safety_uses_only_payload
test_payload_boundary_still_rejects_restricted_payload
test_missing_payload_argument_fails_closed
test_configured_payload_wrapper_preserves_signature
test_chat_route_configures_payload_argument

backend/app/stacks/chat_public/tests/test_rag_citation_generation_contract.py

test_missing_approved_citation_is_appended
test_existing_approved_citation_is_preserved
test_numeric_reference_does_not_satisfy_contract
test_empty_citation_set_does_not_modify_response

backend/app/stacks/chat_public/tests/test_response_verification.py

test_ordinary_response_passes
test_exact_math_result_passes
test_decimal_equivalent_math_result_passes
test_missing_math_result_is_repaired
test_position_size_result_passes
test_allowed_citation_passes
test_missing_required_citation_is_repaired
test_unapproved_citation_is_repaired
test_live_execution_claim_fails_closed
test_safe_live_execution_denial_passes
test_empty_response_fails_closed
test_result_serialization_is_structured
test_verifier_has_no_external_authority

backend/app/stacks/chat_public/tests/test_role_overlay_injection.py

test_role_overlay_is_inserted_in_correct_order
test_no_overlay_path_remains_supported
test_chat_api_passes_principal_to_runtime
test_runtime_passes_overlay_and_intent_metadata
test_unknown_role_fails_closed_to_user_overlay
test_deterministic_developer_path_remains_grounded

backend/app/stacks/chat_public/tests/test_role_overlay_principal_dependency.py

test_chat_endpoint_has_authenticated_principal_dependency
test_chat_endpoint_passes_principal_to_runtime
test_chat_endpoint_has_no_undefined_principal_reference

backend/app/stacks/db_runtime/tests/test_transaction_guard.py

test_guard_does_not_rollback_successful_scope
test_guard_rolls_back_write_failure_and_reraises
test_guard_rolls_back_commit_failure_and_reraises
test_guard_rolls_back_cancellation
test_approved_write_path_uses_transaction_guard
test_legacy_market_schema_remains_isolated

backend/app/stacks/db_runtime/tests/test_transaction_manager.py

test_success_executes_flush_then_commit
test_operation_failure_rolls_back_and_reraises
test_flush_failure_rolls_back_and_reraises
test_commit_failure_rolls_back_and_reraises
test_non_callable_operation_is_rejected

backend/app/stacks/identity_auth/tests/test_api_dependency.py

test_missing_bearer_credentials_are_unauthorized
test_wrong_scheme_is_unauthorized
test_valid_access_token_returns_principal
test_refresh_token_is_rejected_by_api_dependency
test_malformed_token_is_unauthorized

backend/app/stacks/identity_auth/tests/test_api_route_contract.py

test_registration_contract
test_registration_failure_is_generic
test_login_contract
test_login_failure_is_generic
test_router_is_activated_in_canonical_app

backend/app/stacks/identity_auth/tests/test_api_runtime_binding.py

test_registration_dependency_is_async_generator
test_login_dependency_is_async_generator
test_registration_dependency_contract_annotation
test_login_dependency_contract_annotation
test_runtime_service_types_are_canonical

backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py

test_route_policy_inventory
test_public_route_requires_no_token
test_authenticated_route_rejects_missing_token
test_authenticated_route_accepts_principal
test_admin_route_rejects_non_admin
test_admin_route_accepts_server_claim
test_unknown_route_preserves_not_found
test_refresh_token_validation_failure_is_unauthorized

backend/app/stacks/identity_auth/tests/test_canonical_router_inclusion.py

test_canonical_source_includes_auth_router_once
test_auth_router_has_complete_session_lifecycle
test_controlled_local_registration_and_login

backend/app/stacks/identity_auth/tests/test_display_name.py

test_registration_with_display_name
test_registration_with_trimmed_display_name
test_registration_with_empty_display_name
test_registration_with_long_display_name
test_registration_without_display_name
test_session_introspection_includes_display_name

backend/app/stacks/identity_auth/tests/test_login_service.py

test_valid_login_issues_separate_tokens_and_session
test_unknown_user_and_wrong_password_share_error
test_disabled_account_fails_closed
test_inactive_status_fails_closed
test_refresh_session_failure_rolls_back
test_identical_tokens_fail_closed

backend/app/stacks/identity_auth/tests/test_protected_principal_dependency.py

test_missing_bearer_credentials_fail_closed
test_valid_principal_is_returned
test_invalid_credentials_are_generic

backend/app/stacks/identity_auth/tests/test_refresh_session_persistence.py

test_rotation_preserves_family_and_revokes_old
test_reuse_revokes_entire_family
test_logout_is_idempotent

backend/app/stacks/identity_auth/tests/test_registration.py

test_successful_registration
test_registration_with_existing_email
test_registration_with_invalid_password

backend/app/stacks/identity_auth/tests/test_registration_service.py

test_registration_normalizes_and_hashes_password
test_duplicate_registration_fails_generically
test_registration_hash_failure_rolls_back
test_empty_password_fails_closed

backend/app/stacks/identity_auth/tests/test_session_introspection.py

test_session_introspection_with_display_name
test_session_introspection_without_display_name

backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py

test_lifecycle_route_policy_inventory
test_refresh_returns_rotated_pair
test_logout_revokes_current_refresh_session
test_refresh_rejection_is_unauthorized
test_logout_rejection_is_unauthorized
test_logout_all_uses_access_principal_subject
test_logout_all_rejects_missing_access_token
test_refresh_request_forbids_extra_fields
test_logout_request_forbids_extra_fields

backend/app/stacks/identity_auth/tests/test_stage4f_canonical_claim_propagation.py

test_login_issues_canonical_role_and_tier_claims
test_login_rejects_invalid_stored_role
test_refresh_uses_current_user_claims
test_refresh_rejects_missing_current_user

backend/app/stacks/identity_auth/tests/test_stage4f_login_refresh_claims.py

test_login_forwards_canonical_claims_to_both_tokens

backend/app/stacks/identity_auth/tests/test_stage4f_rotated_refresh_claims.py

test_rotated_refresh_token_receives_canonical_claims

backend/app/stacks/identity_auth/tests/test_stage4f_session_lifecycle_runtime_wiring.py

test_session_lifecycle_runtime_builds_user_repository
test_session_lifecycle_runtime_uses_one_shared_session

backend/app/stacks/identity_auth/tests/test_stage5b_b_durable_bearer_logout.py

test_logout_persists_access_and_refresh_revocation_before_commit
test_logout_rolls_back_both_revocations_on_failure
test_logout_rejects_access_refresh_subject_mismatch

backend/app/stacks/identity_auth/tests/test_stage5b_c_revocation_observability_cleanup.py

test_revocation_routes_are_get_only
test_revocation_summary_exposes_no_jti
test_cleanup_service_commits_success
test_cleanup_service_rolls_back_failure

backend/app/stacks/identity_auth/tests/test_stage9d_b_forced_password_change.py

test_replacement_password_policy_rejects_weak_values
test_replacement_password_policy_accepts_strong_value
test_required_password_change_updates_hash_and_revokes_sessions
test_wrong_temporary_password_fails_closed

backend/app/stacks/identity_auth/tests/test_stage9d_c2_admin_read_models.py

test_user_models_expose_no_secrets
test_session_models_expose_no_secrets
test_admin_routes_are_get_only
test_admin_dependency_is_database_authoritative
test_read_service_does_not_serialize_secret_fields
test_openapi_contains_only_expected_admin_methods
test_no_password_reset_route_added_in_c2

backend/app/stacks/identity_auth/tests/test_stage9d_c5_k1_session_introspection.py

test_canonical_router_contains_introspection_route
test_introspection_route_policy_is_authenticated
test_introspection_uses_principal_subject
test_missing_identity_fails_closed
test_inactive_identity_fails_closed
test_disabled_identity_fails_closed

backend/app/stacks/identity_auth/tests/test_token_contract.py

test_missing_secret_fails_closed
test_access_token_round_trip
test_refresh_token_is_not_accepted_as_access
test_access_token_is_not_accepted_as_refresh
test_token_pair_uses_separate_tokens
test_expired_token_is_rejected
test_not_before_claim_is_enforced
test_tampered_payload_is_rejected
test_wrong_issuer_is_rejected
test_wrong_audience_is_rejected
test_malformed_token_is_rejected
test_reserved_claims_cannot_be_overridden

backend/app/stacks/journal_ledger/tests/test_decision_audit_query_facade.py

test_get_by_event_id_delegates_only_to_service
test_get_by_idempotency_key_normalizes_key
test_latest_returns_none_without_exposing_service_record
test_list_recent_returns_immutable_tuple_of_serialized_dtos
test_serialized_dto_returns_fresh_dictionary_copy
test_mapping_proxy_record_is_serialized_without_exposure
test_list_recent_fails_closed_for_invalid_limits
test_facade_rejects_non_service_dependency
test_facade_has_exact_public_query_methods
test_dto_is_frozen

backend/app/stacks/journal_ledger/tests/test_decision_audit_query_facade_failure_behavior.py

test_service_failures_propagate_without_fallback_data
test_blank_idempotency_key_fails_before_service_call
test_non_string_idempotency_key_fails_before_service_call
test_invalid_list_limit_fails_before_service_call
test_unsupported_record_type_fails_closed
test_scalar_service_record_fails_closed
test_mapping_with_non_string_key_fails_closed
test_non_finite_float_fails_closed
test_list_recent_rejects_mapping_as_collection
test_list_recent_does_not_return_partial_collection
test_none_reads_remain_explicit_none
test_valid_result_remains_serialized_after_failure_tests

backend/app/stacks/journal_ledger/tests/test_decision_audit_service.py

test_service_exposes_append_and_read_methods_only
test_append_delegates_to_repository
test_read_methods_delegate_to_repository
test_list_recent_rejects_invalid_limits

backend/app/stacks/journal_ledger/tests/test_decision_event_contract.py

test_draft_normalizes_and_freezes_contract
test_canonical_hash_is_deterministic
test_payload_key_order_does_not_change_hash
test_naive_datetime_is_rejected
test_invalid_confidence_is_rejected
test_first_persisted_event_requires_no_previous_hash
test_non_first_event_requires_previous_hash
test_content_hash_mismatch_is_rejected
test_chain_link_requires_contiguous_sequence_and_hash

backend/app/stacks/journal_ledger/tests/test_decision_event_repository.py

test_first_append_allocates_sequence_one
test_second_append_links_previous_hash
test_duplicate_is_rejected_before_insert
test_commit_failure_rolls_back
test_repository_exposes_no_mutation_methods
test_append_rejects_naive_recorded_at

backend/app/stacks/journal_ledger/tests/test_strategy_decision_audit_adapter.py

test_produce_and_audit_delegates_to_service
test_missing_envelope_field_fails_before_append
test_symbol_mismatch_fails_before_append
test_invalid_confidence_fails_before_append
test_naive_occurred_at_is_rejected
test_adapter_exposes_no_mutation_or_execution_methods

backend/app/stacks/market_data/tests/test_provider_contract.py

test_symbol_normalization
test_empty_symbol_rejected
test_quote_normalizes_fields
test_naive_quote_timestamp_rejected
test_invalid_ohlc_rejected
test_request_date_order_enforced
test_result_requires_matching_symbol
test_fixture_satisfies_protocol
test_fixture_returns_canonical_quote
test_fixture_returns_canonical_bars

backend/app/stacks/market_data/tests/test_provider_runtime.py

test_registry_registers_and_selects_by_priority
test_registry_rejects_duplicate_name
test_registry_ignores_disabled_provider
test_cache_returns_unexpired_value
test_cache_expires_value
test_cache_evicts_least_recently_used
test_market_session_classification
test_market_session_rejects_naive_datetime
test_router_uses_highest_priority_provider
test_router_falls_back_after_provider_failure
test_router_fails_closed_when_all_providers_fail
test_router_quote_cache_prevents_second_provider_call
test_router_returns_canonical_historical_result

backend/app/stacks/market_data/tests/test_runtime_composition.py

test_production_runtime_constructs_without_network
test_runtime_components_are_shared
test_read_only_routes_are_declared
test_status_endpoint_is_network_free
test_quote_endpoint_uses_shared_router
test_historical_endpoint_uses_shared_router
test_invalid_historical_range_fails_closed

backend/app/stacks/market_data/tests/test_stage8_runtime_qualification.py

test_quote_cache_prevents_repeated_provider_call
test_quote_cache_expiry_forces_refresh
test_use_cache_false_always_calls_provider
test_router_falls_back_after_quote_failure
test_router_falls_back_after_historical_failure
test_router_fails_closed_when_every_provider_fails
test_api_translates_provider_failure_to_503
test_api_rejects_invalid_historical_range
test_status_endpoint_does_not_call_provider

backend/app/stacks/market_data/tests/test_yfinance_provider.py

test_module_import_does_not_require_yfinance
test_wrapper_satisfies_provider_contract
test_capabilities_are_declared
test_numeric_quote_is_normalized
test_mapping_quote_is_normalized
test_quote_symbol_mismatch_fails
test_quote_loader_failure_is_translated
test_historical_mapping_is_normalized
test_historical_rows_are_sorted
test_historical_limit_is_applied
test_historical_loader_failure_is_translated
test_healthcheck_does_not_load_dependencies

backend/app/stacks/portfolio/tests/test_authenticated_owned_readonly_portfolio_api.py

test_configured_owner_receives_two_accounts
test_unbound_user_is_denied
test_empty_principal_subject_is_denied
test_owner_receives_only_bound_account_hashes
test_read_views_are_normalized
test_symbol_lookup_is_owner_scoped
test_no_raw_account_identifier_fields_are_returned
test_service_records_no_network_or_database_activity

backend/app/stacks/portfolio/tests/test_authenticated_paper_order_api.py

test_paper_order_route_policy_is_authenticated
test_paper_order_route_is_registered
test_paper_order_normalizes_symbol
test_paper_order_rejects_invalid_symbol
test_paper_order_rejects_invalid_action
test_paper_order_propagates_authenticated_owner
test_two_orders_keep_owners_separate

backend/app/stacks/portfolio/tests/test_authenticated_portfolio_read_boundary.py

test_portfolio_service_passes_principal_subject
test_portfolio_service_rejects_empty_subject
test_paper_snapshot_rejects_empty_user_id
test_paper_snapshot_is_explicitly_account_scoped

backend/app/stacks/portfolio/tests/test_authenticated_portfolio_read_isolation.py

test_accounting_rejects_empty_owner
test_ledger_read_rejects_empty_owner
test_position_route_is_authenticated_and_scoped
test_orders_route_is_authenticated_and_scoped
test_analytics_route_is_authenticated_and_scoped
test_accounting_is_owner_scoped
test_max_allocation_is_owner_scoped
test_risk_propagates_owner
test_execution_propagates_owner

backend/app/stacks/portfolio/tests/test_authenticated_portfolio_valuation_api.py

test_portfolio_valuation_policy_is_authenticated
test_portfolio_valuation_route_is_registered
test_portfolio_valuation_propagates_owner
test_portfolio_valuation_keeps_owners_separate

backend/app/stacks/portfolio/tests/test_multi_owner_reconciliation_startup.py

test_ambiguous_owner_resolution_returns_none
test_single_owner_resolution_returns_owner
test_empty_owner_resolution_returns_none
test_lifespan_guards_legacy_reconciliation_daemon
test_lifespan_does_not_inline_owner_resolution

backend/app/stacks/portfolio/tests/test_ownership_schema_enforcement.py

test_orm_enforces_owned_rows
test_live_database_enforces_owned_rows

backend/app/stacks/portfolio/tests/test_portfolio_snapshot_lifecycle.py

test_refresh_promotes_owner_scoped_snapshot_atomically
test_second_refresh_preserves_last_known_good
test_failed_refresh_keeps_active_snapshot
test_staleness_is_reported
test_retention_is_bounded
test_unbound_user_refresh_is_denied
test_lifecycle_contains_no_raw_owner_id

backend/app/stacks/portfolio/tests/test_readonly_portfolio_facade.py

test_facade_overview
test_lists_account_summaries
test_get_account_by_hash
test_unknown_account_is_rejected
test_lists_all_positions
test_symbol_lookup_is_normalized
test_unknown_symbol_returns_empty_tuple
test_empty_symbol_is_rejected
test_lists_balances
test_totals_are_provider_neutral
test_overview_is_immutable
test_account_summary_is_immutable
test_symbol_result_is_immutable
test_symbol_index_is_not_mutable
test_facade_has_no_mutation_methods
test_facade_source_has_no_provider_import

backend/app/stacks/portfolio/tests/test_reconciliation_ownership_isolation.py

test_reconciliation_rejects_empty_owner
test_daemon_rejects_empty_owner_before_loop
test_reconciliation_inventory_query_is_owner_scoped
test_reconciliation_order_query_is_owner_and_symbol_scoped
test_daemon_propagates_owner_to_each_audit
test_main_propagates_owner_to_both_runtime_callers

backend/app/stacks/risk/tests/test_drawdown_guard_ledger_boundary.py

test_risk_owns_no_persistence_import
test_risk_imports_no_ledger_internals
test_risk_calls_only_read_facade
test_healthcheck_preserves_none_contract
test_healthcheck_uses_scalar_facade
test_ledger_owns_read_query
test_read_facade_exposes_no_session_or_model

backend/app/stacks/snaptrade/tests/test_normalized_portfolio_ingestion.py

test_ingests_qualified_snapshot
test_contract_is_immutable
test_rejects_unsafe_top_level_flags
test_rejects_wrong_schema
test_rejects_wrong_schema_version
test_rejects_raw_account_identifier
test_rejects_position_count_drift
test_does_not_import_snaptrade_sdk

backend/app/stacks/snaptrade/tests/test_portfolio_owner_binding.py

test_empty_registry_fails_closed
test_resolves_only_authenticated_owner
test_rejects_cross_owner_account_reuse
test_filters_snapshot_accounts_to_owner
test_rejects_binding_to_absent_snapshot_account
test_rejects_empty_user_id
test_registry_contains_no_raw_account_ids

backend/app/stacks/strategy_candidate_sandbox/L7_tests/test_replay_contracts.py

Matched Terms: return

backend/app/stacks/wolfden_ai/tests/test_local_model_binding.py

test_request_contract_is_immutable
test_response_contract_is_immutable
test_response_contract_has_failure_status
test_valid_plain_output_is_normalized
test_valid_structured_output_is_parsed
test_invalid_output_fails_closed
test_oversized_output_fails_closed
test_dangerous_text_cannot_unlock_capability
test_approved_adapter_uses_timeout_bridge
test_internal_timeout_maps_to_rejection
test_adapter_exception_maps_to_rejection
test_non_string_adapter_output_maps_to_rejection
test_default_wrapper_preserves_core_behavior
test_model_failure_cannot_block_core
test_rejected_response_cannot_block_core
test_agent_wrapper_has_failure_guard
test_contract_owns_timeout_and_parser
test_contract_owns_no_mutation_capability

backend/app/stacks/wolfden_ai/tests/test_observability_boundary.py

test_observation_is_immutable
test_observation_is_non_persistent
test_observation_rejects_persistent_state
test_observation_rejects_mutation_request
test_payload_is_deeply_frozen
test_standard_logging_is_used
test_agent_router_uses_observability_boundary
test_boundary_owns_no_persistence_or_execution
test_journal_ledger_and_execution_are_preserved

backend/app/stacks/wolfden_ai/tests/test_portfolio_output_result_facade.py

test_result_is_immutable
test_result_is_non_executable
test_result_rejects_executable_state
test_payload_is_deeply_frozen
test_result_has_serializable_mapping_contract
test_agent_router_uses_wolfden_facade_only
test_wolfden_owns_no_execution_or_mutation_capability

backend/app/test/test_graph_event_metrics.py

test_node_metrics_aggregate_latency_and_success
test_security_metrics_count_unauthorized_and_forbidden
test_edge_metrics_are_aggregated
test_snapshot_advertises_metric_contract_version_two

backend/app/test/test_stage8f_graph_materialization.py

test_all_layers_have_declared_nodes
test_required_facades_are_declared_in_l3
test_frontend_workspaces_and_proxies_are_declared
test_snapshot_materializes_declared_topology_without_events
test_real_node_activation_overrides_declared_state
test_real_edge_materializes_both_endpoints
test_declared_edge_becomes_observed_without_losing_relation
test_stage8f_preserves_version_two_contract

backend/app/test/test_trading_pipeline.py

test_trading_pipeline_success
test_trading_pipeline_blocked
test_agent_router_trips_kill_switch

frontend/tests/e2e/04-backend-connectivity.spec.ts

backend documentation endpoint is reachable
backend OpenAPI contract is reachable
protected backend route rejects anonymous request

frontend/tests/e2e/05-authenticated-user-flow.spec.ts

register, login, persist session, and logout
/
/

frontend/tests/e2e/06-dashboard-navigation.spec.ts

/
dashboard, portfolio, and analytics render for a user

frontend/tests/e2e/07-neuro-welcome-briefing.spec.ts

authenticated user can view, close, and reopen the briefing
/

frontend/tests/e2e/08-objective4g-d-authenticated-live-turn.spec.ts

/
qualifies authenticated math, RAG, verification, and replay

frontend/tests/e2e/09-objective4h-b-broad-prompt-matrix.spec.ts

qualifies broad authenticated cognitive behavior

Manual Verification Checklist

[ ] Open analytics with a valid user session

[ ] Verify analytics cannot load without authentication

[ ] Record the exact analytics browser route

[ ] Record every analytics card, graph, table, and metric

[ ] Verify total return calculation

[ ] Verify gain and loss calculations

[ ] Verify portfolio allocation

[ ] Verify market exposure

[ ] Verify performance history

[ ] Verify empty-portfolio analytics

[ ] Verify zero-value portfolio analytics

[ ] Verify missing-market-data behavior

[ ] Verify stale-data behavior

[ ] Verify loading state

[ ] Verify error state

[ ] Verify retry behavior

[ ] Verify user A cannot access user B analytics

[ ] Verify calculations are deterministic

[ ] Verify rounding and currency formatting

[ ] Verify percentages cannot divide by zero

[ ] Verify no NaN or Infinity values appear

[ ] Verify no guaranteed-return claims

[ ] Verify desktop layout

[ ] Verify tablet layout

[ ] Verify mobile layout

[ ] Verify graph accessibility

[ ] Run analytics unit tests

[ ] Run analytics API tests

[ ] Run analytics ownership tests

[ ] Run analytics browser tests

[ ] Capture screenshots

Current Gaps

No dedicated analytics page was detected; analytics may be embedded in the authenticated dashboard.

FUNCTION FLOW GRAPH

Authenticated User
      │
      ▼
GET /user/dashboard
      │
      ▼
frontend/proxy.ts
      │
      ▼
frontend/app/user/dashboard/page.tsx
      │
      ▼
Analytics Request
      │
      ▼
Authentication
      │
      ▼
Authorization
      │
      ▼
Ownership Scope
      │
      ▼
Portfolio + Market Data
      │
      ▼
Analytics Service
      │
      ▼
Deterministic Calculations
      │
      ▼
Normalized Analytics Response
      │
      ▼
Analytics Cards / Tables / Graphs

Repository Files

Frontend Entry

frontend/app/user/dashboard/page.tsx

Frontend Services

frontend/proxy.ts
frontend/services/observabilityTimelineService.ts
frontend/services/riskService.ts
frontend/services/graphService.ts
frontend/services/marketService.ts
frontend/services/requestNormalizer.ts
frontend/services/chatService.ts
frontend/services/requestObservability.ts
frontend/services/strategyService.ts
frontend/services/backendHealthService.ts
frontend/services/portfolioService.ts
frontend/app/api/admin/users/route.ts
frontend/app/api/admin/users/_proxy.ts
frontend/app/api/admin/users/[userId]/route.ts
frontend/app/api/admin/users/[userId]/require-password-reset/route.ts
frontend/app/api/admin/users/[userId]/enable/route.ts
frontend/app/api/admin/users/[userId]/disable/route.ts
frontend/app/api/admin/users/[userId]/temporary-password/route.ts
frontend/app/api/auth/register/route.ts
frontend/app/api/auth/session/route.ts
frontend/app/api/auth/change-password/route.ts
frontend/app/api/auth/logout/route.ts
frontend/app/api/auth/login/route.ts
frontend/app/api/v1/chat/route.ts
frontend/app/api/v1/analytics/route.ts
frontend/app/api/v1/positions/route.ts
frontend/app/api/v1/orders/route.ts
frontend/app/api/v1/graph/live/route.ts
frontend/app/api/v1/risk/gate/[symbol]/route.ts
frontend/app/api/v1/paper/orders/route.ts
frontend/app/api/v1/market/live-price/[symbol]/route.ts
frontend/app/api/v1/portfolio/lifecycle/route.ts
frontend/app/api/v1/portfolio/valuation/route.ts
frontend/app/api/v1/portfolio/positions/route.ts
frontend/app/api/v1/portfolio/refresh/route.ts
frontend/app/api/v1/strategy/decision/[symbol]/route.ts

Backend Routes

backend/app/main.py
backend/app/stacks/chat_public/chat_api.py
backend/app/stacks/identity_auth/admin_mutation_router.py
backend/app/stacks/identity_auth/admin_read_router.py
backend/app/stacks/identity_auth/api_router.py
backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py
backend/app/stacks/market_data/api_router.py

Services

backend/app/spine/L5_api/owned_readonly_portfolio_service.py
backend/app/stacks/chat_public/chat_service.py
backend/app/stacks/chat_public/tests/test_conversation_service_boundary.py
backend/app/stacks/identity_auth/access_token_revocation_cleanup_service.py
backend/app/stacks/identity_auth/admin_mutation_service.py
backend/app/stacks/identity_auth/login_service.py
backend/app/stacks/identity_auth/password_change_service.py
backend/app/stacks/identity_auth/registration_service.py
backend/app/stacks/identity_auth/session_lifecycle_service.py
backend/app/stacks/identity_auth/session_service.py
backend/app/stacks/identity_auth/tests/test_login_service.py
backend/app/stacks/identity_auth/tests/test_registration_service.py
backend/app/stacks/journal_ledger/decision_audit_service.py
backend/app/stacks/journal_ledger/tests/test_decision_audit_service.py
backend/app/stacks/learning_research/L3_service_facade/bulk_historical_data_downloader.py
backend/app/stacks/market_data/market_data_service.py
backend/app/stacks/portfolio/dashboard_service.py
backend/app/stacks/portfolio/portfolio_service.py
backend/app/stacks/risk/risk_runtime_service.py
backend/app/stacks/risk/risk_service.py
backend/app/stacks/strategy/strategy_service.py
backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/candidate_quarantine_trash_path.py
backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/dev_command_read_only_executor.py
backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/dev_territory_command_registry.py
backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/eight_hour_training_stream.py
backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/fixture_replay_calculator.py
backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/learning_artifact_pipeline.py
backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/long_training_run_executor.py
backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/near_miss_refactor_queue.py
backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/real_historical_bar_fetch_service.py
backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/replay_plan_service.py
backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/repository_replay_input_wire.py
backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/training_read_only_learner.py

Facades

backend/app/stacks/journal_ledger/decision_audit_query_facade.py
backend/app/stacks/journal_ledger/tests/test_decision_audit_query_facade.py
backend/app/stacks/journal_ledger/tests/test_decision_audit_query_facade_failure_behavior.py
backend/app/stacks/learning_research/L3_service_facade/bulk_historical_data_downloader.py
backend/app/stacks/portfolio/facades/readonly_portfolio_facade.py
backend/app/stacks/portfolio/tests/test_readonly_portfolio_facade.py
backend/app/stacks/snaptrade/facade/provider_factory.py
backend/app/stacks/snaptrade/facade/snaptrade_readonly_facade.py
backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/candidate_quarantine_trash_path.py
backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/dev_command_read_only_executor.py
backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/dev_territory_command_registry.py
backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/eight_hour_training_stream.py
backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/fixture_replay_calculator.py
backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/learning_artifact_pipeline.py
backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/long_training_run_executor.py
backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/near_miss_refactor_queue.py
backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/real_historical_bar_fetch_service.py
backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/replay_plan_service.py
backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/repository_replay_input_wire.py
backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/training_read_only_learner.py
backend/app/stacks/wolfden_ai/portfolio_output_result_facade.py
backend/app/stacks/wolfden_ai/tests/test_portfolio_output_result_facade.py

Repositories

backend/app/stacks/chat_public/conversation_store.py
backend/app/stacks/chat_public/persistence/chat_models.py
backend/app/stacks/identity_auth/access_token_revocation_repository.py
backend/app/stacks/identity_auth/tests/test_refresh_session_persistence.py
backend/app/stacks/journal_ledger/decision_event_repository.py
backend/app/stacks/journal_ledger/tests/test_decision_event_repository.py
backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/repository_replay_input_wire.py

Models

backend/app/stacks/chat_public/cognitive_model_router.py
backend/app/stacks/chat_public/persistence/chat_models.py
backend/app/stacks/chat_public/tests/test_aiq005f_general_conversation_model_binding.py
backend/app/stacks/chat_public/tests/test_cognitive_model_profiles.py
backend/app/stacks/chat_public/tests/test_cognitive_model_router.py
backend/app/stacks/db_model/base.py
backend/app/stacks/db_runtime/model_registry.py
backend/app/stacks/identity_auth/access_token_revocation_cleanup_service.py
backend/app/stacks/identity_auth/access_token_revocation_models.py
backend/app/stacks/identity_auth/access_token_revocation_repository.py
backend/app/stacks/identity_auth/admin_mutation_router.py
backend/app/stacks/identity_auth/admin_mutation_service.py
backend/app/stacks/identity_auth/admin_read_api_models.py
backend/app/stacks/identity_auth/admin_read_dependencies.py
backend/app/stacks/identity_auth/admin_read_models.py
backend/app/stacks/identity_auth/admin_read_router.py
backend/app/stacks/identity_auth/api_dependencies.py
backend/app/stacks/identity_auth/api_router.py
backend/app/stacks/identity_auth/authorization_policy.py
backend/app/stacks/identity_auth/dependencies.py
backend/app/stacks/identity_auth/dev_owner_provisioner.py
backend/app/stacks/identity_auth/login_service.py
backend/app/stacks/identity_auth/migrations/stage9d_c5_j1_subscription_tier.py
backend/app/stacks/identity_auth/mock_runtime.py
backend/app/stacks/identity_auth/models.py
backend/app/stacks/identity_auth/normalization.py
backend/app/stacks/identity_auth/password_change_service.py
backend/app/stacks/identity_auth/passwords.py
backend/app/stacks/identity_auth/refresh_token_hashing.py
backend/app/stacks/identity_auth/registration_service.py
backend/app/stacks/identity_auth/repositories.py
backend/app/stacks/identity_auth/revocation.py
backend/app/stacks/identity_auth/route_protection.py
backend/app/stacks/identity_auth/runtime_adapter.py
backend/app/stacks/identity_auth/secret_boundary.py
backend/app/stacks/identity_auth/session_introspection.py
backend/app/stacks/identity_auth/session_lifecycle_service.py
backend/app/stacks/identity_auth/session_service.py
backend/app/stacks/identity_auth/tests/test_api_dependency.py
backend/app/stacks/identity_auth/tests/test_api_route_contract.py
backend/app/stacks/identity_auth/tests/test_api_runtime_binding.py
backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py
backend/app/stacks/identity_auth/tests/test_canonical_router_inclusion.py
backend/app/stacks/identity_auth/tests/test_display_name.py
backend/app/stacks/identity_auth/tests/test_login_service.py
backend/app/stacks/identity_auth/tests/test_protected_principal_dependency.py
backend/app/stacks/identity_auth/tests/test_refresh_session_persistence.py
backend/app/stacks/identity_auth/tests/test_registration.py
backend/app/stacks/identity_auth/tests/test_registration_service.py
backend/app/stacks/identity_auth/tests/test_session_introspection.py
backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
backend/app/stacks/identity_auth/tests/test_stage4f_canonical_claim_propagation.py
backend/app/stacks/identity_auth/tests/test_stage4f_login_refresh_claims.py
backend/app/stacks/identity_auth/tests/test_stage4f_rotated_refresh_claims.py
backend/app/stacks/identity_auth/tests/test_stage4f_session_lifecycle_runtime_wiring.py
backend/app/stacks/identity_auth/tests/test_stage5b_b_durable_bearer_logout.py
backend/app/stacks/identity_auth/tests/test_stage5b_c_revocation_observability_cleanup.py
backend/app/stacks/identity_auth/tests/test_stage9d_b_forced_password_change.py
backend/app/stacks/identity_auth/tests/test_stage9d_c2_admin_read_models.py
backend/app/stacks/identity_auth/tests/test_stage9d_c5_k1_session_introspection.py
backend/app/stacks/identity_auth/tests/test_token_contract.py
backend/app/stacks/identity_auth/tokens.py
backend/app/stacks/journal_ledger/decision_event_model.py
backend/app/stacks/portfolio/read_models/readonly_portfolio_snapshot.py
backend/app/stacks/wolfden_ai/local_model_contract.py
backend/app/stacks/wolfden_ai/tests/test_local_model_binding.py

Schemas

backend/app/stacks/chat_public/contracts/chat_contracts.py
backend/app/stacks/chat_public/developer_response_builder.py
backend/app/stacks/chat_public/math_tools/contracts.py
backend/app/stacks/chat_public/rag/contracts.py
backend/app/stacks/chat_public/response_verification.py
backend/app/stacks/chat_public/tests/test_aiq004d_generic_response_contract.py
backend/app/stacks/chat_public/tests/test_developer_response_builder.py
backend/app/stacks/chat_public/tests/test_live_response_verification.py
backend/app/stacks/chat_public/tests/test_rag_citation_generation_contract.py
backend/app/stacks/chat_public/tests/test_response_verification.py
backend/app/stacks/identity_auth/tests/test_api_route_contract.py
backend/app/stacks/identity_auth/tests/test_token_contract.py
backend/app/stacks/journal_ledger/decision_event_contract.py
backend/app/stacks/journal_ledger/tests/test_decision_event_contract.py
backend/app/stacks/market_data/dto.py
backend/app/stacks/market_data/provider_contract.py
backend/app/stacks/market_data/tests/test_provider_contract.py
backend/app/stacks/portfolio/tests/test_ownership_schema_enforcement.py
backend/app/stacks/strategy_candidate_sandbox/L2_domain/bar_replay_math_contract.py
backend/app/stacks/strategy_candidate_sandbox/L2_domain/replay_metric_contract.py
backend/app/stacks/strategy_candidate_sandbox/L2_domain/replay_spec_contract.py
backend/app/stacks/strategy_candidate_sandbox/L7_tests/test_replay_contracts.py
backend/app/stacks/strategy_candidate_sandbox/entry_exit_signal_contract.py
backend/app/stacks/strategy_candidate_sandbox/entry_signal_rule_contract.py
backend/app/stacks/strategy_candidate_sandbox/exit_signal_rule_contract.py
backend/app/stacks/strategy_candidate_sandbox/learning_artifact_contract.py
backend/app/stacks/strategy_candidate_sandbox/qwen_context_response_contract.py
backend/app/stacks/strategy_candidate_sandbox/replay_metrics_contract.py
backend/app/stacks/strategy_candidate_sandbox/risk_gate_contract.py
backend/app/stacks/strategy_candidate_sandbox/strategy_rule_enablement_gate_contract.py
backend/app/stacks/strategy_candidate_sandbox/trade_simulation_contract.py
backend/app/stacks/strategy_candidate_sandbox/trade_simulation_enablement_gate_contract.py
backend/app/stacks/strategy_candidate_sandbox/training_observability_contract.py
backend/app/stacks/wolfden_ai/local_model_contract.py

Providers

backend/app/stacks/market_data/provider_cache.py
backend/app/stacks/market_data/provider_contract.py
backend/app/stacks/market_data/provider_registry.py
backend/app/stacks/market_data/provider_router.py
backend/app/stacks/market_data/tests/test_provider_contract.py
backend/app/stacks/market_data/tests/test_provider_runtime.py
backend/app/stacks/market_data/tests/test_yfinance_provider.py
backend/app/stacks/market_data/yfinance_provider.py
backend/app/stacks/snaptrade/config/provider_config.py
backend/app/stacks/snaptrade/facade/provider_factory.py
backend/app/stacks/snaptrade/providers/mock_provider.py

Calculation Files

backend/app/stacks/portfolio/tests/test_authenticated_portfolio_valuation_api.py
backend/app/stacks/strategy_candidate_sandbox/L2_domain/replay_metric_contract.py
backend/app/stacks/strategy_candidate_sandbox/candidate_scorecard_from_replay_metrics.py
backend/app/stacks/strategy_candidate_sandbox/replay_metrics_contract.py
backend/app/stacks/strategy_candidate_sandbox/replay_metrics_generator.py
backend/app/test/test_graph_event_metrics.py

Tests

backend/app/stacks/chat_public/tests/test_aiq004d2_developer_debug_routing.py
backend/app/stacks/chat_public/tests/test_aiq004d3_runtime_branch_repairs.py
backend/app/stacks/chat_public/tests/test_aiq004d_generic_response_contract.py
backend/app/stacks/chat_public/tests/test_aiq005f_general_conversation_model_binding.py
backend/app/stacks/chat_public/tests/test_authenticated_role_truth_boundary.py
backend/app/stacks/chat_public/tests/test_capability_state_registry.py
backend/app/stacks/chat_public/tests/test_cognitive_model_profiles.py
backend/app/stacks/chat_public/tests/test_cognitive_model_router.py
backend/app/stacks/chat_public/tests/test_conversation_service_boundary.py
backend/app/stacks/chat_public/tests/test_deterministic_math_engine.py
backend/app/stacks/chat_public/tests/test_developer_context_overlay.py
backend/app/stacks/chat_public/tests/test_developer_response_builder.py
backend/app/stacks/chat_public/tests/test_live_math_runtime_integration.py
backend/app/stacks/chat_public/tests/test_live_rag_activation.py
backend/app/stacks/chat_public/tests/test_live_response_verification.py
backend/app/stacks/chat_public/tests/test_local_rag_index.py
backend/app/stacks/chat_public/tests/test_pdf_rag_ingestion.py
backend/app/stacks/chat_public/tests/test_prompt_composer.py
backend/app/stacks/chat_public/tests/test_public_chat_controls.py
backend/app/stacks/chat_public/tests/test_rag_citation_generation_contract.py
backend/app/stacks/chat_public/tests/test_response_verification.py
backend/app/stacks/chat_public/tests/test_role_overlay_injection.py
backend/app/stacks/chat_public/tests/test_role_overlay_principal_dependency.py
backend/app/stacks/db_runtime/tests/test_transaction_guard.py
backend/app/stacks/db_runtime/tests/test_transaction_manager.py
backend/app/stacks/identity_auth/tests/test_api_dependency.py
backend/app/stacks/identity_auth/tests/test_api_route_contract.py
backend/app/stacks/identity_auth/tests/test_api_runtime_binding.py
backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py
backend/app/stacks/identity_auth/tests/test_canonical_router_inclusion.py
backend/app/stacks/identity_auth/tests/test_display_name.py
backend/app/stacks/identity_auth/tests/test_login_service.py
backend/app/stacks/identity_auth/tests/test_protected_principal_dependency.py
backend/app/stacks/identity_auth/tests/test_refresh_session_persistence.py
backend/app/stacks/identity_auth/tests/test_registration.py
backend/app/stacks/identity_auth/tests/test_registration_service.py
backend/app/stacks/identity_auth/tests/test_session_introspection.py
backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
backend/app/stacks/identity_auth/tests/test_stage4f_canonical_claim_propagation.py
backend/app/stacks/identity_auth/tests/test_stage4f_login_refresh_claims.py
backend/app/stacks/identity_auth/tests/test_stage4f_rotated_refresh_claims.py
backend/app/stacks/identity_auth/tests/test_stage4f_session_lifecycle_runtime_wiring.py
backend/app/stacks/identity_auth/tests/test_stage5b_b_durable_bearer_logout.py
backend/app/stacks/identity_auth/tests/test_stage5b_c_revocation_observability_cleanup.py
backend/app/stacks/identity_auth/tests/test_stage9d_b_forced_password_change.py
backend/app/stacks/identity_auth/tests/test_stage9d_c2_admin_read_models.py
backend/app/stacks/identity_auth/tests/test_stage9d_c5_k1_session_introspection.py
backend/app/stacks/identity_auth/tests/test_token_contract.py
backend/app/stacks/journal_ledger/tests/test_decision_audit_query_facade.py
backend/app/stacks/journal_ledger/tests/test_decision_audit_query_facade_failure_behavior.py
backend/app/stacks/journal_ledger/tests/test_decision_audit_service.py
backend/app/stacks/journal_ledger/tests/test_decision_event_contract.py
backend/app/stacks/journal_ledger/tests/test_decision_event_repository.py
backend/app/stacks/journal_ledger/tests/test_strategy_decision_audit_adapter.py
backend/app/stacks/market_data/tests/test_provider_contract.py
backend/app/stacks/market_data/tests/test_provider_runtime.py
backend/app/stacks/market_data/tests/test_runtime_composition.py
backend/app/stacks/market_data/tests/test_stage8_runtime_qualification.py
backend/app/stacks/market_data/tests/test_yfinance_provider.py
backend/app/stacks/portfolio/tests/test_authenticated_owned_readonly_portfolio_api.py
backend/app/stacks/portfolio/tests/test_authenticated_paper_order_api.py
backend/app/stacks/portfolio/tests/test_authenticated_portfolio_read_boundary.py
backend/app/stacks/portfolio/tests/test_authenticated_portfolio_read_isolation.py
backend/app/stacks/portfolio/tests/test_authenticated_portfolio_valuation_api.py
backend/app/stacks/portfolio/tests/test_multi_owner_reconciliation_startup.py
backend/app/stacks/portfolio/tests/test_ownership_schema_enforcement.py
backend/app/stacks/portfolio/tests/test_portfolio_snapshot_lifecycle.py
backend/app/stacks/portfolio/tests/test_readonly_portfolio_facade.py
backend/app/stacks/portfolio/tests/test_reconciliation_ownership_isolation.py
backend/app/stacks/risk/tests/test_drawdown_guard_ledger_boundary.py
backend/app/stacks/snaptrade/tests/test_normalized_portfolio_ingestion.py
backend/app/stacks/snaptrade/tests/test_portfolio_owner_binding.py
backend/app/stacks/strategy_candidate_sandbox/L7_tests/test_replay_contracts.py
backend/app/stacks/wolfden_ai/tests/test_local_model_binding.py
backend/app/stacks/wolfden_ai/tests/test_observability_boundary.py
backend/app/stacks/wolfden_ai/tests/test_portfolio_output_result_facade.py
backend/app/test/test_graph_event_metrics.py
backend/app/test/test_stage8f_graph_materialization.py
backend/app/test/test_trading_pipeline.py
frontend/tests/e2e/04-backend-connectivity.spec.ts
frontend/tests/e2e/05-authenticated-user-flow.spec.ts
frontend/tests/e2e/06-dashboard-navigation.spec.ts
frontend/tests/e2e/07-neuro-welcome-briefing.spec.ts
frontend/tests/e2e/08-objective4g-d-authenticated-live-turn.spec.ts
frontend/tests/e2e/09-objective4h-b-broad-prompt-matrix.spec.ts

Evidence

runtime/system_inventory/function_path_06_analytics_20260730_191127/function_path_06_analytics_inventory.json
runtime/system_inventory/function_path_06_analytics_20260730_191127/function_path_06_copy_paste_section.txt
runtime/system_inventory/function_path_06_analytics_20260730_191127/source

Launch Dependency

Required Before Launch

YES

Blocks

Performance reporting

Portfolio interpretation

Strategy evaluation

Risk reporting

User-facing gains and losses

Controlled early-user launch

Depends On

Authenticated session

Portfolio ownership

Portfolio valuation

Market data

Analytics calculations

Error handling

Responsive rendering

FINAL VERDICT

Function Exists: YES

Dedicated Analytics Page: NOT DETECTED

Frontend Connected: DETECTED

Backend Routes Present: YES

Authentication: DETECTED

Ownership Isolation: DETECTED

Deterministic Calculations: DETECTED

Loading State: DETECTED

Error State: DETECTED

Relevant Tests: PRESENT

Live Verification: NOT COMPLETE

Launch Ready: UNVERIFIED

Overall Classification

PARTIALLY VERIFIED

Launch Classification

CRITICAL

---



---

FUNCTION PATH 07 — PAPER TRADING

Function Status

Inventory Status: INITIAL INVENTORY COMPLETE
Implementation Status: IMPLEMENTED — SOURCE VERIFICATION PENDING
Qualification Status: UNVERIFIED
Launch Importance: CRITICAL
Last Updated: 2026-07-30
Evidence Source: runtime/system_inventory/function_path_07_paper_trading_20260731_004101/function_path_07_paper_trading_inventory.json

Purpose

The Paper Trading function allows an authenticated NeuroVest user
to create simulated orders without submitting real broker orders.

Its purpose is to:

- Require an authenticated user session.
- Validate symbol, side, quantity, and order details.
- Enforce user ownership.
- Apply risk and strategy boundaries.
- Enforce paper-only execution.
- Persist auditable simulated orders.
- Update simulated portfolio state where authorized.
- Return clear approval or rejection results.
- Prevent all live broker execution.

Frontend Requests

POST "/api/v1/paper/orders"
Source: frontend/app/user/components/PaperOrderPanel.tsx:130

Backend Routes

GET /api/v1/orders
Function: get_orders
File: backend/app/main.py:563
Markers: Depends, authenticated, paper, risk, user_id

GET /api/v1/analytics
Function: get_analytics
File: backend/app/main.py:595
Markers: Depends, authenticated, live, owner, paper, risk, user_id

POST /api/v1/paper/orders
Function: submit_authenticated_paper_order
File: backend/app/main.py:647
Markers: Depends, authenticated, live, owner, paper, risk, strategy, user_id

Security

authentication_detected

True

authorization_detected

True

ownership_detected

True

paper_only_markers_detected

True

live_execution_disabled_markers_detected

True

risk_markers_detected

True

strategy_markers_detected

True

idempotency_markers_detected

True

commit_markers_detected

False

rollback_markers_detected

False

audit_or_ledger_markers_detected

True

csrf_markers_detected

True

rate_limit_markers_detected

False

Frontend States

loading_detected

True

success_detected

True

error_detected

True

validation_detected

True

responsive_detected

True

accessibility_detected

True

Tests

backend/app/stacks/chat_public/tests/test_local_rag_index.py

test_chunking_is_deterministic
test_chunking_rejects_invalid_overlap
test_stable_identifiers_are_repeatable
test_source_policy_rejects_secrets_and_runtime
test_prompt_injection_is_detected
test_ingestion_deduplicates_identical_content
test_semantic_retrieval_ranks_relevant_chunk_first
test_no_result_behavior_is_controlled
test_index_contract_contains_no_execution_authority

backend/app/stacks/portfolio/tests/test_authenticated_paper_order_api.py

test_paper_order_route_policy_is_authenticated
test_paper_order_route_is_registered
test_paper_order_normalizes_symbol
test_paper_order_rejects_invalid_symbol
test_paper_order_rejects_invalid_action
test_paper_order_propagates_authenticated_owner
test_two_orders_keep_owners_separate

backend/app/stacks/wolfden_ai/tests/test_local_model_binding.py

test_request_contract_is_immutable
test_response_contract_is_immutable
test_response_contract_has_failure_status
test_valid_plain_output_is_normalized
test_valid_structured_output_is_parsed
test_invalid_output_fails_closed
test_oversized_output_fails_closed
test_dangerous_text_cannot_unlock_capability
test_approved_adapter_uses_timeout_bridge
test_internal_timeout_maps_to_rejection
test_adapter_exception_maps_to_rejection
test_non_string_adapter_output_maps_to_rejection
test_default_wrapper_preserves_core_behavior
test_model_failure_cannot_block_core
test_rejected_response_cannot_block_core
test_agent_wrapper_has_failure_guard
test_contract_owns_timeout_and_parser
test_contract_owns_no_mutation_capability

backend/app/stacks/wolfden_ai/tests/test_observability_boundary.py

test_observation_is_immutable
test_observation_is_non_persistent
test_observation_rejects_persistent_state
test_observation_rejects_mutation_request
test_payload_is_deeply_frozen
test_standard_logging_is_used
test_agent_router_uses_observability_boundary
test_boundary_owns_no_persistence_or_execution
test_journal_ledger_and_execution_are_preserved

backend/app/stacks/wolfden_ai/tests/test_portfolio_output_result_facade.py

test_result_is_immutable
test_result_is_non_executable
test_result_rejects_executable_state
test_payload_is_deeply_frozen
test_result_has_serializable_mapping_contract
test_agent_router_uses_wolfden_facade_only
test_wolfden_owns_no_execution_or_mutation_capability

Current Gaps

No automatic source gap detected.

Controlled live paper-trading qualification remains required.

FUNCTION FLOW GRAPH

Authenticated User
      │
      ▼
Paper Order Panel
      │
      ▼
Frontend Validation
      │
      ▼
POST /api/v1/paper/orders
      │
      ▼
Authentication
      │
      ▼
Authorization and Ownership
      │
      ▼
Request Validation
      │
      ▼
Risk and Strategy Checks
      │
      ▼
Paper-Only Execution Boundary
      │
      ├────────► Rejected
      │                 │
      │                 ▼
      │        Controlled Rejection
      │
      └────────► Approved
                        │
                        ▼
              Simulated Order Record
                        │
                        ▼
                Ledger / Audit Evidence
                        │
                        ▼
                Portfolio State Update
                        │
                        ▼
                 Frontend Confirmation

Repository Files

Frontend

frontend/app/admin/user-stats/page.tsx
frontend/app/api/v1/paper/orders/route.ts
frontend/app/user/chat/page.tsx
frontend/app/user/components/PaperOrderPanel.tsx
frontend/app/user/components/RecentOrderActivity.tsx
frontend/app/user/dashboard/userWorkspaceTypes.ts
frontend/app/user/dashboard/page.tsx

Backend Routes

backend/app/main.py

Services

No paper-trading service isolated.

Facades

backend/app/stacks/wolfden_ai/tests/test_portfolio_output_result_facade.py

Repositories

No paper-order repository isolated.

Models

backend/app/stacks/identity_auth/route_protection.py
backend/app/stacks/wolfden_ai/tests/test_local_model_binding.py

Schemas

backend/app/stacks/chat_public/developer_response_builder.py
backend/app/stacks/strategy_candidate_sandbox/training_observability_contract.py

Risk Files

No risk integration file isolated.

Strategy Files

backend/app/stacks/strategy_candidate_sandbox/training_observability_contract.py

Ledger and Audit Files

No ledger or audit file isolated.

Execution Files

backend/app/stacks/execution/paper_broker.py

Tests

backend/app/stacks/chat_public/tests/test_local_rag_index.py
backend/app/stacks/portfolio/tests/test_authenticated_paper_order_api.py
backend/app/stacks/wolfden_ai/tests/test_local_model_binding.py
backend/app/stacks/wolfden_ai/tests/test_observability_boundary.py
backend/app/stacks/wolfden_ai/tests/test_portfolio_output_result_facade.py

Launch Dependency

Required Before Launch

YES

FINAL VERDICT

Function Exists: YES

Frontend Connected: DETECTED

Backend Route Present: YES

Authentication: DETECTED

Ownership: DETECTED

Paper-Only Boundary: DETECTED

Live Execution Disabled: DETECTED

Risk Integration: DETECTED

Audit Evidence: DETECTED

Relevant Tests: PRESENT

Live Verification: NOT COMPLETE

Launch Ready: UNVERIFIED

Overall Classification

PARTIALLY VERIFIED

Launch Classification

CRITICAL

---



---

FUNCTION PATH 08 — STRATEGY ANALYSIS

Function Status

Inventory Status: INITIAL INVENTORY COMPLETE
Implementation Status: IMPLEMENTED — SOURCE VERIFICATION PENDING
Qualification Status: UNVERIFIED
Launch Importance: CRITICAL
Last Updated: 2026-07-31
Evidence Source: runtime/system_inventory/function_path_08_strategy_analysis_20260731_105732/function_path_08_strategy_analysis_inventory.json

Purpose

The Strategy Analysis function evaluates a selected market symbol
using available market, portfolio, strategy, and risk context.

Its purpose is to:

- Require an authenticated user session.
- Validate and normalize the requested symbol.
- Load current and historical market context.
- Load authorized portfolio and position context.
- Evaluate the configured strategy logic.
- Apply risk context and safety boundaries.
- Return BUY, SELL, HOLD, insufficient-data, unavailable, or
  rejected outcomes according to the canonical contract.
- Return confidence, explanation, rationale, or evidence where supported.
- Remain analytical and read-only.
- Never submit an order automatically.
- Never invoke live broker execution.

User Journey

Authenticated User
      │
      ▼
GET /user/dashboard
      │
      ▼
frontend/proxy.ts
      │
      ▼
frontend/app/user/dashboard/page.tsx
      │
      ▼
Select or Enter Symbol
      │
      ▼
Frontend Symbol Validation
      │
      ▼
GET /api/v1/strategy/decision/{symbol}
      │
      ▼
Authentication and Authorization
      │
      ▼
Symbol Normalization
      │
      ▼
Market + Portfolio Context
      │
      ▼
Strategy Evaluation
      │
      ▼
Risk Context
      │
      ▼
Decision + Confidence + Evidence
      │
      ├────────► BUY
      ├────────► SELL
      ├────────► HOLD
      ├────────► INSUFFICIENT DATA
      └────────► UNAVAILABLE / REJECTED

Entry Point

Browser Route

/user/dashboard

Dedicated Strategy Page

UNKNOWN

Dashboard Strategy Surface

frontend/app/user/dashboard/page.tsx

Selected Entry File

frontend/app/user/dashboard/page.tsx

Middleware

frontend/proxy.ts

Frontend Requests

GET OR DYNAMIC `/api/v1/strategy/decision/${cleanSymbol}`
Source: frontend/services/strategyService.ts:25
Credentials: UNKNOWN

Backend Routes

GET /api/v1/graph/live
Function: get_live_graph
File: backend/app/main.py:204
Markers: Depends, authenticated, live, owner, strategy, symbol, user_id

GET /api/v1/dashboard/summary
Function: summary
File: backend/app/main.py:209
Markers: Depends, authenticated, live, owner, portfolio, strategy, symbol

POST /api/v1/paper/orders
Function: submit_authenticated_paper_order
File: backend/app/main.py:647
Markers: Depends, authenticated, live, market, owner, paper, portfolio, position, risk, strategy, symbol, user_id

GET /api/v1/market/live-price/{symbol}
Function: api_live_market_price
File: backend/app/main.py:706
Markers: Depends, authenticated, live, market, owner, paper, portfolio, position, risk, strategy, symbol, user_id

GET /api/v1/portfolio/positions
Function: api_portfolio_positions
File: backend/app/main.py:711
Markers: Depends, authenticated, live, market, owner, paper, portfolio, position, risk, strategy, symbol, user_id

GET /api/v1/strategy/decision/{symbol}
Function: api_strategy_decision
File: backend/app/main.py:722
Markers: Depends, authenticated, live, market, owner, paper, portfolio, position, risk, strategy, symbol, user_id

GET /api/v1/risk/gate/{symbol}
Function: api_risk_gate
File: backend/app/main.py:727
Markers: Depends, authenticated, live, market, owner, paper, portfolio, position, risk, strategy, symbol, user_id

GET /api/v1/analytics
Function: analytics
File: backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py:24
Markers: authenticated, authorization, market, strategy, user_id

POST /api/v1/admin/backup
Function: admin_backup
File: backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py:32
Markers: authenticated, authorization, market, strategy, user_id

GET /api/v1/market-data/status
Function: market_status
File: backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py:40
Markers: authenticated, authorization, market, strategy, user_id

Security and Behaviour

authentication_detected

True

authorization_detected

True

ownership_detected

True

symbol_validation_detected

True

market_dependency_detected

True

portfolio_dependency_detected

True

risk_dependency_detected

True

evidence_markers_detected

True

deterministic_markers_detected

True

ai_or_model_markers_detected

True

read_only_markers_detected

True

paper_only_markers_detected

True

live_execution_disabled_detected

True

automatic_order_submission_detected

False

csrf_detected

False

rate_limit_detected

False

Frontend States

loading_detected

True

error_detected

True

empty_detected

True

stale_detected

False

refresh_detected

True

retry_detected

False

confidence_detected

True

reason_detected

False

responsive_detected

True

accessibility_detected

True

Tests

backend/app/stacks/chat_public/tests/test_aiq004d3_runtime_branch_repairs.py

test_software_debugging_reaches_coder_generation
test_explicit_developer_review_remains_deterministic
test_http_is_not_extracted_as_a_symbol
test_real_uppercase_ticker_can_still_be_extracted
test_nonfinancial_intent_never_creates_strategy_candidate
test_financial_strategy_intent_remains_eligible

backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py

test_route_policy_inventory
test_public_route_requires_no_token
test_authenticated_route_rejects_missing_token
test_authenticated_route_accepts_principal
test_admin_route_rejects_non_admin
test_admin_route_accepts_server_claim
test_unknown_route_preserves_not_found
test_refresh_token_validation_failure_is_unauthorized

backend/app/stacks/journal_ledger/tests/test_decision_audit_query_facade.py

test_get_by_event_id_delegates_only_to_service
test_get_by_idempotency_key_normalizes_key
test_latest_returns_none_without_exposing_service_record
test_list_recent_returns_immutable_tuple_of_serialized_dtos
test_serialized_dto_returns_fresh_dictionary_copy
test_mapping_proxy_record_is_serialized_without_exposure
test_list_recent_fails_closed_for_invalid_limits
test_facade_rejects_non_service_dependency
test_facade_has_exact_public_query_methods
test_dto_is_frozen

backend/app/stacks/journal_ledger/tests/test_decision_audit_query_facade_failure_behavior.py

test_service_failures_propagate_without_fallback_data
test_blank_idempotency_key_fails_before_service_call
test_non_string_idempotency_key_fails_before_service_call
test_invalid_list_limit_fails_before_service_call
test_unsupported_record_type_fails_closed
test_scalar_service_record_fails_closed
test_mapping_with_non_string_key_fails_closed
test_non_finite_float_fails_closed
test_list_recent_rejects_mapping_as_collection
test_list_recent_does_not_return_partial_collection
test_none_reads_remain_explicit_none
test_valid_result_remains_serialized_after_failure_tests

backend/app/stacks/journal_ledger/tests/test_decision_event_contract.py

test_draft_normalizes_and_freezes_contract
test_canonical_hash_is_deterministic
test_payload_key_order_does_not_change_hash
test_naive_datetime_is_rejected
test_invalid_confidence_is_rejected
test_first_persisted_event_requires_no_previous_hash
test_non_first_event_requires_previous_hash
test_content_hash_mismatch_is_rejected
test_chain_link_requires_contiguous_sequence_and_hash

backend/app/stacks/journal_ledger/tests/test_decision_event_model.py

test_model_uses_canonical_runtime_base
test_table_name_is_canonical
test_required_constraints_and_columns_exist
test_sequence_number_is_primary_key
test_update_listener_rejects_mutation
test_delete_listener_rejects_mutation

backend/app/stacks/journal_ledger/tests/test_decision_event_repository.py

test_first_append_allocates_sequence_one
test_second_append_links_previous_hash
test_duplicate_is_rejected_before_insert
test_commit_failure_rolls_back
test_repository_exposes_no_mutation_methods
test_append_rejects_naive_recorded_at

backend/app/stacks/journal_ledger/tests/test_strategy_decision_audit_adapter.py

test_produce_and_audit_delegates_to_service
test_missing_envelope_field_fails_before_append
test_symbol_mismatch_fails_before_append
test_invalid_confidence_fails_before_append
test_naive_occurred_at_is_rejected
test_adapter_exposes_no_mutation_or_execution_methods

backend/app/test/test_trading_pipeline.py

test_trading_pipeline_success
test_trading_pipeline_blocked
test_agent_router_trips_kill_switch

Current Gaps

No dedicated strategy-analysis page was detected; the strategy surface appears to be embedded in the authenticated dashboard.

FUNCTION FLOW GRAPH

Authenticated User
      │
      ▼
GET /user/dashboard
      │
      ▼
frontend/proxy.ts
      │
      ▼
frontend/app/user/dashboard/page.tsx
      │
      ▼
Symbol Selection
      │
      ▼
GET /api/v1/strategy/decision/{symbol}
      │
      ▼
Authentication
      │
      ▼
Authorization
      │
      ▼
Symbol Validation
      │
      ▼
Market Data
      │
      ▼
Portfolio Context
      │
      ▼
Strategy Engine
      │
      ▼
Risk Context
      │
      ▼
Decision Validation
      │
      ▼
Confidence + Reason + Evidence
      │
      ├────────► BUY
      ├────────► SELL
      ├────────► HOLD
      ├────────► INSUFFICIENT DATA
      └────────► UNAVAILABLE / REJECTED

Repository Files

Frontend

frontend/app/page.tsx
frontend/services/strategyService.ts
frontend/services/chat/chatContracts.ts
frontend/app/components/layout/DashboardShell.tsx
frontend/app/components/cards/StrategyDecisionCard.tsx
frontend/app/components/workspaces/OverviewWorkspace.tsx
frontend/app/components/workspaces/LearningWorkspacePanel.tsx
frontend/app/api/v1/strategy/decision/[symbol]/route.ts
frontend/app/user/dashboard/userWorkspaceTypes.ts
frontend/app/user/dashboard/page.tsx
frontend/app/user/dashboard/UserStrategiesWorkspace.tsx

Frontend Services

frontend/services/strategyService.ts
frontend/services/chat/chatContracts.ts
frontend/app/components/cards/StrategyDecisionCard.tsx
frontend/app/api/v1/strategy/decision/[symbol]/route.ts

Backend Routes

backend/app/main.py
backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py

Strategy Files

backend/app/stacks/chat_public/strategy_proposal_capture.py
backend/app/stacks/journal_ledger/strategy_decision_audit_adapter.py
backend/app/stacks/journal_ledger/tests/test_strategy_decision_audit_adapter.py
backend/app/stacks/strategy/engine.py
backend/app/stacks/strategy/llm_strategy_engine.py
backend/app/stacks/strategy/signal.py
backend/app/stacks/strategy/strategy_service.py
backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/dev_territory_command_registry.py
backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/fixture_replay_calculator.py
backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/learning_artifact_pipeline.py
backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/real_historical_bar_fetch_service.py
backend/app/stacks/strategy_candidate_sandbox/L4_runtime_orchestration/replay_execution_engine.py
backend/app/stacks/strategy_candidate_sandbox/entry_exit_decision_engine_stub.py
backend/app/stacks/strategy_candidate_sandbox/entry_exit_signal_contract.py
backend/app/stacks/strategy_candidate_sandbox/entry_signal_generator_disabled_stub.py
backend/app/stacks/strategy_candidate_sandbox/entry_signal_rule_contract.py
backend/app/stacks/strategy_candidate_sandbox/entry_signal_rule_validator.py
backend/app/stacks/strategy_candidate_sandbox/exit_signal_generator_disabled_stub.py
backend/app/stacks/strategy_candidate_sandbox/exit_signal_rule_contract.py
backend/app/stacks/strategy_candidate_sandbox/exit_signal_rule_validator.py
backend/app/stacks/strategy_candidate_sandbox/hold_decision_to_hold_event_bridge.py
backend/app/stacks/strategy_candidate_sandbox/hold_signal_generator_stub.py
backend/app/stacks/strategy_candidate_sandbox/indicator_knowledge_graph.py
backend/app/stacks/strategy_candidate_sandbox/learning_artifact_contract.py
backend/app/stacks/strategy_candidate_sandbox/learning_reward_scorer.py
backend/app/stacks/strategy_candidate_sandbox/qwen_read_only_architecture_summary_gate.py
backend/app/stacks/strategy_candidate_sandbox/risk_gate_contract.py
backend/app/stacks/strategy_candidate_sandbox/risk_gate_validator.py
backend/app/stacks/strategy_candidate_sandbox/strategy_knowledge_object.py
backend/app/stacks/strategy_candidate_sandbox/strategy_rule_enablement_gate_contract.py
backend/app/stacks/strategy_candidate_sandbox/strategy_rule_enablement_gate_validator.py
backend/app/stacks/strategy_candidate_sandbox/symbol_intelligence_profile.py
backend/app/stacks/strategy_candidate_sandbox/symbol_universe.py
backend/app/stacks/strategy_candidate_sandbox/trade_event_validator.py
backend/app/stacks/strategy_candidate_sandbox/trade_simulation_dry_run_stub.py
backend/app/stacks/strategy_candidate_sandbox/trade_simulation_enablement_gate_contract.py
backend/app/stacks/strategy_candidate_sandbox/trade_simulation_enablement_gate_validator.py
backend/app/stacks/strategy_candidate_sandbox/training_observability_contract.py

Risk Files

backend/app/stacks/strategy_candidate_sandbox/risk_gate_contract.py
backend/app/stacks/strategy_candidate_sandbox/risk_gate_validator.py

Market Files

No market dependency file isolated.

Portfolio Files

No portfolio dependency file isolated.

Services

backend/app/stacks/strategy/strategy_service.py
backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/dev_territory_command_registry.py
backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/fixture_replay_calculator.py
backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/learning_artifact_pipeline.py
backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/real_historical_bar_fetch_service.py

Facades

backend/app/stacks/journal_ledger/tests/test_decision_audit_query_facade.py
backend/app/stacks/journal_ledger/tests/test_decision_audit_query_facade_failure_behavior.py
backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/dev_territory_command_registry.py
backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/fixture_replay_calculator.py
backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/learning_artifact_pipeline.py
backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/real_historical_bar_fetch_service.py

Repositories

backend/app/stacks/chat_public/conversation_store.py
backend/app/stacks/chat_public/persistence/chat_models.py
backend/app/stacks/journal_ledger/decision_event_repository.py
backend/app/stacks/journal_ledger/tests/test_decision_event_repository.py

Models

backend/app/stacks/chat_public/persistence/chat_models.py
backend/app/stacks/identity_auth/route_protection.py
backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py
backend/app/stacks/journal_ledger/decision_event_model.py
backend/app/stacks/journal_ledger/tests/test_decision_event_model.py

Schemas

backend/app/stacks/chat_public/contracts/chat_contracts.py
backend/app/stacks/journal_ledger/decision_event_contract.py
backend/app/stacks/journal_ledger/tests/test_decision_event_contract.py
backend/app/stacks/strategy_candidate_sandbox/entry_exit_signal_contract.py
backend/app/stacks/strategy_candidate_sandbox/entry_signal_rule_contract.py
backend/app/stacks/strategy_candidate_sandbox/exit_signal_rule_contract.py
backend/app/stacks/strategy_candidate_sandbox/learning_artifact_contract.py
backend/app/stacks/strategy_candidate_sandbox/risk_gate_contract.py
backend/app/stacks/strategy_candidate_sandbox/strategy_rule_enablement_gate_contract.py
backend/app/stacks/strategy_candidate_sandbox/trade_simulation_enablement_gate_contract.py
backend/app/stacks/strategy_candidate_sandbox/training_observability_contract.py

Providers

No strategy provider file isolated.

Evidence Files

backend/app/stacks/journal_ledger/decision_event_contract.py
backend/app/stacks/journal_ledger/decision_event_model.py
backend/app/stacks/journal_ledger/decision_event_repository.py
backend/app/stacks/journal_ledger/strategy_decision_audit_adapter.py
backend/app/stacks/journal_ledger/tests/test_decision_audit_query_facade.py
backend/app/stacks/journal_ledger/tests/test_decision_audit_query_facade_failure_behavior.py
backend/app/stacks/journal_ledger/tests/test_decision_event_contract.py
backend/app/stacks/journal_ledger/tests/test_decision_event_model.py
backend/app/stacks/journal_ledger/tests/test_decision_event_repository.py
backend/app/stacks/journal_ledger/tests/test_strategy_decision_audit_adapter.py

Calculation Files

backend/app/stacks/strategy/signal.py
backend/app/stacks/strategy_candidate_sandbox/entry_exit_signal_contract.py
backend/app/stacks/strategy_candidate_sandbox/entry_signal_generator_disabled_stub.py
backend/app/stacks/strategy_candidate_sandbox/entry_signal_rule_contract.py
backend/app/stacks/strategy_candidate_sandbox/entry_signal_rule_validator.py
backend/app/stacks/strategy_candidate_sandbox/exit_signal_generator_disabled_stub.py
backend/app/stacks/strategy_candidate_sandbox/exit_signal_rule_contract.py
backend/app/stacks/strategy_candidate_sandbox/exit_signal_rule_validator.py
backend/app/stacks/strategy_candidate_sandbox/hold_signal_generator_stub.py
backend/app/stacks/strategy_candidate_sandbox/indicator_knowledge_graph.py

AI or Model Files

backend/app/core/cognitive_types.py
backend/app/core/runtime_trace.py
backend/app/main.py
backend/app/stacks/chat_public/chat_intent_regex.py
backend/app/stacks/chat_public/chat_runtime.py
backend/app/stacks/chat_public/context/context_assembler.py
backend/app/stacks/chat_public/contracts/chat_contracts.py
backend/app/stacks/chat_public/conversation_store.py
backend/app/stacks/chat_public/persistence/chat_models.py
backend/app/stacks/chat_public/strategy_proposal_capture.py
backend/app/stacks/chat_public/tests/test_aiq004d3_runtime_branch_repairs.py
backend/app/stacks/identity_auth/route_protection.py
backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py
backend/app/stacks/journal_ledger/decision_event_contract.py
backend/app/stacks/journal_ledger/decision_event_model.py
backend/app/stacks/journal_ledger/decision_event_repository.py
backend/app/stacks/journal_ledger/strategy_decision_audit_adapter.py
backend/app/stacks/journal_ledger/tests/test_decision_audit_query_facade.py
backend/app/stacks/journal_ledger/tests/test_decision_audit_query_facade_failure_behavior.py
backend/app/stacks/journal_ledger/tests/test_decision_event_contract.py
backend/app/stacks/journal_ledger/tests/test_decision_event_model.py
backend/app/stacks/journal_ledger/tests/test_decision_event_repository.py
backend/app/stacks/journal_ledger/tests/test_strategy_decision_audit_adapter.py
backend/app/stacks/strategy/engine.py
backend/app/stacks/strategy/llm_strategy_engine.py
backend/app/stacks/strategy/signal.py
backend/app/stacks/strategy/strategy_service.py
backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/dev_territory_command_registry.py
backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/fixture_replay_calculator.py
backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/learning_artifact_pipeline.py
backend/app/stacks/strategy_candidate_sandbox/L3_service_facade/real_historical_bar_fetch_service.py
backend/app/stacks/strategy_candidate_sandbox/L4_runtime_orchestration/replay_execution_engine.py
backend/app/stacks/strategy_candidate_sandbox/entry_exit_decision_engine_stub.py
backend/app/stacks/strategy_candidate_sandbox/entry_exit_signal_contract.py
backend/app/stacks/strategy_candidate_sandbox/entry_signal_generator_disabled_stub.py
backend/app/stacks/strategy_candidate_sandbox/entry_signal_rule_contract.py
backend/app/stacks/strategy_candidate_sandbox/entry_signal_rule_validator.py
backend/app/stacks/strategy_candidate_sandbox/exit_signal_generator_disabled_stub.py
backend/app/stacks/strategy_candidate_sandbox/exit_signal_rule_contract.py
backend/app/stacks/strategy_candidate_sandbox/exit_signal_rule_validator.py
backend/app/stacks/strategy_candidate_sandbox/hold_decision_to_hold_event_bridge.py
backend/app/stacks/strategy_candidate_sandbox/hold_signal_generator_stub.py
backend/app/stacks/strategy_candidate_sandbox/indicator_knowledge_graph.py
backend/app/stacks/strategy_candidate_sandbox/learning_artifact_contract.py
backend/app/stacks/strategy_candidate_sandbox/learning_reward_scorer.py
backend/app/stacks/strategy_candidate_sandbox/qwen_read_only_architecture_summary_gate.py
backend/app/stacks/strategy_candidate_sandbox/risk_gate_contract.py
backend/app/stacks/strategy_candidate_sandbox/risk_gate_validator.py
backend/app/stacks/strategy_candidate_sandbox/strategy_knowledge_object.py
backend/app/stacks/strategy_candidate_sandbox/strategy_rule_enablement_gate_contract.py
backend/app/stacks/strategy_candidate_sandbox/strategy_rule_enablement_gate_validator.py
backend/app/stacks/strategy_candidate_sandbox/symbol_intelligence_profile.py
backend/app/stacks/strategy_candidate_sandbox/symbol_universe.py
backend/app/stacks/strategy_candidate_sandbox/trade_event_validator.py
backend/app/stacks/strategy_candidate_sandbox/trade_simulation_dry_run_stub.py
backend/app/stacks/strategy_candidate_sandbox/trade_simulation_enablement_gate_contract.py
backend/app/stacks/strategy_candidate_sandbox/trade_simulation_enablement_gate_validator.py
backend/app/stacks/strategy_candidate_sandbox/training_observability_contract.py
backend/app/stacks/wolfden_ai/agent_router.py
backend/app/test/test_trading_pipeline.py

Execution Files

backend/app/stacks/strategy_candidate_sandbox/L4_runtime_orchestration/replay_execution_engine.py

Tests

backend/app/stacks/chat_public/tests/test_aiq004d3_runtime_branch_repairs.py
backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py
backend/app/stacks/journal_ledger/tests/test_decision_audit_query_facade.py
backend/app/stacks/journal_ledger/tests/test_decision_audit_query_facade_failure_behavior.py
backend/app/stacks/journal_ledger/tests/test_decision_event_contract.py
backend/app/stacks/journal_ledger/tests/test_decision_event_model.py
backend/app/stacks/journal_ledger/tests/test_decision_event_repository.py
backend/app/stacks/journal_ledger/tests/test_strategy_decision_audit_adapter.py
backend/app/test/test_trading_pipeline.py

Launch Dependency

Required Before Launch

YES

Blocks

Strategy decision display

Paper-order decision support

Risk-controlled simulation

Portfolio interpretation

Neuro strategy explanations

Controlled early-user launch

Depends On

Authenticated session

Frontend strategy service

Strategy backend route

Symbol validation

Market-data availability

Portfolio context

Strategy logic

Risk context

Evidence and explanation

Read-only boundaries

Failure handling

FINAL VERDICT

Function Exists: YES

Dedicated Strategy Page: NOT DETECTED

Frontend Connected: DETECTED

Backend Route Present: YES

Authentication: DETECTED

Symbol Validation: DETECTED

Market Dependency: DETECTED

Portfolio Dependency: DETECTED

Risk Integration: DETECTED

Evidence or Explanation: DETECTED

Read-Only Boundary: DETECTED

Paper-Only Boundary: DETECTED

Live Execution Disabled: DETECTED

Automatic Order Submission Markers: NOT DETECTED

Relevant Tests: PRESENT

Live Verification: NOT COMPLETE

Launch Ready: UNVERIFIED

Overall Classification

PARTIALLY VERIFIED

Launch Classification

CRITICAL

---



---

FUNCTION PATH 09 — RISK ANALYSIS AND RISK GATE

Function Status

Inventory Status: INITIAL INVENTORY COMPLETE
Implementation Status: IMPLEMENTED — SOURCE VERIFICATION PENDING
Qualification Status: UNVERIFIED
Launch Importance: CRITICAL
Last Updated: 2026-07-31
Evidence Source: runtime/system_inventory/function_path_09_risk_gate_20260731_115048/function_path_09_risk_gate_inventory.json

Purpose

The Risk Analysis and Risk Gate function evaluates whether a selected
symbol, strategy decision, or proposed paper order is allowed under
the authenticated user's portfolio state and NeuroVest safety rules.

Its purpose is to:

- Require an authenticated user session.
- Validate and normalize the requested symbol.
- Load user-owned portfolio, positions, balances, and cash context.
- Load market-price, volatility, and data-freshness context.
- Evaluate exposure, concentration, and position-size limits.
- Evaluate buying power, cash, order value, and loss limits.
- Apply strategy context.
- Enforce SAFE, SIMULATION, LOCKED, and EMERGENCY_STOP modes.
- Fail closed when required data or controls are unavailable.
- Return ALLOW, REJECT, REDUCE SIZE, INSUFFICIENT DATA,
  UNAVAILABLE, or EMERGENCY STOP outcomes where supported.
- Return reasons, limits, violations, and evidence.
- Remain analytical and read-only.
- Never submit an order automatically.
- Never invoke live broker execution.

User Journey

Authenticated User
      │
      ▼
GET /user/dashboard
      │
      ▼
frontend/proxy.ts
      │
      ▼
frontend/app/user/dashboard/page.tsx
      │
      ▼
Select or Enter Symbol
      │
      ▼
GET /api/v1/risk/gate/{symbol}
      │
      ▼
Authentication and Authorization
      │
      ▼
Symbol Validation
      │
      ▼
Portfolio + Position + Balance Context
      │
      ▼
Market Price + Volatility Context
      │
      ▼
Exposure + Concentration + Size Checks
      │
      ▼
Operating Mode + Emergency Stop
      │
      ▼
Risk Decision + Reasons + Evidence
      │
      ├────────► ALLOW
      ├────────► REJECT
      ├────────► REDUCE SIZE
      ├────────► INSUFFICIENT DATA
      ├────────► UNAVAILABLE
      └────────► EMERGENCY STOP

Entry Point

Browser Route

/user/dashboard

Dedicated Risk Page

UNKNOWN

Dashboard Risk Surface

frontend/app/user/dashboard/page.tsx

Selected Entry File

frontend/app/user/dashboard/page.tsx

Middleware

frontend/proxy.ts

Frontend Requests

GET OR DYNAMIC `/api/v1/risk/gate/${cleanSymbol}`
Source: frontend/services/riskService.ts:24
Credentials: UNKNOWN

Backend Routes

GET /api/v1/analytics
Function: get_analytics
File: backend/app/main.py:595
Markers: Depends, authenticated, balance, live, locked, market, mode, owner, paper, portfolio, position, price, risk, strategy, symbol, user_id

POST /api/v1/paper/orders
Function: submit_authenticated_paper_order
File: backend/app/main.py:647
Markers: Depends, authenticated, balance, live, locked, market, mode, owner, paper, portfolio, position, price, risk, strategy, symbol, user_id

GET /api/v1/market/live-price/{symbol}
Function: api_live_market_price
File: backend/app/main.py:706
Markers: Depends, authenticated, balance, live, market, mode, owner, paper, portfolio, position, price, risk, strategy, symbol, user_id

GET /api/v1/portfolio/positions
Function: api_portfolio_positions
File: backend/app/main.py:711
Markers: Depends, authenticated, balance, live, market, mode, owner, paper, portfolio, position, price, risk, strategy, symbol, user_id

GET /api/v1/strategy/decision/{symbol}
Function: api_strategy_decision
File: backend/app/main.py:722
Markers: Depends, authenticated, balance, live, market, mode, owner, paper, portfolio, position, price, risk, strategy, symbol, user_id

GET /api/v1/risk/gate/{symbol}
Function: api_risk_gate
File: backend/app/main.py:727
Markers: Depends, authenticated, balance, live, market, owner, paper, portfolio, position, price, risk, strategy, symbol, user_id

Security and Behaviour

authentication_detected

True

authorization_detected

True

ownership_detected

True

symbol_validation_detected

True

portfolio_dependency_detected

True

market_dependency_detected

True

strategy_dependency_detected

True

exposure_markers_detected

True

cash_or_buying_power_detected

True

order_size_limit_detected

True

loss_or_drawdown_limit_detected

True

mode_enforcement_detected

True

emergency_stop_detected

True

fail_closed_markers_detected

True

deterministic_markers_detected

True

evidence_markers_detected

True

read_only_markers_detected

True

paper_only_markers_detected

True

live_execution_disabled_detected

True

automatic_order_submission_detected

False

csrf_detected

True

rate_limit_detected

False

Frontend States

loading_detected

True

error_detected

True

empty_or_insufficient_data_detected

True

allow_state_detected

True

reject_state_detected

True

reduce_size_state_detected

False

emergency_stop_state_detected

True

reason_detected

False

refresh_detected

True

retry_detected

False

stale_detected

False

responsive_detected

True

accessibility_detected

True

Tests

backend/app/stacks/chat_public/tests/test_capability_state_registry.py

test_registry_is_read_only_and_complete
test_registry_uses_declared_state_categories
test_drawdown_guard_is_not_called_without_balance
test_registry_summary_is_grounded_in_rows
test_developer_response_contains_capability_state
test_developer_capabilities_remain_grounded
test_unverified_adapter_and_async_states_require_attention

backend/app/stacks/chat_public/tests/test_developer_response_builder.py

test_developer_response_is_structured
test_developer_response_does_not_claim_unverified_tests
test_developer_runtime_bypasses_ollama
test_developer_claim_without_permission_uses_ollama
test_general_conversation_still_uses_ollama

backend/app/stacks/identity_auth/tests/test_stage9d_c5_i_authorization_policy.py

test_canonical_roles
test_subscription_tiers_remain_separate
test_owner_normalizes_to_developer
test_administrative_roles
test_unknown_roles_fail_closed
test_admin_user_management_permissions
test_developer_inherits_admin_permissions
test_dangerous_permissions_remain_separate
test_authorization_decisions_fail_closed

backend/app/stacks/journal_ledger/tests/test_decision_event_contract.py

test_draft_normalizes_and_freezes_contract
test_canonical_hash_is_deterministic
test_payload_key_order_does_not_change_hash
test_naive_datetime_is_rejected
test_invalid_confidence_is_rejected
test_first_persisted_event_requires_no_previous_hash
test_non_first_event_requires_previous_hash
test_content_hash_mismatch_is_rejected
test_chain_link_requires_contiguous_sequence_and_hash

backend/app/stacks/journal_ledger/tests/test_decision_event_repository.py

test_first_append_allocates_sequence_one
test_second_append_links_previous_hash
test_duplicate_is_rejected_before_insert
test_commit_failure_rolls_back
test_repository_exposes_no_mutation_methods
test_append_rejects_naive_recorded_at

Current Gaps

No dedicated Risk Analysis page was detected; the risk surface appears to be embedded in the authenticated dashboard.

FUNCTION FLOW GRAPH

Authenticated User
      │
      ▼
GET /user/dashboard
      │
      ▼
frontend/proxy.ts
      │
      ▼
frontend/app/user/dashboard/page.tsx
      │
      ▼
Symbol Selection
      │
      ▼
GET /api/v1/risk/gate/{symbol}
      │
      ▼
Authentication
      │
      ▼
Authorization
      │
      ▼
Symbol Validation
      │
      ▼
Portfolio Ownership Scope
      │
      ▼
Positions + Balances + Cash
      │
      ▼
Market Price + Volatility
      │
      ▼
Exposure + Concentration
      │
      ▼
Position and Order Size Limits
      │
      ▼
Loss and Drawdown Limits
      │
      ▼
Strategy Context
      │
      ▼
SAFE / SIMULATION / LOCKED / EMERGENCY_STOP
      │
      ▼
Risk Decision
      │
      ├────────► ALLOW
      ├────────► REJECT
      ├────────► REDUCE SIZE
      ├────────► INSUFFICIENT DATA
      ├────────► UNAVAILABLE
      └────────► EMERGENCY STOP

Repository Files

Frontend

frontend/services/riskService.ts
frontend/app/register/page.tsx
frontend/app/components/layout/DashboardShell.tsx
frontend/app/components/cards/RiskGateCard.tsx
frontend/app/api/v1/risk/gate/[symbol]/route.ts
frontend/app/user/components/PaperOrderPanel.tsx
frontend/app/user/components/NeuroWelcomeBriefing.tsx

Frontend Services

frontend/services/riskService.ts
frontend/app/components/cards/RiskGateCard.tsx
frontend/app/api/v1/risk/gate/[symbol]/route.ts

Backend Routes

backend/app/main.py

Risk Files

backend/app/stacks/risk/limits.py
backend/app/stacks/risk/risk_service.py
backend/app/stacks/strategy_candidate_sandbox/risk_gate_contract.py
backend/app/stacks/strategy_candidate_sandbox/risk_gate_validator.py

Portfolio Files

No portfolio dependency file isolated.

Market Files

No market dependency file isolated.

Strategy Files

backend/app/stacks/strategy_candidate_sandbox/qwen_context_response_contract.py
backend/app/stacks/strategy_candidate_sandbox/risk_gate_contract.py
backend/app/stacks/strategy_candidate_sandbox/risk_gate_validator.py
backend/app/stacks/strategy_candidate_sandbox/safe_read_only_architecture_inspector.py
backend/app/stacks/strategy_candidate_sandbox/trade_simulation_enablement_gate_contract.py
backend/app/stacks/strategy_candidate_sandbox/trade_simulation_enablement_gate_validator.py

Mode and Safety Files

No runtime-mode or safety file isolated.

Emergency Stop Files

No emergency-stop file isolated.

Calculation Files

backend/app/stacks/risk/limits.py

Evidence Files

backend/app/stacks/journal_ledger/decision_event_contract.py
backend/app/stacks/journal_ledger/tests/test_decision_event_contract.py
backend/app/stacks/journal_ledger/tests/test_decision_event_repository.py

Services

backend/app/stacks/risk/risk_service.py

Facades

No risk facade file isolated.

Repositories

backend/app/stacks/journal_ledger/tests/test_decision_event_repository.py

Models

backend/app/stacks/identity_auth/authorization_policy.py
backend/app/stacks/identity_auth/route_protection.py
backend/app/stacks/identity_auth/tests/test_stage9d_c5_i_authorization_policy.py

Schemas

backend/app/stacks/chat_public/tests/test_developer_response_builder.py
backend/app/stacks/journal_ledger/decision_event_contract.py
backend/app/stacks/journal_ledger/tests/test_decision_event_contract.py
backend/app/stacks/strategy_candidate_sandbox/qwen_context_response_contract.py
backend/app/stacks/strategy_candidate_sandbox/risk_gate_contract.py
backend/app/stacks/strategy_candidate_sandbox/trade_simulation_enablement_gate_contract.py

Providers

No risk provider file isolated.

Paper-Trading Files

backend/app/stacks/execution/paper_broker.py
backend/app/stacks/strategy_candidate_sandbox/trade_simulation_enablement_gate_contract.py
backend/app/stacks/strategy_candidate_sandbox/trade_simulation_enablement_gate_validator.py

Execution Files

backend/app/stacks/execution/paper_broker.py

Tests

backend/app/stacks/chat_public/tests/test_capability_state_registry.py
backend/app/stacks/chat_public/tests/test_developer_response_builder.py
backend/app/stacks/identity_auth/tests/test_stage9d_c5_i_authorization_policy.py
backend/app/stacks/journal_ledger/tests/test_decision_event_contract.py
backend/app/stacks/journal_ledger/tests/test_decision_event_repository.py

Launch Dependency

Required Before Launch

YES

Blocks

Strategy safety evaluation

Paper-order approval

Position-sizing controls

Exposure and concentration controls

Loss and drawdown controls

Emergency-stop enforcement

Controlled early-user launch

Depends On

Authenticated session

Frontend risk service

Risk backend route

Symbol validation

Portfolio ownership

Positions and balances

Cash and buying power

Market prices

Volatility and freshness

Risk policies and limits

Strategy context

Operating-mode enforcement

Emergency-stop enforcement

Evidence and rejection reasons

Read-only boundary

Paper-only boundary

Disabled live execution

FINAL VERDICT

Function Exists: YES

Dedicated Risk Page: NOT DETECTED

Frontend Connected: DETECTED

Backend Route Present: YES

Authentication: DETECTED

Ownership: DETECTED

Symbol Validation: DETECTED

Portfolio Dependency: DETECTED

Market Dependency: DETECTED

Exposure Controls: DETECTED

Cash or Buying Power: DETECTED

Order Size Limits: DETECTED

Loss or Drawdown Limits: DETECTED

Mode Enforcement: DETECTED

Emergency Stop: DETECTED

Fail-Closed Markers: DETECTED

Deterministic Logic: DETECTED

Evidence and Reasons: DETECTED

Read-Only Boundary: DETECTED

Paper-Only Boundary: DETECTED

Live Execution Disabled: DETECTED

Automatic Order Submission Markers: NOT DETECTED

Relevant Tests: PRESENT

Live Verification: NOT COMPLETE

Launch Ready: UNVERIFIED

Overall Classification

PARTIALLY VERIFIED

Launch Classification

CRITICAL

---



---

FUNCTION PATH 10 — MARKET DATA AND LIVE PRICE

Function Status

Inventory Status: INITIAL INVENTORY COMPLETE
Implementation Status: IMPLEMENTED — SOURCE VERIFICATION PENDING
Qualification Status: UNVERIFIED
Launch Importance: CRITICAL
Last Updated: 2026-07-31
Evidence Source: runtime/system_inventory/function_path_10_market_data_20260731_144949/function_path_10_market_data_inventory.json

Purpose

The Market Data and Live Price function retrieves verified pricing
and market context used by the NeuroVest dashboard, portfolio,
analytics, strategy, risk, and paper-trading functions.

Its purpose is to:

- Validate and normalize requested symbols.
- Retrieve current market quotes from approved providers.
- Retrieve historical bars where supported.
- Select approved providers and fallbacks.
- Validate numeric quote values.
- Record provider and observation timestamps.
- Detect stale, delayed, malformed, or unavailable data.
- Normalize provider responses into stable contracts.
- Return controlled unavailable states when providers fail.
- Prevent missing or malformed prices from being fabricated.
- Keep market-data retrieval read-only.
- Never create an order automatically.
- Never invoke live broker execution.

User Journey

Authenticated User
      │
      ▼
GET /user/dashboard
      │
      ▼
frontend/proxy.ts
      │
      ▼
frontend/app/user/dashboard/page.tsx
      │
      ▼
Portfolio / Analytics / Strategy / Risk Consumer
      │
      ▼
Select or Request Symbol
      │
      ▼
GET /api/v1/market/live-price/{symbol}
      │
      ▼
Authentication and Authorization
      │
      ▼
Backend Symbol Validation
      │
      ▼
Market-Data Service
      │
      ▼
Provider Selection
      │
      ├────────► Primary Provider
      └────────► Approved Fallback
      │
      ▼
Quote Validation
      │
      ├────────► CURRENT
      ├────────► DELAYED
      ├────────► STALE
      └────────► UNAVAILABLE
      │
      ▼
Normalized Market Response

Entry Point

Browser Route

/user/dashboard

Dedicated Market Page

UNKNOWN

Dashboard Market Surface

frontend/app/user/dashboard/page.tsx

Selected Entry File

frontend/app/user/dashboard/page.tsx

Middleware

frontend/proxy.ts

Frontend Requests

GET OR DYNAMIC `/api/v1/market/live-price/${encodeURIComponent(
      cleanSymbol,
    )}`
Source: frontend/services/marketService.ts:31
Credentials: UNKNOWN

Backend Routes

GET /api/v1/analytics
Function: get_analytics
File: backend/app/main.py:595
Markers: Depends, authenticated, live, paper, portfolio, price, risk, strategy, symbol, timestamp

POST /api/v1/paper/orders
Function: submit_authenticated_paper_order
File: backend/app/main.py:647
Markers: Depends, authenticated, live, paper, portfolio, price, risk, strategy, symbol

GET /api/v1/market/live-price/{symbol}
Function: api_live_market_price
File: backend/app/main.py:706
Markers: Depends, authenticated, live, paper, portfolio, price, risk, strategy, symbol

GET /api/v1/portfolio/positions
Function: api_portfolio_positions
File: backend/app/main.py:711
Markers: Depends, authenticated, live, paper, portfolio, price, risk, strategy, symbol

GET /api/v1/strategy/decision/{symbol}
Function: api_strategy_decision
File: backend/app/main.py:722
Markers: Depends, authenticated, live, paper, portfolio, price, risk, strategy, symbol

GET /api/v1/risk/gate/{symbol}
Function: api_risk_gate
File: backend/app/main.py:727
Markers: Depends, authenticated, live, paper, portfolio, price, risk, strategy, symbol

GET /status
Function: market_data_status
File: backend/app/stacks/market_data/api_router.py:102
Markers: broker, cache, historical, live, provider, quote, symbol

GET /quote/{symbol}
Function: market_data_quote
File: backend/app/stacks/market_data/api_router.py:168
Markers: broker, cache, historical, live, provider, quote, symbol

GET /historical/{symbol}
Function: market_data_historical
File: backend/app/stacks/market_data/api_router.py:203
Markers: broker, cache, historical, live, provider, quote, symbol

GET /api/v1/analytics
Function: analytics
File: backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py:24
Markers: authenticated, authorization, strategy

POST /api/v1/admin/backup
Function: admin_backup
File: backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py:32
Markers: authenticated, authorization, strategy

GET /api/v1/market-data/status
Function: market_status
File: backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py:40
Markers: authenticated, authorization, strategy

Controls and Behaviour

authentication_detected

True

authorization_detected

True

symbol_validation_detected

True

provider_selection_detected

True

fallback_detected

True

cache_detected

True

timestamp_detected

True

freshness_detected

True

numeric_validation_detected

True

non_positive_price_rejection_detected

True

historical_data_detected

True

provider_timeout_detected

True

controlled_unavailable_detected

True

no_fabrication_markers_detected

False

portfolio_dependency_detected

True

analytics_dependency_detected

True

strategy_dependency_detected

True

risk_dependency_detected

True

paper_dependency_detected

True

read_only_detected

True

automatic_order_submission_detected

False

live_execution_disabled_detected

True

rate_limit_detected

True

csrf_detected

False

Frontend States

loading_detected

True

error_detected

True

empty_or_unavailable_detected

True

stale_detected

True

delayed_detected

False

last_updated_detected

False

provider_display_detected

True

market_status_detected

False

retry_detected

False

refresh_detected

True

responsive_detected

True

accessibility_detected

True

Tests

backend/app/stacks/chat_public/tests/test_aiq004d2_developer_debug_routing.py

test_fastapi_http_500_routes_to_developer_context
test_python_traceback_routes_to_developer_context
test_market_data_api_request_preserves_market_routing
test_generic_endpoint_question_does_not_force_debug_routing
test_live_trade_request_remains_blocked_before_debug_routing

backend/app/stacks/chat_public/tests/test_capability_state_registry.py

test_registry_is_read_only_and_complete
test_registry_uses_declared_state_categories
test_drawdown_guard_is_not_called_without_balance
test_registry_summary_is_grounded_in_rows
test_developer_response_contains_capability_state
test_developer_capabilities_remain_grounded
test_unverified_adapter_and_async_states_require_attention

backend/app/stacks/db_runtime/tests/test_transaction_guard.py

test_guard_does_not_rollback_successful_scope
test_guard_rolls_back_write_failure_and_reraises
test_guard_rolls_back_commit_failure_and_reraises
test_guard_rolls_back_cancellation
test_approved_write_path_uses_transaction_guard
test_legacy_market_schema_remains_isolated

backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py

test_route_policy_inventory
test_public_route_requires_no_token
test_authenticated_route_rejects_missing_token
test_authenticated_route_accepts_principal
test_admin_route_rejects_non_admin
test_admin_route_accepts_server_claim
test_unknown_route_preserves_not_found
test_refresh_token_validation_failure_is_unauthorized

backend/app/stacks/market_data/tests/test_provider_contract.py

test_symbol_normalization
test_empty_symbol_rejected
test_quote_normalizes_fields
test_naive_quote_timestamp_rejected
test_invalid_ohlc_rejected
test_request_date_order_enforced
test_result_requires_matching_symbol
test_fixture_satisfies_protocol
test_fixture_returns_canonical_quote
test_fixture_returns_canonical_bars

backend/app/stacks/market_data/tests/test_provider_runtime.py

test_registry_registers_and_selects_by_priority
test_registry_rejects_duplicate_name
test_registry_ignores_disabled_provider
test_cache_returns_unexpired_value
test_cache_expires_value
test_cache_evicts_least_recently_used
test_market_session_classification
test_market_session_rejects_naive_datetime
test_router_uses_highest_priority_provider
test_router_falls_back_after_provider_failure
test_router_fails_closed_when_all_providers_fail
test_router_quote_cache_prevents_second_provider_call
test_router_returns_canonical_historical_result

backend/app/stacks/market_data/tests/test_runtime_composition.py

test_production_runtime_constructs_without_network
test_runtime_components_are_shared
test_read_only_routes_are_declared
test_status_endpoint_is_network_free
test_quote_endpoint_uses_shared_router
test_historical_endpoint_uses_shared_router
test_invalid_historical_range_fails_closed

backend/app/stacks/market_data/tests/test_stage8_runtime_qualification.py

test_quote_cache_prevents_repeated_provider_call
test_quote_cache_expiry_forces_refresh
test_use_cache_false_always_calls_provider
test_router_falls_back_after_quote_failure
test_router_falls_back_after_historical_failure
test_router_fails_closed_when_every_provider_fails
test_api_translates_provider_failure_to_503
test_api_rejects_invalid_historical_range
test_status_endpoint_does_not_call_provider

backend/app/stacks/market_data/tests/test_yfinance_provider.py

test_module_import_does_not_require_yfinance
test_wrapper_satisfies_provider_contract
test_capabilities_are_declared
test_numeric_quote_is_normalized
test_mapping_quote_is_normalized
test_quote_symbol_mismatch_fails
test_quote_loader_failure_is_translated
test_historical_mapping_is_normalized
test_historical_rows_are_sorted
test_historical_limit_is_applied
test_historical_loader_failure_is_translated
test_healthcheck_does_not_load_dependencies

backend/app/test/test_stage8f_graph_materialization.py

test_all_layers_have_declared_nodes
test_required_facades_are_declared_in_l3
test_frontend_workspaces_and_proxies_are_declared
test_snapshot_materializes_declared_topology_without_events
test_real_node_activation_overrides_declared_state
test_real_edge_materializes_both_endpoints
test_declared_edge_becomes_observed_without_losing_relation
test_stage8f_preserves_version_two_contract

backend/app/test/test_trading_pipeline.py

test_trading_pipeline_success
test_trading_pipeline_blocked
test_agent_router_trips_kill_switch

Current Gaps

No dedicated market-data page was detected; market data appears to be consumed by authenticated dashboard functions.

FUNCTION FLOW GRAPH

Authenticated User
      │
      ▼
GET /user/dashboard
      │
      ▼
frontend/proxy.ts
      │
      ▼
frontend/app/user/dashboard/page.tsx
      │
      ▼
Market Data Consumer
      │
      ▼
Symbol Request
      │
      ▼
GET /api/v1/market/live-price/{symbol}
      │
      ▼
Authentication
      │
      ▼
Authorization
      │
      ▼
Symbol Validation
      │
      ▼
Market-Data Service
      │
      ▼
Provider Adapter
      │
      ├────────► Primary Provider
      └────────► Approved Fallback
      │
      ▼
Price + Timestamp Validation
      │
      ▼
Freshness Evaluation
      │
      ├────────► CURRENT
      ├────────► DELAYED
      ├────────► STALE
      └────────► UNAVAILABLE
      │
      ▼
Normalized Market Response
      │
      ├────────► Portfolio
      ├────────► Analytics
      ├────────► Strategy
      ├────────► Risk
      └────────► Paper Trading

Repository Files

Frontend

frontend/app/page.tsx
frontend/services/marketService.ts
frontend/services/portfolioService.ts
frontend/app/components/layout/DashboardShell.tsx
frontend/app/components/cards/LivePriceCard.tsx
frontend/app/components/ticker/MarketTickerBanner.tsx
frontend/app/api/v1/market/live-price/[symbol]/route.ts
frontend/app/api/v1/portfolio/positions/route.ts
frontend/app/user/dashboard/page.tsx

Frontend Services

frontend/services/marketService.ts
frontend/services/portfolioService.ts
frontend/app/components/cards/LivePriceCard.tsx
frontend/app/components/ticker/MarketTickerBanner.tsx
frontend/app/api/v1/market/live-price/[symbol]/route.ts
frontend/app/api/v1/portfolio/positions/route.ts

Backend Routes

backend/app/main.py
backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py
backend/app/stacks/market_data/api_router.py

Market Files

backend/app/stacks/market_data/api_router.py
backend/app/stacks/market_data/base.py
backend/app/stacks/market_data/dto.py
backend/app/stacks/market_data/feed.py
backend/app/stacks/market_data/market_data_service.py
backend/app/stacks/market_data/market_session.py
backend/app/stacks/market_data/price.py
backend/app/stacks/market_data/provider_contract.py
backend/app/stacks/market_data/provider_registry.py
backend/app/stacks/market_data/provider_router.py
backend/app/stacks/market_data/runtime_composition.py
backend/app/stacks/market_data/tests/test_provider_contract.py
backend/app/stacks/market_data/tests/test_provider_runtime.py
backend/app/stacks/market_data/tests/test_runtime_composition.py
backend/app/stacks/market_data/tests/test_stage8_runtime_qualification.py
backend/app/stacks/market_data/tests/test_yfinance_provider.py
backend/app/stacks/market_data/yfinance_historical_bars_adapter.py
backend/app/stacks/market_data/yfinance_ingestor.py
backend/app/stacks/market_data/yfinance_provider.py

Provider Files

backend/app/stacks/market_data/provider_contract.py
backend/app/stacks/market_data/provider_registry.py
backend/app/stacks/market_data/provider_router.py
backend/app/stacks/market_data/tests/test_provider_contract.py
backend/app/stacks/market_data/tests/test_provider_runtime.py
backend/app/stacks/market_data/tests/test_yfinance_provider.py
backend/app/stacks/market_data/yfinance_provider.py

Adapter Files

backend/app/stacks/market_data/yfinance_historical_bars_adapter.py

Cache Files

No market cache file isolated.

Historical Data Files

backend/app/stacks/market_data/yfinance_historical_bars_adapter.py

Normalization Files

No market normalization file isolated.

Validation Files

backend/app/stacks/db_runtime/tests/test_transaction_guard.py

Services

backend/app/stacks/market_data/market_data_service.py

Facades

No market-data facade file isolated.

Repositories

No market-data repository file isolated.

Models

backend/app/stacks/chat_public/cognitive_model_router.py
backend/app/stacks/identity_auth/route_protection.py
backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py

Schemas

backend/app/stacks/chat_public/developer_response_builder.py
backend/app/stacks/market_data/dto.py
backend/app/stacks/market_data/provider_contract.py
backend/app/stacks/market_data/tests/test_provider_contract.py

Portfolio Dependencies

backend/app/stacks/market_data/runtime_composition.py
backend/app/stacks/market_data/tests/test_runtime_composition.py
backend/app/stacks/portfolio/allocator.py

Analytics Dependencies

No analytics dependency file isolated.

Strategy Dependencies

backend/app/stacks/strategy/engine.py
backend/app/stacks/strategy/llm_strategy_engine.py

Risk Dependencies

No risk dependency file isolated.

Paper-Trading Dependencies

backend/app/stacks/execution/paper_broker.py

Evidence Files

No market-data evidence file isolated.

Execution Files

backend/app/stacks/execution/paper_broker.py

Tests

backend/app/stacks/chat_public/tests/test_aiq004d2_developer_debug_routing.py
backend/app/stacks/chat_public/tests/test_capability_state_registry.py
backend/app/stacks/db_runtime/tests/test_transaction_guard.py
backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py
backend/app/stacks/market_data/tests/test_provider_contract.py
backend/app/stacks/market_data/tests/test_provider_runtime.py
backend/app/stacks/market_data/tests/test_runtime_composition.py
backend/app/stacks/market_data/tests/test_stage8_runtime_qualification.py
backend/app/stacks/market_data/tests/test_yfinance_provider.py
backend/app/test/test_stage8f_graph_materialization.py
backend/app/test/test_trading_pipeline.py

Launch Dependency

Required Before Launch

YES

Blocks

Portfolio valuation

Analytics calculations

Strategy analysis

Risk analysis

Paper-trading pricing

Market status display

Controlled early-user launch

Depends On

Frontend market service

Market backend route

Symbol validation

Provider availability

Provider adapters

Quote normalization

Numeric validation

Timestamp and freshness handling

Controlled fallback behavior

Failure handling

Read-only boundaries

Disabled live execution

FINAL VERDICT

Function Exists: YES

Dedicated Market Page: NOT DETECTED

Frontend Connected: DETECTED

Backend Route Present: YES

Authentication: DETECTED

Symbol Validation: DETECTED

Provider Selection: DETECTED

Fallback Support: DETECTED

Quote Timestamp: DETECTED

Freshness Handling: DETECTED

Numeric Validation: DETECTED

Historical Data: DETECTED

Controlled Unavailable State: DETECTED

Read-Only Boundary: DETECTED

Automatic Order Submission: NOT DETECTED

Live Execution Disabled: DETECTED

Relevant Tests: PRESENT

Live Verification: NOT COMPLETE

Launch Ready: UNVERIFIED

Overall Classification

PARTIALLY VERIFIED

Launch Classification

CRITICAL

---



---

FUNCTION PATH 11 — NEURO AI CHAT AND DECISION ENGINE

Function Status

Inventory Status: INITIAL INVENTORY COMPLETE
Implementation Status: IMPLEMENTED — SOURCE VERIFICATION PENDING
Qualification Status: UNVERIFIED
Launch Importance: CRITICAL
Last Updated: 2026-07-31
Evidence Source: runtime/system_inventory/function_path_11_neuro_ai_chat_20260731_153046/function_path_11_neuro_ai_chat_inventory.json

Purpose

The Neuro AI Chat and Decision Engine accepts authenticated user
messages, loads authorized conversation and financial context, routes
the request to the correct deterministic tools or Ollama model,
verifies the response, persists the conversation, and returns a
normalized response to the frontend.

Its purpose is to:

- Require authenticated chat access.
- Enforce thread and conversation ownership.
- Detect user intent.
- Load recent conversation history.
- Load summary memory and remembered facts.
- Load authorized portfolio context where relevant.
- Use RAG only when retrieval is requested.
- Use deterministic math for calculations.
- Select the appropriate cognitive model profile.
- Compose system, role, context, and user prompts.
- Invoke Ollama.
- Verify deterministic math, citations, and paper-only boundaries.
- Capture strategy proposals without executing them.
- Persist user and assistant messages.
- Persist conversation state and memory updates.
- Return traceable evidence and runtime metadata.
- Never submit an order automatically.
- Never enable live broker execution.

Primary Function Flow

Authenticated User
      │
      ▼
/user/chat or Embedded Neuro Workspace
      │
      ▼
frontend/services/chatService.ts
      │
      ▼
frontend/app/api/v1/chat/route.ts
      │
      ▼
POST /api/v1/chat
      │
      ▼
chat_api.py
      │
      ▼
chat_service.py
      │
      ▼
conversation_service.py
      │
      ▼
chat_runtime.py
      │
      ├────────► Authentication
      ├────────► Thread Ownership
      ├────────► Intent Detection
      ├────────► Context Assembly
      ├────────► Conversation Memory
      ├────────► RAG Retrieval
      ├────────► Deterministic Math
      ├────────► Model Routing
      ├────────► Prompt Composition
      ├────────► Ollama Invocation
      ├────────► Response Verification
      ├────────► Strategy Proposal Capture
      ├────────► Message Persistence
      └────────► Response Serialization

Frontend Requests

No direct chat request detected.

Backend Routes

GET /api/v1/graph/live
Function: get_live_graph
File: backend/app/main.py:204
Stages: authentication, observability, ownership, serialization, verification

GET /api/v1/dashboard/summary
Function: summary
File: backend/app/main.py:209
Stages: authentication, observability, ownership, serialization, verification

POST /api/v1/chat
Function: chat_endpoint
File: backend/app/stacks/chat_public/chat_api.py:39
Stages: authentication, backend_route, frontend_entry, observability, serialization

Controls and Behaviour

authentication_detected

True

authorization_detected

True

thread_ownership_detected

True

intent_detection_detected

True

context_assembly_detected

True

memory_detected

True

rag_detected

True

deterministic_math_detected

True

model_routing_detected

True

prompt_composition_detected

True

ollama_detected

True

response_verification_detected

True

strategy_capture_detected

True

conversation_persistence_detected

True

streaming_detected

True

runtime_trace_detected

True

paper_only_boundary_detected

True

live_execution_disabled_detected

True

automatic_order_submission_detected

True

csrf_detected

True

rate_limit_detected

True

Frontend States

loading_detected

True

error_detected

True

empty_state_detected

True

streaming_state_detected

True

retry_detected

False

cancel_detected

True

thinking_state_detected

True

citations_detected

True

responsive_detected

True

accessibility_detected

True

Tests

backend/app/stacks/chat_public/tests/test_aiq004d2_developer_debug_routing.py

test_fastapi_http_500_routes_to_developer_context
test_python_traceback_routes_to_developer_context
test_market_data_api_request_preserves_market_routing
test_generic_endpoint_question_does_not_force_debug_routing
test_live_trade_request_remains_blocked_before_debug_routing

backend/app/stacks/chat_public/tests/test_aiq004d3_runtime_branch_repairs.py

test_software_debugging_reaches_coder_generation
test_explicit_developer_review_remains_deterministic
test_http_is_not_extracted_as_a_symbol
test_real_uppercase_ticker_can_still_be_extracted
test_nonfinancial_intent_never_creates_strategy_candidate
test_financial_strategy_intent_remains_eligible

backend/app/stacks/chat_public/tests/test_aiq004d_generic_response_contract.py

test_prompt_requires_direct_completion
test_prompt_requires_explicit_count_completion
test_prompt_requires_every_requested_component
test_prompt_requires_generic_factual_honesty
test_prompt_contains_no_aiq_domain_contamination
test_prompt_does_not_modify_execution_policy

backend/app/stacks/chat_public/tests/test_aiq005f_general_conversation_model_binding.py

test_router_constant_uses_qualified_general_model
test_ollama_client_registers_qualified_model
test_greeting_uses_qualified_general_model
test_small_talk_uses_qualified_general_model
test_simple_explanation_uses_qualified_general_model
test_software_debugging_remains_on_coder
test_live_execution_remains_blocked

backend/app/stacks/chat_public/tests/test_authenticated_role_truth_boundary.py

test_system_prompt_rejects_conversational_role_elevation
test_user_overlay_remains_user_despite_developer_claim
test_developer_overlay_requires_server_supplied_developer_role
test_local_evidence_requires_explicit_server_permission
test_authenticated_developer_wording_triggers_developer_intent
test_user_wording_alone_does_not_grant_local_evidence
test_authenticated_developer_permission_uses_local_evidence

backend/app/stacks/chat_public/tests/test_capability_state_registry.py

test_registry_is_read_only_and_complete
test_registry_uses_declared_state_categories
test_drawdown_guard_is_not_called_without_balance
test_registry_summary_is_grounded_in_rows
test_developer_response_contains_capability_state
test_developer_capabilities_remain_grounded
test_unverified_adapter_and_async_states_require_attention

backend/app/stacks/chat_public/tests/test_chat_intent_regex.py

test_detect_chat_intent_v2_metadata_and_legacy_compatibility
test_developer_pronoun_i_is_not_detected_as_ticker
test_market_symbol_is_preserved
test_blocked_live_execution_remains_fail_closed
test_chat_intent_legacy_constructor_remains_valid

backend/app/stacks/chat_public/tests/test_chat_timeout_configuration.py

test_default_timeout_alignment
test_timeout_environment_overrides

backend/app/stacks/chat_public/tests/test_cognitive_model_profiles.py

test_fast_profile_is_canonical
test_reason_profile_is_canonical
test_code_and_fallback_profiles_remain_separate
test_general_request_routes_to_neuro_fast
test_strategy_request_routes_to_neuro_reason
test_developer_request_still_routes_to_code_model
test_model_profiles_do_not_grant_execution_authority
test_profile_files_are_plain_text_contracts

backend/app/stacks/chat_public/tests/test_cognitive_model_router.py

test_routing_decision_is_immutable
test_general_greeting_uses_fast_model
test_analysis_and_strategy_use_reason_model
test_code_work_uses_code_model
test_math_declares_deterministic_tool_requirement
test_current_or_account_data_declares_retrieval
test_decision_serializes_complete_contract
test_exact_authenticated_math_prompt_requires_deterministic_tool
test_exact_authenticated_research_prompt_requires_retrieval
test_common_math_phrasing_requires_deterministic_tool
test_local_research_phrasing_requires_retrieval
test_position_size_uses_math_without_retrieval
test_conversation_memory_avoids_retrieval
test_explicit_retrieval_requests_remain_enabled
test_strategy_family_retains_retrieval_contract
test_market_and_portfolio_family_do_not_force_retrieval
test_router_never_exposes_execution_authority

backend/app/stacks/chat_public/tests/test_conversation_service_boundary.py

test_service_exports_existing_store_symbols
test_service_has_no_direct_persistence_imports
test_route_owners_do_not_import_store_or_persistence
test_external_production_consumers_do_not_import_store

backend/app/stacks/chat_public/tests/test_deterministic_math_engine.py

test_registry_is_explicit_and_complete
test_exact_decimal_arithmetic
test_percentage_of
test_percent_change
test_simple_return
test_compound_return
test_cagr
test_expected_value
test_risk_reward
test_position_size
test_portfolio_weights
test_descriptive_statistics
test_sharpe_ratio_is_deterministic
test_sortino_ratio_is_deterministic
test_maximum_drawdown
test_trade_statistics
test_invalid_inputs_fail_closed
test_unsupported_operation_fails_closed
test_sequence_boundary_is_enforced
test_non_finite_or_invalid_values_are_rejected
test_serialized_result_contains_no_float_values
test_math_engine_has_no_execution_or_network_authority

backend/app/stacks/chat_public/tests/test_developer_context_overlay.py

test_general_conversation_does_not_load_developer_overlay
test_self_evaluation_adds_grounded_developer_requirements
test_architecture_mode_adds_architecture_review_rules
test_developer_repo_and_architecture_context_are_bounded

backend/app/stacks/chat_public/tests/test_developer_response_builder.py

test_developer_response_is_structured
test_developer_response_does_not_claim_unverified_tests
test_developer_runtime_bypasses_ollama
test_developer_claim_without_permission_uses_ollama
test_general_conversation_still_uses_ollama

backend/app/stacks/chat_public/tests/test_live_math_runtime_integration.py

test_supported_math_requests_are_extracted
test_percentage_result_is_exact
test_cagr_result_is_deterministic
test_position_size_uses_whole_units
test_unrequested_math_does_not_execute
test_ambiguous_math_fails_controlled
test_division_by_zero_returns_error_evidence
test_runtime_contains_math_integration
test_live_math_has_no_arbitrary_execution

backend/app/stacks/chat_public/tests/test_live_rag_activation.py

test_strategy_family_requests_retrieval
test_retrieval_is_not_called_when_not_requested
test_retrieval_filters_injection_chunks_and_bounds_top_k
test_prompt_contains_page_aware_citation
test_prompt_respects_total_character_boundary
test_retrieval_failure_returns_controlled_bundle
test_chat_runtime_contains_live_rag_integration
test_live_rag_module_does_not_enable_execution

backend/app/stacks/chat_public/tests/test_live_response_verification.py

test_verifier_replaces_missing_math_result
test_verifier_preserves_exact_math_result
test_verifier_replaces_live_execution_claim
test_runtime_verification_occurs_before_persistence
test_runtime_emits_verification_event
test_runtime_persists_verification_evidence
test_runtime_exposes_verification_metadata

backend/app/stacks/chat_public/tests/test_local_rag_index.py

test_chunking_is_deterministic
test_chunking_rejects_invalid_overlap
test_stable_identifiers_are_repeatable
test_source_policy_rejects_secrets_and_runtime
test_prompt_injection_is_detected
test_ingestion_deduplicates_identical_content
test_semantic_retrieval_ranks_relevant_chunk_first
test_no_result_behavior_is_controlled
test_index_contract_contains_no_execution_authority

backend/app/stacks/chat_public/tests/test_pdf_rag_ingestion.py

test_research_pdf_is_allowlisted
test_downloads_pdf_is_not_allowlisted
test_pdf_extraction_returns_page_metadata
test_scanned_or_blank_pdf_returns_no_text
test_discovery_contains_all_research_pdfs
test_pdf_chunks_keep_source_and_page_metadata
test_srrn_pdf_has_extractable_text

backend/app/stacks/chat_public/tests/test_prompt_composer.py

test_composer_preserves_existing_section_delimiter
test_composer_uses_supplied_existing_bounder
test_composer_reports_character_metadata
test_composer_materializes_iterables_once
test_composer_rejects_invalid_limit
test_composer_rejects_non_string_bounder_result
test_prompt_composition_is_immutable

backend/app/stacks/chat_public/tests/test_public_chat_controls.py

test_public_chat_contract_accepts_valid_text
test_public_chat_contract_rejects_empty_text
test_public_chat_contract_rejects_oversized_text
test_public_chat_safety_denies_restricted_action
test_public_chat_safety_allows_general_discussion
test_public_chat_timeout_maps_to_504
test_public_chat_dependency_failure_maps_to_503
test_public_chat_rate_limit_maps_to_429
test_public_chat_safety_denial_maps_to_403
test_route_is_decorated_with_public_controls
test_public_control_wrapper_preserves_signature
test_payload_boundary_ignores_injected_dependencies
test_payload_boundary_rejects_oversized_payload
test_payload_boundary_rejects_empty_payload
test_payload_boundary_safety_uses_only_payload
test_payload_boundary_still_rejects_restricted_payload
test_missing_payload_argument_fails_closed
test_configured_payload_wrapper_preserves_signature
test_chat_route_configures_payload_argument

backend/app/stacks/chat_public/tests/test_rag_citation_generation_contract.py

test_missing_approved_citation_is_appended
test_existing_approved_citation_is_preserved
test_numeric_reference_does_not_satisfy_contract
test_empty_citation_set_does_not_modify_response

backend/app/stacks/chat_public/tests/test_response_verification.py

test_ordinary_response_passes
test_exact_math_result_passes
test_decimal_equivalent_math_result_passes
test_missing_math_result_is_repaired
test_position_size_result_passes
test_allowed_citation_passes
test_missing_required_citation_is_repaired
test_unapproved_citation_is_repaired
test_live_execution_claim_fails_closed
test_safe_live_execution_denial_passes
test_empty_response_fails_closed
test_result_serialization_is_structured
test_verifier_has_no_external_authority

backend/app/stacks/chat_public/tests/test_role_overlay_injection.py

test_role_overlay_is_inserted_in_correct_order
test_no_overlay_path_remains_supported
test_chat_api_passes_principal_to_runtime
test_runtime_passes_overlay_and_intent_metadata
test_unknown_role_fails_closed_to_user_overlay
test_deterministic_developer_path_remains_grounded

backend/app/stacks/chat_public/tests/test_role_overlay_principal_dependency.py

test_chat_endpoint_has_authenticated_principal_dependency
test_chat_endpoint_passes_principal_to_runtime
test_chat_endpoint_has_no_undefined_principal_reference

backend/app/stacks/chat_public/tests/test_role_overlay_registry.py

test_every_canonical_role_has_an_overlay
test_every_subscription_tier_has_an_overlay
test_role_aliases_use_canonical_roles
test_unknown_role_fails_closed_to_user
test_tier_normalization_uses_canonical_enum
test_unknown_tier_does_not_invent_entitlement
test_principal_claims_resolve_role_and_tier
test_missing_claims_fail_closed_to_user
test_overlay_is_conversational_not_authoritative
test_overlay_models_are_immutable
test_role_overlay_registry_is_immutable
test_admin_does_not_receive_repository_context
test_owner_alias_resolves_to_developer_not_new_role

frontend/tests/e2e/08-objective4g-d-authenticated-live-turn.spec.ts

/
qualifies authenticated math, RAG, verification, and replay

frontend/tests/e2e/09-objective4h-b-broad-prompt-matrix.spec.ts

qualifies broad authenticated cognitive behavior

Current Gaps

No direct frontend /api/v1/chat request was detected.

Potential automatic order-submission markers were detected and require direct review.

FUNCTION FLOW GRAPH

Authenticated User
      │
      ▼
Chat Interface
      │
      ▼
Next.js Chat Proxy
      │
      ▼
POST /api/v1/chat
      │
      ▼
Authentication + Role Overlay
      │
      ▼
Thread Ownership
      │
      ▼
Intent Detection
      │
      ▼
Context + Memory Assembly
      │
      ├────────► Portfolio Context
      ├────────► RAG Retrieval
      └────────► Deterministic Math
      │
      ▼
Cognitive Model Routing
      │
      ▼
Prompt Composition
      │
      ▼
Ollama Invocation
      │
      ▼
Response Verification
      │
      ├────────► Pass
      ├────────► Repair
      └────────► Fail Closed
      │
      ▼
Strategy Proposal Capture
      │
      ▼
Conversation Persistence
      │
      ▼
Normalized Frontend Response

Repository Files

Frontend

frontend/app/api/v1/chat/route.ts
frontend/app/components/chat/FloatingChatWidget.tsx
frontend/app/components/workspaces/GraphWorkspacePanel.tsx
frontend/app/components/workspaces/LearningWorkspacePanel.tsx
frontend/app/components/workspaces/MarketWorkspace.tsx
frontend/app/components/workspaces/NeuroWorkspace.tsx
frontend/app/components/workspaces/ObservabilityWorkspacePanel.tsx
frontend/app/components/workspaces/OverviewWorkspace.tsx
frontend/app/components/workspaces/SharedNeuroWorkspace.tsx
frontend/app/layout.tsx
frontend/app/user/chat/page.tsx
frontend/app/user/dashboard/page.tsx
frontend/components/RoleAwareWorkspaceNav.tsx
frontend/components/app-shell/AppShell.tsx
frontend/components/app-shell/PageHeader.tsx
frontend/components/app-shell/WorkspaceContextBar.tsx
frontend/components/app-shell/WorkspacePage.tsx
frontend/proxy.ts
frontend/services/chat/chatContracts.ts
frontend/services/chatService.ts

Backend

backend/app/core/cognitive_types.py
backend/app/core/runtime_trace.py
backend/app/llm_bridge/cognition_core.py
backend/app/llm_bridge/neuro_cli.py
backend/app/main.py
backend/app/stacks/chat_public/base.py
backend/app/stacks/chat_public/capability_state_registry.py
backend/app/stacks/chat_public/chat_api.py
backend/app/stacks/chat_public/chat_intent_regex.py
backend/app/stacks/chat_public/chat_memory.py
backend/app/stacks/chat_public/chat_runtime.py
backend/app/stacks/chat_public/chat_service.py
backend/app/stacks/chat_public/chat_system_prompt.py
backend/app/stacks/chat_public/cognitive_model_router.py
backend/app/stacks/chat_public/context/__init__.py
backend/app/stacks/chat_public/context/context_assembler.py
backend/app/stacks/chat_public/context_loader.py
backend/app/stacks/chat_public/contracts/__init__.py
backend/app/stacks/chat_public/contracts/chat_contracts.py
backend/app/stacks/chat_public/conversation_service.py
backend/app/stacks/chat_public/conversation_store.py
backend/app/stacks/chat_public/developer_response_builder.py
backend/app/stacks/chat_public/math_tools/__init__.py
backend/app/stacks/chat_public/math_tools/contracts.py
backend/app/stacks/chat_public/math_tools/engine.py
backend/app/stacks/chat_public/math_tools/live_math.py
backend/app/stacks/chat_public/ollama_chat_client.py
backend/app/stacks/chat_public/persistence/__init__.py
backend/app/stacks/chat_public/persistence/chat_models.py
backend/app/stacks/chat_public/prompt_composer.py
backend/app/stacks/chat_public/public_controls.py
backend/app/stacks/chat_public/rag/__init__.py
backend/app/stacks/chat_public/rag/contracts.py
backend/app/stacks/chat_public/rag/embedding_client.py
backend/app/stacks/chat_public/rag/live_retrieval.py
backend/app/stacks/chat_public/rag/local_index.py
backend/app/stacks/chat_public/response_verification.py
backend/app/stacks/chat_public/role_overlay_registry.py
backend/app/stacks/chat_public/strategy_proposal_capture.py
backend/app/stacks/chat_public/tests/test_aiq004d2_developer_debug_routing.py
backend/app/stacks/chat_public/tests/test_aiq004d3_runtime_branch_repairs.py
backend/app/stacks/chat_public/tests/test_aiq004d_generic_response_contract.py
backend/app/stacks/chat_public/tests/test_aiq005f_general_conversation_model_binding.py
backend/app/stacks/chat_public/tests/test_authenticated_role_truth_boundary.py
backend/app/stacks/chat_public/tests/test_capability_state_registry.py
backend/app/stacks/chat_public/tests/test_chat_intent_regex.py
backend/app/stacks/chat_public/tests/test_chat_timeout_configuration.py
backend/app/stacks/chat_public/tests/test_cognitive_model_profiles.py
backend/app/stacks/chat_public/tests/test_cognitive_model_router.py
backend/app/stacks/chat_public/tests/test_conversation_service_boundary.py
backend/app/stacks/chat_public/tests/test_deterministic_math_engine.py
backend/app/stacks/chat_public/tests/test_developer_context_overlay.py
backend/app/stacks/chat_public/tests/test_developer_response_builder.py
backend/app/stacks/chat_public/tests/test_live_math_runtime_integration.py
backend/app/stacks/chat_public/tests/test_live_rag_activation.py
backend/app/stacks/chat_public/tests/test_live_response_verification.py
backend/app/stacks/chat_public/tests/test_local_rag_index.py
backend/app/stacks/chat_public/tests/test_pdf_rag_ingestion.py
backend/app/stacks/chat_public/tests/test_prompt_composer.py
backend/app/stacks/chat_public/tests/test_public_chat_controls.py
backend/app/stacks/chat_public/tests/test_rag_citation_generation_contract.py
backend/app/stacks/chat_public/tests/test_response_verification.py
backend/app/stacks/chat_public/tests/test_role_overlay_injection.py
backend/app/stacks/chat_public/tests/test_role_overlay_principal_dependency.py
backend/app/stacks/chat_public/tests/test_role_overlay_registry.py
backend/app/stacks/chat_public/time_context.py
backend/app/stacks/identity_auth/authorization_policy.py
backend/app/stacks/identity_auth/route_protection.py
backend/app/stacks/identity_auth/runtime_adapter.py
backend/app/stacks/journal_ledger/strategy_decision_audit_adapter.py
backend/app/stacks/wolfden_ai/agent_router.py
backend/app/stacks/wolfden_ai/base.py
backend/app/stacks/wolfden_ai/local_model_contract.py
backend/app/stacks/wolfden_ai/memory.py
backend/app/stacks/wolfden_ai/observability_boundary.py
backend/app/stacks/wolfden_ai/portfolio_output_result_facade.py
backend/app/stacks/wolfden_ai/routing.py
backend/app/stacks/wolfden_ai/runtime.py
backend/app/stacks/wolfden_ai/tests/test_local_model_binding.py
backend/app/stacks/wolfden_ai/tests/test_observability_boundary.py
backend/app/stacks/wolfden_ai/tests/test_portfolio_output_result_facade.py

Launch Dependency

Required Before Launch

YES

Blocks

User chat

Conversation continuity

Portfolio explanations

Strategy explanations

Risk explanations

Market-data explanations

Deterministic calculations

Document retrieval

Controlled early-user launch

FINAL VERDICT

Function Exists: YES

Frontend Connected: UNVERIFIED

Backend Route Present: YES

Authentication: DETECTED

Thread Ownership: DETECTED

Intent Detection: DETECTED

Context Assembly: DETECTED

Memory: DETECTED

RAG: DETECTED

Deterministic Math: DETECTED

Model Routing: DETECTED

Ollama: DETECTED

Response Verification: DETECTED

Persistence: DETECTED

Automatic Order Submission: DETECTED — REVIEW REQUIRED

Live Execution Disabled: DETECTED

Relevant Tests: PRESENT

Live Verification: NOT COMPLETE

Launch Ready: UNVERIFIED

Overall Classification

PARTIALLY VERIFIED

Launch Classification

CRITICAL

---



---

FUNCTION PATH 12 — JOURNAL, LEDGER, AUDIT, AND EVIDENCE

Function Status

Inventory Status: INITIAL INVENTORY COMPLETE
Implementation Status: IMPLEMENTED — SOURCE VERIFICATION PENDING
Qualification Status: UNVERIFIED
Launch Importance: CRITICAL
Last Updated: 2026-07-31
Evidence Source: runtime/system_inventory/function_path_12_journal_ledger_20260731_165547/function_path_12_journal_ledger_inventory.json

Purpose

The Journal, Ledger, Audit, and Evidence function records and exposes
traceable system activity for strategy decisions, risk decisions,
paper orders, conversations, tool evidence, runtime traces, recovery,
and safety events.

Its purpose is to:

- Require authenticated access.
- Enforce user and account ownership.
- Create traceable records.
- Preserve append-only and immutable behavior where required.
- Record strategy decisions and evidence.
- Record risk decisions and rejection reasons.
- Record paper-order lifecycle evidence.
- Record chat messages, tool evidence, and verification metadata.
- Record runtime trace identifiers and observation times.
- Prevent duplicate events through idempotency controls.
- Preserve transaction integrity.
- Support reconciliation, backup, restore, and recovery.
- Prevent unauthorized update or deletion.
- Prevent sensitive credentials from entering journal records.

Primary Function Flow

Authenticated User or Internal Service
      │
      ▼
Strategy / Risk / Paper / Chat / Runtime Event
      │
      ▼
Authentication and Ownership
      │
      ▼
Event Validation
      │
      ▼
Idempotency and Replay Check
      │
      ▼
Journal / Ledger / Audit Adapter
      │
      ▼
Transaction Boundary
      │
      ├────────► Commit
      └────────► Rollback
      │
      ▼
Immutable or Append-Only Record
      │
      ▼
Evidence / History / Audit Response

Frontend Requests

No direct frontend journal or ledger request detected.

Backend Routes

GET /api/v1/graph/live
Function: get_live_graph
File: backend/app/main.py:204
Stages: authentication, backend_route, frontend_entry, idempotency, integrity, ownership, persistence, recovery, runtime_trace, serialization, strategy

GET /api/v1/dashboard/summary
Function: summary
File: backend/app/main.py:209
Stages: authentication, backend_route, frontend_entry, idempotency, integrity, ownership, persistence, recovery, runtime_trace, serialization, strategy

POST /api/v1/chat
Function: chat_endpoint
File: backend/app/stacks/chat_public/chat_api.py:39
Stages: authentication, runtime_trace, serialization

Controls and Behaviour

authentication_detected

True

authorization_detected

True

ownership_detected

True

append_only_detected

True

create_detected

True

read_detected

True

update_markers_detected

True

delete_markers_detected

True

transaction_detected

True

rollback_detected

True

integrity_hash_detected

True

sequence_detected

True

idempotency_detected

True

strategy_evidence_detected

True

risk_evidence_detected

True

paper_order_evidence_detected

True

chat_evidence_detected

True

runtime_trace_detected

True

backup_detected

True

restore_detected

True

reconciliation_detected

True

sensitive_data_controls_detected

True

rate_limit_detected

False

csrf_detected

False

Frontend States

loading_detected

True

error_detected

True

empty_detected

False

filter_detected

False

pagination_detected

False

timestamp_display_detected

True

evidence_display_detected

True

responsive_detected

True

accessibility_detected

True

Tests

backend/app/stacks/chat_public/tests/test_live_math_runtime_integration.py

test_supported_math_requests_are_extracted
test_percentage_result_is_exact
test_cagr_result_is_deterministic
test_position_size_uses_whole_units
test_unrequested_math_does_not_execute
test_ambiguous_math_fails_controlled
test_division_by_zero_returns_error_evidence
test_runtime_contains_math_integration
test_live_math_has_no_arbitrary_execution

backend/app/stacks/chat_public/tests/test_live_rag_activation.py

test_strategy_family_requests_retrieval
test_retrieval_is_not_called_when_not_requested
test_retrieval_filters_injection_chunks_and_bounds_top_k
test_prompt_contains_page_aware_citation
test_prompt_respects_total_character_boundary
test_retrieval_failure_returns_controlled_bundle
test_chat_runtime_contains_live_rag_integration
test_live_rag_module_does_not_enable_execution

backend/app/stacks/chat_public/tests/test_live_response_verification.py

test_verifier_replaces_missing_math_result
test_verifier_preserves_exact_math_result
test_verifier_replaces_live_execution_claim
test_runtime_verification_occurs_before_persistence
test_runtime_emits_verification_event
test_runtime_persists_verification_evidence
test_runtime_exposes_verification_metadata

backend/app/stacks/chat_public/tests/test_response_verification.py

test_ordinary_response_passes
test_exact_math_result_passes
test_decimal_equivalent_math_result_passes
test_missing_math_result_is_repaired
test_position_size_result_passes
test_allowed_citation_passes
test_missing_required_citation_is_repaired
test_unapproved_citation_is_repaired
test_live_execution_claim_fails_closed
test_safe_live_execution_denial_passes
test_empty_response_fails_closed
test_result_serialization_is_structured
test_verifier_has_no_external_authority

backend/app/stacks/chat_public/tests/test_role_overlay_injection.py

test_role_overlay_is_inserted_in_correct_order
test_no_overlay_path_remains_supported
test_chat_api_passes_principal_to_runtime
test_runtime_passes_overlay_and_intent_metadata
test_unknown_role_fails_closed_to_user_overlay
test_deterministic_developer_path_remains_grounded

backend/app/stacks/journal_ledger/tests/__init__.py

Journal or ledger test content detected.

backend/app/stacks/journal_ledger/tests/test_decision_audit_query_facade.py

test_get_by_event_id_delegates_only_to_service
test_get_by_idempotency_key_normalizes_key
test_latest_returns_none_without_exposing_service_record
test_list_recent_returns_immutable_tuple_of_serialized_dtos
test_serialized_dto_returns_fresh_dictionary_copy
test_mapping_proxy_record_is_serialized_without_exposure
test_list_recent_fails_closed_for_invalid_limits
test_facade_rejects_non_service_dependency
test_facade_has_exact_public_query_methods
test_dto_is_frozen

backend/app/stacks/journal_ledger/tests/test_decision_audit_query_facade_failure_behavior.py

test_service_failures_propagate_without_fallback_data
test_blank_idempotency_key_fails_before_service_call
test_non_string_idempotency_key_fails_before_service_call
test_invalid_list_limit_fails_before_service_call
test_unsupported_record_type_fails_closed
test_scalar_service_record_fails_closed
test_mapping_with_non_string_key_fails_closed
test_non_finite_float_fails_closed
test_list_recent_rejects_mapping_as_collection
test_list_recent_does_not_return_partial_collection
test_none_reads_remain_explicit_none
test_valid_result_remains_serialized_after_failure_tests

backend/app/stacks/journal_ledger/tests/test_decision_audit_service.py

test_service_exposes_append_and_read_methods_only
test_append_delegates_to_repository
test_read_methods_delegate_to_repository
test_list_recent_rejects_invalid_limits

backend/app/stacks/journal_ledger/tests/test_decision_event_contract.py

test_draft_normalizes_and_freezes_contract
test_canonical_hash_is_deterministic
test_payload_key_order_does_not_change_hash
test_naive_datetime_is_rejected
test_invalid_confidence_is_rejected
test_first_persisted_event_requires_no_previous_hash
test_non_first_event_requires_previous_hash
test_content_hash_mismatch_is_rejected
test_chain_link_requires_contiguous_sequence_and_hash

backend/app/stacks/journal_ledger/tests/test_decision_event_model.py

test_model_uses_canonical_runtime_base
test_table_name_is_canonical
test_required_constraints_and_columns_exist
test_sequence_number_is_primary_key
test_update_listener_rejects_mutation
test_delete_listener_rejects_mutation

backend/app/stacks/journal_ledger/tests/test_decision_event_repository.py

test_first_append_allocates_sequence_one
test_second_append_links_previous_hash
test_duplicate_is_rejected_before_insert
test_commit_failure_rolls_back
test_repository_exposes_no_mutation_methods
test_append_rejects_naive_recorded_at

backend/app/stacks/journal_ledger/tests/test_strategy_decision_audit_adapter.py

test_produce_and_audit_delegates_to_service
test_missing_envelope_field_fails_before_append
test_symbol_mismatch_fails_before_append
test_invalid_confidence_fails_before_append
test_naive_occurred_at_is_rejected
test_adapter_exposes_no_mutation_or_execution_methods

backend/app/stacks/portfolio/tests/test_authenticated_portfolio_read_isolation.py

test_accounting_rejects_empty_owner
test_ledger_read_rejects_empty_owner
test_position_route_is_authenticated_and_scoped
test_orders_route_is_authenticated_and_scoped
test_analytics_route_is_authenticated_and_scoped
test_accounting_is_owner_scoped
test_max_allocation_is_owner_scoped
test_risk_propagates_owner
test_execution_propagates_owner

backend/app/stacks/portfolio/tests/test_execution_ownership_propagation.py

test_paper_execution_rejects_empty_user_id
test_ledger_rejects_empty_user_id
test_all_paper_broker_save_log_calls_propagate_user_id
test_ledger_inventory_lookup_is_account_scoped
test_order_history_write_is_account_scoped

backend/app/stacks/portfolio/tests/test_ownership_schema_enforcement.py

test_orm_enforces_owned_rows
test_live_database_enforces_owned_rows

backend/app/stacks/risk/tests/test_drawdown_guard_ledger_boundary.py

test_risk_owns_no_persistence_import
test_risk_imports_no_ledger_internals
test_risk_calls_only_read_facade
test_healthcheck_preserves_none_contract
test_healthcheck_uses_scalar_facade
test_ledger_owns_read_query
test_read_facade_exposes_no_session_or_model

backend/app/stacks/wolfden_ai/tests/test_local_model_binding.py

test_request_contract_is_immutable
test_response_contract_is_immutable
test_response_contract_has_failure_status
test_valid_plain_output_is_normalized
test_valid_structured_output_is_parsed
test_invalid_output_fails_closed
test_oversized_output_fails_closed
test_dangerous_text_cannot_unlock_capability
test_approved_adapter_uses_timeout_bridge
test_internal_timeout_maps_to_rejection
test_adapter_exception_maps_to_rejection
test_non_string_adapter_output_maps_to_rejection
test_default_wrapper_preserves_core_behavior
test_model_failure_cannot_block_core
test_rejected_response_cannot_block_core
test_agent_wrapper_has_failure_guard
test_contract_owns_timeout_and_parser
test_contract_owns_no_mutation_capability

backend/app/stacks/wolfden_ai/tests/test_observability_boundary.py

test_observation_is_immutable
test_observation_is_non_persistent
test_observation_rejects_persistent_state
test_observation_rejects_mutation_request
test_payload_is_deeply_frozen
test_standard_logging_is_used
test_agent_router_uses_observability_boundary
test_boundary_owns_no_persistence_or_execution
test_journal_ledger_and_execution_are_preserved

backend/app/test/test_stage8e_runtime_instrumentation.py

test_stage8e_architecture_nodes_are_registered
test_runtime_trace_supports_stage8d_metrics
test_chat_runtime_contains_required_operational_stages
test_route_policy_emits_security_events
test_frontend_preserves_playback_and_exposes_metrics
test_global_event_bus_remains_canonical

Current Gaps

No direct frontend journal or ledger request was detected.

Update markers were detected and must be reviewed against append-only ledger requirements.

Delete markers were detected and must be reviewed against immutable audit requirements.

FUNCTION FLOW GRAPH

Authenticated User or Internal Service
      │
      ▼
Strategy / Risk / Paper / Chat / Runtime Event
      │
      ▼
Authentication
      │
      ▼
Authorization and Ownership
      │
      ▼
Event Validation
      │
      ▼
Idempotency and Replay Protection
      │
      ▼
Journal / Ledger / Audit Adapter
      │
      ▼
Transaction Boundary
      │
      ├────────► Commit
      └────────► Rollback
      │
      ▼
Append-Only Record
      │
      ├────────► Strategy Evidence
      ├────────► Risk Evidence
      ├────────► Paper-Order Evidence
      ├────────► Chat Evidence
      ├────────► Runtime Trace
      └────────► Recovery Evidence
      │
      ▼
Authorized Read / History Response

Repository Files

Frontend

frontend/app/admin/audit/page.tsx
frontend/app/page.tsx
frontend/services/chat/chatContracts.ts

Backend

backend/app/core/cognitive_graph_state.py
backend/app/main.py
backend/app/stacks/chat_public/chat_api.py
backend/app/stacks/chat_public/chat_runtime.py
backend/app/stacks/chat_public/chat_system_prompt.py
backend/app/stacks/chat_public/context/context_assembler.py
backend/app/stacks/chat_public/contracts/chat_contracts.py
backend/app/stacks/chat_public/conversation_store.py
backend/app/stacks/chat_public/developer_response_builder.py
backend/app/stacks/chat_public/persistence/chat_models.py
backend/app/stacks/chat_public/tests/test_live_math_runtime_integration.py
backend/app/stacks/chat_public/tests/test_live_rag_activation.py
backend/app/stacks/chat_public/tests/test_live_response_verification.py
backend/app/stacks/chat_public/tests/test_response_verification.py
backend/app/stacks/chat_public/tests/test_role_overlay_injection.py
backend/app/stacks/db_runtime/model_registry.py
backend/app/stacks/execution/paper_broker.py
backend/app/stacks/identity_auth/route_protection.py
backend/app/stacks/journal_ledger/__init__.py
backend/app/stacks/journal_ledger/base.py
backend/app/stacks/journal_ledger/decision_audit_query_facade.py
backend/app/stacks/journal_ledger/decision_audit_service.py
backend/app/stacks/journal_ledger/decision_event_contract.py
backend/app/stacks/journal_ledger/decision_event_model.py
backend/app/stacks/journal_ledger/decision_event_repository.py
backend/app/stacks/journal_ledger/ledger.py
backend/app/stacks/journal_ledger/record.py
backend/app/stacks/journal_ledger/strategy_decision_audit_adapter.py
backend/app/stacks/journal_ledger/tests/__init__.py
backend/app/stacks/journal_ledger/tests/test_decision_audit_query_facade.py
backend/app/stacks/journal_ledger/tests/test_decision_audit_query_facade_failure_behavior.py
backend/app/stacks/journal_ledger/tests/test_decision_audit_service.py
backend/app/stacks/journal_ledger/tests/test_decision_event_contract.py
backend/app/stacks/journal_ledger/tests/test_decision_event_model.py
backend/app/stacks/journal_ledger/tests/test_decision_event_repository.py
backend/app/stacks/journal_ledger/tests/test_strategy_decision_audit_adapter.py
backend/app/stacks/learning_research/research_loader.py
backend/app/stacks/market_data/yfinance_ingestor.py
backend/app/stacks/portfolio/accounting.py
backend/app/stacks/portfolio/reconciliation.py
backend/app/stacks/portfolio/tests/test_authenticated_portfolio_read_isolation.py
backend/app/stacks/portfolio/tests/test_execution_ownership_propagation.py
backend/app/stacks/portfolio/tests/test_ownership_schema_enforcement.py
backend/app/stacks/risk/drawdown_guard.py
backend/app/stacks/risk/tests/test_drawdown_guard_ledger_boundary.py
backend/app/stacks/wolfden_ai/tests/test_local_model_binding.py
backend/app/stacks/wolfden_ai/tests/test_observability_boundary.py
backend/app/test/test_stage8e_runtime_instrumentation.py

Launch Dependency

Required Before Launch

YES

Blocks

Paper-order auditability

Strategy-decision auditability

Risk-decision auditability

Chat evidence traceability

Runtime recovery

Backup and restore verification

Security investigations

Controlled early-user launch

FINAL VERDICT

Function Exists: YES

Frontend Surface: DETECTED

Backend Routes: DETECTED

Authentication: DETECTED

Ownership: DETECTED

Append-Only Controls: DETECTED

Transaction Controls: DETECTED

Rollback: DETECTED

Integrity Hash or Chain: DETECTED

Idempotency: DETECTED

Strategy Evidence: DETECTED

Risk Evidence: DETECTED

Paper-Order Evidence: DETECTED

Chat Evidence: DETECTED

Runtime Traces: DETECTED

Relevant Tests: PRESENT

Live Verification: NOT COMPLETE

Launch Ready: UNVERIFIED

Overall Classification

PARTIALLY VERIFIED

Launch Classification

CRITICAL

---



---

FUNCTION PATH 13 — NOTIFICATIONS, ALERTS, AND USER MESSAGING

Function Status

Inventory Status: INITIAL INVENTORY COMPLETE
Implementation Status: IMPLEMENTED — SOURCE VERIFICATION PENDING
Qualification Status: UNVERIFIED
Launch Importance: HIGH
Last Updated: 2026-07-31
Evidence Source: runtime/system_inventory/function_path_13_notifications_20260731_170712/function_path_13_notifications_inventory.json

Purpose

The Notifications, Alerts, and User Messaging function creates,
routes, stores, displays, acknowledges, retries, and protects
user-facing and system-generated messages.

Its purpose is to:

- Require authenticated access.
- Enforce recipient ownership.
- Create notifications from approved system events.
- Display unread and historical notifications.
- Support mark-read or acknowledgement state.
- Support dismissal or archival where allowed.
- Preserve severity, category, timestamps, and delivery evidence.
- Enforce user notification preferences.
- Retry failed external deliveries safely.
- Deduplicate repeated events.
- Deliver security warnings.
- Deliver strategy and risk alerts.
- Deliver paper-order lifecycle alerts.
- Deliver system-health and administrative notices.
- Prevent sensitive credentials from entering notification content.

Primary Function Flow

Strategy / Risk / Paper / Security / Runtime / Admin Event
      │
      ▼
Notification Event Validation
      │
      ▼
Recipient Ownership and Preferences
      │
      ▼
Idempotency and Deduplication
      │
      ▼
Notification Service
      │
      ├────────► In-App Notification
      ├────────► Email
      ├────────► SMS
      ├────────► Push
      └────────► Webhook
      │
      ▼
Delivery State and Evidence
      │
      ├────────► Delivered
      ├────────► Failed
      ├────────► Retry
      └────────► Dead Letter
      │
      ▼
Frontend Notification Surface
      │
      ├────────► Unread
      ├────────► Read
      ├────────► Acknowledged
      └────────► Dismissed

Frontend Requests

No direct frontend notification request detected.

Backend Routes

No decorated notification backend route detected.

Controls and Behaviour

authentication_detected

True

authorization_detected

True

ownership_detected

True

creation_detected

False

read_detected

False

mark_read_detected

False

dismiss_detected

False

preference_controls_detected

False

severity_detected

True

category_detected

True

delivery_status_detected

False

retry_detected

False

idempotency_detected

True

security_alerts_detected

False

strategy_alerts_detected

True

risk_alerts_detected

True

paper_order_alerts_detected

True

system_health_alerts_detected

True

admin_broadcast_detected

False

email_provider_detected

False

sms_provider_detected

False

push_provider_detected

False

webhook_delivery_detected

False

transaction_detected

False

rollback_detected

False

sensitive_data_controls_detected

True

rate_limit_detected

True

csrf_detected

True

Frontend States

loading_detected

True

error_detected

True

empty_detected

True

unread_detected

False

mark_read_detected

False

dismiss_detected

True

filter_detected

True

pagination_detected

True

timestamp_display_detected

True

severity_display_detected

True

toast_detected

False

banner_detected

True

responsive_detected

True

accessibility_detected

True

Tests

backend/app/stacks/chat_public/tests/test_authenticated_role_truth_boundary.py

test_system_prompt_rejects_conversational_role_elevation
test_user_overlay_remains_user_despite_developer_claim
test_developer_overlay_requires_server_supplied_developer_role
test_local_evidence_requires_explicit_server_permission
test_authenticated_developer_wording_triggers_developer_intent
test_user_wording_alone_does_not_grant_local_evidence
test_authenticated_developer_permission_uses_local_evidence

backend/app/stacks/chat_public/tests/test_prompt_composer.py

test_composer_preserves_existing_section_delimiter
test_composer_uses_supplied_existing_bounder
test_composer_reports_character_metadata
test_composer_materializes_iterables_once
test_composer_rejects_invalid_limit
test_composer_rejects_non_string_bounder_result
test_prompt_composition_is_immutable

backend/app/test/test_stage8e_runtime_instrumentation.py

test_stage8e_architecture_nodes_are_registered
test_runtime_trace_supports_stage8d_metrics
test_chat_runtime_contains_required_operational_stages
test_route_policy_emits_security_events
test_frontend_preserves_playback_and_exposes_metrics
test_global_event_bus_remains_canonical

Current Gaps

No direct frontend notification request was detected.

No decorated notification or alert backend route was mapped.

Notification creation or emission was not detected.

Notification read or list behavior was not detected.

Mark-read or acknowledgement behavior was not detected.

Delivery status or delivery evidence was not detected.

FUNCTION FLOW GRAPH

Strategy / Risk / Paper / Security / Runtime / Admin Event
      │
      ▼
Notification Event Validation
      │
      ▼
Authentication and Authorization
      │
      ▼
Recipient Ownership
      │
      ▼
User Preferences
      │
      ▼
Idempotency and Deduplication
      │
      ▼
Notification Service
      │
      ├────────► In-App
      ├────────► Email
      ├────────► SMS
      ├────────► Push
      └────────► Webhook
      │
      ▼
Delivery Tracking
      │
      ├────────► Delivered
      ├────────► Failed
      ├────────► Retry
      └────────► Dead Letter
      │
      ▼
Notification Persistence
      │
      ▼
Frontend Notification Surface
      │
      ├────────► Unread
      ├────────► Read
      ├────────► Acknowledged
      └────────► Dismissed

Repository Files

Frontend

frontend/app/change-password/page.tsx
frontend/app/login/page.tsx
frontend/app/register/page.tsx
frontend/app/user/dashboard/page.tsx
frontend/app/user/settings/page.tsx
frontend/components/RoleAwareWorkspaceNav.tsx
frontend/components/ui/StatusMessage.tsx
frontend/services/chat/chatContracts.ts

Backend

backend/app/stacks/chat_public/chat_runtime.py
backend/app/stacks/chat_public/chat_system_prompt.py
backend/app/stacks/chat_public/context/context_assembler.py
backend/app/stacks/chat_public/contracts/chat_contracts.py
backend/app/stacks/chat_public/strategy_proposal_capture.py
backend/app/stacks/chat_public/tests/test_authenticated_role_truth_boundary.py
backend/app/stacks/chat_public/tests/test_prompt_composer.py
backend/app/stacks/notification/__init__.py
backend/app/stacks/notification/base.py
backend/app/stacks/wolfden_ai/agent_router.py
backend/app/test/test_stage8e_runtime_instrumentation.py

Launch Dependency

Required Before Launch

YES

Blocks

Security warnings

Risk alerts

Emergency-stop notices

Paper-order lifecycle visibility

System degradation notices

Administrative user messaging

Controlled early-user launch

FINAL VERDICT

Function Exists: YES

Frontend Surface: DETECTED

Frontend Requests: UNVERIFIED

Backend Routes: UNVERIFIED

Authentication: DETECTED

Ownership: DETECTED

Creation: UNVERIFIED

Read/List: UNVERIFIED

Mark Read: UNVERIFIED

Dismissal: UNVERIFIED

Preferences: UNVERIFIED

Delivery Tracking: UNVERIFIED

Retry: UNVERIFIED

Idempotency: DETECTED

Security Alerts: UNVERIFIED

Strategy Alerts: DETECTED

Risk Alerts: DETECTED

Paper-Order Alerts: DETECTED

System-Health Alerts: DETECTED

Relevant Tests: PRESENT

Live Verification: NOT COMPLETE

Launch Ready: UNVERIFIED

Overall Classification

PARTIALLY VERIFIED

Launch Classification

HIGH

---



---

FUNCTION PATH 14 — ADMIN CONTROL PANEL AND USER MANAGEMENT

Function Status

Inventory Status: INITIAL INVENTORY COMPLETE
Implementation Status: IMPLEMENTED — SOURCE VERIFICATION PENDING
Qualification Status: UNVERIFIED
Launch Importance: CRITICAL
Last Updated: 2026-07-31
Evidence Source: runtime/system_inventory/function_path_14_admin_control_20260731_171125/function_path_14_admin_control_inventory.json

Purpose

The Admin Control Panel and User Management function allows
authorized administrators to inspect users, manage approved account
states, manage roles and sessions, inspect audit evidence, and access
restricted system controls.

Its purpose is to:

- Require an authenticated administrator.
- Reject standard-user and unauthorized developer access.
- Display paginated and searchable user records.
- Display user roles and account status.
- Inspect individual user details.
- Change roles through controlled authorization.
- Disable, suspend, enable, or unlock accounts where permitted.
- Revoke one or all user sessions.
- Protect administrators from accidental self-lockout.
- Protect the final administrator account.
- Require confirmation and administrative reasons for mutations.
- Record actor, target, reason, time, and trace evidence.
- Protect password hashes, tokens, and credentials.
- Apply CSRF and rate-limit controls.
- Prevent uncontrolled deletion of user records.

Primary Function Flow

Authenticated Administrator
      │
      ▼
Protected Admin Page
      │
      ▼
Frontend Middleware
      │
      ▼
Administrator Role Validation
      │
      ▼
Admin API Request
      │
      ▼
Backend Authentication
      │
      ▼
Administrator Authorization
      │
      ▼
Target User Validation
      │
      ├────────► List Users
      ├────────► View User
      ├────────► Change Role
      ├────────► Disable or Enable
      ├────────► Revoke Sessions
      └────────► Inspect Audit Evidence
      │
      ▼
Transaction and Audit Record
      │
      ├────────► Commit
      └────────► Rollback
      │
      ▼
Updated Admin Interface

Admin Pages

frontend/app/admin/audit/page.tsx
frontend/app/admin/page.tsx
frontend/app/admin/sessions/page.tsx
frontend/app/admin/tickets/page.tsx
frontend/app/admin/user-dashboard/page.tsx
frontend/app/admin/user-stats/page.tsx
frontend/app/admin/users/page.tsx

Frontend Requests

GET "/api/admin/users"
Source: frontend/app/admin/users/page.tsx:369
Credentials: same-origin

GET `/api/admin/users/${
            encodeURIComponent(
              user.user_id,
            )
          }`
Source: frontend/app/admin/users/page.tsx:475
Credentials: same-origin

Backend Routes

POST /api/v1/sandbox/signal
Function: set_sandbox_override
File: backend/app/main.py:399
Stages: audit, authentication, authorization, frontend_entry, frontend_request, ownership, persistence, serialization, system_controls, user_status

POST /api/v1/sandbox/audit
Function: trigger_sandbox_audit
File: backend/app/main.py:420
Stages: audit, authentication, authorization, frontend_entry, frontend_request, ownership, persistence, serialization, system_controls, user_status

POST /api/v1/admin/backup
Function: force_system_backup
File: backend/app/main.py:435
Stages: audit, authentication, authorization, frontend_entry, frontend_request, ownership, persistence, serialization, system_controls, user_status

GET /api/v1/portfolio/valuation
Function: get_authenticated_portfolio_valuation
File: backend/app/main.py:462
Stages: audit, authentication, authorization, frontend_entry, frontend_request, ownership, persistence, serialization, system_controls, user_status

POST /{user_id}/require-password-reset
Function: require_password_reset
File: backend/app/stacks/identity_auth/admin_mutation_router.py:30
Stages: authentication, authorization, frontend_entry, frontend_request, ownership, password_security, serialization

POST /{user_id}/temporary-password
Function: issue_temporary_password
File: backend/app/stacks/identity_auth/admin_mutation_router.py:49
Stages: authentication, authorization, frontend_entry, frontend_request, ownership, password_security, serialization

POST /{user_id}/disable
Function: disable_account
File: backend/app/stacks/identity_auth/admin_mutation_router.py:70
Stages: authentication, authorization, frontend_entry, frontend_request, ownership, password_security, serialization

POST /{user_id}/enable
Function: enable_account
File: backend/app/stacks/identity_auth/admin_mutation_router.py:89
Stages: authentication, authorization, ownership, password_security, serialization

DELETE /{user_id}
Function: delete_account
File: backend/app/stacks/identity_auth/admin_mutation_router.py:108
Stages: authentication, authorization, ownership, serialization

GET /introspection
Function: administrative_introspection
File: backend/app/stacks/identity_auth/admin_read_router.py:43
Stages: authentication, authorization, frontend_entry, frontend_request, ownership, serialization, user_detail, user_listing

GET /users
Function: list_administrative_users
File: backend/app/stacks/identity_auth/admin_read_router.py:66
Stages: authentication, authorization, frontend_entry, frontend_request, ownership, serialization, user_detail, user_listing

GET /users/{user_id}
Function: get_administrative_user
File: backend/app/stacks/identity_auth/admin_read_router.py:95
Stages: authentication, authorization, frontend_request, ownership, serialization, user_detail, user_listing

GET /sessions
Function: list_administrative_sessions
File: backend/app/stacks/identity_auth/admin_read_router.py:125
Stages: authentication, authorization, frontend_request, ownership, serialization, user_detail, user_listing

GET /sessions/{session_id}
Function: get_administrative_session
File: backend/app/stacks/identity_auth/admin_read_router.py:170
Stages: authentication, authorization, frontend_request, ownership, serialization, user_detail

GET /access-token-revocations
Function: list_access_token_revocations
File: backend/app/stacks/identity_auth/admin_read_router.py:200
Stages: authentication, authorization, frontend_request, ownership, serialization

GET /access-token-revocations/{revocation_id}
Function: get_access_token_revocation
File: backend/app/stacks/identity_auth/admin_read_router.py:240
Stages: authentication, authorization, ownership, serialization

POST /register
Function: register_identity
File: backend/app/stacks/identity_auth/api_router.py:112
Stages: authentication, ownership, password_security, persistence, serialization, session_management

POST /change-required-password
Function: change_required_password
File: backend/app/stacks/identity_auth/api_router.py:235
Stages: authentication, ownership, password_security, serialization, session_management

POST /refresh
Function: refresh_session
File: backend/app/stacks/identity_auth/api_router.py:282
Stages: authentication, ownership, persistence, serialization, session_management

POST /logout
Function: logout_session
File: backend/app/stacks/identity_auth/api_router.py:351
Stages: authentication, ownership, persistence, serialization, session_management

POST /logout-all
Function: logout_all_sessions
File: backend/app/stacks/identity_auth/api_router.py:428
Stages: authentication, ownership, persistence, serialization, session_management

GET /introspection
Function: session_introspection
File: backend/app/stacks/identity_auth/api_router.py:487
Stages: authentication, ownership, persistence, serialization, session_management

GET /api/v1/analytics
Function: analytics
File: backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py:24
Stages: authentication, authorization, frontend_entry, frontend_request, ownership, password_security, serialization, session_management, user_status

POST /api/v1/admin/backup
Function: admin_backup
File: backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py:32
Stages: authentication, authorization, frontend_entry, frontend_request, ownership, password_security, serialization, session_management, user_status

GET /api/v1/market-data/status
Function: market_status
File: backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py:40
Stages: authentication, authorization, frontend_entry, frontend_request, ownership, password_security, serialization, session_management, user_status

Controls and Behaviour

authentication_detected

True

admin_authorization_detected

True

role_policy_detected

True

user_listing_detected

True

user_detail_detected

True

role_change_detected

False

disable_user_detected

True

enable_user_detected

True

session_revocation_detected

True

self_protection_detected

False

last_admin_protection_detected

False

audit_evidence_detected

True

mutation_reason_detected

True

transaction_detected

True

rollback_detected

True

csrf_detected

True

rate_limit_detected

False

sensitive_data_controls_detected

True

delete_user_markers_detected

True

operating_mode_controls_detected

True

Frontend States

loading_detected

True

error_detected

True

empty_detected

True

search_detected

True

pagination_detected

True

role_display_detected

True

user_status_display_detected

True

confirmation_dialog_detected

True

reason_input_detected

False

success_state_detected

True

responsive_detected

True

accessibility_detected

True

Tests

backend/app/stacks/chat_public/tests/test_role_overlay_registry.py

test_every_canonical_role_has_an_overlay
test_every_subscription_tier_has_an_overlay
test_role_aliases_use_canonical_roles
test_unknown_role_fails_closed_to_user
test_tier_normalization_uses_canonical_enum
test_unknown_tier_does_not_invent_entitlement
test_principal_claims_resolve_role_and_tier
test_missing_claims_fail_closed_to_user
test_overlay_is_conversational_not_authoritative
test_overlay_models_are_immutable
test_role_overlay_registry_is_immutable
test_admin_does_not_receive_repository_context
test_owner_alias_resolves_to_developer_not_new_role

backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py

test_route_policy_inventory
test_public_route_requires_no_token
test_authenticated_route_rejects_missing_token
test_authenticated_route_accepts_principal
test_admin_route_rejects_non_admin
test_admin_route_accepts_server_claim
test_unknown_route_preserves_not_found
test_refresh_token_validation_failure_is_unauthorized

backend/app/stacks/identity_auth/tests/test_canonical_router_inclusion.py

test_canonical_source_includes_auth_router_once
test_auth_router_has_complete_session_lifecycle
test_controlled_local_registration_and_login

backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py

test_lifecycle_route_policy_inventory
test_refresh_returns_rotated_pair
test_logout_revokes_current_refresh_session
test_refresh_rejection_is_unauthorized
test_logout_rejection_is_unauthorized
test_logout_all_uses_access_principal_subject
test_logout_all_rejects_missing_access_token
test_refresh_request_forbids_extra_fields
test_logout_request_forbids_extra_fields

backend/app/stacks/identity_auth/tests/test_stage5b_c_revocation_observability_cleanup.py

test_revocation_routes_are_get_only
test_revocation_summary_exposes_no_jti
test_cleanup_service_commits_success
test_cleanup_service_rolls_back_failure

backend/app/stacks/identity_auth/tests/test_stage9d_a_identity_schema.py

test_identity_model_declares_stage9d_a_fields
test_identity_role_contract_is_canonical
test_identity_role_contract_rejects_unknown_roles
test_identity_model_has_role_check_constraint
test_stage9d_a_migration_is_versioned_and_idempotent

backend/app/stacks/identity_auth/tests/test_stage9d_c2_admin_read_models.py

test_user_models_expose_no_secrets
test_session_models_expose_no_secrets
test_admin_routes_are_get_only
test_admin_dependency_is_database_authoritative
test_read_service_does_not_serialize_secret_fields
test_openapi_contains_only_expected_admin_methods
test_no_password_reset_route_added_in_c2

backend/app/stacks/identity_auth/tests/test_stage9d_c5_b_admin_user_mutations.py

test_admin_mutation_routes_are_exact
test_temporary_password_policy
test_protected_roles_denied
test_self_mutation_denied

backend/app/stacks/identity_auth/tests/test_stage9d_c5_i_authorization_policy.py

test_canonical_roles
test_subscription_tiers_remain_separate
test_owner_normalizes_to_developer
test_administrative_roles
test_unknown_roles_fail_closed
test_admin_user_management_permissions
test_developer_inherits_admin_permissions
test_dangerous_permissions_remain_separate
test_authorization_decisions_fail_closed

frontend/tests/e2e/02-auth-boundary.spec.ts

login page loads with usable form controls
unauthenticated dashboard access is blocked
unauthenticated admin access is blocked

Current Gaps

User-deletion markers were detected and require direct review.

FUNCTION FLOW GRAPH

Authenticated Administrator
      │
      ▼
Admin Frontend Page
      │
      ▼
Frontend Middleware
      │
      ▼
Administrator Role Check
      │
      ▼
Admin API
      │
      ▼
Authentication and Authorization
      │
      ▼
Target User Validation
      │
      ├────────► User List
      ├────────► User Detail
      ├────────► Role Management
      ├────────► Account Status
      ├────────► Session Revocation
      └────────► Audit Evidence
      │
      ▼
Confirmation and Reason
      │
      ▼
Transaction Boundary
      │
      ├────────► Rollback
      └────────► Commit
      │
      ▼
Administrative Audit Record
      │
      ▼
Updated Frontend State

Repository Files

Frontend

frontend/app/admin/audit/page.tsx
frontend/app/admin/layout.tsx
frontend/app/admin/page.tsx
frontend/app/admin/sessions/page.tsx
frontend/app/admin/tickets/page.tsx
frontend/app/admin/user-dashboard/page.tsx
frontend/app/admin/user-stats/page.tsx
frontend/app/admin/users/page.tsx
frontend/app/api/admin/users/[userId]/disable/route.ts
frontend/app/api/admin/users/[userId]/enable/route.ts
frontend/app/api/admin/users/[userId]/require-password-reset/route.ts
frontend/app/api/admin/users/[userId]/route.ts
frontend/app/api/admin/users/[userId]/temporary-password/route.ts
frontend/app/api/admin/users/_proxy.ts
frontend/app/api/admin/users/route.ts
frontend/app/api/auth/login/route.ts
frontend/app/login/page.tsx
frontend/components/RoleAwareWorkspaceNav.tsx
frontend/next.config.ts
frontend/proxy.ts
frontend/tests/e2e/02-auth-boundary.spec.ts

Backend

backend/app/core/cognitive_graph_state.py
backend/app/main.py
backend/app/stacks/chat_public/chat_system_prompt.py
backend/app/stacks/chat_public/role_overlay_registry.py
backend/app/stacks/chat_public/tests/test_role_overlay_registry.py
backend/app/stacks/identity_auth/admin_mutation_api_models.py
backend/app/stacks/identity_auth/admin_mutation_dependencies.py
backend/app/stacks/identity_auth/admin_mutation_router.py
backend/app/stacks/identity_auth/admin_mutation_service.py
backend/app/stacks/identity_auth/admin_read_api_models.py
backend/app/stacks/identity_auth/admin_read_dependencies.py
backend/app/stacks/identity_auth/admin_read_models.py
backend/app/stacks/identity_auth/admin_read_router.py
backend/app/stacks/identity_auth/api_router.py
backend/app/stacks/identity_auth/authorization_policy.py
backend/app/stacks/identity_auth/route_protection.py
backend/app/stacks/identity_auth/session_introspection.py
backend/app/stacks/identity_auth/session_lifecycle_service.py
backend/app/stacks/identity_auth/tests/test_bulk_route_protection.py
backend/app/stacks/identity_auth/tests/test_canonical_router_inclusion.py
backend/app/stacks/identity_auth/tests/test_session_lifecycle_api.py
backend/app/stacks/identity_auth/tests/test_stage5b_c_revocation_observability_cleanup.py
backend/app/stacks/identity_auth/tests/test_stage9d_a_identity_schema.py
backend/app/stacks/identity_auth/tests/test_stage9d_c2_admin_read_models.py
backend/app/stacks/identity_auth/tests/test_stage9d_c5_b_admin_user_mutations.py
backend/app/stacks/identity_auth/tests/test_stage9d_c5_i_authorization_policy.py

Launch Dependency

Required Before Launch

YES

Blocks

Administrator access

User account management

Role management

Session revocation

Security response

Administrative auditability

Controlled early-user launch

FINAL VERDICT

Function Exists: YES

Admin Pages: DETECTED

Frontend Requests: DETECTED

Backend Routes: DETECTED

Authentication: DETECTED

Admin Authorization: DETECTED

Role Policy: DETECTED

User Listing: DETECTED

Role Changes: UNVERIFIED

Account Disable: DETECTED

Account Enable: DETECTED

Session Revocation: DETECTED

Self-Protection: UNVERIFIED

Final-Admin Protection: UNVERIFIED

Audit Evidence: DETECTED

CSRF: DETECTED

Rate Limiting: UNVERIFIED

Relevant Tests: PRESENT

Live Verification: NOT COMPLETE

Launch Ready: UNVERIFIED

Overall Classification

PARTIALLY VERIFIED

Launch Classification

CRITICAL

---



---

FUNCTION PATH 15 — SYSTEM HEALTH, RUNTIME STATUS, AND OBSERVABILITY

Function Status

Inventory Status: INITIAL INVENTORY COMPLETE
Implementation Status: IMPLEMENTED — SOURCE VERIFICATION PENDING
Qualification Status: UNVERIFIED
Launch Importance: CRITICAL
Last Updated: 2026-07-31
Evidence Source: runtime/system_inventory/function_path_15_system_health_20260731_172244/function_path_15_system_health_inventory.json

Purpose

The System Health, Runtime Status, and Observability function
reports whether NeuroVest and its required dependencies are alive,
ready, degraded, unavailable, or operating under a restricted mode.

Its purpose is to:

- Report frontend and backend service health.
- Distinguish liveness from readiness.
- Verify database availability.
- Verify Ollama and model availability.
- Verify market-data provider health.
- Verify broker-integration health without enabling execution.
- Verify workers, queues, and background jobs.
- Expose runtime graph and dependency state.
- Record latency, metrics, logs, and trace identifiers.
- Display healthy, degraded, unavailable, and unknown states.
- Preserve safe operating-mode and emergency-stop context.
- Produce controlled alerts for outages and degradation.
- Prevent secrets and credentials from entering diagnostics.

Primary Function Flow

Authorized User or Monitoring Process
      │
      ▼
System Health Interface
      │
      ▼
Health / Readiness / Status Request
      │
      ▼
Backend Health Aggregator
      │
      ├────────► Backend Process
      ├────────► Database
      ├────────► Ollama
      ├────────► Market Data
      ├────────► Broker Adapter
      ├────────► Workers and Queues
      └────────► Runtime Graph
      │
      ▼
Dependency Results
      │
      ├────────► Healthy
      ├────────► Degraded
      ├────────► Unavailable
      └────────► Unknown
      │
      ▼
Metrics, Logging, and Runtime Trace
      │
      ▼
Frontend Status Display

Health Pages

frontend/app/admin/tickets/page.tsx
frontend/app/admin/users/page.tsx
frontend/app/dashboard/page.tsx
frontend/app/user/dashboard/page.tsx

Frontend Requests

GET `/api/admin/users/${
            encodeURIComponent(
              user.user_id,
            )
          }`
Source: frontend/app/admin/users/page.tsx:475
Credentials: same-origin

GET "/api/auth/session"
Source: frontend/app/user/dashboard/page.tsx:232
Credentials: include

GET OR DYNAMIC "/api/v1/graph/live"
Source: frontend/services/backendHealthService.ts:14
Credentials: UNKNOWN

GET OR DYNAMIC "/api/v1/graph/live"
Source: frontend/services/graphService.ts:272
Credentials: UNKNOWN

Backend Routes

GET /api/v1/graph/live
Function: get_live_graph
File: backend/app/main.py:204
Stages: authentication, backend_route, backend_service, broker, degradation, frontend_entry, frontend_request, frontend_service, operating_mode, runtime_graph, serialization, tracing

GET /api/v1/dashboard/summary
Function: summary
File: backend/app/main.py:209
Stages: authentication, backend_route, backend_service, broker, degradation, frontend_entry, frontend_request, frontend_service, operating_mode, runtime_graph, serialization, tracing

POST /api/v1/sandbox/signal
Function: set_sandbox_override
File: backend/app/main.py:399
Stages: authentication, backend_route, backend_service, broker, frontend_entry, metrics, operating_mode, serialization, tracing

POST /api/v1/sandbox/audit
Function: trigger_sandbox_audit
File: backend/app/main.py:420
Stages: authentication, backend_route, backend_service, frontend_entry, metrics, operating_mode, serialization, tracing

POST /api/v1/admin/backup
Function: force_system_backup
File: backend/app/main.py:435
Stages: authentication, backend_route, backend_service, frontend_entry, metrics, operating_mode, serialization, tracing

GET /api/v1/portfolio/valuation
Function: get_authenticated_portfolio_valuation
File: backend/app/main.py:462
Stages: authentication, backend_route, backend_service, frontend_entry, metrics, operating_mode, serialization, tracing

GET /api/v1/orders
Function: get_orders
File: backend/app/main.py:563
Stages: authentication, backend_route, backend_service, degradation, frontend_entry, frontend_request, market_data, operating_mode, serialization, tracing

GET /api/v1/analytics
Function: get_analytics
File: backend/app/main.py:595
Stages: authentication, backend_route, backend_service, degradation, frontend_entry, frontend_request, market_data, operating_mode, serialization, tracing

POST /api/v1/paper/orders
Function: submit_authenticated_paper_order
File: backend/app/main.py:647
Stages: authentication, backend_route, backend_service, degradation, frontend_entry, frontend_request, market_data, operating_mode, serialization, tracing

GET /api/v1/market/live-price/{symbol}
Function: api_live_market_price
File: backend/app/main.py:706
Stages: authentication, backend_route, backend_service, degradation, frontend_entry, frontend_request, market_data, serialization, tracing

GET /api/v1/portfolio/positions
Function: api_portfolio_positions
File: backend/app/main.py:711
Stages: authentication, backend_route, backend_service, degradation, frontend_entry, frontend_request, market_data, serialization, tracing

GET /api/v1/strategy/decision/{symbol}
Function: api_strategy_decision
File: backend/app/main.py:722
Stages: authentication, backend_route, backend_service, degradation, frontend_entry, frontend_request, market_data, serialization, tracing

GET /api/v1/risk/gate/{symbol}
Function: api_risk_gate
File: backend/app/main.py:727
Stages: authentication, backend_route, backend_service, degradation, frontend_entry, frontend_request, market_data, serialization, tracing

GET /api/v1/portfolio/readonly
Function: authenticated_owned_portfolio_overview
File: backend/app/main.py:796
Stages: authentication, backend_route, backend_service, degradation, frontend_entry, serialization

GET /api/v1/portfolio/readonly/accounts
Function: authenticated_owned_portfolio_accounts
File: backend/app/main.py:819
Stages: authentication, backend_route, backend_service, degradation, frontend_entry, serialization

GET /api/v1/portfolio/readonly/balances
Function: authenticated_owned_portfolio_balances
File: backend/app/main.py:839
Stages: authentication, backend_route, backend_service, degradation, frontend_entry, serialization

POST /api/v1/chat
Function: chat_endpoint
File: backend/app/stacks/chat_public/chat_api.py:39
Stages: authentication, backend_route, backend_service, frontend_entry, readiness, serialization, tracing

GET /status
Function: market_data_status
File: backend/app/stacks/market_data/api_router.py:102
Stages: backend_route, broker, degradation, frontend_entry, frontend_request, market_data, readiness, serialization

GET /quote/{symbol}
Function: market_data_quote
File: backend/app/stacks/market_data/api_router.py:168
Stages: backend_route, broker, degradation, frontend_entry, market_data, serialization

GET /historical/{symbol}
Function: market_data_historical
File: backend/app/stacks/market_data/api_router.py:203
Stages: backend_route, broker, degradation, frontend_entry, market_data, serialization

Controls and Behaviour

authentication_detected

True

admin_authorization_detected

True

liveness_detected

False

readiness_detected

True

database_health_detected

True

ollama_health_detected

True

frontend_health_detected

True

backend_health_detected

True

market_data_health_detected

True

broker_health_detected

True

worker_health_detected

False

runtime_graph_detected

True

metrics_detected

True

latency_detected

True

structured_logging_detected

True

runtime_trace_detected

True

degraded_state_detected

True

unavailable_state_detected

True

operating_mode_detected

True

alert_integration_detected

True

sensitive_data_controls_detected

True

rate_limit_detected

True

Frontend States

loading_detected

True

error_detected

True

healthy_state_detected

True

degraded_state_detected

False

unavailable_state_detected

True

unknown_state_detected

True

refresh_detected

True

auto_refresh_detected

True

timestamp_display_detected

True

latency_display_detected

True

dependency_display_detected

True

responsive_detected

True

accessibility_detected

True

Tests

backend/app/stacks/chat_public/tests/test_capability_state_registry.py

test_registry_is_read_only_and_complete
test_registry_uses_declared_state_categories
test_drawdown_guard_is_not_called_without_balance
test_registry_summary_is_grounded_in_rows
test_developer_response_contains_capability_state
test_developer_capabilities_remain_grounded
test_unverified_adapter_and_async_states_require_attention

backend/app/stacks/chat_public/tests/test_live_rag_activation.py

test_strategy_family_requests_retrieval
test_retrieval_is_not_called_when_not_requested
test_retrieval_filters_injection_chunks_and_bounds_top_k
test_prompt_contains_page_aware_citation
test_prompt_respects_total_character_boundary
test_retrieval_failure_returns_controlled_bundle
test_chat_runtime_contains_live_rag_integration
test_live_rag_module_does_not_enable_execution

backend/app/stacks/chat_public/tests/test_public_chat_controls.py

test_public_chat_contract_accepts_valid_text
test_public_chat_contract_rejects_empty_text
test_public_chat_contract_rejects_oversized_text
test_public_chat_safety_denies_restricted_action
test_public_chat_safety_allows_general_discussion
test_public_chat_timeout_maps_to_504
test_public_chat_dependency_failure_maps_to_503
test_public_chat_rate_limit_maps_to_429
test_public_chat_safety_denial_maps_to_403
test_route_is_decorated_with_public_controls
test_public_control_wrapper_preserves_signature
test_payload_boundary_ignores_injected_dependencies
test_payload_boundary_rejects_oversized_payload
test_payload_boundary_rejects_empty_payload
test_payload_boundary_safety_uses_only_payload
test_payload_boundary_still_rejects_restricted_payload
test_missing_payload_argument_fails_closed
test_configured_payload_wrapper_preserves_signature
test_chat_route_configures_payload_argument

backend/app/stacks/identity_auth/tests/test_login_service.py

test_valid_login_issues_separate_tokens_and_session
test_unknown_user_and_wrong_password_share_error
test_disabled_account_fails_closed
test_inactive_status_fails_closed
test_refresh_session_failure_rolls_back
test_identical_tokens_fail_closed

backend/app/stacks/identity_auth/tests/test_stage5b_c_revocation_observability_cleanup.py

test_revocation_routes_are_get_only
test_revocation_summary_exposes_no_jti
test_cleanup_service_commits_success
test_cleanup_service_rolls_back_failure

backend/app/stacks/journal_ledger/tests/test_decision_audit_query_facade_failure_behavior.py

test_service_failures_propagate_without_fallback_data
test_blank_idempotency_key_fails_before_service_call
test_non_string_idempotency_key_fails_before_service_call
test_invalid_list_limit_fails_before_service_call
test_unsupported_record_type_fails_closed
test_scalar_service_record_fails_closed
test_mapping_with_non_string_key_fails_closed
test_non_finite_float_fails_closed
test_list_recent_rejects_mapping_as_collection
test_list_recent_does_not_return_partial_collection
test_none_reads_remain_explicit_none
test_valid_result_remains_serialized_after_failure_tests

backend/app/stacks/market_data/tests/test_provider_contract.py

test_symbol_normalization
test_empty_symbol_rejected
test_quote_normalizes_fields
test_naive_quote_timestamp_rejected
test_invalid_ohlc_rejected
test_request_date_order_enforced
test_result_requires_matching_symbol
test_fixture_satisfies_protocol
test_fixture_returns_canonical_quote
test_fixture_returns_canonical_bars

backend/app/stacks/market_data/tests/test_provider_runtime.py

test_registry_registers_and_selects_by_priority
test_registry_rejects_duplicate_name
test_registry_ignores_disabled_provider
test_cache_returns_unexpired_value
test_cache_expires_value
test_cache_evicts_least_recently_used
test_market_session_classification
test_market_session_rejects_naive_datetime
test_router_uses_highest_priority_provider
test_router_falls_back_after_provider_failure
test_router_fails_closed_when_all_providers_fail
test_router_quote_cache_prevents_second_provider_call
test_router_returns_canonical_historical_result

backend/app/stacks/market_data/tests/test_runtime_composition.py

test_production_runtime_constructs_without_network
test_runtime_components_are_shared
test_read_only_routes_are_declared
test_status_endpoint_is_network_free
test_quote_endpoint_uses_shared_router
test_historical_endpoint_uses_shared_router
test_invalid_historical_range_fails_closed

backend/app/stacks/market_data/tests/test_stage8_runtime_qualification.py

test_quote_cache_prevents_repeated_provider_call
test_quote_cache_expiry_forces_refresh
test_use_cache_false_always_calls_provider
test_router_falls_back_after_quote_failure
test_router_falls_back_after_historical_failure
test_router_fails_closed_when_every_provider_fails
test_api_translates_provider_failure_to_503
test_api_rejects_invalid_historical_range
test_status_endpoint_does_not_call_provider

backend/app/stacks/market_data/tests/test_yfinance_provider.py

test_module_import_does_not_require_yfinance
test_wrapper_satisfies_provider_contract
test_capabilities_are_declared
test_numeric_quote_is_normalized
test_mapping_quote_is_normalized
test_quote_symbol_mismatch_fails
test_quote_loader_failure_is_translated
test_historical_mapping_is_normalized
test_historical_rows_are_sorted
test_historical_limit_is_applied
test_historical_loader_failure_is_translated
test_healthcheck_does_not_load_dependencies

backend/app/stacks/portfolio/tests/test_authenticated_portfolio_read_isolation.py

test_accounting_rejects_empty_owner
test_ledger_read_rejects_empty_owner
test_position_route_is_authenticated_and_scoped
test_orders_route_is_authenticated_and_scoped
test_analytics_route_is_authenticated_and_scoped
test_accounting_is_owner_scoped
test_max_allocation_is_owner_scoped
test_risk_propagates_owner
test_execution_propagates_owner

backend/app/stacks/risk/tests/test_drawdown_guard_ledger_boundary.py

test_risk_owns_no_persistence_import
test_risk_imports_no_ledger_internals
test_risk_calls_only_read_facade
test_healthcheck_preserves_none_contract
test_healthcheck_uses_scalar_facade
test_ledger_owns_read_query
test_read_facade_exposes_no_session_or_model

backend/app/stacks/snaptrade/tests/test_sdk_client_factory.py

test_credentials_absent_by_default
test_external_access_is_disabled_by_default
test_builds_supported_auth_modes_without_network_call
test_network_health_check_fails_closed
test_wrapper_exposes_no_trading_methods

backend/app/stacks/wolfden_ai/tests/test_local_model_binding.py

test_request_contract_is_immutable
test_response_contract_is_immutable
test_response_contract_has_failure_status
test_valid_plain_output_is_normalized
test_valid_structured_output_is_parsed
test_invalid_output_fails_closed
test_oversized_output_fails_closed
test_dangerous_text_cannot_unlock_capability
test_approved_adapter_uses_timeout_bridge
test_internal_timeout_maps_to_rejection
test_adapter_exception_maps_to_rejection
test_non_string_adapter_output_maps_to_rejection
test_default_wrapper_preserves_core_behavior
test_model_failure_cannot_block_core
test_rejected_response_cannot_block_core
test_agent_wrapper_has_failure_guard
test_contract_owns_timeout_and_parser
test_contract_owns_no_mutation_capability

backend/app/stacks/wolfden_ai/tests/test_observability_boundary.py

test_observation_is_immutable
test_observation_is_non_persistent
test_observation_rejects_persistent_state
test_observation_rejects_mutation_request
test_payload_is_deeply_frozen
test_standard_logging_is_used
test_agent_router_uses_observability_boundary
test_boundary_owns_no_persistence_or_execution
test_journal_ledger_and_execution_are_preserved

backend/app/test/test_graph_event_metrics.py

test_node_metrics_aggregate_latency_and_success
test_security_metrics_count_unauthorized_and_forbidden
test_edge_metrics_are_aggregated
test_snapshot_advertises_metric_contract_version_two

backend/app/test/test_stage8e_runtime_instrumentation.py

test_stage8e_architecture_nodes_are_registered
test_runtime_trace_supports_stage8d_metrics
test_chat_runtime_contains_required_operational_stages
test_route_policy_emits_security_events
test_frontend_preserves_playback_and_exposes_metrics
test_global_event_bus_remains_canonical

backend/app/test/test_stage8f_graph_materialization.py

test_all_layers_have_declared_nodes
test_required_facades_are_declared_in_l3
test_frontend_workspaces_and_proxies_are_declared
test_snapshot_materializes_declared_topology_without_events
test_real_node_activation_overrides_declared_state
test_real_edge_materializes_both_endpoints
test_declared_edge_becomes_observed_without_losing_relation
test_stage8f_preserves_version_two_contract

backend/app/test/test_trading_pipeline.py

test_trading_pipeline_success
test_trading_pipeline_blocked
test_agent_router_trips_kill_switch

frontend/tests/e2e/09-objective4h-b-broad-prompt-matrix.spec.ts

qualifies broad authenticated cognitive behavior

Current Gaps

A dedicated liveness contract was not detected.

FUNCTION FLOW GRAPH

Authorized User or Monitoring Process
      │
      ▼
System Health Frontend
      │
      ▼
Health / Status API
      │
      ▼
Backend Health Aggregator
      │
      ├────────► Backend Process
      ├────────► Database
      ├────────► Ollama
      ├────────► Market Data
      ├────────► Broker Adapter
      ├────────► Workers / Queues
      └────────► Runtime Graph
      │
      ▼
Health Classification
      │
      ├────────► HEALTHY
      ├────────► DEGRADED
      ├────────► UNAVAILABLE
      └────────► UNKNOWN
      │
      ▼
Metrics + Logs + Runtime Trace
      │
      ▼
Alert Integration
      │
      ▼
Frontend Status Display

Repository Files

Frontend

frontend/app/admin/tickets/page.tsx
frontend/app/admin/users/page.tsx
frontend/app/api/auth/login/route.ts
frontend/app/api/auth/register/route.ts
frontend/app/api/v1/graph/live/route.ts
frontend/app/api/v1/portfolio/positions/route.ts
frontend/app/api/v1/portfolio/valuation/route.ts
frontend/app/components/auth/LogoutButton.tsx
frontend/app/components/layout/DashboardShell.tsx
frontend/app/components/layout/WorkspaceRouter.tsx
frontend/app/components/workspaces/LearningWorkspacePanel.tsx
frontend/app/components/workspaces/NeuroWorkspace.tsx
frontend/app/components/workspaces/ObservabilityWorkspacePanel.tsx
frontend/app/components/workspaces/OverviewWorkspace.tsx
frontend/app/dashboard/page.tsx
frontend/app/login/page.tsx
frontend/app/page.tsx
frontend/app/register/page.tsx
frontend/app/user/components/RecentOrderActivity.tsx
frontend/app/user/dashboard/UserStrategiesWorkspace.tsx
frontend/app/user/dashboard/page.tsx
frontend/app/user/settings/page.tsx
frontend/components/app-shell/WorkspacePage.tsx
frontend/components/app-shell/workspaceConfig.ts
frontend/lib/uiPreferences.ts
frontend/services/backendHealthService.ts
frontend/services/chat/chatContracts.ts
frontend/services/graphService.ts
frontend/services/observabilityTimelineService.ts
frontend/services/requestNormalizer.ts
frontend/services/requestObservability.ts
frontend/tests/e2e/09-objective4h-b-broad-prompt-matrix.spec.ts

Backend

backend/app/core/cognitive_event_bus.py
backend/app/core/cognitive_graph_state.py
backend/app/core/config.py
backend/app/llm_bridge/cognition_core.py
backend/app/main.py
backend/app/spine/L5_api/owned_readonly_portfolio_service.py
backend/app/stacks/chat_public/capability_state_registry.py
backend/app/stacks/chat_public/chat_api.py
backend/app/stacks/chat_public/chat_intent_regex.py
backend/app/stacks/chat_public/chat_memory.py
backend/app/stacks/chat_public/chat_runtime.py
backend/app/stacks/chat_public/chat_service.py
backend/app/stacks/chat_public/chat_system_prompt.py
backend/app/stacks/chat_public/context/context_assembler.py
backend/app/stacks/chat_public/contracts/chat_contracts.py
backend/app/stacks/chat_public/conversation_service.py
backend/app/stacks/chat_public/conversation_store.py
backend/app/stacks/chat_public/developer_response_builder.py
backend/app/stacks/chat_public/math_tools/live_math.py
backend/app/stacks/chat_public/public_controls.py
backend/app/stacks/chat_public/tests/test_capability_state_registry.py
backend/app/stacks/chat_public/tests/test_live_rag_activation.py
backend/app/stacks/chat_public/tests/test_public_chat_controls.py
backend/app/stacks/db_runtime/__init__.py
backend/app/stacks/db_runtime/database.py
backend/app/stacks/execution/accounting_engine.py
backend/app/stacks/execution/commission_engine.py
backend/app/stacks/execution/executor.py
backend/app/stacks/execution/fill_engine.py
backend/app/stacks/execution/paper_broker.py
backend/app/stacks/execution/pnl_engine.py
backend/app/stacks/execution/regime_modes.py
backend/app/stacks/execution/regime_simulator.py
backend/app/stacks/execution/sandbox.py
backend/app/stacks/execution/sandbox_runtime.py
backend/app/stacks/execution/trade_ledger.py
backend/app/stacks/identity_auth/admin_mutation_service.py
backend/app/stacks/identity_auth/admin_read_models.py
backend/app/stacks/identity_auth/authorization_policy.py
backend/app/stacks/identity_auth/errors.py
backend/app/stacks/identity_auth/route_protection.py
backend/app/stacks/identity_auth/runtime_adapter.py
backend/app/stacks/identity_auth/tests/test_login_service.py
backend/app/stacks/identity_auth/tests/test_stage5b_c_revocation_observability_cleanup.py
backend/app/stacks/journal_ledger/ledger.py
backend/app/stacks/journal_ledger/tests/test_decision_audit_query_facade_failure_behavior.py
backend/app/stacks/learning_research/backtest_engine.py
backend/app/stacks/learning_research/monte_carlo.py
backend/app/stacks/learning_research/monte_carlo_mix.py
backend/app/stacks/learning_research/probability_engine.py
backend/app/stacks/learning_research/research_runtime.py
backend/app/stacks/learning_research/strategy_evaluator.py
backend/app/stacks/market_data/api_router.py
backend/app/stacks/market_data/dto.py
backend/app/stacks/market_data/feed.py
backend/app/stacks/market_data/market_session.py
backend/app/stacks/market_data/provider_cache.py
backend/app/stacks/market_data/provider_contract.py
backend/app/stacks/market_data/provider_registry.py
backend/app/stacks/market_data/provider_router.py
backend/app/stacks/market_data/runtime_composition.py
backend/app/stacks/market_data/tests/test_provider_contract.py
backend/app/stacks/market_data/tests/test_provider_runtime.py
backend/app/stacks/market_data/tests/test_runtime_composition.py
backend/app/stacks/market_data/tests/test_stage8_runtime_qualification.py
backend/app/stacks/market_data/tests/test_yfinance_provider.py
backend/app/stacks/market_data/yfinance_provider.py
backend/app/stacks/portfolio/dashboard_service.py
backend/app/stacks/portfolio/portfolio_runtime.py
backend/app/stacks/portfolio/reconciliation.py
backend/app/stacks/portfolio/tests/test_authenticated_portfolio_read_isolation.py
backend/app/stacks/risk/drawdown_guard.py
backend/app/stacks/risk/loss_streak_guard.py
backend/app/stacks/risk/risk_runtime_service.py
backend/app/stacks/risk/risk_service.py
backend/app/stacks/risk/tests/test_drawdown_guard_ledger_boundary.py
backend/app/stacks/snaptrade/adapter.py
backend/app/stacks/snaptrade/adapters/sandbox_readonly_client.py
backend/app/stacks/snaptrade/broker.py
backend/app/stacks/snaptrade/execution.py
backend/app/stacks/snaptrade/tests/test_sdk_client_factory.py
backend/app/stacks/strategy/candidate_registry.py
backend/app/stacks/strategy/evolution_engine.py
backend/app/stacks/strategy/strategy_registry.py
backend/app/stacks/strategy/strategy_runtime.py
backend/app/stacks/wolfden_ai/agent_router.py
backend/app/stacks/wolfden_ai/local_model_contract.py
backend/app/stacks/wolfden_ai/memory.py
backend/app/stacks/wolfden_ai/observability_boundary.py
backend/app/stacks/wolfden_ai/routing.py
backend/app/stacks/wolfden_ai/runtime.py
backend/app/stacks/wolfden_ai/tests/test_local_model_binding.py
backend/app/stacks/wolfden_ai/tests/test_observability_boundary.py
backend/app/test/test_graph_event_metrics.py
backend/app/test/test_stage8e_runtime_instrumentation.py
backend/app/test/test_stage8f_graph_materialization.py
backend/app/test/test_trading_pipeline.py

Launch Dependency

Required Before Launch

YES

Blocks

Service readiness verification

Database readiness verification

Ollama readiness verification

Market-data readiness verification

Runtime degradation detection

Outage investigation

Restart and recovery verification

Controlled early-user launch

FINAL VERDICT

Function Exists: YES

Health Pages: DETECTED

Frontend Requests: DETECTED

Backend Routes: DETECTED

Liveness: UNVERIFIED

Readiness: DETECTED

Database Health: DETECTED

Ollama Health: DETECTED

Market-Data Health: DETECTED

Broker Health: DETECTED

Runtime Graph: DETECTED

Metrics: DETECTED

Structured Logging: DETECTED

Runtime Tracing: DETECTED

Degraded State: DETECTED

Unavailable State: DETECTED

Operating Mode: DETECTED

Relevant Tests: PRESENT

Live Verification: NOT COMPLETE

Launch Ready: UNVERIFIED

Overall Classification

PARTIALLY VERIFIED

Launch Classification

CRITICAL

---



---

FUNCTION PATH 16 — BROKER INTEGRATION, SNAPTRADE, AND ACCOUNT CONNECTIONS

Function Status

Inventory Status: INITIAL INVENTORY COMPLETE
Implementation Status: IMPLEMENTED — SOURCE VERIFICATION PENDING
Qualification Status: UNVERIFIED
Launch Importance: CRITICAL
Last Updated: 2026-07-31
Evidence Source: runtime/system_inventory/function_path_16_broker_snaptrade_20260731_173437/function_path_16_broker_snaptrade_inventory.json

Purpose

The Broker Integration, SnapTrade, and Account Connections function
connects authenticated NeuroVest users to supported brokerage
accounts for controlled read-only account, balance, position, and
activity synchronization.

Its purpose is to:

- Require authenticated user access.
- Enforce broker-account ownership.
- Register users with SnapTrade safely.
- Generate controlled brokerage connection portals.
- List brokerage connections and authorizations.
- List connected brokerage accounts.
- Synchronize balances, positions, and activities.
- Record last synchronization and connection status.
- Reconcile broker data with NeuroVest read models.
- Disconnect brokerage connections safely.
- Validate webhook signatures where webhooks are supported.
- Encrypt and redact broker credentials and secrets.
- Apply idempotency, retry, timeout, and rate-limit controls.
- Record audit and runtime evidence.
- Preserve paper-trading and emergency-stop boundaries.
- Prevent automatic live order submission.

Primary Function Flow

Authenticated User
      │
      ▼
Broker / Account Connection Page
      │
      ▼
Frontend Broker Service
      │
      ▼
Next.js Broker Proxy
      │
      ▼
Backend Broker API
      │
      ▼
Authentication and Ownership
      │
      ▼
SnapTrade User Registration
      │
      ▼
Connection Portal
      │
      ▼
Brokerage Authorization
      │
      ▼
Connected Accounts
      │
      ├────────► Balances
      ├────────► Positions
      ├────────► Activities
      └────────► Connection Status
      │
      ▼
Synchronization and Reconciliation
      │
      ▼
Read-Only Portfolio Context

Broker Pages

frontend/app/admin/user-stats/page.tsx

Frontend Requests

No direct frontend broker or SnapTrade request detected.

Backend Routes

No decorated broker or SnapTrade route detected.

Possible Order-Execution Functions

backend/app/stacks/snaptrade/tests/test_sdk_client_factory.py:191
Function: test_wrapper_exposes_no_trading_methods
Markers: cancel_order, execute_order, place_order, submit_order

backend/app/stacks/wolfden_ai/tests/test_observability_boundary.py:270
Function: test_boundary_owns_no_persistence_or_execution
Markers: execute_order, place_order, submit_order

backend/app/stacks/wolfden_ai/tests/test_portfolio_output_result_facade.py:222
Function: test_wolfden_owns_no_execution_or_mutation_capability
Markers: execute_order, place_order, submit_order

Controls and Behaviour

authentication_detected

True

authorization_detected

True

ownership_detected

True

snaptrade_client_detected

True

user_registration_detected

True

connection_portal_detected

False

connection_listing_detected

False

disconnect_detected

False

account_listing_detected

True

balance_sync_detected

True

position_sync_detected

True

activity_sync_detected

False

synchronization_detected

False

reconciliation_detected

True

webhook_detected

True

webhook_signature_detected

False

credential_encryption_detected

False

sensitive_data_controls_detected

True

idempotency_detected

True

retry_detected

True

rate_limit_detected

True

transaction_detected

True

rollback_detected

True

audit_evidence_detected

True

paper_boundary_detected

True

emergency_stop_detected

False

live_execution_disabled_detected

False

possible_execution_markers_detected

True

Frontend States

loading_detected

False

error_detected

False

empty_detected

False

connected_detected

False

disconnected_detected

False

connect_action_detected

False

disconnect_action_detected

False

sync_action_detected

False

last_sync_display_detected

False

account_display_detected

False

balance_display_detected

False

position_display_detected

False

confirmation_dialog_detected

False

responsive_detected

True

accessibility_detected

False

Tests

backend/app/stacks/chat_public/tests/test_capability_state_registry.py

test_registry_is_read_only_and_complete
test_registry_uses_declared_state_categories
test_drawdown_guard_is_not_called_without_balance
test_registry_summary_is_grounded_in_rows
test_developer_response_contains_capability_state
test_developer_capabilities_remain_grounded
test_unverified_adapter_and_async_states_require_attention

backend/app/stacks/portfolio/tests/test_authenticated_owned_readonly_portfolio_api.py

test_configured_owner_receives_two_accounts
test_unbound_user_is_denied
test_empty_principal_subject_is_denied
test_owner_receives_only_bound_account_hashes
test_read_views_are_normalized
test_symbol_lookup_is_owner_scoped
test_no_raw_account_identifier_fields_are_returned
test_service_records_no_network_or_database_activity

backend/app/stacks/portfolio/tests/test_portfolio_snapshot_lifecycle.py

test_refresh_promotes_owner_scoped_snapshot_atomically
test_second_refresh_preserves_last_known_good
test_failed_refresh_keeps_active_snapshot
test_staleness_is_reported
test_retention_is_bounded
test_unbound_user_refresh_is_denied
test_lifecycle_contains_no_raw_owner_id

backend/app/stacks/portfolio/tests/test_readonly_portfolio_facade.py

test_facade_overview
test_lists_account_summaries
test_get_account_by_hash
test_unknown_account_is_rejected
test_lists_all_positions
test_symbol_lookup_is_normalized
test_unknown_symbol_returns_empty_tuple
test_empty_symbol_is_rejected
test_lists_balances
test_totals_are_provider_neutral
test_overview_is_immutable
test_account_summary_is_immutable
test_symbol_result_is_immutable
test_symbol_index_is_not_mutable
test_facade_has_no_mutation_methods
test_facade_source_has_no_provider_import

backend/app/stacks/snaptrade/tests/__init__.py

Broker-related test content detected.

backend/app/stacks/snaptrade/tests/test_normalized_portfolio_ingestion.py

test_ingests_qualified_snapshot
test_contract_is_immutable
test_rejects_unsafe_top_level_flags
test_rejects_wrong_schema
test_rejects_wrong_schema_version
test_rejects_raw_account_identifier
test_rejects_position_count_drift
test_does_not_import_snaptrade_sdk

backend/app/stacks/snaptrade/tests/test_portfolio_owner_binding.py

test_empty_registry_fails_closed
test_resolves_only_authenticated_owner
test_rejects_cross_owner_account_reuse
test_filters_snapshot_accounts_to_owner
test_rejects_binding_to_absent_snapshot_account
test_rejects_empty_user_id
test_registry_contains_no_raw_account_ids

backend/app/stacks/snaptrade/tests/test_sdk_client_factory.py

test_credentials_absent_by_default
test_external_access_is_disabled_by_default
test_builds_supported_auth_modes_without_network_call
test_network_health_check_fails_closed
test_wrapper_exposes_no_trading_methods

backend/app/stacks/wolfden_ai/tests/test_local_model_binding.py

test_request_contract_is_immutable
test_response_contract_is_immutable
test_response_contract_has_failure_status
test_valid_plain_output_is_normalized
test_valid_structured_output_is_parsed
test_invalid_output_fails_closed
test_oversized_output_fails_closed
test_dangerous_text_cannot_unlock_capability
test_approved_adapter_uses_timeout_bridge
test_internal_timeout_maps_to_rejection
test_adapter_exception_maps_to_rejection
test_non_string_adapter_output_maps_to_rejection
test_default_wrapper_preserves_core_behavior
test_model_failure_cannot_block_core
test_rejected_response_cannot_block_core
test_agent_wrapper_has_failure_guard
test_contract_owns_timeout_and_parser
test_contract_owns_no_mutation_capability

backend/app/stacks/wolfden_ai/tests/test_observability_boundary.py

test_observation_is_immutable
test_observation_is_non_persistent
test_observation_rejects_persistent_state
test_observation_rejects_mutation_request
test_payload_is_deeply_frozen
test_standard_logging_is_used
test_agent_router_uses_observability_boundary
test_boundary_owns_no_persistence_or_execution
test_journal_ledger_and_execution_are_preserved

backend/app/stacks/wolfden_ai/tests/test_portfolio_output_result_facade.py

test_result_is_immutable
test_result_is_non_executable
test_result_rejects_executable_state
test_payload_is_deeply_frozen
test_result_has_serializable_mapping_contract
test_agent_router_uses_wolfden_facade_only
test_wolfden_owns_no_execution_or_mutation_capability

Current Gaps

No direct frontend broker or SnapTrade request was detected.

No decorated broker or SnapTrade backend route was mapped.

Broker connection-portal generation was not detected.

Broker synchronization state was not detected.

Explicit encryption for broker secrets was not detected.

Potential broker order-execution functions were detected and require direct call-path review.

FUNCTION FLOW GRAPH

Authenticated User
      │
      ▼
Broker Connection Frontend
      │
      ▼
Next.js Broker Proxy
      │
      ▼
Backend Broker API
      │
      ▼
Authentication + Authorization
      │
      ▼
User and Account Ownership
      │
      ▼
SnapTrade Adapter
      │
      ├────────► User Registration
      ├────────► Connection Portal
      ├────────► Authorizations
      ├────────► Accounts
      ├────────► Balances
      ├────────► Positions
      └────────► Activities
      │
      ▼
Synchronization
      │
      ▼
Reconciliation
      │
      ▼
Credential Redaction + Audit Evidence
      │
      ▼
Read-Only Portfolio Context
      │
      └────────► No Automatic Live Execution

Repository Files

Frontend

frontend/app/admin/user-stats/page.tsx

Backend

backend/app/core/cognitive_graph_state.py
backend/app/core/global_firewall_v1.py
backend/app/core/runtime_firewall_v1.py
backend/app/snaptrade/executions/config.py
backend/app/snaptrade/executions/execution_layer.py
backend/app/spine/L5_api/owned_readonly_portfolio_service.py
backend/app/stacks/chat_public/capability_state_registry.py
backend/app/stacks/chat_public/chat_system_prompt.py
backend/app/stacks/chat_public/developer_response_builder.py
backend/app/stacks/chat_public/public_controls.py
backend/app/stacks/chat_public/tests/test_capability_state_registry.py
backend/app/stacks/portfolio/portfolio_snapshot_lifecycle.py
backend/app/stacks/portfolio/tests/test_authenticated_owned_readonly_portfolio_api.py
backend/app/stacks/portfolio/tests/test_portfolio_snapshot_lifecycle.py
backend/app/stacks/portfolio/tests/test_readonly_portfolio_facade.py
backend/app/stacks/snaptrade/__init__.py
backend/app/stacks/snaptrade/adapter.py
backend/app/stacks/snaptrade/adapters/readonly_adapter.py
backend/app/stacks/snaptrade/adapters/sandbox_readonly_client.py
backend/app/stacks/snaptrade/adapters/sdk_client_factory.py
backend/app/stacks/snaptrade/application/__init__.py
backend/app/stacks/snaptrade/application/normalized_portfolio_ingestion.py
backend/app/stacks/snaptrade/application/portfolio_owner_binding.py
backend/app/stacks/snaptrade/base.py
backend/app/stacks/snaptrade/broker.py
backend/app/stacks/snaptrade/config/external_activation_gate.py
backend/app/stacks/snaptrade/config/provider_config.py
backend/app/stacks/snaptrade/contracts/readonly_models.py
backend/app/stacks/snaptrade/contracts/readonly_provider.py
backend/app/stacks/snaptrade/execution.py
backend/app/stacks/snaptrade/facade/provider_factory.py
backend/app/stacks/snaptrade/facade/snaptrade_readonly_facade.py
backend/app/stacks/snaptrade/providers/disabled_provider.py
backend/app/stacks/snaptrade/providers/mock_provider.py
backend/app/stacks/snaptrade/security/credential_boundary.py
backend/app/stacks/snaptrade/security/redaction.py
backend/app/stacks/snaptrade/tests/__init__.py
backend/app/stacks/snaptrade/tests/test_normalized_portfolio_ingestion.py
backend/app/stacks/snaptrade/tests/test_portfolio_owner_binding.py
backend/app/stacks/snaptrade/tests/test_sdk_client_factory.py
backend/app/stacks/wolfden_ai/observability_boundary.py
backend/app/stacks/wolfden_ai/portfolio_output_result_facade.py
backend/app/stacks/wolfden_ai/tests/test_local_model_binding.py
backend/app/stacks/wolfden_ai/tests/test_observability_boundary.py
backend/app/stacks/wolfden_ai/tests/test_portfolio_output_result_facade.py

Launch Dependency

Required Before Launch

YES FOR BROKER-CONNECTED READ FEATURES

Blocks

Broker account connection

External account synchronization

External balance visibility

External position visibility

Broker activity history

Broker reconciliation

Connected-account portfolio context

Controlled SnapTrade paper integration

FINAL VERDICT

Function Exists: YES

Broker Pages: DETECTED

Frontend Requests: UNVERIFIED

Backend Routes: UNVERIFIED

Authentication: DETECTED

Ownership: DETECTED

SnapTrade Client: DETECTED

User Registration: DETECTED

Connection Portal: UNVERIFIED

Connections: UNVERIFIED

Account Listing: DETECTED

Balances: DETECTED

Positions: DETECTED

Activities: UNVERIFIED

Synchronization: UNVERIFIED

Reconciliation: DETECTED

Webhook Support: DETECTED

Webhook Signature Verification: UNVERIFIED

Credential Encryption: UNVERIFIED

Credential Redaction: DETECTED

Idempotency: DETECTED

Retry and Timeout: DETECTED

Rate Limiting: DETECTED

Paper Boundary: DETECTED

Emergency Stop: UNVERIFIED

Possible Execution Functions: DETECTED — DIRECT REVIEW REQUIRED

Relevant Tests: PRESENT

Live Verification: NOT COMPLETE

Launch Ready: UNVERIFIED

Overall Classification

PARTIALLY VERIFIED

Launch Classification

CRITICAL

---



---

FUNCTION PATH 17 — OPERATING MODES, SAFETY CONTROLS, AND EMERGENCY STOP

Function Status

Inventory Status: INITIAL INVENTORY COMPLETE
Implementation Status: IMPLEMENTED — SOURCE VERIFICATION PENDING
Qualification Status: UNVERIFIED
Launch Importance: CRITICAL
Last Updated: 2026-07-31
Evidence Source: runtime/system_inventory/function_path_17_operating_modes_20260731_174530/function_path_17_operating_modes_inventory.json

Purpose

The Operating Modes, Safety Controls, and Emergency Stop function
defines which NeuroVest operations are permitted and ensures that
restricted actions cannot bypass the current safety state.

Its purpose is to:

- Define SAFE, SIMULATION, LOCKED, and EMERGENCY_STOP states.
- Display the current operating mode.
- Restrict operating-mode changes to authorized administrators.
- Validate every mode transition.
- Require confirmation and a reason for high-impact transitions.
- activate emergency stop through a controlled path.
- Prevent casual or unauthorized emergency-stop clearing.
- Apply the current mode to strategy, risk, paper, broker, and chat.
- Prevent live execution unless separately approved.
- Preserve paper-only operation during controlled launch.
- Persist operating mode safely.
- Recover the correct mode after restart.
- Fail closed when mode state is unavailable or corrupt.
- Record actor, prior mode, new mode, reason, time, and trace evidence.
- Apply CSRF, rate limiting, idempotency, transactions, and rollback.

Primary Function Flow

Authenticated Administrator
      │
      ▼
Safety Control Interface
      │
      ▼
Operating-Mode Request
      │
      ▼
Authentication and Administrator Authorization
      │
      ▼
Current Mode
      │
      ▼
Requested Mode
      │
      ▼
Transition Validation
      │
      ├────────► SAFE
      ├────────► SIMULATION
      ├────────► LOCKED
      └────────► EMERGENCY_STOP
      │
      ▼
Confirmation and Reason
      │
      ▼
Transaction and Persistent State
      │
      ├────────► Commit
      └────────► Rollback
      │
      ▼
Audit Evidence
      │
      ▼
Central Execution Gate
      │
      ├────────► Strategy
      ├────────► Risk
      ├────────► Paper Trading
      ├────────► Broker Integration
      └────────► Chat Actions

Safety Pages

frontend/app/admin/page.tsx
frontend/app/dashboard/page.tsx

Frontend Requests

No direct frontend operating-mode or emergency-stop request detected.

Backend Routes

No decorated operating-mode or emergency-stop route detected.

Detected Mode Constants

PAPER
Source: backend/app/stacks/execution/paper_broker.py:34

PAPER
Source: backend/app/stacks/execution/paper_broker.py:37

PAPER
Source: backend/app/stacks/execution/paper_broker.py:133

PAPER
Source: backend/app/stacks/execution/paper_broker.py:189

SIMULATION
Source: backend/app/stacks/execution/paper_broker.py:189

PAPER
Source: backend/app/stacks/execution/paper_broker.py:202

PAPER
Source: backend/app/stacks/identity_auth/authorization_policy.py:46

EMERGENCY_STOP
Source: backend/app/stacks/identity_auth/authorization_policy.py:102

EMERGENCY_STOP
Source: backend/app/stacks/identity_auth/tests/test_stage9d_c5_i_authorization_policy.py:119

Execution-Marker Functions

No execution-marker function detected.

Controls and Behaviour

authentication_detected

True

admin_authorization_detected

True

safe_mode_detected

False

simulation_mode_detected

True

paper_mode_detected

False

locked_mode_detected

False

emergency_stop_detected

True

mode_read_detected

False

mode_mutation_detected

False

transition_validation_detected

False

emergency_activation_detected

True

emergency_clear_detected

False

execution_gate_detected

False

paper_gate_detected

False

live_gate_detected

False

strategy_gate_detected

True

risk_gate_detected

True

broker_gate_detected

False

chat_gate_detected

False

persistence_detected

True

restart_recovery_detected

False

audit_evidence_detected

True

reason_detected

True

confirmation_detected

True

csrf_detected

True

rate_limit_detected

False

idempotency_detected

False

transaction_detected

True

rollback_detected

True

sensitive_data_controls_detected

False

Frontend States

loading_detected

True

error_detected

True

mode_display_detected

False

safe_display_detected

True

simulation_display_detected

True

locked_display_detected

True

emergency_display_detected

False

mode_control_detected

False

emergency_action_detected

False

clear_emergency_action_detected

False

reason_input_detected

False

confirmation_dialog_detected

True

timestamp_display_detected

False

actor_display_detected

False

responsive_detected

True

accessibility_detected

True

Tests

backend/app/stacks/identity_auth/tests/test_stage9d_c5_i_authorization_policy.py

test_canonical_roles
test_subscription_tiers_remain_separate
test_owner_normalizes_to_developer
test_administrative_roles
test_unknown_roles_fail_closed
test_admin_user_management_permissions
test_developer_inherits_admin_permissions
test_dangerous_permissions_remain_separate
test_authorization_decisions_fail_closed

backend/app/stacks/portfolio/tests/test_execution_ownership_propagation.py

test_paper_execution_rejects_empty_user_id
test_ledger_rejects_empty_user_id
test_all_paper_broker_save_log_calls_propagate_user_id
test_ledger_inventory_lookup_is_account_scoped
test_order_history_write_is_account_scoped

backend/app/stacks/risk/tests/test_drawdown_guard_ledger_boundary.py

test_risk_owns_no_persistence_import
test_risk_imports_no_ledger_internals
test_risk_calls_only_read_facade
test_healthcheck_preserves_none_contract
test_healthcheck_uses_scalar_facade
test_ledger_owns_read_query
test_read_facade_exposes_no_session_or_model

backend/app/test/test_trading_pipeline.py

test_trading_pipeline_success
test_trading_pipeline_blocked
test_agent_router_trips_kill_switch

Current Gaps

No direct frontend operating-mode or emergency-stop request was detected.

No decorated operating-mode or emergency-stop backend route was mapped.

SAFE mode was not detected.

LOCKED mode was not detected.

Explicit operating-mode transition validation was not detected.

A centralized execution gate was not detected.

Operating-mode restart recovery was not detected.

FUNCTION FLOW GRAPH

Authenticated Administrator
      │
      ▼
Safety Control Frontend
      │
      ▼
Operating Mode API
      │
      ▼
Authentication + Administrator Authorization
      │
      ▼
Current Mode + Requested Mode
      │
      ▼
Transition Policy
      │
      ├────────► SAFE
      ├────────► SIMULATION
      ├────────► LOCKED
      └────────► EMERGENCY_STOP
      │
      ▼
Confirmation + Reason
      │
      ▼
Persistent Runtime State
      │
      ├────────► Commit
      └────────► Rollback
      │
      ▼
Administrative Audit Evidence
      │
      ▼
Central Safety Gate
      │
      ├────────► Strategy Decisions
      ├────────► Risk Decisions
      ├────────► Paper Orders
      ├────────► Broker Actions
      └────────► Chat Tool Actions
      │
      ▼
Allowed or Rejected Operation

Repository Files

Frontend

frontend/app/admin/page.tsx
frontend/app/api/v1/risk/gate/[symbol]/route.ts
frontend/app/components/layout/DashboardShell.tsx
frontend/app/dashboard/page.tsx
frontend/app/login/page.tsx
frontend/app/page.tsx
frontend/app/user/components/NeuroWelcomeBriefing.tsx

Backend

backend/app/snaptrade/executions/execution_layer.py
backend/app/stacks/execution/__init__.py
backend/app/stacks/execution/accounting_engine.py
backend/app/stacks/execution/base.py
backend/app/stacks/execution/broker.py
backend/app/stacks/execution/commission_engine.py
backend/app/stacks/execution/executor.py
backend/app/stacks/execution/fill_engine.py
backend/app/stacks/execution/paper_broker.py
backend/app/stacks/execution/pnl_engine.py
backend/app/stacks/execution/regime_modes.py
backend/app/stacks/execution/regime_simulator.py
backend/app/stacks/execution/sandbox.py
backend/app/stacks/execution/sandbox_runtime.py
backend/app/stacks/execution/trade_ledger.py
backend/app/stacks/identity_auth/authorization_policy.py
backend/app/stacks/identity_auth/tests/test_stage9d_c5_i_authorization_policy.py
backend/app/stacks/portfolio/tests/test_execution_ownership_propagation.py
backend/app/stacks/risk/__init__.py
backend/app/stacks/risk/base.py
backend/app/stacks/risk/drawdown_guard.py
backend/app/stacks/risk/exposure.py
backend/app/stacks/risk/kill_switch.py
backend/app/stacks/risk/limits.py
backend/app/stacks/risk/loss_streak_guard.py
backend/app/stacks/risk/risk_runtime_service.py
backend/app/stacks/risk/risk_service.py
backend/app/stacks/risk/tests/test_drawdown_guard_ledger_boundary.py
backend/app/stacks/wolfden_ai/agent_router.py
backend/app/test/test_trading_pipeline.py

Launch Dependency

Required Before Launch

YES

Blocks

Safe controlled operation

Paper-trading authorization

Execution isolation

Emergency shutdown

Restart safety

Administrative mode control

Broker safety boundaries

Controlled early-user launch

FINAL VERDICT

Function Exists: YES

Safety Pages: DETECTED

Frontend Requests: UNVERIFIED

Backend Routes: UNVERIFIED

Authentication: DETECTED

Administrator Authorization: DETECTED

SAFE Mode: UNVERIFIED

SIMULATION Mode: DETECTED

Paper Mode: UNVERIFIED

LOCKED Mode: UNVERIFIED

EMERGENCY_STOP: DETECTED

Mode Read: UNVERIFIED

Mode Mutation: UNVERIFIED

Transition Validation: UNVERIFIED

Emergency Activation: DETECTED

Emergency Clear: UNVERIFIED

Central Execution Gate: UNVERIFIED

Paper Gate: UNVERIFIED

Live Gate: UNVERIFIED

Risk Gate: DETECTED

Broker Gate: UNVERIFIED

Restart Recovery: UNVERIFIED

Audit Evidence: DETECTED

CSRF: DETECTED

Rate Limiting: UNVERIFIED

Idempotency: UNVERIFIED

Transactions: DETECTED

Rollback: DETECTED

Relevant Tests: PRESENT

Live Verification: NOT COMPLETE

Launch Ready: UNVERIFIED

Overall Classification

PARTIALLY VERIFIED

Launch Classification

CRITICAL

---



---

