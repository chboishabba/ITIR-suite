# Chat Context Resolver Shell Finish

Date: 2026-03-31

## Change Class

Standard change.

## Problem

After the resolver flow extraction, the entrypoint was close to the intended
shape but still kept two residual shell concerns inline:

- parse plus runtime-resolution error handling in `main()`
- mixed plaintext rendering branches in one formatter entrypoint

That is small debt, but it still leaves the script less obviously a pure
composition wrapper than it should be.

## Requirement

- keep `scripts/chat_context_resolver.py` as a pure composition wrapper
- move parse/runtime handoff into the CLI helper
- split plaintext rendering by source branch while preserving the public print
  entrypoint
- do not move analysis, DB, live-provider, or flow semantics again

## Promoted Slice

- add a cohesive parse-and-runtime helper in
  `chat_context_resolver_lib/cli.py`
- split db/web/error plaintext rendering in
  `chat_context_resolver_lib/formatters.py`
- reduce `main()` to:
  - parse/runtime handoff
  - flow dependency wiring
  - flow call
  - print
  - exit code

## Acceptance

- `chat_context_resolver.py` reads as a composition wrapper
- output payload semantics remain unchanged
- db, web, and error plaintext branches are directly covered

## Quality Gate

Run from repo root:

- `pytest tests/test_chat_context_resolver_analysis.py tests/test_chat_context_resolver_db_lookup.py tests/test_chat_context_resolver_live_provider.py tests/test_chat_context_resolver_cli_formatters.py tests/test_chat_context_resolver_flow.py -q`

## C4 / PlantUML

```plantuml
@startuml
title Chat Context Resolver Shell Finish

Component(script, "chat_context_resolver.py", "CLI entrypoint")
Component(cli, "cli.py", "Parse/runtime handoff")
Component(flow, "flow.py", "Resolver flow owner")
Component(formatters, "formatters.py", "Output formatting")

Rel(script, cli, "parses args and resolves runtime")
Rel(script, flow, "delegates resolver flow")
Rel(script, formatters, "prints result")

@enduml
```
