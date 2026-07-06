# GWB Linkage Artifact Audit

Date: 2026-07-05

## Scope

This note audits actual emitted GWB artifacts rather than only unit tests.

Inspected surfaces:

- `SensibLaw/demo/ingest/gwb/corpus_v1/wiki_timeline_gwb_corpus_v1.json`
- `SensibLaw/demo/ingest/gwb/corpus_v1/wiki_timeline_gwb_corpus_v1_aoo.json`
- `SensibLaw/demo/ingest/gwb/public_bios_v1/wiki_timeline_gwb_public_bios_v1_rich.json`
- `SensibLaw/tests/fixtures/zelph/gwb_broader_corpus_checkpoint_v1/gwb_broader_corpus_checkpoint_v1.json`
- runtime-built broader review artifact from `SensibLaw/scripts/build_gwb_broader_review.py`
- runtime-built projected report and receipt from `src.policy.gwb_broader_review_world_model` and `src.policy.gwb_linkage_depth`

## Headline

The receipt seam is clean, but the emitted GWB artifact stack is mixed:

- `linkage_case` and receipt preserve a typed queue-to-review-to-tranche ladder.
- multi-source timeline extraction exists and produces source-backed semantic relations.
- the corpus timeline is not yet historically trustworthy as a timeline.
- the broader-review bundle flattens most event/legal/source detail into review rows before the receipt layer.

So the current system proves:

- projected artifacts can carry a typed receipt path
- multi-source extraction can add new GWB relations

It does not yet prove:

- historically anchored multi-source timeline depth
- inspectable event/legal/source ladders all the way through the broader-review artifact

## What Survives

### 1. Corpus and public-bios timeline extraction are real

The local GWB corpus timeline contains 320 events across 4 book files.

- each file contributes 80 snippet events
- each event carries a local source `path`
- the downstream AOO artifact adds citation follow records back to the source document path

The richer public-bios timeline contains 52 events across 6 public web sources.

- each event carries a local raw-file `path`
- each event also preserves the original public `url`

### 2. Semantic extraction is not empty

Running the GWB semantic/linkage builders over those timeline artifacts produces:

- `public_bios_timeline`: 8 promoted relations, 12 unresolved mentions, 10 ambiguous events
- `corpus_book_timeline`: 33 promoted relations, 91 unresolved mentions, 144 ambiguous events

The broader corpus checkpoint confirms the multi-source merge:

- 3 source families
- 18 distinct promoted relations after merge
- 3 new relations beyond checked handoff
- 5 seed lanes supported in multiple families

Examples of new relations surviving the broader pass:

- `George W. Bush ruled_by Supreme Court of the United States` from `corpus_book_timeline`
- `George W. Bush signed No Child Left Behind Act` from `public_bios_timeline`

### 3. The receipt path is typed

The projected broader-review `linkage_case` stores, under `payload`, a six-layer path:

- `source_anchor`
- `source_container`
- `domain_candidate`
- `authority_surface`
- `review_surface`
- `tranche_anchor`

The attached receipt carries the same nodes and edges and declares the same expected layers.

This means the receipt is not merely wrapping raw text. It is certifying a projected linkage ladder.

## What Collapses

### 1. Timeline anchors are ingest-time, not event-time

Both timeline families use ingest anchors in the emitted event rows.

Examples:

- corpus snippets are anchored to `2026-03-24`
- public-bio snippets are anchored to `2026-07-05`

This means the emitted timeline is currently:

- source-backed
- orderable as ingestion output

but not yet:

- historically anchored as a real Bush timeline

For timeline proof, this is the biggest gap.

### 2. Corpus snippet quality is noisy

The corpus builder creates fixed-count snippets per book, but many emitted rows are not event-like.

Observed failure modes:

- table-of-contents or index style debris
- frontmatter becoming events
- long biographical inventory strings emitted as one event
- fallback actions such as `reported`, `translated`, `called`
- no actors or no objects extracted

Examples seen in the emitted AOO artifact:

- frontmatter for `41 - Inside the Presidency of George H. W. Bush`
- index-like lines from `Jeb and the Bush Crime Family`
- Senate and House inventory strings spanning many decades

This explains the high ambiguity count in the corpus pass.

### 3. Broader-review source rows flatten typed depth

By the time the broader-review artifact is built, most source rows have already collapsed into coarse review inputs such as:

- `seed_family_support`
- `merged_promoted_relation`
- `source_family_summary`

These rows preserve:

- source family
- support kind
- review status
- seed lane
- relation text label

They usually do not preserve:

- exact source span
- event node identity
- legal reference node identity in the row itself
- actor-role distinctions
- event-to-legal-context-to-authority intermediate structure

So the broader-review layer is review-effective, but not deep enough to audit event-level path quality directly.

### 4. The current receipt mostly certifies follow-queue depth

In the runtime-built broader-review report, the `linkage_case` and receipt are dominated by legal-follow queue items, especially followed legislation sources.

That is a valid typed path, but it is not yet a proof that the broader multi-source Bush event graph remains inspectable end-to-end.

Stated differently:

- the receipt certifies queue/review/tranche geometry
- it does not yet certify event/relation/legal-context geometry from the corpus/public-bios substrate

## Concrete Findings

### Finding A

Multi-source GWB extraction is real and already adds non-handoff relations.

### Finding B

The typed receipt boundary is now correct.

### Finding C

The main flatness hotspot is upstream of receipt attachment:

- corpus snippet generation
- event anchoring
- broader-review source row normalization
- checkpoint merge

### Finding D

The broader-review artifact is currently better at review routing than at proving event-level lineage.

## Recommended Next Tests

### 1. Timeline depth test

Require at least one inspectable path of:

`source path/url -> emitted event -> promoted relation -> merged seed lane or review row`

for each of:

- `public_bios_timeline`
- `corpus_book_timeline`

### 2. Historical anchor test

Reject corpus/public-bios timeline artifacts that contain only ingest anchors for events that also contain explicit historical years or dates in text.

### 3. Broader-review preservation test

Require at least one broader-review source row to preserve an explicit upstream event identifier and source citation reference, not only a family-level support label.

### 4. Candidate/promoted distinction test

Assert that candidate-only semantic relations remain distinguishable from promoted relations after broader-corpus merge and broader-review normalization.

## Recommended Next Implementation Tranche

Highest-alpha next work:

1. build a cross-document event braid over the local GWB corpus and public sources
2. preserve `source -> local_event -> cross_source_event_or_edge -> review` lineage into broader-review rows
3. extend the linkage contract so receipt coverage can refer to event/legal context layers, not only queue/review/tranche layers
4. improve historical anchoring and snippet filtering after the braid substrate exists

The dedicated follow-on contract is:

- `docs/planning/gwb_cross_document_event_braid_20260705.md`

## Working Invariant

The current true invariant is:

`GWB receipts certify a projected review linkage path, but not yet a historically reliable multi-source event timeline path.`

The next target invariant is:

`GWB broader-review evidence rows preserve an inspectable source -> local_event -> cross_source_event_or_edge -> review path.`
