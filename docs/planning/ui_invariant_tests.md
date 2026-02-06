# UI Invariant Tests (Checklist)

These checks operationalize the context invariant as testable UI behaviors.

---

## UI-INV-01: No Context-Free Rendering

- Attempt to open an artifact directly from a deep link.
- Expected: context strip renders and cannot be collapsed.
- Expected: warning appears if context fields are missing.

## UI-INV-02: No Silent Context Loss

- Attempt to copy/export an artifact.
- Expected: context removal modal appears.
- Expected: export includes context envelope by default.
- Expected: context removal is logged when explicitly chosen.

## UI-INV-03: Expand Context Is Cheaper Than Summarize

- Attempt to open a summary view.
- Expected: raw artifact is one click away.
- Expected: no irreversible compression.

## UI-INV-04: Interpretation Is Always Optional

- Attempt to open a graph or timeline with interpretation disabled.
- Expected: system renders only artifacts and relationships without narrative.

## UI-INV-05: Context Drift Warning

- Open an artifact outside original venue or audience.
- Expected: drift warning overlay and explicit acknowledgement.

## UI-INV-06: Epistemic Timeline Integrity

- Drag the epistemic slider between "Known Then" and "Known Now."
- Expected: later facts appear only in "Known Now" view.
- Expected: "Known Then" view never includes later revelations.
