Yes. We should stop treating performance as an open-ended sequence of bottlenecks and instead declare the **target execution architecture** first. Then each tranche has one job: remove whatever remains inconsistent with that architecture.

The core principle is:

$$
\boxed{
\textbf{PostgreSQL is the durable authority boundary, not the internal execution bus.}
}
$$

Everything follows from that.

## 1. The target end-to-end flow

The production compiler should converge on:

$$
\boxed{
\begin{aligned}
\text{immutable source}
&\rightarrow
\text{bounded parser fibre}
\\
&\rightarrow
\text{packed structural fibre}
\\
&\rightarrow
\text{local semantic solve}
\\
&\rightarrow
\text{typed semantic delta + residuals}
\\
&\rightarrow
\text{delta transport through hierarchy}
\\
&\rightarrow
\text{document fixed point}
\\
&\rightarrow
\text{atomic authority publication}.
\end{aligned}
}
$$

The essential distinction is that the first several objects are **execution objects**. PostgreSQL should not be required between them.

A stronger formulation is:

$$
\boxed{
S
\xrightarrow{P}
F
\xrightarrow{L}
\Delta_0
\xrightarrow{T}
\Delta_1
\xrightarrow{T}
\cdots
\xrightarrow{R}
A
}
$$

where:

* \(S\): immutable source;
* \(P\): parser projection;
* \(F\): bounded packed structural fibre;
* \(L\): local PNF reduction;
* \(\Delta_i\): typed semantic deltas/residuals at hierarchy level \(i\);
* \(T\): delta transport;
* \(R\): canonical reconciliation;
* \(A\): durable authority.

That should become the **constitutional architecture**.

---

# 2. The first hard rule: persist authority, not interiors

For every intermediate object \(x\), ask:

$$
\boxed{
\text{Must another independent future computation observe }x
\text{ exactly as a durable authority?}
}
$$

If not, \(x\) does not belong on the mandatory PostgreSQL hot path.

That gives us three very different categories.

### Execution interior

Examples:

* spaCy `Doc`;
* raw token objects;
* local dependency coordinates;
* sentence-local morphology arrays;
* packed sentence fibres;
* scratch indexes;
* temporary candidate sets;
* local graph adjacency used only during reduction.

These should normally live in RAM or a compact execution artifact.

$$
\boxed{
\text{execution interior}\not\Rightarrow\text{SQL row}
}
$$

### Durable but non-authoritative execution evidence

Examples:

* parser receipt;
* content-addressed packed parser artifact;
* checkpoint;
* worker attempt;
* performance telemetry;
* optional reference projection.

These may be persisted, but consumers must not mistake them for semantic authority.

### Semantic authority

Examples:

* admitted semantic objects;
* factors/relations;
* unresolved typed demands;
* residuals;
* promoted exports;
* canonical lookup projections;
* committed provenance;
* authoritative document generation.

These belong in PostgreSQL.

---

# 3. Parser fibres are computation partitions, not database partitions

The semantic document remains the object.

A parser fibre exists because:

$$
\text{bounded memory}
+
\text{parallelism}
+
\text{restartability}
$$

require partitioning.

It does **not** imply:

$$
\text{each fibre}
\rightarrow
\text{durable relational token graph}
\rightarrow
\text{next stage}.
$$

The target is instead:

$$
\boxed{
\operatorname{Parse}(S_i)
\rightarrow
F_i
}
$$

with \(F_i\) containing precisely the local structure needed by the semantic reducer.

For example:

$$
F_i=
(
\text{spans},
\text{lemma},
\text{POS},
\text{tag},
\text{dependency},
\text{head-relative offset},
\text{morphology},
\text{entity annotations},
\text{boundary obligations}
).
$$

The representation should remain compact and local.

The measured packed-carrier properties make this especially attractive: relative coordinates, local head deltas and small numeric vocabularies are overwhelmingly compact.

---

# 4. Database-local IDs must leave the semantic critical path

This is important.

A PostgreSQL `BIGINT` surrogate is a **storage coordinate**, not intrinsic semantic identity.

So the architecture should distinguish:

