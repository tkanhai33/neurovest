# NeuroVest Launch Candidate

## Candidate identity

- Candidate date: 2026-08-01
- Local freeze time: 2026-08-01T14:46:37-06:00
- UTC freeze time: 2026-08-01T20:46:37+00:00
- Branch: `unified-frontend-design-20260725_152222`
- Candidate source HEAD before manifest commit: `b8e839f43b800021b729391fd19cbb646fed27b1`
- Qualified auth recovery commit: `b8e839f43b800021b729391fd19cbb646fed27b1`
- Launch mode: controlled early-user, paper-only
- Live broker execution: not approved
- Production broker execution: not approved

## Qualified objectives

### Objective 5A — Simulated 10-user controlled launch

- Result: PASS
- Simulated users: 10
- Passed users: 10
- Failed users: 0
- Summary: `runtime/launch_candidate/objective_5a_rerun_20260801_141108/summary.json`
- Console evidence: `runtime/launch_candidate/objective_5a_console_20260801_141107.txt`

### Objective 5B — Service restart and existing-user recovery

- Result: PASS
- Existing users recovered: 10/10
- Evidence directory: `runtime/launch_candidate/objective_5b_restart_recovery_20260801_141626`

### Objective 5C — Database backup and restore

- Result: PASS
- PostgreSQL version: 15.18
- Public tables restored: 14
- Simulated accounts restored: 5/5
- Simulated accounts active after restore: 5/5
- Live database replaced or dropped: no
- Temporary restore database removed: yes
- Backup: `runtime/launch_candidate/objective_5c_container_restore_20260801_142920/neurovest_20260801_142920.dump`
- Backup SHA-256: `f9e60cf2b971539ef2797d5c1369eb9557f516c6aefaceb5506e02a7f7841fe5`
- Qualification report: `runtime/launch_candidate/objective_5c_container_restore_20260801_142920/qualification.txt`
- Account manifest: `runtime/launch_candidate/objective_5c_container_restore_20260801_142920/accounts.json`
- Archive listing: `runtime/launch_candidate/objective_5c_container_restore_20260801_142920/archive_contents.txt`
- Restore log: `runtime/launch_candidate/objective_5c_container_restore_20260801_142920/restore.log`

## Runtime qualification

- Backend OpenAPI: HTTP 200
- Frontend: HTTP 200
- Ollama API: HTTP 200
- PostgreSQL readiness: PASS
- PostgreSQL container: `neurovest_postgres`

### Ollama placement at freeze

```text
NAME    ID    SIZE    PROCESSOR    CONTEXT    UNTIL 
```

## Previously frozen qualifications

- Canonical RAG commit: `a062919a9b09e07b7464d834e5d827c7f1437887`
- Canonical RAG tag: `neurovest-canonical-rag-qualified-20260801_125626`
- Model provenance commit: `c077467dc835bd1003d754f9a033fc9f198eb992`
- Model provenance tag: `neurovest-model-provenance-qualified-20260801_133354`
- Safe backend launcher commit: `7056c2f6ef335fe25f65f6d84f7895586fc1f568`
- Safe backend launcher tag: `neurovest-backend-launcher-qualified-20260801_134114`

## Launch boundaries

This candidate remains restricted to:

- controlled early-user access;
- research and grounded conversational use;
- simulation and paper-trading boundaries;
- read-only brokerage connectivity where separately qualified;
- no live order execution;
- no production broker authorization;
- no uncontrolled public launch authorization.

## Evidence integrity

Runtime evidence is intentionally not committed because the `runtime/`
directory contains local qualification artifacts and may contain sensitive
operational data.

Evidence file checksums were captured during the freeze under:

`runtime/launch_candidate/objective_5d_launch_candidate_freeze_20260801_144635/evidence_sha256.txt`

The PostgreSQL backup checksum is:

`f9e60cf2b971539ef2797d5c1369eb9557f516c6aefaceb5506e02a7f7841fe5`
