# Federated world materialisation boundary across Casey / StatiBaker / SensibLaw

Date: 2026-09-15

## Purpose

Record how the new skeletal-corpus / retention / replication roadmap fits the already-frozen ITIR-suite ownership boundaries.

This is an interface note, not a new runtime.

## Existing ownership remains unchanged

```text
SensibLaw / SL
  -> semantic construction, admissibility, promotion, consumer residuals

casey-git-clone
  -> live candidate/workspace/collapse/build state

StatiBaker
  -> append-only observer memory, operation/build receipts and references

ZOS
  -> non-authoritative semantic/object overlay

fuzzymodo
  -> advisory selection/ranking over exported state
```

Federation, IPFS, content addressing, compression, or replication do not transfer authority among these systems.

## New materialisation distinction

For any semantic/content object distinguish:

```text
semantic identity
materialised bytes
local availability
replica availability
candidate/workspace membership
observer receipt/history
semantic authority/payment
```

None should be inferred solely from another.

Examples:

```text
CID available
!= Casey candidate selected

Casey build references CID
!= StatiBaker owns blob bytes

StatiBaker records retrieval receipt
!= SensibLaw proposition paid

many mirrors
!= truth
```

## Casey placement

Casey may refer to content-addressed objects from mutable candidate sets and immutable builds.

A future Casey candidate can therefore be represented conceptually as:

```text
path
+ candidate/version identity
+ content digest
+ zero-or-more locators
+ optional local materialisation state
```

without requiring that every candidate's full bytes remain permanently local.

However:

- Casey retains workspace/collapse/build authority;
- external storage providers do not collapse a Casey candidate set;
- missing local bytes do not imply a candidate ceased to exist;
- a build that requires unavailable bytes becomes non-realisable/retrieval-blocked rather than silently rewritten.

## StatiBaker placement

The current Casey -> StatiBaker observer-only contract remains the correct model.

SB should record bounded references such as:

```text
operation id
workspace/tree/build id
content digest/CID when relevant
locator/reference identity
retrieval/materialisation transition receipt
selection digest
receipt hash
```

SB must not become a mirror of Casey mutable candidate graphs or a general blob store merely because federation exists.

A retention transition can be observable without transferring storage authority:

```text
HotLocal -> ReferenceOnly
```

may create an append-only receipt containing the object identity/digest and policy decision while bytes move or are purged elsewhere.

## Replication

Replication can occur independently of Casey/SB ownership:

```text
peer A -> IPFS/public mirror
peer B -> parser/compute
peer C -> routing/discovery
peer D -> ontology/authority cache
```

Casey can use content identities/locators where admitted.
SB can observe relevant operations.
SensibLaw decides whether the resulting source/evidence can pay a consumer residual.

## Compression and deduplication

Do not conflate:

```text
byte compression
deduplication
semantic projection
cold storage
reference-only representation
```

Casey identity/replay requirements may constrain byte-level storage differently from SensibLaw skeletal-corpus requirements.

For example, a SensibLaw navigation consumer may need only a segment graph and authoritative locator, while a Casey immutable build may require exact byte recovery.

## Practical profiles

### Personal notes / Obsidian

Canonical source bodies may remain in the vault.
SensibLaw may retain graph/refs.
Casey is optional unless the user wants explicit superposition/version/collapse workflows.
StatiBaker may retain operation/history receipts.
Encrypted backup or IPFS-style replication is policy-selected, not mandatory.

### Legal / CLC

Matter bytes may remain restricted/local.
Public authority material can be skeletal + retrievable or institutionally mirrored.
Casey can preserve competing draft/formulation candidates where needed.
StatiBaker records the operational provenance of those selections without deciding legal truth.

### Clinical

Patient material defaults to protected local/institutional storage.
Public ontology/guideline content may be remote.
Casey/SB federation must obey disclosure policy before capability routing.

## High-alpha cross-suite work

Complete next when touching this seam:

1. stable content/object identity usable across Casey build refs, SensibLaw skeletal objects, and SB receipts;
2. append-only materialisation/retention receipt family;
3. retrieval-blocked / availability residual rather than implicit deletion;
4. capability-discovery and admitted job transport reused from the existing distributed surfaces;
5. query-indexed proof that reference-only/skeletal representation is adequate for some consumers but not exact-byte/build consumers.

Defer broad compression codecs, universal IPFS mirroring, and ZKP/on-chain storage until workload/privacy receipts demonstrate a concrete need.

## Boundary law

```text
world representability != local materialisation
local materialisation != durable retention
durable retention != replication
replication != semantic authority
observer history != operational authority
```

The intended architecture is therefore federated and content-addressable without becoming a distributed authority conflation.