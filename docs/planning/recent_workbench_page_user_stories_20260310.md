# Recent Workbench Page User Stories And Deliverables (2026-03-10)

## Purpose
Define user-facing expectations for the recent `itir-svelte` workbench pages so
future implementation passes have one concrete reference for functionality and
appearance.

This note is intentionally page-facing. It complements the canonical suite
stories in `docs/user_stories.md` and the FriendlyJordies proving-case note in
`docs/planning/friendlyjordies_narrative_validation_and_competing_narratives_20260309.md`.

## Related context
- `docs/user_stories.md`
- `docs/planning/friendlyjordies_narrative_validation_and_competing_narratives_20260309.md`
- `docs/planning/recent_page_audit_20260309.md`
- `itir-svelte/README.md`

## Shared graph-review model
These workbench pages share one review posture even when their source artifacts
are different.

Common rules:
- Each page has one `primary review object`:
  - thread claim/family for `/arguments/thread/[threadId]`
  - compared proposition/wrapper row for `/graphs/narrative-compare`
  - selected article/window for `/graphs/wiki-revision-contested`
- Graph views are always secondary review surfaces, never the orientation
  surface.
- Each page preserves one `selection bridge` across:
  - source artifact, row, or message
  - detail/inspector pane
  - bounded graph subview
- Graph drill-in is local by default:
  - it centers on the current review object
  - it does not widen to a corpus/global graph unless the user explicitly asks
    for broader context
- Returning from graph detail is lossless:
  - same selected object
  - same thread/row/article context
  - same scroll position or local focus when feasible
- Hover remains transient; stable review state comes from explicit selection.
- Empty, missing, unsupported, or unavailable graph states are designed review
  states rather than exceptions.

Shared selection-bridge rule:
- The inspector/detail pane is the authoritative explanation of the current
  selected object.
- Source text/rows and graph views echo that selected object rather than
  competing with it.
- Graph selection may update the primary review object only when the newly
  selected node remains inside the current bounded review scope.

## User Story 1: Thread-Grounded Argument Review
As a reviewer, I want to read the canonical chat transcript and inspect
argument extraction in place so I can move from raw conversation to normalized
claims without losing source context.

Primary page:
- `/arguments/thread/[threadId]`

Success posture:
- The transcript remains the primary artifact.
- Overlay content helps me inspect claims, not replace the chat with a derived
  summary.
- Selection, provenance, and graph drill-in stay scoped to the currently
  selected claim family.

### Functional deliverables
- `Canonical transcript loads in message order with source provenance intact`
  - Resolve a stable thread identity before rendering the workbench.
  - Show messages in canonical chronological order, not ingestion order or
    heuristic grouping order.
  - Expose enough header provenance to answer what thread this is, where it
    came from, and why it is the canonical record.
  - If the route was opened through a non-canonical identifier, still resolve
    and make the canonical target explicit.
  - Show missing rows, partial transcript availability, or source ambiguity as
    explicit loader states rather than silent degradation.
- `Claim/fact/wrapper overlays are selectable from the transcript`
  - Anchor overlays to visible transcript content or to a clearly labeled
    message/block fallback when exact spans are unavailable.
  - Keep claim, fact, attribution wrapper, and counterpoint overlays distinct
    even when they share a family.
  - Selecting an overlay establishes one active review object that the rest of
    the workbench follows.
  - Do not emit overlays from family keyword fanout alone; they need
    message-grounded justification.
  - If an extracted object cannot be anchored responsibly, expose it as
    unanchored metadata rather than pretending it is text-local evidence.
- `Literal vs family highlighting modes are defined and visually distinguishable`
  - `Literal` means exact text span, bounded sentence, or explicit
    message-block fallback tied to a source-local claim.
  - `Family` means that the message participates in the same argument family,
    not that it literally states the selected claim.
  - Switching modes changes highlight semantics without discarding the current
    selection.
  - Explain the difference between modes in terse UI copy so users do not
    mistake family participation for literal provenance.
  - Make mixed anchor quality visible instead of flattening all highlights into
    one style.
- `Inspector tabs expose claim detail, counterpoints, and focused graph state`
  - `Claim` shows normalized claim text, source surface text, provenance,
    confidence or anchor quality, and receipts/snippets.
  - `Counterpoints` shows competing or qualifying claims from the same thread
    or family, including abstentions where relevant.
  - `Graph` shows a bounded graph centered on the current claim family, not
    the entire corpus.
  - Tab switching preserves the active claim selection.
  - Tabs with no meaningful data explain why rather than collapsing.
- `Selection stays synchronized between transcript, inspector, and any graph drill-in`
  - Clicking a transcript highlight selects the same object in the inspector
    and graph.
  - Selecting from the inspector scrolls the transcript to the relevant
    message/span.
  - Graph selection stays scoped to the current claim family unless the user
    explicitly broadens context.
  - Multi-select, if supported, has clear rules for primary versus secondary
    comparison objects.
  - Selection state survives harmless UI actions like mode switches or tab
    changes.
