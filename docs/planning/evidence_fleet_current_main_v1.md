# Fleet convergence v1: current-main bounded cut

## Docs / TODO
- [x] Retire ordinary title-carousel CLI before transport imports.
- [x] Provide task/gap-based deterministic planner with a 2–4 proposal cap, multi-parent evidence references and independent receipt links.
- [ ] Run local Python regression suite and archive-snapshot migration validation.
- [ ] Replace legacy internal callable paths and connect incremental refresh / PNF gap adapters through existing stdio MCP authority.

## Operator contract
Run `python -m scripts.evidence_fleet_controller --db PATH --plan --limit 3` to propose work only. The command may create reference-only SQLite tables; it never sends account prompts. Conversation graphs and canonical archive remain truth. Bulk ingestion is owned by chat-export-structurer; active-thread refresh by chat-context-sync. No second scheduler, transcript store or HTTP service. Do not import legacy carousel internals for production. Account mutations must use direct async curl_cffi, no DOM fallback, and must stop on commit_unknown.

## Local verification

Run tests using discovery; the tests directory is not an importable package:

```bash
python -m unittest discover -s tests -p 'test_evidence_fleet_controller.py' -v
python -m unittest discover -s tests -p 'test_legacy_fleet_fail_closed.py' -v
```

Independent archive verification reported six planner tests passing and one legacy diagnostic assertion failing before this correction. The amended assertion still requires local rerun; no test execution is claimed here.

## Changelog
- Added bounded evidence-first planner and focused tests on current main.
- Retired ordinary legacy daemon CLI; no automatic title-keyword dispatch through its entrypoint.
- No formal proof promotion or authenticated ChatGPT acceptance claimed.
