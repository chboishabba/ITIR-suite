# Lens DSL (rho(t) JSON-AST)

This defines a safe JSON-AST for lens definitions. It is deterministic and
inspectable; no arbitrary code execution is allowed.

## Core structure

A lens is a JSON object:

```json
{
  "lens_id": "time",
  "units": "seconds",
  "rho": {"op": "const", "value": 1}
}
```

## Supported ops

- `signal(name)`
- `const(value)`
- `add/sub/mul/div`
- `clamp(min,max,x)`
- `smooth(window,x)` (moving average)
- `abs`, `log1p`, `sqrt`
- `threshold(x,k)` (0/1 indicator)
- `blend([{w, expr}, ...])` (convex)
- `mask(expr, predicate)` (opacity/scoped visibility)

## Execution model

- Signals are aligned time-indexed arrays.
- Evaluate AST pointwise to obtain rho(t).
- Clamp negative values to 0 (or require a clamp op).
- Compute mass by summing/integrating rho(t).
- Normalize widths by total mass.

## Determinism

- Lens hash is computed from canonical JSON (sorted keys, no whitespace).
- Evaluation is pure and side-effect free.

## Example (blend)

```json
{
  "lens_id": "procedural_plus_evidence",
  "units": "points",
  "rho": {
    "op": "blend",
    "terms": [
      {"w": 0.6, "expr": {"op": "signal", "name": "procedural_stage_weight"}},
      {"w": 0.4, "expr": {"op": "signal", "name": "citation_rate"}}
    ]
  }
}
```
