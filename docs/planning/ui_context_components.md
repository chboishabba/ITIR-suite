# UI Context Components (Implementation Targets)

This document specifies concrete, testable UI components that enforce the
context invariant across ITIR/SL/SB.

---

## 1. Artifact Viewer (Core Panel)

Layout:

```
┌───────────────────────────────────────────┐
│ Artifact Content                           │
│ (email / quote / transcript / image)       │
├───────────────────────────────────────────┤
│ CONTEXT STRIP (always visible)             │
│ - Date / Time                              │
│ - Venue                                   │
│ - Intended Audience                       │
│ - Epistemic State (Then)                  │
│ - Epistemic State (Now)                   │
└───────────────────────────────────────────┘
```

Rules:
- Context strip cannot be collapsed.
- Artifact cannot be copied without context.
- Screenshots watermark the context hash.

---

## 2. Context Drift Warning Overlay

Triggered when:
- Artifact is viewed outside original venue
- Artifact is time-shifted past epistemic horizon
- Artifact is cross-audience reused

Overlay copy:
```
This artifact is being viewed outside its original context.
Meaning may differ from original intent or understanding.
```

Users must explicitly acknowledge.

---

## 3. Epistemic Timeline Slider

Interactive horizontal control:
```
[ Known Then ]----------|----------[ Known Now ]
```

Rules:
- Dragging updates visible annotations.
- Later facts never overwrite earlier state.
- Default view is "Known Then".

---

## 4. Claim Typing Badge (SL Integration)

Every assertion rendered with a badge:
- FACT
- TESTIMONY
- INFERENCE
- OPINION
- PR / NARRATIVE
- UNVERIFIED

Rules:
- Hover reveals provenance graph.
- Unbadged text is forbidden.

---

## 5. Reputational Exposure Graph (SB)

Explicit label: "No Verdict View"

Nodes show:
- Contact
- Assistance
- PR activity
- Temporal proximity

Rules:
- Edges never imply intent or guilt.
- Legend states:
  - Presence does not imply culpability
  - Absence does not imply exoneration

---

## 6. Context Removal Gate (Export / Share)

Modal copy:
```
You are attempting to remove context.
This may distort meaning and provenance.
```

Options:
- Export with full context
- Export redacted context (logged)
- Cancel

All context removal actions are logged immutably.
