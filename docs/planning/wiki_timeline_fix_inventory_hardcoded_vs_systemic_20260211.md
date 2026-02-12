# Wiki Timeline Fix Inventory: Hardcoded vs Systemic (2026-02-11)

## Scope
This note classifies the implemented wiki timeline + AAO fixes requested in the recent GWB pass.

- Focus: extraction/parser behavior and graph hydration fixes.
- Excluded: cosmetic-only UI style/layout tweaks.

## Count summary
- Total classified fixes: `26`
- Hardcoded/heuristic fixes: `8`
- Systemic/algorithmic fixes: `18`

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

## Systemic / algorithmic fixes (`17`)
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

10. Fact timeline loader fallback chain (`fact_timeline[]` -> nested `timeline_facts[]` -> synthesized from `steps[]`).
File: `itir-svelte/src/routes/graphs/wiki-fact-timeline/+page.server.ts`

11. Fact timeline diagnostics lane (`fact_row_source`, raw/output row counts) for payload-shape visibility.
Files:
- `itir-svelte/src/routes/graphs/wiki-fact-timeline/+page.server.ts`
- `itir-svelte/src/routes/graphs/wiki-fact-timeline/+page.svelte`

12. Route repo-root resolution made deterministic across cwd variants (`.` then `..` check for `SensibLaw/`).
Files:
- `itir-svelte/src/routes/graphs/wiki-timeline/+page.server.ts`
- `itir-svelte/src/routes/graphs/wiki-timeline-aoo/+page.server.ts`
- `itir-svelte/src/routes/graphs/wiki-timeline-aoo-all/+page.server.ts`
- `itir-svelte/src/routes/graphs/wiki-fact-timeline/+page.server.ts`

13. Wiki timeline context now surfaces link breadth (`links[]` chips) without changing extraction semantics.
File: `itir-svelte/src/routes/graphs/wiki-timeline/+page.svelte`

14. Action-local object extraction now uses dependency attachments per step (verb-specific), then merges
    deterministic fallback wikilinks for identity glue instead of one shared object bucket per sentence.
File: `SensibLaw/scripts/wiki_timeline_aoo_extract.py`

15. Request-clause normalization emits explicit requester-led steps (`request`) with role-correct
    subjects/objects and removes leaked pseudo-`requested` steps from generic verb scanning.
File: `SensibLaw/scripts/wiki_timeline_aoo_extract.py`

16. Negation-aware step metadata (`step.negation`) and clause-level `content_clause`/`infinitive_clause`
    chains are emitted for complement structures, while keeping canonical action labels stable.
File: `SensibLaw/scripts/wiki_timeline_aoo_extract.py`

17. Fact timeline synthesis now carries chain-aware crosslinks (`prev_fact_ids`, `next_fact_ids`,
    `chain_kinds`) derived from event `chains[]` so f01/f02 navigation is explicit in context.
Files:
- `itir-svelte/src/routes/graphs/wiki-fact-timeline/+page.server.ts`
- `itir-svelte/src/routes/graphs/wiki-fact-timeline/+page.svelte`
- `itir-svelte/src/lib/server/wikiTimelineAoo.ts`

18. Extractor behavior is now profile-driven for action regex inventory and requester title labels
    (`--profile`), and emitted artifacts pin `extraction_profile` provenance (id/version/hash).
Files:
- `SensibLaw/scripts/wiki_timeline_aoo_extract.py`
- `SensibLaw/policies/wiki_timeline_aoo_profile_v1.json`

## What this means
- We are not hardcoding event text into the UI; graph content is generated from JSON artifacts.
- We are still using bounded heuristic patches for known citation/prose pathologies.
- The direction remains: keep truth capture broad and deterministic, push promotion/weighting into view logic.

## Remaining de-hardcode targets
1. Replace `REPORTED_SUBJECT_RE` with dependency-first subject extraction only.
2. Replace explicit reported->cautioned split with generic clause/verb-chain decomposition.
3. Replace surface phrase object injections with dependency/object promotion + resolver confidence thresholds.
4. Keep citation-tail stripping, but move from pattern list to token-span aware reference-tail detection.

## 2026-02-12 follow-up (systemic extraction changes)
- Object de-duplication now canonicalizes determiner variants (`the X` vs `X`) and
  resolves collisions via deterministic row scoring (source + resolver hints), then
  merges resolver hints into a single canonical row.
  File: `SensibLaw/scripts/wiki_timeline_aoo_extract.py`
- Purpose-step derivation is now verb-gated (`spaCy` parse first, conservative fallback),
  preventing non-verb heads (e.g., `for`) from appearing as actions.
  File: `SensibLaw/scripts/wiki_timeline_aoo_extract.py`
- Step/event payloads now include `entity_objects` and `modifier_objects` lanes,
  allowing view-layer suppression of clause mechanics without truth-layer pruning.
  File: `SensibLaw/scripts/wiki_timeline_aoo_extract.py`
- Modal-container constructions now promote semantic xcomp verbs (`have/be` wrappers)
  into the action lane and keep wrapper nouns/adjectives as `modifiers[]`, reducing
  legal-narrative action leakage (`have`, `be`) without regex sentence families.
  File: `SensibLaw/scripts/wiki_timeline_aoo_extract.py`
- Parser fallback action selection now prefers non-wrapper verbs (e.g. xcomp/acl)
  over `have/be` when multiple verb candidates exist in a sentence.
  File: `SensibLaw/scripts/wiki_timeline_aoo_extract.py`

## 2026-02-12 follow-up (HCA cleanup pass: hardcoded vs systemic)
- `hardcoded fixes`: `0`
  - No new sentence-family branches or dataset-specific literals were added in this pass.
- `systemic fixes`: `4`
  1. Parser input now strips parenthetical citation noise before dependency extraction
     (keeps event text canonical; parse path de-noised).
     File: `SensibLaw/scripts/wiki_timeline_aoo_extract.py`
  2. Subject normalization now resolves possessive evidence wrappers to person actors
     (e.g., `Fr Dillon's evidence` -> `Fr Dillon`) instead of leaving wrapper nouns as subjects.
     File: `SensibLaw/scripts/wiki_timeline_aoo_extract.py`
  3. Entity/object hygiene now applies shared surface cleanup for footnote/citation tails and
     promotes person/party-role mentions to `entity_objects` when resolver IDs are absent.
     File: `SensibLaw/scripts/wiki_timeline_aoo_extract.py`
  4. Action/object extraction paths now use the cleaned parse text consistently, reducing
     citation-fragment leakage into `purpose`, `objects`, and timeline facts.
     File: `SensibLaw/scripts/wiki_timeline_aoo_extract.py`

## 2026-02-12 follow-up (communication-chain de-hardcode)
- `hardcoded fixes`: `0`
- `systemic fixes`: `2`
  1. Removed sentence-family `reported/cautioned` extraction branch and replaced with
     profile-driven dependency communication-chain extraction over `ccomp/xcomp`.
     File: `SensibLaw/scripts/wiki_timeline_aoo_extract.py`
  2. Removed regex reported-subject actor injection (`REPORTED_SUBJECT_RE`) from truth actor lane;
     subject attribution now comes from dependency subject resolution and chain modifiers.
     File: `SensibLaw/scripts/wiki_timeline_aoo_extract.py`
