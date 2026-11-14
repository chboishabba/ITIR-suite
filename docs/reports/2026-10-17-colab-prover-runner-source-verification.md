# Colab Prover Runner Source Verification Boundary

This report records the pre-Colab source handoff state for `chatgpt/colab-prover-runner`.

## Connector-side static findings

- Runtime queue artifacts are absent from the reviewed source branch.
- Runtime state is fixed to `colab-runner-state`.
- Public operations are limited to `lake_build`, `lake_env_lean`, and `agda_module`.
- Public repositories are limited to `chboishabba/dashi_lean4` and `chboishabba/dashi_agda`.
- Jobs require exact 40-hex commit SHAs.
- Runner subprocess calls are argv-based and explicitly use `shell=False`.
- GitHub credentials are read from environment/Colab Secrets and are not serialized into jobs/results by the runner.
- Compiler receipts are explicitly non-authoritative for theorem truth, source merge, and Clay promotion.

## Verification not claimed here

No local pytest execution was available through the GitHub connector session, so no test-suite GREEN claim is made by this report. No Lean, Lake, or Agda compiler invocation has been performed locally. Real prover acceptance remains Colab-only after local pytest/static verification.

Local permitted verification command:

```bash
pytest \
  tests/test_colab_prover_protocol.py \
  tests/test_colab_prover_relay.py \
  tests/test_colab_prover_worker.py \
  tests/test_colab_prover_bootstrap.py \
  tests/test_colab_prover_authority.py -v
```

After that passes, the next gate is Task 10 on the provisioned High-RAM Colab runtime.
