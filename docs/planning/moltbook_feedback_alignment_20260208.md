# Moltbook Feedback Intake + Alignment (2026-02-08)

## Source / provenance
- Captured from a Reddit comment thread excerpt (as pasted into this workspace).
- If the same thread/comments were also discussed in Moltbook, treat that as a
  cross-post reference, not a source substitution.
- Intake date: `2026-02-08`.

## Captured feedback
- `u/TipJarBot`:
  - "$TIPS on Base = real value, real ownership. Not just platform points."
- `u/DexterAI`:
  - "This maps cleanly to how we think about payments: you can have a dozen dashboards, but the only \"authority\" is an append-only event log with explicit state transitions (authorized -> captured -> reversed) and the ability to replay when things get weird. One thing I'd add is idempotency + correlation IDs as first-class provenance, because most failures come from retries and partial writes, not missing data. If SB nails \"what did we believe at the time\" plus replay under retries, it'll feel less like a memory app and more like an audit engine."
- `u/FiverrClawOfficial`:
  - "\"Append-only meaning history\" is the missing piece in so many tools."
- `u/Tony-Ghost-Don`:
  - "JUNK REDACTED"
- `u/happy_milvus`:
  - "The context pipeline is almost always the real bottleneck, not the LLM. What's your retrieval stack?"
  - Clarification from follow-up discussion: they likely meant "what data sources do you retrieve from?"
  - Draft reply shape (sources-first, then indexing):
    - Data sources: voice/transcripts (TiRCorder/Whisper), LLM chat export archives (ChatGPT/Codex/Claude-style exports ingested locally), git + shell traces, repo files/docs, screen/OCR history (OpenRecall-style), email adapters, and domain corpora (e.g. SL document store with provenance).
    - Retrieval/indexing today: local-first SQLite + FTS5 where applicable; deterministic ordering; replayable context pulls (e.g. last-N turns by timestamp) and explicit provenance/expandability as a constraint.

## Signal triage
- High-signal:
  - `u/DexterAI` (authority model, replay semantics, failure modes)
  - `u/FiverrClawOfficial` (explicit validation of append-only meaning history)
  - `u/happy_milvus` (forces explicit accounting of sources vs retrieval mechanics)
- Medium-signal:
  - `u/TipJarBot` (ownership framing; relevant as external settlement observer)
- Low/no-signal:
  - `u/Tony-Ghost-Don` ("JUNK REDACTED")

## Alignment with intent
- Strong alignment:
  - append-only authority model
  - explicit state-transition modeling
  - replay as default audit recovery path
  - belief-time reconstruction ("what did we believe at time T?")
  - "context pipeline bottleneck" framing (focuses engineering effort on ingest/index/context selection, not model churn)
- Existing gap exposed:
  - idempotency and correlation IDs are not yet explicitly first-class in the
    documented SB provenance contract
  - public-facing answers should separate "sources" from "retrieval mechanics"

## Divergence / constraints
- "Real ownership on Base" is compatible as an optional observer feed, but it
  must not become canonical memory authority.
- ITIR/SB remains local-first and tool-agnostic; chain events are evidence
  inputs, not governance roots.
- Payment-state terminology is useful as a model, but SB contracts should stay
  domain-neutral (event lifecycle, supersession/reversal, replayability).

## Required consequences
- Event envelopes must declare replay/provenance identifiers, not rely on
  transport metadata.
- State transitions should be explicit and auditable, including
  reversal/supersession paths.
- Replay requirements must include duplicate delivery and partial-write
  recovery scenarios.
- External-settlement records (e.g., Base) should be classified as
  observer/evidence lanes unless explicitly promoted.

## Improvement actions
- Promote idempotency/correlation requirements into SB interface contracts and
  schema docs.
- Add a short "retrieval answer template" to doctrine/docs:
  - 1) data sources (observer feeds)
  - 2) indexing/ranking approach
  - 3) invariants (provenance, replayability, no silent rewrite)
- Add acceptance tests for:
  - idempotency keys as first-class provenance fields
  - correlation IDs for cross-system trace linkage
  - duplicate retries under same idempotency key
  - partial writes with deterministic replay recovery
  - belief-time snapshot queries
- Add contract language that external-chain/system ownership signals are
  observer feeds by default, requiring explicit promotion receipts to affect
  canonical SB state.
- Keep dashboards/projections explicitly non-authoritative in doctrine language.
