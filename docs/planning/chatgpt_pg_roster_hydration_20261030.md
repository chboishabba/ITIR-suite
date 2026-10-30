# PostgreSQL-first ChatGPT roster and hydration MCP continuation (2026-10-30)

## Ownership and invocation
ITIR MCP is an agent-facing adapter to re-gpt's shared PG-backed catalog and explicit read-only remote graph acquisition. The terminal is **not** a prerequisite. No tmux, UI control socket or browser DOM is required. SLR owns production semantic interpretation, the existing ITIR PostgreSQL corpus owns durable source records and work queue, DASHI Agda contracts remain formal authority, and SensibLaw is deprecated reference only.

Tools:
- Read-only: `itir.chatgpt.pg_search` (hydrated corpus pagination), `itir.chatgpt.pg_roster_list` (bounded PG roster+corpus union), `itir.chatgpt.pg_read` (message bodies + provenance).
- PG mutations/network reads: `itir.chatgpt.pg_roster_sync` (fetch roster pages and persist identities), `itir.chatgpt.pg_hydrate_selected` (fetch one exact graph and persist), `itir.chatgpt.pg_hydrate_pending` (bounded explicit queue worker).

The new queue is `ops.chat_hydration_roster`. This is not a new canonical chat content store; source message bodies remain in existing `corpus.chat_archive_message` and its content-addressable ancestry. The queue distinguishes `queued`, `hydrated`, and `error`, with attempt counts and typed error records.

## Delivery and honest limitations
No background work runs inside ITIR MCP by itself. The TUI currently starts a best-effort daemon thread on roster load; MCP clients can explicitly call a bounded worker pass. For restart-persistent scheduling use the existing suite/AO scheduler; do not claim a thread constitutes durable execution. Exact JSON tool records, branch revisions, PostgreSQL schema/constraint acceptance, and reactive picker updates still need review. The content import rejects existing message identities with conflicting source revisions rather than silently replacing source bodies.

Do not merge this as verified production ingestion until tests exercise a real PostgreSQL transaction and the SLR production source-store equivalence is established. The prior live 35-conversation and 7-message read check does not establish ingestion correctness.
