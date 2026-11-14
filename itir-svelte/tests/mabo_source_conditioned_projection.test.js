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

const paidRadicalTitleSource = Object.freeze({
  semanticRef: 'mabo:proposition:radical-title-native-title',
  sourceRevisionRef: 'source-revision:mabo:1992:hca:23:wikisource:page-39:2026-06-22',
  spanRef: 'span:mabo:brennan:radical-title:no-automatic-beneficial-ownership',
  exactAuthoritySpanPaid: true,
  propositionChainPaid: false,
  claimTruthPaid: false,
  applicabilityPaid: false,
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

test('PG-paid radical-title span flips only the authority Source action to execute', () => {
  const specimen = createSourceConditionedMaboSpecimen({
    corpusEvidence,
    readerPayments: [paidRadicalTitleSource],
  });
  const authorityStage = specimen.stages.find((stage) => stage.role === 'authority-proposition');
  const otherStages = specimen.stages.filter((stage) => stage.role !== 'authority-proposition');

  assert.equal(authorityStage.exactAuthorityReady, true);
  assert.equal(authorityStage.sourceRevisionRef, paidRadicalTitleSource.sourceRevisionRef);
  assert.equal(authorityStage.sourceSpanRef, paidRadicalTitleSource.spanRef);
  assert.equal(authorityStage.proofPaid, false);
  assert.deepEqual(authorityStage.actionAvailability.source, { status: 'execute' });
  assert.deepEqual(authorityStage.actionAvailability.why, {
    status: 'defer',
    residual: 'mabo:residual:detailed-proposition-chain',
  });
  assert.deepEqual(compileReadingIntent(authorityStage, 'source'), {
    action: 'OpenSource',
    targetKind: 'Source',
    target: 'source:mabo:1992:hca:23',
  });
  assert.deepEqual(compileReadingIntent(authorityStage, 'why'), {
    action: 'Defer',
    targetKind: 'Residual',
    target: 'mabo:residual:detailed-proposition-chain',
    requestedIntent: 'why',
  });
  assert.ok(otherStages.every((stage) => stage.exactAuthorityReady === false));
});

test('reader payment cannot upgrade source when truth/applicability flags are smuggled in', () => {
  assert.throws(
    () => createSourceConditionedMaboSpecimen({
      corpusEvidence,
      readerPayments: [{ ...paidRadicalTitleSource, claimTruthPaid: true }],
    }),
    /reader source payment cannot carry claim truth or applicability/,
  );
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