- `Message-level badges and family markers summarize argumentative density without replacing the chat`
  - Per-message badges summarize how many reviewable objects are anchored to
    that message.
  - Family markers show recurrence or density across the thread without
    asserting that every marked message says the same thing.
  - Counts reflect grounded anchors for the active mode rather than inflated
    family membership.
  - Dense-message summaries help navigation instead of competing with message
    reading.
  - Badge logic degrades cleanly when extraction coverage is partial.

### Appearance deliverables
- `Transcript remains chat-first and readable without overlays enabled`
  - Chat bubbles, message spacing, role differentiation, and timestamps remain
    legible before any semantic layer is considered.
  - Overlay controls do not visually dominate the conversation on initial
    load.
  - Long threads still read like a conversation rather than a report or table.
  - Disabling or hiding overlays leaves a coherent plain-transcript
    experience behind.
  - Text wrapping and line-height prioritize reading quoted discussion over
    aggressive compactness.
- `Highlights are visually distinct from normal text selection and from one another`
  - Hover, selected, inactive, literal, and family states each have separable
    styling.
  - Browser text selection is not confused with semantic highlighting.
  - Claim types differ enough that users can tell whether they are looking at a
    claim, wrapper, counterpoint, or family echo.
  - Weak anchors or fallback blocks look less precise than exact spans.
  - Highlight styling suggests evidence review, not confidence or verdict.
- `Badges/gutter markers are compact and non-noisy on dense threads`
  - Dense discussions do not become a wall of chips.
  - Gutter signals summarize recurrence without pulling attention away from
    message content.
  - Badge density has a visual ceiling so one overloaded message does not
    distort the whole thread.
  - Markers remain scannable during quick scrolling.
  - Family color or icon systems remain comprehensible when several families
    are present.
- `Selected claim state is obvious in both transcript and inspector`
  - The active transcript anchor is unmistakable.
  - The inspector clearly shows which transcript selection it represents.
  - Users never have to infer whether the right pane is stale.
  - Graph focus reinforces the same active object rather than introducing a
    competing selection state.
  - Deselection or no-active-claim state is visually calm and explicit.
- `Empty/unavailable states explain why no overlay exists instead of looking broken`
  - Distinguish between no extraction attempted, extraction unavailable, thread
    unsupported, and nothing anchorable found.
  - Keep copy short but diagnostic enough for review work.
  - Plain transcript mode still looks intentional when overlays are absent.
  - Empty states do not resemble loading failures.
  - Unsupported lanes explain the current proving-case boundary.
- `Graph drill-in feels scoped and local, not like a full context switch`
  - The graph tab reads as a focused extension of the selected claim rather
    than as a new app.
  - Layout, labeling, and back-navigation preserve the sense that the
    transcript remains primary.
  - The graph enters at a family-centered frame rather than a global zoomed-out
    universe.
  - Opening graph detail preserves selection continuity.
  - The graph panel visually inherits the workbench context instead of resetting
    the user’s mental model.

### User flow
Primary review flow:
1. Open the thread route and orient on thread title, provenance, and overlay
   controls.
2. Read the transcript as chat first before selecting any derived object.
3. Notice highlight, badge, gutter, or mini-map cues that suggest argumentative
   density.
4. Select one grounded overlay from the transcript.
5. Inspect the `Claim` tab for normalized claim text, provenance, and receipts.
6. Move to `Counterpoints` to inspect competing or qualifying material without
   losing the active selection.
7. Open the bounded `Graph` tab for the same claim family.
8. Return to the transcript with selection and scroll position preserved.

Fallback flows:
- Supported thread, no anchorable overlays:
  - transcript still loads as the primary artifact
  - the page explains that extraction exists but could not be responsibly
    anchored
  - unanchored metadata remains secondary and clearly labeled
- Unsupported thread:
  - plain transcript remains usable
  - the page explains that the current overlay lane is limited to the present
    proving scope
- Mode switch:
  - changing `Literal` to `Family` preserves the selected claim
  - only highlight semantics and emphasis change

### Visual structure
- Top header strip:
  - thread title
  - canonical thread id and source identity
  - raw-thread link
  - overlay mode toggle and any density/filter controls
- Main split:
  - primary left transcript column
  - secondary right inspector column
- Transcript chrome:
  - subtle gutter lane for family markers
  - inline highlight layer inside message content
  - message badges near bubble header or edge
- Optional bottom mini-map:
  - recurrence overview across the thread
  - jump navigation by family or density cluster
- Mobile behavior:
  - transcript remains first
  - inspector collapses into a secondary sheet/tab rather than competing for
    equal width

### Visual language
- Typography stays readable and review-oriented rather than dashboard-like.
- Provenance/context colors stay distinct from disagreement and error colors.
- Literal and family highlighting differ by more than hue; fill, border, or
  texture also signals the difference.
- Weak anchors look less precise than exact spans.
- Dense information compresses via grouping and progressive disclosure rather
  than tiny unreadable chips.
- Primary reading objects get more spacing than secondary diagnostics.
- The overall tone is an inspection workbench: deliberate, bounded, and calm.

### Interaction contract
- Single click selects an overlay and sets the active review object.
- Hover previews normalized claim text and anchor quality without changing the
  active selection.
- Selecting in the inspector scrolls or re-centers the transcript on the
  originating message/span.
