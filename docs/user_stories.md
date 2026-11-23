# ITIR Suite User Stories

## Purpose
These user stories codify how ITIR, SensibLaw (SL), and StatiBaker (SB) protect
context, resist narrative coercion, and prevent evidentiary collapse when
handling adversarial corpora (e.g., large, fragmentary, reputationally charged
datasets).

## Suite-Level Invariants (Non-Negotiable)
- Context is mandatory: artifacts must never be interpreted without temporal,
  social, and epistemic frame metadata.
- Interpretation is optional: the system does not silently promote moral, legal,
  clinical, causal or other domain conclusions from observation alone.
- It must be cheaper to expand context than to compress it.
- Context removal is explicit and logged.
- Observation, occurrence, report, interpretation, review/admission and
  authority remain distinct states.
- Missing/failed/stale coverage is not negative evidence.
- Every derived/displayed semantic value must remain navigable to exact source
  revision/anchor and its transformation/review dependencies.
- A timeline, proof tree, Sankey/ribbon, citation graph and source pane are
  projections, not independent truth stores.

---

# ITIR (Interpretive / Temporal Record)

## ITIR-US-01: Context-Bound Artifact Viewing
As a user, I want to view any artifact only within its original context so that
meaning is not distorted by temporal or situational drift.

Acceptance criteria:
- Every artifact view shows date/time, venue/medium, intended audience, and
  known public facts at the time.
- Raw excerpt viewing is not the default.
- Removing context requires an explicit user action with a warning.

## ITIR-US-02: Epistemic State Overlay
As a user, I want to see what was knowable at the time an artifact was created
so I can distinguish hindsight judgment from contemporaneous knowledge.

Acceptance criteria:
- Timeline overlays show public knowledge, legal status, and investigative
  status at the time of creation.
- Later revelations are visually separated.
- UI labels distinguish "known then", "known later", and "unknown at time".

## ITIR-US-03: Context Drift Detection
As a user, I want the system to flag when an artifact is interpreted outside
its original frame so I can recognize when meaning may be distorted.

Acceptance criteria:
- System detects cross-audience reuse, temporal reuse beyond a configured
  context horizon, and medium shifts (private to public, comedy to moral claim).
- A warning banner indicates the drift and offers the original frame.

## ITIR-US-08: Public Media Narrative Validation
As a user, I want to drop a public media URL or transcript into ITIR so the
system can ingest it, preserve its source context, and show which parts of the
narrative are sourced, unsupported, contradictory, or still unresolved.

Acceptance criteria:
- URL/transcript ingest preserves source metadata and transcript provenance.
- Extracted narrative output distinguishes propositions, rhetoric, and
  abstentions.
- Review surfaces may include bounded workbench pages that keep transcript or
  source context visible while extracted claims are inspected in place.
- Later corroboration lanes (wiki, Wikidata, web) remain cited and reviewable
  rather than silently becoming truth.
- The system does not output an unreviewed trust score or verdict.

## ITIR-US-09: OpenRecall Capture Reuse
As a user, I want OpenRecall-style screen/OCR captures to enter ITIR as
observer-class evidence so that ambient work context can feed reviewable
activity, mission, and semantic pipelines without becoming hidden authority.

Acceptance criteria:
- Imported captures preserve app/window/time provenance.
- OCR text is available as source-local text for downstream extraction.
- Captures appear as reviewable activity evidence rather than silently
  rewriting mission or semantic state.
- Promotion from capture evidence into stronger state remains explicit.

## ITIR-US-18: Source-Addressable Semantic Node
As a user, I want every important value shown by ITIR to be traceable to the
exact source material and derivation that produced it so that I can inspect,
challenge and reuse the value without trusting a hidden summary.

Examples include a reported sample size, a bank transfer, a judgment paragraph,
a Wikidata statement, a sensor reading or a derived pattern.

Acceptance criteria:
- Hover or local inspection can show a bounded source preview with the relevant
  span/row/coordinate highlighted where the source supports one.
- Opening the item reaches the exact source revision and anchor rather than a
  generic document homepage.
- "Why?" exposes the dependency/evidence path.
- "Used where?" exposes downstream consumers.
- Citation-capable sources expose outgoing and incoming citation/source edges
  with citing context where available.
- Revision/supersession lineage and unresolved residuals are inspectable.
- Switching Explain/Why/Source/Context/Graph views does not clone or silently
  alter the underlying semantic identity.

## ITIR-US-19: Heterogeneous Cross-Stream Reconstruction
As a user, I want health/sensor observations, communications, financial flows,
documents and external world observations to align on one time/provenance
surface so I can inspect temporal relationships without the system silently
turning correlation into causation or a legal/clinical finding.

Acceptance criteria:
- Each stream retains its native source/revision/device/account/document
  provenance.
- Temporal alignment can create a candidate relationship/pattern while keeping
  each underlying observation distinct.
- Source freshness, genealogy/diversity and coverage gaps remain visible when
  relevant.
- Missing observations are never rendered as observed absence.
- Downstream consumers such as SensibLaw may interpret the aligned observations
  only through their own explicit review/admission boundaries.

## ITIR-US-20: Competing World Alternatives Without Forced Collapse
As a user, I want incompatible but still plausible interpretations to coexist so
I can investigate what evidence would distinguish them instead of having the
system prematurely merge or choose one.

Acceptance criteria:
- Candidate alternatives remain individually source-backed and inspectable.
- Selection/collapse is explicit and receipted when a domain owner authorizes it.
- An experiment/proof-search/discriminator surface may propose the next
  observation likely to separate consumer-relevant alternatives.
- A possibility/workspace selection is not silently promoted into world truth.

---

# SL (SensibLaw) - Claim Discipline

## SL-US-04: Claim Type Enforcement
As a user, I want every assertion to be typed so I can see whether I am reading
adjudicated fact, primary evidence, testimony, inference, or opinion.

Acceptance criteria:
- Untyped claims are rejected or must be explicitly typed before save/share.
- Inference claims require a linked evidence graph.
- Narrative or PR framing language is flagged.

## SL-US-05: Denial Pattern Surfacing
As a user, I want to see when denials follow shared templates so I can
distinguish independent testimony from coordinated narrative.

Acceptance criteria:
- Similar denial language is clustered and timestamped.
- Counsel or PR involvement is flagged when known.
- The system does not infer guilt; it only shows patterning.

## SL-US-08: Competing Narrative Comparison
As a user, I want to compare two competing narratives so I can see their common
facts, disagreements, predicate/flow differences, and evidentiary support
without the system prematurely choosing a winner.

Acceptance criteria:
- Shared facts/propositions are surfaced explicitly.
- Conflicting facts/propositions and reasoning links are surfaced explicitly.
- Source-local receipts remain attached to every compared item.
- Bounded comparison workbenches may expose inspector and graph drill-in views,
  but they stay scoped to the compared material rather than a global graph.
- Comparison does not silently merge incompatible narratives into one story.
- The system may abstain when overlap or disagreement is unresolved.

## ITIR-US-10: Thread-Grounded Argument Inspection
As a user, I want a workbench that keeps a conversation transcript and its
derived argument structure side by side so I can inspect claims, counterpoints,
and focused graph links without losing the underlying chat context.

Acceptance criteria:
- The transcript remains readable as chat first, not as a replaced summary.
- Claim overlays are visibly grounded in source-local text, message blocks, or
  explicit family participation.
- The inspector distinguishes claim detail, counterpoints, and focused graph
  drill-in.
- Message-level density cues and family markers help navigation without hiding
  the raw messages.
- Missing overlays or extraction gaps are shown as explicit states, not silent
  emptiness.

Detailed page deliverables for this workbench family are tracked in
`docs/planning/recent_workbench_page_user_stories_20260310.md`.

## ITIR-US-17: Wiki Revision Review Assist
As a reviewer working from Wikipedia or Wikidata-adjacent migration/dispute
pages, I want ITIR to capture a specific revision, parse its bounded sections
and cited references, and follow selected links through bounded source seams so
that difficult split/review cases become faster to inspect without treating the
wiki page itself as authority.

Acceptance criteria:
- A specific wiki revision can be captured as a revision-locked artifact with
  stable section/span anchors.
- The system can expose cited references, outbound links, and selected follow
  candidates as explicit review aids rather than hidden background crawling.
