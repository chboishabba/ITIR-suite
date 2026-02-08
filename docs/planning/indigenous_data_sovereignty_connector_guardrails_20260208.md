# Indigenous Data Sovereignty Connector Guardrails (2026-02-08)

## Purpose
Define mandatory guardrails for connectors and overlays that may intersect with
Indigenous people, Country, community knowledge, and seasonal systems.

This is a contract/policy document for implementation work.

## Scope
- SB observed-signal connectors (`social_*`, future iNaturalist/ecology feeds).
- Context overlays (`context_type=indigenous_season`, `agro_ecological`).
- Location timeline overlays (`context_type=location_timeline`).
- Cross-lane promotion into SL/ITIR authoritative lanes.

## Non-negotiable rules
1. Community authority and provenance are required.
- `provenance` must include source authority where available (community org,
  ranger program, nation/locale, publication or data steward).
- Unknown authority must be explicit; do not backfill with guessed labels.

2. Consent and purpose limitation.
- Collect only metadata required for the declared operational purpose.
- No ingestion of private message bodies, sacred text, or cultural narratives by
  default.
- Promotion from observer signals requires explicit promotion receipt and policy
  receipt reference.

3. No silent flattening.
- Indigenous seasonal systems must not be auto-collapsed into Gregorian-only
  buckets.
- Parallel representations are allowed; forced one-to-one mapping is not.

4. No causal overreach.
- Context overlays cannot assert behavioural or legal causation on their own.
- Rendering must avoid language that claims cultural determinism.

5. Spatial and identity minimization.
- Coarse location by default for ecology/community signals unless stronger
  precision is explicitly authorized.
- Hash identifiers at the adapter boundary.
- For personal location timelines, default to coarse hashed cells; do not ingest
  addresses, place names, or raw coordinates into observer-class lanes.

## Connector implementation checklist
- Meta-only schema enforced at adapter boundary.
- Forbidden fields red-team test coverage.
- `provenance.source` + `provenance.collected_at` always present.
- If Indigenous context is represented, include provenance authority metadata.
- For unresolved authority/consent fields, fail closed or tag record as
  non-promotable.

## Integration notes (current)
- Existing `context_type` already includes `indigenous_season`.
- Messaging stubs (FB Messenger, Telegram, WhatsApp) remain observer-class
  metadata only; no content ingestion.
- Future iNaturalist connector should follow this contract before enabling
  trend-derived overlays in UI.

## Open decisions
- Minimal required schema for `provenance.authority` values.
- Promotion workflow for community-reviewed semantic anchors.
- Default geo-coarsening policy by connector class.
