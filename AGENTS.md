# Repository Guidelines

## Read First
Before writing code in this repo, read the nearest applicable style/doctrine
docs for the project you are changing.

Minimum rule:

- check the local `AGENTS.md`
- check the project `README.md`
- check the project implementation/style guide before adding code

Do not code from generic habits alone. This repo prefers shared generic
interfaces with data-in/world-model-out product boundaries, not lane-owned
semantics.

## Generic-First Rule
No lane owns a semantic method.

If an operation could apply to more than one lane, source family, or corpus,
the operation should live in a shared generic interface, adapter, carrier,
projection, or audit layer. Historical lane modules should supply only:

- demo or regression fixture loading
- compatibility wrappers over the generic API
- authority/source defaults for demonstrations
- outward labels for demonstrations only

Examples of shared capabilities that should stay generic:

- source anchors
- text/document units
- normalized forms and PNF units
- task / claim / event / theme / relation candidates
- follow graphs and authority lineage
- world models and projections
- linkage cases and receipts

Shared capabilities such as follow, legal-follow, narrative-follow, task
extraction, theme extraction, PNF-backed normalization, authority lineage, and
external joins must be treated as generic repo capabilities. Lanes may label or
prefill them, but must not redefine them as lane-owned primitives.

Do not expose lane names as public API namespaces or selector values when a
user should be able to provide data directly.

The product contract is:

- `build_world_model(data)`
- `project_report(world_model)`
- `project_claim_table(world_model)`
- `project_timeline(world_model)`
- `project_review_surface(world_model)`
- `project_linkage_case(world_model)`
- `attach_receipt(projection_or_report)`

Lane modules such as `nat.py`, `au.py`, `gwb.py`, and `brexit.py` are
demonstration or compatibility shims, not the primary user-facing API.

## Lane-Specific Detection Rule
If you encounter lane-specific adapters, node families, projection labels,
function names, or content that appear reusable across lanes, stop and raise it
to the user before extending it further.

Do not silently deepen lane-local semantics such as:

- `gwb_*`
- `au_*`
- `brexit_*`
- `nat_*`
- `wikidata_*`

when the underlying operation could be shared.

When raising the issue, include:

- the current lane-specific surface
- why it is overindexed or non-portable
- the most likely generic owner
- the thin lane/profile wrapper that should remain after extraction

Treat lane-local terms such as actor, office, legal reference, review item,
archive policy item, AU review fact, GWB legal-follow queue item, or similar as
profile metadata over shared carrier types unless the applicable style guide
proves they must remain local.

## Naming Rule
If the module already carries the lane or domain name, public callable names
must stay generic.

Lane identity belongs in:

- the module name
- the registry key
- the fixture/demo selector
- the lane-family wrapper

Profile identity belongs in selectors such as `profile`, `artifact`, or
`selector` only inside compatibility/demo layers, not in the product API.

Keep lane family and profile distinct in code and docs. For example, `nat` is a
lane family, while `climate_review_demonstrator`, `disjointness_report`, and
`q43229_superclass_pressure` are profiles.

Prefer:

- `build_world_model`
- `build_report`
- `build_case`
- `build_contract`
- `build_receipt`
- `attach_receipt`
- `load_fixture`
- `load_records`

Canonical demo surfaces should be zero-glue, but they remain demos. Prefer a
single product call such as `build_world_model(data)` for user-facing
interfaces.

Avoid public callables that encode both lane and operation.

Before adding a new public helper, search for an existing generic workflow,
adapter, carrier, or projection and extend that surface first. If a proposed
public function name contains both the lane name and the operation, stop and
refactor.

## World-Model Rule
Keep the carrier/projection/receipt split explicit:

- `build_world_model(...)` is receipt-free
- `project_*(world_model)` is receipt-free
- `attach_receipt(...)` happens only at the boundary

Keep the missing adapter layer explicit:

- `artifact -> world_model_adapters -> CandidateWorldModel`

Do not leave lane-local normalization semantics parked permanently in
lane-local `*_world_model.py`, `*_follow_graph.py`, or similar wrappers if the
transformation can be shared.

Fixture loaders are not product capabilities. Shared modules must not expose or
depend on `load_nat_fixture`, `load_gwb_fixture`, `load_au_fixture`,
`load_brexit_fixture`, or similar lane-specific loaders outside demos, tests,
and compatibility wrappers.

Prefer shared projections such as:

- `project_report(...)`
- `project_claim_table(...)`
- `project_timeline(...)`
- `project_review_surface(...)`
- `project_linkage_case(...)`

before inventing a lane-local report or review surface.

Use generic vocabulary where possible:

- `SourceAnchor`
- `TextUnit`
- `DocumentUnit`
- `NormalizedForm`
- `PNFUnit`
- `TaskCandidate`
- `ClaimCandidate`
- `EventCandidate`
- `ThemeCandidate`
- `RelationCandidate`
- `FollowTarget`
- `FollowEdge`
- `AuthorityCandidate`
- `AuthorityLineage`
- `ExternalBridgeCandidate`
- `ReviewSurface`
- `TrancheAnchor`

The core audits.
Adapters emit.
Profiles configure.
Lanes prefill.
Wrappers attach.
Authority remains external.

## Regex & Parsing Guideline
Avoid using raw regex or importing raw spaCy, `src.text.*`, or `src.nlp.*` modules directly for text segmentation, sentence splitting, tokenization, or entity parsing unless absolutely necessary. Downstream policy and integration code must utilize the public `sensiblaw.interfaces` wrapper layer (specifically `parser_adapter` for parsing/segmentation and `shared_reducer` for token/span/reducer work).

Available interface functions:
- `parse_canonical_text`
- `tokenize_presemantic_text`
- `split_presemantic_text_segments`
- `tokenize_canonical_with_spans`
- `collect_canonical_relational_bundle`

Standard Python string methods (such as `.split()`, `.replace()`, `.strip()`) are preferred for simple layout/separator checks.
