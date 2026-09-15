# Mabo Reading Workbench v0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first ITIR/Svelte Reading Workbench vertical slice that explains one Mabo proposition chain progressively, reopens exact source/proof context, and exposes stable semantic targets for JCUI without making the UI a second legal-semantics engine.

**Architecture:** Add a producer-shaped `ReadingWorkbenchModel` plus a small family of Svelte read components. Reuse the existing `selectionBridge`, `DocumentViewer`, and `LayeredGraph` primitives. The route owns view state only; Mabo legal semantics remain in the source read model. JCUI integration is an application adapter over semantic target ids and actions; ITIR does not implement the JCUI binary codec.

**Tech Stack:** SvelteKit 2, Svelte 5, TypeScript 5.6, Tailwind 3.4, Node test runner, Playwright accessibility tests, existing ITIR/Svelte UI primitives.

**Spec:** `docs/planning/mabo_reading_workbench_v0_20260915.md`

## Global Constraints

- Default UX is argument-first, graph-second, provenance-on-demand.
- `ProofGraphAvailable != ProofGraphInitiallyVisible`.
- Same canonical read model drives lay and expert views; no simplified truth model.
- Semantic selection uses stable semantic ids, never CSS selectors as canonical identity.
- Wikipedia/Wikidata are context/navigation only; they do not become legal authority.
- PNF annotations are explanatory aids and do not create legal conclusions.
- Source text must come from producer/source payloads; never synthesize an “exact passage” from explanation text.
- Reading Trail is ephemeral by default and cannot infer belief or understanding.
- ITIR/Svelte does not implement the JCUI binary codec or physical gesture mapping.
- No full unbounded graph, dashboard, personalization model, or proof-state editing in v0.

---

## File Structure

Create:

- `itir-svelte/src/lib/reading/types.ts` — stable Reading Workbench read-model types.
- `itir-svelte/src/lib/reading/maboFixture.ts` — bounded Mabo v0 specimen read model assembled from existing canonical IDs/source coordinates.
- `itir-svelte/src/lib/reading/ReadingSurface.svelte` — plain explanation + five-node progressive reading view.
- `itir-svelte/src/lib/reading/SemanticInspector.svelte` — compact selected-node inspector.
- `itir-svelte/src/lib/reading/SourceDrawer.svelte` — exact-source view using `DocumentViewer`.
- `itir-svelte/src/lib/reading/ProofCone.svelte` — bounded adapter to `LayeredGraph`.
- `itir-svelte/src/lib/reading/ReadingTrail.svelte` — visible ephemeral navigation trail.
- `itir-svelte/src/lib/reading/readingTrail.ts` — pure navigation-stack state transition helper.
- `itir-svelte/src/lib/reading/jcuiAdapter.ts` — maps decoded JCUI semantic actions/observations to Reading Workbench state; no wire codec.
- `itir-svelte/src/routes/reading/mabo/+page.svelte` — workbench composition route.
- `itir-svelte/src/routes/reading/mabo/+page.server.ts` — load the bounded read model.
- `itir-svelte/tests/mabo_reading_workbench_regressions.test.js` — structural/product regressions.
- `itir-svelte/tests/mabo_reading_workbench.a11y.spec.ts` — keyboard/focus/progressive-disclosure browser checks.

Modify:

- `itir-svelte/src/lib/workbench/selectionBridge.ts` only if a missing reason/scope transition is demonstrated by a failing test; otherwise leave unchanged.
- `itir-svelte/README.md` — list `/reading/mabo` as the first Reading Workbench.

Do not modify `LayeredGraph.svelte` or `DocumentViewer.svelte` unless a failing v0 test demonstrates a missing generic primitive.

---

### Task 1: Pin the Reading Workbench read-model contract

**Files:**
- Create: `itir-svelte/src/lib/reading/types.ts`
- Create: `itir-svelte/src/lib/reading/maboFixture.ts`
- Test: `itir-svelte/tests/mabo_reading_workbench_regressions.test.js`

**Interfaces:**
- Produces: `ReadingWorkbenchModel`, `ReadingSemanticRef`, `ReadingSourceRef`, `ReadingPnfToken`, `ReadingEdge`, `maboReadingWorkbenchFixture`.
- Consumed by: Tasks 2–8.