$$
\boxed{
\text{semantic identity}
\neq
\text{database surrogate}.
}
$$

Inside packed fibres and semantic deltas, use stable identities such as:

$$
\text{typed digest}
=
H(
\text{kind},
\text{canonical value}
).
$$

Dense local integer IDs are fine inside a fibre for compression:

$$
0,1,2,\ldots,n.
$$

But those are execution coordinates.

Only when something crosses the durable authority boundary do we resolve:

$$
\text{stable typed identity}
\rightarrow
\text{database-local BIGINT}.
$$

That means the ideal hot path no longer needs:

$$
\text{spaCy}
\to
\boxed{\text{intern every parser symbol in PostgreSQL}}
\to
\text{solve}.
$$

It becomes:

$$
\text{spaCy}
\to
\text{local symbol dictionary}
\to
\text{solve}
\to
\boxed{\text{batch-intern only durable surviving identities}}.
$$

That potentially removes much more than the advisory-lock problem we just reduced.

---

# 5. `semantic_parser_token` becomes a reference projection

This is probably the most consequential architectural declaration.

The table does **not** disappear.

Instead its status becomes explicit:

$$
\boxed{
\texttt{semantic\_parser\_token}
=
\text{reference/audit projection}
}
$$

rather than:

$$
\boxed{
\texttt{semantic\_parser\_token}
=
\text{mandatory semantic bus}.
}
$$

Three modes make sense.

**Production mode**

$$
\text{spaCy}\to F\to Solve
$$

No parser-token SQL projection on the critical path.

**Parity/certification mode**

$$
F
\to
\begin{cases}
Solve_{\rm direct}\\
Project_{\rm SQL}\to Solve_{\rm reference}
\end{cases}
$$

and require consumer equivalence.

**Audit/debug mode**

Persist the parser relational projection when needed for inspection.

So:

$$
\boxed{
N_{\text{parser-token writes, production}}=0
}
$$

becomes an architectural acceptance gate.

---

# 6. Sentence-local solving should have zero DB crossings

For a closed sentence fibre \(F_s\),

$$
\boxed{
DBCrossings(LocalSolve(F_s))=0.
}
$$

The local solver should receive the packed structure directly.

Its output should be something like:

$$
L(F_s)
=
(
\Delta_s,
R_s,
U_s,
X_s
)
$$

where:

* \(\Delta_s\): admitted semantic delta;
* \(R_s\): unresolved typed residuals/demands;
* \(U_s\): uncertainty/alternative structure;
* \(X_s\): explicitly exported boundary state.

The exact names can follow existing owners, but this separation matters.

No step should be:

$$
F_s
\rightarrow SQL
\rightarrow SELECT
\rightarrow L.
$$

---

# 7. The same law applies recursively at every hierarchy level

This is where all the Agda work suddenly collapses into one architecture.

At every level:

$$
\boxed{
\text{child interior}
\rightarrow
\text{child boundary delta}
\rightarrow
\text{parent local reducer}.
}
$$

Never:

$$
\text{child changed}
\rightarrow
\text{reconstruct entire child}
\rightarrow
\text{reconstruct entire parent}.
$$

Let parent state be \(P\), incoming child delta \(\Delta C\), and affected key set:

$$
K_\Delta=Keys(\Delta C).
$$

Then:

$$
P'
=
R(P,\Delta C,K_\Delta).
$$

Only if the observable parent boundary changes:

