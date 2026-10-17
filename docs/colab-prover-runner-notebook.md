# Colab Prover Runner Notebook Launcher

The Google Colab notebook is a thin **launcher**. It must not become the source of truth for worker logic, prover policy, repository mutation, or credentials.

The intended notebook is the user's High-RAM Colab runtime. Use Colab Secrets for the dedicated fine-grained GitHub credential and expose it to the process as `ITIR_COLAB_GITHUB_TOKEN`; never paste or serialize the secret into a notebook cell or repository file.

## Minimal launcher flow

1. Clone or fetch `chboishabba/ITIR-suite` and checkout the exact approved runner source commit.
2. Load `ITIR_COLAB_GITHUB_TOKEN` from **Colab Secrets** into the process environment.
3. Run:

```bash
python scripts/colab_bootstrap_provers.py
```

4. Start the worker:

```bash
python scripts/colab_worker.py --poll
```

Runtime queue state is isolated on `colab-runner-state`; it must never be merged to `main`.

## Pinned integrations

- `googlecolab/google-colab-cli` commit `006ff96ac2d0e4dcfb702467a76493d687929be8`
- optional `googlecolab/colab-mcp` commit `b9ab3899e0f1fa493390b1fd6d54aa2e464ecdf1`
- baseline Lean `v4.35.0-rc3`, with repository `lean-toolchain` taking precedence for `repo_pinned` jobs

## Workstation boundary

Do not run Lean/Lake or Agda compiler builds on the local workstation as part of this workflow. Local work may run pytest, static checks, `dashi-agda-preflight`, source editing, and PR management. All real prover compiler execution is dispatched to the Colab worker.

## Recovery

If the Colab runtime restarts, repeat the launcher flow. Existing jobs, generated claim history, terminal results, and chunked logs remain visible on `colab-runner-state`. Stale claims are recovered by append-only generation takeover rather than overwriting prior claim history.
