# Phase E: PNF x Zelph/WD Linkage-Depth Contract

Date: 2026-07-03

## Purpose

This note defines the next highest-alpha tranche after the shared flatness
doctrine note.

The correction is:

- start with Zelph/WD as the first external bridge
- do not let Zelph/WD define flatness
- keep PNF as the spine
- require the bridge to preserve the spine rather than erase it

Short version:

- Zelph/WD is the first bridge
- PNF is the spine
- the flatness audit ensures the bridge does not erase the spine

## Target Path

The first machine-facing linkage-depth audit should be built around this path:

```text
token/span
-> sentence:document
-> sentence:PNF
-> document:PNF
-> entity/topic candidate
-> WD lexical/semantic candidate
-> Zelph/WD review surface
-> review packet / tranche
```

This gives one tranche with both:

- local role-preservation audit
- external WD linker audit

The explicit anti-goal is auditing only:

```text
token -> WD
```

because that would reproduce the original flatness problem in a shinier form.

## Why This Bridge Goes First

This is the first bridge with obvious external value:

```text
plain text / article / legal document
-> PNF role structure
-> WD candidate grounding
-> reviewable ontology packet
```

That makes it a better alpha demonstration than a purely internal PNF audit,
while still requiring the local PNF/document/review ladder to stay intact.

## Early WD vs Late WD

The contract must explicitly separate two WD moments.

### Early WD

```text
token -> WD lexical candidate
```

Status:

- `soft_stitch`
- `promotion = blocked`

Purpose:

- lexical/semantic hint only
- retrieval/disambiguation aid
- not authority

### Late WD

```text
PNF/entity/topic candidate -> WD review candidate
```

Status:

- `semantic_review_candidate`
- `promotion = candidate_only`

Purpose:

- reviewable ontology grounding
- constrained by source, PNF role, residuals, and tranche/review boundaries

## First Deliverables

1. `ExpectedLayerContract` schema
2. first contract instance:
   `sensiblaw_pnf_wd_linkage`
3. first non-visual linkage-depth audit surface
4. one tiny dog/mention fixture
5. one real SensibLaw text fixture
6. Zelph/WD bridge-edge requirements

As of 2026-07-03, the first executable surface is:

- `cd SensibLaw && ../.venv/bin/python -m cli.__main__ wikidata linkage-depth`

Implemented in the first pass:

- shared `ExpectedLayerContract`
- first `sensiblaw_pnf_wd_linkage` contract instance
- one synthetic dog soft-stitch case
- one bounded real-text climate review demonstrator case
- non-visual linkage-depth audit output over both cases

## Suggested Contract Shape

The first contract should carry fields such as:

- `domain`
- `anchor_kind`
- `expected_layers`
- `required_bridges`
- `terminal_anchor`
- `minimum_depth`
- `required_authority_boundaries`

Example target contract:

```json
{
  "domain": "sensiblaw_pnf_wd_linkage",
  "anchor_kind": "token_or_span",
  "expected_layers": [
    "token_span",
    "sentence_document",
    "sentence_pnf",
    "document_pnf",
    "entity_topic_candidate",
    "wd_lexical_or_semantic_candidate",
    "zelph_wd_review_surface",
    "review_packet_tranche"
  ],
  "required_bridges": [
    ["token_span", "sentence_document"],
    ["sentence_document", "sentence_pnf"],
    ["sentence_pnf", "document_pnf"],
    ["document_pnf", "entity_topic_candidate"],
    ["entity_topic_candidate", "wd_lexical_or_semantic_candidate"],
    ["wd_lexical_or_semantic_candidate", "zelph_wd_review_surface"],
    ["zelph_wd_review_surface", "review_packet_tranche"]
  ],
  "minimum_depth": 7
}
```

## Audit Outputs

The new audit should go beyond the current shallow graph-shape screen and emit:

- `layer_coverage`
- `typed_path_depth`
- `bridge_completeness`
- `role_erasure_detected`
- `wd_soft_stitch_present`
- `wd_promotion_blocked`
- `anchor_to_tranche_reachability`
- `collapse_points`
- `collapse_origin`

## Minimal Fixtures

