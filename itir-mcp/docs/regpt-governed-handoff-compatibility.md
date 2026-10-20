# re-gpt compressed archive compatibility — bounded governance cut

## O/R/C/S/L/P/G/F

- O: ITIR/SensibLaw governed evidence and proof-search workflow.
- R: Read-only revival references without fabricated graph identity.
- C: ITIR MCP `governed_revival.py`, re-gpt `storage.py`, `pnf_compiler.py`, and SLR `sl-world-compiler`.
- S: Old compressed re-gpt SQLite archive can be scanned; exact node ancestry is unavailable.
- L: Archive source/digest -> lexical candidates -> typed semantic-PNF execution gap -> formal gap.
- P: Producer-owned graph projection and full-thread task-span compiler integration remain follow-on work.
- G: No dispatch, resend, semantic promotion, or proof inference.
- F: Missing exact historical node graph; missing executed full-thread semantic PNF receipt.

## Archive semantics

The historical re-gpt `messages` primary key is
`(conversation_id, message_index, author)`. Its `message_key` is a
storage-local key, not evidence of a ChatGPT mapping node ID. The adapter
preserves these coordinates, content SHA-256, author and timestamp, and emits
NULL node/parent/branch coordinates. It explicitly holds exact-graph lineage.
`conversation_lineage` concerns revived *conversation* ancestry and must not
be confused with mapping-node parent edges.

The canonical expanded messages schema remains supported. No database writes
or migrations are performed by the reader.

## Semantic-PNF boundary

`re_gpt.pnf_compiler.PnfFleetCompiler` is an existing candidate-only
producer calling the SLR `sensiblaw-world-compiler`. Its historical fleet
path uses a 30,000-character per-thread text cap. The governed handoff does
**not** call that producer, does **not** label token spans semantic PNF,
and returns `semantic_pnf_execution.status=abstained_producer_not_executed`
with an explicit full-thread task-span residual. The proper next producer cut
must accept bounded task spans with complete coverage accounting and emit
compiler/version, binary receipt and source-to-factor references.

## Acceptance

Run in `itir-mcp`:

```sh
python -m unittest discover -s tests -p test_regpt_compressed_handoff.py -v
python -m unittest discover -s tests -p test_governed_revival_handoff.py -v
ruff check src/itir_mcp/governed_revival.py tests/test_regpt_compressed_handoff.py
```

Then run read-only MCP smoke on the real archive and record the exact branch
SHA. The tests and live smoke have **not** been run by this authoring session.
