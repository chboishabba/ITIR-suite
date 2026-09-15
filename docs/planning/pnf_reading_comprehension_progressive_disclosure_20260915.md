# PNF Reading Comprehension + Progressive Disclosure Addendum

Date: 2026-09-15

## Status

This is a focused addendum to:

- `docs/planning/progressive_proof_explanation_workbench_20260915.md`
- `docs/planning/mabo_reading_workbench_v0_20260915.md`
- `docs/user_stories.md`
- `docs/planning/recent_workbench_page_user_stories_20260310.md`

It does not create another product roadmap.

The purpose is to make explicit a reusable interaction primitive that the existing user stories already imply:

```text
literal text
-> optional role / meaning overlay
-> exact source
-> bounded reasoning / proof cone
-> wider context / follow trail
```

The primitive must work for legal reading, ordinary reading, transcript review, Wiki/Wikidata review, and later education-oriented surfaces without creating a second semantic truth model in the UI.

## Product thesis

PNF is not merely parser output for internal inspection. Used conservatively, it can become a reading-comprehension overlay over text the user is already reading.

Example:

```text
They wove a panel of golden spider silk.
```

A user may optionally inspect:

```text
They               -> actor / subject -> antecedent candidate -> source span
wove               -> predicate
panel               -> patient / object
golden spider silk  -> material / modifier
```

The literal sentence remains the orientation surface. The role overlay explains structure; it does not replace the sentence.

The same interaction grammar applies to a Mabo proposition:

```text
plain-language proposition
-> select expression
-> role / meaning
-> exact judgment span
-> authority / applicability
-> bounded support / defeater / comparator cone
-> optional related concept / source follow
-> return
```

## Formal boundary

DASHI owns the formal companion:

```text
DASHI/Interop/ReadingTrailPNFProgressiveDisclosureExact.agda
```

The intended laws are:

```text
Q_layReading may factor through a shallow readable projection.
Q_primaryAuthorityAudit need not factor through that same projection.

hidden from shallow view != deleted
role overlay != source replacement
role overlay != proposition truth
role overlay != legal authority
interaction receipt != comprehension
interaction receipt != belief
context link != evidence payment
```

The retained state must remain reopenable through source/provenance receipts.

## Shared interaction grammar

The existing user-story corpus repeatedly asks for the same seven capabilities. Treat these as shared Reading/Review primitives rather than route-local features:

1. **Orient** — identify the current object, source/frame, epistemic status and relevant time/context.
2. **Project** — show the smallest consumer-relevant view first; deeper state remains available.
3. **Explain / Why?** — expose bounded support, applicability, defeater, comparator and residual structure.
4. **Source** — reopen exact source span, surrounding context, version/revision and provenance.
5. **Meaning** — expose PNF/lexical/concept structure progressively.
6. **Follow** — move to a related authority, concept, cited source, Wiki/Wikidata identity or related event while preserving the return trail.
7. **Next unresolved** — show what remains unpaid/uncertain and one bounded action that could reduce that uncertainty.

These primitives should be reusable across:

- Mabo legal explanation;
- thread-grounded argument review;
- Wiki revision / source-follow review;
- CLC / lived-history intake;
- competing narrative comparison;
- ordinary reading-comprehension surfaces.

## Information-density law

The user stories already require that dense information compress via grouping and progressive disclosure rather than tiny unreadable chips.

Therefore:

```text
available graph != initially rendered graph
available PNF != always-highlighted text
available provenance != always-visible hashes/QIDs
available residuals != default residual table
```

Initial text should look readable without overlays enabled.

A compact action vocabulary is preferred:

```text
Why? | Source | Meaning | Follow
```

A quieter secondary control may expose:

```text
What still needs checking?
```

## PNF presentation contract

### Default

- literal text is primary;
- no full tuple dump;
- no parser confidence wall;
- no compulsory grammar terminology;
- high-value roles are quiet until requested.

### First disclosure

When a user activates `Meaning` on a phrase/token:

- lightly highlight its literal span;
- show one human-readable role;
- show the phrase it connects to when useful;
- explain the role using the current sentence, not an abstract grammar lecture.

Example:

