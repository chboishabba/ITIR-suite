# Ribbon UI Contract (Selectors + Conservation)

This file documents the data attributes required to make conservation tests
stable and implementation-agnostic. These are documentation-only right now; do
not infer the UI exists until wired.

## Required selectors

- `data-testid="ribbon-viewport"`
- `data-testid="segment"`
  - `data-seg-id="..."`
  - `data-mass="..."`
  - `data-width-norm="..."` (optional but recommended)
- `data-testid="conservation-badge"`
  - `data-total-mass="..."`
  - `data-lens-id="..."`
- `data-testid="heatline"` (optional)
- `data-testid="compare-overlay"` (optional)
- `data-testid="lens-switcher"`
  - `data-testid="lens-item:<id>"`

## Conservation checks

- Sum of segment pixel widths ~= viewport width.
- Sum of `data-width-norm` ~= 1 (if exposed).
- Split/merge does not change total width.
- Lens switch preserves segment ordering (topology stability).

## Notes

- These are accounting tests, not visual-quality tests.
- If widths are rendered via transforms, tests should measure client bounding
  boxes after transforms are applied.
