import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';

import {
  buildUnifiedWorkbenchProjection,
  nextUnifiedWorkbenchStage,
} from '../src/lib/workbench/unifiedWorkbench.js';

const ROOT = new URL('..', import.meta.url);

function readJson(rel) {
  return JSON.parse(readFileSync(join(ROOT.pathname, rel), 'utf8'));
}

test('M10 Wave-5 projection keeps journal lineage and unresolved timeline without fabricating proof', () => {
  const bundle = readJson('tests/fixtures/fact_review_wave5_real_professional_handoff_demo_bundle.json');
  const projection = buildUnifiedWorkbenchProjection(bundle.workbench, {
    selectedFactId: 'fact:2499c1b666ccd133',
  });

  assert.equal(projection.version, 'itir.unified_workbench.v0_1');
  assert.equal(projection.selected_fact_id, 'fact:2499c1b666ccd133');

  assert.equal(projection.stage_by_key.journal.status, 'available');
  assert.deepEqual(
    projection.stage_by_key.journal.source_ids,
    ['src:5e78e41d87374808']
  );
  assert.deepEqual(
    projection.stage_by_key.journal.statement_ids,
    ['statement:6a76d26b680c03e9']
  );

  assert.notEqual(projection.stage_by_key.timeline.status, 'available');
  assert.equal(projection.stage_by_key.matter_proof.status, 'unavailable');
  assert.match(
    projection.stage_by_key.matter_proof.reason,
    /not promoted into legal applicability/i
  );

  assert.equal(projection.invariant.shared_world_only, true);
  assert.equal(projection.invariant.creates_semantic_authority, false);
  assert.equal(projection.invariant.creates_claim_truth, false);
});

test('M10 Wave-5 selected handoff fact is visible in handoff stage', () => {
  const bundle = readJson('tests/fixtures/fact_review_wave5_real_professional_handoff_demo_bundle.json');
  const handoffItems = bundle.workbench.operator_views.professional_handoff.items;
  assert.ok(handoffItems.length >= 1);

  const selected = handoffItems[0];
  const projection = buildUnifiedWorkbenchProjection(bundle.workbench, {
    selectedFactId: selected.fact_id,
  });

  assert.equal(projection.stage_by_key.handoff.status, 'available');
  assert.equal(projection.stage_by_key.handoff.fact_id, selected.fact_id);
  assert.equal(projection.stage_by_key.handoff.item.fact_id, selected.fact_id);
});

test('M10 unselected Wave-5 fact is blocked from handoff rather than silently included', () => {
  const bundle = readJson('tests/fixtures/fact_review_wave5_real_professional_handoff_demo_bundle.json');
  const handoffFactIds = new Set(
    bundle.workbench.operator_views.professional_handoff.items.map((item) => item.fact_id)
  );
  const outside = bundle.workbench.facts.find((fact) => !handoffFactIds.has(fact.fact_id));

  assert.ok(outside);
  const projection = buildUnifiedWorkbenchProjection(bundle.workbench, {
    selectedFactId: outside.fact_id,
  });

  assert.equal(projection.stage_by_key.handoff.status, 'blocked');
  assert.match(projection.stage_by_key.handoff.reason, /not currently included/i);
});

test('M10 research stage exposes persisted review pressure rather than inventing residuals', () => {
  const bundle = readJson('tests/fixtures/fact_review_wave5_real_professional_handoff_demo_bundle.json');
  const projection = buildUnifiedWorkbenchProjection(bundle.workbench, {
    selectedFactId: 'fact:e0667b55061037f4',
  });

  assert.equal(projection.stage_by_key.research.status, 'available');
  assert.ok(projection.stage_by_key.research.review_queue_count >= 1);
  assert.ok(projection.stage_by_key.research.pressure_count >= 1);
});

test('M10 stage navigation preserves fixed semantic order', () => {
  const bundle = readJson('tests/fixtures/fact_review_wave5_real_professional_handoff_demo_bundle.json');
  const projection = buildUnifiedWorkbenchProjection(bundle.workbench, {
    selectedFactId: 'fact:e0667b55061037f4',
  });

  assert.equal(nextUnifiedWorkbenchStage(projection, 'journal')?.key, 'timeline');
  assert.equal(nextUnifiedWorkbenchStage(projection, 'timeline')?.key, 'handoff');
  assert.equal(nextUnifiedWorkbenchStage(projection, 'handoff')?.key, 'matter_proof');
  assert.equal(nextUnifiedWorkbenchStage(projection, 'matter_proof')?.key, 'research');
  assert.equal(nextUnifiedWorkbenchStage(projection, 'research'), null);
});
