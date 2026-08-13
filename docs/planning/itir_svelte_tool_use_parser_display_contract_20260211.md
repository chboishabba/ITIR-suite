# ITIR Svelte Tool-Use Parser Display Contract

Date: 2026-02-11

## Purpose

Define display-layer parsing rules for `itir-svelte` Tool Use Summary (and related
timeline/thread tool previews) so command grouping is consistent, explainable,
and parity-aligned with legacy SB HTML behavior.

This is a **view contract**, not a canonical event model.

## Scope

Applies to:
- `tool_use_summary` command-family rendering in `itir-svelte`
- shared command preview formatting where tool payloads include shell lines

Does not apply to:
- SB reducer math/counters
- canonical event identity or ingest storage schema

## Invariants (must hold)

1. Preserve SB-native family counts/labels from JSON payload.
2. Display grouping may reorganize variants, but must not reclassify families.
3. Directory grouping is a visualization aid only.
4. Parser failures must degrade gracefully to raw command text.

Rationale overlap:
- `StatiBaker/CONTEXT.md:280` requires timeline/accounting truth to stay with SB
  deterministic segmentation; UI parsing must remain non-authoritative.

## Input Contract

Primary fields:
- `tool_use_summary.families[]`
  - `name`
  - `calls`
  - `variants[]` (raw command examples + call counts)

Optional:
- top-directory slices and additional summary metadata when present

## Normalization Pipeline (display-only)

1. Tokenize shell line conservatively.
2. Split compound segments on control operators:
   - `&&`, `||`, `;`, `|`
3. Capture leading directory context:
   - `cd <dir>`
   - `pushd <dir>`
   - (optional) resolve `cd -` with an "unknown/previous dir" placeholder.
4. Attribute subsequent segments to active directory context.
5. Extract segment operator + normalized signature.
6. Group output by:
   - family -> directory context -> normalized signature.
7. Keep one representative raw line in hover/title for auditability.

## Special Cases

Heredoc (`python - <<'PY'`):
- Trunk under family variant `'PY'`.
- Derive sub-variants from body fingerprint/first non-empty logical line.

Patch payload (`apply_patch`):
- Trunk under `'PATCH'`.
- Sub-variant label derives from patch ops/paths:
  - Add/Update/Delete/Move + touched file shortlist.

Empty stdin writes (`write_stdin`):
- Render compactly as `chars=(empty)` when empty string.
- Raw JSON remains behind explicit expansion.

## Directory Grouping Rules

1. If raw line begins with `cd <dir> && <cmd>`, group under `<dir>`.
2. Show `<cmd>` as the variant label, not the `cd` wrapper.
3. If no directory context exists, use unscoped group.
4. Repeated roots should render once with grouped subcommands beneath.

Example:
- Raw:
  - `cd /repo/SensibLaw && ls src/sensiblaw`
  - `cd /repo/SensibLaw && ../.venv/bin/pytest tests/test_x.py`
- Display:
  - `/repo/SensibLaw`
    - `ls src/sensiblaw`
    - `../.venv/bin/pytest tests/test_x.py`

## Signature Rules (current target)

`find`:
- Normalize by predicate signature order:
  `-maxdepth`, `-mindepth`, `-type`, `-name/-iname`, `-path/-ipath`,
  `-size`, `-printf`, `-exec`, `-print0/-print`, `-delete`.
- Keep root-directory grouping first.

Generic families (`cat`, `ls`, `rg`, `python`, etc.):
- Reuse the same compound-splitting and directory-context logic.
- Do not create one-off per-family parsers unless strictly required.

## Non-goals

- Reconstruct full shell semantics in all quoting/escaping edge cases.
- Guarantee byte-perfect command replay from normalized display form.
- Mutate counters or quality metrics computed upstream by SB.

## Open Follow-ups

1. Add fixtures for mixed operators with quoted control symbols.
2. Add fixtures for nested subshells and here-strings.
3. Add parity checks against representative legacy HTML rows.
4. Decide whether to canonicalize home-relative paths (`~`) in display.