- Tab switching preserves the active selected claim.
- Graph selection never silently broadens scope beyond the current family.
- Mode toggles preserve selection and change only highlight semantics.
- If multi-select exists, one primary claim remains visually dominant and
  secondary selections are clearly marked.
- Keyboard focus order follows header -> transcript -> inspector.
- Focus, badge, and marker semantics are conveyed with text/state labels, not
  color alone.

### State matrix
- `loading transcript`
  - route identity is visible
  - transcript body and inspector remain visibly pending rather than empty
- `transcript ready, overlays available`
  - transcript reads normally
  - badges/highlights/markers are active
  - inspector invites claim selection or shows the current one
- `transcript ready, no overlays`
  - transcript remains primary
  - page explains whether no extraction was available or nothing anchorable was
    found
- `claim selected`
  - one anchor/message is visibly active
  - inspector and graph context match that object
- `claim selected, graph tab open`
  - graph remains family-local
  - transcript position and claim selection stay intact
- `unsupported thread`
  - plain transcript still renders
  - overlay controls are disabled or scoped with explanatory copy
- `partial extraction / unanchored metadata`
  - transcript shows only responsibly anchored overlays
  - unanchored derived objects remain inspectable but clearly secondary

### Graph and review flow
- The transcript is the orientation surface and remains the first reading
  object.
- The first meaningful selection comes from a transcript highlight, a badge, a
  gutter marker, or a mini-map jump.
- After selection, the right-pane inspector becomes the stable review anchor.
- `Claim` is the default landing tab after transcript selection.
- `Counterpoints` is a same-family adjacent review, not a separate selection
  universe.
- `Graph` is a bounded family-centered graph focused on the selected claim.
- The graph distinguishes at least:
  - selected claim
  - supporting links
  - undermining or counter links
  - attribution or wrapper relations
- Graph opening starts focused on the current family, not zoomed out to
  everything available in the thread.
- Selecting a graph node inside the same bounded family updates inspector state
  and transcript scroll target.
- Selecting a graph node outside the current bounded family is not implicit:
  either disallow it in v1 or require an explicit expand-context action.
- Leaving the graph returns the user to the same transcript claim position.

Graph/review appearance specifics:
- The selected transcript span and selected graph node share one visual family.
- The inspector acts as the authoritative current-selection surface; transcript
  and graph echo it.
- Hover in the transcript can preview but must not steal stable selection from
  graph or inspector state.
- Counterpoints need related but distinct styling from direct supports.
- Family mode broadens transcript emphasis while graph mode remains bounded to
  the selected claim family.
- If multi-select appears later, graph remains single-primary-selection in v1
  and compare semantics stay inspector-led.

Graph/review state specifics:
- `no selection yet`
  - transcript is primary
  - inspector invites selection without pretending a current claim exists
- `claim selected, claim tab active`
  - selected transcript anchor and claim pane agree
- `claim selected, counterpoints tab active`
  - counterpoint list stays bound to the current family
- `claim selected, graph tab active`
  - graph focus and transcript anchor remain synchronized
- `graph unavailable for selected claim`
  - graph tab explains why it is unavailable without discarding the rest of the
    review context
- `family mode on with one primary selected claim`
  - transcript broadens visually
  - graph focus remains local to the selected claim family
- `unanchored metadata available but no graphable local family`
  - metadata stays inspectable
  - graph state is absent intentionally rather than looking broken

## User Story 2: Competing Narrative Comparison
As a reviewer, I want to compare competing narrative variants so I can see
shared material, disputed propositions, and source-local receipts without the
system silently merging them into one story.

Primary page:
- `/graphs/narrative-compare`

Success posture:
- The page distinguishes common ground from disagreement.
- Every compared item keeps local provenance.
- The page may abstain when overlap or disagreement is unresolved.

### Functional deliverables
- `Shared vs disputed propositions are separated explicitly`
  - Present common ground, source-only material, and disputed material as
    distinct buckets.
  - Let users tell whether narratives agree on substance but differ in wording,
    or genuinely conflict.
  - Keep predicate disagreement, target disagreement, and reasoning-flow
    disagreement separate where possible.
  - Do not collapse source-specific propositions into disagreement by default.
  - If the system cannot classify an item responsibly, abstain rather than
    forcing it into shared/disputed bins.
- `Each compared item keeps source-local receipts/provenance`
  - Every row retains which narrative side it came from and what local text
    supports it.
  - Provenance survives normalization; normalized claim text alone is
    insufficient.
  - Receipts include enough context to review the claim without losing source
    locality.
  - When an item is derived from attribution or wrapper structure, that
    provenance remains visible.
  - Missing provenance is shown as a deficiency rather than hidden.
- `Attribution wrappers and authority links remain inspectable`
  - Structures like `X said that...` and `authority held that...` remain
    first-class objects.
  - Distinguish source speaker, cited authority, and proposition content.
  - Wrapper inspection helps users see whether disagreement is about who said
    something, what was said, or whether the authority link exists.
  - Do not flatten authority-linked items into plain fact rows unless the UI
    labels that flattening explicitly.
  - Preserve enough structure for later proposition-link widening.
