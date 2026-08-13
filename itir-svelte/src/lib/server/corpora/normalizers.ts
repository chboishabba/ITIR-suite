import { deriveFeedbackDrillIn, buildFactReviewHref, buildRawSourceHref } from './navigation';
import { readJsonFile } from './transport';
import type {
  FeedbackReceiptSummary,
  OpenRecallSummary,
  PersonalAffidavitResult,
  PersonalProcessedRun
} from '../corpora';

export type OpenRecallSummaryRaw = {
  captureCount?: number;
  firstCapturedAt?: string | null;
  lastCapturedAt?: string | null;
  screenshotCoverage?: {
    withScreenshot?: number;
    withoutScreenshot?: number;
    coveragePercent?: number;
  };
  countsByApp?: Array<{ appName?: string; captureCount?: number }>;
  countsByDate?: Array<{ capturedDate?: string; captureCount?: number }>;
};

type FeedbackReceiptRow = {
  receipt_id?: string;
  feedback_class?: string;
  role_label?: string;
  task_label?: string;
  target_product?: string | null;
  target_surface?: string | null;
  workflow_label?: string | null;
  source_kind?: string;
  summary?: string;
  quote_text?: string;
  severity?: string;
  desired_outcome?: string | null;
  sentiment?: string | null;
  captured_at?: string;
  tags?: string[];
  provenance?: Record<string, unknown>;
  created_at?: string;
};

export type AffidavitArtifact = {
  key: string;
  label: string;
  artifactPath: string;
  origin: 'fixture' | 'live';
};

export function normalizeOpenRecallSummary(summary: OpenRecallSummaryRaw | null): OpenRecallSummary | null {
  if (!summary) return null;
  const apps = Array.isArray(summary.countsByApp)
    ? summary.countsByApp.map((row) => ({
        appName: String(row.appName ?? ''),
        count: Number(row.captureCount ?? 0) || 0
      }))
    : [];
  const coverage = {
    withScreenshot: Number(summary.screenshotCoverage?.withScreenshot ?? 0) || 0,
    withoutScreenshot: Number(summary.screenshotCoverage?.withoutScreenshot ?? 0) || 0,
    coveragePercent: Number(summary.screenshotCoverage?.coveragePercent ?? 0) || 0
  };
  return {
    captureCount: Number(summary.captureCount ?? 0) || 0,
    uniqueAppCount: apps.length,
    withScreenshotCount: coverage.withScreenshot,
    withoutScreenshotCount: coverage.withoutScreenshot,
    coverage,
    latestCapturedAt: summary.lastCapturedAt ?? null,
    apps,
    dates: Array.isArray(summary.countsByDate)
      ? summary.countsByDate.map((row) => ({
          capturedDate: String(row.capturedDate ?? ''),
          count: Number(row.captureCount ?? 0) || 0
        }))
      : []
  };
}

export function normalizeFeedbackReceipt(row: FeedbackReceiptRow): FeedbackReceiptSummary {
  const drillIn = deriveFeedbackDrillIn(row);
  return {
    ...(() => ({ drillInHref: drillIn.href, drillInLabel: drillIn.label }))(),
    receiptId: String(row.receipt_id ?? ''),
    feedbackClass: String(row.feedback_class ?? ''),
    roleLabel: String(row.role_label ?? ''),
    taskLabel: String(row.task_label ?? ''),
    targetProduct: row.target_product ? String(row.target_product) : null,
    targetSurface: row.target_surface ? String(row.target_surface) : null,
    workflowLabel: row.workflow_label ? String(row.workflow_label) : null,
    sourceKind: String(row.source_kind ?? ''),
    summary: String(row.summary ?? ''),
    quoteText: String(row.quote_text ?? ''),
    severity: String(row.severity ?? ''),
    desiredOutcome: row.desired_outcome ? String(row.desired_outcome) : null,
    sentiment: row.sentiment ? String(row.sentiment) : null,
    capturedAt: String(row.captured_at ?? ''),
    tags: Array.isArray(row.tags) ? row.tags.map((value) => String(value)) : [],
    provenance: row.provenance && typeof row.provenance === 'object' ? row.provenance : {},
    createdAt: String(row.created_at ?? '')
  };
}

export function normalizePersonalRun(row: {
  source_label?: string;
  workflow_link?: { workflow_kind?: string; workflow_run_id?: string };
  run_id?: string;
  created_at?: string;
  notes?: string;
  source_count?: number;
  statement_count?: number;
  fact_count?: number;
  observation_count?: number;
  event_count?: number;
  review_count?: number;
  contestation_count?: number;
}): PersonalProcessedRun {
  const sourceLabel = String(row.source_label ?? '');
  const workflowKind = String(row.workflow_link?.workflow_kind ?? '');
  const workflowRunId = String(row.workflow_link?.workflow_run_id ?? '');
  const runId = String(row.run_id ?? '');
  return {
    sourceLabel,
    runId,
    workflowKind,
    workflowRunId,
    createdAt: String(row.created_at ?? ''),
    notes: String(row.notes ?? ''),
    counts: {
      sourceCount: Number(row.source_count ?? 0) || 0,
      statementCount: Number(row.statement_count ?? 0) || 0,
      factCount: Number(row.fact_count ?? 0) || 0,
      observationCount: Number(row.observation_count ?? 0) || 0,
      eventCount: Number(row.event_count ?? 0) || 0,
      reviewCount: Number(row.review_count ?? 0) || 0,
      contestationCount: Number(row.contestation_count ?? 0) || 0
    },
    summary: {},
    operatorViews: [],
    acceptanceSummary: null,
    rawSourceHref: buildRawSourceHref(sourceLabel, workflowKind),
    workbenchHref: buildFactReviewHref({
      source_label: sourceLabel,
      workflow_kind: workflowKind,
      workflow_run_id: workflowRunId
    })
  };
}

export async function normalizeAffidavitArtifacts(
  artifacts: AffidavitArtifact[],
  seenKeys: Set<string>
): Promise<PersonalAffidavitResult[]> {
  const results: PersonalAffidavitResult[] = [];
  for (const artifact of artifacts) {
    try {
      const payload = await readJsonFile<any>(artifact.artifactPath);
      const sourceKind = String(payload?.source_input?.source_kind ?? '').trim();
      const sourceLabel = String(payload?.source_input?.source_label ?? '').trim();
      const dedupeKey = sourceKind || sourceLabel || artifact.key;
      if (seenKeys.has(dedupeKey)) continue;
      const summary = payload?.summary ?? {};
      results.push({
        key: artifact.key,
        label: artifact.label,
        artifactPath: artifact.artifactPath,
        origin: artifact.origin,
        reviewRunId: null,
        storageBasis: 'artifact',
        affidavitPath: String(payload?.affidavit_input?.path ?? ''),
        sourcePath: String(payload?.source_input?.path ?? ''),
        summary: {
          affidavitPropositionCount: Number(summary?.affidavit_proposition_count ?? 0) || 0,
          coveredCount: Number(summary?.covered_count ?? 0) || 0,
          partialCount: Number(summary?.partial_count ?? 0) || 0,
          unsupportedAffidavitCount: Number(summary?.unsupported_affidavit_count ?? 0) || 0,
          missingReviewCount: Number(summary?.missing_review_count ?? 0) || 0,
          substantiveResponseCount: Number(summary?.substantive_response_count ?? 0) || 0,
          affidavitSupportedRatio: Number(summary?.affidavit_supported_ratio ?? 0) || 0,
          substantiveResponseRatio: Number(summary?.substantive_response_ratio ?? 0) || 0
        }
      });
    } catch {
      // optional artifact
    }
  }
  return results;
}