- Review surfaces distinguish page wording, extracted review constraints,
  followed source receipts, and unresolved uncertainty.
- The system can reduce reviewer uncertainty or improve reviewer speed without
  silently promoting wiki prose or followed links into semantic truth.
- Failure to resolve or follow a cited source remains explicit and reviewable.

---

# SB (StatiBaker) - Temporal Observer State

StatiBaker owns temporal reconstruction, observer memory, gaps and deterministic
replay. It may retain references/receipts from other systems but does not inherit
their semantic, legal, workspace or source authority.

# SB (StatiBaker) - Pattern Without Narrative

## SB-US-06: Reputational Exposure Map (No Verdict Mode)
As a user, I want to see networks of association, assistance, and protection
without the system implying guilt or innocence.

Acceptance criteria:
- Graphs show contact, assistance, reputation management, and timing.
- No labels like "criminal" or "predator" appear.
- Users apply their own interpretation.

## SB-US-07: Power Asymmetry Indicator
As a user, I want to see when accountability differs by status so I can
understand systemic imbalance without conspiracy framing.

Acceptance criteria:
- Status indicators include wealth, institutional protection, and legal
  insulation.
- Visual comparisons show consequences faced versus evidence volume.
- The system does not assert causality.

---

# Cross-Suite UI Invariants (Testable)

## UI-INV-01: No Context-Free Excerpts
Any excerpt rendered alone must show a warning badge.

## UI-INV-02: Interpretation Is Always Optional
The system never produces moral judgment, legal conclusion, or psychological
inference as default output.

## UI-INV-03: Expand Context Is Cheaper Than Summarize
Raw artifacts are always one click away; no irreversible compression.

## UI-INV-04: Context Removal Is Logged
Any user action that removes or suppresses context is logged with a timestamp.

---

## Design Sentence (Suite-Wide)
ITIR federates source-addressable observations and typed world material without
collapsing authority; SL/SensibLaw reviews and admits semantic/legal
interpretations; StatiBaker preserves temporal observer continuity; Casey owns
explicit workspace/candidate collapse; formal workers check bounded obligations;
projection surfaces show these objects without becoming new truth stores.

---

# Mary-Parity / Fact-Review User Stories

These stories pressure-test the current Mary-parity direction:

- `source -> excerpt -> statement -> observation -> event/fact -> review bundle`
- chronology as a review surface, not a hidden canonical model
- provenance and contestation visible at every step

They are intentionally role-shaped rather than feature-shaped so they can be
used to assess whether the current transcript/AU fact-review substrate is
actually useful to real operators.

## SensibLaw operator stories

### SL-US-09: Community Legal Centre Intake Triage
As a community legal centre intake worker, I want to ingest a client narrative,
linked documents, and call/transcript fragments into a reviewable fact bundle
so I can separate what was said, what is evidenced, what is disputed, and what
still needs corroboration before escalating the matter.

Typical flow:
- Intake worker creates a new matter-local fact-review run from interview
  notes, supporting documents, and any call or transcript material.
- Early pass is allowed to be messy: incomplete dates, partial actor labels,
  and contradictory statements remain visible.
- Worker reviews chronology and contested-item summary to decide:
  - what requires immediate safety or deadline escalation
  - what needs follow-up evidence
  - what should remain explicitly unknown

Preferences:
- Fast source/excerpt drill-down from any fact or event row.
- A review queue that explains why an item needs follow-up, not just that it
  exists.
- Clear distinction between client account, supporting document, and later
  staff annotation.

Requirements:
- Context-poor notes must not be silently upgraded into accepted facts.
- Timeline must preserve approximate/relative ordering when exact dates are not
  available.
- Export/report surfaces must remain safe for handoff to a supervising lawyer
  without erasing uncertainty.

Acceptance criteria:
- Source documents, excerpts, and statements remain drillable from every fact.
- Intake notes do not silently become accepted facts.
- Review queue highlights missing dates, missing actors, and contested facts.
- Chronology view helps triage urgent procedural windows without implying legal
  merit.

### SL-US-10: NGO Litigation Campaign Case Assembly
As an NGO legal/policy team member, I want to assemble facts from reports,
correspondence, transcripts, and public materials into a provenance-first
bundle so I can prepare strategic litigation or advocacy without flattening
uncertainty or overclaiming from partial evidence.

Typical flow:
- Team assembles a shared matter bundle from mixed public and private sources.
- Operators compare overlapping narratives, identify corroborated fragments,
  and keep unresolved contradictions live for review.
- Bundle is reused across campaign, policy, and litigation prep without
  converting advocacy framing into canonical fact.

Preferences:
- Easy separation of public-source, client-source, and internal-analysis
  material.
- Clear chronology over incidents, procedural milestones, and follow-up work.
- Reusable query/report surfaces so the same run can support several work
  products.

Requirements:
- Source class and sensitivity must remain visible in the review bundle.
- Campaign rhetoric or theory-of-change text must not be silently ingested as
  accepted fact.
- External refs may assist navigation across cases, courts, and legislation
  but must not replace reviewable evidence.

Acceptance criteria:
- Public-source and client/source-private materials remain distinguishable.
- Fact bundles preserve contested items and abstentions explicitly.
- External refs to courts, statutes, and cases assist navigation but do not
  rewrite the underlying fact substrate.
- Bundle exports remain review-oriented and do not claim a legal conclusion by
  default.

### SL-US-11: Paralegal Evidence Pack Preparation
As a paralegal, I want to turn pleadings, witness material, transcripts, and
source documents into a chronology-linked fact review run so I can prepare
hearing bundles and follow-up tasks without losing the statement-level source
trail.

Typical flow:
- Paralegal ingests pleadings, transcript extracts, and supporting documents.
- Review queue is used to identify which candidate facts still need checking,
  citation anchoring, or timeline clarification.
- Chronology report is used as the working spine for hearing bundle prep and
  internal tasking.

Preferences:
- Stable run IDs so the same run can be reopened later.
- Fact/event rows that can be copied into internal checklists without losing
  provenance.
- Clear separation between what is ready for filing/reference and what is
  still review-only.

Requirements:
- Every fact/event row must link back to source statements and excerpts.
- Reconstructed chronology must distinguish event candidates from document-only
  fact rows.
- The system must never require the paralegal to trust a hidden merge.

Acceptance criteria:
- One persisted run can be queried later by run ID.
- Review queue surfaces unreviewed and contested fact candidates clearly.
- Chronology output distinguishes event-level and fact-level ordering.
- A later operator can reconstruct each event candidate from observation
  evidence.

### SL-US-12: Solicitor Case Theory Preparation
As a solicitor/lawyer, I want to inspect a fact-review bundle that separates
observations, event candidates, and fact candidates so I can test a case theory
without confusing extracted source statements with accepted findings.

Typical flow:
- Solicitor opens an existing matter run, reviews chronology, then drills into
  observations for particular events or contradictions.
- Competing case theories are tested against the same underlying observation
  layer rather than by rewriting the substrate.
- Review statuses and contestations are updated as preparation progresses.

Preferences:
- Strong visibility of what is candidate-only versus reviewed.
- Ability to move from theory-testing back to raw text quickly.
- Clean handling of doctrinally relevant procedural/legal predicates like
  `claimed`, `denied`, `ordered`, `ruled`.

Requirements:
- Observations remain canonical and reviewable in their own right.
- Event candidates remain obviously derived from observation evidence.
- The bundle must support contradiction inspection without forced resolution.

Acceptance criteria:
- Fact candidates remain explicitly typed as candidate/reviewed/uncertain/
  abstained.
- Event candidates are visible as derived objects, not hidden internal joins.
- Contradictory statements can coexist without forced merge.
- The system never silently upgrades candidate facts into adjudicated truth.

### SL-US-13: Barrister Chronology and Contradiction Prep
As a barrister, I want a chronology-focused report over an existing fact-review
run so I can test the sequence of events, spot contradiction clusters, and jump
back to exact source text before conference or hearing.

Typical flow:
- Barrister opens a chronology report for a matter shortly before conference or
  hearing prep.
- Timeline is scanned first for sequence anomalies, date gaps, and event/fact
  collisions.
- Contested summary is then used to select contradictions worth testing in
  oral or written argument.

Preferences:
- Chronology-first presentation with dated vs undated material clearly split.
- A short contradiction/contestation summary that does not require reading the
  whole bundle.
