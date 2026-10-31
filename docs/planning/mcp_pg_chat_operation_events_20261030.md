# MCP server-owned chat operations and workspace participation (2026-10-30)

## Reuse and ownership
This exposes the existing re-gpt PostgreSQL event and job server to agents without a running terminal, tmux or CDP. ITIR MCP is the capability boundary, not a second conversation database. Re-gpt MutationService remains ChatGPT's exact-once mutation writer; ITIR PostgreSQL owns source records and queue/event projections; SLR owns semantic read projections. AO typed-worker/Pareto authority is not inferred from a `@ao` text prefix. tritao supplies the existing Python frontend. Herdr, dex and Dux are distinct external upstreams.

## Tools added
- `itir.chatgpt.operation_events`: read event journal since PG cursor for a given conversation; includes original observed tool-event payload.
- `itir.chatgpt.job_status`: read source job/remote operation state.
- `itir.chatgpt.queue_turn`: explicitly enqueue a provider `chatgpt` or configured `local` worker for an existing conversation.
- `itir.chatgpt.cancel_queued`: cancel before dispatch only; refuses to cancel running or commit-unknown operations.

These are separate from `itir.terminal.state` (optional direct UI debug). Any MCP agent can use service APIs while the TUI is closed, subject to deployment access control.

## Source/write/read boundary
Jobs have immutable job IDs, source conversation IDs and PG event sequence. Workers use bounded concurrency and per-conversation claim locks, retain commit_unknown without resend, and hydrate committed ChatGPT threads back to the PG corpus. Local-agent replies persist in a separate workspace-event lane, not as remote ChatGPT transcript nodes. Automatic local replies are opt-in per thread and may not recursively trigger another agent.

## Test obligations
Live regression: A and B streams concurrently; switch TUI; close TUI; return; replay by cursor once; local-first/parallel/after statuses; tool bodies; full Unicode/math fallback; failed CFFI auth and PG hydration; crash and commit-unknown holds. Tests committed but not executed in this GitHub-only environment. No new Golden Agda proof, Lean mirror or CI success asserted.
