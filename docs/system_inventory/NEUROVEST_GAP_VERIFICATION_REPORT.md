# NEUROVEST GAP VERIFICATION REPORT

Generated: 2026-07-31T19:29:46.327404

## FP02

Gap: Registration rate limiting was not conclusively detected.

Classification: VERIFY DETECTION

Evidence Found:

- frontend/app/page.tsx:127
- frontend/tests/e2e/09-objective4h-b-broad-prompt-matrix.spec.ts:451
- frontend/tests/e2e/09-objective4h-b-broad-prompt-matrix.spec.ts:453
- frontend/tests/e2e/09-objective4h-b-broad-prompt-matrix.spec.ts:478
- frontend/tests/e2e/09-objective4h-b-broad-prompt-matrix.spec.ts:483
- frontend/tests/e2e/09-objective4h-b-broad-prompt-matrix.spec.ts:493
- frontend/tests/e2e/05-authenticated-user-flow.spec.ts:4
- frontend/tests/e2e/05-authenticated-user-flow.spec.ts:69
- frontend/tests/e2e/05-authenticated-user-flow.spec.ts:70
- frontend/tests/e2e/05-authenticated-user-flow.spec.ts:79

---

## FP03

Gap: Login rate limiting was not conclusively detected.

Classification: VERIFY DETECTION

Evidence Found:

- frontend/proxy.ts:204
- frontend/proxy.ts:207
- frontend/proxy.ts:210
- frontend/proxy.ts:211
- frontend/proxy.ts:212
- frontend/proxy.ts:218
- frontend/proxy.ts:330
- frontend/proxy.ts:395
- frontend/proxy.ts:398
- frontend/proxy.ts:399

---

## FP04

Gap: The exact successful login-to-dashboard redirect was not conclusively detected.

Classification: VERIFY DETECTION

Evidence Found:

- frontend/next.config.ts:74
- frontend/proxy.ts:204
- frontend/proxy.ts:207
- frontend/proxy.ts:210
- frontend/proxy.ts:211
- frontend/proxy.ts:212
- frontend/proxy.ts:217
- frontend/proxy.ts:218
- frontend/proxy.ts:223
- frontend/proxy.ts:233

---

## FP11

Gap: No direct frontend /api/v1/chat request was detected.

Classification: VERIFY FRONTEND

Evidence Found:

- frontend/services/chatService.ts:5
- frontend/services/chatService.ts:6
- frontend/services/chatService.ts:7
- frontend/services/chatService.ts:9
- frontend/services/chatService.ts:13
- frontend/services/chatService.ts:15
- frontend/services/chatService.ts:19
- frontend/services/chatService.ts:20
- frontend/services/chatService.ts:31
- frontend/services/chatService.ts:37

---

## FP12

Gap: No direct frontend journal or ledger request was detected.

Classification: VERIFY FRONTEND

Evidence Found:

- NONE

---

## FP13

Gap: No decorated notification or alert backend route was mapped.

Classification: VERIFY ROUTE

Evidence Found:

- frontend/components/RoleAwareWorkspaceNav.tsx:60
- frontend/node_modules/axe-core/axe.js:14354
- frontend/node_modules/axe-core/axe.js:14359
- frontend/node_modules/axe-core/axe.js:14362
- frontend/node_modules/axe-core/axe.js:15309
- frontend/node_modules/axe-core/axe.js:15728
- frontend/node_modules/axe-core/axe.js:21777
- frontend/node_modules/axe-core/axe.js:21788
- frontend/node_modules/axe-core/axe.js:23933
- frontend/node_modules/axe-core/axe.js:26964

---

## FP13

Gap: No direct frontend notification request was detected.

Classification: VERIFY FRONTEND

Evidence Found:

- frontend/components/RoleAwareWorkspaceNav.tsx:60
- frontend/node_modules/axe-core/axe.js:14354
- frontend/node_modules/axe-core/axe.js:14359
- frontend/node_modules/axe-core/axe.js:14362
- frontend/node_modules/axe-core/axe.js:15309
- frontend/node_modules/axe-core/axe.js:15728
- frontend/node_modules/axe-core/axe.js:21777
- frontend/node_modules/axe-core/axe.js:21788
- frontend/node_modules/axe-core/axe.js:23933
- frontend/node_modules/axe-core/axe.js:26964

---

## FP16

Gap: No decorated broker or SnapTrade backend route was mapped.

Classification: VERIFY ROUTE

Evidence Found:

- frontend/app/page.tsx:247
- frontend/app/page.tsx:427
- frontend/app/page.tsx:436
- frontend/app/page.tsx:562
- frontend/tests/e2e/08-objective4g-d-authenticated-live-turn.spec.ts:1514
- frontend/.next/server/app/page.js:2
- frontend/.next/server/app/admin/page.js:1
- frontend/.next/server/app/login/page.js:2
- frontend/.next/server/app/dashboard/page.js:1
- frontend/.next/server/app/dashboard/page.js:2

---

## FP16

Gap: No direct frontend broker or SnapTrade request was detected.

Classification: VERIFY FRONTEND

Evidence Found:

- frontend/app/page.tsx:247
- frontend/app/page.tsx:427
- frontend/app/page.tsx:436
- frontend/app/page.tsx:562
- frontend/tests/e2e/08-objective4g-d-authenticated-live-turn.spec.ts:1514
- frontend/.next/server/app/page.js:2
- frontend/.next/server/app/admin/page.js:1
- frontend/.next/server/app/login/page.js:2
- frontend/.next/server/app/dashboard/page.js:1
- frontend/.next/server/app/dashboard/page.js:2

---

## FP17

Gap: No decorated operating-mode or emergency-stop backend route was mapped.

Classification: VERIFY ROUTE

Evidence Found:

- frontend/next.config.ts:11
- frontend/next.config.ts:15
- frontend/next.config.ts:18
- frontend/app/page.tsx:39
- frontend/app/page.tsx:48
- frontend/app/page.tsx:110
- frontend/app/page.tsx:111
- frontend/app/page.tsx:247
- frontend/app/page.tsx:248
- frontend/app/page.tsx:270

---

## FP17

Gap: No direct frontend operating-mode or emergency-stop request was detected.

Classification: VERIFY FRONTEND

Evidence Found:

- frontend/next.config.ts:11
- frontend/next.config.ts:15
- frontend/next.config.ts:18
- frontend/app/page.tsx:39
- frontend/app/page.tsx:48
- frontend/app/page.tsx:110
- frontend/app/page.tsx:111
- frontend/app/page.tsx:247
- frontend/app/page.tsx:248
- frontend/app/page.tsx:270

---