- Minimal noise from already-resolved or low-value rows.

Requirements:
- Event chronology must preserve source-event/source-statement handles.
- Contradicted items must stay linked to their underlying statements.
- Querying a stored run must be fast and deterministic; no rerun required for
  basic prep.

Acceptance criteria:
- Chronology report shows dated vs undated events explicitly.
- Derived event rows keep source-event or source-statement provenance handles.
- Contested items are summarized separately from the main chronology.
- The report is queryable from a stored run without recomputing the extraction
  pipeline.

### SL-US-14: Judge / Associate Procedural Reconstruction
As a judicial officer or associate, I want to inspect a read-only, provenance-
first chronology bundle so I can reconstruct what was alleged, admitted,
contested, and procedurally ordered without the tool suggesting findings or
 outcomes.

Typical flow:
- Associate or judicial officer opens a read-only bundle to reconstruct a
  procedural or factual sequence.
- Procedural/legal observations are inspected alongside chronology, not hidden
  inside narrative summaries.
- Missing or disputed material is treated as an explicit part of the record,
  not silently smoothed over.

Preferences:
- Read-only posture is obvious.
- Procedural/legal predicates are easy to inspect directly.
- Clear distinction between party assertion, procedural act, and adjudicated
  position.

Requirements:
- No merits scoring, outcome suggestion, or legal reasoning overlay.
- Report must preserve provenance and explicit absence.
- Bundle must be suitable for reconstruction and orientation, not adjudication
  support.

Acceptance criteria:
- Procedural/legal observations such as `claimed`, `denied`, `ordered`, and
  `ruled` are visible as observations or attributes, not hidden summaries.
- The system distinguishes party assertions from adjudicated or procedural
  outcomes.
- Review/report outputs remain read-only and non-reasoning.
- Missing evidence or unresolved gaps appear as explicit absences.

## ITIR-general user stories

### ITIR-US-11: Personal User Memory Reconstruction
As a personal ITIR user, I want to gather scattered notes, screenshots,
messages, and transcripts into a chronology-grounded bundle so I can inspect
what happened over time without being forced into a single summary or story.

Typical flow:
- User imports a mixed set of notes, screenshots, transcripts, and fragments.
- System builds a chronology/review bundle that keeps incomplete material
  visible.
- User uses chronology and source drill-down to reconstruct events gradually,
  without pressure to settle on one interpretation.

Preferences:
- Fragments can stay partial.
- Review surfaces should privilege reconstruction and browsing over “insight”.
- Undated material should remain visible but not distort the dated timeline.

Requirements:
- The system must preserve uncertainty and abstention explicitly.
- Source fragment provenance must remain available from every derived row.
- No scoring or behavioral inference should appear in these surfaces.

Acceptance criteria:
- Fragments can remain incomplete and still appear in the chronology.
- Source/excerpt drill-down is available from each derived event/fact.
- Uncertain or abstained items remain visible rather than disappearing.
- The system does not turn personal fragments into wellness, risk, or moral
  scores.

### ITIR-US-12: General ITIR Investigative User
As an ITIR user investigating a complex situation, I want to query existing
fact-review runs and compare chronology, review queue, and contested items so I
can decide what requires human follow-up without rerunning ingestion every
time.

Typical flow:
- User ingests once, then reopens the persisted run repeatedly through query or
  report surfaces.
- Summary output is used to decide whether to inspect chronology, review queue,
  or contested items next.
- Follow-up work is tracked by reopening the same run or a descendant run, not
  by losing the original substrate.

Preferences:
- Fast query surface with compact summaries first.
- Review queue reasons should be readable and actionable.
- Chronology and contested views should be separable, not one overloaded page.

Requirements:
- Stored runs must be listable and queryable by run ID.
- Summary/report surfaces must remain descriptive and provenance-first.
- Query surfaces must not silently mutate or recompute canonical substrate
  state.

Acceptance criteria:
- Stored runs can be listed and reopened by query/report CLI.
- Summary output shows contested-item count, review-queue count, and chronology
  density.
- Review queue gives reasons such as unreviewed, contested, uncertain, or
  abstained.
- Query/report surfaces stay descriptive and provenance-first, not advisory.

### ITIR-US-13: Trauma-Survivor Safe Reconstruction
As a trauma survivor using ITIR, I want to record fragmented, uncertain, or
contradictory material into a fact/chronology substrate that preserves gaps and
contestability so I am not forced into coherence before I am ready.

Typical flow:
- User captures fragments over time with approximate or missing dates.
- Bundle preserves contradictions, partial chronology, and abstentions.
- User or trusted helper reopens the run later without the system having
  collapsed uncertainty into a cleaner but false story.

Preferences:
- “Unknown”, “not ready”, and abstained states should be normal and visible.
- Chronology should not overclaim sequence from sparse or approximate dates.
- Review surfaces should be low-pressure and provenance-first.

Requirements:
- Contradictory fragments must coexist without auto-resolution.
- Missing context must remain explicit.
- The system must not optimize for institutional readability over user safety
  and agency.

Acceptance criteria:
- “Unknown”, “not ready”, and abstained states are preserved explicitly.
- Contradictory fragments can coexist without auto-resolution.
- Chronology reports do not imply false certainty from sparse dates.
- Review bundles privilege safe reconstruction and provenance over completion
  pressure.

### ITIR-US-14: Support Worker / Advocate Timeline Assist
As a support worker or advocate helping a vulnerable user, I want a chronology
and contested-item summary that stays anchored to source fragments so I can
assist with preparation for services, complaints, or legal escalation without
speaking over the user’s uncertainty.

Typical flow:
- Advocate/support worker opens a user-approved run with chronology and
  contested summaries.
- They use chronology to identify follow-up needs, service windows, and missing
  documentary support.
- Any downstream export or handoff retains visible uncertainty and source
  grounding.

Preferences:
- Support-facing summaries should emphasize follow-up needs, not credibility
  judgments.
- User-authored statements and later annotations should be distinguishable.
- Context warnings should survive export/handoff.

Requirements:
- The support-facing view must remain read-only and provenance-first.
- Contested or unclear items must stay framed as unresolved, not suspect.
- Reporting must not flatten uncertainty to satisfy institutional preferences.

Acceptance criteria:
- Support-facing review surfaces distinguish direct user statements from later
  annotations.
- Contested or unclear items are summarized as follow-up needs, not as
  credibility judgments.
- The underlying user material remains accessible in-place.
- Exports retain context warnings and do not flatten uncertainty for
  institutional readability.

### ITIR-US-15: Personal-to-Professional Provenance Handoff
As a personal ITIR user, I want to build my own chronology and evidentiary
record first, and then pass the resulting graph/bundle to a lawyer,
psychologist, doctor, advocate, or other professional without losing context,
uncertainty, or authorship boundaries.

Typical flow:
- User reconstructs events gradually inside ITIR from notes, messages,
  screenshots, documents, and transcripts.
- At a later stage they share the run or a descendant bundle with a trusted
  professional.
- The receiving professional needs to see what is user-authored, what is
  documentary, what is later annotation, and what remains unresolved.

Preferences:
- User retains a clear sense of what originated from them versus later
  professional interpretation.
- Handoff should preserve chronology, provenance, and uncertainty rather than
  compressing into a summary memo.
- Different professionals should be able to use the same substrate for
  different purposes without rewriting it.

Requirements:
- The system must preserve user authorship, source class, and review state
  across handoff.
- It must support read-only professional inspection without silently
  converting the user’s reconstruction into institutional truth.
- Later professional notes must remain distinguishable from the original user
  record.

Acceptance criteria:
- A personal run can be reopened by a later professional without losing source
  and chronology context.
- User-authored material, documentary material, and later professional notes
  remain distinguishable.
- Handoff preserves uncertainty and abstentions rather than flattening them.
- The same substrate can support lawyer/psychologist/doctor review without
  hidden rewriting of the original record.

### ITIR-US-16: Combating AI Psychosis / False-Coherence Escalation
As a user or reviewer worried about AI systems escalating confusion,
paranoia, or false certainty into a more rigid story, I want ITIR to preserve
uncertainty, provenance, contradiction, and abstention so the system resists
turning fragmented material into a persuasive but delusion-like narrative.

Typical flow:
- User brings fragmented, emotionally charged, or high-conflict material into
  ITIR.
