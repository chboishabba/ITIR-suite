# GWB Completeness Scorecard (2026-03-24)

## Purpose
Make the repo explicit about the intended destination for the GWB lane:
complete GWB/topic understanding, not merely a bounded public handoff slice.

Companion index:
- `docs/planning/zelph_handoff_index_20260324.md`

This note separates:

- destination:
  complete reviewed, provenance-backed topic understanding
- current checked artifact:
  one scored checkpoint toward that destination

The point is to stop speaking vaguely about "works" or "partial" and instead
measure where the current GWB lane stands.

Role of this note:
- broader completeness/corpus-accounting note
- not the bounded handoff spec
- not the pack-definition doc

## Destination
For GWB, the intended destination is:

- broad topic-lane coverage over the public GWB material we choose to model
- explicit entity, office, institution, statute, and court understanding
- deterministic relation promotion where evidence is strong
- explicit abstention where evidence is weak
- downstream queryability over the resulting reviewed graph

That means the goal is not just a handoff bundle. The goal is a complete,
reviewed topic model for the chosen GWB scope.

## Why the checked handoff is still not the full destination
The checked handoff artifact is deliberately bounded. It proves:

- public-entity handoff is real
- Zelph export is real
- narrative explanation is real
- ambiguity handling is real

But it does not by itself prove:

- full topic-lane inventory coverage
- full event coverage
- full cross-lane closure
- full recall against a reviewed GWB topic inventory

So the right framing is:
- destination: complete GWB/topic understanding
- current checked artifact: a scored public-facing checkpoint

## Checked slice vs broader GWB completeness
The repo should now distinguish these explicitly.

### 1. Checked GWB handoff slice
This is the current outward-facing public-entity artifact:
- reviewed
- bounded
- legible to a Zelph developer
- built from the current linkage + semantic + handoff surfaces

Use it to prove:
- public-topic ingest/review/handoff is real
- promotion, abstention, and downstream Zelph reasoning are all real

Do not use it to prove:
- full GWB source-family coverage
- full event inventory over the broader GWB corpus
- completeness over non-wiki source families

### 2. Broader GWB corpus completeness target
The actual destination is wider than the current checked slice.

Existing repo source families already point to that broader target:
- wiki/timeline artifacts under `SensibLaw/.cache_local/wiki_timeline_gwb*.json`
- public-bios timeline material under
  `SensibLaw/demo/ingest/gwb/public_bios_v1/`
- broader corpus timeline build support in
  `SensibLaw/scripts/gwb_corpus_timeline_build.py`
- book/corpus source material under `SensibLaw/demo/ingest/gwb/`, including:
  - `Decision Points`
  - `41`
  - `Family of Secrets`
  - `Jeb and the Bush Crime Family`

So a stronger completeness claim must account for source-family breadth, not
just the current wiki/seed-oriented checked slice.

## Scorecard dimensions
The repo should use a small scorecard rather than one vague completeness claim.

### 1. Promoted relation coverage
How many clean promoted semantic relations exist in the checked or full run?

Signals:
- promoted relation count
- promoted relation family diversity
- number of public-law lanes represented by promoted relations

### 2. Review-lane pressure
How much of the topic is still present only as review items?

Signals:
- matched seed lane count
- candidate-only seed lane count
- ambiguous event count

### 3. Broad-cue dependence
How much of the apparent understanding still relies on broad cues rather than
direct reviewed support?

Signals:
- direct-support seed lane count
- broad-cue-supported seed lane count

### 4. Abstention quality
Whether the system is refusing to overresolve discourse labels appropriately.

Signals:
- unresolved discourse surface count
- explicit unresolved surface list

### 5. Downstream reasoning viability
Whether the bounded export is actually usable by Zelph, not just serializable.

Signals:
- facts bundle generated
- rules bundle generated
- Zelph engine status
- query/rule outputs materially reflect the promoted and review lanes

## Current checked checkpoint
The current checked public handoff artifact reports:

