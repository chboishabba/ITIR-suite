# GWB U.S.-Law Linkage Seed (2026-03-07)

## Purpose
Create a deterministic reviewed seed set that ties visible George W. Bush
timeline actions to reviewed U.S.-law institutions, courts, and statutes so the
later cross-jurisdiction analysis has a concrete starting point and an auditable
shared-DB report surface.

## Scope
This seed is intentionally reviewed and bounded, but it is no longer just a
tiny starter pack:
- all clearly visible U.S.-law lanes currently surfaced in the checked GWB corpus
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

## Current Reviewed Seed Targets
- Iraq War authority:
  - anchor action: Iraq invasion / war authorization decisions
  - U.S.-law authority: Authorization for Use of Military Force Against Iraq Resolution of 2002
  - institutions: U.S. Senate, U.S. House of Representatives
- Clear Skies lane:
  - anchor action: Clear Skies proposal and related Clean Air Act framing
  - U.S.-law authority: Clear Skies Act of 2003, Clean Air Act
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
- Syria sanctions lane:
  - anchor action: Bush signing the Syria Accountability Act
  - U.S.-law authority: Syria Accountability Act
- Stem cell lane:
  - anchor action: Bush veto of the Stem Cell Research Enhancement Act
  - U.S.-law authority: Stem Cell Research Enhancement Act
- SCHIP veto lane:
  - anchor action: veto of State Children's Health Insurance Program legislation
  - U.S.-law authority: SCHIP / State Children's Health Insurance Program
- Genetic discrimination lane:
  - anchor action: signing the Genetic Information Nondiscrimination Act
  - U.S.-law authority: Genetic Information Nondiscrimination Act
- Supreme Court appointments lane:
  - anchor action: Roberts / Alito nominations and Senate confirmation path
  - court/institutions: U.S. Supreme Court, U.S. Senate
- Congressional subpoena litigation lane:
  - anchor action: congressional subpoena and immunity litigation path
  - institutions/courts: House of Representatives, district-court lane

## Non-Goals
- final legal analysis
- broad person/entity linking
- ingesting chat-derived text into canonical legal storage
- forcing every GWB event into a U.S.-law row

## Current Implementation Status
- Reviewed seed is checked in at
  `SensibLaw/data/ontology/gwb_us_law_linkage_seed_v1.json`.
- Shared DB import/query surface exists in `itir.sqlite` via:
  - `gwb_us_law_linkage_seeds`
  - `gwb_us_law_linkage_seed_authorities`
  - `gwb_us_law_linkage_seed_refs`
  - `gwb_us_law_linkage_seed_cues`
  - `gwb_us_law_linkage_matches`
  - `gwb_us_law_linkage_match_receipts`
- Deterministic importer / runner / reporter exists in
  `SensibLaw/scripts/gwb_us_law_linkage.py`.

## Current Live Run Status
On the current DB-backed GWB run:
- `event_count`: `142`
- `matched_event_count`: `15`
- `ambiguous_event_count`: `8`
- matched seeds: `11 / 11`
- strongest clean lanes are the explicit reviewed authority-title and
  court/institution lanes (`Clear Skies`, `Syria Accountability Act`,
  `Stem Cell Research Enhancement Act`, `Genetic Information
  Nondiscrimination Act`, `NSA surveillance review`, `Supreme Court
  appointments`)

## Next Step
Tighten generic cue handling so broad cues like `Congress`, `Iraq`, `veto`, and
`Supreme Court` require stronger co-signals before promotion, while keeping the
current DB-backed report and receipt surface stable.