- System builds a chronology/review substrate without forcing strong causal,
  moral, or psychological conclusions.
- User or helper checks whether the system is preserving ambiguity rather than
  amplifying one fragile interpretation into a hardened worldview.

Preferences:
- The system should normalize “unknown”, “contested”, and “not enough evidence”.
- Source-local wording and context should remain easy to inspect.
- Derived structures should feel inspectable and reversible rather than
  mysteriously authoritative.

Requirements:
- ITIR must not reward narrative overconfidence.
- Contradictions and abstentions must remain explicit.
- The system must not generate default psychologizing, guilt, or conspiracy
  conclusions from sparse evidence.

Acceptance criteria:
- Sparse or contradictory material does not silently become a coherent single
  story.
- Provenance remains available at every layer of the derived substrate.
- Review surfaces preserve explicit uncertainty and abstention.
- The system resists false-coherence escalation rather than amplifying it.

## Wiki / public-knowledge operator stories

### SL-US-15: Wikipedia Moderator on Highly Contested Public-Figure Pages
As a Wikipedia moderator working on a highly contested public-figure page, I
want to inspect competing claims, chronology, source provenance, and legal/
reputational risk signals so I can decide whether material is sufficiently
supported, unduly defamatory, or too unresolved to remain as stated.

Typical flow:
- Moderator opens a contested run built from page revisions, cited sources,
  transcripts, and related public materials.
- They inspect chronology, disputed statements, and source grounding before
  deciding whether a claim should stay, be softened, be attributed, or be
  removed.
- They need to keep editorial moderation separate from hidden truth claims by
  the system.

Preferences:
- Fast separation between attributed allegation, procedural finding, and
  unsupported accusation.
- Clear signals when material is high-conflict, weakly sourced, or likely to
  create defamation risk if stated too strongly.
- Ability to inspect source-local wording rather than only a normalized claim.

Requirements:
- The system must not label a person guilty or defamatory by default.
- It must distinguish sourced allegation, adjudicated finding, editorial note,
  and unresolved dispute.
- High-conflict moderation should remain provenance-first and inspectable.

Acceptance criteria:
- Contested public-figure material can be inspected without collapsing into one
  canonical narrative.
- Review surfaces distinguish allegation, denial, finding, and unsupported
  assertion.
- Source/excerpt drill-down remains available for moderation-sensitive claims.
- The system supports defamation-risk review posture without rendering a legal
  conclusion.

### SL-US-16: Wikidata Ontology / Claim Worker on Contested Entities
As a Wikidata ontology worker handling contested entities and statements, I
want to inspect identity, relation, time-validity, and sourcing pressure so I
can decide whether a claim belongs, should be qualified, or should remain out
pending better evidence.

Typical flow:
- Worker reviews contested actor/case/office/jurisdiction claims alongside
  provenance and time qualifiers.
- They compare competing source support, qualifier drift, and ontology fit
  before deciding whether a statement should be modeled, time-bounded, or
  deferred.
- They need support for difficult public-figure claims where source quality and
  defamation sensitivity matter.

Preferences:
- Strong visibility of time validity, source class, and statement conflict.
- Easy comparison between mere identity facts and contentious allegation-like
  claims.
- Clear cues when a claim is structurally modellable but evidentially weak.

Requirements:
- The system must not turn contested sourcing into hidden authority transfer.
- Ontology convenience must not override provenance or moderation sensitivity.
- Time-scoped and source-scoped disagreements must remain explicit.

Acceptance criteria:
- Workers can inspect qualifier/time-validity pressure on contested statements.
- Identity/role facts stay separable from contentious action/allegation claims.
- Weakly sourced or conflict-heavy claims remain visibly unresolved.
- The system supports statement qualification and deferral logic conceptually
  without silently performing it.

### SL-US-17: Mereology / Structure Worker for Institutional or Composite Actors
As a mereology-focused ontology worker, I want to inspect part-whole,
office-holder, institution, and responsibility boundaries for contested cases
so I can model who did what, in what capacity, and on whose behalf without
flattening institutional structure.

Typical flow:
- Worker reviews a run involving governments, campaigns, companies, courts, or
  church/organizational bodies.
- They inspect actor, office, organization, and jurisdiction relations to avoid
  collapsing distinct entities into one blamed or credited actor.
- They need to preserve difficult boundaries in cases involving public figures
  and institutional responsibility.

Preferences:
- Clear separation of person, office, organization, and jurisdiction roles.
- Easy inspection of who is primary actor, co-actor, institution, or target.
- Explicit visibility of unresolved structural ambiguity.

Requirements:
- The system must not silently merge person and institution identity.
- Part-whole and office-capacity uncertainty must remain reviewable.
- Mereological structure must support later legal analysis without pre-judging
  responsibility.

Acceptance criteria:
- Institutional and personal actors remain distinguishable in review surfaces.
- Office-holder and organization relationships can be inspected without forced
  merge.
- Structural ambiguity remains explicit where the evidence is unclear.

### SL-US-18: Lawyer Assessing Legality of Public-Figure Conduct
As a lawyer trying to assess whether George W. Bush, Donald Trump, or another
public figure acted lawfully, unlawfully, or in a legally dubious way in a
highly publicized circumstance, I want a provenance-first chronology and
observation/event bundle that separates established findings, live allegations,
procedural developments, and unresolved legal predicates so I can test legal
theories without mistaking public narrative for adjudicated fact.

Typical flow:
- Lawyer opens a contested public-figure run built from transcripts, public
  records, reporting, court material, and timeline sources.
- They inspect chronology, procedural/legal observations, and source-local
  wording for incidents that appear clearly lawful, clearly unlawful, or still
  unresolved.
- They compare cases where conduct was proven unlawful against cases that are
  only alleged, disputed, or structurally dubious.

Preferences:
- Clear separation between adjudicated illegality, pleaded/alleged illegality,
  and non-adjudicated public controversy.
- Easy drill-down from legal/procedural observation to source-local evidence.
- Ability to compare one public actor lane against another without forcing one
  merged “truth” narrative.

Requirements:
- The system must remain non-reasoning and non-verdicting at this stage.
- Legal assessment work must preserve procedural status and source class.
- Publicity or repetition must not substitute for evidentiary quality.

Acceptance criteria:
- The system distinguishes proven unlawful conduct from alleged or dubious
  conduct.
- Procedural posture and legal observations are visible enough to support
  theory-testing.
- Competing public narratives do not silently become accepted legal findings.
- Source-local receipts remain attached for all high-stakes public-figure
  claims.

### SL-US-19: Wikipedia Legal-Circumstance Fidelity Review
As a Wikipedia editor or legal-fidelity reviewer, I want to compare an
article’s wording against the exact legal circumstances, procedural posture,
and trial/appellate record so I can determine whether the public article
matches the record, overstates it, or blurs distinct legal stages together.

Typical flow:
- Reviewer opens a run built from article claims, cited reporting, pleadings,
  judgments, transcript fragments, and timeline material.
- They compare article-level wording against the legal record to check whether
  an event, allegation, finding, conviction, appeal outcome, or procedural
  step is being stated too broadly or inaccurately.
- They need to preserve exactness around who alleged what, what the court
  found, what happened at trial, and what changed on appeal.

Preferences:
- Direct article-claim to legal-record comparison without losing source-local
  wording.
- Clear stage separation between allegation, charge, trial finding, appeal,
  settlement, and later commentary.
- Fast visibility into where article language compresses or distorts the legal
  record.

Requirements:
- The system must preserve legal-stage distinctions rather than flattening them
  into a single timeline claim.
- It must keep article wording inspectable alongside the legal record.
- It must not silently elevate journalistic summary into adjudicated truth.

Acceptance criteria:
- The review surface distinguishes allegation, trial finding, appellate
  posture, and later commentary.
- Article wording can be checked against source-local legal material.
- Mismatches between article phrasing and legal record remain explicit.
- The system supports fidelity review without becoming an automated editor or
  legal adjudicator.

### SL-US-20: Lawyer Using Wikipedia as a Starting Argument Surface
As a lawyer using Wikipedia or wiki-shaped public material to orient an
argument, I want the system to help me separate navigational value from legal
authority so I can trace a public narrative back to primary sources, identify
what is merely alleged or summarized, and avoid arguing from unstable or
defamatory formulations.