- `Users can trace how a selected difference maps back to source text`
  - Selecting a disputed item exposes the text or snippet that produced it on
    each side.
  - Make clear whether the difference comes from wording, target, stance, or
    missing support.
  - Let users follow one selected difference through claim detail, receipts,
    and any bounded graph or proposition view.
  - Traceability still works when the compared narratives are asymmetric in
    detail.
  - Derived comparison labels never outrun the user’s ability to inspect the
    receipts behind them.
- `Comparison abstains cleanly when overlap is weak or unresolved`
  - Weak overlap, sparse evidence, and ambiguous normalization have an explicit
    abstention path.
  - Abstention preserves what was compared and why no stronger classification
    was made.
  - Low-overlap cases do not resemble successful high-signal comparisons.
  - The page avoids inventing pseudo-conflicts from poor extraction or sparse
    receipts.
  - Abstention is visible at both row level and whole-comparison level where
    appropriate.
- `Graph/claim subviews stay bounded to the compared material, not the full corpus`
  - Graph drill-ins remain comparison-local.
  - The page does not pull users into unrelated propositions or broader corpora
    unless they explicitly ask for expansion.
  - Claim detail and graph views are alternate representations of the same
    bounded comparison set.
  - Navigation back to the main comparison is immediate and lossless.
  - The page preserves the distinction between a comparison workbench and
    global graph tooling.

### Appearance deliverables
- `Visual grouping makes shared/common material easy to distinguish from conflicts`
  - Shared rows look calm and consolidated.
  - Disputed rows read as active review items rather than merely recolored
    shared rows.
  - Source-only material sits visually between shared and disputed states.
  - Group headings and section ordering support fast top-down review.
  - Users can scan the page and answer where the narratives agree before
    reading every row.
- `Disputed rows look different from merely source-specific rows`
  - A true conflict has stronger visual treatment than a proposition that only
    appears on one side.
  - Predicate conflict, target conflict, and missing-counterpart rows do not
    all share one generic disputed look.
  - Styling reduces false impressions of contradiction.
  - Visual hierarchy helps users distinguish contested from unmatched.
  - Conflict styling stays serious and review-oriented rather than theatrical.
- `Receipts and provenance are visible without dumping raw JSON by default`
  - The default view exposes enough support to inspect a row without opening
    developer payloads.
  - Receipts can be compact, but they are not hidden behind raw-only
    affordances.
  - Provenance labels are readable and close to the compared item.
  - Advanced raw payload inspection can exist, but it is not required for
    normal review.
  - Dense receipt areas still preserve text legibility.
- `Comparison panes support dense review without collapsing into a debug wall`
  - Use grouping, spacing, and bounded detail sections to support long
    comparisons.
  - The layout supports careful review of many items without becoming visually
    flat.
  - Secondary metadata stays visible but subordinate to the comparison itself.
  - Users do not have to mentally parse one long machine-shaped list.
  - Repeated structural elements feel consistent enough to scan quickly.
- `Colors and labels reflect claim posture rather than implying verdict`
  - Shared, disputed, source-only, attributed, and abstained items use
    semantics that describe review posture rather than truth status.
  - Labels avoid sounding like system adjudication unless that is actually
    supported.
  - The page does not imply one narrative is the winner just because its rows
    are more numerous or more saturated.
  - Color semantics remain usable even when receipts or metadata are expanded.
  - Any confidence-like signal is clearly about extraction/provenance quality,
    not truth.
- `Empty sections use informative copy, not blank panels`
  - A page with no shared material, no disputes, or no wrappers states that
    explicitly.
  - Empty states explain whether the absence reflects the data, the comparison
    result, or an unsupported lane.
  - Blank space does not carry the burden of interpretation.
  - Sections with no content still preserve page rhythm and readability.
  - Low-signal comparisons still look intentional and complete.

### User flow
Primary review flow:
1. Open the comparison route and orient on source A, source B, and the overall
   comparison posture.
2. Scan summary counts or section headers for shared, disputed, source-only,
   and abstained material.
3. Review shared material first to establish common ground.
4. Move to disputed items and select one difference.
5. Inspect receipts and provenance for both sides.
6. Open attribution-wrapper or authority detail where relevant.
7. Open a bounded claim or graph subview for the selected difference.
8. Return to the main comparison without losing the selected comparison
   context.

Fallback flows:
- Low-overlap comparison:
  - page enters an abstention-forward posture
  - comparison still explains what was compared and why stronger classification
    was not made
- Sparse one-sided provenance:
  - rows remain reviewable
  - provenance weakness is visible rather than silently flattened
- Wrapper-heavy comparison:
  - users can inspect whether disagreement is about authority/speaker
    structure rather than proposition text

### Visual structure
- Header band:
  - source A identity
  - source B identity
  - comparison posture or fixture context
- Summary band:
  - shared count
  - disputed count
  - source-only count
  - abstained count
- Main review sections:
  - shared/common material first
  - disputed material second
  - source-specific material third
  - wrappers/authorities adjacent to the relevant propositions rather than
    buried as an appendix
- Detail model:
  - expandable rows or a bounded side pane for receipts, provenance, and claim
    detail
- Graph/claim drill-in:
  - remains nested within the comparison page rather than taking over the route

