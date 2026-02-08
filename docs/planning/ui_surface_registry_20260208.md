# ITIR UI Surface Registry (2026-02-08)

## Purpose
Provide one canonical place to find user-facing interfaces across core ITIR
components, including how to launch them and which authority lane they belong
to.

## Frontend decision check
- Referenced thread: `69882c94-3094-839a-b539-15529d7e9c6c`
  (`ITIR Competitors and Overlaps`, fetched via `scripts/chat_context_resolver.py`).
- Current practical frontend target for SB migration: `SvelteKit + Tailwind`.
- React remains documented as fallback; this is a working target, not an
  irreversible lock.
- Existing SB migration plan source:
  `StatiBaker/docs/svelte_migration_sprint.md`.

## Stable user-facing entrypoints
| Component | Surface | Access | Launch command | Authority lane |
| --- | --- | --- | --- | --- |
| `SensibLaw` | Streamlit app | `http://127.0.0.1:8501` (default Streamlit port) | `cd SensibLaw && streamlit run streamlit_app.py` | Interpretive (`SL`) |
| `WhisperX-WebUI` | Gradio web UI | `http://127.0.0.1:7860` | `cd WhisperX-WebUI && bash start-webui.sh` | Capture/observer (`TiRC` upstream) |
| `WhisperX-WebUI` | FastAPI backend docs | `http://127.0.0.1:8000/docs` | `cd WhisperX-WebUI && uvicorn backend.main:app --host 0.0.0.0 --port 8000` | Service/API (non-canonical) |
| `StatiBaker` | Static daily dashboard | `StatiBaker/runs/<date>/outputs/dashboard.html` | `cd StatiBaker && python scripts/build_dashboard.py --date <YYYY-MM-DD>` | Temporal (`SB`) projection |
| `StatiBaker` | Static weekly dashboard | `StatiBaker/runs/<date>/outputs/dashboard_weekly_<N>d.html` | `cd StatiBaker && python scripts/build_dashboard.py --date <YYYY-MM-DD> --weekly --weekly-days <N>` | Temporal (`SB`) projection |
| `StatiBaker` | Static lifetime dashboard | `StatiBaker/runs/<date>/outputs/dashboard_lifetime.html` | `cd StatiBaker && python scripts/build_dashboard.py --date <YYYY-MM-DD> --lifetime` | Temporal (`SB`) projection |
| `ITIR-suite` | Repo-wide docs browser | `http://127.0.0.1:8001/docs/_site/index.html` | `python scripts/build_docs_site.py && python -m http.server 8001` | Read-only (non-canonical) |

## Interfaces without standalone local web renderer (current)
These components are still first-class interfaces, but currently expose
CLI/API/data contracts rather than a dedicated browser UI surface:

- `SL-reasoner`
- `tircorder-JOBBIE`
- `itir-ribbon` (model/contract layer, consumed by host UIs)
- `reverse-engineered-chatgpt`
- `chat-export-structurer`
- `notebooklm-py`
- `Chatistics`
- `pyThunderbird`
- `SimulStreaming`
- `whisper_streaming`
- `fuzzymodo`
- `casey-git-clone`
- `living-environment-simulator` (planned observer stub)
- `aquaponics-calculator` (planned observer stub)
- `crops-planner` (planned observer stub)
- `medication-tracker` (planned observer stub)
- `pet-smart-collar` (planned observer stub)

Contract source for each remains:
- `docs/planning/project_interfaces.md`
- `<component>/docs/interfaces.md`

## Linking policy (suite-wide)
1. Do not hide native entrypoints behind a forced unified shell.
2. Keep each renderer linked as its own authority-bounded surface.
3. Treat inter-surface links as navigation only, not implicit authority
   promotion.
4. Require explicit promotion receipts for any write crossing authority lanes.

## Registry artifact
Machine-readable mirror:
- `docs/planning/ui_surface_manifest.json`

This manifest is the target input for a future launcher/portal page.
