-- Context fields as non-authoritative overlays (weather, market, astronomy, symbolic)
-- Align by time/place only; never part of inference/alerts.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS context_fields (
    context_id    TEXT PRIMARY KEY,
    context_type  TEXT NOT NULL, -- weather | market | astronomy | astrology | agro_ecological | indigenous_season | symbolic_overlay
    source        TEXT,
    retrieved_at  TEXT,
    location      TEXT,
    time_start    TEXT,
    time_end      TEXT,
    provenance    JSON,
    payload       JSON,
    symbolic      INTEGER NOT NULL DEFAULT 0 CHECK (symbolic IN (0,1)),
    created_at    TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS context_field_values (
    context_id  TEXT NOT NULL REFERENCES context_fields(context_id) ON DELETE CASCADE,
    key         TEXT NOT NULL,
    value_num   REAL,
    value_text  TEXT,
    unit        TEXT,
    PRIMARY KEY (context_id, key)
);

CREATE TABLE IF NOT EXISTS symbolic_overlays (
    overlay_id   TEXT PRIMARY KEY,
    system       TEXT,   -- e.g., western_tropical, named indigenous calendar
    label        TEXT,   -- human-readable symbol
    time_start   TEXT,
    time_end     TEXT,
    provenance   JSON,
    notes        TEXT
);

CREATE INDEX IF NOT EXISTS idx_context_fields_type_time ON context_fields(context_type, time_start, time_end);
CREATE INDEX IF NOT EXISTS idx_context_fields_location ON context_fields(location);
CREATE INDEX IF NOT EXISTS idx_context_fields_updated ON context_fields(updated_at);
