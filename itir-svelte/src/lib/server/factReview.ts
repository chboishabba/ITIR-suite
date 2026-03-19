import path from 'node:path';
import { spawn } from 'node:child_process';
import { parseFactReviewCliPayload } from '$lib/server/factReviewCli.js';

export type FactReviewSelector = {
  runId?: string | null;
  workflowKind?: string | null;
  workflowRunId?: string | null;
  sourceLabel?: string | null;
};

export interface FactReviewWorkflowLink {
  workflow_kind?: string;
  workflow_run_id?: string;
  fact_run_id?: string;
}

export interface FactReviewRun {
  run_id: string;
  source_label: string;
  workflow_link?: FactReviewWorkflowLink;
  contract_version: string;
}

export interface FactReviewSource {
  source_id: string;
  source_order: number;
  source_type: string;
  source_label: string;
  provenance: Record<string, unknown>;
  latest_workflow_link?: FactReviewWorkflowLink;
  run_count?: number;
}

export interface FactReviewRecentSource {
  source_label: string;
  workflow_kind?: string;
  workflow_run_id?: string;
  fact_run_id?: string;
  run_count?: number;
  latest_workflow_link?: FactReviewWorkflowLink;
}

export interface FactReviewIssueFilter {
  filter_key: string;
  label: string;
  count: number;
  fact_ids: string[];
}

export interface FactReviewIssueFilters {
  default_filter: string;
  available_filters: string[];
  filters: FactReviewIssueFilter[];
  summary: Record<string, number>;
}

export interface FactReviewInspectorClassification {
  status_keys: Record<string, boolean>;
  dominant_label: string;
  display_labels: string[];
}

export interface FactReviewFact {
  fact_id: string;
  canonical_label?: string;
  fact_text?: string;
  candidate_status?: string;
  event_ids?: string[];
  statement_ids?: string[];
  excerpt_ids?: string[];
  signal_classes?: string[];
  source_signal_classes?: string[];
  latest_review_note?: string | null;
  inspector_classification?: FactReviewInspectorClassification;
  observations?: Array<{
    predicate_key?: string;
    object_text?: string;
  }>;
  source_types?: string[];
  statement_roles?: string[];
}

export interface FactReviewStatement {
  statement_id: string;
  statement_text: string;
}

export interface FactReviewExcerpt {
  excerpt_id: string;
  excerpt_text: string;
}

export interface FactReviewEvent {
  event_id: string;
  event_type?: string;
  primary_actor?: string;
  time_start?: string | null;
  label?: string;
}

export interface FactReviewChronologyRow {
  fact_id?: string;
  event_id?: string;
  event_type?: string;
  primary_actor?: string;
  time_start?: string | null;
  label?: string;
}

export interface FactReviewViewItem {
  fact_id: string;
  label?: string;
  latest_review_status?: string | null;
  candidate_status?: string | null;
  contestation_count?: number | null;
  reason_labels?: string[];
  primary_contested_reason_text?: string | null;
  signal_classes?: string[];
  source_signal_classes?: string[];
}

export interface FactReviewOperatorView {
  title: string;
  summary?: Record<string, number>;
  groups?: Record<string, FactReviewViewItem[] | FactReviewEvent[]>;
  items?: FactReviewViewItem[];
}

export interface FactReviewWorkbench {
  run: FactReviewRun;
  summary: Record<string, number>;
  sources: FactReviewSource[];
  facts: FactReviewFact[];
  events: FactReviewEvent[];
  statements: FactReviewStatement[];
  excerpts: FactReviewExcerpt[];
  review_queue: FactReviewViewItem[];
  chronology_summary: Record<string, number>;
  chronology_groups: Record<string, FactReviewChronologyRow[]>;
  contested_summary: Record<string, unknown>;
  operator_views: Record<string, FactReviewOperatorView>;
  reopen_navigation: {
    current: {
      run_id?: string;
      source_label?: string;
      workflow_kind?: string;
      workflow_run_id?: string;
    };
    query: {
      workflow_kind?: string;
      workflow_run_id?: string;
      source_label?: string;
    };
    recent_sources: FactReviewRecentSource[];
  };
  issue_filters: FactReviewIssueFilters;
  inspector_classification: {
    status_order: string[];
    selected_fact_id?: string | null;
    facts: Record<string, FactReviewInspectorClassification>;
  };
  inspector_defaults: {
    selected_fact_id?: string | null;
    default_view: string;
  };
}

