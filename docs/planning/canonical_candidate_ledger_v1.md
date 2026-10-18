# Canonical archive-first AO candidate ledger v1

## Contract / TODO before code

AO selects from explicit canonical structurer archive coordinates and durable PNF/task/repo/formal receipts, **never** from re-gpt operational history or title/turn-count carousel. The default archive locator is `~/chat_archive.sqlite`; `~/.chat_archive.sqlite` must be selected explicitly and is not silently merged. Same task atom plus equivalent evidence converges to one survivor. Ambiguous overlap is parked for review, not merged automatically.

`active` means an outstanding ChatGPT implementation operation awaiting a canonical receipt. It is not the number of local response-processing workers (default 20). Submission pacing follows adapter health/cooldown and ITIR governed worker authorization; no mutation or resend is implemented here.

TODO: [ ] implement canonical candidate ledger; [ ] feed formal gap and task evidence into explicit selectors; [ ] link governed AO worker receipts; [ ] local tests. No daemon or CI.

## Delivered (2026-10-18)

`scripts/canonical_candidate_ledger.py` verifies explicit candidate thread IDs against canonical structurer `messages.canonical_thread_id` via a read-only SQLite connection, and ranks only supplied task/formal/repo/PNF evidence. It records admit/merge/park/retire reasons and exact survivor identity, excluding generic chat, personal/admin and vague ideation unless explicitly promoted. `active_outstanding_operations` is counted separately from `local_response_workers_default=20`; there is no cap on active receipts. No re-gpt cache query or mutation is performed.

**Known gaps:** ledger is a pure projection and is not yet connected to the governed `itir.ao.*` dispatch/health/cooldown controller. It does not infer task atoms or evidence from raw chat, nor implement revival policy or source-digest joins. The retired legacy carousel is not reenabled. Formal gaps are first-class explicit receipt inputs, not title keywords.

Local verification:
```bash
python -m unittest discover -s tests -p 'test_canonical_candidate_ledger.py' -v
```
