# Bounded canonical archive → PNF work packet v1

## Contract / TODO — before implementation

The sole corpus authority is the structured SQLite archive at `~/chat_archive.sqlite` (override `ITIR_CANONICAL_CHAT_ARCHIVE`). `~/.chatgpt_history.sqlite3` is operational cache only. Read canonical `messages.text` in bounded, selected windows; never put message text in source refs, packets or receipt tables. Packet identities are deterministic digests of selectors, selected source digests, evidence and policy. PNF output is candidate-only and not semantic proof or task promotion. Explicit truncation receipts are mandatory. Do not require PostgreSQL: reference-source projection is local in memory with an explicit unavailable PG adapter. AO may compose worker briefs from packets and repository state, without full-thread reads. No autonomous dispatch.

TODO:
- [ ] Implement strict archive schema gate, bounded tail selection, SHA-256 references and receipt projection.
- [ ] Implement source-linked lightweight candidate PNF units with abstentions, without duplicating SLR parsing authority.
- [ ] Add capped MCP tool and fixture tests; execute locally where possible.
- [ ] Record delivered behavior, test receipt and remaining producer/PG integration gap.

## Delivered — candidate-only v1

`itir-mcp/src/itir_mcp/pnf_work_packet_provider.py` opens the canonical archive read-only and strictly checks the 25 production `messages` columns. It tail-selects at most 40 messages and 24,000 text characters per thread by default (hard ceilings 200 messages / 100,000 characters); at most eight threads per call. Packet JSON defaults to a 24,000-character ceiling, hard ceiling 100,000. On overflow it removes **derived candidate units from the tail** and records `packet_budget_truncated` plus the number removed; if source references alone exceed the ceiling, it fails closed. No source body is serialized.

The lightweight extraction contract is deliberately narrow: a selected message with matching bounded vocabulary (`lemma/theorem/proof/formal/agda/lean/gap/TODO/blocked/implement/PR #n`) contributes **unverified lexical candidate kinds**, linked to a canonical message reference. This is **not** SLR semantic PNF parsing and must not be treated as proof, task promotion or equivalent-claim detection. The existing `itir.pnf.task_memory_preview` and `itir.pnf.observer_evidence` remain independent producer-facing interfaces; no new parser authority is asserted. Each packet carries deterministic `packet_id`, digest-checked locator coordinates, ledger evidence receipts, selected/total counts and truncation flags, and an in-memory `local_reference_only` projection receipt. The PostgreSQL adapter explicitly raises `NotImplementedError`; no PostgreSQL connection is made or required.

The tool `itir.pnf.work_packet` is registered through existing `get_pnf_tools` and `build_default_registry` with `additionalProperties: false`. It is read-only, candidate evidence only. AO can compose a worker brief from task atom, source references, candidate kinds and evidence receipts without reading the whole transcript; any deeper SLR/PNF parse must be separately selected and attributed.

### Local validation commands

```bash
python -m unittest discover -s tests -p 'test_pnf_work_packet_provider.py' -v
ruff check itir-mcp/src/itir_mcp/pnf_work_packet_provider.py itir-mcp/src/itir_mcp/pnf_tools.py tests/test_pnf_work_packet_provider.py
PYTHONPATH=itir-mcp/src python -c 'from itir_mcp.registry import build_default_registry; print([t.name for t in build_default_registry().list_tools()])'
```

**Execution receipt:** pending local referee execution. GitHub connector edits were made without a runnable local repository checkout; no test/ruff success is claimed, no CI or Colab invoked.

**Remaining gaps:** real SLR selected-span parser composition, persistent local projection receipts (the current receipt is in-memory), formal comparison/gap producer joins, source-content verification against external archive snapshots, and downstream 500-thread AO routing integration. No PG startup, raw transcript duplication, autonomous dispatch, browser or mutation.

## Referee fix — production MCP import isolation

Moved the complete provider implementation to `itir-mcp/src/itir_mcp/pnf_work_packet_provider.py` and changed `pnf_tools.pnf_work_packet` to use `from .pnf_work_packet_provider import build_work_packet`. The package now resolves its own `canonical_archive_path` without importing `scripts.canonical_candidate_ledger`. The obsolete repo-root provider was deleted. This removes both imports that failed under the production `cwd=itir-mcp; PYTHONPATH=src` configuration. The new subprocess fixture test invokes the registered MCP tool from that cwd with the package source as its only explicit PYTHONPATH, using a temporary real-schema canonical SQLite archive.

Local referee previously verified 5/5 tests and the registry before this correction. **Post-correction tests, Ruff, and real-archive MCP smoke call are not executed by this GitHub connector**; these remain pending and are not claimed green.

```bash
python -m unittest discover -s tests -p 'test_pnf_work_packet_provider.py' -v
ruff check itir-mcp/src/itir_mcp/pnf_work_packet_provider.py itir-mcp/src/itir_mcp/pnf_tools.py tests/test_pnf_work_packet_provider.py
(cd itir-mcp && PYTHONPATH=src python -c "from itir_mcp.registry import build_default_registry; r=build_default_registry().invoke('itir.pnf.work_packet', {'proposals':[{'canonical_thread_id':'6825e290-f1bc-8002-9e5a-73b675157c0c','task_atom':'smoke'}]}); print(r); assert r['ok'] and r['result']['packets'][0]['source_refs']")
```

No CI, browser, mutation, resend, or production archive write.

## Referee round 2 — FastMCP transport artifact

The production stdio call reached the registry but failed the strict field allowlist because FastMCP injects a reserved `kwargs` field. The shared `itir_mcp.server._register_fastmcp_tool` wrapper now removes `kwargs` **after** merging `arguments` and before invoking any registered handler. This corrects the transport/handler boundary for every strict tool without relaxing unknown-field validation.

Added a regression test that registers `itir.pnf.work_packet` through the actual `_register_fastmcp_tool` wrapper on a capture server and invokes the resulting function with `arguments=...`, `kwargs={}`. It checks successful nonempty source refs and rejection of a genuine unexpected field. The fixture does not require the optional FastMCP transport package or a live archive.

**Post-fix validation pending referee execution** (GitHub connector cannot execute local repository commands):

```bash
python -m unittest discover -s tests -p 'test_pnf_work_packet_provider.py' -v
ruff check itir-mcp/src/itir_mcp/server.py itir-mcp/src/itir_mcp/pnf_tools.py itir-mcp/src/itir_mcp/pnf_work_packet_provider.py tests/test_pnf_work_packet_provider.py
```

Full stdio smoke to be re-run by the referee with `cwd=itir-mcp`, `PYTHONPATH=src`, and `tools/call` arguments plus `kwargs={}`. Expected result is `ok:true` and nonempty `source_refs`; this has **not** been observed in this session. No CI, browser, mutation, or production write.