$$
Boundary(P')\neq Boundary(P)
$$

do we emit:

$$
\Delta P.
$$

Therefore:

$$
\boxed{
Boundary(P')=Boundary(P)
\Rightarrow
\Delta P=0.
}
$$

And recursively:

$$
\Delta_s
\to
\Delta_p
\to
\Delta_a
\to
\Delta_d.
$$

This is the same \(D\times H\) shape we've been trying to obtain piecemeal.

---

# 8. One generic reconciliation algebra everywhere

Every keyed materialized relation should obey the same generic law.

For current state \(C\) and desired state \(D\):

$$
D,C
\mapsto
(
\Delta^+,
\Delta^-,
\Delta^\*,
U
).
$$

Where:

$$
\Delta^+=D\setminus C
$$

$$
\Delta^-=C\setminus D
$$

$$
\Delta^\*=
\{\text{same key, changed value}\}
$$

$$
U=
\{\text{same key, same value}\}.
$$

And universally:

$$
\boxed{
U\Rightarrow 0\text{ writes}.
}
$$

This shouldn't be a candidate optimization.

It should become the default physical semantics of:

* candidate relations;
* parent exports;
* lookup projections;
* actor summaries;
* demand state;
* adjacency products;
* resolution state;
* derived caches;
* any keyed current-state projection.

Event histories remain append-only **only when a semantic event actually occurred**.

The generic law is:

$$
\boxed{
\text{reconsideration}
\neq
\text{transition}.
}
$$

---

# 9. PostgreSQL gets five jobs

This makes its proper role much clearer.

## PostgreSQL job 1 — durable authority

Canonical semantic state belongs there.

## PostgreSQL job 2 — global shared identity

For durable objects that actually need database-local numeric IDs:

$$
StableIdentity
\leftrightarrow
BIGINT.
$$

But perform that resolution in batches at publication boundaries.

## PostgreSQL job 3 — global reconciliation

Operations genuinely spanning independently produced fibres belong there where set-wise relational operations are useful.

For example:

* global lookup;
* cross-document lookup;
* unresolved demand matching across committed boundaries;
* generation publication;
* global uniqueness;
* durable provenance.

## PostgreSQL job 4 — recovery/checkpoint metadata

PostgreSQL is good at recording:

$$
\text{run},
\text{partition},
\text{attempt},
\text{generation},
\text{checkpoint},
\text{artifact digest}.
$$

It need not store the whole execution interior to provide recovery.

## PostgreSQL job 5 — audit/reference projections

Including the relational parser representation when certification or debugging needs it.

---

# 10. What PostgreSQL should specifically *not* do

This should be equally explicit.

PostgreSQL should not be the mandatory engine for:

* token-local dependency traversal;
* sentence-local PNF assembly;
* morphology decoding;
* repeatedly reconstructing closed child interiors;
* per-token intermediary publication;
* repeated candidate recomputation that can happen locally;
* per-interface hierarchy traversal;
* execution-only scratch topology;
* same-document temporary graph materialization;
* trivial local joins over data we already hold in memory.

A useful law is:

$$
\boxed{
\text{If all operands are already inside one bounded execution fibre,}
\quad
\text{do not cross into PostgreSQL merely to combine them.}
}
$$

---

# 11. Durable parser recovery should use a compact artifact, not relational explosion

There is one legitimate concern with removing parser-token SQL persistence:

> What if parsing finishes and the process dies before semantic closure?

We don't need 50,000 SQL token rows to solve that.

Persist a content-addressed packed parser artifact:

$$
A_F=Encode(F_1,\ldots,F_n)
$$

with:

$$
digest(A_F)
$$

and store only its receipt/locator in PostgreSQL.

Then:

$$
\text{crash}
\rightarrow
\text{reload }A_F
\rightarrow
\text{resume local semantic solve}.
$$

The packed representation is exactly suited for this.

So recovery becomes:

$$
\boxed{
\text{compact immutable artifact}
+
\text{small PostgreSQL checkpoint}
}
$$

rather than:

$$
\text{large indexed relational shadow of parser memory}.
$$

---

# 12. We should also stop using a gigantic semantic transaction

This is another architectural opportunity exposed by the recent diagnostics.

We can separate:

$$
\boxed{
\text{durable staging}
\neq
\text{published authority}.
}
$$

Each fibre may durably checkpoint:

$$
(\Delta_i,R_i,\text{receipt}_i)
$$

into a run/generation namespace.

Those rows are:

$$
\boxed{\text{durable but not consumer-visible authority}.}
$$

After the document reaches fixed point, perform a **small atomic publication transaction**:

$$
Generation_{candidate}
\rightarrow
Generation_{current}.
$$

Conceptually:

$$
\boxed{
\text{many resumable staging commits}
+
\text{one tiny authority flip}.
}
$$

That has several advantages:

* crash recovery;
* no enormous rollback;
* short database transactions;
* less lock lifetime;
* diagnostic receipts survive;
* easier replay;
* clean atomic consumer visibility.

This is much more appropriate than holding minutes of work inside one giant transaction.

---

# 13. Authority becomes generation-based

The clean implementation is probably an immutable or append-oriented generation model.

For document \(d\):

$$
G_d^0,G_d^1,\ldots
$$

Compiler work builds:

$$
G_d^{n+1}
$$

out of sight.

Consumer authority is:

$$
CurrentGeneration(d)=n.
$$

Final publication becomes approximately:

$$
\boxed{
CurrentGeneration(d):n\mapsto n+1.
}
$$

The expensive work has already happened.

This gives us transactional atomicity without requiring the entire computation itself to occur in one transaction.

---

# 14. Concurrency becomes much easier

Workers should own disjoint execution fibres.

They may share:

* immutable source;
* parser model;
* stable symbol hashes;
* document structural carrier.

They should **not** contend on global SQL dictionaries during ordinary local processing.

Only publication needs global coordination.

So:

$$
\boxed{
\text{parallel local compute}
\rightarrow
\text{batched convergence}
}
$$

instead of:

$$
\boxed{
\text{parallel compute}
\rightarrow
\text{constant contention on shared SQL state}.
}
$$

This is likely the proper final answer to the old `semantic_symbol` deadlock too: deterministic advisory locking is a useful safety mechanism, but the bigger architecture says those locks shouldn't sit in the parser's inner loop in the first place.

---

# 15. The whole compiler becomes a staged fixed-point machine

I would formalize the runtime as five phases.

$$
\boxed{
\mathcal C =
Publish
\circ
Close
\circ
Transport
\circ
Solve
\circ
Parse.
}
$$

With:

$$
Parse:S\rightarrow F
$$

$$
Solve:F\rightarrow(\Delta,R)
$$

$$
Transport:\Delta_i\rightarrow\Delta_{i+1}
$$

$$
Close:(State,\Delta^\*)\rightarrow State^\*
$$

$$
Publish:State^\*\rightarrow Authority.
$$

And the important fixed-point criterion:

$$
\boxed{
\Delta_{\rm outward}=\varnothing
}
$$

not:

> every table has been rescanned.

---

# 16. The commuting laws are the real correctness specification

There are several diagrams we should require the implementation to commute.

### Direct versus reference parser path

$$
\boxed{
Observe_C(Solve_{\rm packed}(F))
=
Observe_C(Solve_{\rm SQL}(Project(F)))
}
$$

for every relevant consumer \(C\).

### Child-to-parent transport

$$
\boxed{
Restrict(Apply(x,\Delta))
=
Apply(Restrict(x),Transport(\Delta)).
}
$$

### Batch versus sequential delta application

For independent/disjoint deltas:

$$
\boxed{
Apply(x,\Delta_1\oplus\Delta_2)
=
Apply(Apply(x,\Delta_1),\Delta_2).
}
$$

subject to the explicit dependency/order conditions.

### Reconciliation

$$
\boxed{
Reconcile(C,D)=D.
}
$$

And:

$$
\boxed{
C=D
\Rightarrow
Writes=0.
}
$$

### Publication

Candidate generation is invisible until:

$$
Valid(G)\land Closed(G)\land Certified(G).
$$

Then and only then:

$$
Publish(G).
$$

---

# 17. Consumer-specific residuals remain first-class

Performance cannot justify destructive pruning.

If a sentence cannot fully resolve something:

$$
F_s
\rightarrow
(\Delta_s,R_s).
$$

The residual survives upward:

$$
R_s
\rightarrow
Transport(R_s).
$$

A parent may:

* resolve it;
* refine it;
* retain ambiguity;
* emit another residual.

The system therefore never needs to retain the entire child interior merely because some future parent might care.

It retains the **typed residual sufficient for that future consumer**.

That's precisely where the formal residual/observer work becomes operationally valuable.

---

# 18. Boundary size must be bounded by semantics, not accumulated state

For a closed fibre \(f\):

$$
B(f)=
Exports(f)
\cup
Summaries(f)
\cup
Residuals(f)
\cup
Scope(f).
$$

Not:

$$
B(f)=Interior(f).
$$

And where the bounded-interface theorem applies:

$$
|Keys(B(f))|\le C.
$$

Then runtime work should have the corresponding structural receipt:

$$
\boxed{
W
\sim
N\,W_f\,(3C+B)
}
$$

or the appropriate existing theorem form.

If a runtime owner touches far more than its admitted affected-key bound, that's an architecture violation—not merely “slow SQL.”

---

# 19. Observability gets its own architecture

This also solves the painful optimization workflow.

We should have two completely separate evidence planes.

### Authority plane

May roll back.

Determines semantic acceptance.

### Diagnostic plane

Must survive process death and semantic rollback.

Never determines semantic authority.

Every optimization probe should continuously emit:

$$
\boxed{
\begin{aligned}
&T_{\rm parser},\\
&T_{\rm projection},\\
&T_{\rm localSolve},\\
&T_{\rm transport},\\
&T_{\rm DBpublish},\\
&T_{\rm reference},\\
&CPU,\\
&RSS,\\
&DBWait,\\
&SQLCalls,\\
&RowsIns/Upd/Del,\\
&KeysTouched,\\
&UnchangedSkipped,\\
&SemanticDeltasEmitted.
\end{aligned}
}
$$

And explicitly:

$$
acceptanceEligible=false
$$

for incomplete probes.

A 30-second kill and a 10-minute timeout should yield essentially the same **shape** of diagnostic evidence.

That should be permanent infrastructure now.

---

# 20. Flame graphs have a specific place

They aren't abolished.

Use them when:

$$
\frac{CPU}{Wall}
$$

is high enough that CPU execution needs explaining.

Don't use them as the first diagnostic for:

$$
Wall=80s,\qquad CPU=6s.
$$

In that regime:

$$
DB waits + I/O + synchronization
$$

are the relevant observables.

So the profiling hierarchy should be:

$$
\boxed{
\text{owner timing}
\rightarrow
\text{DB waits/churn}
\rightarrow
\text{SQL template timing}
\rightarrow
\text{CPU flamegraph if CPU remains material}.
}
$$

---

# 21. The production architecture therefore has four persistence cuts

This is probably the cleanest way to remember the entire design.

### Cut A — immutable input

Persist:

$$
\text{source bytes/digest}.
$$

### Cut B — resumability

Optionally persist:

$$
\text{packed execution artifact + parser receipt}.
$$

Not row-wise parser interiors.

### Cut C — semantic staging

Persist:

$$
\Delta,\ R,\ provenance,\ receipts
$$

in a non-current generation.

### Cut D — authority publication

Atomically publish the closed generation.

That's it.

Everything else has to justify its existence.

---

# 22. This gives us a concrete database constitution

A useful design test for every table is:

> Which persistence cut owns this table?

If the answer is none, it probably should not be on the production path.

For example:

| Object                           | Production PG role                                  |
| -------------------------------- | --------------------------------------------------- |
| immutable source                 | yes                                                 |
| parser run/checkpoint            | yes                                                 |
| compact parser artifact receipt  | yes                                                 |
| every parser token               | **no, optional reference**                          |
| every raw parser symbol          | **no, unless survives into durable semantic state** |
| sentence-local scratch graph     | no                                                  |
| local candidate scratch relation | no                                                  |
| semantic delta                   | yes                                                 |
| unresolved residual              | yes                                                 |
| promoted interface export        | yes                                                 |
| global lookup                    | yes                                                 |
| generation pointer               | yes                                                 |
| acceptance receipt               | yes                                                 |
| diagnostic telemetry             | separate non-authority channel                      |

That table alone can stop us circling back into the current design.

---

# 23. The implementation roadmap should now be convergence, not discovery

From here I would stop naming performance migrations according to whatever symptom was last measured.

Everything should converge on one named architecture—for example:

$$
\boxed{\textbf{Direct Delta Compiler Architecture}}
$$

or whatever repository terminology you prefer.

Then the remaining work is simply making each runtime boundary satisfy it:

1. **Parser seam:** spaCy → packed structural fibre without mandatory SQL token projection.
2. **Local semantic seam:** packed fibre → semantic delta with zero DB crossings.
3. **Hierarchy seam:** delta → affected keys → local reducer → changed parent delta.
4. **Persistence seam:** durable non-authoritative staging + compact artifacts.
5. **Publication seam:** atomic generation promotion.
6. **Reference seam:** SQL token path retained solely for parity/audit until retirement criteria are met.
7. **Observability seam:** rollback-independent diagnostics across every stage.
8. **Certification seam:** direct/reference equivalence plus completed-corpus acceptance.

That is the one list I would put at the top of the implementation programme.

---

# 24. The final performance constitution

We should make the physical requirements explicit too.

Correctness first:

$$
\boxed{
Observe_C(A_{\rm direct})
=
Observe_C(A_{\rm reference})
}
$$

for required consumers.

Then execution shape:

$$
\boxed{
DBCrossings_{\rm sentence-local}=0
}
$$

$$
\boxed{
ParserTokenWrites_{\rm production}=0
}
$$

$$
\boxed{
UnchangedRelationWrites=0
}
$$

$$
\boxed{
HierarchyWork\propto D\times H
}
$$

$$
\boxed{
ClosedChildInteriorReads_{\rm parent}=0
}
$$

$$
\boxed{
GlobalIDResolution
\text{ occurs only at durable publication boundaries}
}
$$

and eventually:

$$
\boxed{
T_{\rm post-parser}
\le
0.1\,T_{\rm spaCy}
}
$$

for the ultimate target, with an intermediate practical gate such as:

$$
T_{\rm total}\le1.5\,T_{\rm spaCy}.
$$

Those become **architectural acceptance criteria**, not aspirations.

---

# 25. The resulting picture

The whole system becomes:

```text
                  EXECUTION DOMAIN
                  ────────────────

Immutable Source
      │
      ▼
┌───────────────┐
│ Parser Fibre  │
└───────┬───────┘
        │
        ▼
┌──────────────────────┐
│ Packed Structural F  │
│ local IDs + digests  │
└──────────┬───────────┘
           │   no PostgreSQL
           ▼
┌──────────────────────┐
│ Local PNF Reducer    │
└──────────┬───────────┘
           │
           ▼
   Δ + residuals
           │
           ▼
┌──────────────────────┐
│ Delta Transport      │◄──── affected keys only
└──────────┬───────────┘
           │
           ▼
   Document Fixed Point
           │
           │
           ├──────────────► optional packed checkpoint
           │
           ▼

                  DURABLE DOMAIN
                  ──────────────

┌──────────────────────┐
│ Semantic Staging     │
│ non-current gen      │
└──────────┬───────────┘
           │
           ▼
     validate / close
           │
           ▼
┌──────────────────────┐
│ Atomic Publication   │
└──────────┬───────────┘
           │
           ▼
  Canonical Authority
  + lookup + provenance


        REFERENCE / CERTIFICATION DOMAIN
        ────────────────────────────────

Packed Fibre ──► relational parser projection
                         │
                         ▼
                 reference SQL solver
                         │
                         ▼
                  consumer parity
```

And alongside the whole thing:

```text
external diagnostic observer
    │
    ├── owner wall
    ├── CPU
    ├── RSS
    ├── PostgreSQL waits
    ├── SQL calls
    ├── WAL/churn
    ├── touched keys
    ├── unchanged skipped
    └── emitted semantic deltas

never semantic authority
survives rollback / SIGTERM
```

That is, I think, the architecture we've actually been converging toward the whole time.

The important change now is to **declare it finished conceptually**.

We no longer ask:

> “What should we optimize after token insertion?”

We ask:

> **“Which remaining runtime edge violates the Direct Delta Compiler architecture?”**

Then every tranche is mechanical convergence toward an already-known endpoint.

And by that standard the current largest violation is obvious:

$$
\boxed{
\text{mandatory parser-token PostgreSQL materialization}
}
$$

followed by any remaining SQL-mediated sentence-local solving, then any remaining reconstruction rather than delta transport.

That gives us a finite programme, a formal destination, and an objective definition of “done.”
