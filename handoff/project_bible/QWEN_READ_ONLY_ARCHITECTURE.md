# Qwen Read-Only Architecture


QWEN READ-ONLY ARCHITECTURE

Qwen is certified only as a read-only architecture observer.

Allowed:
- read architecture state
- summarize architecture
- explain locked gates
- report missing context
- summarize disabled capabilities
- summarize certified capabilities
- inspect final context package
- inspect terminal snapshot

Forbidden:
- file writes
- patch generation
- shell execution
- runtime execution
- source mutation
- broker execution
- live trading
- recursive execution
- autonomous phase execution

Terminal state:
Qwen may read and summarize only, then stop.

