import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import {
  buildFactReviewCurrentHref,
  buildFactReviewHrefForSource,
  resolveChronologyBuckets,
  resolveFactReviewAvailableIssueFilters,
  resolveFactReviewFilteredItems,
  resolveFactReviewSourceRows,
  resolveInspectorClassification,
  resolveInspectorStatusRows,
  resolveSelectedFact,
} from '../src/lib/workbench/factReview.js';
import {
  classifyFactReviewErrorMessage,
  parseFactReviewCliPayload,
} from '../src/lib/server/factReviewCli.js';

const ROOT = new URL('..', import.meta.url);

function read(rel) {
  return readFileSync(join(ROOT.pathname, rel), 'utf8');
}

function readJson(rel) {
  return JSON.parse(read(rel));
}

test('factReview server adapter defines expected workbench and acceptance interfaces', () => {
  const s = read('src/lib/server/factReview.ts');
  assert.ok(s.includes('export interface FactReviewWorkbench'));
  assert.ok(s.includes('export interface FactReviewAcceptanceReport'));
  assert.ok(s.includes('export interface FactReviewSource'));
  assert.ok(s.includes('export interface FactReviewRecentSource'));
  assert.ok(s.includes('export interface FactReviewRun'));
  assert.ok(s.includes('export interface FactReviewIssueFilters'));
  assert.ok(s.includes('export interface FactReviewInspectorClassification'));
  assert.ok(s.includes('export interface FactReviewStoryResult'));
});

test('factReview server adapter implements robust runQuery with JSON and error validation', () => {
  const s = read('src/lib/server/factReview.ts');
  assert.ok(s.includes('async function runQuery<T>(commandArgs: string[], field: string): Promise<T>'));
  assert.ok(s.includes('parseFactReviewCliPayload<T>(raw, field)'));
});

test('factReview server adapter exported loaders are correctly typed', () => {
  const s = read('src/lib/server/factReview.ts');
  assert.ok(s.includes('export async function loadFactReviewWorkbench(selector: FactReviewSelector): Promise<FactReviewWorkbench>'));
  assert.ok(s.includes('export async function loadFactReviewAcceptance('));
  assert.ok(s.includes('Promise<FactReviewAcceptanceReport>'));
  assert.ok(s.includes('export async function listFactReviewSources(workflowKind?: string | null): Promise<FactReviewSource[]>'));
});

test('fact review route server uses SvelteKit PageServerLoad typing', () => {
  const s = read('src/routes/graphs/fact-review/+page.server.ts');
  assert.ok(s.includes("import type { PageServerLoad } from './$types';"));
  assert.ok(s.includes('export const load: PageServerLoad = async ({ url }) => {'));
  assert.ok(s.includes('Promise.allSettled'));
  assert.ok(s.includes('classifyFactReviewErrorMessage'));
});

test('fact review page consumes typed Mary-parity helpers and page data', () => {
  const s = read('src/routes/graphs/fact-review/+page.svelte');
  assert.ok(s.includes("import type { PageData } from './$types';"));
  assert.ok(s.includes('export let data: PageData;'));
  assert.ok(s.includes('buildFactReviewCurrentHref'));
  assert.ok(s.includes('resolveFactReviewAvailableIssueFilters'));
  assert.ok(s.includes('resolveFactReviewFilteredItems'));
  assert.ok(s.includes('resolveFactReviewSourceRows'));
  assert.ok(s.includes('resolveInspectorClassification'));
  assert.ok(s.includes('resolveInspectorStatusRows'));
  assert.ok(s.includes('resolveChronologyBuckets'));
});

