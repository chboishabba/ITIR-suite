# Zelph/Wikidata HF artifact locator and ITIR MCP acceptance (2026-11-14)

This is the definitive **source-qualified locator guide** for the existing ITIR MCP/Wikidata and Zelph contracts. It updates the historical July transport audit; it is not a fresh byte-level probe of Hugging Face.

## 1. Is Wikidata implemented in ITIR MCP?

**Yes.** The actual tool registry registers `get_governance_tools` and `get_wikidata_disjointness_tools`:

- [governance_tools.py](https://github.com/chboishabba/ITIR-suite/blob/main/itir-mcp/src/itir_mcp/governance_tools.py) registers `itir.wikidata.review_packet`, `itir.wikidata.object_review_bundle`, `itir.wikidata.migration_candidate`, `itir.wikidata.tooling_profile`; `itir.zelph.hf_manifest_contract`, `itir.zelph.pack_sources`, `itir.zelph.transport_boundary`, `itir.zelph.partial_closure`; and `itir.shard.validate_artifact`, `itir.shard.route_selector`, `itir.shard.partial_graph_view`, `itir.shard.bounded_graph_slice_plan`, `itir.shard.payload_probe`.
- [wikidata_disjointness_tool.py](https://github.com/chboishabba/ITIR-suite/blob/main/itir-mcp/src/itir_mcp/wikidata_disjointness_tool.py) registers `itir.wikidata.disjointness_report`.
- [registry.py](https://github.com/chboishabba/ITIR-suite/blob/main/itir-mcp/src/itir_mcp/registry.py) installs those registrations in the MCP tool registry.
- [domain_tools.py](https://github.com/chboishabba/ITIR-suite/blob/main/itir-mcp/src/itir_mcp/domain_tools.py) supplies review/migration and partial-closure logic.
- [shard_transport.py](https://github.com/chboishabba/ITIR-suite/blob/main/itir-mcp/src/itir_mcp/shard_transport.py) implements manifest normalization, selector routing and bounded *planning*; `build_bounded_graph_slice_view` explicitly does **not** fetch shard payloads.
- [MCP tests](https://github.com/chboishabba/ITIR-suite/tree/main/itir-mcp/tests) include test_domain_tools, test_registry, test_wikidata_object_review, test_shard_transport and test_shard_transport_handoff. Existing tests are source evidence; this audit did not run them afresh.

Therefore: **the MCP ABI exists**, but that does not by itself establish real HF shard decode, full graph query completeness, or SLR persisted replay.

## 2. Canonical published HF dataset, not guessed paths

**Upstream authoritative source:** [Stefan Zipproth / acrion Zelph — Sharding and Partial Loading](https://zelph.org/sharding/), [published binary catalog](https://zelph.org/binaries/), [Hugging Face dataset](https://huggingface.co/datasets/acrion/zelph).

The upstream documentation specifies:

| Artifact | Manifest (repo-relative) | Intended scope |
|---|---|---|
| Full 2026-03-09 Wikidata | `wikidata-20260309-all/wikidata-20260309-all.hf-v2.json` | 983M-node entity-linked graph |
| Pruned-small 2026-03-09 Wikidata | `wikidata-20260309-all-pruned-small/wikidata-20260309-all-pruned-small.hf-v2.json` | reduced graph; no general whole-Wikidata absence inference |

The canonical manifest URL prefix is `hf://datasets/acrion/zelph/`. Upstream gives the following exact load commands:

```text
.load-partial hf://datasets/acrion/zelph/wikidata-20260309-all/wikidata-20260309-all.hf-v2.json left=0
.load-partial hf://datasets/acrion/zelph/wikidata-20260309-all-pruned-small/wikidata-20260309-all-pruned-small.hf-v2.json meta-only
```

The published layout is `<artifact>/<artifact>.hf-v2.json`, `<artifact>/artifact.index.json`, and `<artifact>/shards/{left,right,nameOfNode,nodeOfName}/...`. Upstream's exact example objectPath is `hf://datasets/acrion/zelph/wikidata-20260309-all/shards/left/chunk-000000.capnp-packed`. This is a *documented example*, not independent confirmation of current payload SHA or HTTP 200.

**Source correction:** the [ITIR July 4 readiness document](https://github.com/chboishabba/ITIR-suite/blob/main/docs/planning/zelph_develop_sparql_partial_load_readiness_20260702.md) observed publicly readable shards but could not find canonical manifest/route/index at that checkpoint. The current upstream documentation specifies published manifests and indexes. Treat the July observation as **historical**, not as present-day nonexistence. Do not claim a *specific current revision or checksum* until live metadata readback establishes it.

**The earlier `chbwa/zelph-sharded` repo is a proof-of-concept**, not the production artifact to route by. Upstream says its original manifest source-bin paths were local to the builder's machine.

## 3. How to resolve an exact QID without guessing

There are two distinct namespaces:

1. **External stable identifier:** Wikidata `Q...` or `P...` string.
2. **Zelph internal node ID/chunk index:** created by a particular `.bin`; may change when the graph is regenerated.

For a pinned manifest that explicitly advertises `nodeRouteIndex`, follow upstream's route selectors:

```text
.load-partial <pinned-manifest> route-name=Q207 route-lang=wikidata
```

This resolves the exact *name* into `nodeOfName` chunks. It does **not** load node adjacency or guarantee the node's own `nameOfNode` representation. To inspect its adjacency, first obtain the actual internal node ID from the loaded graph, then use `route-node=<internal-id>` on the **same manifest/artifact**. Do **not** pass an external `Q207` string as `route-node` or infer that `nameOfNode=0` and `nodeOfName=0` contain the same set.

The route sidecar may be **incomplete by design**. Its absence or a miss is not evidence that the QID does not exist. The upstream documentation explicitly says route selectors require `nodeRouteIndex` advertised by the manifest. ITIR's own [filtered Nat route PR #14](https://github.com/chboishabba/ITIR-suite/pull/14) is an exact, read-only five-QID special case; it is not whole-graph routing.

Upstream also states that the name-section `chunkIndex` is **section-global across languages**. For the published pruned-small artifact, Wikidata name chunks are indices 0–7 and English chunks 8–12 (per current upstream documentation). Chunk numbers are **artifact-local** and must be revalidated after regeneration.

## 2026-11-14 implementation continuation — exact route MCP and reproducible HF probe

**Golden / production / reference:** [DASHI Agda](https://github.com/chboishabba/dashi_agda) is the formal gold source, [SLR](https://github.com/chboishabba/slr/blob/main/docs/ROADMAP.md) is the Rust/PostgreSQL production owner, this ITIR MCP is the tool catalogue/integration layer, and [SensibLaw](https://github.com/chboishabba/SensibLaw) is historical Python reference. The [updated ITIR Wiki stories](https://github.com/chboishabba/ITIR-suite/blob/agent/nat-filtered-route-producer/docs/user_stories.md) now explicitly list existing tool ABIs and the exact-shard user story WIKI-US-05.

**New read-only MCP endpoint on [ITIR PR #14](https://github.com/chboishabba/ITIR-suite/pull/14):** `itir.shard.exact_wikidata_name_route` calls [`exact_wikidata_name_route`](https://github.com/chboishabba/ITIR-suite/blob/agent/nat-filtered-route-producer/itir-mcp/src/itir_mcp/shard_transport.py). It uses a **caller-supplied pinned** `route_index`, requires a canonical `Q...`, exact `nodeOfName`/Wikidata language and unambiguous section-global indexed shard. This prevents the generic family's `routingKeys` fallback from masquerading as exact QID routing. Its output is an artifact-revision-bound **plan**; `payload_fetch=false`, `payload_decode=false`, `query_coverage_complete=false`.

**Reproducible metadata-only probe:** [`tools/probe_zelph_hf_nat_routes.py`](https://github.com/chboishabba/ITIR-suite/blob/agent/nat-filtered-route-producer/tools/probe_zelph_hf_nat_routes.py) performs:

1. GET `https://huggingface.co/api/datasets/acrion/zelph` with a bounded metadata cap and parse its immutable `sha`.
2. GET the exact upstream-documented full (or `--artifact pruned-small`) HF manifest at `/resolve/<sha>/...`, hash the actual manifest response.
3. Only fetch the **manifest-declared** `hfObjects.nodeRouteIndex.path`, pinned to the *same* SHA, then hash it. **Do not invent a sidecar filename.** If not advertised, return an explicit blocked result.
4. Resolve five exact Nat QIDs: `Q10403939`, `Q10416948`, `Q10422059`, `Q10651551`, `Q56404383`. Emit per-QID exact-route or unresolved and the identity digests, with no payload download or authority claim.
5. Fail closed if DNS/HTTP is unavailable, metadata exceeds bounds, a sidecar is absent, or a specific QID has no unique exact witness.

Commands from an ITIR checkout:

```sh
python tools/probe_zelph_hf_nat_routes.py
python tools/probe_zelph_hf_nat_routes.py --artifact pruned-small
python -m pytest -q itir-mcp/tests/test_exact_wikidata_name_route.py tests/test_probe_zelph_hf_nat_routes.py
```

**Network status of this audit:** direct live HF dataset API and manifest reads were attempted on 2026-11-14. Browser retrieval could not access them, and the available container failed DNS resolution of `huggingface.co`. We therefore have **no actual dataset SHA, manifest byte digest, sidecar byte digest or live QID result** from this environment. The command is executable but its remote outcome is unverified; new test files have been committed but not executed in a native ITIR checkout here. The [upstream Zelph published docs](https://zelph.org/sharding/) do specify the canonical paths and revised cache/transfer behaviour, but are not substitute transport receipts.

**Next separate gates:** no-fallback pinned physical shard GET, Cap'n Proto decode against the blessed Zelph binary, measured physical GET/bytes, query-family completeness and SLR source/S29 persisted review. All remain open until runtime receipts are collected.

## 4. What remains unverified, and the exact next probe

The current GPT connector can read GitHub source but has **not** fetched the live HF metadata/binary blob and therefore does not certify the current manifest, route file, individual shard digests, CDN responses or live QID resolution.

The minimum direct-receipt operation is:

1. Query `https://huggingface.co/api/datasets/acrion/zelph` and record immutable dataset `sha`; identify the published revision.
2. Download the documented manifest **at that SHA**, not `main`, and verify `manifestVersion`, `transport.primary`, `sections.*.chunks`, `hfObjects.nodeRouteIndex` and its advertised capability.
3. Fetch the **route sidecar named inside that exact manifest**; never fabricate its filename. Bind route-sidecar bytes and manifest bytes to SHA-256 receipts.
4. For the five pinned Nat QIDs, resolve exact names against that sidecar; record any routing misses as **route-unresolved** rather than native-family absence. If necessary, use a separately revision-pinned Wikidata source confirmation.
5. On that *same artifact*, fetch one declared name shard and one declared adjacency shard; validate content digest, decode and selector/manifest equality with no sequential fallback. Store physical GET count, bytes, latency and cache status.
6. Ensure `itir.zelph.hf_manifest_contract` normalized bytes map to `shared-shard-artifact/v1` without source/artifact identity drift, and prove the graph read stays `candidate_only`, `coverage_incomplete` absent a relevant completeness witness.
7. Do not promote NORA/Zelph production routing until source/revision and coverage receipts are persisted/replayed by native SLR and the existing S29/ITIR review tools.

## 5. Specific compatibility risk worth testing

ITIR's generic `shard_transport.route_selector` first consults the supplied sidecar, but if that returns no match it can fall back to `routingKeys` and even a **family-only** match (for example `route-name`). That fallback can yield a coarse selection and is not evidence that an *exact name/QID* was routed. For an audit path, require an **exact matched selector with route witness**, distinguish explicit coarse fallback, and fail closed when an exact route has no evidence. The existing generic caller may intentionally support coarse grouping; it should not be silently used as a proof of exact Nat routing.

## 6. Relation to NORA

The [NORA handoff PR #514](https://github.com/chboishabba/SensibLaw/pull/514) should consume this existing MCP ABI and SLR's native source route. A `manual_search` choice creates a bounded candidate acquisition request, **not** a completed shard fetch, an admissible `P854` source proposition or a Wikidata edit.

**Next max-cut:** current HF revision → exact manifest/sidecar readback → five Nat QID route receipts → direct shard decode + bounded costs → SLR persisted review. Nothing in the old July audit proves current unavailability.