### Visual language
- Shared, disputed, source-only, and abstained rows each have distinct row
  grammar, not merely different badge text.
- Wrappers and authority-linked items look structurally different from plain
  propositions.
- Typography and spacing prioritize scanning dense review output over dashboard
  theatrics.
- Provenance colors stay distinct from disagreement colors.
- Color semantics avoid truth/winner signaling.
- Dense receipt blocks use bounded expansion and grouping to preserve
  legibility.

### Interaction contract
- Selecting a row opens receipts and provenance without navigating away from the
  comparison context.
- Drill-in to claim or graph detail is explicit, not automatic.
- Switching focus between source sides preserves enough context to compare both
  narratives.
- Wrapper and authority rows remain expandable without flattening their
  structure into plain text.
- Abstained items can still be opened and reviewed.
- Keyboard focus follows summary -> comparison rows -> detail pane.
- Focus and row state are visible in text and structure, not only by color.

### State matrix
- `loading comparison`
  - source identities are visible
  - main sections show pending state rather than blank panels
- `high-overlap comparison`
  - shared material dominates first view
  - disputed rows remain clearly separated
- `low-overlap abstention`
  - abstention copy is prominent
  - weak overlap does not masquerade as a normal shared/disputed comparison
- `one-sided sparse provenance`
  - rows remain visible
  - provenance weakness is called out locally
- `wrapper-heavy comparison`
  - wrapper/authority structures remain first-class and legible
- `no comparable output / unsupported lane`
  - page explains whether the issue is unsupported input, missing comparison
    artifacts, or genuinely empty output

### Graph and review flow
- The page opens on grouped comparison material rather than on graph detail.
- The primary review object is a selected shared, disputed, source-only, or
  wrapper row.
- Row selection first opens claim, receipt, and provenance detail in place.
- Graph subview is explicitly invoked from that selected row.
- The graph centers on the selected proposition or wrapper relationship.
- Graph contents stay limited to:
  - the selected row’s proposition family
  - direct provenance or attribution edges
  - directly competing or qualifying nodes
- Source A and source B identity remain visible inside graph/detail flows and
  are not flattened away.
- Returning from graph detail restores the same comparison section and row
  focus.
- Wrapper-heavy items preserve speaker, authority, and proposition content as
  distinct review roles rather than one flattened text blob.
- Abstained rows may still open detail, but graph availability is explicit and
  may be absent.

Graph/review appearance specifics:
- Shared, disputed, source-only, and abstained rows each use consistent row
  grammar and matching graph-node posture.
- Source A and source B identity persist visually inside both detail and graph
  views.
- Graph detail feels embedded beneath or beside the selected row context rather
  than like a route change.
- Receipts and provenance remain visible while graph is open or stay one click
  away in the same pane.
- Selecting a different row resets graph focus cleanly to the new local review
  object.
- Graph colors express role, posture, and provenance rather than winner/loser
  semantics.

Graph/review state specifics:
- `no row selected`
  - summary/group sections are primary
  - detail pane remains instructional rather than empty
- `shared row selected`
  - common-ground detail is primary
  - graph, if present, stays comparison-local
- `disputed row selected`
  - dispute detail and provenance are primary
  - graph emphasizes direct conflict/qualification structure
- `wrapper row selected`
  - speaker/authority/proposition roles remain structurally distinct
- `abstained row selected`
  - abstention reasoning is explicit
  - graph may be unavailable without treating the row as an error
- `graph available for selected row`
  - graph reinforces the selected local comparison object
- `graph unavailable but receipts/detail available`
  - comparison remains reviewable through text-local provenance
- `unsupported/low-overlap comparison with abstention-forward detail only`
  - page remains complete and intentional without graph equivalence

## User Story 3: Contested Evidence Window Inspection
As a reviewer, I want to inspect a bounded contested Wikipedia revision window
so I can see whether a graph exists, why it might not exist, and which revision
pairs or regions the page is summarizing.

Primary page:
- `/graphs/wiki-revision-contested`

Success posture:
- The page always makes the selected pack, run, and article explicit.
- Graph-bearing runs, non-graph packs, missing-payload cases, and producer
  failures are visually and semantically distinct.
- The page helps the reviewer inspect bounded contested material instead of
  implying a general Wikipedia verdict.

### Functional deliverables
- `Pack/run/article state is always visible`
  - Keep the currently selected pack, run, and article visible across all page
    states.
  - Do not make users infer whether a blank graph is due to a different article
    or a failed run.
  - Surface pack identity because some packs are graph-enabled and some are
    not.
  - Keep route parameters and the effective selected tuple synchronized.
  - Support deep links that remain self-explanatory when revisited later.
- `UI distinguishes graph_ready, graph_not_enabled, missing_graph_payload, producer_error, and no_graph`
  - `graph_ready` means a graph payload exists and is displayable.
  - `graph_not_enabled` means the selected pack/run class does not emit this
    graph lane by design.
  - `missing_graph_payload` means a graph should exist under the contract, but
    the payload is absent or not hydrating.
  - `producer_error` means the run/article failed upstream and the page is
    reflecting that failure.
  - `no_graph` means the run/article is valid but no contested graph was
    produced for the selected article/window.
