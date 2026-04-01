# User Story Alignment And Reprioritization

Date: 2026-04-02

Purpose: record the first major post-substrate user-story alignment pass after
the reusable Python/store/runtime campaign reached near-completion.

## Read

The suite is no longer primarily blocked by substrate ambiguity.

The strongest remaining gaps are now story-fit and operator workflow gaps:

- guided next-step UX
- annotation / QA workbench depth
- real user feedback collection beyond proxy/story notes
- capture/transcription setup friction and accessibility
- continuity tooling that is strong on local archives but still uneven on live
  fetch and recovery

This means the next execution rounds should optimize for user stories and
operator workflows, not continue broad substrate refactoring by default.

## What is now strong enough to treat as baseline

- SQLite/canonical-store posture across the recent SensibLaw normalization
  lanes
- explicit provenance / receipt doctrine
- normalized review geometry across AU, Wikidata, and GWB
- fact-review workbench/read-model/operator-view surfaces
- feedback receipt receiver/query/capture baseline
- repo-owned path/runtime helpers for SQLite, repo roots, and manifest loading

## Current story-fit read by surface

### SensibLaw

Strong now:

- bounded review, comparison, provenance, and explicit abstention
- fact-review workbench payloads and operator views
- portable follow/review control-plane posture
- bounded personal handoff and protected-disclosure lanes

Still weak:

- annotation / QA workbench for humans doing real review loops
- role-specific guided workflows rather than builder-oriented CLI/report paths
- smoother real-corpus ingest into those review surfaces

### itir-svelte

Strong now:

- browse/inspect surfaces for processed results and workbench-linked outputs
- canonical web direction is clear
- feedback capture and drill-in exists in the personal-results lane

Still weak:

- "what should I do next?" is not explicit enough
- workflow cohesion across routes is still fragmented
- the browser is still more inspectable than operable

### StatiBaker

Strong now:

- doctrine fit for append-only continuity and interruption recovery
- conceptually strong state/reduction posture

Still weak:

- builder/infrastructure posture still outruns operator product surface
- carryover/reduction refinement still matters to day-state trust
- cross-product ergonomics remain partial

### TiRCorder / intake

Strong now:

- capture/transcription can feed real downstream lanes
- local/remote intake posture exists

Still weak:

- setup/config friction
- accessibility backlog
- capture-to-review path is still not simple enough for broader operators

### Chat/history tooling

Strong now:

- archive-first SQLite/corpus posture
- long-term continuity/replay support

Still weak:

- live fetch/auth/browser recovery remains too brittle
- operator trust is much higher for archives than for live continuity

## Reprioritization rule

For the next phase:

1. user-story workflow gaps first
2. evidence-backed prioritization second
3. substrate work only when a story lane is genuinely blocked by missing
   canonical infrastructure

This is a real priority inversion from the last phase.

## Top priority lanes after this pass

### P0

- guided workflow / next-action surfaces in `itir-svelte`
- annotation / QA workbench and reviewer execution flow over existing
  fact-review/read-model surfaces
- feedback-receipt ergonomics and real evidence gathering beyond proxy notes
- wiki reviewer-packet + citation-follow workbench completion for the split
  assist / review-heavy story family
- personal escalation workflow productization over the existing bounded
  handoff/disclosure adapters

### P1

- capture/transcription setup and accessibility hardening
- chat/live-continuity reliability improvements
- SB operator ergonomics over the existing continuity substrate

### P2

- remaining optional route-shell cleanup
- further substrate normalization only when it clearly unlocks a blocked story

## Orchestrated nonblocking analysis lanes

The post-substrate user-story pass splits cleanly into these read-only lanes:

- SensibLaw operator/review story fit
- `itir-svelte` workflow/guided-action fit
- StatiBaker continuity/operator fit
- TiRCorder intake/accessibility fit
- chat/history continuity fit

The orchestrator owns the cross-suite synthesis and final promotion order.

## Next implementation recommendation

The strongest next implementation lane is not another generic substrate helper.
It is a guided workflow surface that turns existing browse/workbench state into
one obvious next action for operators.

The second strongest lane is the first real annotation/QA workbench slice over
the existing fact-review/operator-view/read-model spine.

## Worker readback summary

### SensibLaw lane

- strongest still-partial stories:
  - wiki reviewer packet / split-assist completeness
  - personal escalation workflow completeness
  - integrator-facing packaging/contract clarity

### `itir-svelte` lane

- strongest still-partial stories:
  - guided next-step UX
  - cross-route workflow cohesion
  - workbench execution rather than inspection-only browsing

### StatiBaker lane

- strongest still-partial stories:
  - polished operator continuity surface
  - carryover/reduction trust
  - cross-product adapter completeness

### TiRCorder lane

- strongest still-partial stories:
  - setup/config simplification
  - accessibility completion
  - simpler capture-to-review flow

### Chat/history lane

- strongest still-partial stories:
  - local archive as the visible default continuity surface
  - less brittle live continuity fallback
  - presentation-grade continuity output rather than raw tool posture

## Governance posture

- ITIL:
  - move from architecture stabilization into service/workflow improvement
- ISO 9000:
  - prioritize operator-visible quality gaps, not only internal structure
- ISO 42001 / NIST AI RMF:
  - keep feedback/provenance visible and separate proxy evidence from direct
    user evidence
- ISO 27001 / ISO 27701:
  - keep personal/protected-disclosure boundaries explicit while improving UX
- ISO 23894:
  - treat guided workflow and continuity gaps as operational risk factors
- Six Sigma:
  - reduce operator friction and route fragmentation now that process variance
    in the substrate is much lower
- C4:
  - product/workflow surfaces now become the main container-level focus, while
    the substrate remains the stable supporting layer
