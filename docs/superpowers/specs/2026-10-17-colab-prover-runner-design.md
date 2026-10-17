# Colab Prover Runner Design

**Date:** 2026-10-17  
**Status:** Proposed written specification for formal review  
**Owner:** ITIR-suite integration layer

## 1. Purpose

ITIR-suite needs a remote compiler-execution surface for proof repositories whose local policy forbids running Lean/Lake or Agda compiler builds on the local workstation. The approved execution host is a user-controlled Google Colab High-RAM runtime. Local work remains limited to static analysis, pytest, preflight, source editing, and PR management.

The runner must let both local agents and a cloud ChatGPT session submit exact-SHA Lean/Agda verification jobs, observe structured results, and preserve enough provenance to replay or challenge every compiler run.

This system is an execution adapter. It does not promote mathematical authority, merge pull requests, or reinterpret compiler output.

## 2. Upstream components and pinning

The implementation will integrate rather than fork the two official Google Colab projects:

- `googlecolab/google-colab-cli`, pinned initially to commit `006ff96ac2d0e4dcfb702467a76493d687929be8` (observed 2026-10-17). This is the primary headless execution/runtime control surface.
- `googlecolab/colab-mcp`, pinned initially to commit `b9ab3899e0f1fa493390b1fd6d54aa2e464ecdf1` (observed 2026-10-17). This is an optional local-agent/browser-session frontend, not the canonical execution protocol.

No upstream source is copied into ITIR-suite unless a later implementation step demonstrates that a small vendored patch is necessary. The default is commit-pinned installation plus attribution metadata.

The upstream Colab MCP server is browser/WebSocket mediated and dynamically proxies tools exposed by the connected Colab frontend. That makes it useful for local MCP clients, but insufficient as the sole bridge for this cloud ChatGPT session. The GitHub-backed relay defined below is therefore the canonical cross-environment protocol.

## 3. Architecture

The system has four layers.

### 3.1 Submission layer

A submitter creates one immutable job document at:

```text
.itir/colab/jobs/<job-id>.json
```

The submitter may be this ChatGPT session via the existing GitHub connector, a local CLI helper, or another approved agent using the same schema.

Jobs identify an immutable repository commit and one allowlisted prover operation. Arbitrary shell strings are not part of the public protocol.

### 3.2 Colab worker

A long-running worker in the user-controlled Colab runtime polls the job directory, validates candidate jobs against the JSON schema and policy, claims one job, materializes the requested repository at the exact commit, executes the corresponding allowlisted operation, and emits an immutable result.

The worker is generic. Lean and Agda are execution profiles, not separate queue implementations.

### 3.3 Result layer

Each completed or failed job produces:

```text
.itir/colab/results/<job-id>.json
.itir/colab/logs/<job-id>/<chunk-index>.txt
```

The result is the small machine-readable summary. Logs are chunked to avoid oversized GitHub blobs and response payloads.

The result binds to the job ID, canonical job digest, resolved repository commit, toolchain versions, exact argv after allowlist expansion, start/end timestamps, elapsed duration, exit code / terminal status, host/runtime metadata including memory observations, and ordered log chunk paths and hashes.

A result is a compiler receipt, not theorem authority. Consumers may use it only as evidence that a particular compiler invocation exited with the recorded status at a particular source SHA.

### 3.4 Optional Colab MCP frontend

`googlecolab/colab-mcp` remains an optional convenience surface for local MCP-capable clients. It may connect to the same Colab runtime and notebook, but it does not bypass the canonical job schema for repository verification jobs.

This prevents local-agent convenience behavior from becoming a second execution semantics.

## 4. Relay state machine and idempotency

The public state machine is:

```text
SUBMITTED -> CLAIMED -> RUNNING -> {SUCCEEDED | FAILED | REJECTED | ABORTED}
```

Jobs are immutable after submission. The worker never edits a job document.

To prevent duplicate execution, the worker creates a claim receipt before execution:

```text
.itir/colab/claims/<job-id>.json
```

A claim contains `job_digest`, worker identity, claim time, and lease metadata. Claim creation is compare-and-create: if another valid claim already exists for the same digest, the worker does not execute the job a second time.

A stale lease may be taken over only under an explicit stale-claim rule. The takeover is recorded; it never silently overwrites the original claim history. The implementation may use a generation suffix for takeover receipts if GitHub's file semantics make append-only takeover cleaner than mutation.

Repeated submission of byte-equivalent job content is safe. A submitter may reuse a job ID only when the canonical job digest is identical; conflicting reuse is rejected.

## 5. Job schema

The initial `colab_prover_job_v1` schema contains at least:

