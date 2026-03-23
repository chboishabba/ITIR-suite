# Casey x JMD MDL Contract (2026-03-22)

## Purpose
Define the first precise interop contract between the existing JMD-facing
object/shard surfaces and a Casey/SL-side normalization plus MDL proof layer.

This note is intentionally narrower than a full runtime integration plan.

## Main decision
Phase-1 interop does not require a JMD-side pull request.

If ITIR/SL can already:

- read JMD-facing raw or object surfaces,
- emit structured semantic atoms or graphs,
- normalize those graphs,
- and attach MDL-style proof objects on the ITIR/SL side,

then that is enough to start interoperability work locally.

An upstream JMD-side change is only justified later when first-class,
proof-carrying interop is desired inside JMD-native step or shard objects.

## Current implementation status (2026-03-23)
Implemented locally in ITIR-suite:

- a read-only `itir_jmd_bridge` runtime lane that resolves runtime objects,
  runtime graphs, and runtime receipts from paste/raw plus ERDFA-facing inputs
- a local prototype that can:
  - project a real runtime bundle into graph-like input
  - discover candidate motifs
  - emit one transform plan
  - emit one MDL proof object
- a latest-post inspection path that summarizes prototype output over newest
  browse-page posts when host surfaces are available

Known uncertainties:

- the proof object shape is now real and tested, but still heuristic
- host browse/raw stability remains too weak to treat live latest-post checks as
  a dependable always-on validation surface
- replay policy for cached latest-index entries and cached resolved bundles is
  not yet pinned

## Narrow future PR surface
If a JMD-side PR is made, keep it intentionally tiny and optional.

Suggested optional fields on step/shard nodes:

- `sl:normal_form_cid`
- `sl:mdl_proof_cid`
- `sl:canonicalization_version`

These fields are additive and do not require JMD to adopt SL/Casey as the
authoritative canonicalization engine.

## Parties
Let:

- `J` = JMD stack: ERDFA, DASL, ZOS execution, shard representation
- `C` = Casey/SL stack: normalization, MDL search, canonical graph emission

`J` provides stable identity, storage, typing, and execution surfaces.
`C` provides quotienting, model selection, and canonicalized graph output.

## Exchange object
A Casey <-> JMD exchange object is:

`K = (cid_in, graph_in, norm_plan, graph_out, proof, meta)`

where:

- `cid_in`: CID or stable object id of the source JMD object
- `graph_in`: exported typed shard graph or root graph reference
- `norm_plan`: Casey-side transform plan
- `graph_out`: canonicalized graph emitted by Casey/SL
- `proof`: MDL proof object
- `meta`: versioning, invariants, interpreter information

## Contract laws
### Law A: Reconstructibility
There exists a decoder `decode_C` such that:

`decode_C(graph_out, norm_plan) = graph_in`

### Law B: Type preservation
For every node or edge in `graph_in`, normalization preserves the declared JMD
typing constraints or records an admissible refinement explicitly.

### Law C: Canonical address compatibility
If JMD canonicalization already maps semantic structure to stable DASL/DRISL
identity, Casey-side normalization must preserve those export laws.

### Law D: MDL monotonicity
For accepted transforms `T`:

`L(T(G)) <= L(G)`

### Law E: Execution verifiability
If JMD executes a step over `graph_out`, the output must still satisfy the
declared output CID contract.

### Law F: Proof-carrying optionality
Normalized outputs may attach:

- proof CID
- trace commitment
- interpreter version

without requiring the base runtime to understand the full proof system.

## MDL proof object
Minimal proof object shape:

```json
{
  "type": "sl::MDLProof",
  "version": "sl-mdl-proof@0.1.0",
  "input_cid": "cid:...",
  "input_graph_cid": "cid:...",
  "normalized_graph_cid": "cid:...",
  "dictionary_cid": "cid:...",
  "transform_plan_cid": "cid:...",
  "base_cost": 10432,
  "normalized_cost": 9811,
  "net_gain": 621,
  "reconstructible": true,
  "type_preserved": true,
  "canonical_export_preserved": true,
  "search_family": "macro_subgraph_v1",
  "interpreter_version": "casey-mdl@0.1.0",
  "proof_mode": "hash-stub",
  "proof_payload_cid": "cid:..."
}
```

## Verification rule
Verifier flow:

1. load `input_graph_cid`
2. load `transform_plan_cid`
3. recompute normalized graph
4. assert the recomputed graph CID equals `normalized_graph_cid`
5. recompute `base_cost` and `normalized_cost`
6. assert `normalized_cost <= base_cost`
7. assert reconstructibility and typing invariants
8. if `proof_mode == "zk"`, run the zk verifier

## Prototype scope
The first prototype should remain local to ITIR/SL and do only this:

- ingest a graph-like JSON object,
- discover reusable candidate motifs,
- apply one explicit transform plan,
- emit normalized graph plus dictionary,
- emit an MDL proof object keyed by content hashes/CIDs.

That is enough to prove the bridge shape without opening an upstream PR.

## Current prototype limits
- candidate discovery is still lexical/motif-oriented rather than a richer
  graph rewrite search
- the runtime-bundle projection is improving, but still a projection layer
  rather than a canonical ERDFA semantics reader
- proof mode remains `hash-stub`; there is no JMD-native verification surface
  yet
- latest-post evaluation still depends on host reachability unless local replay
  caches are added

## Non-goals

- not a commitment that JMD must consume Casey graphs directly today
- not a requirement to move ephemeral runtime events into content-addressed
  semantic events yet
- not a claim that the first proof object must already be zero-knowledge

## Relationship to the existing bridge notes
This note refines:

- `docs/planning/jmd_sl_corpus_bridge_contract_20260319.md`
- `docs/planning/jmd_triage_roadmap_20260320.md`

It does not replace them. It clarifies the local proof-carrying
normalization lane within the already-approved read-only JMD object graph ->
SL corpus graph bridge.