Typical flow:
- Lawyer starts from a Wikipedia article, public timeline, or wiki-derived
  summary while exploring a public-figure or institutional matter.
- They use the system to trace article claims and timeline assertions back to
  judgments, pleadings, transcripts, statutes, reporting, and other cited
  sources.
- They need to know what can support issue-spotting only, what needs primary
  verification, and what should not be used as legal authority at all.

Preferences:
- Fast follow paths from wiki/public claim to primary or stronger source.
- Clear warnings when a claim is only wiki-backed, journalistically summarized,
  or conflict-heavy.
- Easy comparison between public narrative and legal/procedural record.

Requirements:
- Wikipedia must remain a navigational/review surface, not silent authority.
- The system must preserve whether a statement is article wording, sourced
  legal material, or later operator note.
- It must help the lawyer avoid overclaiming from unstable public narrative.

Acceptance criteria:
- Wiki/public-source claims remain distinguishable from primary legal sources.
- The review surface helps trace a public claim toward stronger authority.
- Conflict-heavy or weakly sourced wiki claims remain visibly non-authoritative.
- The system supports issue-spotting and source follow-up without treating
  Wikipedia as legal proof.

### SL-US-21: Lawyer–Maintainer Conflict Over Wiki-Based Legal Framing
As a lawyer trying to use Wikipedia-shaped public material to advance an
framing or argument, and as a Wikipedia maintainer worried that the framing is
unsupported, defamatory, or legally overbroad, I want the system to make the
underlying provenance, legal stage, source strength, and contestation visible
enough that both sides can inspect the same record without the tool silently
choosing a winner.

Typical flow:
- Lawyer points to Wikipedia/public-summary language as support for a claim
  about what happened or what was unlawful.
- Maintainer/editor checks whether that framing overstates the legal record,
  collapses allegations into findings, or relies on weakly sourced or
  conflict-heavy material.
- Both need a shared review surface showing article wording, legal record,
  chronology, and disputed status in parallel.

Preferences:
- Shared side-by-side visibility of public wording, legal/procedural material,
  and stronger primary sources.
- Explicit cues when language shifts from allegation to finding, or from
  navigational summary to purported authority.
- Ability to inspect who is relying on which source class without hidden
  prioritization by the system.

Requirements:
- The system must not automatically privilege either the advocate’s framing or
  the maintainer’s skepticism.
- It must preserve source class, procedural posture, and stage distinctions.
- It must surface when wording becomes potentially defamatory or legally
  overbroad because the record is thinner than the framing suggests.

Acceptance criteria:
- Public-summary wording, legal record, and source class can be inspected in
  one review flow.
- The surface distinguishes allegation, finding, commentary, and editorial
  framing.
- Conflict between advocacy framing and moderation caution remains explicit.
- The tool stays provenance-first and non-adjudicative even in adversarial
  cross-role use.

### SL-US-22: Adversarial Overstatement of Legal Record
As an operator reviewing a disputed public-figure matter, I want to detect when
an advocate, journalist, editor, or lawyer is overstating what the legal
record actually supports so that allegation, suspicion, and procedural posture
do not get rewritten as proven wrongdoing.

Typical flow:
- A public summary or advocacy document uses strong language that appears to go
  beyond the pleadings, transcript, or judgment.
- Reviewer compares the strong framing against the underlying chronology and
  source-local record.
- They need to identify exactly where the overstatement occurs.

Acceptance criteria:
- Strong framing can be compared against the narrower legal record.
- The system shows where wording outruns source support or legal stage.
- Overstatement pressure is visible without the tool itself declaring the claim
  false or defamatory.

### SL-US-23: Adversarial Minimization or Sanitization
As an operator reviewing a disputed public-figure or institutional matter, I
want to detect when another actor is minimizing, sanitizing, or proceduralizing
away legally or morally serious conduct so that a misleadingly narrow public
summary can be checked against the fuller evidentiary record.

Typical flow:
- An article, brief, or statement frames serious conduct as merely disputed,
  technical, or peripheral.
- Reviewer compares that framing against source-local evidence, chronology, and
  procedural outcomes.
- They need to distinguish genuine uncertainty from strategic understatement.

Acceptance criteria:
- The system can surface when substantive source material is being hidden
  behind overly narrow public wording.
- Contested and established elements remain separately visible.
- Minimization pressure is reviewable without the tool asserting a final moral
  or legal verdict.

### SL-US-24: Source-Shopping and Narrative Cherry-Picking
As an operator working on a high-conflict public matter, I want to see when an
actor is selectively relying on weaker wiki/public sources while ignoring
stronger primary or procedural material so that narrative cherry-picking is
inspectable as a provenance pattern.

Typical flow:
- Reviewer sees a claim supported mostly by Wikipedia wording, thin reporting,
  or a subset of selective citations.
- They compare the cited path against stronger but omitted judgments,
  transcripts, pleadings, or official material.
- They need to inspect not just what was included, but what stronger source
  classes were bypassed.

Acceptance criteria:
- Source class remains visible enough to compare weak and strong support.
- The system helps identify when stronger legal sources were bypassed.
- Narrative cherry-picking remains an explicit review issue, not a hidden
  background suspicion.

## Family-law and cross-side user stories

### SL-US-25: Family-Law Client Circumstance Reconstruction
As a family-law client trying to understand my circumstances, I want a
provenance-first chronology of events, communications, filings, and child-
related issues so I can see what is actually in the record, what is disputed,
 and what still needs evidence without being forced into the other side’s
 narrative.

Typical flow:
- Client reviews a matter bundle built from messages, notes, filings, orders,
  reports, and timeline material.
- They use chronology and contested-item views to understand what each side is
  saying and what the current procedural state is.
- They need child-sensitive material handled carefully and contextualized.

Acceptance criteria:
- The system distinguishes client account, other-side account, procedural
  orders, and third-party records.
- Child-related material remains provenance-first and context-sensitive.
- Disputed events remain visible without collapsing into one party’s story.

### SL-US-26: Family-Law Lawyer Preparing Both-Sides Circumstance Review
As a family lawyer reviewing a family-law matter, I want to inspect competing
accounts from both sides, procedural history, and child-related chronology so I
can test what is agreed, what is disputed, and what can safely be put before
the court without losing source-local nuance.

Typical flow:
- Lawyer reviews a chronology built from both-side material plus court and
  third-party records.
- They compare allegation, response, order, and later compliance/non-compliance
  across the same timeline.
- They need to preserve child-sensitive distinctions and not overstate what is
  actually supported.

Acceptance criteria:
- The system keeps side A, side B, court, and third-party material distinct.
- Procedural steps and child-related issues remain visible without flattening.
- Contradictory side accounts can coexist with provenance attached.

### SL-US-27: Child-Sensitive Circumstance Review
As an operator dealing with family-law or child-impact material, I want the
system to preserve chronology and provenance while making child-sensitive
material clearly contextualized so review can happen without collapsing care,
risk, and family allegations into crude blame summaries.

Typical flow:
- Operator reviews incidents, communications, reports, and orders that touch
  on children, care, contact, schooling, or safety.
- They need to inspect what is directly evidenced, what is alleged by one side,
  and what has been procedurally recognized.
- They must avoid letting sparse or emotionally charged material harden into
  false certainty.

Acceptance criteria:
- Child-related events and records remain visible but carefully contextualized.
- The system distinguishes allegation, report, and procedural finding.
- Chronology supports safe review without turning child-sensitive material into
  flattened accusation graphs.

### SL-US-28: Provenance-Preserving Cross-Side Handoff
As an operator handing a matter bundle between sides, counsel, or support
workers, I want the graph/review bundle to pass between recipients without
losing source class, uncertainty, or party distinction so that later users do
not inherit a silently flattened or biased substrate.

Typical flow:
- One side or operator prepares a bundle for handoff to another lawyer,
  advocate, or reviewer.
- Recipient reopens the same or descended run and checks chronology, contested
  items, and provenance instead of starting from a paraphrased memo.
- They need the handoff to preserve side boundaries and uncertainty.

Acceptance criteria:
- Handoff surfaces preserve party/source distinction and review state.
- Chronology and contested items survive transfer without silent compression.
- Recipients can reconstruct why a fact/event is present from source-local
  evidence.

## Professional-discipline / medical overlap stories

