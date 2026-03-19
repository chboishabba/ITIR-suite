# JMD x ITIR Intended Surface (2026-03-19)

## Purpose
Record the intended future integration surface between JMD-style shard graphs
and the current ITIR stack without promoting it to an active repo contract.

## Source context
- resolved via `robust-context-fetch`
- title: `Dependency-aware task scheduling`
- online UUID: `69bb8ef6-e9d0-839c-a917-ae92116a02cd`
- canonical thread ID: `2a13394ff8c932629d42aed76bb07f049eede036`
- source used: `db` after pulling the online UUID into `~/chat_archive.sqlite`
- related archived thread:
  - title: `Full Stack Architecture`
  - online UUID: `69bb70ca-19ac-83a0-a087-8d2416e8be07`
  - canonical thread ID: `fe1aead0a943806609b767cf3c27e2eeef2e54f1`
  - source used: `db` after direct UUID pull into `~/chat_archive.sqlite`
  - main relevance:
    - Rabbit is described as the process/queue I/O fabric
    - pastebin/IPFS behaves like persistent shared memory/state
    - ERDFA is better treated as canonical structural/shard substrate than as
      an embedding layer
    - Rust appears as a programmable transform/execution layer via custom rust
      driver/plugin tooling

## Intended surface only
This note is awareness/documentation only.

It does **not** mean:
- Casey now owns JMD task execution
- fuzzymodo now owns JMD-native scoring semantics
- StatiBaker now has a committed JMD receipt schema
- the repo currently ships a JMD/ERDFA adapter

## Draft role mapping
- JMD/ERDFA shard graph:
  external structured task/content graph
- Casey:
  mutable execution-state / candidate-state runtime
- fuzzymodo:
  scoring/ranking/advisory layer over ready or competing nodes
- StatiBaker:
  append-only receipt/audit trace for execution decisions

## Draft minimal shape
- shard `cid` acts like task identity
- shard links act like dependency edges
- Casey runtime may later host local execution state for those task nodes
- fuzzymodo may later score ready nodes or alternatives without mutating Casey
- StatiBaker may later record execution receipts by reference only

## Caution
Keep this as a planning surface until there is:
- a concrete JMD-side repo or adapter target
- a pinned shard schema to integrate against
- an explicit contract note for the actual producer/consumer boundary

## Immediate implication
The repo should stay aware of this as a future surface, but current execution
priority remains:
1. Casey -> fuzzymodo
2. Casey -> StatiBaker
3. only then broader external graph/task integrations