export interface FactReviewStoryCheck {
  check_id: string;
  passed: boolean;
  explanation?: string;
}

export interface FactReviewStoryResult {
  story_id: string;
  label: string;
  status: 'pass' | 'fail' | 'partial';
  check_count: number;
  passed_check_count: number;
  failed_check_ids: string[];
  gap_tags: string[];
  blocking_explanation?: string | null;
  checks: FactReviewStoryCheck[];
}

export interface FactReviewAcceptanceReport {
  version: string;
  wave: string;
  fixture_kind: string;
  run: {
    run_id?: string;
    source_label?: string;
    workflow_link?: FactReviewWorkflowLink;
  };
  summary: {
    story_count: number;
    pass_count: number;
    partial_count: number;
    fail_count: number;
  };
  stories: FactReviewStoryResult[];
}

function resolveRepoRoot(): string {
  return path.resolve('..');
}

function resolveItirDbPath(repoRoot: string): string {
  const raw = process.env.ITIR_DB_PATH?.trim() || '.cache_local/itir.sqlite';
  return path.resolve(repoRoot, raw);
}

function queryScriptPath(repoRoot: string): string {
  return path.join(repoRoot, 'SensibLaw', 'scripts', 'query_fact_review.py');
}

async function readStdout(cmd: string, args: string[], cwd: string): Promise<string> {
  return await new Promise<string>((resolve, reject) => {
    const child = spawn(cmd, args, { cwd });
    let stdout = '';
    let stderr = '';
    child.stdout.on('data', (d) => (stdout += d.toString()));
    child.stderr.on('data', (d) => (stderr += d.toString()));
    child.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`${cmd} ${args.join(' ')} failed with ${code}\n${stderr || stdout}`));
      } else {
        resolve(stdout);
      }
    });
  });
}

function selectorArgs(selector: FactReviewSelector): string[] {
  const args: string[] = [];
  if (selector.runId) args.push('--run-id', selector.runId);
  if (selector.workflowKind) args.push('--workflow-kind', selector.workflowKind);
  if (selector.workflowRunId) args.push('--workflow-run-id', selector.workflowRunId);
  if (selector.sourceLabel) args.push('--source-label', selector.sourceLabel);
  return args;
}

async function runQuery<T>(commandArgs: string[], field: string): Promise<T> {
  const repoRoot = resolveRepoRoot();
  const raw = await readStdout(
    'python3',
    [queryScriptPath(repoRoot), '--db-path', resolveItirDbPath(repoRoot), ...commandArgs],
    repoRoot
  );
  return parseFactReviewCliPayload<T>(raw, field);
}

export async function loadFactReviewWorkbench(selector: FactReviewSelector): Promise<FactReviewWorkbench> {
  return await runQuery<FactReviewWorkbench>([...selectorArgs(selector), 'workbench'], 'workbench');
}

export async function loadFactReviewAcceptance(
  selector: FactReviewSelector,
  opts: { wave?: string; fixtureKind?: string } = {}
): Promise<FactReviewAcceptanceReport> {
  return await runQuery<FactReviewAcceptanceReport>(
    [
      ...selectorArgs(selector),
      'acceptance',
      '--wave',
      opts.wave ?? 'all',
      '--fixture-kind',
      opts.fixtureKind ?? 'unknown'
    ],
    'acceptance'
  );
}

export async function listFactReviewSources(workflowKind?: string | null): Promise<FactReviewSource[]> {
  const args = ['sources'];
  if (workflowKind) args.push('--workflow-kind', workflowKind);
  return await runQuery<FactReviewSource[]>(args, 'sources');
}
