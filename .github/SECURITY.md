
NeuroVest Security Policy
Current security posture

NeuroVest is under active development.

The following capabilities are not approved merely because code or adapters exist:

live brokerage execution;
autonomous trading;
autonomous deployment or source mutation;
autonomous risk override;
production AI action authority.

Paper trading, simulation, and controlled development testing must remain separated from live financial execution.

Reporting a vulnerability

Do not disclose vulnerabilities through public issues, discussions, screenshots, or pull requests containing exploit details.

Use GitHub private vulnerability reporting when available.

Include:

affected component and route;
reproduction conditions;
expected and observed behavior;
authentication level required;
potential financial, privacy, availability, or AI-safety impact;
logs or evidence with secrets removed;
suggested mitigation, when known.
Sensitive information

Never include:

plaintext passwords;
JWT secrets;
raw access or refresh tokens;
database credentials;
broker credentials;
API keys;
private customer or portfolio data;
production configuration secrets.

Revoke or rotate exposed credentials immediately.

Priority areas

Highest-priority boundaries include:

authentication, authorization, session rotation, or revocation;
administrative or owner-role escalation;
live-versus-paper execution separation;
risk-gate or kill-switch bypass;
order duplication, replay, or idempotency failure;
ledger or audit-record tampering;
prompt injection leading to unauthorized tool use;
model-context or private-data disclosure;
dependency or build-chain compromise;
denial of service against public chat or financial APIs.
Supported versions

Until a formal release exists, only the current active development branch is supported.

Response process

A valid report should be:

acknowledged;
reproduced in a controlled environment;
classified by security and financial impact;
remediated with focused regression tests;
qualified against affected runtime boundaries;
documented without exposing exploitation details;
released only after required approval.

A passing test does not authorize production, live brokerage, or autonomous AI operation.
