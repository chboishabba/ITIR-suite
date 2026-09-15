import assert from 'node:assert/strict';
import test from 'node:test';

import {
  cardKinds,
  compileReadingIntent,
  createMaboReadingSpecimen,
  guideCues,
  projectReadingStage,
} from '../src/lib/workbench/readingSurface.js';

test('Mabo reading specimen defaults to a bounded five-stage explanation', () => {
  const specimen = createMaboReadingSpecimen();

  assert.equal(specimen.stages.length, 5);
  assert.deepEqual(
    specimen.stages.map((stage) => stage.role),
    [
      'challenged-premise',
      'historical-input',
      'authority-proposition',
      'immediate-implication',
      'downstream-application',
    ],
  );
  assert.equal(specimen.defaultView, 'explain');
  assert.equal(specimen.graphVisibleByDefault, false);
  assert.equal(specimen.contextVisibleByDefault, false);
  assert.equal(specimen.guideVisibleByDefault, false);
});

test('all view projections preserve semantic, proof, and source identity', () => {
  const stage = createMaboReadingSpecimen().stages[2];

  for (const view of ['explain', 'why', 'source', 'context', 'graph', 'guide']) {
    const projected = projectReadingStage(stage, view);
    assert.equal(projected.semanticRef, stage.semanticRef);
    assert.equal(projected.proofRef, stage.proofRef);
    assert.equal(projected.sourceRef, stage.sourceRef);
  }
});

test('reading interactions compile to the existing JCUI semantic actions', () => {
  const stage = createMaboReadingSpecimen().stages[2];

  assert.deepEqual(compileReadingIntent(stage, 'why'), {
    action: 'Expand',
    targetKind: 'Semantic',
    target: stage.semanticRef,
  });
  assert.deepEqual(compileReadingIntent(stage, 'source'), {
    action: 'OpenSource',
    targetKind: 'Source',
    target: stage.sourceRef,
  });
  assert.deepEqual(compileReadingIntent(stage, 'context'), {
    action: 'Follow',
    targetKind: 'Semantic',
    target: stage.semanticRef,
  });
  assert.deepEqual(compileReadingIntent(stage, 'graph'), {
    action: 'Zoom',
    targetKind: 'Semantic',
    target: stage.semanticRef,
    detail: 'Fit',
  });
});

test('identity source and proof cards remain separate', () => {
  assert.deepEqual(cardKinds, ['identity', 'source', 'proof']);
});

test('guide mode uses the PNF reading cue vocabulary only', () => {
  assert.deepEqual(guideCues, [
    'actor',
    'predicate',
    'patient',
    'negation',
    'modality',
    'condition',
    'temporal',
    'coreference',
  ]);
});

test('lay projection does not expose expert metadata by default', () => {
  const specimen = createMaboReadingSpecimen();

  assert.equal(specimen.showQidsByDefault, false);
  assert.equal(specimen.showHashesByDefault, false);
  assert.equal(specimen.showAllResidualsByDefault, false);
  assert.equal(specimen.showAllSourceRolesByDefault, false);
});

test('source inspection retains exact-source readiness coordinates', () => {
  const stage = createMaboReadingSpecimen().stages[2];

  assert.ok(stage.sourceRef);
  assert.ok(stage.sourceSpanRef);
  assert.ok(stage.sourceRevisionRef);
  assert.equal(stage.exactAuthorityReady, true);
});

test('Mabo context keeps Wikidata and Wikipedia navigation explicitly non-authoritative', () => {
  const specimen = createMaboReadingSpecimen();

  assert.equal(specimen.context.wikidataQid, 'Q1501525');
  assert.equal(specimen.context.wikipediaRef, 'wiki:en:Mabo_v_Queensland_(No_2)');
  assert.equal(specimen.context.identityCandidateOnly, true);
  assert.equal(specimen.context.legalAuthority, false);
  assert.equal(specimen.context.evidencePaid, false);
  assert.equal(specimen.context.semanticPromotion, false);
});

test('fixture cannot encode legal verdict, payment, belief, or comprehension state', () => {
  const specimen = createMaboReadingSpecimen();

  assert.equal('legalVerdict' in specimen, false);
  assert.equal('evidencePaid' in specimen, false);
  assert.equal('userBelieves' in specimen, false);
  assert.equal('userUnderstands' in specimen, false);
});
