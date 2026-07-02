# Phase 12 AI Chat Skeleton Contract

## Status

Phase 12 skeleton only.

## Purpose

Create the AI chat stack shape without implementing real model calls, RAG, memory, tool execution, runtime orchestration, broker interaction, trading advice, or business logic.

## Allowed

- chat message contract
- chat session contract
- AI tool request contract
- Ollama placeholder adapter
- skeleton denial service
- status service
- API placeholder
- tests
- certification artifact

## Forbidden

- real Ollama calls
- model inference
- RAG implementation
- memory implementation
- tool execution
- runtime execution
- broker interaction
- order placement
- trading advice implementation
- business logic

## Default State

- Ollama adapter implemented: false
- model calls enabled: false
- RAG implemented: false
- memory implemented: false
- tool use implemented: false
- runtime integration implemented: false
- broker integration implemented: false
- trading advice implemented: false

## Exit Criteria

- tests pass
- ai_chat stack has contracts/services/api/adapters placeholders
- all tool requests denied by skeleton
- no model calls exist
- no broker/runtime execution exists
