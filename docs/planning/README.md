# Planning Docs

This folder contains ADRs, UI component specs, doctrine notes, and validation
artifacts for the context invariant.

## Validation (Stub)

The context envelope validation stub lives at:
- `docs/planning/context_envelope_validate_stub.py`

To wire validation:
1. Choose a JSON Schema validator (draft 2020-12 compatible).
2. Implement the TODOs in the stub.
3. Add the script to CI or a pre-commit hook.
