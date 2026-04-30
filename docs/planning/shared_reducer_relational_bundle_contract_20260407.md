# Shared Reducer Relational Bundle Contract (2026-04-07)

## Purpose

Define the smallest auditable upstream contract extension that preserves
deterministic structural bindings across the shared reducer boundary.

This is not a request for domain classification.
It is a request to stop collapsing canonical structural bindings back into flat
atoms before downstream consumers can inspect them.

## Problem

Current shared reducer output exposes:

- atomic token or lexeme occurrences
- span receipts
- existing structural refs

But it does not expose explicit bindings between:

- predicate head and arguments
- modifiers and heads
- conjunction members
- temporal anchors and scopes
- utterance composition mode

For canonical conversational text such as:

`how does crypto promise to hedge asset volatility and uncertainty in 2026`

the downstream consumer receives flat atoms rather than a reviewable structural
bundle. That forces any higher-order interpretation to happen through local
heuristics, which is the wrong owner and the wrong boundary.

## Ownership

- `SensibLaw` owns deterministic parser and reducer contracts.
- downstream consumers such as Mirror consume emitted evidence and map it
  locally, but should not recreate missing reducer structure through keyword
  lists.

This aligns with:

- `docs/planning/reducer_ownership_contract_20260208.md`
- `docs/planning/mirror_telegram_support_layer_boundary_20260401.md`
- `SensibLaw/docs/planning/event_assembly_portability_20260315.md`

## Request

Expose a bounded relation-emission layer in the shared reducer output.

The emitted surface must be:

- deterministic
- span-anchored
- provenance-bearing
- parser-derived from canonical text
- platform-agnostic
- domain-agnostic

The emitted surface must not:

- add routing logic
- add product-specific policy
- add ontology-heavy semantic labels
- expose keyword buckets as a consumer API

## Minimal General Relation Families

The smallest generic family that solves the present gap without domain creep:

- `predicate`
- `modifier`
- `conjunction`
- `temporal`
- `composition`

These are structural families only.
They do not claim domain semantics such as "finance", "risk", or "hedging".

## Contract Shape

### Input

- canonical conversational text

### Output

- existing atoms
- existing structure refs
- new `relations` bundle

The shared reducer remains responsible for deterministic structural emission.
Downstream systems remain responsible for local interpretation and routing.

## SQL Sketch

This is a planning artifact, not a migration order.
It exists to freeze the shape and invariants of the proposed bundle.

```sql
CREATE TABLE relational_bundle_version (
    version TEXT PRIMARY KEY,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO relational_bundle_version (version, description)
VALUES ('relational_bundle_v1', 'Deterministic dependency-derived relational structure emission');

CREATE TABLE relational_bundle (
    bundle_id TEXT PRIMARY KEY,
    version TEXT NOT NULL,
    source_doc_id TEXT NOT NULL,
    canonical_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (version) REFERENCES relational_bundle_version(version)
);

CREATE TABLE relational_atom (
    atom_id TEXT PRIMARY KEY,
    bundle_id TEXT NOT NULL,
    text TEXT NOT NULL,
    span_start INTEGER NOT NULL,
    span_end INTEGER NOT NULL,
    FOREIGN KEY (bundle_id) REFERENCES relational_bundle(bundle_id)
);

CREATE TABLE relational_edge (
    edge_id TEXT PRIMARY KEY,
    bundle_id TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN (
        'predicate',
        'modifier',
        'conjunction',
        'temporal',
        'composition'
    )),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bundle_id) REFERENCES relational_bundle(bundle_id)
);

CREATE TABLE relational_role (
    role_id TEXT PRIMARY KEY,
    edge_id TEXT NOT NULL,
    role_name TEXT NOT NULL,
    atom_id TEXT,
    literal_value TEXT,
    FOREIGN KEY (edge_id) REFERENCES relational_edge(edge_id),
    FOREIGN KEY (atom_id) REFERENCES relational_atom(atom_id)
);

CREATE TABLE relational_provenance (
    provenance_id TEXT PRIMARY KEY,
    edge_id TEXT NOT NULL,
    atom_id TEXT NOT NULL,
    span_start INTEGER NOT NULL,
    span_end INTEGER NOT NULL,
    FOREIGN KEY (edge_id) REFERENCES relational_edge(edge_id),
    FOREIGN KEY (atom_id) REFERENCES relational_atom(atom_id)
);
```

## Invariants

1. Every edge must belong to one bundle.
2. Every edge must expose at least one role.
3. Every role must reference either:
   - an atom, or
   - a literal value for composition-style non-lexical roles.
4. Every atom span must resolve into canonical text without silent mutation.
5. Relation `type` must remain structural, not ontological.
6. The bundle may add structure, but it may not mutate or reinterpret the
   canonical text itself.

## Golden Test Surface

The first lock for this contract is a golden fixture at:

- `service_telegram/test/fixtures/relational_bundle_v1_fx_public_hedging_volatility.json`

That fixture exists to pin the intended emitted boundary for the known failing
Telegram case:

- `fx_public_hedging_volatility`

The fixture is illustrative of the contract surface, not evidence that the
upstream reducer already emits it today.

## Example Structural Bundle

For:

`how does crypto promise to hedge asset volatility and uncertainty in 2026`

the expected structural bundle shape is:

- one `predicate` relation binding `hedge` to `volatility`
- one `modifier` relation binding `uncertainty` to `volatility`
- one `conjunction` relation preserving the linked item set
- one `temporal` relation for `2026`
- one `composition` relation with mode `question`

This stays within structural binding only.
It does not classify the text as a finance, market, or risk question.

## Promotion Gate

The contract is successful only if it enables downstream consumers to respond
to structural bindings without reintroducing local keyword heuristics.

For the Mirror Telegram support layer, the measurable downstream signal is:

- `fx_public_hedging_volatility` should no longer remain at
  `structural_gain=0` once the upstream bundle is actually emitted and
  consumed.

## Non-Goals

- no direct Telegram coupling in `SensibLaw`
- no domain ontology surface
- no routing contract changes here
- no claim that interpretive graph overlays belong in the shared reducer

The target is a structural bundle, not an interpretive overlay.
