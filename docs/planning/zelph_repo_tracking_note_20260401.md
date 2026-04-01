Zelph Repo Tracking
===================

Default upstream: `https://github.com/acrion/zelph` (track this when adding the submodule).

Feature fork for partial-load + HF shard work: `https://github.com/chboishabba/zelph`, branch `develop`, commit `744b132` (merged PR #26). If you need those features before they land upstream, either:

- temporarily point the submodule at `chboishabba/zelph@744b132`, or
- cherry-pick the range `origin/develop..744b132` from that fork into your working copy.

The `aur/zelph` working tree in this repo currently mirrors the chboishabba fork and already contains the partial-load changes; no submodule is configured yet.
