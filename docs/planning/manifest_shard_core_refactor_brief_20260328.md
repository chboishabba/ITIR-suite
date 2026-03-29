# Manifest and Shard Core Refactor Brief

## Current surface

[`tools/build_zelph_hf_manifest.py`](/home/c/Documents/code/ITIR-suite/tools/build_zelph_hf_manifest.py)
and
[`tools/build_shared_shard_artifact_contract.py`](/home/c/Documents/code/ITIR-suite/tools/build_shared_shard_artifact_contract.py)
are the highest-value paired refactor because they already describe adjacent
parts of one artifact/shard contract.

Today they still split the responsibility awkwardly:

- one file is transport-branded around Zelph/HF manifest generation
- the other is closer to a neutral shared shard contract
- both still mix normalization, layout policy, digests, sink attachment, and
  CLI concerns

## Reusable core to preserve or extract

- logical shard identity
- section flattening / chunk normalization
- layout strategy abstraction
- digest computation and encoding inference
- transport-neutral contract assembly

That is the suite-level reusable core.

## Specialized remainder that should stay explicit

- Zelph source-manifest ingestion assumptions
- HF projection / shard emission details
- optional IPFS attachment behavior
- top-level CLI entrypoints

Those are adapters and projections, not the artifact contract itself.

## Proposed modules after split

- `tools/shared_shards/core.py`
  logical shard identity, normalization, flattening
- `tools/shared_shards/digests.py`
  digest and encoding helpers
- `tools/shared_shards/layouts.py`
  v1/future layout strategy objects
- `tools/shared_shards/contracts.py`
  transport-neutral contract builder
- `tools/shared_shards/adapters/zelph.py`
  Zelph manifest ingestion
- `tools/shared_shards/adapters/hf.py`
  HF projection/emission
- `tools/shared_shards/adapters/ipfs.py`
  IPFS ref attachment
- existing CLI files become thin wrappers over that core

## Acceptance checks

- current emitted shard IDs and manifest references remain stable for the same
  inputs
- HF-specific logic can be removed or swapped without rewriting the core
- the neutral contract no longer uses `hf` or `zelph` naming in its base API
- CLI tools become composition wrappers, not contract-definition files
