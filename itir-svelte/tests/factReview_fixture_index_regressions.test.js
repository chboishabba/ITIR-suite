import test from 'node:test';
import assert from 'node:assert/strict';
import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const ROOT = new URL('..', import.meta.url);

function read(rel) {
  return readFileSync(join(ROOT.pathname, rel), 'utf8');
}

test('fact review demo-bundle fixture index stays aligned with checked-in real bundles', () => {
  const fixtureIndex = read('tests/fixtures/FACT_REVIEW_DEMO_BUNDLES.md');
  const routeDoc = read('docs/planning/mary_fact_review_demo_path_20260319.md');

  const expectedFiles = [
    'tests/fixtures/fact_review_wave1_real_demo_bundle.json',
    'tests/fixtures/fact_review_wave1_real_au_demo_bundle.json',
    'tests/fixtures/fact_review_wave1_real_au_demo_bundle_b0babf.json',
    'tests/fixtures/fact_review_wave3_real_fragmented_support_demo_bundle.json',
    'tests/fixtures/fact_review_wave5_real_professional_handoff_demo_bundle.json',
    'tests/fixtures/fact_review_wave5_real_false_coherence_demo_bundle.json',
  ];

  for (const rel of expectedFiles) {
    assert.ok(existsSync(join(ROOT.pathname, rel)), `${rel} should exist`);
    assert.ok(fixtureIndex.includes(rel.split('/').at(-1) ?? rel), `${rel} should be indexed`);
  }

  assert.ok(routeDoc.includes('wave1:real_transcript_intake_v1'));
  assert.ok(routeDoc.includes('wave1:real_au_procedural_v1'));
  assert.ok(routeDoc.includes('wave3:real_transcript_fragmented_support_v1'));
  assert.ok(routeDoc.includes('wave5:real_transcript_professional_handoff_v1'));
  assert.ok(routeDoc.includes('wave5:real_transcript_false_coherence_v1'));
});
