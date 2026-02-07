# Phase 17: Casey Git Clone - Context

**Gathered:** 2026-02-07
**Status:** Ready for planning

<vision>
## How This Should Work

Build a practical, branch-friendly versioning prototype inspired by Casey's
superposition framing: sync never blocks, conflicting edits coexist, and
resolution is deferred until a human or policy chooses a buildable view.
</vision>

<essential>
## What Must Be Nailed

- Conflict as coexistence (`candidates`) rather than immediate failure.
- View selection as first-class (workspace/build views).
- Deterministic, auditable state transitions.
</essential>

<boundaries>
## What's Out of Scope

- Replacing Git for this repo.
- Full networked VCS protocol implementation in first phase.
- AI-authored semantic commit curation.
</boundaries>

<specifics>
## Specific Ideas

- Core objects: `Blob`, `FileVersion`, `PathState`, `TreeState`, `WorkspaceView`.
- Deferred collapse operation: many candidates -> one resolved candidate.
- BuildView snapshot to pin exactly what CI/build consumed.
</specifics>

<notes>
## Additional Context

Source thread from local archive: `Git Coordination Debate`
(`canonical_thread_id: b8800296148a7c14e0b84a152e0c67a2ba32acb0`).
</notes>

---

*Phase: 17-casey-git-clone*
*Context gathered: 2026-02-07*