```json
{
  "schema_version": "colab_prover_job_v1",
  "job_id": "...",
  "repository": "chboishabba/dashi_lean4",
  "commit_sha": "40-hex-sha",
  "operation": "lake_build",
  "arguments": {"target": "QuantumMereology"},
  "toolchain_policy": "repo_pinned",
  "requested_by": "...",
  "created_at": "RFC3339",
  "resource_class": "high_mem",
  "timeout_seconds": 7200
}
```

### 5.1 Repository policy

Version 1 accepts only an explicit repository allowlist. Initial repositories are:

- `chboishabba/dashi_lean4`
- `chboishabba/dashi_agda`

The worker verifies that `commit_sha` exists in the named repository before execution and checks out that detached commit. Mutable branch names are never substituted for the requested SHA.

### 5.2 Operation allowlist

Version 1 operations are:

- `lake_build`
- `lake_env_lean`
- `agda_module`

Each operation has a typed argument object and a deterministic argv builder owned by the worker.

`lake_build` accepts a Lake target name or an explicit approved default target. It expands to an argv vector, not a shell command string.

`lake_env_lean` accepts one repository-relative `.lean` path, rejects path traversal and paths outside the checkout, and expands to `lake env lean <validated-path>`.

`agda_module` accepts one repository-relative `.agda` path plus a named include/profile selection. It rejects arbitrary flags and expands through the Agda execution profile.

No initial operation accepts `bash -c`, shell metacharacters, arbitrary environment overrides, arbitrary URLs, or arbitrary package installation commands.

## 6. Toolchain bootstrap and version policy

`scripts/colab_bootstrap_provers.py` prepares a fresh Colab runtime idempotently.

It installs or verifies Git, Python runtime dependencies for the worker, `elan`, baseline Lean `v4.35.0-rc3` and matching Lake availability, Agda plus the standard-library/package configuration required by the approved repositories, and the pinned `google-colab-cli` integration used to provision/control Colab sessions when operating from a headless local client.

The baseline Lean installation is available to the runtime, but **repository-pinned toolchains remain authoritative by default**. A `lake_build` or `lake_env_lean` job with `toolchain_policy = "repo_pinned"` respects the target checkout's `lean-toolchain`. Version 1 does not silently replace the repository toolchain.

The same rule applies to Agda configuration: repository/project configuration is preferred. The bootstrap supplies runtime dependencies; the execution profile records the exact Agda and stdlib versions actually used.

Bootstrap is idempotent and emits a machine-readable environment receipt so notebook setup failures can be diagnosed independently of proof-job failures.

## 7. Notebook integration

The user's draft Colab notebook remains a thin launcher, not the source of truth for runner logic.

The intended notebook flow is:

1. authenticate/access the required Colab runtime;
2. make the fine-grained GitHub credential available through Colab Secrets;
3. clone or fetch `ITIR-suite` at an approved runner commit;
4. run `scripts/colab_bootstrap_provers.py`;
5. run `scripts/colab_worker.py --poll`;
6. leave the worker running while jobs are submitted through GitHub.

The notebook may display status and logs, but all substantive worker, schema, bootstrap, and execution logic lives in version-controlled ITIR-suite files. A notebook restart must be recoverable by re-running the launcher cells.

No secret is embedded in the notebook, repository, job, result, or log.

## 8. Authentication and security boundary

The worker reads a dedicated fine-grained GitHub token from Colab Secrets/environment injection. The token must have the minimum permissions necessary to read the allowed source repositories, read ITIR-suite jobs/configuration, and create claim/result/log artifacts in the relay branch.

The runner never serializes token values or the full environment.

Mandatory controls are:

- repository allowlist;
- exact 40-hex commit SHA validation;
- operation allowlist;
- strict typed argument validation;
- repository-relative path normalization and traversal rejection;
- bounded timeout;
- bounded output/log chunk size;
- bounded concurrent jobs per worker;
- redaction of configured sensitive values from stdout/stderr before commit;
- no automatic merge, PR mutation, or theorem promotion from compiler success.

The worker executes in a fresh per-job checkout/worktree directory and removes or recycles it only after the result receipt has been durably written.

## 9. GitHub write model

The relay is append-oriented. Normal operation creates new files rather than repeatedly mutating a shared queue document.

The initial implementation targets a dedicated runner-state branch in `ITIR-suite`, tentatively `colab-runner-state`, rather than writing generated job/log noise to `main`. Source code remains on normal reviewed branches/main; runtime state remains isolated.

Submitters and the worker use optimistic GitHub writes. If the state branch advances, they refresh and retry their single-file create rather than force-pushing.

The worker never rewrites source branches in `dashi_lean4` or `dashi_agda`.

## 10. Result semantics

`colab_prover_result_v1` distinguishes at least:

- `SUCCEEDED`: requested process exited zero;
- `FAILED`: process ran and exited nonzero;
- `REJECTED`: job validation/policy failed before execution;
- `ABORTED`: infrastructure/runtime termination prevented a normal compiler result.