### Tiny Dog Fixture

The small proving fixture should follow:

```text
dog-word / dog-mention
-> token
-> WD soft lexical stitch
-> span:sentence:document
-> sentence:PNF
-> role/filler in generic PNF carrier
-> document:PNF
-> entity/topic candidate
-> corpus query result
-> review packet / tranche
```

The audit should fail if the graph only contains:

```text
dog -> sentence
```

or:

```text
dog -> WD
```

It should only pass when the middle role-bearing structure survives.

### Real SensibLaw Fixture

Add one bounded real text slice so the contract is not only synthetic.

The point is not to prove all of SensibLaw. It is to prove that the
token/document/PNF/WD/review ladder can survive one real lane end-to-end.

## Integration Order

Highest-alpha implementation order:

1. add `ExpectedLayerContract`
2. add `sensiblaw_pnf_wd_linkage`
3. add dog fixture and one real SensibLaw fixture
4. add non-visual linkage-depth audit
5. make Zelph/WD linker emit/retain contract-compatible bridge edges
6. plug the result into a generic lane adapter
7. only then touch `itir-svelte` rendering

As of 2026-07-04, step 5 is now active on the first bounded real-text bridge:

- `climate_review_demonstrator` remains a normalized lane artifact
- `wikidata_lane_receipts.py` emits a first-class `linkage_depth_receipt`
  alongside that artifact at the lane boundary
- the receipt carries:
  - `contract`
  - `expected_anchor_ids`
  - `expected_terminal_ids`
  - contract-compatible `nodes`
  - contract-compatible `edges`
  - bridge diagnostics
- soft token -> WD edges remain `promotion_status = blocked`
- the linkage-depth audit now accepts this emitted artifact path directly,
  rather than only reconstructing the spine after the fact

This is the doctrinal transition from:

```text
audit reconstruction
```

to:

```text
bridge-emitted non-flatness receipt
```

Boundary rule:

```text
generic WD adapters expose normalized carriers
lane receipt builders construct typed geometry
audits verify receipts
```

As of 2026-07-04, that same emitted-receipt boundary now covers the bounded
`disjointness_report` lane too:

- `wikidata_disjointness.py` stays a normalized report projector
- `wikidata_lane_receipts.py` emits the structural WD disjointness receipt at
  the lane boundary
- `wikidata_linkage_depth.py` now accepts mixed lane contracts rather than
  forcing every case through the PNF contract

The disjointness receipt is intentionally not PNF-shaped. Its contract is:

```text
source_window
→ statement_bundle
→ disjoint_pair
→ violation_candidate
→ WD review candidate
→ Zelph/WD review surface
→ review packet / tranche
```

That preserves the same doctrine:

```text
generic adapter stays generic
lane-level emitted receipt carries the typed ladder
audit blesses the receipt, not a hidden adapter-specific geometry
```

## Generic Lane Adapter

This bridge should not stop at one demo surface.

Once the contract/audit exists, it should plug into a generic lane adapter for
surfaces such as:

- `nat`
- `climate`
- `GWB`
- `brexit`
- `AU`
- other ontology-bearing lanes

That is the real scaling story:

- one shared flatness doctrine
- one shared linkage-depth contract model
- many lane adapters

## Distinct Contract Families

The extracted linkage-depth core should stay broader than the first WD bridge.
The next contract families are now explicitly frozen as:

- GWB/Brexit: bounded public-source / legal-follow proving grounds
- AU: richer legal authority spine proving sentence/provision, instrument,
  jurisdiction, authority, and review depth
- affidavit: reconciliation / coverage spine proving normalized proposition,
  response candidate, reconciliation root or incident root, dominant relation
  decision, and coverage/review depth

This keeps the shared core open-string and lane-inherited rather than forcing
all follow-on work back through WD-shaped geometry.

## Relationship To Existing Notes

Read alongside:

- `docs/planning/itir_flatness_doctrine_20260703.md`
- `docs/planning/itir_wd_zelph_sensiblaw_flatness_optimisation_roadmap_20260702.md`
- `docs/planning/wikidata_lane_architecture_and_roadmap_20260703.md`
