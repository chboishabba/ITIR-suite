# ITIR Windows Compliance MCP Contract (2026-04-07)

This note defines the intended Windows endpoint compliance lane for `ITIR-suite`
as a bounded MCP-first contract. It is a planning artifact only. It does not
mean the Windows tool family is implemented today.

## Purpose

Use `ITIR` / `SL` / `SB` as a deterministic evidence, evaluation, explanation,
and audit stack around Windows endpoint state.

The intended posture is:

- Windows tools collect normalized evidence
- `SL` evaluates that evidence against executable controls
- `SB` records receipts, plans, approvals, and post-check outcomes
- remediation remains harder than observation or evaluation

The tool family must not collapse into "agent edits Windows directly."

## Core doctrine

Windows administration is split into four surfaces:

1. observe
2. evaluate
3. plan
4. act

Only `observe` and `evaluate` should be easy by default.

`act` must remain tightly gated by policy, approval, scope, and receipts.

## Intended tool family

The planned `itir-mcp` tool family is:

- `itir.windows.collect_registry`
- `itir.windows.collect_policy_state`
- `itir.windows.collect_service_state`
- `itir.windows.collect_local_security_state`
- `itir.windows.collect_eventlog_state`
- `itir.windows.evaluate_profile`
- `itir.windows.plan_remediation`
- `itir.windows.apply_remediation`

This family should follow the same canonical contract doctrine as the existing
comparison lane:

- MCP is the primary contract layer
- bridge or HTTP shells are transport details
- results are deterministic, structured, and auditable

## Safety posture by tool class

### Evidence tools

These are read-only and safe by default.

- `collect_registry`
- `collect_policy_state`
- `collect_service_state`
- `collect_local_security_state`
- `collect_eventlog_state`

They must return normalized evidence objects, not prose summaries.

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

## Evidence-first contract

The intended flow is:

```text
endpoint
  -> evidence snapshot
  -> policy evaluation
  -> compliance result
  -> optional remediation plan
  -> optional approved action
```

Not:

```text
prompt
  -> agent
  -> direct registry or system mutation
```

## Example evidence object

Registry collection should normalize to a deterministic evidence shape:

- host id
- timestamp
- source kind
- hive
- path
- name
- value type
- value data
- presence

This evidence object is the canonical substrate for Windows registry checks.

## Example evaluation posture

Windows compliance should compile prose controls into executable rules such as:

- PowerShell script block logging enabled
- Defender enabled
- Firewall enabled
- BitLocker enabled on system volume
- SMBv1 disabled
- LSASS protection enabled
- local Administrators membership constrained
- event log retention configured

The first useful profile is a small Windows endpoint auditability profile, not a
full remote-management framework.

## Managed-host extension beyond registry

The same contract extends naturally from registry checks to broader managed-host
and rollout control surfaces.

Expected evidence families include:

- remote shell or remote command posture
- patch and update state
- firewall and network policy state
- installed software inventory
- scheduled tasks and startup entries
- configuration file state
- process and listener inventory
- certificate store posture
- local or directory-backed group membership

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

- endpoint managers
- RMM tools
- patch rollout systems
- remote shell or PowerShell controllers
- registry/policy/service/firewall managers
- CI/CD deploy controllers
- fleet configuration systems

It is not the posture for arbitrary agent-directed remote administration.

### Managed-host safety doctrine

- observe, evaluate, and plan are the default-safe classes
- apply remains the most heavily gated class
- post-state verification is mandatory after any consequential action
- `SB` receipts must capture:
  - what changed
  - why it changed
  - what evidence justified it
  - whether verification passed
  - whether rollback was required

### Typical managed-host policy questions

Examples that fit this lane:

- all Windows endpoints must have PowerShell Script Block Logging enabled
- no reboot during a blocked business-hours window unless severity is critical
- deny remote action if host identity, environment, or approval state is uncertain
- allow rollout only when canary verification passed and blast radius is bounded

This remains a future extension of the same evidence/evaluate/plan/apply model,
not a license for broad mutable automation.

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

It does not redefine Windows semantics, compliance rules, or `SB` governance.

## Constraints and invariants

- read-only evidence collection must remain easier than mutation
- direct mutable remote-admin posture is not the primary surface
- all action tools must be subordinate to evidence, evaluation, and receipts
- missing or conflicting evidence must allow abstention
- outputs must remain structured and deterministic
- policy, explanation, and enforcement must use one reason-code vocabulary

## Relationship to the existing guarded MCP lane

This Windows family should sit under the same guarded doctrine already used for
`safe_call`:

- all tool outputs are proposals until verified
- sensitive or privileged actions require policy gating
- receipts are mandatory for consequential decisions

Windows evidence collection is therefore a natural future extension of the
existing:

- classification
- verification
- status explanation
- receipt

surfaces already present in `itir-mcp`.

## Separate trust model: public discovery is not managed-host authority

Public internet and social-source discovery is a distinct lower-trust lane and
must not be conflated with managed-host evidence.

Discovery sources such as:

- X/Twitter
- blogs
- newsletters
- forums
- GitHub repositories and READMEs

are suitable for proposal and triage only.

They may propose:

- candidate findings
- risk hypotheses
- evidence references
- follow obligations

They must not directly authorize:

- internal enforcement
- exploitability claims as fact
- autonomous remote remediation
- fleet changes on managed systems

The governing doctrine is:

```text
Public discovery proposes risk.
Internal evidence authorizes action.
```

Managed-host action therefore requires recollected internal evidence even when a
public discovery lane first surfaces the issue.

## Current state

As of 2026-04-07:

- this is a planned contract only
- no Windows collector/evaluator/remediation tool family is implemented here
- remediation remains intentionally deferred behind the evidence/evaluate seam
