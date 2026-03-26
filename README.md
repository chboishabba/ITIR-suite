# ITIR-suite

ITIR-suite is the top-level workspace for a set of tools that help capture,
organize, review, and hand off difficult material without losing provenance.

In plain language:

- `tircorder-JOBBIE` and `WhisperX-WebUI` help capture and transcribe audio.
- `SensibLaw` turns messy source material into structured, reviewable artifacts.
- `StatiBaker` compiles day-level state from logs, tools, and activity traces.
- the suite-level docs and contracts in this repo keep those projects aligned.

This repo is the place where those pieces are pinned together, documented
together, and routed together. Most detailed setup and day-to-day running
happens inside the individual project directories.

## What This Repo Is For

Use the root repo when you want to:

- clone the whole suite in one shot
- keep submodules pinned to known commits
- find the main cross-project contracts and handoff docs
- understand what the suite can already do today
- jump to the right subproject README instead of guessing

This root repo is not a single deployable app. It is the shared workspace and
control surface for multiple related tools.

## What You Can Do Today

### 1. Capture and transcribe real-world material

The suite can capture spoken material, run transcription, and keep the outputs
available for downstream review instead of treating them as disposable text.

Typical flow:

- capture or collect audio in `tircorder-JOBBIE`
- transcribe through `WhisperX-WebUI`
- pass transcripts and related outputs into structured review surfaces

Why that matters:

- you keep a trail back to the source material
- downstream tools can work from stable artifacts instead of ad hoc notes

### 2. Turn messy source material into reviewable structured data

`SensibLaw` is the main deterministic review layer in the suite. It is built to
take difficult source material and turn it into bounded, inspectable outputs
rather than magical summaries.

Typical outputs include:

- structured slices and projections
- review queues
- handoff bundles
- provenance-backed JSON artifacts

Why that matters:

- a later reviewer can inspect what was found
- you can keep uncertainty visible instead of flattening it away

### 3. Compile day-level state instead of relying on memory

`StatiBaker` turns logs, activity, and machine-readable traces into a daily
state view.

Typical outputs include:

- what changed
- what stalled
- what remains unresolved
- what actions or machine states are still pending

Why that matters:

- it is designed to preserve traceable state, not pretend to be a chatbot
- it helps recover continuity after interruption or context collapse

### 4. Run bounded ontology diagnostics and produce human-readable review artifacts

The suite also includes a bounded Wikidata diagnostics lane inside
`SensibLaw`. This is one of the clearest current examples of the repo doing
something concrete and externally legible.

The important point is not just "we have diagnostics." It is that the outputs
are small, pinned, reviewable, and backed by repo artifacts.

## Proven Abilities

These are not abstract goals. They are current repo-backed examples.

### Bounded Wikidata examples

- A clean baseline around `nucleon` / `proton` / `neutron`, where the
  disjointness relation is present but there are no violations.
- A real contradiction around `working fluid`, where `working fluid` is typed
  as both `gas` and `liquid`.
- A real contradiction in the `fixed construction` / `geographic entity` area,
  where the current pinned slice shows several subclass violations.
- A synthetic transport example used to make the reporting deterministic, with
  amphibious/land/water subclass and instance violations.

What those examples mean:

- the system can preserve a real "nothing wrong here" baseline, not just find
  false alarms everywhere
- it can catch direct item-level conflicts
- it can also catch longer subclass-chain structural problems
- it can turn those findings into checked summaries and review rows instead of
  leaving them as raw graph noise

Short version:

- one zero-violation baseline
- one direct instance contradiction
- one subclass contradiction chain
- one synthetic deterministic regression/demo case

### Human-readable review and handoff surfaces

The suite already has checked handoff artifacts that summarize bounded slices in
plain-language summaries plus machine-readable artifacts, instead of expecting a
reviewer to inspect only raw intermediate data.

That matters because:

- the outputs are discussable with collaborators
- they are stable enough to revisit
- they make the current boundaries explicit: what is demonstrated, what is
  still under review, and what is not being claimed yet

### Cross-project workflow, not just isolated modules

The projects in this workspace are not just adjacent folders. The repo already
contains cross-project contracts covering handoff, review boundaries, and
orchestration responsibilities.

That means the suite is already useful as:

- a bounded evidence-to-review workflow
- a diagnostics-and-handoff workspace
- a place to keep multiple tools aligned without silently merging their roles

## Root Setup

Clone the suite and initialize the pinned submodules:

```bash
git clone https://github.com/chboishabba/ITIR-suite.git
cd ITIR-suite
./setup.sh
```

If you already have the repo:

```bash
git submodule update --init --recursive
```

Optional root Python environment:

