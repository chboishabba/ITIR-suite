# ITIR-suite

ITIR is not an operating system.

ITIR-suite is the orchestration/control plane for a bounded product stack. It
pins submodules, coordinates local projects, and defines cross-project handoff
contracts.

Definition source context (raw archive extracts, role-attributed, no synthesis):
- `__CONTEXT/ITIR_DEFINITION_CONTEXT.md`
Definition ratification draft (accepted/rejected/pending clauses):
- `__CONTEXT/ITIR_DEFINITION_RATIFICATION.md`

Canonical product identity (from archived doctrine threads in
`chat-export-structurer/my_archive.sqlite`):
- `SensibLaw`: deterministic ground-truth substrate and provenance spine.
- `ITIR`: investigative/interpretive coordination layer over evidence, not a
  command authority.
- historical phrase `investigative operating system` is treated as shorthand
  metaphor, not runtime/platform semantics.
- `StatiBaker`: daily state distillation engine and context prosthesis, not an
  autonomous assistant.
- `tircorder-JOBBIE` + `WhisperX-WebUI`: capture/transcription ingest channels.
- `SL-reasoner` and adjacent tools: optional analysis/derivation layers bound
  by provenance and authority constraints.

Use this repo to pull and orchestrate the whole toolchain in one shot; build
and run inside the individual submodules.

Context is not commentary. Context is infrastructure.

## Components (submodules + local projects)
- `SensibLaw/` – ingestion + operations console for span-anchored legal corpora (see that repo for build/run docs).
- `SL-reasoner/` – reasoning/IR spine that the SensibLaw UI and tooling consume.
- `tircorder-JOBBIE/` – investigative/interpretive tooling (ITIR/TIRC experiments).
- `StatiBaker/` – daily state distillation engine (temporal compiler over ITIR/TIRC/SL artifacts; docs-only, see that repo for design/specs).
- `WhisperX-WebUI/` – speech-to-text pipeline + UI (WhisperX wrapper).
- `reverse-engineered-chatgpt` – wrapper for programmatic access to chatGPT interface (note, issues with sending messages - testing stalled due to bot detection - chat account otherwise unaffected).
- `chat-export-structurer/` – utilities for ingesting chat exports into SQLite with FTS.
- `notebooklm-py/` – NotebookLM automation client (third-party; see that repo for setup).
- `Chatistics/` – chat export analytics and visualization toolkit.
- `pyThunderbird/` – Thunderbird automation client (third-party; see that repo for setup).
- `SimulStreaming/` – research-grade streaming ASR policy/decoding (ufal).
- `whisper_streaming/` – Whisper streaming policy reference implementation (ufal).
- `fuzzymodo/` – selector DSL and norm-constraint scaffold for quirk-vs-vulnerability reasoning.
- `casey-git-clone/` – standalone superposition-style VCS prototype scaffold based on Casey thread.

The definitive instructions for each live in the submodule’s own README; this file only tracks how to manage them together.

## ITIR as Orchestrator
- ITIR-suite is the control plane for cross-project planning, context, and
  execution routing.
- Component repos remain the implementation/data planes.
- Cross-component behavior is declared via interface contracts, not implicit
  coupling.

Orchestrator contract:
- `docs/planning/itir_orchestrator.md`

Interface contract index for cross-project handoffs:
- `docs/planning/project_interfaces.md`

## Quickstart
```bash
git clone https://github.com/chboishabba/ITIR-suite.git
cd ITIR-suite
./setup.sh   # runs `git submodule update --init --recursive`
```

If you already have the repo, sync to the recorded commits with:

```bash
git submodule update --init --recursive
```

## Working with submodules
- To pull latest from all submodules (fast-forward to upstream):
  ```bash
  git submodule update --remote --recursive
  ```
- To commit/push submodule changes in bulk (use with care), `sync-all-submodules.sh` will run `git add/commit/push` inside each submodule and then commit the updated pointers in this meta-repo.
- When changing a submodule, commit inside the submodule first, then `git add <submodule>` in this repo to record the new pointer.

## Notes
- This repo carries no standalone build; everything interesting happens inside the submodules.
- Keep `setup.sh` up to date if new modules are added.

## Dependencies (aggregated)
The repo root `requirements.txt` is a consolidated superset of submodule Python dependencies so you can
optionally build a single compatibility venv at the root. Submodules still ship their own venvs and
requirements; prefer those unless you explicitly need a unified environment.

## Chat Context Sync
To avoid copy-pasting long CLI commands, maintain the conversation list in
`__CONTEXT/convo_ids.md` and run:

```bash
./scripts/sync_chat_context.sh
```

The script writes a timestamped report into `__CONTEXT/last_sync/` with
line-numbered excerpts so you can cite `ID:line#` in context files.
It uses the root `ITIR-suite/.venv` Python environment and sets `PYTHONPATH`
to the `reverse-engineered-chatgpt` package so it does not require a
submodule-specific venv.


## Dev Note
Due to technical constraints, the below command is used for running a compatibility docker. We are hoping to eventually provide ITIR as a deployable container separate to this as well.
The compatibility docker is provided due to development being conducted on AMD RX580 (gfx803), requiring some compiled modules due to importing torch/ctranslate2 for speech-to-text in WhisperX-WebUI.
This is already quite fast on CPU, especially with whisperx, and when VAD chunking is performed by tircorder, however does result in degradation of desktop experience for the server/host.
Most newer consumer cards will not require this compatibility layer.


```
docker run -it \
              --name ITIR \
              --device=/dev/kfd --device=/dev/dri \
              --security-opt seccomp=unconfined \
              --group-add video \
              -v /usr/include/vulkan:/usr/include/vulkan:ro \
              -v /usr/include/spirv:/usr/include/spirv:ro \
              -v /usr/include/vk_video:/usr/include/vk_video:ro \
              -v /usr/include/glslang:/usr/include/glslang:ro \
              -v /usr/bin/glslangValidator:/usr/bin/glslangValidator:ro \
              -v "/home/c/Documents/code/ITIR-suite:/opt/ITIR-suite" \
              --entrypoint /bin/bash \
              dashi_ready_image
```
then ``` cd /opt/ITIR-suite (linked to host)```
and ```source /Whisper-WebUI/venv/bin/activate```
