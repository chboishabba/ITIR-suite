# Bounded canonical archive → PNF work packet v1

## Contract / TODO — before implementation

The sole corpus authority is the structured SQLite archive at `~/chat_archive.sqlite` (override `ITIR_CANONICAL_CHAT_ARCHIVE`). `~/.chatgpt_history.sqlite3` is operational cache only. Read canonical `messages.text` in bounded, selected windows; never put message text in source refs, packets or receipt tables. Packet identities are deterministic digests of selectors, selected source digests, evidence and policy. PNF output is candidate-only and not semantic proof or task promotion. Explicit truncation receipts are mandatory. Do not require PostgreSQL: reference-source projection is local in memory with an explicit unavailable PG adapter. AO may compose worker briefs from packets and repository state, without full-thread reads. No autonomous dispatch.

TODO:
- [ ] Implement strict archive schema gate, bounded tail selection, SHA-256 references and receipt projection.
- [ ] Implement source-linked lightweight candidate PNF units with abstentions, without duplicating SLR parsing authority.
- [ ] Add capped MCP tool and fixture tests; execute locally where possible.
- [ ] Record delivered behavior, test receipt and remaining producer/PG integration gap.