```bash
./env_init.sh
source .venv/bin/activate
```

Use the root environment when you need a shared compatibility environment across
the workspace. For most real work, prefer the setup instructions in each
subproject's own README.

## How To Use The Suite

Start at the root only long enough to get the workspace in place. Then move to
the subproject that matches the job you actually want to do.

### If you want to work with structured review, provenance, or Wikidata diagnostics

Go to [SensibLaw/README.md](SensibLaw/README.md).

### If you want audio capture and transcription intake

Go to [tircorder-JOBBIE/README.md](tircorder-JOBBIE/README.md)
and [WhisperX-WebUI/README.md](WhisperX-WebUI/README.md).

### If you want daily state compilation and context recovery

Go to [StatiBaker/README.md](StatiBaker/README.md).

### If you want the chat/context tooling

Go to [reverse-engineered-chatgpt/README.md](reverse-engineered-chatgpt/README.md)
and [chat-export-structurer/README.md](chat-export-structurer/README.md).

## Where To Find Things

### Suite-level orientation

- project interface index:
  [docs/planning/project_interfaces.md](docs/planning/project_interfaces.md)
- orchestration role:
  [docs/planning/itir_orchestrator.md](docs/planning/itir_orchestrator.md)
- architecture boundary doctrine:
  [docs/architecture/admissibility_lattice.md](docs/architecture/admissibility_lattice.md)

### Proven example and handoff docs

- shortest Wikidata/Zelph external handoff overview:
  [docs/planning/wikidata_zelph_single_handoff_20260325.md](docs/planning/wikidata_zelph_single_handoff_20260325.md)
- current Wikidata working status:
  [SensibLaw/docs/wikidata_working_group_status.md](SensibLaw/docs/wikidata_working_group_status.md)
- disjointness report contract:
  [docs/planning/wikidata_disjointness_report_contract_v1_20260325.md](docs/planning/wikidata_disjointness_report_contract_v1_20260325.md)
- disjointness case index:
  [docs/planning/wikidata_disjointness_case_index_v1.json](docs/planning/wikidata_disjointness_case_index_v1.json)
- checked structural handoff summary:
  [SensibLaw/tests/fixtures/zelph/wikidata_structural_handoff_v1/wikidata_structural_handoff_v1.summary.md](SensibLaw/tests/fixtures/zelph/wikidata_structural_handoff_v1/wikidata_structural_handoff_v1.summary.md)

### Additional operator and onboarding docs

- SensibLaw onboarding playbooks:
  [SensibLaw/docs/onboarding_playbooks.md](SensibLaw/docs/onboarding_playbooks.md)
- suite user stories:
  [docs/user_stories.md](docs/user_stories.md)

## Handoff And Collaboration

If you need a bounded, sendable explanation of what is already demonstrated and
what is not yet being claimed, start with:

- [docs/planning/wikidata_zelph_single_handoff_20260325.md](docs/planning/wikidata_zelph_single_handoff_20260325.md)

If you need the concrete checked artifact surfaces behind that summary, use:

- [SensibLaw/tests/fixtures/zelph/wikidata_structural_handoff_v1/wikidata_structural_handoff_v1.summary.md](SensibLaw/tests/fixtures/zelph/wikidata_structural_handoff_v1/wikidata_structural_handoff_v1.summary.md)
- [docs/planning/wikidata_disjointness_case_index_v1.json](docs/planning/wikidata_disjointness_case_index_v1.json)

This repo currently treats handoff as document- and artifact-backed. In other
words, the collaboration surface is the checked documentation and fixture
artifacts, not a vague promise that the system can do more than it has already
shown.

## Working With Submodules

- sync pinned submodules:
  ```bash
  git submodule update --init --recursive
  ```
- fast-forward submodules to tracked upstream state:
  ```bash
  git submodule update --remote --recursive
  ```
- sync clean submodules safely:
  ```bash
  ./sync-all-submodules.sh
  ```

If you change a submodule, commit inside that submodule first, then record the
updated pointer in this root repo.

## Helpful Root Scripts

- `./setup.sh`: initialize and update submodules
- `./env_init.sh`: build an optional root compatibility venv
- `./scripts/sync_chat_context.sh`: sync conversation context into
  `__CONTEXT/last_sync/`
- `python scripts/build_docs_site.py`: build a lightweight local index of the
  repo's markdown docs under `docs/_site/`

## Advanced Environment Note

This workspace includes a compatibility-container path used during development
for AMD RX580 / older ROCm-related constraints. That is an environment-specific
development workaround, not the main entrypoint for most readers.

If you need that path, see the existing container/dev notes in the repo and the
relevant subproject setup docs before using it.
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/chboishabba/ITIR-suite)