test('fact review CLI parser accepts the real Mary wave1 demo bundle payloads', () => {
  const bundlePayload = read('tests/fixtures/fact_review_wave1_real_demo_bundle.json');
  const bundle = JSON.parse(bundlePayload);
  const workbench = parseFactReviewCliPayload(bundlePayload, 'workbench');
  const acceptance = parseFactReviewCliPayload(bundlePayload, 'acceptance');
  const sources = parseFactReviewCliPayload(bundlePayload, 'sources');

  assert.equal(workbench.run.run_id, 'factrun:e82b0742b88f1839f1b359d53f0ffa60dd1764bb5e33a98b43e2ad392892554b');
  assert.equal(acceptance.wave, 'wave1_legal');
  assert.equal(sources[2].source_label, 'wave1:real_transcript_intake_v1');
  assert.equal(bundle.selector.workflow_kind, 'transcript_semantic');
  assert.equal(bundle.selector.fixture_kind, 'real');
  assert.equal(bundle.selector.workflow_run_id, 'transcript_acceptance_real_intake_v1');
});

test('fact review CLI parser accepts the real Mary AU wave1 demo bundle payloads', () => {
  const bundlePayload = read('tests/fixtures/fact_review_wave1_real_au_demo_bundle.json');
  const bundle = JSON.parse(bundlePayload);
  const workbench = parseFactReviewCliPayload(bundlePayload, 'workbench');
  const acceptance = parseFactReviewCliPayload(bundlePayload, 'acceptance');
  const sources = parseFactReviewCliPayload(bundlePayload, 'sources');

  assert.equal(workbench.run.run_id, 'factrun:1de59c55e079ea96c0b1a4ad7f0df5635d37d963ce6b07d43a407bb442d0f6c5');
  assert.equal(acceptance.wave, 'wave1_legal');
  assert.equal(sources[1].source_label, 'wave1:real_au_procedural_v1');
  assert.equal(bundle.selector.workflow_kind, 'au_semantic');
  assert.equal(bundle.selector.fixture_kind, 'real');
  assert.equal(bundle.selector.workflow_run_id, 'run:5ab560b645ee10d0badd59fe6ef0a9442bf5d41bc57e7ff950688ae5961ef12d');
});

test('fact review real demo bundle preserves the persisted Mary selector and contract shape', () => {
  const bundle = readJson('tests/fixtures/fact_review_wave1_real_demo_bundle.json');

  assert.equal(bundle.selector.workflow_kind, bundle.workbench.reopen_navigation.query.workflow_kind);
  assert.equal(bundle.selector.workflow_run_id, bundle.workbench.reopen_navigation.query.workflow_run_id);
  assert.equal(bundle.selector.source_label, bundle.workbench.reopen_navigation.query.source_label);
  assert.ok(Array.isArray(bundle.workbench.issue_filters.available_filters));
  assert.ok(Array.isArray(bundle.workbench.operator_views.intake_triage.items));
  assert.ok(Array.isArray(bundle.sources));
});

test('SL-US-10 reopen behavior stays anchored to the real Mary transcript baseline', () => {
  const bundle = readJson('tests/fixtures/fact_review_wave1_real_demo_bundle.json');
  const sourceRows = resolveFactReviewSourceRows(bundle.workbench, bundle.sources);
  const currentHref = buildFactReviewCurrentHref(bundle.workbench, {
    workflowKind: bundle.selector.workflow_kind,
    wave: bundle.selector.wave,
    view: 'intake_triage',
  });

  assert.equal(sourceRows.length, 3);
  assert.equal(sourceRows[2].source_label, 'wave1:real_transcript_intake_v1');
  assert.equal(
    currentHref,
    '/graphs/fact-review?workflow=transcript_semantic&workflowRunId=transcript_acceptance_real_intake_v1&sourceLabel=wave1%3Areal_transcript_intake_v1&wave=wave1_legal&view=intake_triage'
  );
});

test('fact review CLI error classifier distinguishes missing runs and parse failures', () => {
  const missingRun = classifyFactReviewErrorMessage('ValueError: No fact workflow link found for transcript_semantic');
  const parseFailure = classifyFactReviewErrorMessage('Failed to parse SensibLaw CLI output as JSON: SyntaxError: Unexpected token');

  assert.equal(missingRun.kind, 'missing_run');
  assert.equal(parseFailure.kind, 'parse_error');
});

