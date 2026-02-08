# Chat Artifact Capture Contract (2026-02-08)

## Purpose
Define how ITIR captures assistant-generated artifacts from non-codex ChatGPT
threads (files, runnable snippets, and execution claims) as first-class,
replayable evidence.

This is a planning/contract artifact only.

## Evidence (DB scan)
Source: `chat-export-structurer/my_archive.sqlite`, `platform='chatgpt'`,
`role='assistant'`.

- Messages with `sandbox:/mnt/data/` download links: `121`
- Messages with explicit "I ran ...": `33`
- Messages with `Traceback`: `37`
- Messages with code-fence markers (`python|md|bash`): `3661`
- File-style language (`save as`, `.py`, `.md`, heredoc): present and repeated
  across multiple threads

Top artifact-heavy threads include:
- `53a59124...` (`Branch · Topology and MDA/MDL`)
- `e40d17da...` (`Compare 3-6-9 with TL`)
- `01e9e9e5...` (`Shrikhande graph plot`)
- `ea0e0d53...` (`Branch · Visualising Collapse and Sparsity - RTX - light transport`)

Phrase sweep (chatgpt-only subset):
- `failure mode(s)`: `393`
- `control polic*`: `8`
- `test gate*`: `3`
- `compression*`: `1024`
- `dedupe*`: `309`
- `idempotency*`: `54`

Additional high-signal search terms for follow-up:
- `provenance`
- `replay`
- `append-only`
- `ed25519`
- `merkle`
- `cid`

## Artifact Classes
1. `download_link_artifact`
- Trigger: `sandbox:/mnt/data/<filename>` URL in assistant text.
2. `inline_file_artifact`
- Trigger: explicit file emission pattern (`save as *.py|*.md`, heredoc blocks,
  fenced code with filename context).
3. `execution_claim_artifact`
- Trigger: explicit run/execution language (`I ran`, `output:`, `traceback`).
4. `mixed_artifact`
- Trigger: message includes file artifact + execution claim.

## Canonical Record
Each extracted artifact record MUST include:

- `artifact_capture_id` (stable UUID)
- `message_id`
- `canonical_thread_id`
- `ts_utc`
- `platform`
- `artifact_class`
- `artifact_locator` (URL, filename hint, or message-local locator)
- `artifact_label` (best-effort display name)
- `artifact_hash` (hash of canonicalized capture payload)
- `idempotency_key`
- `payload_hash`
- `correlation_id` (thread-level)
- `causation_id` (message-level, when known)
- `capture_method_version`
- `provenance` (query/source metadata)

## Idempotency and Dedupe Rules
Apply shared suite rule:

- same `idempotency_key` + same `payload_hash` -> no-op
- same `idempotency_key` + different `payload_hash` -> hard conflict

Recommended key shape:
- `chat_artifact::<platform>::<message_id>::<artifact_class>::<artifact_locator_hash>`

## Capture Flow
1. Query archive (`messages`) for artifact triggers.
2. Normalize/extract candidate artifacts from message text.
3. Emit deterministic artifact records to an append-only JSONL sink.
4. Emit a capture receipt containing:
- extractor version
- query fingerprint
- input DB file hash/mtime
- output file hash
5. Make records available to SB as observer inputs only (non-authoritative until
   promoted).

## Promotion Boundary
- Raw chat artifact captures are observer-class by default.
- Any promotion into authoritative interpretive/state lanes requires promotion
  receipts and provenance retention.
- If artifacts touch Indigenous context or community knowledge, apply
  `docs/planning/indigenous_data_sovereignty_connector_guardrails_20260208.md`
  before promotion.

## Required Tests/Gates
1. Fixture test: detect `sandbox:/mnt/data/*.py` and `.md` links.
2. Fixture test: detect inline file emission patterns (`save as`, heredoc).
3. Fixture test: detect execution claims and attach to same message artifact.
4. Idempotency replay test (no-op).
5. Conflict test (same key, altered payload).
6. Contract schema test for canonical record fields.

## Open Decisions
- Whether to store extracted artifact payload snippets or only locators + hashes.
- Whether codex-platform assistant artifacts should share the same collision
  domain or a separate one.
- Whether capture output should be written under `StatiBaker/runs/.../logs/` or
  under a dedicated suite-level artifact ledger path.
