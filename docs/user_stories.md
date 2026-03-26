# ITIR Suite User Stories

## Purpose
These user stories codify how ITIR, SensibLaw (SL), and StatiBaker (SB) protect
context, resist narrative coercion, and prevent evidentiary collapse when
handling adversarial corpora (e.g., large, fragmentary, reputationally charged
datasets).

## Suite-Level Invariants (Non-Negotiable)
- Context is mandatory: artifacts must never be interpreted without temporal,
  social, and epistemic frame metadata.
- Interpretation is optional: the system does not render moral or legal verdicts.
- It must be cheaper to expand context than to compress it.
- Context removal is explicit and logged.

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

---

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
ITIR preserves what happened, SL constrains what can be claimed, and SB refuses
to tell you what it means.

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