```text
wove
Role: predicate
Meaning here: the action performed by “they”.
```

### Second disclosure

Offer optional technical language:

```text
predicate / verb phrase
actor / grammatical subject
patient / object
negation
modality
condition
antecedent candidate
```

The technical label is an educational refinement, not the primary explanation.

### Legal operator emphasis

For legal/proof reading, the most useful optional highlights are often not ordinary noun/verb categories but operators such as:

- negation;
- modality (`must`, `may`, `can`, `cannot`);
- conditions (`if`, `unless`, `subject to`);
- exceptions / qualifiers;
- attribution wrappers (`held`, `said`, `submitted`, `alleged`);
- actor/patient role changes.

These should be skimmability aids, not evidentiary weights.

## Source / Wiki / Wikidata follow contract

The rabbit-hole experience should feel closer to Encarta/Wikipedia than to a dashboard, while preserving source discipline.

Typed chain:

```text
canonical object
<-> Wikidata identity
<-> revision-locked Wikipedia/context page
-> cited references / outbound candidates
-> explicitly selected followed source
-> source receipt / unresolved follow
```

Firewalls:

```text
QID identity != legal applicability
Wikipedia wording != legal authority
outbound link != evidence
followed source != automatically paid proposition
```

A user should be able to click a related concept or source and make it the new primary review object without losing their prior location.

## Reading Trail contract

The trail is a navigation aid, not a learner model.

Recordable actions may include:

```text
activate
meaning
open_source
follow
expand_reasoning
back
```

Default v0 persistence is in-memory/session-local.

Optional future StatiBaker persistence remains opt-in and may record only temporal interaction facts such as:

```text
opened object A
followed concept B
opened source C
returned to A
```

It must not infer:

```text
user understands A
user believes B
user prefers C
user mastered concept D
```

## Mabo flagship acceptance additions

In addition to the existing Mabo v0 criteria:

1. Initial load is readable with PNF overlays disabled.
2. Activating `Meaning` on one phrase reveals one bounded role explanation first.
3. The user can optionally reveal technical PNF terminology without changing proof state.
4. Negation/modality/condition operators may be highlighted as a separate skimming aid.
5. A `Follow` action can move to one related concept/source and `Back` restores the previous selected locus.
6. Wiki/Wikidata context remains visually distinct from legal authority/source receipts.
7. Source reopening remains one action away from every explanation-bearing legal assertion.
8. No interaction receipt is rendered as evidence of comprehension, belief or legal truth.

## Reuse pressure from lived-history / CLC

The same primitive should survive a non-legal-authority-first fixture.

For an anonymised lived-history object:

```text
event/recollection text
-> actor / predicate / temporal / attribution structure
-> exact source artefact
-> evidence role
-> professional relevance
-> residual / missing fact
-> bounded follow / side memory
-> return
```

If the Reading/Review primitive only works for Mabo, it is too legal-domain-specific.

## Educational product boundary

A reading-comprehension product is a plausible later consumer of this primitive, but v0 does not claim educational efficacy.

Allowed v0 claim:

```text
The system can expose source-grounded semantic/PNF structure progressively while preserving literal text and provenance.
```

Not yet allowed:

```text
The system improves comprehension.
The system teaches grammar better than conventional instruction.
The user has learned a concept because they clicked or followed it.
```

Those require direct user evidence and separate evaluation.

## Immediate implementation order

1. Implement `Meaning` against producer-owned PNF spans in the Mabo read model.
2. Keep literal text readable with overlays off.
3. Add source reopening from the same selected semantic object.
4. Add one bounded `Follow` path through concept/Wiki/Wikidata/source context.
5. Preserve return locus through the Reading Trail.
6. Add `What still needs checking?` from existing residual/operator-view state.
7. Reuse the same interaction primitives against the anonymised lived-history/CLC fixture.
8. Only then generalise the richer hyperformal ribbon visualisation.

## Validation posture

Use three evidence classes separately:

```text
repo user story / acceptance criterion = demand proxy
implemented interaction + test = implementation receipt
observed real-user feedback = direct product evidence
```

Do not promote a story proxy into evidence that users actually found the interaction useful.
