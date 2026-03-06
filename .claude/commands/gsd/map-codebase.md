---
name: gsd:map-codebase
description: Analyze codebase with parallel inheriting agents to produce .planning/codebase/ documents
argument-hint: "[optional: specific area to map, e.g., 'api' or 'auth']"
allowed-tools:
  - Read
  - Bash
  - Glob
  - Grep
  - Write
  - Task
---

<objective>
Analyze existing codebase using parallel inheriting agents to produce structured codebase documents.

This project-local override exists because the built-in Explore agent model selection is incompatible with the current LiteLLM-backed setup. Use the custom `gsd-code-explorer` agent instead.

Output: `.planning/codebase/` with 7 structured documents about the current codebase state.
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/map-codebase.md
@~/.claude/get-shit-done/templates/codebase/stack.md
@~/.claude/get-shit-done/templates/codebase/architecture.md
@~/.claude/get-shit-done/templates/codebase/structure.md
@~/.claude/get-shit-done/templates/codebase/conventions.md
@~/.claude/get-shit-done/templates/codebase/testing.md
@~/.claude/get-shit-done/templates/codebase/integrations.md
@~/.claude/get-shit-done/templates/codebase/concerns.md
</execution_context>

<context>
Focus area: $ARGUMENTS (optional)

Load `.planning/STATE.md` if it exists.

Important:
- Use `Task` with `subagent_type="gsd-code-explorer"` for background parallel analysis.
- Do not use the built-in `Explore` agent in this repository.
</context>
