# ITIR-suite

Meta-repo that pins the moving pieces of the ITIR / SensibLaw stack as git submodules. Use this repo to pull the whole toolchain in one shot; build and run inside the individual submodules.

## Components (submodules)
- `SensibLaw/` – ingestion + operations console for span-anchored legal corpora (see that repo for build/run docs).
- `SL-reasoner/` – reasoning/IR spine that the SensibLaw UI and tooling consume.
- `tircorder-JOBBIE/` – investigative/interpretive tooling (ITIR/TIRC experiments).
- `WhisperX-WebUI/` – speech-to-text pipeline + UI (WhisperX wrapper).

The definitive instructions for each live in the submodule’s own README; this file only tracks how to manage them together.

## Quickstart
```bash
git clone https://github.com/chboishabba/ITIR-suite.git
cd ITIR-suite
./setup.sh   # runs `git submodule update --init --recursive`
```

If you already have the repo, sync to the recorded commits with:

```bash
git submodule update --init --recursive
```

## Working with submodules
- To pull latest from all submodules (fast-forward to upstream):
  ```bash
  git submodule update --remote --recursive
  ```
- To commit/push submodule changes in bulk (use with care), `sync-all-submodules.sh` will run `git add/commit/push` inside each submodule and then commit the updated pointers in this meta-repo.
- When changing a submodule, commit inside the submodule first, then `git add <submodule>` in this repo to record the new pointer.

## Notes
- This repo carries no standalone build; everything interesting happens inside the submodules.
- Keep `setup.sh` up to date if new modules are added.
