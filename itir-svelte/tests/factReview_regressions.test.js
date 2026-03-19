import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import {
  buildFactReviewHrefForSource,
  resolveChronologyBuckets,
  resolveFactReviewAvailableIssueFilters,
  resolveFactReviewFilteredItems,
  resolveFactReviewSourceRows,
  resolveInspectorClassification,
  resolveSelectedFact,
} from '../src/lib/workbench/factReview.js';

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
  assert.ok(s.includes('JSON.parse(raw)'));
  assert.ok(s.includes('if (!payload.ok)'));
  assert.ok(s.includes('if (!(field in payload))'));
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
});

test('fact review page consumes typed Mary-parity helpers and page data', () => {
  const s = read('src/routes/graphs/fact-review/+page.svelte');
  assert.ok(s.includes("import type { PageData } from './$types';"));
  assert.ok(s.includes('export let data: PageData;'));
  assert.ok(s.includes('resolveFactReviewAvailableIssueFilters'));
  assert.ok(s.includes('resolveFactReviewFilteredItems'));
  assert.ok(s.includes('resolveFactReviewSourceRows'));
  assert.ok(s.includes('resolveInspectorClassification'));
  assert.ok(s.includes('resolveChronologyBuckets'));
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
