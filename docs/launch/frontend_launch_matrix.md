# NeuroVest Controlled Early-Access Frontend Matrix

## Launch boundary

NeuroVest launches as:

- authenticated multi-user early access
- paper trading and simulation only
- no live broker execution
- no autonomous mutation
- small invited-user group

---

## USER WORKSPACE

### /user/dashboard

Access:
- user

Launch requirement:
- account session summary
- paper-trading entry point
- account-scoped positions
- account-scoped orders/activity
- account-scoped analytics
- market ticker
- Neuro chat access
- clear simulation-only status

Current state:
- styled
- session protected
- ticker present
- portfolio placeholder only
- news placeholder only
- no paper-trading controls
- no real positions rendering
- no real orders rendering
- no real analytics rendering

Disposition:
- CRITICAL — BUILD FIRST

### /user/chat

Access:
- user

Launch requirement:
- authenticated Neuro chat
- visible loading/error state
- user-context boundary
- no developer controls

Current state:
- shared Neuro workspace present

Disposition:
- VERIFY AND HARDEN

### /user/settings

Access:
- user

Launch requirement:
- account identity summary
- password-change link
- logout/session control
- subscription tier display
- support link

Current state:
- styled informational shell
- no meaningful account actions

Disposition:
- REQUIRED — SMALL BUILD

### /change-password

Access:
- password-change-required session

Launch requirement:
- current temporary password
- new password
- confirmation
- validation and error feedback
- redirect after success

Current state:
- functional form and API route present

Disposition:
- VERIFY WITH PLAYWRIGHT

---

## ADMIN WORKSPACE

### /admin

Access:
- admin
- owner
- developer only if intentionally permitted

Launch requirement:
- administrative directory
- links to operational pages
- no customer trading actions

Current state:
- styled and structurally complete

Disposition:
- VERIFY

### /admin/users

Access:
- admin
- owner
- permitted developer role

Launch requirement:
- search users
- inspect user
- enable/disable account
- require password change
- issue temporary password
- close account with confirmation

Current state:
- most complete admin page
- database-backed
- large and complex

Disposition:
- CRITICAL — PLAYWRIGHT TEST ACTIONS

### /admin/sessions

Access:
- admin
- owner

Launch requirement:
- list active sessions
- identify owner and timestamps
- revoke session

Current state:
- styled informational shell
- no direct data fetch
- no visible action controls

Disposition:
- REQUIRED — IMPLEMENT OR CLEARLY MARK READ-ONLY

### /admin/audit

Access:
- admin
- owner

Launch requirement:
- list audit records
- filtering or pagination
- read-only behavior

Current state:
- styled informational shell
- no direct data fetch

Disposition:
- REQUIRED — CONNECT READ-ONLY DATA

### /admin/tickets

Access:
- admin
- owner

Launch requirement:
- support-ticket list
- ticket detail
- controlled response/status workflow

Current state:
- styled informational shell
- no direct data fetch or forms

Disposition:
- DEFER unless support tickets are promised at launch

### /admin/user-stats

Access:
- admin
- owner

Launch requirement:
- real user/account statistics only

Current state:
- styled static presentation
- no direct data fetch

Disposition:
- DEFER OR LABEL PREVIEW

### /admin/user-dashboard

Access:
- admin
- owner

Launch requirement:
- safe customer-workspace preview
- no privilege confusion

Current state:
- styled preview page

Disposition:
- OPTIONAL

---

## DEVELOPER WORKSPACE

### /dashboard

Access:
- developer
- owner

Launch requirement:
- runtime status
- architecture graph
- observability
- market services
- controlled learning/replay visibility
- developer Neuro tools

Current state:
- globally restyled
- existing workspace tabs preserved
- no direct page fetches because hooks/components own data access

Disposition:
- INTERNAL — VERIFY EACH TAB
- NOT A CUSTOMER LAUNCH BLOCKER

---

## PUBLIC WORKSPACE

### /

Access:
- public

Launch requirement:
- product explanation
- simulation-only disclosure
- login and registration links
- no misleading live-trading claims

Current state:
- styled marketing page
- no unresolved internal links

Disposition:
- LAUNCH READY AFTER COPY REVIEW

### /login

Access:
- public

Current state:
- functional
- Playwright qualified

Disposition:
- READY

### /register

Access:
- public

Current state:
- functional
- backend registration qualified

Disposition:
- READY AFTER PLAYWRIGHT REGISTRATION COVERAGE

---

# Final role boundary

## user

Can access:

- /user/dashboard
- /user/chat
- /user/settings
- /change-password when required

Cannot access:

- /admin
- /dashboard

## admin

Can access:

- /admin
- administrative subpages

Customer workspace access must be explicitly decided.

Cannot access:

- /dashboard unless also developer/owner

## developer

Can access:

- /dashboard

Administrative access must be explicitly decided.

## owner

Can access:

- /dashboard
- /admin

Customer-preview behavior must remain explicit.

---

# Launch implementation order

1. User dashboard real data and paper-trading workspace
2. User settings minimum viable account controls
3. Admin user-management browser qualification
4. Admin sessions and audit real read-only data
5. Role/access Playwright suite
6. Deployment, backup, rollback, monitoring
7. Defer tickets, aggregate statistics, and nonessential previews if unfinished

---

# Definition of done

A page is launch-ready only when:

- its correct role can access it
- unauthorized roles cannot access it
- displayed data is real or clearly labeled unavailable
- actions work end to end
- loading, empty, and error states exist
- Playwright covers the primary workflow
- TypeScript, lint, build, and tests pass
