# Chat archive storage roles v1

## Decision

`~/chat_archive.sqlite` is the sole canonical chat corpus. Its structured
`messages` records, canonical-thread coordinates, provenance and hydration
receipts are the source for archive retrieval, evidence selection and bounded
handoff.

`~/.chatgpt_history.sqlite3` is re-gpt's operational store. It contains
adapter and mutation state, not canonical corpus authority. A governed MCP
lookup may read bounded receipt fields only after resolving exactly one
canonical `source_thread_id`; it must not select corpus candidates, return
transcript bodies, or authorize a resend.

`~/.chat_archive.sqlite` is a historical archive location. It remains an
operator-selected legacy source and is never silently chosen, moved or merged.
Derived frontier roster and transition receipts are stored separately from both
the canonical corpus and re-gpt operations.

## Migration rule

The only permitted cross-store materialization is a reviewed one-way backfill:
read a selected operational source, ingest compatible rows into the canonical
archive, and retain source identity/digest hydration receipts. Conflicts are
recorded rather than overwriting canonical text. This is not a SQLite database
merge.

## Deprecation plan

1. Change every governed transport-receipt caller to require an explicit
   locator or a dedicated configuration variable.
2. Keep the locator read-only and receipt-bounded; no corpus queries may fall
   back to it.
3. Audit and retire the legacy title/browser fleet daemon path.
4. Only after those callers no longer rely on the default path, rename or
   archive `~/.chatgpt_history.sqlite3` and make selection of the old name fail
   closed.

The database is deliberately not renamed in this tranche: current bounded
receipt tools still declare it as their fallback, so renaming it now would turn
an intentional migration into an uncontrolled outage.
