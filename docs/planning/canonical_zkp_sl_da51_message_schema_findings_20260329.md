# Canonical ZKP / SL / DA51 Message Schema Findings (2026-03-29)

## Goal

Record the useful repo-facing part of the fetched thread
`69c3f3e7-3440-839c-8a3e-05309f1269dd`
without overstating it as a finished wire contract.

## Thread provenance

- title:
  `Canonical ZKP ↔ SL ↔ DA51 message schema`
- online UUID:
  `69c3f3e7-3440-839c-8a3e-05309f1269dd`
- canonical thread ID:
  `d70ac076cbdc08df81a593b66a8915541f71f08b`
- source used:
  `db` after direct UUID pull into the canonical archive

## Current finding

The thread proposes a minimal, content-addressed message envelope that can move
across storage backends while preserving verifiability.

The useful high-level shape is:

- one human-friendly JSON projection
- one compact CBOR projection
- one content-derived stable ID
- optional signatures
- optional proof attachments
- explicit provenance/parent links as a DAG

This is directionally aligned with current ITIR work on:

- content-addressed artifacts
- DA51 / CBOR publication
- provenance-first contracts
- proof-first execution receipts

## Useful envelope fields

The thread's proposed minimal message shape includes:

- `id`
  - content-derived stable identifier
- `msg_type`
  - coarse message kind
- `sender`
  - sender identity + key reference
- `recipients`
  - explicit target set or broadcast
- `timestamp`
  - ISO-8601 UTC
- `provenance`
  - parent message/content refs
- `payload`
  - the actual semantic content
- optional `proof`
  - zero-knowledge or other attached proof material
- optional `signatures`
  - detached or embedded signature material

## Why this matters for ITIR

This does not replace the shard/artifact contracts already being written.

It does give a cleaner mental model for a cross-system message/envelope layer
that could sit around:

- JMD-side proof/execution receipts
- SL-side promoted/observed payloads
- DA51/CBOR shard references
- future content-addressed exchange between systems

In other words:

- shard/artifact contracts answer:
  "what artifact or shard is this?"
- message/envelope contracts answer:
  "what signed/provenanced transmission or event is carrying it?"

## Current limit

This fetched thread is useful as schema direction, not as a pinned ITIR wire
standard.

It does not yet specify:

- canonical hashing/canonicalization rules
- exact CBOR field layout
- signature suite or verification rules
- proof attachment conventions
- transport semantics

So the right current posture is:

- keep it as a useful future-facing envelope reference
- do not collapse existing shard or SL contracts into it
- do not claim the repo has adopted it as normative wire format yet

## Practical follow-up

If this direction is promoted later, the cleanest first use would be:

- wrap existing shard/artifact IDs or SL/JMD payloads in a small signed,
  provenance-linked envelope
- keep JSON and CBOR as projections of the same message identity
- keep message identity separate from sink location