test('SL-US-09 intake triage uses canonical issue filters and grouped queue rows from the real bundle', () => {
  const bundle = readJson('tests/fixtures/fact_review_wave1_real_demo_bundle.json');
  const filters = resolveFactReviewAvailableIssueFilters(bundle.workbench, 'intake_triage');
  const missingActor = resolveFactReviewFilteredItems(bundle.workbench, 'intake_triage', 'missing_actor');
  const contradictory = resolveFactReviewFilteredItems(bundle.workbench, 'intake_triage', 'contradictory_chronology');

  assert.deepEqual(filters, ['all', 'missing_actor', 'missing_date', 'contradictory_chronology', 'procedural_significance']);
  assert.equal(missingActor.length, 1);
  assert.equal(missingActor[0].fact_id, 'fact:66bb2f25f2473baf');
  assert.equal(contradictory.length, 1);
  assert.equal(contradictory[0].fact_id, 'fact:548917ce2a38675e');
});

test('SL-US-09 chronology and contested-item reading flow stay visible in the real bundle', () => {
  const bundle = readJson('tests/fixtures/fact_review_wave1_real_demo_bundle.json');
  const chronology = resolveChronologyBuckets(bundle.workbench);
  const contestedItems = bundle.workbench.operator_views.contested_items.items;

  assert.equal(chronology.dated.length, 0);
  assert.equal(chronology.approximate.length, 0);
  assert.equal(chronology.contested.length, 1);
  assert.equal(chronology.contested[0].fact_id, 'fact:548917ce2a38675e');
  assert.equal(contestedItems.length, 1);
  assert.equal(contestedItems[0].fact_id, 'fact:548917ce2a38675e');
});

test('SL-US-11 transcript lane keeps party assertion and later annotation distinct in the inspector', () => {
  const bundle = readJson('tests/fixtures/fact_review_wave1_real_demo_bundle.json');
  const assertionFact = resolveSelectedFact(bundle.workbench, 'fact:548917ce2a38675e');
  const laterNoteFact = resolveSelectedFact(bundle.workbench, 'fact:66bb2f25f2473baf');
  const assertionStatuses = resolveInspectorStatusRows(resolveInspectorClassification(bundle.workbench, assertionFact));
  const laterStatuses = resolveInspectorStatusRows(resolveInspectorClassification(bundle.workbench, laterNoteFact));

  assert.deepEqual(
    assertionStatuses.map((row) => [row.key, row.active]),
    [
      ['party_assertion', true],
      ['procedural_outcome', false],
      ['later_annotation', false],
    ]
  );
  assert.deepEqual(
    laterStatuses.map((row) => [row.key, row.active]),
    [
      ['party_assertion', false],
      ['procedural_outcome', false],
      ['later_annotation', true],
    ]
  );
});

test('SL-US-12 through SL-US-14 keep procedural posture visible from the real transcript bundle', () => {
  const bundle = readJson('tests/fixtures/fact_review_wave1_real_demo_bundle.json');
  const proceduralItems = bundle.workbench.operator_views.procedural_posture.items;
  const proceduralFact = resolveSelectedFact(bundle.workbench, 'fact:847888989678a140');
  const proceduralStatuses = resolveInspectorStatusRows(resolveInspectorClassification(bundle.workbench, proceduralFact));

  assert.equal(proceduralItems.length, 2);
  assert.ok(proceduralItems.some((row) => row.fact_id === 'fact:847888989678a140'));
  assert.deepEqual(
    proceduralStatuses.map((row) => [row.key, row.active]),
    [
      ['party_assertion', false],
      ['procedural_outcome', true],
      ['later_annotation', false],
    ]
  );
});

test('real AU demo bundle preserves the persisted Mary selector and contract shape', () => {
  const bundle = readJson('tests/fixtures/fact_review_wave1_real_au_demo_bundle.json');

  assert.equal(bundle.selector.workflow_kind, bundle.workbench.reopen_navigation.query.workflow_kind);
  assert.equal(bundle.selector.workflow_run_id, bundle.workbench.reopen_navigation.query.workflow_run_id);
  assert.equal(bundle.selector.source_label, bundle.workbench.reopen_navigation.query.source_label);
  assert.ok(Array.isArray(bundle.workbench.issue_filters.available_filters));
  assert.ok(Array.isArray(bundle.workbench.operator_views.procedural_posture.items));
  assert.ok(Array.isArray(bundle.sources));
});

