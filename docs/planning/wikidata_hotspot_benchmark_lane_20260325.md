# Wikidata Hotspot Benchmark Lane (2026-03-25)

## Purpose
Define a bounded benchmark/evaluation lane that turns the repo's existing
Wikidata structural diagnostics into reproducible LLM consistency tests.

This note exists because competitor work, including IBM's
_Reasoning about concepts with LLMs: Inconsistencies abound_
(`2405.20163v1`), is already using Wikidata-derived ontologies to generate
question clusters and claim "hotspot" detection. The repo already has a
stronger starting position in one critical respect: it can mine the structural
pathologies of Wikidata directly instead of first flattening them away.

## Paper takeaways relevant to this repo
From the IBM paper:

- they extract bounded ontologies from Wikidata
- they flatten `P31` and `P279` into one `subConceptOf` relation
- they generate yes/no question clusters over:
  - direct edges
  - inverse edges
  - hierarchy closure / transitivity
  - property inheritance
- they treat mixed answers inside a cluster as inconsistency
- they use simple KG-based prompting to improve results

That is useful, but it leaves a gap we can exploit:

- flattening `P31` and `P279` hides exactly the mixed-order and entity-kind
  failures our current diagnostics already surface
- hotspot claims become less legible if the benchmark no longer preserves why a
  region of the graph is pathological

## Repo-native advantage
The current Wikidata control-plane lane is already designed to surface
diagnostic structure rather than assume a clean ontology:

- mixed-order `P31` / `P279` use
- `P279` SCCs
- metaclass-heavy neighborhoods
- qualifier drift
- typed parthood ambiguity
- property/constraint interaction
- label harmonization as a secondary smell

So the benchmark lane should not be:

- "Can we ask the same yes/no questions IBM asked?"

It should be:

- "Can we generate benchmark clusters from bounded structural pathologies and
  retain the provenance that explains why the cluster is high-yield?"

## Generalization
This lane is not domain-specific.

The repo's Wikidata diagnostics are not just for finance/property semantics;
they are domain-agnostic structural review tools that detect entity-kind
collapse across domains, including:

- software artifacts vs projects vs communities
- products vs services vs categories
- class vs instance vs metaclass use
- structurally ambiguous property families

Examples already visible from recent review discussion:

- finance/product-service-category:
  - `financial product` (`Q15809678`)
  - `financial services` (`Q837171`)
  - `product` (`Q2424752`)
- software/project/artifact:
  - `GNU` (`Q44571`)
  - `GNU Project` (`Q7598`)

## Proposed hotspot families
Use hotspot families as the canonical benchmark-generation primitive.

### 1. Mixed-order hotspot
Signal:
- same node participates materially in both `P31` and `P279` use

Benchmark families:
- edge clusters
- inverse edge clusters
- hierarchy clusters

### 2. Entity-kind collapse hotspot
Signal:
- one item is carrying incompatible roles at once:
  artifact, project, category, service, product, community, class

Benchmark families:
- edge clusters
- inverse edge clusters
- kind-disambiguation clusters

### 3. SCC / circular subclass hotspot
Signal:
- reciprocal or cyclic `P279` structure

Benchmark families:
- edge clusters
- hierarchy/transitivity clusters
- contradiction-sensitive inverse clusters

### 4. Property/constraint hotspot
Signal:
- subject/value restrictions or neighboring property choices imply conflicting
  conceptualization

Benchmark families:
- property inheritance clusters
- constraint-sensitive scenario clusters

### 5. Qualifier-drift hotspot
Signal:
- same `(subject, property)` slot changes qualifier signature or qualifier
  property set across revisions

Benchmark families:
- temporalized statement clusters
- revision-pair agreement clusters

### 6. Typed parthood hotspot
Signal:
- parthood edges are structurally present but the endpoint typing leaves the
  semantic reading underdetermined

Benchmark families:
- edge clusters
- inverse-validity clusters
- type-sensitive inheritance clusters

## Benchmark contract
Each hotspot selected for the benchmark lane should preserve:

- source QIDs / PIDs
- hotspot family
- slice provenance
- why the hotspot was selected
- generated cluster family
- expected answer shape
- whether the cluster tests:
  - edge truth
  - inverse strictness
  - transitivity
  - property inheritance
  - temporal/qualifier stability
  - kind disambiguation

## What "beating IBM" should mean
Do not define success as "more swarms" or "more model calls."

Define it as:

1. better hotspot legibility
   - every benchmark cluster has a structural reason for existence
2. better provenance
   - every hotspot traces back to pinned Wikidata slices or revision pairs
3. better domain generality
   - the same machinery works across finance, software, medical, and other
     domains without inventing domain-specific logic each time
4. better determinism
   - repeated runs over the same slices generate the same hotspot packs
5. better explainability
   - we can say why a hotspot is dangerous:
     mixed-order, SCC, qualifier drift, entity-kind collapse, etc.

## Immediate bounded next step
Build a small fixture-backed pilot pack that includes:

- one mixed-order example
- one SCC example
- one qualifier-drift example
- one product/service/category entity-kind-collapse example
- one software/project/artifact entity-kind-collapse example

Only after that should the repo add:

- cluster generators
- model evaluators
- prompting experiments

Follow-on contract/spec artifacts for this lane:

- `docs/planning/wikidata_hotspot_pack_contract_20260325.md`
- `docs/planning/wikidata_hotspot_pilot_pack_v0.manifest.json`

## Non-goals
- no automatic Wikidata repair
- no claim that the benchmark lane defines ontology truth
- no broad benchmark-generation implementation before fixture-backed hotspot
  selection is stable
