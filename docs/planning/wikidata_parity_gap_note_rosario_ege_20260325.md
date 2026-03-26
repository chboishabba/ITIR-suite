# Wikidata Parity Gap Note: Rosario vs Ege/Peter (2026-03-25)

## Purpose
State, in repo-backed terms, where the current Wikidata lane stands relative to:

- Rosario's IBM-affiliated LLM consistency benchmark framing
- Ege Doğan / Peter Patel-Schneider's disjointness-violation work

This note is for collaboration positioning, not for marketing.

## One-line summary
The repo now has meaningful partial parity with Rosario on benchmark
construction/scoring shape, but only adjacent overlap with Ege/Peter because it
does not yet have a dedicated `P2738` disjointness lane.

## Current repo state
The current Wikidata lane already provides:

- deterministic bounded slices and revision-pair fixtures
- structural diagnostics over `P31` / `P279`
- qualifier-drift detection on pinned revision pairs
- typed parthood packs
- hotspot-pack selection over structural pathology families
- cluster generation
- score-only evaluation with pinned response-bundle fixtures

Primary current surfaces:

- `docs/planning/wikidata_hotspot_benchmark_lane_20260325.md`
- `docs/planning/wikidata_hotspot_pack_contract_20260325.md`
- `docs/planning/wikidata_hotspot_pilot_pack_v1.manifest.json`
- `SensibLaw/src/ontology/wikidata_hotspot.py`
- `SensibLaw/src/ontology/wikidata_hotspot_eval.py`

## Parity against Rosario / IBM consistency framing

### Where parity is real
The repo now overlaps materially with Rosario on:

- bounded cluster-pack generation
- reproducible yes/no-style question surfaces
- evaluator/report contract
- cross-domain coverage
- deterministic pinned examples instead of only live-query drift

Concretely, the repo already has hotspot-backed examples for:

- mixed-order
- SCC / circular subclass
- qualifier drift
- entity-kind collapse

### Where parity is not real
The repo does not yet match Rosario's method directly because it does not:

- flatten `P31` and `P279` into a single clean ontology edge
- generate large benchmark families from a broad ontology extraction pipeline
- treat LLM inconsistency measurement as the primary truth surface
- include a built-in live model-running pipeline

### Best current reading
- surface-mechanics parity: moderate
- exact-method parity: no
- research-intent parity: adjacent

The repo is stronger on pathology preservation and provenance, but weaker on
large automatic ontology-to-benchmark throughput.

The productive discovery surface is also different in practice:

- Rosario-style work assumes broad current-graph extraction and benchmarking
  rather than dependence on small retained local bins
- in this repo, live/current WDQS-backed Wikidata probing is the productive
  source for contradiction-pack discovery
- local pruned `.bin` artifacts have now behaved only as runtime/loader
  negative controls for the current contradiction families

## Parity against Ege/Peter disjointness work

### What their paper is doing
`2410.13707v2` is centered on:

- extracting pairwise disjoint class pairs from `disjoint union of` (`P2738`)
- counting subclass violations and instance violations
- identifying culprit classes/items that generate many downstream violations
- using SPARQL-driven analysis over Wikidata's current disjointness modeling
- discussing how disjointness could be represented and expanded better

### Where the repo overlaps
The repo already overlaps in broad ontology-diagnostic posture:

- deterministic review over bounded slices
- emphasis on structural contradiction, not just data ingestion
- willingness to keep diagnostics separate from auto-fix claims
- explicit working-group orientation

The repo also has one major capability Ege/Peter do not:

- a Zelph-export lane for checked downstream reasoning over reviewed structure

That matters for collaboration positioning, but it does not close the parity gap
on the paper's main technical core.

### Main missing parity
The repo currently lacks:

- a `P2738` extractor
- pairwise disjoint-class materialization as a first-class review surface
- subclass-violation counts for disjoint pairs
- instance-violation counts for disjoint pairs
- culprit-mining specific to disjointness violations
- a dedicated disjointness report contract

### Best current reading
- concrete method parity: low
- ontology-diagnostic philosophy parity: moderate
- complementarity: high

The repo is best described as adjacent and collaboration-compatible, not as a
reproduction or substitute.

The local-pruned-bin experiments make that boundary clearer:

- both `wikidata-20171227-pruned.bin` and `wikidata-20260309-all-pruned.bin`
  returned zero useful signal across profile, wide, bounded, exact, and
  seedless local scans for the current target families
- so practical progress toward Ege/Peter-style disjointness work is coming from
  live/current Wikidata, then pinning reviewed slices into repo fixtures

## Why Zelph changes the positioning
Ege/Peter's paper is stronger than the current repo on disjointness-specific
analysis.

The current repo is stronger on:

- turning bounded reviewed structure into downstream machine-readable artifacts
- preserving abstention/review pressure
- exporting checked structure into a second reasoning surface

So the strongest honest positioning is:

- Rosario comparison:
  benchmark-lane adjacency with meaningful partial parity
- Ege/Peter comparison:
  method gap on disjointness, but stronger downstream reviewed-structure
  handoff potential

## Recommended wording for external discussion
Use wording like:

- "partial parity with Rosario on the benchmark/scorer side"
- "adjacent to Ege/Peter, but not yet parity on the `P2738` disjointness core"
- "stronger on reviewed export / downstream reasoning because of the Zelph lane"

Avoid wording like:

- "we reproduced Rosario"
- "we already have parity with Ege/Peter"
- "our current hotspot lane subsumes disjointness analysis"

## Best next move for substantive parity with Ege/Peter
Build one bounded `P2738` disjointness lane that:

1. extracts pairwise disjoint class pairs from `P2738` + `P11260`
2. detects subclass violations
3. detects instance violations
4. computes culprit classes/items
5. emits one deterministic review report with fixture-backed tests

That would move the repo from "adjacent" to "serious parity candidate" on the
paper's core method.
