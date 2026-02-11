# Chat Context Resolver: Online IDs + Local Fallback (2026-02-10)

## Problem
We routinely get "online IDs" that look like:

- `698ac6a3-c56c-839a-b855-47822ac1a901`

These are **ChatGPT conversation IDs** (UUIDs).

But `chat-export-structurer/my_archive.sqlite` is keyed by:

- `messages.canonical_thread_id` (an internal canonical ID, typically a hash-like string)

and an online UUID will not match `canonical_thread_id` unless we also store an
upstream ID in the archive.

## Intended Behavior (Option 1: implement now)
`scripts/chat_context_resolver.py` should support online UUID selectors without
requiring a live ChatGPT session by consulting local chat export caches first.

Resolution order:

1. Structurer DB (`chat-export-structurer/my_archive.sqlite`)
   - `source_thread_id` exact (when upstream IDs exist in `messages`)
   - `canonical_thread_id` exact
   - title exact / title contains
   - FTS candidates (for human keywords, not for UUID selectors)
2. Local chat export DBs (`chat_exports/backups/*chatgpt_history_*.sqlite3`)
   - match `conversations.conversation_id` exactly
   - if found: emit title + last_seen + message count and a small recent snippet
3. Live fallback (`re-gpt --view`) only when explicitly configured
   - requires `CHATGPT_SESSION_TOKEN` or `~/.chatgpt_session`

This keeps `$robust-context-fetch` "DB-first" while making online IDs usable in
environments where web access and session tokens are unavailable.

## Why UUIDs Must Not Stop At FTS Candidates
UUIDs like `69882c94-3094-839a-b539-15529d7e9c6c` are a terrible input for FTS:
they tokenize into short hex chunks that match unrelated tool logs.

So for UUID selectors:
- do not treat FTS candidates as a "successful" DB-first outcome
- try local `chat_exports` mapping
- then (if configured) try web fallback

## Operator Runbook
If an online ID does not resolve:

1. Check whether local chat export backups are current.
   - If not, run the chat export sync job (chat-context-sync) to refresh
     `chat_exports/backups/*chatgpt_history_*.sqlite3`.
2. If you need the thread in `my_archive.sqlite` as canonical truth:
   - run the structurer ingest pipeline on the relevant exports and retry.
3. If you need live messages right now:
   - provide a valid ChatGPT session token and use web fallback.

## Notes From A Real Thread (Example)
Thread `69882c94-3094-839a-b539-15529d7e9c6c` is referenced in:
- `__CONTEXT/COMPACTIFIED_CONTEXT.md` (frontend direction)
- `StatiBaker/docs/svelte_migration_sprint.md` (SB migration plan)

Even if the UUID cannot be resolved locally, the load-bearing outcome can still
be captured in repo docs, and later reconciled into the archive when exports are
ingested.

## Why Not Option 2 (store conversation_id in my_archive.sqlite) Yet
We likely *should* store stable upstream IDs in the structurer archive, e.g.:

- `source_conversation_id` (ChatGPT conversation UUID)
- `source_message_id` (platform message IDs)

Pros:
- Deterministic mapping from online ID -> canonical_thread_id without additional DBs.
- Better provenance/cross-tool interop.

Cons:
- Requires a schema + ingest change in `chat-export-structurer`.
- Forces us to define "canonical" across platforms sooner than necessary.

Decision posture:
- Document the case for Option 2, but implement Option 1 first (local fallback +
  clearer operator guidance).

Update (2026-02-10):
- We implemented the minimal schema support in `chat-export-structurer` as nullable
  columns:
  - `messages.source_thread_id` (ChatGPT "online ID" / conversation UUID)
  - `messages.source_message_id` (upstream per-message ID, when available)
  and updated ingest to upsert these opportunistically (allowing nulls so old DBs
  remain valid).
- We also implemented a persistence fallback path: if `re-gpt --download` times out,
  the resolver can capture the conversation via SyncChatGPT and emit a synthetic
  `resolver_live_v1` export (ingested with `--format resolver_live`).

Update (2026-02-10, later):
- Resolver persistence now **defaults to live capture**, and only attempts
  `re-gpt --download` as a last-resort fallback if live capture fails to run.

Update (2026-02-10):
- `--web-timeout` now bounds both subprocess web fallbacks and the SyncChatGPT
  live-capture path (best-effort via SIGALRM on POSIX) to avoid "hangs" with no output.

Update (2026-02-11):
- Verified live resolution for online ID
  `698c1cec-51c0-839a-a81b-c821aa4eabbb` using:
  `timeout 60 .venv/bin/python scripts/chat_context_resolver.py "<id>"`
- Result source was `web` (DB miss), and the resolved thread title was
  `Browne v Dunn Parsing`.
- Action taken: recorded the thread in `__CONTEXT/convo_ids.md` and captured
  ingest implications in:
  `docs/planning/legal_principles_ingest_bootstrap_au_20260211.md`.