- [ ] **Step 1: Write the failing structural regression**

Add to `mabo_reading_workbench_regressions.test.js`:

```js
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';

const ROOT = new URL('../', import.meta.url);
const read = (rel) => readFileSync(join(ROOT.pathname, rel), 'utf8');

test('Mabo reading model keeps semantic promotion false and graph bounded', () => {
  const types = read('src/lib/reading/types.ts');
  const fixture = read('src/lib/reading/maboFixture.ts');
  assert.match(types, /schema: 'itir\.reading_workbench\.v0_1'/);
  assert.match(types, /semanticPromotion: false/);
  assert.match(fixture, /Why was Mabo such a big deal\?/);
  assert.match(fixture, /initialNodeIds/);
  assert.match(fixture, /semanticPromotion: false/);
});
```

- [ ] **Step 2: Run the test and verify RED**

Run:

```bash
cd itir-svelte
node --test tests/mabo_reading_workbench_regressions.test.js
```

Expected: FAIL because `src/lib/reading/types.ts` / `maboFixture.ts` do not exist.

- [ ] **Step 3: Implement minimal typed model**

Create `types.ts` with exactly the contract in the spec. Create `maboFixture.ts` exporting one five-node fixture. Use stable ids such as:

```ts
export const MABO_IDS = {
  question: 'mabo:question:why-big-deal',
  before: 'mabo:explanation:before',
  premise: 'mabo:proposition:terra-nullius',
  change: 'mabo:proposition:sovereignty-not-automatic-extinguishment',
  consequence: 'mabo:consequence:native-title-may-survive',
  qualification: 'mabo:qualification:not-every-claim-succeeds',
  proofCone: 'mabo:proof-cone'
} as const;
```

The fixture must include the High Court source identity as a `primary_authority` source and keep Wiki/Wikidata entries in `wikiContext` only.

- [ ] **Step 4: Verify GREEN and type-check**

```bash
node --test tests/mabo_reading_workbench_regressions.test.js
npm run check
```

Expected: PASS; `svelte-check` reports no errors from the new types/fixture.

- [ ] **Step 5: Commit**

```bash
git add src/lib/reading/types.ts src/lib/reading/maboFixture.ts tests/mabo_reading_workbench_regressions.test.js
git commit -m 'feat(reading): add Mabo workbench read model'
```

---

### Task 2: Build the progressive Reading Surface

**Files:**
- Create: `itir-svelte/src/lib/reading/ReadingSurface.svelte`
- Modify: `itir-svelte/tests/mabo_reading_workbench_regressions.test.js`

**Interfaces:**
- Consumes: `ReadingWorkbenchModel`, `SelectionBridge<string>`.
- Emits: semantic selection only through callbacks/bridge; no proof mutation.

- [ ] **Step 1: Add failing UI-contract assertions**

```js
test('ReadingSurface is explanation-first and graph-free by default', () => {
  const s = read('src/lib/reading/ReadingSurface.svelte');
  assert.match(s, /Why was Mabo such a big deal\?/);
  assert.match(s, />Why\?</);
  assert.match(s, />Source</);
  assert.match(s, />Show reasoning</);
  assert.doesNotMatch(s, /LayeredGraph/);
});
```

- [ ] **Step 2: Run RED**

```bash
node --test tests/mabo_reading_workbench_regressions.test.js
```

Expected: FAIL because the component does not exist.

- [ ] **Step 3: Implement minimal component**

`ReadingSurface.svelte` renders `model.summary` and only `model.initialNodeIds`. Use native `<button>` elements for semantic actions. Dispatch:

```ts
createEventDispatcher<{
  select: { semanticId: string };
  source: { semanticId: string };
  reasoning: { semanticId: string };
  meaning: { semanticId: string };
  follow: { semanticId: string };
}>();
```

Do not import `LayeredGraph`.

- [ ] **Step 4: Verify GREEN**

```bash
node --test tests/mabo_reading_workbench_regressions.test.js
npm run check
```

