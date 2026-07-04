
# NEUROVEST ARCHITECTURE GUARANTEE (LOCKED)

## LAYER RULES

### L3 (Facade Layer)
- ONLY exposes stable APIs
- MAY call L4
- MUST NOT import L5
- MUST NOT perform tracing
- MUST NOT mutate files
- MUST remain import-safe

### L4 (Runtime / Domain Layer)
- CORE business logic only
- MUST NOT import L3
- MUST NOT import L5
- MUST NOT contain CLI logic
- MUST NOT contain tracing
- MUST be pure + testable

### L5 (CLI / Observability Layer)
- MAY import L3
- MAY wrap calls with tracing
- MUST NOT contain business logic
- MUST NOT define core algorithms

---

## FORBIDDEN PATTERNS

- Circular imports across layers
- Facade importing trace modules
- Runtime importing CLI modules
- Any file rewriting itself
- Any "self-healing" that modifies production logic silently

---

## ALLOWED DEPENDENCY FLOW

L5 → L3 → L4

NEVER reverse direction.

---

## DRIFT DEFINITION

Drift occurs when:
- Any layer imports upward
- Any circular dependency exists
- Any runtime mutation occurs without explicit approval

