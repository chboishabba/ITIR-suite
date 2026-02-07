# ITIR Definition Context (Source Extracts)

## Purpose
Collect high-signal ITIR definition snippets from the canonical chat archive
without adding new interpretation.

## Source and Method
- Source DB: `chat-export-structurer/my_archive.sqlite`
- Extraction mode: read-only SQLite queries (`sqlite3 -readonly`)
- Filter style: explicit definition phrases (`ITIR is ...`, `ITIR-suite ...`,
  `one system, multiple operating modes`, `daily state distillation engine`,
  `context prosthesis`)

## Raw Snippets (No Synthesis)

### 1) ITIR as investigative operating system (assistant)
- `ts`: `2026-02-03T03:41:12+00:00`
- `role`: `assistant`
- `canonical_thread_id`: `d368629d32111762fee2a415839a53ee398cb2df`
- `title`: `Branch · Branch · Cross-comparison of SL ITIR TIRC`
- excerpt:
  - `SL is the ground-truth substrate. ITIR is the investigative operating system.`
  - `If SL is a ledger, ITIR is a collaborative newsroom.`

### 2) ITIR-suite as meta-repo boundary (assistant)
- `ts`: `2026-02-03T04:11:54+00:00`
- `role`: `assistant`
- `canonical_thread_id`: `d368629d32111762fee2a415839a53ee398cb2df`
- `title`: `Branch · Branch · Cross-comparison of SL ITIR TIRC`
- excerpt:
  - `ITIR-suite is now a meta-repo with submodules.`

### 3) Multi-mode framing (user)
- `ts`: `2026-02-06T01:56:43+00:00`
- `role`: `user`
- `canonical_thread_id`: `dff2e608e358fe5ed5cf1d0376a36ff8a87a6f2d`
- `title`: *(empty in archive)*
- excerpt:
  - `The correct model: one system, multiple operating modes.`
  - `ITIR/SB isn’t one thing.`

### 4) Multi-mode summary written to doctrine docs (tool)
- `ts`: `2026-02-06T01:58:08+00:00`
- `role`: `tool`
- `canonical_thread_id`: `dff2e608e358fe5ed5cf1d0376a36ff8a87a6f2d`
- `title`: *(empty in archive)*
- excerpt:
  - `StatiBaker/ITIR is one system with multiple operating modes.`
  - `...authority never crosses boundaries silently.`

### 5) StatiBaker product identity (user)
- `ts`: `2026-02-03T18:07:47+00:00`
- `role`: `user`
- `canonical_thread_id`: `8b6bc52574d461d481becc4e19e08b6736449184`
- `title`: *(empty in archive)*
- excerpt:
  - `StatiBaker is defined not as a personal assistant, but as a daily state distillation engine and a context prosthesis...`

### 6) ITIR boundary guardrail (assistant)
- `ts`: `2026-02-05T05:58:41+00:00`
- `role`: `assistant`
- `canonical_thread_id`: `eeefa20ff7e326ff38d083915f134bc67392fb14`
- `title`: `Linux Copilot Recall Clone`
- excerpt:
  - `ITIR can never accidentally re-segment time.`

## Notes
- This file intentionally preserves source-role distinctions (`assistant`,
  `user`, `tool`) instead of collapsing them.
- Contradictions are expected at this stage; resolve in a separate definition
  ratification pass.