### SL-US-29: Medical Negligence Circumstance Review
As a lawyer, advocate, or reviewer working on a medical-negligence or
healthcare dispute, I want to inspect treatment events, consent/warning
material, injury chronology, and competing clinical narratives so I can
separate what happened, what is documented, what is alleged, and what remains
medically or legally contested.

Typical flow:
- Operator reviews records, notes, correspondence, expert summaries,
  transcript fragments, and later procedural material.
- They compare treatment chronology, communication/warning issues, and injury
  consequences against the available record.
- They need to keep clinical documentation, patient account, later expert
  interpretation, and procedural posture distinct.

Acceptance criteria:
- Treatment, warning/communication, harm, and chronology can be reviewed
  together without forced merge.
- Clinical record, patient account, and later interpretation remain
  distinguishable.
- The system supports negligence-oriented review without silently performing
  negligence reasoning.

### SL-US-30: Professional Discipline / Regulatory Record Review
As a lawyer, regulator, journalist, or professional-discipline reviewer, I
want to inspect allegations, responses, findings, sanctions, and institutional
structures in a provenance-first bundle so I can reconstruct whether a matter
concerns mere complaint, active investigation, disciplinary finding, or later
public narrative drift.

Typical flow:
- Operator reviews complaint material, regulator correspondence, hearing
  outcomes, tribunal/court material, and public reporting.
- They compare what was alleged, denied, admitted, found, and sanctioned.
- They need to preserve professional role, office, institution, and procedural
  stage distinctions.

Acceptance criteria:
- Complaint, investigation, finding, and sanction stages remain distinguishable.
- Professional role and institution are not silently merged.
- Public narrative and regulatory record can be compared without hidden
  authority transfer.

### SL-US-31: Corpus-to-Affidavit Coverage Review
As a lawyer or paralegal preparing an affidavit from a client corpus, I want
the system to preserve a high-recall, provenance-first extraction substrate and
compare it against the affidavit draft so I can see what is represented, what
is only partially represented, what appears to be missing, and what is still
too ambiguous or contested to promote.

Typical flow:
- Operator ingests mixed client material such as interview notes, documents,
  correspondence, and transcripts into one matter-local substrate.
- A draft affidavit or declaration is then reviewed against that substrate
  rather than replacing it.
- The operator works through coverage rows that show supported, partial,
  omitted, contested, and abstained source-grounded material before filing.

Preferences:
- High recall is preferable to early over-cleaning, as long as provenance and
  status remain visible.
- Affidavit propositions should be traceable back to exact source rows and
  spans.
- Omission review should be grouped into actionable buckets rather than one
  undifferentiated backlog.

Requirements:
- Dense source-grounded extraction must remain separate from later affidavit
  comparison status.
- Ambiguous or contested source material must not be silently treated as
  affidavit omissions.
- The comparison surface must preserve document, span, statement, and run
  lineage so later reviewers can audit why an item was marked covered, partial,
  missing, or abstained.

Acceptance criteria:
- Each affidavit proposition can link back to one or more source-grounded rows
  or be marked unsupported explicitly.
- Source-grounded rows above the configured review threshold that do not appear
  in the affidavit are surfaced as omission-review items.
- Contested, ambiguous, or abstained source rows remain visibly distinct from
  clear omissions.
- The review surface stays provenance-first and does not claim the affidavit is
  legally sufficient or complete by default.

## AO-OP-1 — Canonical operator evidence-to-handoff (implementation slice)

Source-written, pending caller verification: a read-only `itir.ao.operator_workflow` composes canonical frontier/ledger, typed references, bounded PNF packet, governed handoff and operation review for ITIR-US-11/12/15/16. Operator acceptance: explicit canonical task and provenance; bounded source digests and candidate disposition; holds for ambiguity/unverified semantic or formal evidence; no bodies, mutation or automatic resend. This is shared workflow infrastructure, **not** full acceptance of any UI story or a verified semantic parser. See `docs/planning/ao_operator_workflow_v1.md`.

AO-OP-1 acceptance follow-up: uniquely canonical admitted tasks now yield deterministic actionable **review-only** handoffs even without optional PostgreSQL materialisation or a semantic PNF producer. A trusted producer resolver can attest verified-PNF in direct composition; ordinary governed MCP output remains explicitly unverified/candidate-only until a real verifier is wired. This closes operator review access without claiming semantic promotion, create-thread support, or autonomous dispatch.

---

## Proof search and formal verification operator stories

### SLR-US-01 / ITIR-US-18: Formal Multiset Gap Check Operator (PNF-to-AST Residual Accounting)
As a formal verification researcher or proof-search operator, I want to compute
the exact difference between informal research thread claims and formal
Agda/Lean AST factors ($\Delta_{\text{Gap}} = M_{\text{informal}} \setminus M_{\text{formal}}$)
via `itir.ao.gap_check` so I can identify unformalized premises (Alpha targets)
and ungrounded formal assertions without guessing.

Typical flow:
- Operator specifies a canonical research conversation ID and an active formal
  specification file (e.g. `dashi_digital_esd/ITIRPNFAssessment.agda` or Lean 4
  theorem file).
- `itir.ao.gap_check` extracts the compiled PNF semantic multiset from the
  research thread and the syntactic AST multiset from the formal file.
- The multiset difference is computed, classifying factors into matched,
  unmatched informal (missing premises), and unmatched formal (unaddressed
  constraints).
- The operator reviews top missing premise signatures and targets them for the
  next formal proof step.

Preferences:
- Direct multiset accounting summary table with clear factor signatures.
- Ranked list of top unformalized premises with recommended formalization
  targets (e.g., add lemma constraint or hypothesis bound).
- Fast execution over local or pre-compiled PNF world stores.

Requirements:
- Gap computation must be strictly read-only and deterministic.
- Zero-residue provenance comparison doctrine: informal claims without formal
  AST counterparts must never be marked verified.
- Status must fail closed to `RESIDUAL GAP DETECTED` unless exact multiset
  equality holds.

Acceptance criteria:
- `itir.ao.gap_check` returns structured reports and markdown summaries
  matching the `ExactGapComparator` contract.
- Missing informal factors are explicitly distinguished from unaddressed formal
  invariants.
- Zero proof authority is transferred without an AST-level match.

### SLR-US-02 / ITIR-US-19: SLR Candidate-Only Proof Search Spine & Exploration Lattice
As a mathematician or theorem search operator, I want to explore candidate proof
paths through an SLR-backed candidate search lattice (AutoInAgda, Lean Mathlib
cache, external prover runner) while ensuring that every proof step emits a
verifiable receipt and candidate hold, so that no informal LLM step is mistaken
for a kernel-checked theorem.

Typical flow:
- Operator initiates proof search over a formal target (e.g. Navier-Stokes,
  Riemann Hypothesis reduction, or Quantum Mereology lemma).
- Prover spine expands candidate proof branches, ranking tactics and candidate
  lemmas.
- Candidate steps are held as `candidate_only` until an independent kernel
  verifier produces an execution receipt.
- Negative results, dead ends, and syntax/sort errors are explicitly recorded in
  the candidate ledger to prevent infinite search loops.

Preferences:
- Tree and branch visualization separating unverified explorations from
  kernel-accepted nodes.
- Explicit display of proof search budget, depth, and remaining open goals.
- Direct link from search nodes to exact line/column AST coordinates.

Requirements:
- Kernel verifier receipts are strictly external: LLM output or search path
  generation cannot self-certify correctness.
- Incomplete proof trees or unproven `sorry`/`admit` postulates must be flagged
  with open formal gap status.
- Proof receipts must reference immutable artifact CIDs or SHA-256 digests.

Acceptance criteria:
- Candidate proof paths remain strictly partitioned from authoritative lemmas.
- Invariant violations (e.g. serde in compiler crates or invalid sort signatures)
  halt promotion and emit actionable diagnostic holds.
- Full provenance trace is preserved from informal informal premise to formal
  tactic.

### SLR-US-03 / ITIR-US-20: Multi-Prover Bridge & Remote Prover Runner (Colab / GPU Container)
As a prover pipeline operator, I want to dispatch bounded proof check jobs to a
remote runner (Colab Agda/Lean runner or ITIR GPU container) and ingest
verifiable execution receipts (`artifact-resolution-receipt/v1`, typecheck logs,
AST factors) back into the canonical frontier without attaching unverified code
to `main`.