test('SL-US-12 AU real-path bundle keeps procedural posture and assertion-outcome distinction explicit', () => {
  const bundle = readJson('tests/fixtures/fact_review_wave1_real_au_demo_bundle.json');
  const proceduralItems = bundle.workbench.operator_views.procedural_posture.items;
  const appealFact = resolveSelectedFact(bundle.workbench, 'fact:44e3b170c347a29b');
  const ordersFact = resolveSelectedFact(bundle.workbench, 'fact:9d43035cc83c0c08');
  const appealStatuses = resolveInspectorStatusRows(resolveInspectorClassification(bundle.workbench, appealFact));
  const ordersStatuses = resolveInspectorStatusRows(resolveInspectorClassification(bundle.workbench, ordersFact));

  assert.equal(proceduralItems.length, 3);
  assert.ok(proceduralItems.some((row) => row.fact_id === 'fact:44e3b170c347a29b'));
  assert.ok(proceduralItems.some((row) => row.fact_id === 'fact:9d43035cc83c0c08'));
  assert.deepEqual(
    appealStatuses.map((row) => [row.key, row.active]),
    [
      ['party_assertion', true],
      ['procedural_outcome', true],
      ['later_annotation', false],
    ]
  );
  assert.deepEqual(
    ordersStatuses.map((row) => [row.key, row.active]),
    [
      ['party_assertion', false],
      ['procedural_outcome', true],
      ['later_annotation', false],
    ]
  );
});

test('SL-US-13 AU real-path bundle keeps chronology and contested-item reading flow explicit', () => {
  const bundle = readJson('tests/fixtures/fact_review_wave1_real_au_demo_bundle.json');
  const chronology = resolveChronologyBuckets(bundle.workbench);
  const noEventFacts = bundle.workbench.chronology_groups.facts_with_no_event;
  const contestedItems = bundle.workbench.operator_views.contested_items.items;

  assert.equal(chronology.dated.length, 0);
  assert.equal(chronology.approximate.length, 2);
  assert.equal(chronology.undated.length, 0);
  assert.equal(chronology.contested.length, 1);
  assert.equal(chronology.contested[0].fact_id, 'fact:44e3b170c347a29b');
  assert.equal(noEventFacts.length, 1);
  assert.equal(noEventFacts[0].fact_id, 'fact:9d43035cc83c0c08');
  assert.equal(contestedItems.length, 1);
  assert.equal(contestedItems[0].fact_id, 'fact:44e3b170c347a29b');
});

test('SL-US-14 AU real-path bundle keeps reopen and read-only procedural reconstruction anchored to the persisted selector', () => {
  const bundle = readJson('tests/fixtures/fact_review_wave1_real_au_demo_bundle.json');
  const sourceRows = resolveFactReviewSourceRows(bundle.workbench, bundle.sources);
  const currentHref = buildFactReviewCurrentHref(bundle.workbench, {
    workflowKind: bundle.selector.workflow_kind,
    wave: bundle.selector.wave,
    view: 'procedural_posture',
  });

  assert.equal(sourceRows.length, 2);
  assert.equal(sourceRows[1].source_label, 'wave1:real_au_procedural_v1');
  assert.equal(
    currentHref,
    '/graphs/fact-review?workflow=au_semantic&workflowRunId=run%3A5ab560b645ee10d0badd59fe6ef0a9442bf5d41bc57e7ff950688ae5961ef12d&sourceLabel=wave1%3Areal_au_procedural_v1&wave=wave1_legal&view=procedural_posture'
  );
  assert.ok(bundle.acceptance.stories.some((story) => story.story_id === 'SL-US-14'));
});

