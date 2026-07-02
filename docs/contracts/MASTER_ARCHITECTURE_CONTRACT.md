# NeuroVest Master Architecture Contract

## Purpose

NeuroVest is a local-first fintech, AI, research, portfolio analysis, and paper-trading platform.

It must be built top-down, stack-first, layer-isolated, contract-driven, test-certified, and safety-locked.

## Starting Mode

NeuroVest starts as:

```text
Research + portfolio analysis + paper trading only

Forbidden at start:

No live trading
No broker orders
No autonomous real-money execution
No AI self-mutation
No hidden runtime writes
No frontend-to-broker calls
No AI-to-broker calls
No paid AI dependency
No public deployment
Layer Model
L0 External Providers
L1 Security / Safety
L2 Domain Logic
L3 Services / Facades
L4 Runtime Orchestration
L5 API Presentation
L6 Frontend
L7 Tests / Certification
Build Rule

Every feature must follow:

Design
Contract
Skeleton
Test Plan
Implementation
Certification
Lock

Execution comes last.
