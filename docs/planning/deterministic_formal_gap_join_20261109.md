# Deterministic formal gap join (no AO orchestrator)

A batch invocation of the **existing** `itir.formal.inspect` and
`itir.formal.route` functions. It neither creates a new semantic engine nor
invokes any LLM or orchestration services.

## Why it exists

The Agda preflight service already knows source declarations, related symbols,
proof-owner discovery, requirements and dependency closures. The ITIR formal
MCP already supplies bounded, candidate-only inspect and obligation-routing
receipts. Rather than duplicating any of that, `scripts/formal_gap_join.py`
takes explicit *formal obligations* and runs the two tools as a deterministic
join. An external orchestrator may invoke the script, but the script never
dispatches an agent.

The separate `formalverification/lean2agda` translator is a **candidate
transport implementation**, not the gap-finding service. Its issue #61 is
outreach, not completion of library translation. The user's existing
`chboishabba/agda2lean` repository already implements the reverse direction
with independent Lean validation. Both remain outside the scope of this script.

## Invocation

```sh
export PYTHONPATH=itir-mcp/src
export DASHI_AGDA_ROOT=/path/to/dashi_agda
export DASHI_AGDA_INDEX=/path/to/dashi_agda/.dashi/repository.sqlite3

python scripts/formal_gap_join.py \
  --input /tmp/formal_obligations.jsonl \
  --output /tmp/formal_gap_candidates.jsonl
```

One input row per independent formal demand:

```json
{"obligation_ref":"example:hecke:1","target_prover":"lean","query":"Hecke prime-power recurrence","statement_digest":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}
```

The caller **must** provide the real statement SHA-256 digest instead of the
example's placeholder. Output is sorted by `obligation_ref` and always
`candidate_only=true`, `establishes_proof=false`,
`discharges_obligation=false`. The original `statement_digest` is forwarded
unaltered to `proof_route_for_obligation`; no guessed equivalence is promoted.

**Source prerequisites:** The caller is responsible for running
`dashi-repo index` and ensuring the inventory is fresh; the script uses the
existing `DashiAgdaMcpTools` provider and its configured database. The
`itir_mcp.formal_tools` default database path may be historical: set
`DASHI_AGDA_INDEX` explicitly to the canonical index.

Run offline unit tests:

```sh
python -m unittest discover -s tests -p 'test_formal_gap_join.py' -v
```

## Precise boundary

- This is **Agda owner/gap discovery for either Agda or Lean target obligations**.
  It does not elaborate all 21,481 external Lean repositories.
- An external Lean declaration must first be inspected in its pinned Lean
  environment and attached as source evidence; source metadata or
  names alone cannot pay the target obligation.
- A later source-aware, kernel-checked Lean-to-Lean proof is checked by Lean.
  A subsequent Lean-to-Agda transport may use lean2agda, where translation
  is supported and independent Agda acceptance is obtained.
- ITIR's existing `itir.formal.certify` is a separate trusted-referee
  boundary: candidate evidence cannot invoke it to declare a proof.
- The emitted JSONL is an **ephemeral interoperability receipt**, not a new
  canonical database. Persistence, if required, belongs to the existing
  formally governed authority.
- Unpublished DASHI proof material is not submitted to upstream repositories.
  No third-party issue, PR, comment or upload is performed.

## Remaining acceptance cut

1. Verify the default `itir.formal.*` provider works against the current
   `dashi-repo` canonical index and is not reading stale metadata.
2. Execute the tests and a real two-obligation batch on the pinned
   `dashi_agda` checkout, retaining exact candidate/absence receipts.
3. Supply Lean-source declaration metadata for selected cross-corpus donors
   and make its *elaborated* type available to the source-aware matcher.
4. Connect an actual kernel-accepted Lean proof-reuse result, retaining
   assumptions, axiom closure and source revision.
5. Require separately accepted Agda translation/interpretation before
   declaring a Lean donor's theorem available as an Agda theorem.

Do not introduce a new AO fleet, orchestration state, PNF authority, source
parser, theorem fingerprint system, or proof transport here.

## Translator round-trip interoperability (2026-11-09)

The **authoritative** translator-specific phase/deliverable/exact-lemma
ledger is [agda2lean/docs/BIDIRECTIONAL_ROUNDTRIP_MAX_CUT.md](https://github.com/chboishabba/agda2lean/blob/main/docs/BIDIRECTIONAL_ROUNDTRIP_MAX_CUT.md).
Existing `itir.formal.inspect`, `itir.formal.route`, and this
`scripts/formal_gap_join.py` remain read-only, candidate-only source
discovery. Neither the AO fleet nor LLM orchestration is part of this
mathematical script.

Bidirectional benchmark roles are explicitly separate:

1. `dashi_lean4`/Lean: primary ingestion and kernel checking for external
   Lean theorem donors.
2. `agda2lean`: Agda → Lean typed-IR and strict capability/translation;
   plus the new round-trip source/audit runner and feature taxonomy.
3. `formalverification/lean2agda`: independent Lean → Agda candidate
   translator, inspected but not modified.
4. `dashi_agda`: Agda source-owning theorem proof and cross-language
   representation/correspondence obligations.
5. `ITIR-suite`: a small external-automation-optional gap query,
   **not** the runtime or theorem proof authority.

The audited corpora have 19 agda2lean feature fixtures, zero source-promoted
correspondences, and 12 lean2agda hand-translation corpus entries. A
conservative reviewed feature crosswalk creates 42 candidate pairs;
zero become formal equivalences by lookup. Generic inverse-law theorems
have been written on Agda and Lean sides, but neither a real selected
translation cycle nor the two required independent kernel receipts has
yet been executed and paid by this effort.

No unpublished DASHI source is supplied to upstream maintainers.
