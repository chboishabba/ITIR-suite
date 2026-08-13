# Largest-File Refactor Priority 1 Briefs

This note is the aggregate pre-triage brief set for the current Priority 1
targets in the large-file refactor lane.

Use it as the entrypoint for bounded triage. Each child brief defines:

- current surface
- reusable core to preserve or extract
- specialized remainder that should stay explicit
- proposed modules after split
- acceptance checks

Child briefs:

- `docs/planning/chat_context_resolver_refactor_brief_20260328.md`
- `docs/planning/wiki_timeline_runtime_refactor_brief_20260328.md`
- `docs/planning/wiki_timeline_aoo_all_route_refactor_brief_20260328.md`
- `docs/planning/manifest_shard_core_refactor_brief_20260328.md`
- `docs/planning/itir_jmd_runtime_refactor_brief_20260328.md`

Triage order:

1. `scripts/chat_context_resolver.py`
2. `itir-svelte/src/lib/server/wikiTimelineAoo.ts`
3. `itir-svelte/src/routes/graphs/wiki-timeline-aoo-all/+page.svelte`
4. `tools/build_zelph_hf_manifest.py` +
   `tools/build_shared_shard_artifact_contract.py`
5. `itir_jmd_bridge/runtime.py`

Execution rule:

- do not start implementation from this note alone
- use the child brief for the specific target being triaged
- keep generic core extraction ahead of cosmetic renaming
