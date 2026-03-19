import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';

const ROOT = new URL('..', import.meta.url);

function read(rel) {
  return readFileSync(join(ROOT.pathname, rel), 'utf8');
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

test('fact review page consumes canonical issue filters and typed page data', () => {
  const s = read('src/routes/graphs/fact-review/+page.svelte');
  assert.ok(s.includes("import type { PageData } from './$types';"));
  assert.ok(s.includes('export let data: PageData;'));
  assert.ok(s.includes("data.workbench?.issue_filters?.available_filters ?? ['all']"));
  assert.ok(!s.includes("Object.keys(issueGroups).filter"));
});

test('fact review page prefers reopen navigation rows and supports both source-link shapes', () => {
  const s = read('src/routes/graphs/fact-review/+page.svelte');
  assert.ok(s.includes('type FactReviewSourceRow = FactReviewSource | FactReviewRecentSource;'));
  assert.ok(s.includes('reopenNavigation?.recent_sources ?? data.sources ?? []'));
  assert.ok(s.includes("source?.latest_workflow_link?.workflow_kind ?? source?.workflow_kind ?? data.workflowKind"));
  assert.ok(s.includes("source?.latest_workflow_link?.workflow_run_id ?? source?.workflow_run_id ?? null"));
});

test('fact review page resolves inspector classification from selected fact first, then workbench map', () => {
  const s = read('src/routes/graphs/fact-review/+page.svelte');
  assert.ok(s.includes('selectedFact?.inspector_classification'));
  assert.ok(s.includes("data.workbench?.inspector_classification?.facts?.[selectedFact?.fact_id ?? '']"));
  assert.ok(s.includes('Inspector classification'));
});