- [ ] **Step 5: Commit**

```bash
git add src/lib/reading/ReadingSurface.svelte tests/mabo_reading_workbench_regressions.test.js
git commit -m 'feat(reading): add progressive Mabo reading surface'
```

---

### Task 3: Add opt-in PNF reading affordances and Semantic Inspector

**Files:**
- Create: `itir-svelte/src/lib/reading/SemanticInspector.svelte`
- Modify: `itir-svelte/src/lib/reading/ReadingSurface.svelte`
- Modify: `itir-svelte/tests/mabo_reading_workbench_regressions.test.js`

**Interfaces:**
- Consumes: selected semantic id and `pnfByNode` entries.
- Produces: visible textual role labels and explicit context/source/reasoning actions.

- [ ] **Step 1: Write failing regressions**

```js
test('PNF affordances are opt-in and role text is not color-only', () => {
  const surface = read('src/lib/reading/ReadingSurface.svelte');
  const inspector = read('src/lib/reading/SemanticInspector.svelte');
  assert.match(surface, /Show language roles/);
  assert.match(inspector, /actor|predicate|patient|negation|modality|condition/);
  assert.match(inspector, /Explore context/);
});
```

- [ ] **Step 2: Run RED**

```bash
node --test tests/mabo_reading_workbench_regressions.test.js
```

- [ ] **Step 3: Implement minimal PNF toggle + inspector**

Maintain a route/view boolean `showPnf`; do not write to the model. Render PNF token role as text/ARIA, e.g.:

```svelte
<span aria-label={`${token.text}: ${token.role}`}>
  {token.text}<span class="sr-only"> ({token.role})</span>
</span>
```

The inspector gets the active `ReadingSemanticRef` and displays kind, label, one explanation/context summary, plus buttons for `Source`, `Show reasoning`, `Explore context`.

- [ ] **Step 4: Verify**

```bash
node --test tests/mabo_reading_workbench_regressions.test.js
npm run check
```

- [ ] **Step 5: Commit**

```bash
git add src/lib/reading/ReadingSurface.svelte src/lib/reading/SemanticInspector.svelte tests/mabo_reading_workbench_regressions.test.js
git commit -m 'feat(reading): add PNF affordances and semantic inspector'
```

---

### Task 4: Reuse DocumentViewer as exact Source Drawer

**Files:**
- Create: `itir-svelte/src/lib/reading/SourceDrawer.svelte`
- Modify: `itir-svelte/tests/mabo_reading_workbench_regressions.test.js`

**Interfaces:**
- Consumes: `ReadingSourceRef`, source text supplied by route/model, exact char span.
- Uses: `DocumentViewer`, `DocumentHighlight`.
- Produces: compact provenance header + exact passage highlight.

- [ ] **Step 1: Write failing regression**

```js
test('SourceDrawer reuses DocumentViewer and refuses fabricated source text', () => {
  const s = read('src/lib/reading/SourceDrawer.svelte');
  assert.match(s, /DocumentViewer/);
  assert.match(s, /primary authority|Source role|Used here for/i);
  assert.match(s, /Source text unavailable/);
});
```

- [ ] **Step 2: Run RED**

```bash
node --test tests/mabo_reading_workbench_regressions.test.js
```

- [ ] **Step 3: Implement source drawer**

Use the existing char-span contract:

```ts
const highlights: DocumentHighlight[] = source.charStart != null && source.charEnd != null
  ? [{
      key: source.id,
      charStart: source.charStart,
      charEnd: source.charEnd,
      color: '#f59e0b',
      kind: 'active',
      source: 'receipt',
      sourceArtifactId: source.sourceArtifactId
    }]
  : [];
```

If no source text exists, render `Source text unavailable in this artifact` and metadata/actions only.

- [ ] **Step 4: Verify**

```bash
node --test tests/mabo_reading_workbench_regressions.test.js
npm run check
```

- [ ] **Step 5: Commit**

```bash
git add src/lib/reading/SourceDrawer.svelte tests/mabo_reading_workbench_regressions.test.js
git commit -m 'feat(reading): add exact source drawer'
```

---

### Task 5: Add bounded Proof Cone using LayeredGraph

