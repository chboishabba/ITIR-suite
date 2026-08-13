# Casey Git Clone MVP Backlog

## P0
- Implement dataclass models for core objects.
- Implement deterministic JSON canonicalization + hashing helpers.
- Implement candidate-set validation utilities.

## P1
- Implement publish/sync/collapse/build-view operation functions.
- Add fixtures for divergent same-path edits.
- Add tests for selection validity and collapse behavior.

## P2
- Add optional `ChangeGroup` model for cross-file coherence.
- Add serializer compatibility adapters for future Git-backed persistence.
