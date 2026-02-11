# Wiki Timeline Fix Inventory: Hardcoded vs Systemic (2026-02-11)

## Scope
This note classifies the implemented wiki timeline + AAO fixes requested in the recent GWB pass.

- Focus: extraction/parser behavior and graph hydration fixes.
- Excluded: cosmetic-only UI style/layout tweaks.

## Count summary
- Total classified fixes: `17`
- Hardcoded/heuristic fixes: `8`
- Systemic/algorithmic fixes: `9`

## Hardcoded / heuristic fixes (`8`)
These are deterministic but still rule-based/special-case logic that should eventually shrink.

1. Citation-tail strip regexes for sentence cleanup (`CITATION_TAIL_RE`).
File: `SensibLaw/scripts/wiki_timeline_extract.py:82`

2. Punctuation spacing recovery for citation joins (`exam.Rutenberg` style).
File: `SensibLaw/scripts/wiki_timeline_extract.py:306`

3. Middle-initial sentence-split protection (`George W. Bush` guard).
File: `SensibLaw/scripts/wiki_timeline_extract.py:293`

4. Non-person token guard expansion for name-like title suppression.
File: `SensibLaw/scripts/wiki_timeline_aoo_extract.py:31`

5. Regex action-pattern expansion (`initiated`, `discharged`, `suspended`, `reported`, etc.).
File: `SensibLaw/scripts/wiki_timeline_aoo_extract.py:96`

6. Regex subject hook for `"X reported"` extraction (`REPORTED_SUBJECT_RE`).
File: `SensibLaw/scripts/wiki_timeline_aoo_extract.py:93`

7. Surface phrase object injections (`the war`, `continue weakening ...`) for lossy sentences.
File: `SensibLaw/scripts/wiki_timeline_aoo_extract.py:887`

8. Explicit reported->cautioned split fallback for that sentence family.
File: `SensibLaw/scripts/wiki_timeline_aoo_extract.py:975`

## Systemic / algorithmic fixes (`9`)
These are reusable extraction/data-model improvements, not tied to one sentence.

1. spaCy parser lane with pinned provenance metadata in output (`parser` block).
File: `SensibLaw/scripts/wiki_timeline_aoo_extract.py:281`

2. Dependency-gated purpose extraction (`to` infinitival clause) replacing allowlist behavior.
File: `SensibLaw/scripts/wiki_timeline_aoo_extract.py:355`

3. Dependency-based subject extraction/refinement per action step.
File: `SensibLaw/scripts/wiki_timeline_aoo_extract.py:585`

4. Dependency-based object fallback lane (`noun_chunks` + dep object roles).
File: `SensibLaw/scripts/wiki_timeline_aoo_extract.py:438`

5. Resolver-hint scoring lane (`exact`/`near`) across sentence links, paragraph links, candidate titles.
File: `SensibLaw/scripts/wiki_timeline_aoo_extract.py:480`

6. Step-level chain model (`sequence`, `purpose_clause`) in payload.
File: `SensibLaw/scripts/wiki_timeline_aoo_extract.py:1233`

7. Derived purpose-step generation for nested/chain rendering.
File: `SensibLaw/scripts/wiki_timeline_aoo_extract.py:622`

8. `span_candidates` unresolved-mention lane with recurrence + hygiene metadata.
File: `SensibLaw/scripts/wiki_timeline_aoo_extract.py:1032`

9. UI hydration switched to step-local subject/object wiring (reduces false co-subject joins).
Files:
- `itir-svelte/src/routes/graphs/wiki-timeline-aoo/+page.svelte:137`
- `itir-svelte/src/routes/graphs/wiki-timeline-aoo-all/+page.svelte:111`

## What this means
- We are not hardcoding event text into the UI; graph content is generated from JSON artifacts.
- We are still using bounded heuristic patches for known citation/prose pathologies.
- The direction remains: keep truth capture broad and deterministic, push promotion/weighting into view logic.

## Remaining de-hardcode targets
1. Replace `REPORTED_SUBJECT_RE` with dependency-first subject extraction only.
2. Replace explicit reported->cautioned split with generic clause/verb-chain decomposition.
3. Replace surface phrase object injections with dependency/object promotion + resolver confidence thresholds.
4. Keep citation-tail stripping, but move from pattern list to token-span aware reference-tail detection.