**Files:**
- Create: `itir-svelte/src/lib/reading/ProofCone.svelte`
- Modify: `itir-svelte/tests/mabo_reading_workbench_regressions.test.js`

**Interfaces:**
- Consumes: current semantic locus, bounded nodes/edges from `ReadingWorkbenchModel`.
- Uses: `LayeredGraph.svelte` and the same selection bridge.
- Produces: explicit power view only after user expansion.

- [ ] **Step 1: Write failing boundedness regression**

```js
test('ProofCone reuses LayeredGraph and is explicitly bounded', () => {
  const s = read('src/lib/reading/ProofCone.svelte');
  assert.match(s, /LayeredGraph/);
  assert.match(s, /bounded/i);
  assert.match(s, /nodeSelect/);
});
```

- [ ] **Step 2: Run RED**

```bash
node --test tests/mabo_reading_workbench_regressions.test.js
```

- [ ] **Step 3: Implement one-neighborhood adapter**

Build layers from only:

```ts
selected node
+ direct incoming/outgoing support/defeater/comparator/source/application nodes
+ immediate consequence/residual nodes already present in model
```

Never fetch/render the full proof graph from this component. Pass `scale` only as display emphasis; never compute truth/confidence from it.

- [ ] **Step 4: Verify**

```bash
node --test tests/mabo_reading_workbench_regressions.test.js
npm run check
```

- [ ] **Step 5: Commit**

```bash
git add src/lib/reading/ProofCone.svelte tests/mabo_reading_workbench_regressions.test.js
git commit -m 'feat(reading): add bounded proof cone'
```

---

### Task 6: Add explicit Reading Trail and Back/Follow behavior

**Files:**
- Create: `itir-svelte/src/lib/reading/readingTrail.ts`
- Create: `itir-svelte/src/lib/reading/ReadingTrail.svelte`
- Modify: `itir-svelte/tests/mabo_reading_workbench_regressions.test.js`

**Interfaces:**
- Produces: `ReadingTrailEntry`, `pushTrail`, `backTrail`.
- Consumed by: route composition and JCUI adapter.

- [ ] **Step 1: Write failing source-contract regression**

```js
test('Reading Trail is explicit and ephemeral by default', () => {
  const t = read('src/lib/reading/readingTrail.ts');
  assert.match(t, /ephemeral/);
  assert.match(t, /activate|follow|open_source|expand_reasoning|back/);
  assert.doesNotMatch(t, /understands|beliefScore|mastery/);
});
```

- [ ] **Step 2: Run RED**

```bash
node --test tests/mabo_reading_workbench_regressions.test.js
```

- [ ] **Step 3: Implement pure trail transitions**

```ts
export type ReadingTrailEntry = {
  semanticId: string;
  action: 'activate' | 'follow' | 'open_source' | 'expand_reasoning' | 'back';
};

export type ReadingTrailState = {
  persistence: 'ephemeral';
  entries: ReadingTrailEntry[];
};

export function pushTrail(state: ReadingTrailState, entry: ReadingTrailEntry): ReadingTrailState {
  return { ...state, entries: [...state.entries, entry] };
}
```

`backTrail` returns the previous semantic locus without deleting history.

- [ ] **Step 4: Verify**

```bash
node --test tests/mabo_reading_workbench_regressions.test.js
npm run check
```

- [ ] **Step 5: Commit**

```bash
git add src/lib/reading/readingTrail.ts src/lib/reading/ReadingTrail.svelte tests/mabo_reading_workbench_regressions.test.js
git commit -m 'feat(reading): add explicit reading trail'
```

---

### Task 7: Compose `/reading/mabo` around one selection bridge

**Files:**
- Create: `itir-svelte/src/routes/reading/mabo/+page.server.ts`
- Create: `itir-svelte/src/routes/reading/mabo/+page.svelte`
- Modify: `itir-svelte/tests/mabo_reading_workbench_regressions.test.js`

**Interfaces:**
- Consumes: Mabo fixture/model, all Tasks 2–6 components.
- Produces: first end-to-end Reading Workbench route.

- [ ] **Step 1: Write failing route regression**

