# HTTP idempotency and retries
Source: https://www.rfc-editor.org/rfc/rfc9110.html

A method is idempotent when multiple identical requests have the same intended server effect as one request. HTTP method semantics alone do not make an application POST retry-safe. For retryable non-idempotent operations, the server needs durable deduplication or equivalent operation semantics; a non-atomic check-then-process-then-save sequence can race.

