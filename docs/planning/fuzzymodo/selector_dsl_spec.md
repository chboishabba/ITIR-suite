# Selector DSL Specification (Draft v0.1)

## 1. Design Goals
- Declarative only.
- Deterministic and hash-stable.
- Graph-scoped clauses only.
- Intersective by default (`all_of`).
- Non-inventive: selectors bind to observed facts only.

## 2. Top-Level Shape
```yaml
selector:
  all_of:
    - graph: structural
      where:
        function.name: parse_text
```

Optional keys:
- `any_of`
- `not`

At least one of `all_of`, `any_of`, `not` must be present.

## 3. Clause Shape
Each clause must include:
- `graph`: one of `structural`, `execution`, `build`, `threat`,
  `ecosystem`, `normative`, `timeline`
- `where`: map of field predicates

## 4. Predicate Operators
Allowed predicate forms:
- scalar equality:
  - `field: value`
- operator map:
  - `eq`, `neq`, `lt`, `lte`, `gt`, `gte`, `in`, `startswith`, `matches`, `exists`

No implicit operator merging across different fields.

## 5. Graph Layer Field Catalog (Initial)
- `structural`: `function.name`, `function.visibility`, `module.path`,
  `node.type`, `edge.kind`, `introduced_in.commit`
- `execution`: `execution.entrypoint`, `execution.network_exposed`,
  `path.executed`, `input.origin`, `crash.cluster`
- `build`: `feature.enabled`, `flag.name`, `platform.os`, `platform.arch`,
  `release.channel`
- `threat`: `attacker.auth`, `attacker.position`, `primitive`, `cwe.id`,
  `exploited.in_wild`
- `ecosystem`: `api.surface`, `dependent.external`, `dependent.count`,
  `relies_on.quirk`
- `normative`: `decision.kind`, `decision.owner`, `decision.confidence`,
  `decision.expires_at`
- `timeline`: `introduced_in.commit`, `valid_until.commit`, `after.incident`,
  `before.release`

## 6. Composition and Evaluation
Evaluation order:
1. Evaluate all `all_of` clauses: all must pass.
2. Evaluate `any_of` clauses (if present): at least one must pass.
3. Evaluate `not` clause (if present): must fail.
4. Result is boolean selector match.

## 7. Rejection Rules
Reject selector payload if:
- clause omits `graph` or `where`
- unknown operator appears
- regex in `matches` is invalid
- no composition keys are provided

## 8. Versioning
Each selector payload must include:
- `dsl_version` (example: `0.1`)

Breaking changes must increment major version.
