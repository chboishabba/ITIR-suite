# Time-Series Transformations (ITIR / SL Alignment)

Status: draft (2026-03-04).

## Purpose
Define a shared transformation model where time-indexed observations can be
derived from other observations via explicit, auditable functions.

This aligns:
- **ITIR**: everything is a time-indexed observation.
- **SensibLaw**: facts → rules → derived conclusions.
- **StatiBaker**: events → derived views and summaries.

## Core Model

### TimeSeries
- `series_id`
- `entity_id`
- `metric`
- `unit`
- `provenance` (source + version)

### Observation
- `series_id`
- `timestamp`
- `value`
- `provenance` (source + extraction version)

### Transformation
- `transform_id`
- `input_series_ids[]`
- `function` (e.g., `diff`, `sum`, `convert`)
- `parameters` (e.g., currency, scale, window)
- `output_series_id`
- `provenance` (rule ID + version)

## Niklas Example Mapping (Cumulative → Monthly, Currency Conversion)
Example:
- `Series A`: cumulative donations (foreign)
- `Series B`: monthly donations
- `Series C`: monthly donations in USD

Transformations:
1. `B(t) = A(t) - A(t-1)`  
   `function=diff`, `input=[A]`, `output=B`
2. `C(t) = B(t) * exchange_rate(t)`  
   `function=convert`, `input=[B, exchange_rate]`, `output=C`

This is the same functional pattern used by SL for:
facts → rules → derived conclusions.

## Invariants
1. Derived series must be reproducible from inputs + function + parameters.
2. Every derived value must be traceable to its input observations.
3. Transformations are explicit objects; no hidden math in UI layers.
4. Transformations do not mutate inputs; they emit new derived series.
5. Temporal alignment rules are deterministic (no silent interpolation).

## Tests (Required)
1. **Determinism**: same inputs + same transform => identical outputs.
2. **Traceability**: each derived value links to input observation IDs.
3. **No mutation**: input series unchanged after transformation.
4. **Temporal alignment**: windowing/joins produce deterministic output length.
5. **Unit correctness**: derived units are computed or declared explicitly.

## SL Mapping (Fact → Rule → Conclusion)
SL’s derivation pipeline is structurally equivalent:
- `Observation` → `Rule` → `Derived Observation`

Example:
- Fact: "X punched Y" at `t`
- Rule: battery conditions
- Derived: `wrong=battery` at `t`

This is the same functional pattern as time-series algebra.

## ITIR / SB Mapping (Observation → Derived View)
SB summaries and ITIR overlays should treat derived views as:
- explicitly computed transformations
- never authoritative over raw observations

## Non-goals
- Implementing the computation engine in this document.
- Defining domain-specific functions beyond the minimal set.

## Alignment With Existing SL Finance Docs
This model sits on top of existing finance substrates:
- `SensibLaw/docs/FINANCE_SCHEMA.md` (accounts/transactions/transfers)
- `SensibLaw/docs/numeric_representation_contract_20260213.md` (currency normalization)
- `SensibLaw/docs/ITIR.md` (finance connector lessons)

It does not replace those; it declares **how derived series are defined and
audited** once canonical finance observations exist.