- 19 selected promoted relations
- 11 selected seed/review lanes
- 9 ambiguous events
- 7 unresolved discourse surfaces
- Zelph engine status `ok`

Interpreting those numbers:

- strong enough to prove a real public-facing handoff
- not strong enough to claim full GWB/topic closure yet
- especially because several selected lanes still depend on `broad_cue`
  support rather than only narrow direct support

## Promotion criteria for stronger completeness claims
The repo should only start talking about near-complete GWB/topic understanding
when we can show all of the following against a reviewed scope:

1. reviewed topic-lane inventory exists
2. each lane has an explicit state:
   promoted, candidate-only, ambiguous, abstained, or missing
3. broad-cue dependence is declining, not merely hidden
4. downstream queries operate over more than one handpicked slice
5. the narrative summary can explain both what is known and what remains open
6. source-family coverage is explicit:
   wiki/timeline, public bios, books, and any other chosen public corpus lanes

## Recommended broader GWB scorecard additions
To move from a handoff checkpoint to a corpus-completeness claim, add:

- source family inventory
- per-family source counts
- per-family promoted relation counts
- per-family candidate-only lane counts
- per-family unresolved/abstained lane counts
- cross-family merge and dedup notes
- checked-slice-to-full-run ratio

## First broader GWB checkpoint target
The next concrete GWB move should not be "more prose about completeness." It
should be one broader machine-readable checkpoint built over the source
families already present in-repo.

Proposed source families for the first broader checkpoint:
- checked handoff lane:
  `SensibLaw/tests/fixtures/zelph/gwb_public_handoff_v1/`
- public bios rich timeline lane:
  `SensibLaw/demo/ingest/gwb/public_bios_v1/wiki_timeline_gwb_public_bios_v1_rich.json`
- corpus/book timeline lane:
  `SensibLaw/demo/ingest/gwb/corpus_v1/wiki_timeline_gwb_corpus_v1.json`

Proposed broader-checkpoint artifact:
- `SensibLaw/tests/fixtures/zelph/gwb_broader_corpus_checkpoint_v1/`

Intended outputs:
- `gwb_broader_corpus_checkpoint_v1.json`
- `gwb_broader_corpus_checkpoint_v1.summary.md`

Acceptance target for this first broader checkpoint:
- run deterministic linkage + semantic extraction over the public-bios and
  corpus/book timeline inputs, not only the checked handoff timeline
- merge relations by canonical `(subject, predicate, object)` identity so the
  broader checkpoint measures widened coverage rather than raw duplication
- count seed-lane support across source families
- expose which source families actually contributed promoted relations
- remain honest about ambiguous/broad-cue lanes instead of collapsing them

Current result from the first broader checkpoint:
- artifact now exists under
  `SensibLaw/tests/fixtures/zelph/gwb_broader_corpus_checkpoint_v1/`
- 3 source families counted in the merged extraction checkpoint
- 16 distinct promoted relations after canonical dedupe
- 1 new promoted relation beyond the checked handoff
- only 1 seed lane matched in multiple source families
- public-bios rich timeline now contributes 2 matched seed lanes and 8
  promoted relations in the current pass
- corpus/book timeline contributes 3 promoted relations and 1 matched seed lane

Public-bios implementation update:
- the broader checkpoint no longer uses the old title-only
  `wiki_timeline_gwb_public_bios_v1.json` input
- it now builds and consumes
  `SensibLaw/demo/ingest/gwb/public_bios_v1/wiki_timeline_gwb_public_bios_v1_rich.json`
  from the raw HTML pages under `public_bios_v1/raw/`
- the rich builder emits cue-filtered snippet windows over body paragraphs,
  captions, and meta descriptions, and now flushes malformed HTML paragraph
  transitions so explicit statute-signing sentences survive as standalone
  events
- that richer shaping is enough to recover one genuinely new broader-source
  public-law family:
  `George W. Bush -> signed -> No Child Left Behind Act`