- `Selected article detail shows the primary pair and supporting run metadata`
  - Article detail remains useful even when no graph is present.
  - The primary pair, scoring basis, article status, and supporting run facts
    help the reviewer understand what the page is trying to show.
  - Pair detail helps distinguish interesting pairs with no graph from nothing
    happened.
  - Supporting metadata stays attached to the article detail rather than being
    scattered across the page.
  - The page preserves the relationship between run-level summary and
    article-level detail.
- `Region/cycle/top-graph summaries stay synchronized with the selected article`
  - Do not show stale top-graph or cycle summaries from a different
    article/run context.
  - Selected article changes consistently update summary and detail sections.
  - Summary absence is meaningful and local to the current selection.
  - Treat cross-section inconsistencies as loader/read-model defects, not as
    tolerated drift.
  - Article detail, top summaries, and graph detail all describe the same
    bounded evidence window.
- `Artifact-backed payloads and DB-backed payloads are both valid sources when the contract allows`
  - The page does not care whether the selected graph came from DB persistence
    or artifact reconstruction, as long as the contract is satisfied.
  - Preserve enough source metadata to explain what was loaded.
  - Reviewers can see whether they are looking at a persisted graph, a
    manifest-backed graph, or no graph at all.
  - Source-type differences surface only when they change what can be
    reviewed.
  - Fallback source resolution does not silently downgrade state semantics.
- `Route behavior is robust to stale/error runs and does not silently present them as empty success`
  - Old error-only runs render as explicit diagnostic states.
  - Partially populated runs do not masquerade as healthy no-graph cases.
  - Preserve as much valid summary and article detail as exists even when graph
    detail is missing.
  - Loader recovery prefers explicit state classification over optimistic
    emptiness.
  - The UI never asks the user to infer from absence whether the producer
    failed.

### Appearance deliverables
- `State panels are prominent and interpretable at a glance`
  - Keep the selected article state near the top and visually unambiguous.
  - A reviewer can tell quickly whether they are looking at a healthy graph, a
    disabled lane, a missing payload, or a producer failure.
  - State styling is not subtle enough to miss during quick scanning.
  - The panel summarizes state without forcing the user to parse all downstream
    sections first.
  - State visuals remain consistent across different run/article tuples.
- `Summary metrics are visually separated from diagnostic/error copy`
  - Numeric summaries do not visually imply graph availability on their own.
  - Counts and state explanations stay close enough to relate but distinct
    enough not to blur together.
  - Error or contract-gap copy does not drown out useful summary metrics that
    still exist.
  - A failed or disabled graph state still leaves readable run summary
    information.
  - The page avoids the failure mode where numbers look healthy but the actual
    artifact state is broken.
- `Graph-present vs graph-absent states are clearly different`
  - A graph-ready page feels materially different from a no-graph or error
    state.
  - When a graph is absent, the empty space is intentional and explained rather
    than just a missing canvas.
  - Graph panels, summaries, and detail areas reinforce whether a reviewable
    graph exists.
  - The layout does not tempt users to think a graph failed to load when the
    real state is not enabled or no graph.
  - Visual differentiation supports diagnosis rather than ornament.
- `Detail sections degrade gracefully when cycles/regions/pairs are absent`
  - Empty lists still render as valid sections with useful copy.
  - The page keeps structural rhythm even when multiple subsections have no
    data.
  - Missing cycles, regions, or high-severity pairs do not collapse the page
    into awkward gaps.
  - The absence of one detail class does not obscure the presence of another.
  - Degraded states remain scannable and calm.
- `Page hierarchy makes run summary, article detail, and graph detail easy to scan`
  - Section order matches how a reviewer answers the page’s main questions:
    what run is this, what article is selected, is there a graph, and what are
    the most important summaries.
  - Headings, cards, and spacing support both quick triage and deeper
    inspection.
  - The page does not force equal visual weight on every subsection.
  - High-signal sections are easy to locate repeatedly across different states.
  - Metadata density does not destroy scanning order.
- `Producer failures and contract gaps look intentional and diagnostic, not like generic missing content`
  - Error states use language and styling that identify the class of problem.
  - Contract gaps are distinguishable from upstream producer errors.
  - The UI communicates that this is a reviewable failure mode rather than that
    the page simply broke.
  - Diagnostic states still fit the overall page design instead of appearing as
    unstyled exceptions.
  - Reviewers come away knowing what failed, not merely that something is
    absent.

### User flow
Primary review flow:
1. Open the route with the selected `pack`, `run`, and `article`.
2. Confirm the selected tuple and current article state from the top of the
   page.
3. Scan run summary metrics.
4. Inspect selected article detail and the primary pair.
5. Review top-graph, cycle, and region summaries.
6. Inspect graph detail if the page is in `graph_ready`.
7. If no graph is present, use the state panel and article detail to diagnose
   why.

Fallback flows:
- `graph_not_enabled`:
  - the state panel explains that the selected pack does not emit this lane by
    design
  - summary and article detail remain reviewable
- `producer_error`:
  - the page shows the producer failure as a first-class diagnostic state
  - valid summary/article fields remain visible where available