```js
test('Mabo route composes reading, inspector, source, trail and proof cone through selection bridge', () => {
  const s = read('src/routes/reading/mabo/+page.svelte');
  assert.match(s, /createSelectionBridge/);
  assert.match(s, /ReadingSurface/);
  assert.match(s, /SemanticInspector/);
  assert.match(s, /SourceDrawer/);
  assert.match(s, /ProofCone/);
  assert.match(s, /ReadingTrail/);
});
```

- [ ] **Step 2: Run RED**

```bash
node --test tests/mabo_reading_workbench_regressions.test.js
```

- [ ] **Step 3: Implement route composition**

`+page.server.ts` returns `maboReadingWorkbenchFixture` for v0. `+page.svelte` creates exactly one:

```ts
const selection = createSelectionBridge<string>(MABO_IDS.change, 'local');
```

View-only state includes:

```ts
let showPnf = false;
let showReasoning = false;
let sourceId: string | null = null;
let contextId: string | null = null;
```

Actions update view state/selection and append trail entries; they do not mutate the read model.

- [ ] **Step 4: Verify**

```bash
node --test tests/mabo_reading_workbench_regressions.test.js
npm run check
```

- [ ] **Step 5: Commit**

```bash
git add src/routes/reading/mabo src/lib/reading tests/mabo_reading_workbench_regressions.test.js
git commit -m 'feat(reading): compose Mabo reading workbench'
```

---

### Task 8: Add JCUI application adapter without duplicating the wire codec

**Files:**
- Create: `itir-svelte/src/lib/reading/jcuiAdapter.ts`
- Modify: `itir-svelte/tests/mabo_reading_workbench_regressions.test.js`

**Interfaces:**
- Consumes decoded interaction steps from the JesusCrust/JCUI boundary:

```ts
export type JcuiDecodedStep =
  | { kind: 'act'; action: 'Activate' | 'Focus' | 'Select' | 'Expand' | 'Collapse' | 'Follow' | 'OpenSource' | 'Zoom'; targetKind: 'Semantic' | 'Source'; target: string; detail?: 'In' | 'Out' | 'Fit' }
  | { kind: 'expect'; observation: 'Visible' | 'Hidden' | 'Focused' | 'Selected' | 'Expanded' | 'Collapsed'; targetKind: 'Semantic' | 'Source'; target: string };
```

- Produces application actions/observations against semantic ids only.
- Does not parse `JCUI v1` bytes and does not know CSS selectors.

- [ ] **Step 1: Write failing boundary regression**

```js
test('JCUI adapter is semantic-id based and contains no selector/gesture vocabulary', () => {
  const s = read('src/lib/reading/jcuiAdapter.ts');
  assert.match(s, /Activate|OpenSource|Zoom/);
  assert.match(s, /Visible|Expanded/);
  assert.doesNotMatch(s, /querySelector|cssSelector|mouseDown|touchstart|clientX|clientY/);
});
```

- [ ] **Step 2: Run RED**

```bash
node --test tests/mabo_reading_workbench_regressions.test.js
```

- [ ] **Step 3: Implement minimal adapter**

Define:

```ts
export type ReadingWorkbenchDriver = {
  activate(id: string): void;
  expand(id: string): void;
  collapse(id: string): void;
  follow(id: string): void;
  openSource(id: string): void;
  zoom(id: string, detail: 'In' | 'Out' | 'Fit'): void;
  observe(id: string, observation: JcuiDecodedStep & { kind: 'expect' }): boolean;
};

export function executeJcuiStep(driver: ReadingWorkbenchDriver, step: JcuiDecodedStep): boolean {
  // exhaustive switch; unknown tags are impossible at this decoded boundary
}
```

Keep binary/tag validation in JesusCrust.

- [ ] **Step 4: Verify**

```bash
node --test tests/mabo_reading_workbench_regressions.test.js
npm run check
```

- [ ] **Step 5: Commit**

```bash
git add src/lib/reading/jcuiAdapter.ts tests/mabo_reading_workbench_regressions.test.js
git commit -m 'feat(reading): add JCUI semantic interaction adapter'
```

