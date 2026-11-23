# Cursor Claude extension supply-chain incident: evidence contract v1

Date: 2026-11-01. Status: research-to-contract formalisation; **not an executable detector, proof certificate, host assessment or claimed remediation**.

## Source anchors and attribution

- Cursor Security, notice published 2026-10-29 and amended 2026-10-30: https://cursor.com/blog/claude-code-extension-security-notice
- Microsoft Security Research, independent analysis 2026-10-30: https://www.microsoft.com/en-us/security/blog/2026/10/30/inside-malicious-claude-code-branded-cursor-extension-persistent-ssh-backdoor/
- Phorion technical research: https://phorion.io/blog/offical-claude-code-vsx-compromise/
- Dan Goodin, Ars Technica, reporting 2026-10-30: https://arstechnica.com/security/2026/10/anthropic-vs-code-extension-on-cursor-backdoored-for-nearly-12-hours/

Reported distribution interval: 2026-10-29 09:27–20:35 UTC (approximate). The updated Cursor notice identifies versions 2.1.312 and 2.1.313 for macOS and Windows. An earlier article emphasized 2.1.313. Package identity is distinct from payload behavior: Linux-compatible behavior in analyzed code does not by itself establish Linux package distribution. Reported potential exposure of at most 5,000 users is not a verified count of backdoored or remotely accessed endpoints.

Microsoft reports Anthropic asserted its own systems were not compromised and that its npm package and the Microsoft VS Code marketplace were not affected. How the malicious packages entered Cursor's distribution path, and threat-actor identity, remain unresolved on the reviewed evidence.

## O / R / C / S / L / P / G / F

- O (organization): ITIR owns cross-project provenance contracts, SensibLaw owns normalized source claims and evaluation, StatiBaker owns review/receipts, managed-host lanes own endpoint observations, MCP enforces interface boundaries.
- R (request): prevent a marketplace publisher badge, version identifier or update from being confused with independently verified bytes or trusted runtime behavior.
- C (code): this contract provides formal abstract relations and negative acceptance vectors; no production module or Agda kernel result is claimed.
- S (sources): maintain individually dated, immutable anchors and explicit revision provenance when advisories are updated.
- L (logic): four independent propositions about package bytes, module execution, host persistence and remote authenticated access; use three-valued findings.
- P (postconditions): no unproved promotion between those propositions.
- G (governance): public advisories only open review obligations; internal evidence, permissions, scope and receipts gate action.
- F (formal gaps): actual package ingestion mechanism; individual host execution and access receipts; Linux package publication; macOS managed-host tool ownership; independent source-to-release reproducibility.

## Trust boundary

Author -> build provenance -> artifact digest -> marketplace -> automatic update -> IDE extension host -> user account and developer tools.

Marketplace verification attests only marketplace-associated identity. It does not logically imply the uploaded artifact was built by that software author or that its contents are harmless.

The malicious injected loader is reported to have executed upon loading the extension module, before normal activation, and to have attempted host reconnaissance, unauthorized SSH access setup, persistence and reporting. Whether a particular remote-access attempt succeeded depends on the affected host configuration. Collected environment-variable names are not evidence that variable values were exfiltrated.

## Typed observations

PackageEvidence:
  package_digest, digest_kind, marketplace, claimed_publisher, extension_id,
  version, target_os, architecture, observation_time, install_time, evidence_anchor.

HostEvidence:
  host_reference, observed_installed_artifact, module_load_evidence,
  unauthorized_authorization_evidence, persistence_evidence,
  process_network_evidence, authenticated_session_evidence,
  evidence_anchor, evidence_collection_time.

ResponseEvidence:
  preservation_receipt, scope, plan, approval, execution_receipt,
  independent_postcheck, credential_review, provenance.

Unspecified evidence is UNKNOWN, never FALSE by default. Normalize independently of the specific marketplace, extension or endpoint product.

## Abstract propositions

Let:
- B(a): digest of artifact a matches a validated malicious-package hash;
- E(h,a): host h installed a during a supported suspect interval;
- X(h,a): malicious extension code execution is independently observed;
- K(h): unauthorized SSH authorization or persistence artifacts observed;
- T(h): suspect tunnel activity observed;
- A(h): a successful unauthorized interactive authentication was observed;
- R(h): verified recovery state, with separately evidenced cleanup and post-check.

Obligations:

- INV-01: VerifiedPublisher(a) does not imply AuthenticBuild(a).
- INV-02: Matching a reported version/time/channel is candidate exposure, not proof of module execution; matched malicious artifact digest is stronger evidence than version.
- INV-03: B(a) and E(h,a) do not imply X(h,a). X does not imply T. K and T do not imply A.
- INV-04: An extension update, extension uninstall, or infrastructure takedown does not imply R(h), because artifacts outside the extension directory may remain.
- INV-05: An absent single IOC cannot imply a clean host; host observation must account for coverage, retention and the collection method.
- INV-06: Names of environment variables being transmitted do not imply confirmed disclosure of corresponding secret values.
- INV-07: Publisher, source repository, package version, target architecture and actual artifact digest are separate typed coordinates.
- INV-08: Independent host evidence is required before public-source findings cause response actions.
- INV-09: Revisions to public advisories are new dated claims, not retroactive rewrites of earlier reporting.
- INV-10: Successful unauthorized access and verified remediation require distinct receipts, not just package or process indicators.

Output state is a product of independent dimensions:
  release: unknown | candidate | digest_match;
  execution: unknown | observed;
  persistence: unknown | observed;
  remote_access: unknown | attempt_observed | authentication_observed;
  recovery: not_assessed | planned | changed_unverified | independently_verified.

These are **not** a single scalar severity ranking; no branch promotes one state to a stronger state in another dimension.

## Owners and handoff

1. Public-source discovery: anchored risk candidate, versioned source reconciliation.
2. Managed-host Linux/Windows observations: read-only inventory, hashes, file and process observations, independent session evidence. Both tool families are currently described as planned in their contracts, not already implemented.
3. SensibLaw: shared evidence-carrier evaluation and contradiction handling, never Cursor-specific semantic primitives.
4. StatiBaker: structured review, bounded action approval and post-check receipts.
5. MCP: read-only by default; no autonomous host remediation from a public article.
6. Agda/Lean: eventual abstract invariant proofs must be separately authored, typechecked and attributed. This document is *not* kernel verification.

Parent references: itir_public_repo_security_discovery_contract_20260407.md, itir_linux_compliance_mcp_contract_20260407.md, itir_windows_compliance_mcp_contract_20260407.md, itir_security_non_agentic_posture_20260209.md.

## Negative test obligations

Reject: version-only equals trusted bytes; claimed publisher equals author signature; installation equals execution; an attempted backdoor equals successful authenticated access; metadata reconnaissance equals secret theft; missing one indicator equals clean; extension upgrade equals remediation; endpoint takedown equals host cleanup; public article equals approval for host modification. Hold when source, target or observation is incomplete.
