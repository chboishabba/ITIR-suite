# ITIR Colab Prover Runner

This package provides an exact-SHA, allowlisted remote compiler lane for Lean/Lake and Agda using a user-controlled Google Colab High-RAM runtime. It is an execution adapter only: compiler success does not merge code, promote theorem authority, or change Clay status.

## Fixed upstream pins

- `googlecolab/google-colab-cli`: `006ff96ac2d0e4dcfb702467a76493d687929be8`
- `googlecolab/colab-mcp` optional frontend: `b9ab3899e0f1fa493390b1fd6d54aa2e464ecdf1`
- baseline Lean available in Colab: `v4.35.0-rc3`
- repository toolchain policy: `repo_pinned`

`colab-mcp` is optional convenience for a local MCP-capable client. The canonical prover semantics are the ITIR job schema, worker, and GitHub relay.

## Security boundary

Version 1 accepts only:

- repositories `chboishabba/dashi_lean4` and `chboishabba/dashi_agda`;
- exact 40-hex commit SHAs;
- operations `lake_build`, `lake_env_lean`, and `agda_module`;
- typed operation arguments.

There is no arbitrary shell command, raw environment override, arbitrary URL, or source-repository write operation. Jobs run with argv subprocess semantics and `shell=False`.

The GitHub credential must be injected from **Colab Secrets** into `ITIR_COLAB_GITHUB_TOKEN`. Never embed a token in notebook cells, job JSON, result JSON, source files, or logs.

## Runtime state branch

All queue state lives on the dedicated branch **`colab-runner-state`**:

```text
.itir/colab/jobs/<job-id>.json
.itir/colab/claims/<job-id>.<generation>.json
.itir/colab/results/<job-id>.json
.itir/colab/logs/<job-id>/<chunk>.txt
```

Generated runtime state is never merged back to `main`.

One-time branch initialization can be done from an ordinary Git checkout without adding runtime files to `main`:

```bash
git fetch origin
git switch --orphan colab-runner-state
git rm -rf .
printf '%s\n' '# ITIR Colab prover runtime state' > README.md
git add README.md
git commit -m 'chore: initialize Colab runner state branch'
git push origin colab-runner-state
git switch main
```

This branch contains runtime receipts only. Source changes belong on normal reviewed branches.

## Colab bootstrap

The notebook is a **launcher only**. From a checkout of the exact approved ITIR runner source SHA, inject the GitHub token from Colab Secrets and run:

```bash
python scripts/colab_bootstrap_provers.py
python scripts/colab_worker.py --poll
```

The bootstrap installs/verifies Git, `elan`, baseline Lean `v4.35.0-rc3`, Lake through the Lean toolchain, Agda + stdlib support, this runner package, the pinned `google-colab-cli`, and the pinned optional `colab-mcp`. Repository `lean-toolchain` remains authoritative for Lean jobs.

## Submit jobs

Examples from an approved client environment:

```bash
python scripts/colab_submit.py \
  --repository chboishabba/dashi_lean4 \
  --commit-sha <exact-40-hex-sha> \
  --operation lake_build \
  --target QuantumMereology
```

```bash
python scripts/colab_submit.py \
  --repository chboishabba/dashi_agda \
  --commit-sha <exact-40-hex-sha> \
  --operation agda_module \
  --path DASHI/Physics/CanonicalClayFrontierExact.agda
```

Do **not** execute Lean, Lake, or Agda compiler builds on the local workstation for this workflow. Local verification is limited to pytest, static review, `dashi-agda-preflight`, and PR management. Real prover execution belongs to the provisioned Colab runtime.

## Receipt semantics

A `SUCCEEDED` result means only that the recorded allowlisted command exited zero against the recorded exact repository SHA in the recorded runtime/toolchain environment. `FAILED` records a normal compiler nonzero exit; `REJECTED` is policy/schema rejection; `ABORTED` is infrastructure/timeout termination.

No result changes theorem truth or repository authority by itself.
