# Repo User-Story State And Feedback Audit

Date: 2026-03-27

Purpose: assess the current state of the main repos in `ITIR-suite` against the
existing user stories, then surface the strongest likely user frustrations with:

- competitor tools / current mainstream workflows
- our current suite
- what users are likely to like / value

Important boundary:

- This document is a **repo/state audit plus proxy voice-of-user pass**.
- It is grounded in:
  - current READMEs/docs/contracts
  - existing user stories
  - current implementation coverage notes
- It is **not** the same as real interview/usability evidence.
- Real user frustration receipts still need to be gathered and persisted as a
  separate lane.
- That separate lane now has first bounded capture ergonomics through
  `SensibLaw/scripts/query_fact_review.py`:
  `feedback-add` for one receipt and `feedback-import` for local JSONL/JSON
  batches.

## Current suite-level thesis

The suite is strongest where the stories demand:

- provenance
- bounded review
- explicit uncertainty
- separation between capture, state, and semantic promotion

The suite is weakest where the stories demand:

- low-friction everyday operator UX
- polished end-to-end workflows
- selective export/handoff UI
- real user feedback loops and comparative usability evidence

That means the current suite already fits the **epistemic hygiene** part of the
stories better than the **workflow productization** part.

## Repo-by-repo state against the stories

### 1. SensibLaw

Primary story fit:

- strongest fit for the lawyer / forensic / review-heavy stories
- strongest fit for bounded comparison, review, handoff, provenance, and
  non-silent promotion

Current strengths:

- deterministic review geometry and semantic-governance layers
- bounded authority seams
- fact-review / contested-review / handoff artifacts
- explicit promotion gates and truth-bearing boundaries
- strong doctrine against silent semantic drift

Current gaps against stories:

- still too CLI/artifact/report oriented for many end users
- annotation / QA workbench remains missing
- role-specific review UX remains partial
- broader live ingest and “just use it with my real corpus” flows remain uneven
- many lanes are legible to builders, but not yet frictionless to operators

Likely user likes:

- “it keeps the source trail visible”
- “it doesn’t pretend to know more than it does”
- “I can inspect why something was surfaced”
- “disagreement and abstention are visible instead of flattened away”

Likely user frustrations with our current SL experience:

- “I still need to know too much about the internal lanes”
- “the outputs are real, but the path to them is not yet smooth”
- “too many JSON/artifact/report surfaces; not enough one obvious workflow”
- “the doctrine is strong, but the interface still feels like a research system”

Likely frustrations with competitor legal/review tools:

- opaque summarization
- weak provenance
- silent authority inflation
- ad hoc web lookup
- poor reproducibility

### 2. itir-svelte

Primary story fit:

- strongest fit for cross-corpus browsing, workbench presentation, and operator
  visibility
- main candidate web surface for turning internal artifacts into something
  actual users can inspect

Current strengths:

- corpus browser and processed-results browsing now exist
- thread viewer, personal results, broader diagnostic surfaces are live
- DB-first direction is increasingly explicit
- web transition policy is clear: this is the primary intended UI

Current gaps against stories:

- still more browse/workbench than end-to-end guided workflow
- some routes have only recently stabilized
- UX cohesion across corpora, workbenches, and downstream actions is still
  incomplete
- “what should I do next?” remains weak compared with “what is here?”

Likely user likes:

- “I can finally see what the system actually ingested”
- “processed outputs are inspectable, not hidden in internal files”
- “it is becoming possible to browse multiple corpora in one place”

Likely user frustrations with our current UI:

- “pages exist, but the overall product flow is still fragmented”
- “there are still too many specialized routes to remember”
- “the browser is useful for inspection, but not yet the whole job surface”

Likely frustrations with competitor dashboards/browsers:

- siloed data views
- no cross-corpus provenance continuity
- pretty UI without a reliable substrate

### 3. StatiBaker

Primary story fit:

- strongest fit for banker / CEO / manager / day-reconstruction stories
- strongest fit for append-only state, unresolved work, and interruption
  recovery

Current strengths:

- daily state compilation posture is clear
- append-only/read-only doctrine is strong
- SQLite/dashboard/bundle surfaces already exist
- good conceptual fit for “what changed / stalled / remains unresolved”

Current gaps against stories:

- still more infrastructure/compiler than polished operator experience
- reduction rules and carryover semantics are still under active refinement
- some important connectors and cross-product adapters remain incomplete
- strong doctrine, weaker product surface

Likely user likes:

- “it preserves reality instead of pretending to manage me”
- “it helps recover continuity after interruptions”
- “unresolved state is visible instead of rewritten away”

Likely user frustrations with our current SB experience:

- “I still need to understand the bake/build model too much”
- “it is closer to a state compiler than a finished product”
- “great internals, but not yet enough simple user-facing affordances”

Likely frustrations with competitor productivity tools:

- rewrite history
- flatten ambiguity
- incentivize false closure
- weak provenance about where state came from

### 4. TiRCorder / transcription intake

Primary story fit:

- strongest fit for capture/transcription intake stories
- useful across legal, clinical, meeting, and personal capture workflows

Current strengths:

- local/remote transcription paths
- queueing and downstream fan-out posture
- explicit relation to the rest of the suite

Current gaps against stories:

- setup/config friction remains non-trivial
- accessibility TODOs remain open
- capture-to-review path is real, but still not simple enough for broader
  less-technical users

Likely user likes:

- “recording/transcription can feed real downstream workflows”
- “it isn’t just loose transcript files”

Likely user frustrations with our current intake experience:

- “backend/config choices are still too exposed”
- “this feels powerful, but not yet effortless”

Likely frustrations with competitor transcription flows:

- transcripts stranded as dead text
- cloud lock-in
- weak provenance about model/backend/run details

### 5. reverse-engineered-chatgpt / chat corpus tooling

Primary story fit:

- strongest fit for long-term chat/context corpus stories
- useful for continuity, replay, cross-thread browsing, and later review

Current strengths:

- SQLite-first corpus posture
- thread recovery and archive browsing
- canonical-thread / archive-first thinking aligns strongly with story doctrine

Current gaps against stories:

- live fetch/auth remains brittle relative to archived data
- browser/Cloudflare/auth realities leak into the operator experience
- more robust as a corpus backend than as a seamless everyday tool

Likely user likes:

- “chat history becomes queryable and revisitable”
- “archive state is more trustworthy than ad hoc exports”

Likely user frustrations with our current chat tooling:

- “live fetch is still more fragile than it should be”
- “auth/browser recovery is still too technical”

Likely frustrations with competitor chat/history tools:

- weak export/query support
- poor continuity across platforms
- dependence on opaque vendor interfaces

### 6. OpenRecall bridge / observer capture

Primary story fit:

- useful for observer/capture augmentation
- strongest as an upstream evidence lane, not as a semantic authority surface

Current strengths:

- local-first upstream capture exists
- ITIR bridge/import path now exists
- useful for recovering activity traces and screenshot-backed context

Current gaps against stories:

- still more source lane than polished downstream user experience
- screenshot/OCR capture can become noisy without strong downstream filtering
- needs careful boundary discipline to avoid semantic overreach

Likely user likes:

- “real local capture exists”
- “I can recover what was on screen”

Likely user frustrations with our current use of it:

- “capture is there, but the downstream UX is still emerging”
- “it can feel like raw evidence, not yet a finished workflow”

Likely frustrations with competitor memory/capture tools:

- privacy concerns
- cloud dependence
- hardware restrictions
- little control over epistemic boundaries

### 7. Root repo / orchestration layer

Primary story fit:

- strongest for builders, maintainers, and cross-project integrity
- weaker as an end-user product surface

Current strengths:

- boundaries between projects are explicit
- cross-project contracts are increasingly real
- shared doctrine is a real advantage

Current gaps against stories:

- suite discoverability is still builder-oriented
- end-user value proposition is easier to infer than to experience directly
- too much of the integration story still lives in planning docs and repo
  memory rather than end-user flows

## Cross-repo frustration themes

### Competitor / mainstream workflow frustrations

These are strongly supported by the current story set:

- opaque AI outputs with weak provenance
- silent rewriting of uncertainty into confidence
- poor context boundary control
- weak auditability/reproducibility
- data silos between capture, review, and state
- polished UX but epistemically dangerous internals

### Our current suite frustrations

These are the most likely recurring complaints today:

- too much builder-facing complexity
- too many parallel surfaces before one obvious path
- artifacts and receipts are strong, but user flows are uneven
- some repo layers are mature as substrates but not yet as products
- actual user feedback is under-instrumented; we infer too much from doctrine
  and internal usage

### What users are most likely to like

- explicit provenance
- explicit uncertainty
- no silent promotion
- cross-project traceability
- ability to reopen and inspect
- local-first / bounded / reproducible posture

## Current honest product-positioning answer

The suite is currently strongest as:

- a provenance-first review and state substrate
- a bounded evidence/corpus/workbench environment
- a builder/operator system for high-consequence material

It is not yet strongest as:

- a polished end-user workflow product across all personas
- a low-friction mainstream productivity app
- a finished cross-role collaboration suite

## Missing evidence

The biggest missing artifact is not another doctrine note. It is:

- real user feedback receipts

Specifically missing:

- structured interviews
- frustration inventories
- “what do you hate about your current tools?” captures
- “what is confusing / brittle / annoying about our system?” captures
- “what do you actually love / keep returning for?” captures

## Recommended next step

Add a bounded feedback-receipt lane with three classes of evidence:

1. Competitor frustration receipts
- short structured captures about existing workflows/tools

2. Our-suite frustration receipts
- route/feature/task-specific pain points

3. Delight / retention signals
- what users actively prefer and why

Minimum contract:

- user role/persona
- task attempted
- current tool/workflow used
- frustration kind
- severity
- exact quoted complaint
- desired outcome
- source/provenance and date

This should become a first-class bounded dataset, not just lore in chats.