---

### Task 9: Add keyboard/focus and progressive-disclosure acceptance test

**Files:**
- Create: `itir-svelte/tests/mabo_reading_workbench.a11y.spec.ts`

**Interfaces:**
- Tests the actual route behavior, not internal component implementation.

- [ ] **Step 1: Write failing Playwright acceptance test**

```ts
import { test, expect } from '@playwright/test';

test('Mabo workbench reveals reasoning and source progressively', async ({ page }) => {
  await page.goto('/reading/mabo');
  await expect(page.getByRole('heading', { name: /Why was Mabo such a big deal/i })).toBeVisible();
  await expect(page.getByText(/full authority graph/i)).toHaveCount(0);

  const reasoning = page.getByRole('button', { name: /Show reasoning/i }).first();
  await reasoning.focus();
  await expect(reasoning).toBeFocused();
  await reasoning.press('Enter');
  await expect(page.getByRole('region', { name: /bounded proof cone/i })).toBeVisible();

  await page.getByRole('button', { name: /^Source$/i }).first().click();
  await expect(page.getByRole('dialog', { name: /Source/i })).toBeVisible();
});
```

- [ ] **Step 2: Run and verify RED/GREEN as implementation requires**

```bash
npm run dev -- --host 127.0.0.1
npm run test:a11y -- tests/mabo_reading_workbench.a11y.spec.ts
```

Expected final state: PASS.

- [ ] **Step 3: Verify full frontend suite**

```bash
npm test
npm run check
npm run build
```

Expected: all PASS.

- [ ] **Step 4: Commit**

```bash
git add tests/mabo_reading_workbench.a11y.spec.ts
git commit -m 'test(reading): cover Mabo progressive disclosure and keyboard flow'
```

---

### Task 10: Document the first Reading Workbench and final verification

**Files:**
- Modify: `itir-svelte/README.md`
- Modify: `docs/planning/progressive_proof_explanation_workbench_20260915.md` only to record implementation status after all verification passes.

**Interfaces:**
- No new runtime interface.

- [ ] **Step 1: Add route documentation**

Add under Workbench Surfaces:

```text
- `/reading/mabo`: first progressive Reading Workbench; explanation-first Mabo specimen with opt-in PNF, source inspection, bounded proof cone, Wiki/Wikidata context and JCUI semantic targets.
```

- [ ] **Step 2: Run the complete verification surface**

```bash
cd itir-svelte
npm test
npm run check
npm run build
npm run test:a11y -- tests/mabo_reading_workbench.a11y.spec.ts
```

Do not mark the roadmap implementation complete unless every command exits 0.

- [ ] **Step 3: Self-review the product invariants**

Manually confirm:

```text
initial graph hidden
source exact/unavailable state explicit
Wiki/QID context separated from authority
PNF opt-in
single selection bridge
Reading Trail ephemeral
no proof mutation from UI
no selectors/gestures in JCUI adapter
```

- [ ] **Step 4: Commit docs/status**

```bash
git add itir-svelte/README.md docs/planning/progressive_proof_explanation_workbench_20260915.md
git commit -m 'docs(reading): record Mabo workbench v0'
```

---

## Self-review

### Spec coverage

- Progressive lay explanation: Tasks 1–3, 7.
- PNF affordances: Task 3.
- Exact source inspection: Task 4.
- Wiki/Wikidata context separation: Tasks 1, 3, 7.
- Bounded proof cone: Task 5.
- Reading Trail/anti-panopticon: Task 6.
- One synchronized semantic selection: Task 7.
- JCUI semantic intent boundary: Task 8.
- Accessibility/progressive disclosure: Task 9.
- Route/docs/verification: Task 10.

### Explicitly deferred

The following are intentionally outside v0 and require separate plans if pursued:

- anonymised lived-history/Dad UI adapter;
- wash-trading/investigation specimen;
- persistent StatiBaker navigation receipts;
- full graph/ribbon/hyperformal visualization;
- generic browser/physical gesture JCUI backend;
- learning exercises/mastery UI;
- GPU/WebGPU graph acceleration.

No v0 requirement depends on any of those deferred projects.
