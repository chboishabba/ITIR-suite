import test from 'node:test';
import assert from 'node:assert/strict';
import { buildGraphGate, buildTokenArcDebug, normalizeReviewedLinkage } from '../src/lib/server/semantic-report/analytics.ts';
import { parseReport } from '../src/lib/server/semantic-report/payload.ts';
import { buildCorrectionRecord, CorrectionValidationError, parseCorrectionForm } from '../src/lib/server/semantic-report/corrections.ts';

function sampleReport(overrides: Partial<Record<string, unknown>> = {}) {
  return {
    run_id: 'rid',
    summary: {
      entity_count: 0,
      relation_candidate_count: 0,
      promoted_relation_count: 0,
      candidate_only_relation_count: 0,
      abstained_relation_candidate_count: 0,
      unresolved_mention_count: 0
    },
    promoted_relations: [],
    candidate_only_relations: [],
    unresolved_mentions: [],
    ...overrides
  };
}

test('parseReport accepts valid semantic payload', () => {
  const payload = sampleReport();
  const actual = parseReport(JSON.stringify(payload));
  assert.strictEqual(actual.run_id, payload.run_id);
});

test('parseReport rejects invalid payload', () => {
  assert.throws(() => parseReport('{}'), (error: Error) => error.message.includes('Invalid semantic report payload'));
});

test('buildGraphGate enables when thresholds are satisfied', () => {
  const report = sampleReport({
    summary: {
      entity_count: 5,
      relation_candidate_count: 10,
      promoted_relation_count: 4,
      candidate_only_relation_count: 6,
      abstained_relation_candidate_count: 0,
      unresolved_mention_count: 0
    },
    promoted_relations: [
      {
        candidate_id: 1,
        event_id: 'e1',
        predicate_key: 'p1',
        display_label: 'P1',
        promotion_status: 'promoted',
        confidence_tier: 'high',
        subject: { entity_id: 1, entity_kind: 'person', canonical_key: 'sub', canonical_label: 'Sub' },
        object: { entity_id: 2, entity_kind: 'person', canonical_key: 'obj', canonical_label: 'Obj' },
        receipts: []
      }
    ],
    candidate_only_relations: [
      {
        candidate_id: 2,
        event_id: 'e2',
        predicate_key: 'p2',
        display_label: 'P2',
        promotion_status: 'candidate',
        confidence_tier: 'low',
        subject: { entity_id: 3, entity_kind: 'person', canonical_key: 'sub2', canonical_label: 'Sub2' },
        object: { entity_id: 4, entity_kind: 'person', canonical_key: 'obj2', canonical_label: 'Obj2' },
        receipts: []
      },
      {
        candidate_id: 3,
        event_id: 'e3',
        predicate_key: 'p2',
        display_label: 'P2',
        promotion_status: 'candidate',
        confidence_tier: 'low',
        subject: { entity_id: 3, entity_kind: 'person', canonical_key: 'sub2', canonical_label: 'Sub2' },
        object: { entity_id: 4, entity_kind: 'person', canonical_key: 'obj2', canonical_label: 'Obj2' },
        receipts: []
      }
    ]
  });

  const gate = buildGraphGate(report);
  assert.ok(gate.enabled);
});

test('normalizeReviewedLinkage respects gwb linkage', () => {
  const report = sampleReport({
    gwb_us_law_linkage: {
      ambiguous_events: [{ event_id: 'e', matches: [] }],
      per_seed: [{ seed_id: 's', matched_count: 0, candidate_count: 0 }],
      unmatched_seed_ids: ['u']
    }
  });
  const linkage = normalizeReviewedLinkage(report);
  assert.strictEqual(linkage?.label, 'Reviewed U.S.-law seed coverage');
});

test('buildTokenArcDebug falls back when no text debug exists', () => {
  const report = sampleReport();
  const tokenDebug = buildTokenArcDebug(report);
  assert.deepStrictEqual(tokenDebug, {
    events: [],
    unavailableReason: 'No text-rich semantic events with defensible token anchors are available for this corpus yet.'
  });
});

function buildCorrectionForm(overrides: Record<string, string> = {}) {
  const form = new FormData();
  form.set('source', overrides.source ?? 'gwb');
  form.set('runId', overrides.runId ?? 'run-1');
  form.set('corpusLabel', overrides.corpusLabel ?? 'Corpus');
  form.set('eventId', overrides.eventId ?? 'event-1');
  form.set('relationId', overrides.relationId ?? 'rel-1');
  form.set('anchorKey', overrides.anchorKey ?? 'anchor');
  form.set('actionKind', overrides.actionKind ?? 'promote');
  form.set('proposedPredicateKey', overrides.proposedPredicateKey ?? 'pred');
  form.set('replacementLabel', overrides.replacementLabel ?? 'Pred');
  form.set('note', overrides.note ?? 'note');
  form.set('evidencePayload', overrides.evidencePayload ?? '[]');
  return form;
}

test('parseCorrectionForm validates required inputs', () => {
  const form = buildCorrectionForm({ evidencePayload: '' });
  assert.throws(() => parseCorrectionForm(form), (error: Error) => error.message === 'Missing required correction fields.');
});

test('parseCorrectionForm rejects invalid evidence JSON', () => {
  const form = buildCorrectionForm({ evidencePayload: 'truthy' });
  assert.throws(
    () => parseCorrectionForm(form),
    (error: Error) => error instanceof CorrectionValidationError && error.message === 'Correction evidence payload was not valid JSON.'
  );
});

test('buildCorrectionRecord produces stable metadata when options provided', () => {
  const form = buildCorrectionForm();
  const fields = parseCorrectionForm(form);
  const record = buildCorrectionRecord(fields, { createdAt: '2024-01-01T00:00:00.000Z', submissionTimestamp: 123 });
  assert.strictEqual(record.correction_submission_id, 'corr:gwb:123');
  assert.strictEqual(record.created_at, '2024-01-01T00:00:00.000Z');
});