test('fact review CLI parser accepts the real trauma/support and handoff demo bundle payloads', () => {
  const wave3Payload = read('tests/fixtures/fact_review_wave3_real_fragmented_support_demo_bundle.json');
  const wave5Payload = read('tests/fixtures/fact_review_wave5_real_professional_handoff_demo_bundle.json');
  const wave3Bundle = JSON.parse(wave3Payload);
  const wave5Bundle = JSON.parse(wave5Payload);
  const wave3Acceptance = parseFactReviewCliPayload(wave3Payload, 'acceptance');
  const wave5Acceptance = parseFactReviewCliPayload(wave5Payload, 'acceptance');

  assert.equal(wave3Bundle.selector.wave, 'wave3_trauma_advocacy');
  assert.equal(wave3Bundle.selector.workflow_run_id, 'real_transcript_fragmented_support_v1');
  assert.equal(wave3Acceptance.wave, 'wave3_trauma_advocacy');
  assert.equal(wave5Bundle.selector.wave, 'wave5_handoff_false_coherence');
  assert.equal(wave5Bundle.selector.workflow_run_id, 'real_transcript_professional_handoff_v1');
  assert.equal(wave5Acceptance.wave, 'wave5_handoff_false_coherence');
});

test('ITIR-US-13 trauma real-path bundle keeps abstention, source distinction, and contested chronology visible', () => {
  const bundle = readJson('tests/fixtures/fact_review_wave3_real_fragmented_support_demo_bundle.json');
  const chronology = resolveChronologyBuckets(bundle.workbench);
  const traumaItems = bundle.workbench.operator_views.trauma_handoff.items;
  const abstainedFact = bundle.workbench.facts.find((fact) => fact.fact_id === 'fact:c4706bc1e1e5f402');

  assert.equal(bundle.workbench.summary.abstained_fact_count, 1);
  assert.equal(chronology.contested.length, 1);
  assert.equal(bundle.workbench.operator_views.contested_items.items.length, 1);
  assert.equal(traumaItems.length, 2);
  assert.deepEqual(abstainedFact?.source_signal_classes, ['later_annotation', 'support_worker_note']);
  assert.ok(abstainedFact?.policy_outcomes.includes('bounded_context_required'));
  assert.ok(bundle.acceptance.stories.some((story) => story.story_id === 'ITIR-US-13'));
});

test('ITIR-US-14 trauma real-path bundle keeps support handoff posture anchored to the persisted selector', () => {
  const bundle = readJson('tests/fixtures/fact_review_wave3_real_fragmented_support_demo_bundle.json');
  const sourceRows = resolveFactReviewSourceRows(bundle.workbench, bundle.sources);
  const currentHref = buildFactReviewCurrentHref(bundle.workbench, {
    workflowKind: bundle.selector.workflow_kind,
    wave: bundle.selector.wave,
    view: 'trauma_handoff',
  });

  assert.ok(bundle.workbench.operator_views.professional_handoff.items.length >= 1);
  assert.ok(bundle.workbench.operator_views.trauma_handoff.items.length >= 1);
  assert.ok(sourceRows.some((row) => row.source_label === 'wave3:real_transcript_fragmented_support_v1'));
  assert.ok(sourceRows.some((row) => row.workflow_kind === 'transcript_semantic' || row.latest_workflow_link?.workflow_kind === 'transcript_semantic'));
  assert.equal(
    currentHref,
    '/graphs/fact-review?workflow=transcript_semantic&workflowRunId=real_transcript_fragmented_support_v1&sourceLabel=wave3%3Areal_transcript_fragmented_support_v1&wave=wave3_trauma_advocacy&view=trauma_handoff'
  );
  assert.ok(bundle.acceptance.stories.some((story) => story.story_id === 'ITIR-US-14'));
});

