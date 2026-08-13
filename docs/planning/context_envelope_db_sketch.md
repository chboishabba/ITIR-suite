# Context Envelope DB Sketch (Draft)

This sketch maps the Context Envelope schema to relational tables compatible
with ITIR/SL-style storage.

## Tables

### context_envelopes
- `context_id` TEXT PRIMARY KEY
- `artifact_id` TEXT NOT NULL
- `created_at` TEXT NOT NULL
- `duration_ms` INTEGER
- `sequence_index` INTEGER NOT NULL
- `sequence_group_id` TEXT
- `medium` TEXT NOT NULL
- `intended_audience` TEXT NOT NULL
- `visibility_scope` TEXT NOT NULL
- `legal_status_then` TEXT NOT NULL
- `investigative_status_then` TEXT NOT NULL
- `speaker_role` TEXT NOT NULL
- `recipient_role` TEXT NOT NULL
- `institutional_asymmetry` TEXT NOT NULL
- `source_id` TEXT NOT NULL
- `revision_id` TEXT NOT NULL

Indexes:
- `idx_context_artifact_id` on (`artifact_id`)
- `idx_context_sequence_group` on (`sequence_group_id`, `sequence_index`)
- `idx_context_created_at` on (`created_at`)

### context_known_then
- `context_id` TEXT NOT NULL
- `fact` TEXT NOT NULL
- PRIMARY KEY (`context_id`, `fact`)

### context_known_now
- `context_id` TEXT NOT NULL
- `fact` TEXT NOT NULL
- PRIMARY KEY (`context_id`, `fact`)

### context_later_discovered
- `context_id` TEXT NOT NULL
- `fact` TEXT NOT NULL
- PRIMARY KEY (`context_id`, `fact`)

### context_status_flags
- `context_id` TEXT NOT NULL
- `flag` TEXT NOT NULL
- PRIMARY KEY (`context_id`, `flag`)

### context_text_spans
- `context_id` TEXT NOT NULL
- `start_char` INTEGER NOT NULL
- `end_char` INTEGER NOT NULL
- PRIMARY KEY (`context_id`, `start_char`, `end_char`)

## Notes
- `context_id` can be derived as a hash of `artifact_id` + `revision_id` +
  `sequence_index` for deterministic IDs.
- The three fact tables preserve "known then/now/later" without overwriting.