- `missing_graph_payload`:
  - the page explains that the contract implied a graph should exist but the
    payload is absent
  - artifact/DB source information remains visible
- `no_graph`:
  - the page shows that the run/article is valid but produced no graph for this
    selected window

### Visual structure
- Header band:
  - pack
  - run
  - article
  - DB/artifact source context when relevant
- Top state panel:
  - first high-signal object on the page
  - explains the current article state before the user reads metrics
- Second band:
  - run summary metrics
- Main body:
  - article detail before graph detail
  - top graphs/cycles/regions as summary cards
  - graph canvas/detail area only when graph data is actually available
- Empty/error cards:
  - occupy the same structural slot as graph detail so absence feels
    intentional

### Visual language
- State classes use distinct card tone and labeling:
  - `graph_ready`
  - `graph_not_enabled`
  - `missing_graph_payload`
  - `producer_error`
  - `no_graph`
- Metric cards never visually override the state card.
- Diagnostic cards remain precise and review-oriented rather than alarmist.
- Graph-present and graph-absent layouts feel materially different.
- Empty subsections retain the same page grammar instead of collapsing into
  awkward whitespace.
- Typography and spacing support quick triage first, detailed review second.

### Interaction contract
- Changing the selected article updates state, summary, and detail sections
  coherently.
- State panel updates immediately with the effective selected tuple.
- Graph detail controls are hidden or disabled in non-graph states.
- Pair selection, if present, stays synchronized with article detail.
- Artifact-backed and DB-backed payloads follow the same interaction model
  unless the available data actually differs.
- Keyboard focus follows tuple/header -> state panel -> summary -> article
  detail -> graph/detail sections.
- State semantics are never color-only; labels and explanatory copy remain
  visible.

### State matrix
- `loading / unresolved tuple`
  - tuple identity is still visible
  - state panel and detail sections show pending placeholders
- `graph_ready`
  - graph detail occupies the main detail slot
  - summary and article detail reinforce the same bounded window
- `graph_not_enabled`
  - state card is primary
  - graph canvas is replaced by explicit explanatory copy
- `missing_graph_payload`
  - state card identifies contract gap
  - summary and article detail remain visible
- `producer_error`
  - state card identifies upstream failure
  - the page preserves whatever valid run/article context still exists
- `no_graph`
  - the page makes clear that the selected article/run is valid but produced no
    graph for this case
  - graph area remains intentionally empty with explanatory copy

### Graph and review flow
- Orientation starts with tuple and state panel rather than with graph.
- The primary review object is the selected article/window, optionally narrowed
  to a pair or contested region.
- Run summary and article detail establish why the graph matters before any
  graph canvas appears.
- In `graph_ready`, the page opens a bounded contested-window graph rather than
  a general revision graph.
- Graph detail remains synchronized with:
  - selected article
  - primary pair
  - top-region and top-cycle summaries where relevant
- If pair or region selection is supported, it updates graph focus without
  desynchronizing article detail.
- In `graph_not_enabled`, `missing_graph_payload`, `producer_error`, and
  `no_graph`, the same layout slot becomes a diagnostic review panel rather
  than disappearing.
- The user should always be able to answer:
  - is there a graph here
  - if not, why not
  - what bounded article/pair/window is still reviewable

Graph/review appearance specifics:
- The top state card owns the page mood; graph presence never overrides it.
- Graph-ready view feels materially different from graph-absent states in both
  layout and emphasis.
- Summary cards remain secondary to state interpretation.
- Pair, region, and cycle cards read as scoped diagnostic summaries rather than
  equal peers to the main graph.
- Non-graph states preserve strong article-detail readability in the same space
  where graph detail would otherwise live.
- Artifact-backed versus DB-backed provenance remains inspectable but visually
  secondary unless it changes the state diagnosis.

Graph/review state specifics:
- `graph_ready with graph detail`
  - graph is the main secondary inspection surface
  - article detail and summaries reinforce the same bounded window
- `graph_not_enabled with explanatory diagnostic panel`
  - no graph controls are implied
  - article detail remains primary after the state card
- `missing_graph_payload with contract-gap panel`
  - page emphasizes reviewable contract failure rather than generic emptiness
- `producer_error with upstream-failure panel`
  - page preserves valid context while making the producer failure explicit
- `valid no_graph with article-detail-first empty state`
  - absence of graph is treated as a valid result class
- `graph_ready but no cycles/regions/top-graph summaries`
  - graph remains available
  - empty summary subsections stay intentional and diagnostic

## Cross-workbench expectations
These recent pages should be treated as one family of review workbenches rather
than isolated custom screens.

Shared expectations:
- context and provenance remain visible by default
- no page silently promotes derived output into canonical truth
- empty/unavailable/error states are first-class interface states
- graph drill-ins stay bounded to the local review object
- raw JSON or artifact dumps remain available for debugging, but not as the
  default reading experience

Shared flow principles:
- the first view must answer what the user is looking at
- the second layer must answer what is reviewable here
- the third layer must answer what is missing, unsupported, or unresolved
- graph/detail drill-ins stay local and reversible
- provenance and raw-source access remain one action away
- empty and error states are part of the designed flow rather than exceptions

Shared appearance and interaction matrix:
- `hover`
  - transient preview only
  - never steals stable selection