Typical flow:
- Operator submits a batch of formal modules or proof patches for remote
  typechecking.
- Remote runner executes parallel checks (e.g., `run_agda29_parallel_check.sh`
  or `lake build` against cached Mathlib oleans).
- Runner returns a structured execution receipt with return code, elapsed time,
  stderr diagnostics, and artifact hash.
- Front-end imports the receipt into the candidate ledger, updating the status
  of dependent candidate operations.

Preferences:
- Support for parallel execution across independent formal subtrees.
- Transparent reuse of pre-compiled Mathlib caches and Agda libraries.
- Headless, non-interactive batch execution with clear progress heartbeats.

Requirements:
- Remote runner must never execute arbitrary unreviewed shell code outside
  sandboxed execution boundaries.
- Stderr/stdout logs must be captured with exact line and column error bounds.
- Typecheck failure must produce an explicit hold receipt rather than crashing
  the orchestration loop.

Acceptance criteria:
- Bounded verification runs complete within configured timeout budgets.
- Verification receipts satisfy `artifact-resolution-receipt/v1` schema.
- Failed modules (such as sort mismatches) are isolated without contaminating
  verified modules.

### SLR-US-04 / ITIR-US-21: Spectral & Algebraic Invariant Packet Extraction
As a formal methods researcher working on complex dynamics, fluid mechanics, or
physics models, I want to extract candidate spectral packets
(`itir.spectral.candidate_packet`) from algebraic structures to evaluate
harmonic and topological invariants before formalizing them in Agda/Lean.

Typical flow:
- Researcher selects an algebraic system or triad complex.
- `itir.spectral.candidate_packet` computes eigenvalues, spectral projections,
  and candidate algebraic invariants.
- The resulting candidate packet provides quantitative bounds that inform formal
  lemma formulation.
- The packet is attached as review-only evidence to the formalization work packet.

Preferences:
- Clean decomposition into spectral components, trace bounds, and energy
  landscapes.
- Explicit comparison between empirical/spectral data and formal constraints.

Requirements:
- Spectral packets are review surfaces and heuristic guides, not formal proofs.
- Mathematical assumptions and precision tolerances must be documented in the
  packet metadata.

Acceptance criteria:
- Tool returns valid candidate spectral packets without mutating canonical state.
- Packets carry non-authoritative review boundaries and full computation receipts.

### SLR-US-05 / ITIR-US-22: Governed Actor–Critic PR Lifecycle & Commit-Bound Verification
As a repository maintainer, I want candidate commits from remote generative actors
to pass an independently verified, commit-bound promotion protocol with typed
restorative critiques so that generative exploration cannot self-certify or
bypass local governance.

Typical flow:
- Remote generative actor explores candidate implementations/proofs and pushes an
  immutable commit SHA to a feature branch or draft PR.
- Local cooperative discriminator fetches the exact commit and executes
  deterministic checks (`cargo test`, `agda`, `pytest`, `ruff`) plus scope and
  sovereignty gates.
- If checks fail, the discriminator emits a minimal, deterministic critique
  residual (`slr.referee-critique.v1`) containing exact failing checks, source
  coordinates, expected-vs-observed values, and an evidence digest.
- If checks pass, the discriminator records a commit-bound verification receipt
  binding the exact commit SHA, verifier identity, checker digest, and dependency
  closure digest.

Preferences:
- Zero conversational filler in failure critiques; exact compiler/prover/test
  coordinates and digests only.
- Explicit separation between actor preliminary self-tests and independent
  referee certification.

Requirements:
- Actor output is strictly candidate-only (`ActorGenerated(x) !=> Verified(x)`).
- Verification receipts are bound to an immutable commit SHA; pushing a new commit
  invalidates promotion eligibility unless an explicit verified reuse rule applies.
- Merge eligibility requires all mandatory checks and policy gates (`TestsPass(c)`
  alone does not imply `MergeSafe(c)` if unauthorized schema/policy changes exist).

Acceptance criteria:
- Every actor submission and referee receipt identifies an immutable commit SHA
  and dependency closure digest.
- Failed checks produce typed diagnostic holds and minimal critique residuals.
- The actor cannot authorize its own promotion, and replaying identical receipts
  does not create duplicate authoritative transitions.

### SLR-US-06 / ITIR-US-23: Context-Insulated State Commons & Deterministic Snapshot Capsules
As a distributed research agent, I want to receive compact, content-addressed
state capsules projected from the single PostgreSQL semantic spine and retrieve
supporting historical evidence on demand so that work can continue without
transferring sprawling conversation histories.

Typical flow:
- Local coordinator queries the single PostgreSQL spine
  (`sensiblaw_sparse_ready_20260818`) under a consistent snapshot (`REPEATABLE READ`)
  to project a canonical `StateCapsule`.
- Dispatcher transmits a compact event trigger (~100-200 tokens) referencing the
  capsule's canonical digest, active frontier revision, and obligation ID.
- Remote actor uses the state capsule to orient immediately and retrieves raw
  source spans, logs, or proof artifacts by digest only when required.
- Before promoting any resulting candidate, the referee verifies optimistic
  concurrency compatibility between the capsule's frontier revision and the
  current active frontier.

Preferences:
- Three-tier separation: (1) compact event trigger, (2) PostgreSQL state snapshot,
  (3) on-demand historical evidence in canonical SQLite/source stores.
- Preservation of pointers to relevant negative evidence and reopening history so
  context compression never masks prior failed proof attempts or disputed premises.

Requirements:
- Do not introduce a second orchestration database; project directly from
  existing `slr_world_v2_*`, `formal_bridge.*`, and `resolution.*` relations.
- Original chat transcripts remain in canonical SQLite (`~/.chatgpt_history.sqlite3`);
  PostgreSQL stores semantic references and evidence lineage without duplicating
  raw transcript bodies.
- Context compression must never erase active protected formal obligations
  (`ActiveProtected(H, r) <= SnapshotFrontier(H, r)`).

Acceptance criteria:
- Every state capsule carries a protocol version and length-prefixed canonical
  SHA-256 digest; reconstructing the same state produces the identical digest.
- Concurrent frontier updates cannot silently invalidate promotion assumptions.
- Protected singleton obligations and negative-evidence pointers survive snapshot
  compression without loss.

### SLR-US-07 / ITIR-US-24: Federated Capability & Local Machine Sovereignty Enforcement
As a participating node operator in a federated mesh, I want to delegate bounded
capabilities to remote generative agents while retaining strict local sovereignty
over command execution, database persistence, and branch promotion.

Typical flow:
- Participating nodes advertise explicit capability sets (`generate`, `search`,
  `propose` for remote actors; `verify`, `review`, `authorize`, `persist` for
  local referees).
- Remote actor proposes candidate branches and structured packets within its
  scoped capability window.
- Local sovereignty gate validates capability scope, expiry, and command
  allowlists before running local verification or persisting approved receipts.

Preferences:
- Capability-constrained peer federation rather than a monolithic hidden
  centralized supervisor.
- Idempotent receipt ingestion with full provenance attribution.

Requirements:
- Repository and corpus content must be treated as untrusted data to defend
  against prompt injection and malicious test commands.
- Protected database operations and schema migrations require explicit local
  authorization.
- Duplicate, expired, revoked, or forged capability/receipt messages must fail
  closed.

Acceptance criteria:
- Remote actors cannot execute unauthorized local commands or self-certify
  promotions.
- Every accepted state transition records an attributable actor, verifier
  principal, and authorization receipt.
- Nodes can contribute independently verified artifacts across the mesh without
  surrendering local machine sovereignty.

### SLR-US-08 / ITIR-US-25: Condensed Formal Preflight, Similarity Routing & Candidate-Only Interactive Proof States
As a governed proof-search operator, I want a lean MCP facade over the existing
dashi-agda-preflight diagnostic, similarity, routing and isolated kernel-check
capabilities so that interactive proof exploration remains candidate-only while
the local referee retains independent certification authority.

Typical flow:
- Actor requests `formal.inspect` for a module or obligation: the adapter
  condenses `diagnose`, `next_error`, `affected`, `related_symbols`,
  `discover`, and `round_lineage` into bounded diagnostics with exact
  retrieval references for complete underlying evidence.
