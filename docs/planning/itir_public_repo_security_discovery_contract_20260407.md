# ITIR Public Repo Security Discovery Contract (2026-04-07)

This note defines the intended lower-trust public discovery lane for
`ITIR-suite`. It is a planning artifact only. It does not mean this discovery
family is implemented today.

## Purpose

Use `ITIR` / `SL` / `SB` as a bounded discovery, triage, and follow-obligation
stack for public software/security signals without letting public content
silently become authority.

## Core doctrine

```text
Public discovery proposes risk.
Internal evidence authorizes action.
```

This lane exists to discover and structure candidate risk, not to autonomously
assert exploitability or trigger unmanaged action.

## Intended sources

- X/Twitter posts
- blogs and newsletters
- release posts and project announcements
- GitHub repositories
- README files
- package manifests
- Dockerfiles
- CI workflows
- example configuration files

## Intended flow

```text
public source
  -> candidate repo or artifact
  -> bounded ingest
  -> surface extraction
  -> risk hypothesis
  -> follow obligation
  -> optional internal exposure check
```

Not:

```text
tweet or README
  -> assumed truth
  -> autonomous enforcement
```

## Intended tool family

The planned `itir-mcp` family for this lane is:

- `itir.discovery.collect_public_repo_surface`
- `itir.discovery.collect_repo_workflow_surface`
- `itir.discovery.evaluate_repo_risk`
- `itir.discovery.plan_internal_exposure_check`

Any future mutable internal follow-on belongs to managed-host or rollout lanes,
not to the public discovery lane itself.

## Output posture

This lane should emit structured candidate findings such as:

- candidate finding id
- risk category
- confidence band
- evidence references
- reason codes
- recommended next action

Expected next actions include:

- inspect internal exposure
- inspect auth boundary
- inspect update path
- hold for review

## Good candidate detections

Suitable deterministic or semi-deterministic findings include:

- secrets committed
- dangerous install instructions
- broad token or OAuth requirements
- risky Docker or runtime flags
- suspicious CI workflow patterns
- unsigned release or update paths
- missing `SECURITY.md`
- weak or unclear trust boundaries
- plugin or MCP exposure without a clear auth boundary

These remain candidate findings until corroborated.

## Trust model

### High-trust lane

Managed internal systems:

- endpoints
- servers
- fleet rollout
- known configuration state

These can authorize action because:

- identity is known
- evidence can be recollected
- rollback can be specified
- policy is local and owned

### Lower-trust lane

Public discovery sources:

- social posts
- public repos
- READMEs
- claimed behavior in documentation

These can only authorize:

- proposal
- triage
- follow obligation

They cannot authorize remediation on their own.

## Relationship to managed-host lanes

This lane is designed to feed managed-host and compliance lanes, not replace
them.

The intended handoff is:

```text
public candidate finding
  -> internal exposure check
  -> internal evidence
  -> managed evaluation
  -> optional remediation plan
```

This means a public discovery lane may cause `SB` to open a follow obligation,
but any actual action on managed systems still requires internal evidence,
policy, and receipts.

## Role split

### ITIR / SL

Own:

- bounded surface extraction
- risk hypothesis shaping
- candidate reason codes
- follow-obligation recommendations

### SB

Own:

- candidate-finding receipts
- review status
- exposure-check follow obligations
- escalation state

### MCP layer

Owns the contract boundary only.

It does not redefine public-source truth, exploitability, or remediation
authority.

## Constraints and invariants

- public-source findings remain hypotheses until corroborated
- tweets, READMEs, and repo metadata must not silently promote to truth
- no autonomous enforcement from public discovery alone
- findings must preserve provenance and evidence references
- internal action requires recollected internal evidence

## Current state

As of 2026-04-07:

- this is a planned contract only
- no public repo/security discovery family is implemented here
- the lane is intentionally separate from managed-host remediation
