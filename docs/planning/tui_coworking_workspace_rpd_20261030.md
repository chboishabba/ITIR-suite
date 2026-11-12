# Terminal co-working workspace RPD (2026-10-30)

## Attribution and UI reference correction
The user's preferred Neovim split-workspace screenshot belongs to **Herdr**; a second image of an "AI agents proper office" belongs to **Dux**. Neither is a screenshot of sumofbytes/**dex**. Do not reuse unidentified image search results as visual evidence. Inspect actual licences, communities and integration APIs before any vendoring.

## Reuse-first roles
- Herdr: optional external workspace shell, tabs, split panes, Neovim alongside agent processes. Evaluate rather than rebuild.
- dex: Rust delegated-worker execution precedent (spawn/steer/follow_up/resume_from, isolated context, approvals, background daemon). Do not confuse with Herdr or use its JSONL as canonical archive.
- tritao/chatgpt-web: existing Python TUI display; upstream source remains separately installed.
- re-gpt: authenticated network operations, SSE and operation receipts. A terminal navigation action must not own operation lifetime.
- ITIR PG: canonical conversation, archived messages, worker/operation/event/provenance/read-model state. Network roster and exact-graph reads hydrate PG explicitly.
- ITIR MCP: independent agent-facing API, no requirement for a running TUI or control socket.
- AO conductor: high-alpha Pareto/max-cut graph scheduling, scoped agent work, lineage and claims; nonpromotion until verified.
- SLR: production semantic read runtime; SensibLaw deprecated reference only.
- Golden Agda: read-only projection/nonpromotion authority; do not touch ESD surfaces.

## Live multi-chat acceptance contract
Operation {conversation_id, operation_id, seq, actor, state, source_revision_ref} determines event routing, *never* ChatTui.messages[-1].
- Launch remote A, switch client to B and dispatch B while A continues. No cancellation, duplicate dispatch, or cross-thread stream pollution.
- Persist real tool bodies and structured arguments/results when observed, without replacing them with generic activity labels. Private unavailable chain-of-thought cannot be fabricated.
- Client restart, reconnect by event cursor, replay exactly once from PG, resume subscriptions without resubmission.
- Keep Firefox-originated exact-graph revision watching from re_gpt/conversation_sync.py; no DOM scraping.
- PG owns immutable source bodies; the renderer supports rich citations/LaTeX/Markdown with original-copy fidelity.
- Local @local/@ao/@both messages belong to workspace events (not fabricated remote ChatGPT graph nodes); auto-response bounded by capacity, generation and consent.
- Conductor must distinguish source claims, observed tool results, executed tests and Agda kernel proofs.

## Work order
1. Reconcile existing re-gpt PG hydration/CFFI/session PRs and accept live PG writes.
2. Implement durable server-side operation/event queue and replay subscriptions, reuse existing re-gpt and AO operations.
3. Test two concurrent conversations, switching, reconnect, cancellation, unknown commit and tool events.
4. Complete Python TUI rich content rendering; initial Unicode fallback is not TeX typesetting.
5. Add AO agent routing and optional UI shell integration with Herdr/Neovim, after proving stable event contract.

See matching re-gpt RPD docs/python_tui_client_server_completion_rpd_20261030.md. This document is architectural and claims no new production capability or formal proof.
