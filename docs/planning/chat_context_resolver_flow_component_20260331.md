# Chat Context Resolver Flow Component

Date: 2026-03-31

## Change Class

Standard change.

## Problem

After extracting DB lookup, live-provider, transcript, analysis, CLI, and
formatting helpers, the entrypoint still owned the DB-vs-web decision tree and
payload assembly inline in:

- `scripts/chat_context_resolver.py`

That left `main()` as a logic bucket instead of a thin CLI coordinator.

## Requirement

Create one shared Python owner for resolver flow orchestration so the script
only parses args, resolves runtime options, delegates flow, and prints the
result.

## Component Boundary

Shared owner:

- `chat_context_resolver_lib/flow.py`

First adopter:

- `scripts/chat_context_resolver.py`

Promoted slice:

- DB lookup outcome handling
- recent-turn preload and warning shaping
- DB-vs-web freshness decision tree
- cross-thread analysis routing
- thread-local analysis gating
- web fallback payload assembly
- no-web error payload assembly

## Acceptance

- `main()` becomes a thin parser/runtime/print wrapper
- DB-only, no-web, and cross-thread branches are covered by focused tests
- existing resolver analysis, DB lookup, live-provider, and CLI tests stay green

## Quality Gate

Run from repo root:

- `pytest tests/test_chat_context_resolver_analysis.py tests/test_chat_context_resolver_db_lookup.py tests/test_chat_context_resolver_live_provider.py tests/test_chat_context_resolver_cli_formatters.py tests/test_chat_context_resolver_flow.py -q`

## C4 / PlantUML

```plantuml
@startuml
title Chat Context Resolver Flow Component

Component(script, "scripts/chat_context_resolver.py", "CLI entrypoint")
Component(flow, "chat_context_resolver_lib/flow.py", "Resolver flow coordinator")
Component(db, "db_lookup.py", "DB lookup owner")
Component(live, "live_provider.py", "Live-provider adapter")
Component(formatters, "formatters.py", "Output formatting")

Rel(script, flow, "delegates resolver decision tree")
Rel(flow, db, "consumes lookup result")
Rel(flow, live, "calls web fallback and freshness checks")
Rel(script, formatters, "prints payload")

@enduml
```