test('ITIR-US-15 professional handoff real-path bundle preserves source boundaries and bounded context', () => {
  const bundle = readJson('tests/fixtures/fact_review_wave5_real_professional_handoff_demo_bundle.json');
  const sourceRows = resolveFactReviewSourceRows(bundle.workbench, bundle.sources);
  const therapistFact = bundle.workbench.facts.find((fact) => fact.fact_id === 'fact:2499c1b666ccd133');
  const journalFact = bundle.workbench.facts.find((fact) => fact.fact_id === 'fact:e0667b55061037f4');
  const currentHref = buildFactReviewCurrentHref(bundle.workbench, {
    workflowKind: bundle.selector.workflow_kind,
    wave: bundle.selector.wave,
    view: 'professional_handoff',
  });

  assert.equal(bundle.workbench.operator_views.professional_handoff.items.length, 2);
  assert.equal(bundle.workbench.operator_views.trauma_handoff.items.length, 2);
  assert.deepEqual(therapistFact?.source_signal_classes, ['later_annotation', 'professional_interpretation', 'professional_note']);
  assert.ok(therapistFact?.policy_outcomes.includes('preserve_source_boundary'));
  assert.deepEqual(journalFact?.source_signal_classes, ['client_account', 'user_authored']);
  assert.ok(journalFact?.policy_outcomes.includes('preserve_source_boundary'));
  assert.ok(sourceRows.some((row) => row.source_label === 'wave5:real_transcript_professional_handoff_v1'));
  assert.equal(
    currentHref,
    '/graphs/fact-review?workflow=transcript_semantic&workflowRunId=real_transcript_professional_handoff_v1&sourceLabel=wave5%3Areal_transcript_professional_handoff_v1&wave=wave5_handoff_false_coherence&view=professional_handoff'
  );
  assert.ok(bundle.acceptance.stories.some((story) => story.story_id === 'ITIR-US-15'));
});

test('ITIR-US-16 false-coherence real-path bundle keeps contradiction clusters and contested review visible', () => {
  const bundle = readJson('tests/fixtures/fact_review_wave5_real_false_coherence_demo_bundle.json');
  const falseCoherenceItems = bundle.workbench.operator_views.false_coherence_review.items;
  const contestedItems = bundle.workbench.operator_views.contested_items.items;
  const fragmentA = bundle.workbench.facts.find((fact) => fact.fact_id === 'fact:23fbeeeccea59b14');
  const supportNote = bundle.workbench.facts.find((fact) => fact.fact_id === 'fact:b4fa09470be846ce');

  assert.equal(falseCoherenceItems.length, 4);
  assert.equal(contestedItems.length, 1);
  assert.ok(fragmentA?.signal_classes.includes('contradiction_cluster'));
  assert.ok(fragmentA?.signal_classes.includes('fragmentary_account'));
  assert.ok(supportNote?.policy_outcomes.includes('bounded_context_required'));
  assert.ok(supportNote?.policy_outcomes.includes('preserve_source_boundary'));
  assert.equal(bundle.workbench.summary.review_queue_count, 4);
  assert.ok(bundle.acceptance.stories.some((story) => story.story_id === 'ITIR-US-16'));
});

test('fact review helpers prefer recent reopen rows and fall back to listed sources', () => {
  const intake = readJson('tests/fixtures/fact_review_wave1_intake.json');
  const fallback = readJson('tests/fixtures/fact_review_wave1_reopen_fallback.json');
  const recentRows = resolveFactReviewSourceRows(intake.workbench, intake.sources);
  const fallbackRows = resolveFactReviewSourceRows(fallback.workbench, fallback.sources);

  assert.equal(recentRows.length, 1);
  assert.equal(recentRows[0].source_label, 'wave1:real_transcript_intake_v1');
  assert.equal(fallbackRows.length, 1);
  assert.equal(fallbackRows[0].source_label, 'wave1:synthetic_sparse_dates_v1');
});

