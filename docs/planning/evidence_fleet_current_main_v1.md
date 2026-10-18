# Fleet convergence v1: current-main bounded cut

## Docs / TODO
- [x] Retire ordinary title-carousel CLI before transport imports.
- [x] Provide task/gap-based deterministic planner with a 2–4 proposal cap, multi-parent evidence references and independent receipt links.
- [ ] Run local Python regression suite and archive-snapshot migration validation.
- [x] Retire legacy internal callable dispatch paths with an import-safe exception boundary.\n- [ ] Connect incremental refresh / PNF gap adapters through existing stdio MCP authority.

## Operator contract
Run `python -m scripts.evidence_fleet_controller --db PATH --plan --limit 3` to propose work only. The command may create reference-only SQLite tables; it never sends account prompts. Conversation graphs and canonical archive remain truth. Bulk ingestion is owned by chat-export-structurer; active-thread refresh by chat-context-sync. No second scheduler, transcript store or HTTP service. Legacy carousel imports and all former public scheduling, lifecycle and advancement routes now raise `LegacyCarouselRetired` without importing MutationService. No legacy read-only API is retained because its lifecycle decisions were coupled to dispatch. Account mutations must use direct async curl_cffi, no DOM fallback, and must stop on commit_unknown.

## Local verification

Run tests using discovery; the tests directory is not an importable package:

```bash
python -m unittest discover -s tests -p 'test_evidence_fleet_controller.py' -v
python -m unittest discover -s tests -p 'test_legacy_fleet_fail_closed.py' -v
```

Independent archive verification reported six planner tests passing and one legacy diagnostic assertion failing before this correction. The amended assertion still requires local rerun; no test execution is claimed here.

## Changelog
- Added bounded evidence-first planner and focused tests on current main.
- Retired ordinary legacy daemon CLI and callable orchestration methods; no title-keyword dispatch, retry, DOM fallback or account mutation remains in this module.
- No formal proof promotion or authenticated ChatGPT acceptance claimed.

## Read-only exact-ID lifecycle cut

`refresh_work_evidence(db, work_id, canonical_conversation_uuid, provider)` is an explicitly invoked, non-dispatching operation. The injected `provider(uuid)` is called once per invocation and must implement accepted exact-thread refresh, incremental canonical archive ingest and PNF/exact-gap reduction *outside* this controller. It returns only nine allowlisted compact metadata fields: `receipt_ref`, `source_ref`, `source_digest`, `archive_delta`, `pnf_ref`, `gap_ref`, `gap_digest`, `gap_score`, `observed_at`. No title/FTS discovery, transcripts or network calls are performed here. The operation verifies UUID membership in the work unit, records one unique receipt per work unit and receipt ID, and projects gap score to priority without changing `state`. Stages are `refreshed → ingested → reduced → rescored` on success, or `deferred`/`failed` with error class only. Duplicate receipts are not inserted; failure details and secrets are not stored.

Reused interfaces identified: `scripts/chat_archive_batch.py` offers `select_threads` with explicit `thread_ids`, `plan_thread_chunks`, `run_status` and chunk progress/claim conventions; **do not** call its title/FTS selection or whole-run worker path from this controller. `scripts/export_chat_archive_thread.py` has canonical-thread-id read selection and read-only SQLite connection; `itir-mcp/README.md` documents read-only `itir.pnf.context_index`, `itir.pnf.task_memory_preview`, `itir.pnf.observer_evidence` and proposal receipt tools. The re-gpt README describes exact graph reads and canonical SQLite receipts, with no automatic retry of uncertain POST. The concrete stdio MCP bridge and accepted exact refresh/ingest provider remain **unwired**: never treat the injected fake as an actual integration.

TODO: [ ] Independently verify provider read-only behavior and canonical archive delta semantics; [ ] expose the adapter through stdio MCP with provenance and authority checks; [ ] separately design user-authorized direct async `curl_cffi` execution with `dom_fallback=False` and exactly-once receipt gating. No promotion from a PNF/gap score to a formal theorem.

Changelog: added exact-ID injected lifecycle receipt storage, deterministic priority re-score and deferred/failure audit facts without ChatGPT mutation.

## Exact-ID async operator adapter (explicit invocation only)

The controller CLI delegates exactly one supplied UUID to the **existing** `reverse-engineered-chatgpt/scripts/pull_to_structurer.py` using `--ids UUID --engine async --mode pull --concurrency 1 --no-skip-existing --json --no-progress`. The puller's existing identity check and chat-export-structurer canonical ingest remain authoritative. Its own subprocess runs `asyncio.run(_fetch_async(...))` once; no nested event-loop issue. The CLI requires a canonical archive DB and explicit puller path. Optional formal comparison requires **both** a formal source file and a `.slrw` world store, using `re_gpt.gap_comparator.ExactGapComparator.compare`. No formal target is inferred.

```bash
python -m scripts.evidence_fleet_controller --db /path/to/fleet_control.sqlite \
  --refresh-work WORK_ID --conversation-id CANONICAL_UUID \
  --puller /path/to/reverse-engineered-chatgpt/scripts/pull_to_structurer.py \
  --archive-db /path/to/canonical_chat_archive.sqlite --account main \
  --formal-file /path/to/explicit.agda --slrw /path/to/world.slrw
```

The puller may fetch authenticated private content into the *owned canonical archive* only. It must not be run without operator authorization. The controller records metadata only, not raw responses or tokens. Rejected/identity-invalid/transport-unavailable reads are classified as deferred; malformed receipts or comparator failures are classified as failed. There is no retry, browser, sync or mutation fallback in this adapter. **Caveat:** `archive_delta` currently reflects the puller's fetched message count, not a verified before/after inserted-row delta; archive-count semantics must be reconciled with structurer ingest statistics before treating it as a canonical delta. This is not a formal receipt or promotion gate.

TODO: [ ] Verify true archive insertion/update deltas and immutable source IDs from structurer; [ ] verify optional comparator against explicit `.slrw` and formal path; [ ] expose stdio MCP operation with authorization and receipt gates; [ ] separately implement authorized exactly-once async mutation adapter.
Changelog: added operator-invoked existing async exact-ID puller delegation and optional existing exact-gap comparator.
