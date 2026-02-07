# Canonical Serialization and Hashing (Draft)

## Purpose
Ensure selector and norm-constraint evaluation is replay-safe and diffable.

## Canonicalization Rules
1. UTF-8 encoding only.
2. Serialize as canonical JSON (no comments, sorted object keys).
3. Remove insignificant whitespace.
4. Preserve array order exactly as authored.
5. Normalize line endings to LF before hashing.

## Hash Inputs
- Selector hash input: canonical JSON representation of `selector` object.
- Norm hash input: canonical JSON representation of full `norm_constraint`.

## Hash Function
- Default: `sha256`.
- Output encoding: lowercase hex.

## Example
Input object (canonical JSON bytes) -> `sha256` -> `selector_hash`.

## Drift Behavior
- Any change in selector structure/values yields new hash.
- Constraint history should record `prev_hash` and `new_hash` when edited.
