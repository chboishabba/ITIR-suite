import assert from 'node:assert/strict';
import test from 'node:test';

import {
  buildElucidatoryCone,
  compileSemanticIntent,
  createContextCandidate,
  createSemanticTarget,
  defaultSemanticDisclosure,
  resolveExplainOutcome,
} from '../src/lib/workbench/semanticTrail.js';

test('overlapping constituent and composite targets retain independent identities', () => {
  const composite = createSemanticTarget({
    spanRef: 'span:0:18:36',
    targetKind: 'composite',
    surface: 'golden spider silk',
    semanticRef: 'semantic:golden-spider-silk',
  });
  const constituent = createSemanticTarget({
    spanRef: 'span:0:32:36',
    targetKind: 'constituent',
    surface: 'silk',
    semanticRef: 'semantic:silk',
  });

  assert.notEqual(composite.semanticRef, constituent.semanticRef);
  assert.notEqual(composite.spanRef, constituent.spanRef);
  assert.equal(composite.targetKind, 'composite');
  assert.equal(constituent.targetKind, 'constituent');
});

test('adaptive cone keeps base-depth nodes plus high-value farther context only', () => {
  const nodes = [
    { id: 'focus', distance: 0, elucidatoryValue: 0 },
    { id: 'near', distance: 1, elucidatoryValue: 0.1 },
    { id: 'far-useful', distance: 4, elucidatoryValue: 0.95 },
    { id: 'far-noise', distance: 4, elucidatoryValue: 0.2 },
  ];

  const cone = buildElucidatoryCone({ nodes, baseDepth: 1, threshold: 0.8 });
  assert.deepEqual(cone.map((node) => node.id), ['focus', 'near', 'far-useful']);
});

test('adequate local projection executes without acquisition', () => {
  const outcome = resolveExplainOutcome({
    referenceResolved: true,
    capabilitySupported: true,
    disclosurePermitted: true,
    localProjectionAdequate: true,
  });

  assert.deepEqual(outcome, { status: 'execute', acquire: false, residual: null });
});

test('missing local materialisation defers with exact residual rather than global failure', () => {
  const outcome = resolveExplainOutcome({
    referenceResolved: true,
    capabilitySupported: true,
    disclosurePermitted: true,
    localProjectionAdequate: false,
    residual: 'materialise:source:mabo:1992:hca:23',
  });

  assert.deepEqual(outcome, {
    status: 'defer',
    acquire: true,
    residual: 'materialise:source:mabo:1992:hca:23',
  });
  assert.equal('globalFailure' in outcome, false);
});

test('unresolvable reference rejects explicitly', () => {
  const outcome = resolveExplainOutcome({
    referenceResolved: false,
    capabilitySupported: true,
    disclosurePermitted: true,
    localProjectionAdequate: false,
  });

  assert.deepEqual(outcome, {
    status: 'reject',
    defect: 'unresolved-reference',
  });
});

test('portable reading intents compile independently of DOM gestures', () => {
  const target = createSemanticTarget({
    spanRef: 'span:0:0:4',
    targetKind: 'role',
    surface: 'They',
    semanticRef: 'semantic:they',
    role: 'actor',
    entityRef: 'entity:team',
  });

  assert.deepEqual(compileSemanticIntent('ExplainRole', target), {
    action: 'ExplainRole',
    targetKind: 'Span',
    target: target.spanRef,
  });
  assert.deepEqual(compileSemanticIntent('ExploreEntity', target), {
    action: 'ExploreEntity',
    targetKind: 'Entity',
    target: target.entityRef,
  });
  assert.deepEqual(compileSemanticIntent('FollowReference', { referenceRef: 'reference:archive:1' }), {
    action: 'FollowReference',
    targetKind: 'Reference',
    target: 'reference:archive:1',
  });
  assert.deepEqual(compileSemanticIntent('Back', { trailRef: 'trail:previous' }), {
    action: 'Back',
    targetKind: 'Trail',
    target: 'trail:previous',
  });
});

test('Wiki and Wikidata context candidates never inherit authority or payment', () => {
  const context = createContextCandidate({
    semanticRef: 'semantic:mabo',
    qid: 'Q1124706',
    wikipediaRef: 'wiki:en:Mabo_v_Queensland_(No_2)',
    sourceRefs: ['source:mabo:1992:hca:23'],
  });

  assert.equal(context.identityCandidateOnly, true);
  assert.equal(context.legalAuthority, false);
  assert.equal(context.evidencePaid, false);
  assert.equal(context.semanticPromotion, false);
});

test('default disclosure remains reader-first and hides expert density', () => {
  assert.deepEqual(defaultSemanticDisclosure, {
    showQids: false,
    showHashes: false,
    showProofGraph: false,
    showAllResiduals: false,
    showAllSourceRoles: false,
    showTechnicalPnfLabels: false,
  });
});
