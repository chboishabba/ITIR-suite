# JMD Fixture Pack

Fixture pack for the first JMD -> SL bridge example.

Files:
- `erdfa_manifest_promotion_v1.example.json`
- `jmd_sl_ingest_v1.example.json`
- `sl_jmd_overlay_v1.example.json`
- `zkperf_on_sl_observation_v1.example.json`
- `hf_container_index_v1.example.json`

These fixtures are documentation-first examples, not live protocol tests.

The intended v1 shape is:
- ERDFA-backed text shard
- dual paste/CID retrieval refs
- byte-addressable reversible SL anchors
- reserved proof/provenance commitment fields kept optional
