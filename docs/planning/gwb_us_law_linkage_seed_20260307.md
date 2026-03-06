# GWB U.S.-Law Linkage Seed (2026-03-07)

## Purpose
Create a small deterministic seed set that ties selected George W. Bush
timeline actions to reviewed U.S.-law institutions, courts, and statutes so the
later cross-jurisdiction analysis has a concrete starting point.

## Scope
This seed is intentionally narrow:
- a few high-yield Bush-era actions
- explicit U.S. statutes or congressional authorities where applicable
- explicit U.S. courts or institutions where later litigation/review matters
- no broad open-world entity linking

## Seed Contract
Each seed row should record:
- stable local seed ID
- short action summary
- anchor/provenance cue from the GWB corpus or timeline text
- linked institutions/courts by canonical internal ref
- linked U.S.-law authorities by title
- notes on whether the item is executive action, litigation, or congressional authority

This seed is not a legal conclusion. It is a deterministic reviewed starting
pack for later legal pinning and reasoning.

## Initial Seed Targets
- Iraq War authority:
  - anchor action: Iraq invasion / war authorization decisions
  - U.S.-law authority: Authorization for Use of Military Force Against Iraq Resolution of 2002
  - institutions: U.S. Senate, U.S. House of Representatives
- Military commissions / detainee litigation:
  - anchor action: Military Commissions Act of 2006
  - U.S.-law authority: Military Commissions Act of 2006
  - court: Supreme Court of the United States
- NSA surveillance / review lane:
  - anchor action: warrantless surveillance controversy
  - U.S.-law authority: Foreign Intelligence Surveillance Act
  - courts: United States Court of Appeals for the Sixth Circuit, United States district court
- Defense/executive operations lane:
  - anchor action: defense/executive decision path involving the Department of Defense
  - institution: United States Department of Defense

## Non-Goals
- final legal analysis
- broad person/entity linking
- ingesting chat-derived text into canonical legal storage
- forcing every GWB event into a U.S.-law row

## Next Step
Promote the initial reviewed seed rows into a checked-in JSON artifact and make
them queryable from the shared DB or ontology import path without changing
canonical lexeme identity.