- Actor requests `formal.route`: existing `proof_route_for_obligation` and
  DA51 bridge produce exact target-prover demands without creating proof authority.
- Actor optionally requests `formal.refine`: Agda interaction-JSON or Lean LSP
  supplies goals, contexts and candidate hole refinements; every response is
  `candidate_only=true`, `establishes_proof=false`.
- Local discriminator invokes `formal.certify`: existing `certify_artifact`
  and isolated Agda/Lean shadow runners verify an immutable artifact, and
  `validate_kernel_handoff` checks the resulting handoff before any formal
  evidence is considered for payment or promotion.
- The native SLR referee receipt binds the exact commit, source digest,
  checker/environment/dependency digests, authenticated verifier identity,
  and check outcome. Critiques retain exact diagnostic evidence by digest.

Requirements:
- Public MCP surface remains four task-oriented operations
  (`formal.inspect`, `formal.route`, `formal.refine`, `formal.certify`);
  internal preflight tools are not individually re-exported.
- Do not reimplement preflight indexing, similarity, proof routing or kernel
  certification in `itir-mcp`; invoke the existing dashi-agda-preflight owner.
- Interactive goal inspection and similarity matches are never kernel receipts;
  `formal_resolver` must not interpret a Boolean or lexical match as proof.
- No actor-controlled claim of successful certification can self-authorize
  promotion; authenticated local referee evidence and policy gates are required.
- Condensed payloads are bounded, deterministic, source-addressable and include
  digests for lossless on-demand recovery; 90% reduction is a benchmark target,
  not a license to drop blocking errors or protected obligations.
- Local files, database schemas, runner commands and credentials remain within
  the sovereign node's capability boundary.

Acceptance criteria:
- Candidate-only goal/refinement/similarity receipts cannot discharge formal
  obligations even when they report success or exact signature equivalence.
- Source changes after checking invalidate certification; stale commit,
  environment or dependency digests fail closed.
- Isolated kernel handoff validates artifact, statement, checker and dependency
  identities; failures produce deterministic `slr.referee-critique.v1` holds.
- Large diagnostics return bounded summaries plus retrievable immutable evidence
  references; protected singleton obligations and negative evidence survive.
- Replay and duplicate delivery are idempotent; no duplicate proof payment.
- The local referee can run fixture tests with no external interactive MCP
  installed; optional Lean/Agda interactive adapters fail closed to unavailable.

---

## Wiki and public-knowledge operator integration stories

### WIKI-US-01 / SL-US-38: Wikidata Statement Review Packet & Batch Review Surface
As a Wikidata contributor or ontology custodian, I want to inspect candidate
statement edits and entity modifications through `itir.wikidata.review_packet`
and `itir.wikidata.object_review_bundle` with strict validation and no silent
repair, ensuring zero unreviewed mutations to live Wikidata.

Typical flow:
- Contributor imports an entity statement bundle or batch edit proposal.
- `itir.wikidata.review_packet` validates statements, qualifiers, references,
  and item links against strict schema constraints.
- The operator inspects discrepancies, missing references, and qualifier drifts
  in a structured review surface.
- Edits are approved or rejected individually; approved candidates emit review
  receipts for external batch transport.

Preferences:
- Clear separation between observed item state, candidate modification, and
  validation receipt.
- Fast drill-down into property datatypes, rank qualifiers, and reference URLs.
- Bulk review queue grouping similar statement modifications.

Requirements:
- Review packet operations must be strictly read-only (`mutates: false`).
- Validation mode must be strict: malformed statements must be rejected, not
  silently repaired or normalized without provenance.
- Tool must never execute autonomous writes to live Wikidata endpoints.

Acceptance criteria:
- Candidate entity edits produce review receipts adhering to
  `itir.wikidata.review_packet.v1`.
- Validation errors include exact property and statement IDs.
- Canonical entity truth remains untouched.

### WIKI-US-02 / SL-US-39: WikiProject Tooling & Governance Profiles
As a WikiProject coordinator or community moderator, I want to evaluate external
bot and batch tools (QuickStatements, OpenRefine, EntitySchemas, KrBot, Listeria,
Property Constraints) against governed authority profiles
(`itir.wikiproject.tooling_profile`), mapping tool capabilities and risk
classes so that batch updates remain strictly diagnostic and candidate-only.

Typical flow:
- Coordinator reviews proposed automation or batch ingestion toolchain.
- `itir.wikiproject.tooling_profile` returns the governance taxonomy, tool
  capabilities ($\kappa$), output classes ($O$), and authority bounds ($B$).
- System verifies that tools with high write impact (e.g. QuickStatements) are
  constrained to `candidate_only: true` and `promotion_enabled: false`.
- Diagnostic and repair tools (OpenRefine, Listeria) are assigned appropriate
  review-only and receipt-mirroring profiles.

Preferences:
- Clear categorization of tools into batch transport, repair, schema, bot,
  ingestion, and constraints.
- Formal profile cards showing tool capabilities and promotion boundaries.

Requirements:
- Tool authority profiles must prevent autonomous promotion (`self_promotes: false`).
- Outputs must be classified as `candidate` or `diagnostic`.
- Governance profiles must be versioned and verifiable.

Acceptance criteria:
- `itir.wikiproject.tooling_profile` emits complete governance descriptors
  matching `itir.wikiproject.tooling_profile.v1`.
- All 6 core WikiProject tool families are accurately represented with their
  operational boundaries.

### WIKI-US-03 / SL-US-40: Ontology Constraint & Disjointness Violation Triaging
As an ontology maintainer, I want to run disjointness audits (e.g., P2738
disjoint union, Q24017414 second-order classes, P8225 metaclasses) across
entity graphs, surfacing constraint violations and structural flatness
diagnostics before proposing ontology migration candidates
(`itir.wikidata.migration_candidate`).

Typical flow:
- Maintainer targets a contested ontology branch or high-violation property
  (e.g., calendar year disjointness or metaclass hierarchies).
- System executes constraint audit across entity slices, detecting pairwise
  disjointness collisions and order confusion.
- Maintainer inspects flatness diagnostics and evaluates whether statements
  should be qualified, split, or migrated.
- Migration proposals are exported as non-authoritative candidate bundles.

Preferences:
- Visual representation of disjointness clashes and ontology hierarchy depth.
- Quantitative violation counts and hotspot ranking.
- Export of candidate repair statements with source justification.

Requirements:
- Audits must preserve conflicting evidence rather than forcing false consensus.
- Disjointness violations must be flagged as structural pressure, not deleted
  unilaterally.
- Migration candidates must carry provenance linking back to the audit run.

Acceptance criteria:
- Constraint audits accurately detect P2738 and class-order violations.
- `itir.wikidata.migration_candidate` emits well-formed candidate migration
  bundles without mutating live ontology.

### WIKI-US-04 / SL-US-41: Cross-Corpus Wiki-to-SensibLaw Evidence Reconciliation
As a legal or journalistic investigator, I want to project Wikipedia/Wikidata
entity graphs into SensibLaw timeline and claim review surfaces
(`sl.wikidata_signal_review_bundle.v0_1`) alongside transcripts and public
filings, separating crowd-sourced assertions from primary source evidence
without collapsing into single-narrative bias.

Typical flow:
- Investigator loads a contested public affair or litigation subject into
  SensibLaw.
- Wikipedia article revision history and Wikidata statements are ingested via
  governed adapters into `sl.wikidata_signal_review_bundle.v0_1`.
- Chronology overlay places wiki claims alongside primary documents, court
  rulings, and verified corporate filings.
- Investigator filters claims by source authority, distinguishing crowd-sourced
  allegations from primary evidence.

Preferences:
- Source-weighted timeline ribbon highlighting contemporaneous vs retrospective
  wiki edits.
- Side-by-side comparison of wiki claim wording against primary source texts.
- Defamation and reputational risk flags on weakly sourced public-figure claims.

Requirements:
- Wikipedia text must never be treated as legal proof or primary evidence.
- Edit timestamps must be preserved to track narrative drift over time.
- All wiki-derived claims must carry clear `candidate` or `review_surface`
  authority tags.

Acceptance criteria:
- Wiki entities and claims integrate seamlessly into SensibLaw review bundles.
- Primary evidence and crowd-sourced claims remain strictly segregated in the UI.
- Narrative drift and retroactive edits are clearly surfaced on the timeline.
