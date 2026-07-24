# Wikidata Lanes After Zelph 0.9.6

Date: 2026-07-03

## Purpose

Record the concrete next read on the current Wikidata lanes now that Zelph
`v0.9.6` is released with:

- SPARQL subset support
- qualifier import
- sharding and partial loading

This note is intentionally narrower than the broader roadmap docs. It answers:

1. which Wikidata lanes are executable right now in ITIR/SensibLaw,
2. which of those lanes directly benefit from Zelph `0.9.6`,
3. what is still blocked on the hosted Wikidata shard publication surface.

## Current executable lane surface

The repo now has an executable audit command:

```bash
cd SensibLaw
../.venv/bin/python -m cli.__main__ wikidata lane-status
```

That runtime currently audits five concrete lanes:

- `climate_review_demonstrator`
- `change_review_packet`
- `disjointness_report`
- `hotspot_eval`
- `nat_live_follow_preflight`

The point of this command is not to claim authority. It is to give one small
machine-runnable answer to "what Wikidata lanes do we actually have today?"

Two companion commands now expose the normalized architecture surfaces for one
lane at a time:

```bash
cd SensibLaw
../.venv/bin/python -m cli.__main__ wikidata lane-bundle --lane disjointness_report
../.venv/bin/python -m cli.__main__ wikidata lane-graph --lane disjointness_report
../.venv/bin/python -m cli.__main__ wikidata lane-flatness
../.venv/bin/python -m cli.__main__ wikidata lane-plan --lane climate_review_demonstrator
../.venv/bin/python -m cli.__main__ wikidata lane-proof --lane disjointness_report
```

Those commands are the first implementation of:

- a shared review bundle across Wikidata lanes
- a graph-side latent slice / flatness diagnostic surface
- a cross-lane non-visual flatness audit surface
- a bounded adjacent-Zelph discovery-plan surface for the climate/live lanes
- a bounded direct-Zelph proof surface for the first shard-native lane

Important definition boundary:

- the current audit defines `projection_flat` as a shallow derived graph
  posture
- that is useful, but it is narrower than the broader ITIR meaning of
  flatness, which is loss of intermediate linkage depth between local evidence
  and higher-order semantic/review anchors
- the canonical cross-domain definition now lives in:
  `docs/planning/itir_flatness_doctrine_20260703.md`
- visual/webui rendering remains a separate downstream question

## Read now

### Direct Zelph 0.9.6 beneficiary

- `disjointness_report`
  - this is the clearest direct bridge because Zelph `0.9.6` now supports the
    qualifier/SPARQL surface that matches the `P2738` + `P11260` lane
  - the repo-local bounded report already works on pinned slices
  - the repo now also exposes a bounded local `lane-proof` surface that marks
    the direct Zelph contract as locally ready while still keeping hosted WD
    acceptance pending
  - the remaining gap is not lane semantics, but end-to-end WD hosted artifact
    publication
  - the current latent-slice graph for this lane still reads as
    `projection_flat`, which is useful: it means we now have a measurable graph
    posture rather than a hand-wavy flatness complaint

### Adjacent, but not blocked on Zelph

- `climate_review_demonstrator`
  - still primarily a bounded review packet lane
  - Zelph SPARQL can help later with broader candidate discovery and climate
    family confirmation pressure, but the current demonstrator does not require
    Zelph to execute
  - the repo now exposes that next step explicitly through
    `wikidata lane-plan --lane climate_review_demonstrator`
- `nat_live_follow_preflight`
  - live-oriented and already useful as a bounded review-preflight surface
  - complements future Zelph-backed discovery rather than depending on it
  - the repo now also exposes that adjacency as
    `wikidata lane-plan --lane nat_live_follow_preflight`

### Mostly independent reviewer-geometry lanes

- `change_review_packet`
- `hotspot_eval`

These remain important, but they are not the primary pressure points for the
new Zelph release.

They are still useful for the flatness tranche though:

- `wikidata lane-flatness` currently reports every lane as `projection_flat`
- that means the repo still does not have a "renderer definitely at fault"
  signal yet
- `hotspot_eval` also shows a concrete pre-render projection issue: duplicate
  node ids collapse 20 emitted nodes down to 13 unique nodes
- and the broader doctrine now treats the next honest gap as linkage-depth
  measurement across domains, not only Wikidata lane density

## Hosted shard reality on 2026-07-03

As of 2026-07-03, the new released Zelph code can be integrated locally and the
visible HF shard objects can be probed, but the full WD shard-native acceptance
path is still not complete from ITIR's side unless the canonical hosted
manifest/index entrypoints are present and byte-aligned with the uploaded
artifacts.

Practical consequence:

- treat `disjointness_report` as the first direct Wikidata lane to push through
  Zelph `0.9.6`
- do not block broader Wikidata lane work on the pruned `.bin`
- keep the shard-native full-WD proof as a separate acceptance item

## Recommended next move

1. use `wikidata lane-status` as the current quick audit surface
2. push the disjointness lane first when testing Zelph-backed Wikidata work
3. keep climate/live-follow lanes moving in parallel because they do not depend
   on the final hosted-manifest state
4. treat the next flatness/linkage tranche as:
   `docs/planning/pnf_zelph_wd_linkage_depth_contract_20260703.md`
