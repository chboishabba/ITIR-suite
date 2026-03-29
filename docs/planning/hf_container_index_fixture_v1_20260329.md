# HF Container/Index Fixture `v1` (2026-03-29)

## Goal

Provide one tiny concrete fixture for the HF container/index contract so later
implementation can target a stable minimal shape.

## Fixture file

Use:

- `docs/planning/jmd_fixtures/hf_container_index_v1.example.json`

as the first bounded example.

## What the fixture proves

The fixture demonstrates:

- one logical artifact revision
- one HF container object
- multiple logical shard members inside that container
- shard identity preserved independently of the HF object path

## Intended read

The fixture should be read in this order:

1. identify the artifact:
   - `artifactId`
   - `artifactRevision`
2. identify the container:
   - `containerId`
   - `containerRevision`
   - `containerObjectRef`
3. identify the members:
   - `shardId`
   - `contentDigest`
   - `memberPath`
   - `sizeBytes`
4. recover payloads by:
   - selector -> logical shard ids -> member entry -> HF object -> member path

## Minimal invariants

The fixture is valid only if all of these hold:

- `artifactId` and `artifactRevision` are explicit
- container metadata is distinct from logical shard identity
- each member entry repeats:
  - `shardId`
  - `contentDigest`
  - `memberPath`
  - `sizeBytes`
- HF object path appears only under container metadata, not as shard identity

## Why this is enough for now

This fixture is intentionally tiny.

It is only meant to unblock:

- code-facing spec discussions
- deterministic fixture tests later
- small rehearsal harnesses

It is not trying to solve:

- exact tar byte-offset indexing
- partition sharding strategy
- IPFS mirror representation
- spectral ranking metadata
