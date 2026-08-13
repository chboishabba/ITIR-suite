# Phase 17: Casey Git Clone - Context

**Gathered:** 2026-02-07
**Status:** Updated 2026-03-19

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

Current local reality:
- Casey now has a Casey-owned sqlite runtime and minimal CLI-backed testbed.
- The local alice/bob divergent same-path workflow is test-covered.
- The next missing work is not more internal Casey theory; it is the two
  external boundaries:
  - Casey -> fuzzymodo
  - Casey -> StatiBaker

Current contract docs:
- `docs/planning/casey_fuzzymodo_interface_contract_20260319.md`
- `docs/planning/casey_git_clone_statiBaker_interface_20260309.md`
- `docs/planning/casey_statiBaker_receipt_schema_20260319.md`
- `docs/planning/casey-git-clone/sqlite_runtime_decision_20260319.md`
</notes>

---

*Phase: 17-casey-git-clone*
*Context gathered: 2026-02-07; refreshed: 2026-03-19*