test('fact review helpers build reopen links from both workflow row shapes', () => {
  const intake = readJson('tests/fixtures/fact_review_wave1_intake.json');
  const fallback = readJson('tests/fixtures/fact_review_wave1_reopen_fallback.json');
  const recentHref = buildFactReviewHrefForSource(intake.workbench.reopen_navigation.recent_sources[0], {
    workflowKind: 'fact_review',
    view: 'intake_triage',
    wave: 'wave1_legal',
  });
  const fallbackHref = buildFactReviewHrefForSource(fallback.sources[0], {
    workflowKind: 'fact_review',
    view: 'chronology_prep',
  });

  assert.equal(
    recentHref,
    '/graphs/fact-review?workflow=transcript_semantic&workflowRunId=real_transcript_intake_v1&sourceLabel=wave1%3Areal_transcript_intake_v1&wave=wave1_legal&view=intake_triage'
  );
  assert.equal(
    fallbackHref,
    '/graphs/fact-review?workflow=transcript_semantic&workflowRunId=synthetic_sparse_dates_v1&sourceLabel=wave1%3Asynthetic_sparse_dates_v1&view=chronology_prep'
  );
});

test('fact review helpers build a repeatable current persisted-run href from workbench metadata', () => {
  const intake = readJson('tests/fixtures/fact_review_wave1_intake.json');
  const currentHref = buildFactReviewCurrentHref(intake.workbench, {
    workflowKind: 'fact_review',
    wave: 'wave1_legal',
    view: 'intake_triage',
  });

  assert.equal(
    currentHref,
    '/graphs/fact-review?workflow=transcript_semantic&workflowRunId=real_transcript_intake_v1&sourceLabel=wave1%3Areal_transcript_intake_v1&wave=wave1_legal&view=intake_triage'
  );
});

test('fact review helpers use canonical issue filters instead of deriving keys from group objects', () => {
  const intake = readJson('tests/fixtures/fact_review_wave1_intake.json');
  const filters = resolveFactReviewAvailableIssueFilters(intake.workbench, 'intake_triage');
  const filtered = resolveFactReviewFilteredItems(intake.workbench, 'intake_triage', 'missing_actor');

  assert.deepEqual(filters, ['all', 'missing_actor', 'contradictory_chronology']);
  assert.equal(filtered.length, 1);
  assert.equal(filtered[0].fact_id, 'fact:later-note');
});

test('fact review helpers resolve selected fact and prefer inline inspector classification before workbench fallback', () => {
  const intake = readJson('tests/fixtures/fact_review_wave1_intake.json');
  const selectedExplicit = resolveSelectedFact(intake.workbench, 'fact:later-note');
  const selectedFallback = resolveSelectedFact(intake.workbench, null);
  const explicitClassification = resolveInspectorClassification(intake.workbench, selectedExplicit);
  const fallbackClassification = resolveInspectorClassification(
    intake.workbench,
    intake.workbench.facts.find((fact) => fact.fact_id === 'fact:injury-date')
  );

  assert.equal(selectedExplicit?.fact_id, 'fact:later-note');
  assert.equal(selectedFallback?.fact_id, 'fact:injury-date');
  assert.deepEqual(explicitClassification.display_labels, ['party assertion', 'later annotation']);
  assert.deepEqual(fallbackClassification.display_labels, ['unclassified']);
});

test('fact review helpers expose distinct inspector status rows for Mary classifications', () => {
  const procedural = readJson('tests/fixtures/fact_review_wave1_procedural.json');
  const selectedFact = resolveSelectedFact(procedural.workbench, 'fact:outcome');
  const classification = resolveInspectorClassification(procedural.workbench, selectedFact);
  const statuses = resolveInspectorStatusRows(classification);

  assert.deepEqual(
    statuses.map((row) => [row.key, row.active]),
    [
      ['party_assertion', false],
      ['procedural_outcome', true],
      ['later_annotation', true],
    ]
  );
});

test('fact review helpers keep chronology buckets distinct and preserve contested chronology rows', () => {
  const chronology = readJson('tests/fixtures/fact_review_wave1_chronology.json');
  const buckets = resolveChronologyBuckets(chronology.workbench);

  assert.equal(buckets.dated.length, 1);
  assert.equal(buckets.approximate.length, 1);
  assert.equal(buckets.undated.length, 1);
  assert.equal(buckets.contested.length, 1);
  assert.equal(buckets.undatedOrContested.length, 2);
  assert.equal(buckets.contested[0].fact_id, 'fact:contested');
});