Practical reading:
- the bottleneck is no longer source-family inventory
- the public-bios lane now reaches real broader-source promoted output on one
  additional public-law family, not just repeated review-relation confirmation
- diagnostics now sharpen that bottleneck:
  there are now two clean broader promoted families, but most broader-source
  lanes are still linkage-heavy and semantics-light
- so the immediate next repair is event shaping / semantic anchoring over the
  public-bios and corpus/book lanes, not blind source expansion and not
  promotion-policy loosening by default

## Broader-source diagnostics artifact
The repo now also carries a machine-readable diagnostic companion for that
failure mode:

- `SensibLaw/tests/fixtures/zelph/gwb_broader_promotion_diagnostics_v1/`

Current diagnostic result:
- 2 broader source families inspected:
  public bios rich timeline and corpus/book timeline
- both families now provide matched seed support
- both families now provide relation candidates
- both families now provide promoted relations
- current diagnostic counts:
  - public bios rich timeline: 8 relation candidates, 8 promoted relations
  - corpus/book timeline: 3 relation candidates, 3 promoted relations
- text-debug is now available on both broader-source families rather than
  remaining fully unavailable

Interpretation of those promotions:
- one broader promoted family remains an independent confirmation of an
  already-known checked-handoff relation family:
  `George W. Bush -> subject_of_review_by -> Supreme Court of the United States`
- the richer public-bios lane now also contributes one genuinely new broader
  promoted public-law relation:
  `George W. Bush -> signed -> No Child Left Behind Act`
- the merged broader checkpoint now adds `1` new distinct promoted relation
  after canonical dedupe, which is the correct honest result

Practical implication:
- broader-source GWB is no longer stuck entirely before semantics
- it now reaches independent broader-source promoted confirmation on one clean
  repeated review-relation family, while still remaining conservative about new
  relation-family expansion
- a follow-on disambiguation pass now also abstains bare `Bush` in explicit
  father/family-history corpus contexts instead of silently resolving those
  rows to George W. Bush
- the next concrete work should improve candidate quality and mention/object
  resolution so additional broader-source families can become promotable

## Current implementation hook
The checked GWB handoff artifact should carry a machine-readable scorecard so
the repo can stop relying on prose-only quality judgments.

Current artifact directory:
- `SensibLaw/tests/fixtures/zelph/gwb_public_handoff_v1/`

Expected scorecard shape:
- `destination`
- `current_stage`
- `promoted_relation_count`
- `matched_seed_lane_count`
- `candidate_only_seed_lane_count`
- `broad_cue_seed_lane_count`
- `direct_support_seed_lane_count`
- `ambiguous_event_count`
- `unresolved_surface_count`
- `zelph_engine_status`

Near-term corpus-level companion artifact:
- `SensibLaw/tests/fixtures/zelph/gwb_corpus_scorecard_v1/`
- generated outputs:
  - `gwb_corpus_scorecard_v1.json`
  - `gwb_corpus_scorecard_v1.summary.md`

Current generated checkpoint:
- 4 source families counted
- 19 promoted relations still visible from the checked handoff
- 9 public-bios manifest documents
- 320 corpus timeline events
- 260 corpus AAO events
- 4 local demo/book files

Command:
- `cd /home/c/Documents/code/ITIR-suite && python SensibLaw/scripts/build_gwb_corpus_scorecard.py`

Purpose of the corpus-level companion:
- inventory wider in-repo GWB source families beyond the checked handoff slice
- keep public-bios, corpus-timeline, and local book/demo surfaces visible in
  one machine-readable checkpoint
- separate source-family breadth from promoted-relation completeness so the
  repo stops speaking about "GWB completeness" as if it were one number

## Immediate next use
- keep using the current checked artifact for public handoff
- use the scorecard to decide whether GWB should become pack `v1.5`
- expand later from checked slice metrics to wider real-run metrics that
  include non-wiki source families already present in the repo
