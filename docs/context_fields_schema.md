# Context Fields Schema (read-only overlays)

Purpose: define how external fields of force (weather, market indices,
astronomy, symbolic overlays) are represented without becoming interpretive
inputs. These are time/place-aligned overlays; they never participate in
inference, alerts, or prioritisation.

## Core tables (proposed)

### context_fields
- `context_id` TEXT PRIMARY KEY (e.g., `weather:bom:2026-02-06T12Z:latlon`)
- `context_type` TEXT CHECK IN (`weather`,`market`,`astronomy`,`astrology`,`agro_ecological`,`indigenous_season`,`symbolic_overlay`)
- `source` TEXT          -- data provider or published calendar
- `retrieved_at` TEXT    -- ISO timestamp of fetch
- `location` TEXT        -- freeform or geo URI; optional for non-spatial fields
- `time_start` TEXT      -- ISO start
- `time_end` TEXT        -- ISO end (can equal start)
- `provenance` JSON      -- license, uncertainty, notes
- `payload` JSON         -- structured values (see below)
- `symbolic` INTEGER DEFAULT 0 -- 1 when intentionally symbolic (e.g., astrology)

### context_field_values (optional normalization)
- `context_id` TEXT REFERENCES context_fields(context_id)
- `key` TEXT
- `value_num` REAL
- `value_text` TEXT
- `unit` TEXT
- PRIMARY KEY (context_id, key)

### symbolic_overlays (optional for cultural lenses)
- `overlay_id` TEXT PRIMARY KEY
- `system` TEXT            -- e.g., western_tropical, indigenous_calendar_name
- `label` TEXT             -- human-readable symbol
- `time_start` TEXT
- `time_end` TEXT
- `provenance` JSON
- `notes` TEXT

## Ingest contract
- Ingest creates/updates `context_fields` only; SB core never mutates them.
- `symbolic` flag MUST be set for astrology and other non-empirical overlays.
- Weather/market/astronomy MUST include raw observed values; no derived
  behaviour or advice stored.
- Indigenous/seasonal calendars must include `source` and `authority` in
  `provenance`; no auto-mapping to Gregorian months.
- Exports dropping context MUST log loss; summaries must declare inclusion or
  exclusion of context fields.

## UI/summary guardrails (testable)
- Context fields cannot trigger alerts or reorder summaries.
- Language lint: forbid causal terms (“caused, influenced, impacted”) in context
  renderers.
- Opt-in toggles for symbolic overlays; default off.

## Open questions
- Do we want bucketed materialized views for fast timeline overlays?
- How to store multi-model Indigenous seasonal calendars without flattening?
- Should uncertainty bands be normalized (e.g., low/medium/high) across sources?
