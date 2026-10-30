# 2026-10-30 PostgreSQL semantic authority cut

`load_preferred_semantic_corpus` now fails closed when PostgreSQL is unavailable, and explicitly rejects SLRW loader/path arguments. SLRW remains legacy migration input, not runtime semantic truth. Added tests for outage and legacy fallback rejection. Existing SQLite migration paths and local SQLite formal receipt store remain to be migrated; this slice does not claim full sole-database compliance. Golden Agda and ESD unchanged. Tests require local referee rerun.
