import assert from 'node:assert/strict';
import test from 'node:test';

import {
  MABO_CANONICAL_CORPUS_REF,
  createSourceConditionedMaboSpecimen,
  resolveMaboStageAction,
} from '../src/lib/workbench/maboSourceProjection.js';
import { compileReadingIntent } from '../src/lib/workbench/readingSurface.js';

const corpusEvidence = Object.freeze({
  corpusRef: MABO_CANONICAL_CORPUS_REF,
  citation: 'Mabo v Queensland (No 2) [1992] HCA 23',
  court: 'High Court of Australia',
  date: '1992-06-03',
  body: 'The High Court recognised native title in Australia and rejected the doctrine of terra nullius.',
});

test('canonical corpus pays only the coarse Mabo coordinates it actually states', () => {
  const specimen = createSourceConditionedMaboSpecimen({ corpusEvidence });

  assert.equal(specimen.sourceBasis.corpusRef, MABO_CANONICAL_CORPUS_REF);
  assert.equal(specimen.sourceBasis.recognisedNativeTitle, true);
  assert.equal(specimen.sourceBasis.rejectedTerraNullius, true);
  assert.equal(specimen.sourceBasis.paysExactRadicalTitleSpan, false);
  assert.equal(specimen.sourceBasis.paysDetailedFiveStageChain, false);
  assert.equal(specimen.stages.length, 5);
});

test('unpaid exact-authority stages defer instead of inventing paragraph/span support', () => {
  const specimen = createSourceConditionedMaboSpecimen({ corpusEvidence });
  const authorityStage = specimen.stages.find((stage) => stage.role === 'authority-proposition');

  assert.equal(authorityStage.exactAuthorityReady, false);
  assert.equal(authorityStage.sourceSpanRef, null);
  assert.equal(authorityStage.sourceRevisionRef, null);
  assert.deepEqual(resolveMaboStageAction(authorityStage, 'source'), {
    status: 'defer',
    residual: 'mabo:residual:exact-authority-span',
    requestedSourceRef: 'source:mabo:1992:hca:23',
  });
});

test('stage publishes generic action availability so ReadingSurface cannot bypass the residual', () => {
  const specimen = createSourceConditionedMaboSpecimen({ corpusEvidence });
  const authorityStage = specimen.stages.find((stage) => stage.role === 'authority-proposition');

  assert.deepEqual(authorityStage.actionAvailability.source, {
    status: 'defer',
    residual: 'mabo:residual:exact-authority-span',
  });
  assert.deepEqual(authorityStage.actionAvailability.why, {
    status: 'defer',
    residual: 'mabo:residual:detailed-proposition-chain',
  });
  assert.deepEqual(compileReadingIntent(authorityStage, 'source'), {
    action: 'Defer',
    targetKind: 'Residual',
    target: 'mabo:residual:exact-authority-span',
    requestedIntent: 'source',
  });
});

test('reader prose remains visible while machine/source depth stays query-indexed', () => {
  const specimen = createSourceConditionedMaboSpecimen({ corpusEvidence });

  assert.equal(specimen.defaultView, 'explain');
  assert.equal(specimen.graphVisibleByDefault, false);
  assert.equal(specimen.contextVisibleByDefault, false);
  assert.equal(specimen.showQidsByDefault, false);
  assert.equal(specimen.showHashesByDefault, false);
  assert.ok(specimen.lead.length > 0);
  assert.ok(specimen.stages.every((stage) => stage.summary.length > 0));
});

test('canonical corpus mismatch fails closed rather than welding the wrong source object', () => {
  assert.throws(
    () => createSourceConditionedMaboSpecimen({ corpusEvidence: { ...corpusEvidence, citation: 'Other case' } }),
    /canonical Mabo citation/,
  );
});