- `selected`
  - one authoritative current object per page
- `pinned / opened detail`
  - stable until explicit replacement
- `inactive related`
  - visible but visually secondary
- `unsupported`
  - rendered as explanatory state, not mysterious disabled chrome
- `error`
  - diagnostic, specific, and non-generic
- `abstained`
  - explicit review posture, not weak error styling

Shared emphasis rules:
- Selected vs hover vs inactive vs unavailable vs error remain visually
  separable.
- Graph node hierarchy distinguishes:
  - selected node
  - directly connected nodes
  - contextual or secondary nodes
- Panel hierarchy distinguishes:
  - orientation/header/state
  - primary detail
  - graph/detail adjunct
  - diagnostics/raw payload
- Dense chips/badges have a visual ceiling; grouping and progressive disclosure
  should absorb overflow before readability collapses.
- Border, texture, opacity, or layout changes should carry part of the meaning
  so color is not doing all the work.

## Route acceptance checks

### /arguments/thread/[threadId]
1. Load route with canonical id and confirm header includes resolved canonical thread id, source id, and title before first interaction.
2. Verify message order remains canonical regardless of extraction mode and transcript content is readable with overlays off.
3. Enable Literal mode and verify highlights appear only on grounded anchors (exact spans, sentence blocks, or explicit fallback markers) without synthetic zero-index anchors.
4. Enable Family mode and verify active selection and inspector content remain unchanged while message emphasis broadens.
5. Click any overlay and verify single source of truth: transcript, claim inspector, and graph focus all reflect the same review object.
6. Open Graph tab and verify the graph is scoped to current family, then return to transcript and verify selection, scroll focus, and inspector remain stable.
7. Load a thread with no extractable overlays and verify the page enters explicit unsupported/no-overlay diagnostic state instead of blank content.

### /graphs/narrative-compare
1. Verify source identities, comparison fixture, and grouped shared/disputed/source-only/abstained presentation are visible on initial render.
2. Verify shared and disputed rows have different row semantics and are not merged when overlap exists.
3. Select a disputed row and verify receipts/provenance are shown in-place before any graph or claim drill-in.
4. Open explicit graph drill-in from selected row and verify nodes reflect only local comparison family and source-side identity.
5. Return from graph to compare view and verify selected row and right-side context are preserved.
6. Validate wrapper/authority rows keep speaker-authority-proposition structure readable and not flattened into generic rows.
7. Load a low-overlap/asymmetric case and verify abstention state is rendered explicitly with no false conflict claim.

### /graphs/wiki-revision-contested
1. Verify route always renders pack, run, article tuple, and a state badge before reviewing details.
2. Validate all five states are distinct and labeled: graph_ready, graph_not_enabled, missing_graph_payload, producer_error, no_graph.
3. In graph_ready, verify graph detail appears in the same bounded article window and that selected pair/article metadata is consistent with graph highlights.
4. For graph_not_enabled and missing_graph_payload, verify graph area is intentionally replaced by explanatory panel using the same layout slot as graph detail.
5. For producer_error, verify upstream failure is explicit while preserving valid run summary fields that still exist.
6. Change article within the same run and verify state panel, summary, article detail, and graph/detail panel update together.
7. Validate no-graph states still preserve readable run/article detail and explicit state explanation instead of generic empty panels.

## Component-level interaction contracts

### Interaction ownership
- `Transcript Overlay + Message Layer`
  - owns hover preview and click-to-select events for claim/fact/wrapper highlights.
  - owns message badges and gutter markers count source-of-truth.
  - does not own graph scope changes.
- `Claim Inspector`
  - owns active object canonical state and tab rendering (`Claim`, `Counterpoints`, `Graph`).
  - preserves selected object across tab changes and mode changes.
  - surfaces no-data reasons for each tab.
- `Graph Dock`
  - owns bounded rendering around active object scope only.
  - allows selection updates only when within graph scope.
  - emits context-preserving back action to Inspector + transcript focus.
- `Narrative Compare Rows`
  - owns row-level selection and in-place detail disclosure.
- `Narrative Compare Detail`
  - owns receipts, provenance, and attribution/authority expansion.
  - can trigger Graph/Claim drill-in without changing route context.
- `Contested Wiki State Shell`
  - owns article-state card precedence over summary/details.
  - owns state-specific panel selection for five wiki states.
  - owns synchronized rendering of summary, detail, and graph/detail sections.

### Event contract
- `selection_changed` updates one active object and is propagated to all three panes (source, inspector, graph).
- `selection_hover` updates only preview surfaces; active selection remains unchanged.
- `mode_change` updates highlight rendering and counts while preserving selection.
- `open_graph` is explicit and must be scoped to current selection context.
- `close_graph` restores previous selection and scroll/focus context.
- `change_tuple_or_thread` clears selection, updates tuple context state, and reruns loaders deterministically.
- `state_change` emits specific diagnostic reasons (loading, unsupported, empty, missing payload, producer error) instead of generic null/blank rendering.

## Implementation note for future devs
When these pages evolve, functional and appearance changes should be evaluated
against this note and against `docs/user_stories.md`, not only against local
component convenience.