A successful result means only:

> At the recorded time, in the recorded Colab/runtime/toolchain environment, the recorded allowlisted command exited zero against the recorded repository commit.

It does not mean a PR is merge-safe, a theorem is physically true, a Clay problem is solved, or a repository's authority gates should change.

## 11. Runtime and resource receipts

Each job result records best-effort host metadata without exposing user secrets:

- Python version;
- OS/kernel identifier;
- CPU count;
- total/available memory sampled before and after execution;
- optional peak RSS for the child process where reliably measurable;
- Lean/Agda/Lake version strings relevant to the operation;
- Colab resource class requested/observed where available.

The worker must tolerate Colab runtime eviction. If the process can emit an `ABORTED` receipt before termination, it should; otherwise the next worker may identify an expired claim and perform a recorded takeover/retry.

## 12. Components to implement

The approved implementation surface is:

```text
tools/colab-runner/pyproject.toml
tools/colab-runner/README.md
scripts/colab_worker.py
scripts/colab_submit.py
scripts/colab_bootstrap_provers.py
schemas/colab_prover_job_v1.schema.json
schemas/colab_prover_result_v1.schema.json
tests/test_colab_prover_protocol.py
```

Supporting focused modules may be added under `tools/colab-runner/` when separation improves testability, for example:

```text
tools/colab-runner/src/itir_colab_runner/model.py
tools/colab-runner/src/itir_colab_runner/policy.py
tools/colab-runner/src/itir_colab_runner/executor.py
tools/colab-runner/src/itir_colab_runner/github_relay.py
tools/colab-runner/src/itir_colab_runner/runtime_receipt.py
```

The public scripts remain thin adapters over those generic modules, consistent with ITIR-suite's generic-first rule.

## 13. Testing strategy

Implementation is tests-first.

Unit/contract tests must cover valid Lean and Agda job parsing, exact-SHA enforcement, repository allowlist enforcement, operation allowlist enforcement, path traversal rejection, deterministic argv construction, canonical job digest stability, duplicate-job/idempotency behavior, claim collision behavior, stale-claim policy, terminal result construction, log chunking and hashing, secret redaction, toolchain-policy handling, runtime receipt serialization, and the absence of any arbitrary-shell execution path.

Tests must not require an actual Colab allocation or actual Lean/Agda compiler invocation. Integration verification of the real worker happens on the provisioned Colab runtime after source/tests are locally green.

The first end-to-end acceptance jobs should be deliberately narrow:

1. `dashi_lean4`: `lake_build` for a known small target or the currently relevant `QuantumMereology` target at an exact commit;
2. `dashi_agda`: `agda_module` for one known canonical safe module at an exact commit.

Only after those receipts are validated should the worker be used for full-repository or long-running builds.

## 14. Failure handling

Failure domains stay separate:

- submission/schema failure -> `REJECTED` without repository checkout;
- repository resolution/checkout failure -> explicit phase failure;
- bootstrap/toolchain failure -> environment/bootstrap receipt plus job `ABORTED`/`FAILED` as appropriate;
- compiler nonzero exit -> `FAILED`, preserving stdout/stderr chunks;
- GitHub result-publish failure -> retain local pending result and retry publication without rerunning the compiler;
- runtime eviction -> claim lease expires; a later worker may perform a recorded retry.

A publication retry must never cause compiler re-execution if a durable local terminal result already exists.

## 15. Scope boundaries

Version 1 explicitly does **not** include arbitrary remote shell execution, automatic PR merging or source-branch mutation, direct mutation of `dashi_lean4` or `dashi_agda` source from Colab, automatic theorem-authority promotion based on compiler status, multiple cloud providers, a general CI replacement, guaranteed always-on Colab availability, automatic notebook editing through Drive, or copying the entire upstream Colab CLI/MCP implementation into ITIR-suite.

The narrow product is an exact-SHA, allowlisted, replayable prover execution lane with GitHub-visible receipts.

## 16. Acceptance criteria

The tranche is complete when:

1. ITIR-suite contains validated job/result schemas and a tested generic runner core.
2. A submitter can create a valid exact-SHA Lean or Agda job without arbitrary shell access.
3. The Colab worker can claim the job exactly once, checkout the exact SHA, execute the approved command, and publish a structured terminal receipt with chunked logs.
4. Bootstrap is idempotent on a fresh Colab runtime and records the actual prover toolchains.
5. The supplied notebook can launch bootstrap + worker without containing source-of-truth logic or secrets.
6. A cloud ChatGPT session can submit a job and inspect its result solely through the existing GitHub connector.
7. A local MCP-capable client may optionally use the pinned upstream Colab MCP frontend without creating alternate prover semantics.
8. No compiler success can automatically change theorem/Clay authority state.
