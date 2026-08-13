# `itir_jmd_bridge/runtime.py` Refactor Brief

## Current surface

[`itir_jmd_bridge/runtime.py`](/home/c/Documents/code/ITIR-suite/itir_jmd_bridge/runtime.py)
currently mixes:

- runtime object construction
- graph derivation
- receipt derivation
- browse-list ingestion and concurrency
- provider/default getter behavior

The clearest seams are:

- object assembly at `itir_jmd_bridge/runtime.py:168`
- graph projection at `itir_jmd_bridge/runtime.py:247`
- receipt generation at `itir_jmd_bridge/runtime.py:329`
- ingest loop at `itir_jmd_bridge/runtime.py:451`
- prototype ingest path at `itir_jmd_bridge/runtime.py:560`

## Reusable core to preserve or extract

- runtime-object contract assembly
- graph projection over a runtime bundle
- receipt metadata / dependency surface summaries
- generic list-ingest loop with bounded concurrency

These are runtime-assembly concerns and should not stay coupled to one
provider-history path.

## Specialized remainder that should stay explicit

- provider-specific browse/fetch behavior
- default-getter policy
- prototype-only MDL or exploratory projection paths

Those belong in provider adapters or explicit prototype surfaces.

## Proposed modules after split

- `itir_jmd_bridge/runtime_object.py`
  content-ref handling, IPFS verification, runtime object builder
- `itir_jmd_bridge/runtime_graph.py`
  graph derivation
- `itir_jmd_bridge/runtime_receipt.py`
  receipt and dependency metadata builders
- `itir_jmd_bridge/runtime_ingest.py`
  generic list-ingest loop and adaptive settings
- `itir_jmd_bridge/runtime.py`
  thin compatibility facade and orchestration entrypoint

## Acceptance checks

- current runtime bundle payloads remain stable for fixed provider fixtures
- list-ingest paths share one generic ingest loop instead of duplicating browse
  / capability / throttle logic
- provider-specific logic stays outside the runtime core
- `runtime.py` becomes a composition facade, not the whole subsystem
