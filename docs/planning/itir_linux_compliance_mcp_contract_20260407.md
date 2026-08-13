# ITIR Linux Compliance MCP Contract (2026-04-07)

This note defines the intended Linux endpoint compliance lane for `ITIR-suite`
as a bounded MCP-first contract. It is a planning artifact only. It does not
mean the Linux tool family is implemented today.

## Purpose

Use `ITIR` / `SL` / `SB` as a deterministic evidence, evaluation, explanation,
and audit stack around Linux host state.

The intended posture is:

- Linux tools collect normalized evidence
- `SL` evaluates that evidence against executable controls
- `SB` records receipts, plans, approvals, and post-check outcomes
- remediation remains harder than observation or evaluation

The tool family must not collapse into "agent edits Linux directly."

## Core doctrine

Linux administration is split into four surfaces:

1. observe
2. evaluate
3. plan
4. act

Only `observe` and `evaluate` should be easy by default.

`act` must remain tightly gated by policy, approval, scope, and receipts.

## Linux as a distributed configuration surface

Windows has a strong registry-centered configuration substrate.

Linux should be treated as a distributed configuration substrate across:

- configuration files
- service state
- kernel/sysctl state
- firewall and network state
- package inventory
- process and listener state
- auth and identity configuration

The architecture stays the same:

```text
collect
  -> normalize
  -> evaluate
  -> explain
  -> optional remediation plan
  -> optional approved action
```

## Intended tool family

The planned `itir-mcp` tool family is:

- `itir.linux.collect_state`
- `itir.linux.evaluate_profile`
- `itir.linux.plan_remediation`
- `itir.linux.apply_remediation`

This family should follow the same canonical contract doctrine as the existing
comparison lane:

- MCP is the primary contract layer
- bridge or HTTP shells are transport details
- results are deterministic, structured, and auditable

## Evidence-first Linux posture

Linux has no single registry-equivalent authority surface, so evidence must be
collected across several bounded families and normalized into one reusable host
state object.

Expected evidence families include:

- files under `/etc/` and related config roots
- `systemd` unit state
- `sysctl` and `/proc/sys/*` state
- firewall posture (`iptables`, `nftables`, `ufw`, `firewalld`)
- package inventory
- process and network listener inventory
- identity/auth surfaces such as:
  - `/etc/passwd`
  - `/etc/group`
  - `sudoers`

They must return normalized evidence objects, not prose summaries.

## Example managed-host loop

The intended full managed-host control loop is:

```text
observe
  -> evaluate
  -> plan
  -> approve or gate
  -> apply
  -> verify
  -> receipt
```

This is the correct posture for:

- Linux fleet hardening
- baseline compliance checking
- SSH and auth posture checks
- firewall and network policy checks
- package/update state checks
- controlled rollout and remediation planning

It is not the posture for arbitrary agent-directed shell execution.

## Typical Linux control questions

Examples that fit this lane:

- SSH root login disabled
- firewall enabled
- IP forwarding disabled where not explicitly required
- `sudo` posture constrained
- unsafe services disabled
- required logging/audit surfaces enabled

The first useful target is a small Linux endpoint auditability profile, not a
full generic remote-management framework.

## Safety posture by tool class

### Evidence tools

These are read-only and safe by default.

- `collect_state`

They should normalize file, service, kernel, network, and auth state into one
bounded host evidence object.

### Evaluation tools

These consume evidence and executable control profiles.

- `evaluate_profile`

They must return:

- satisfied / not_satisfied / insufficient_evidence / conflicted
- evidence references
- reason codes
- derived signals where needed

### Planning tools

These propose changes but do not apply them.

- `plan_remediation`

They must emit:

- exact proposed changes
- rollback steps
- justification by control id
- bounded target scope

### Action tools

These change the host and therefore require the strongest controls.

- `apply_remediation`

They must only run when:

- target identity is verified
- scope is authorized
- rollback is known
- a matching plan exists
- `SB` receipt creation is enforced
- an approval posture is satisfied

## Role split

### ITIR / SL

Own:

- evidence normalization
- derived signals
- control evaluation
- contradiction handling
- explanation

### SB

Own:

- receipts
- policy outcomes
- approval and execution logging
- plan tracking
- post-check recording

### MCP layer

Owns the contract boundary only.

It does not redefine Linux semantics, compliance rules, or `SB` governance.

## Constraints and invariants

- read-only evidence collection must remain easier than mutation
- direct mutable remote-admin posture is not the primary surface
- all action tools must be subordinate to evidence, evaluation, and receipts
- missing or conflicting evidence must allow abstention
- outputs must remain structured and deterministic
- policy, explanation, and enforcement must use one reason-code vocabulary
- Linux config must be verified from live state, not inferred from a single file

## Relationship to the existing guarded MCP lane

This Linux family should sit under the same guarded doctrine already used for
`safe_call`:

- all tool outputs are proposals until verified
- sensitive or privileged actions require policy gating
- receipts are mandatory for consequential decisions

Linux host evaluation is therefore a natural future extension of the existing:

- classification
- verification
- status explanation
- receipt

surfaces already present in `itir-mcp`.

## Relationship to managed-host and discovery trust models

This is a higher-trust managed-host lane, like the Windows lane.

It is distinct from lower-trust public repo/social discovery:

- public discovery proposes risk
- internal evidence authorizes action

Public-source findings may trigger Linux exposure checks, but they do not
authorize Linux remediation on their own.

## Current state

As of 2026-04-07:

- this is a planned contract only
- no Linux collector/evaluator/remediation tool family is implemented here
- remediation remains intentionally deferred behind the evidence/evaluate seam
