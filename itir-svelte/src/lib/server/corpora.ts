import path from 'node:path';
import fs from 'node:fs/promises';
import os from 'node:os';
import crypto from 'node:crypto';
import { resolveItirDbPath, resolveRepoRoot } from './utils';
import { listThreads, type ThreadIndexRow } from './threadIndex';
import { resolveChatArchivePath } from './chatArchive';
import { listSemanticCorpora, loadSemanticReport } from './semanticReport';
import { loadFactReviewAcceptance, loadFactReviewWorkbench } from './factReview';
import {
  messengerQueryScript,
  openRecallQueryScript,
  factReviewQueryScript,
  resolveMessengerDbPath,
  runJsonQuery,
  readJsonFile,
  resolveLatestLiveContestedAffidavitPath
} from './corpora/transport';
import {
  normalizeAffidavitArtifacts,
  normalizeFeedbackReceipt,
  normalizeOpenRecallSummary,
  normalizePersonalRun,
  type AffidavitArtifact,
  type OpenRecallSummaryRaw
} from './corpora/normalizers';

export { resolveMessengerDbPath } from './corpora/transport';

export type CorpusCard = {
  key: string;
  label: string;
  description: string;
  href: string;
  status: 'available' | 'missing';
  detail: string;
};

export type MessengerRun = {
  run_id: string;
  created_at: string;
  source_db_path: string;
  source_db_size: number;
  sample_limit: number;
  source_namespace: string;
  source_class: string;
  retention_policy: string;
  redaction_policy: string;
  note: string | null;
  message_count: number;
  conversation_count: number;
};

export type MessengerSummary = MessengerRun & {
  first_ts: string | null;
  last_ts: string | null;
  filter_counts: Record<string, number>;
  top_conversations: Array<{
    conversation_hash: string;
    conversation_type: string;
    message_count: number;
    first_ts: string | null;
    last_ts: string | null;
    sample_sender: string | null;
  }>;
};

export type MessengerMessage = {
  run_id: string;
  row_order: number;
  conversation_hash: string;
  conversation_type: string;
  ts: string;
  sender: string;
  text: string;
};

export type OpenRecallRun = {
  import_run_id: string;
  source_db_path: string;
  storage_path: string | null;
  imported_at: string;
  source_entry_count: number;
  imported_capture_count: number;
  latest_source_timestamp: number | null;
};

export type OpenRecallCapture = {
  capture_id: string;
  import_run_id: string;
  source_db_path: string;
  source_entry_id: number | null;
  source_timestamp: number;
  captured_at: string;
  captured_date: string;
  app_name: string;
  window_title: string;
  ocr_text: string;
  screenshot_path: string | null;
  screenshot_hash: string | null;
  embedding_present: number;
  content_sha1: string;
  created_at: string;
};

export type OpenRecallSummary = {
  captureCount: number;
  uniqueAppCount: number;
  withScreenshotCount: number;
  withoutScreenshotCount: number;
  coverage: {
    withScreenshot: number;
    withoutScreenshot: number;
    coveragePercent: number;
  };
  latestCapturedAt: string | null;
  apps: Array<{ appName: string; count: number }>;
  dates: Array<{ capturedDate: string; count: number }>;
};

export type ProcessedCorpusSummary = {
  key: string;
  label: string;
  runId: string;
  summary: {
    entityCount: number;
    relationCandidateCount: number;
    promotedRelationCount: number;
    candidateOnlyRelationCount: number;
    abstainedRelationCandidateCount: number;
    unresolvedMentionCount: number;
  };
  semanticBasisCounts: Record<string, number>;
  topPredicates: Array<{ predicateKey: string; displayLabel: string; totalCount: number }>;
  href: string;
};

export type BroaderDiagnosticsSummary = {
  key: string;
  label: string;
  artifactPath: string;
  summaryLines: Array<{ label: string; value: string | number }>;
  sections: Array<{
    key: string;
    label: string;
    stats: Array<{ label: string; value: string | number }>;
  }>;
};

export type BroaderDiagnosticsDetail = {
  key: string;
  label: string;
  artifactPath: string;
  headline: Array<{ label: string; value: string | number }>;
  families?: Array<{
    key: string;
    label: string;
    stats: Array<{ label: string; value: string | number }>;
    unresolvedSurfaces?: string[];
    mentionHeavyEvents?: Array<{ eventId: string; mentionCount: number; matchCount: number; text: string }>;
  }>;
  seedDiagnostics?: Array<{
    seedId: string;
    linkageKind: string;
    actionSummary: string;
    families: Array<{
      sourceFamily: string;
      reviewStatus: string;
      matchedEventCount: number;
      candidateEventCount: number;
      supportKind: string;
      sampleEvents: Array<{ eventId: string; confidence: string; matched: boolean; receiptKinds: string[]; text: string }>;
    }>;
  }>;
  workflowSummaries?: Array<{
    workflowKind: string;
    stats: Array<{ label: string; value: string | number }>;
  }>;
  bundlePressure?: Array<{
    sourceLabel: string;
    workflowKind: string;
    bundlePath: string;
    pressureScore: number;
    contestedItemCount: number;
    reviewQueueCount: number;
    factCount: number;
    eventCount: number;
  }>;
  rawSourceBacklog?: {
    root: string;
    fileCount: number;
    filesBySuffix: Record<string, number>;
    files: string[];
  } | null;
};

export type PersonalProcessedRun = {
  sourceLabel: string;
  runId: string;
  workflowKind: string;
  workflowRunId: string;
  createdAt: string;
  notes: string;
  counts: {
    sourceCount: number;
    statementCount: number;
    factCount: number;
    observationCount: number;
    eventCount: number;
    reviewCount: number;
    contestationCount: number;
  };
  summary: Record<string, number>;
  operatorViews: string[];
  acceptanceSummary: {
    storyCount: number;
    passCount: number;
    partialCount: number;
    failCount: number;
  } | null;
  rawSourceHref: string;
  workbenchHref: string;
};

export type PersonalAffidavitResult = {
  key: string;
  label: string;
  artifactPath: string | null;
  origin: 'fixture' | 'live' | 'persisted';
  reviewRunId: string | null;
  storageBasis: 'sqlite' | 'artifact';
  affidavitPath: string;
  sourcePath: string;
  summary: {
    affidavitPropositionCount: number;
    coveredCount: number;
    partialCount: number;
    unsupportedAffidavitCount: number;
    missingReviewCount: number;
    substantiveResponseCount: number;
    affidavitSupportedRatio: number;
    substantiveResponseRatio: number;
  };
};

export type PersonalProcessedOverview = {
  runs: PersonalProcessedRun[];
  affidavits: PersonalAffidavitResult[];
};

export type FeedbackReceiptSummary = {
  receiptId: string;
  feedbackClass: string;
  roleLabel: string;
  taskLabel: string;
  targetProduct: string | null;
  targetSurface: string | null;
  workflowLabel: string | null;
  sourceKind: string;
  summary: string;
  quoteText: string;
  severity: string;
  desiredOutcome: string | null;
  sentiment: string | null;
  capturedAt: string;
  tags: string[];
  createdAt: string;
  provenance: Record<string, unknown>;
  drillInHref: string | null;
  drillInLabel: string | null;
};
type FactReviewRunsPayload = {
  runs?: Array<{
    run_id?: string;
    source_label?: string;
    created_at?: string;
    notes?: string;
    source_count?: number;
    statement_count?: number;
    fact_count?: number;
    observation_count?: number;
    event_count?: number;
    review_count?: number;
    contestation_count?: number;
    workflow_link?: {
      workflow_kind?: string;
      workflow_run_id?: string;
    };
  }>;
};

type ContestedRunsPayload = {
  runs?: Array<{
    review_run_id?: string;
    artifact_version?: string;
    fixture_kind?: string | null;
    source_kind?: string | null;
    source_label?: string | null;
    source_input_path?: string | null;
    affidavit_input_path?: string | null;
    affidavit_proposition_count?: number;
    covered_count?: number;
    partial_count?: number;
    unsupported_affidavit_count?: number;
    missing_review_count?: number;
    semantic_basis_counts?: Record<string, number>;
    created_at?: string;
  }>;
};

type ContestedSummaryPayload = {
  review?: {
    run?: {
      review_run_id?: string;
      source_kind?: string | null;
      source_label?: string | null;
      source_input_path?: string | null;
      affidavit_input_path?: string | null;
    };
    summary?: {
      affidavit_proposition_count?: number;
      covered_count?: number;
      partial_count?: number;
      unsupported_affidavit_count?: number;
      missing_review_count?: number;
      substantive_response_count?: number;
      affidavit_supported_ratio?: number;
      substantive_response_ratio?: number;
    };
  };
};

type FeedbackReceiptsPayload = {
  receipts?: Array<{
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
  }>;
};

export async function loadPersonalProcessedOverview(): Promise<PersonalProcessedOverview> {
  const repoRoot = resolveRepoRoot();
  const dbPath = resolveItirDbPath(repoRoot);
  const runsPayload = await runJsonQuery<FactReviewRunsPayload>(
    'python3',
    [factReviewQueryScript(repoRoot), '--db-path', dbPath, 'runs', '--limit', '50'],
    repoRoot
  ).catch(() => ({ runs: [] }));
  const realRunRows = (runsPayload.runs ?? []).filter((row) => String(row.source_label ?? '').includes(':real_'));
  const runs = await Promise.all(
    realRunRows.map(async (row) => {
      const base = normalizePersonalRun(row);
      const { runId, workflowKind, workflowRunId, sourceLabel } = base;
      const [workbench, acceptance] = await Promise.all([
        loadFactReviewWorkbench({ runId }).catch(() => null),
        loadFactReviewAcceptance({ runId }, { fixtureKind: 'real' }).catch(() => null)
      ]);
      return {
        ...base,
        summary: Object.fromEntries(
          Object.entries(workbench?.summary ?? {}).map(([key, value]) => [key, Number(value ?? 0) || 0])
        ),
        operatorViews: Object.keys(workbench?.operator_views ?? {}),
        acceptanceSummary: acceptance?.summary
          ? {
              storyCount: Number(acceptance.summary.story_count ?? 0) || 0,
              passCount: Number(acceptance.summary.pass_count ?? 0) || 0,
              partialCount: Number(acceptance.summary.partial_count ?? 0) || 0,
              failCount: Number(acceptance.summary.fail_count ?? 0) || 0
            }
          : null,
      } satisfies PersonalProcessedRun;
    })
  );
  runs.sort((a, b) => b.createdAt.localeCompare(a.createdAt));

  const affidavitArtifacts: AffidavitArtifact[] = [
    {
      key: 'au_narrow_affidavit',
      label: 'AU affidavit coverage',
      artifactPath: path.join(
        repoRoot,
        'SensibLaw',
        'tests',
        'fixtures',
        'zelph',
        'au_affidavit_coverage_review_v1',
        'affidavit_coverage_review_v1.json'
      ),
      origin: 'fixture'
    },
    {
      key: 'au_dense_affidavit',
      label: 'AU dense affidavit coverage',
      artifactPath: path.join(
        repoRoot,
        'SensibLaw',
        'tests',
        'fixtures',
        'zelph',
        'au_dense_affidavit_coverage_review_v1',
        'affidavit_coverage_review_v1.json'
      ),
      origin: 'fixture'
    }
  ];
  const liveContestedPath = await resolveLatestLiveContestedAffidavitPath();
  if (liveContestedPath) {
    affidavitArtifacts.unshift({
      key: 'google_docs_contested_latest',
      label: 'Dad/Johl contested narrative review',
      artifactPath: liveContestedPath,
      origin: 'live'
    });
  }

  const persistedContested = await runJsonQuery<ContestedRunsPayload>(
    'python3',
    [factReviewQueryScript(repoRoot), '--db-path', dbPath, 'contested-runs', '--limit', '20'],
    repoRoot
  ).catch(() => ({ runs: [] }));

  const affidavits: PersonalAffidavitResult[] = [];
  const seenKeys = new Set<string>();
  for (const row of persistedContested.runs ?? []) {
    const reviewRunId = String(row.review_run_id ?? '').trim();
    if (!reviewRunId) continue;
    const detail = await runJsonQuery<ContestedSummaryPayload>(
      'python3',
      [factReviewQueryScript(repoRoot), '--db-path', dbPath, 'contested-summary', '--review-run-id', reviewRunId],
      repoRoot
    ).catch(() => null);
    const run = detail?.review?.run ?? {};
    const summary = detail?.review?.summary ?? {};
    const sourceKind = String(run.source_kind ?? row.source_kind ?? '').trim();
    const sourceLabel = String(run.source_label ?? row.source_label ?? '').trim();
    const label =
      sourceKind === 'google_docs_contested_narrative'
        ? 'Dad/Johl contested narrative review'
        : sourceKind === 'au_dense_overlay_slice'
          ? 'AU dense affidavit coverage'
          : sourceKind === 'au_checked_handoff_slice'
            ? 'AU affidavit coverage'
            : sourceLabel || sourceKind || 'Persisted affidavit review';
    const key = sourceKind || sourceLabel || reviewRunId;
    seenKeys.add(key);
    affidavits.push({
      key,
      label,
      artifactPath: null,
      origin: 'persisted',
      reviewRunId,
      storageBasis: 'sqlite',
      affidavitPath: String(run.affidavit_input_path ?? row.affidavit_input_path ?? ''),
      sourcePath: String(run.source_input_path ?? row.source_input_path ?? ''),
      summary: {
        affidavitPropositionCount: Number(summary.affidavit_proposition_count ?? row.affidavit_proposition_count ?? 0) || 0,
        coveredCount: Number(summary.covered_count ?? row.covered_count ?? 0) || 0,
        partialCount: Number(summary.partial_count ?? row.partial_count ?? 0) || 0,
        unsupportedAffidavitCount: Number(summary.unsupported_affidavit_count ?? row.unsupported_affidavit_count ?? 0) || 0,
        missingReviewCount: Number(summary.missing_review_count ?? row.missing_review_count ?? 0) || 0,
        substantiveResponseCount: Number(summary.substantive_response_count ?? 0) || 0,
        affidavitSupportedRatio: Number(summary.affidavit_supported_ratio ?? 0) || 0,
        substantiveResponseRatio: Number(summary.substantive_response_ratio ?? 0) || 0
      }
    });
  }

  const artifactAffidavits = await normalizeAffidavitArtifacts(affidavitArtifacts, seenKeys);
  affidavits.push(...artifactAffidavits);

  affidavits.sort((a, b) => {
    const rank = (value: PersonalAffidavitResult['origin']) => (value === 'persisted' ? 0 : value === 'live' ? 1 : 2);
    return rank(a.origin) - rank(b.origin) || a.label.localeCompare(b.label);
  });

  return { runs, affidavits };
}

export async function loadFeedbackReceipts(limit = 20): Promise<FeedbackReceiptSummary[]> {
  const repoRoot = resolveRepoRoot();
  const dbPath = resolveItirDbPath(repoRoot);
  const payload = await runJsonQuery<FeedbackReceiptsPayload>(
    'python3',
    [factReviewQueryScript(repoRoot), '--db-path', dbPath, 'feedback-receipts', '--limit', String(limit)],
    repoRoot
  ).catch(() => ({ receipts: [] }));
  return (payload.receipts ?? []).map((row) => normalizeFeedbackReceipt(row));
}

export async function addFeedbackReceipt(
  fields: Record<string, string | string[] | Record<string, unknown> | null | undefined>
): Promise<{ receiptId: string; feedbackClass: string }> {
  const repoRoot = resolveRepoRoot();
  const dbPath = resolveItirDbPath(repoRoot);
  const args = [factReviewQueryScript(repoRoot), '--db-path', dbPath, 'feedback-add'];
  const addArg = (flag: string, value: string | null | undefined) => {
    if (value && value.trim()) args.push(flag, value.trim());
  };
  addArg('--feedback-class', typeof fields.feedbackClass === 'string' ? fields.feedbackClass : null);
  addArg('--role-label', typeof fields.roleLabel === 'string' ? fields.roleLabel : null);
  addArg('--task-label', typeof fields.taskLabel === 'string' ? fields.taskLabel : null);
  addArg('--source-kind', typeof fields.sourceKind === 'string' ? fields.sourceKind : null);
  addArg('--summary', typeof fields.summary === 'string' ? fields.summary : null);
  addArg('--quote-text', typeof fields.quoteText === 'string' ? fields.quoteText : null);
  addArg('--severity', typeof fields.severity === 'string' ? fields.severity : null);
  addArg('--captured-at', typeof fields.capturedAt === 'string' ? fields.capturedAt : null);
  addArg('--target-product', typeof fields.targetProduct === 'string' ? fields.targetProduct : null);
  addArg('--target-surface', typeof fields.targetSurface === 'string' ? fields.targetSurface : null);
  addArg('--workflow-label', typeof fields.workflowLabel === 'string' ? fields.workflowLabel : null);
  addArg('--desired-outcome', typeof fields.desiredOutcome === 'string' ? fields.desiredOutcome : null);
  addArg('--sentiment', typeof fields.sentiment === 'string' ? fields.sentiment : null);
  const tags = Array.isArray(fields.tags)
    ? fields.tags
    : typeof fields.tags === 'string'
      ? [fields.tags]
      : [];
  for (const tag of tags.map((value) => String(value).trim()).filter(Boolean)) {
    args.push('--tag', tag);
  }
  addArg('--provenance-collector', typeof fields.provenanceCollector === 'string' ? fields.provenanceCollector : null);
  addArg('--provenance-source-ref', typeof fields.provenanceSourceRef === 'string' ? fields.provenanceSourceRef : null);
  if (fields.provenanceJson && typeof fields.provenanceJson === 'object' && !Array.isArray(fields.provenanceJson)) {
    args.push('--provenance-json', JSON.stringify(fields.provenanceJson));
  }
  const raw = await runJsonQuery<{ receipt?: { receipt_id?: string; feedback_class?: string } }>('python3', args, repoRoot);
  return {
    receiptId: String(raw.receipt?.receipt_id ?? ''),
    feedbackClass: String(raw.receipt?.feedback_class ?? '')
  };
}

export async function importFeedbackReceiptsFromJsonlText(text: string): Promise<{ importedCount: number }> {
  const repoRoot = resolveRepoRoot();
  const dbPath = resolveItirDbPath(repoRoot);
  const tempPath = path.join(os.tmpdir(), `itir-feedback-import-${crypto.randomUUID()}.jsonl`);
  await fs.writeFile(tempPath, text, 'utf8');
  try {
    const payload = await runJsonQuery<{ imported_count?: number }>(
      'python3',
      [factReviewQueryScript(repoRoot), '--db-path', dbPath, 'feedback-import', '--input', tempPath],
      repoRoot
    );
    return { importedCount: Number(payload.imported_count ?? 0) || 0 };
  } finally {
    await fs.rm(tempPath, { force: true }).catch(() => undefined);
  }
}

export async function loadCorpusHome(): Promise<{
  cards: CorpusCard[];
  recentThreads: ThreadIndexRow[];
  messengerSummary: MessengerSummary | null;
  openrecallSummary: OpenRecallSummary | null;
}> {
  const repoRoot = resolveRepoRoot();
  const chatPath = resolveChatArchivePath();
  const messengerPath = resolveMessengerDbPath(repoRoot);
  const itirDbPath = resolveItirDbPath(repoRoot);

  const recentThreads = await listThreads(repoRoot, { limit: 8, offset: 0 }).then((r) => r.threads).catch(() => []);
  const messengerSummary = await loadMessengerSummary().catch(() => null);
  const openrecallSummary = await loadOpenRecallSummary().catch(() => null);

  const cards: CorpusCard[] = [
    {
      key: 'chat_archive',
      label: 'Chat archive',
      description: 'Canonical threads from the local chat archive.',
      href: '/corpora/chat-archive',
      status: recentThreads.length > 0 ? 'available' : 'missing',
      detail: chatPath
    },
    {
      key: 'messenger',
      label: 'Messenger test DB',
      description: 'Filtered Messenger rows and conversation slices from the bounded ingest DB.',
      href: '/corpora/messenger',
      status: messengerSummary ? 'available' : 'missing',
      detail: messengerPath
    },
    {
      key: 'openrecall',
      label: 'OpenRecall captures',
      description: 'Imported app/window/OCR captures from the canonical ITIR DB.',
      href: '/corpora/openrecall',
      status: openrecallSummary ? 'available' : 'missing',
      detail: itirDbPath
    },
    {
      key: 'processed',
      label: 'Processed results',
      description: 'Semantic/report outputs over the ingested corpora, including extracted relations and promotion summaries.',
      href: '/corpora/processed',
      status: 'available',
      detail: path.join(repoRoot, 'SensibLaw', '.cache_local')
    }
  ];

  return { cards, recentThreads, messengerSummary, openrecallSummary };
}

export async function loadProcessedCorpusSummaries(): Promise<ProcessedCorpusSummary[]> {
  const corpora = listSemanticCorpora();
  const rows = await Promise.all(
    corpora.map(async (corpus) => {
      const payload = await loadSemanticReport(corpus.key);
      const report = payload.report as any;
      const summary = report?.summary ?? {};
      const basisCounts = (summary?.semantic_basis_counts ?? {}) as Record<string, number>;
      const promoted = Array.isArray(report?.promoted_relations) ? report.promoted_relations : [];
      const candidateOnly = Array.isArray(report?.candidate_only_relations) ? report.candidate_only_relations : [];
      const predicateCounts = new Map<string, { displayLabel: string; totalCount: number }>();
      for (const row of [...promoted, ...candidateOnly]) {
        const key = String(row?.predicate_key ?? '').trim();
        if (!key) continue;
        const current = predicateCounts.get(key) ?? {
          displayLabel: String(row?.display_label ?? key),
          totalCount: 0
        };
        current.totalCount += 1;
        predicateCounts.set(key, current);
      }
      const topPredicates = Array.from(predicateCounts.entries())
        .map(([predicateKey, value]) => ({
          predicateKey,
          displayLabel: value.displayLabel,
          totalCount: value.totalCount
        }))
        .sort((a, b) => b.totalCount - a.totalCount || a.predicateKey.localeCompare(b.predicateKey))
        .slice(0, 8);

      return {
        key: corpus.key,
        label: corpus.label,
        runId: String(report?.run_id ?? ''),
        summary: {
          entityCount: Number(summary?.entity_count ?? 0) || 0,
          relationCandidateCount: Number(summary?.relation_candidate_count ?? 0) || 0,
          promotedRelationCount: Number(summary?.promoted_relation_count ?? 0) || 0,
          candidateOnlyRelationCount: Number(summary?.candidate_only_relation_count ?? 0) || 0,
          abstainedRelationCandidateCount: Number(summary?.abstained_relation_candidate_count ?? 0) || 0,
          unresolvedMentionCount: Number(summary?.unresolved_mention_count ?? 0) || 0
        },
        semanticBasisCounts: Object.fromEntries(
          Object.entries(basisCounts).map(([k, v]) => [k, Number(v ?? 0) || 0])
        ),
        topPredicates,
        href: `/graphs/semantic-report?source=${encodeURIComponent(corpus.key)}`
      } satisfies ProcessedCorpusSummary;
    })
  );
  return rows;
}

export async function loadBroaderDiagnosticsSummaries(): Promise<BroaderDiagnosticsSummary[]> {
  const repoRoot = resolveRepoRoot();
  const gwbCandidates = [
    '/tmp/gwb_broader_promotion_diagnostics_live/gwb_broader_promotion_diagnostics_v1.json',
    path.join(
      repoRoot,
      'SensibLaw',
      'tests',
      'fixtures',
      'zelph',
      'gwb_broader_promotion_diagnostics_v1',
      'gwb_broader_promotion_diagnostics_v1.json'
    )
  ];
  let gwbPath = '';
  for (const candidate of gwbCandidates) {
    try {
      await fs.access(candidate);
      gwbPath = candidate;
      break;
    } catch {
      // keep searching
    }
  }

  const auPath = path.join(
    repoRoot,
    'SensibLaw',
    'tests',
    'fixtures',
    'zelph',
    'au_broader_corpus_diagnostics_v1',
    'au_broader_corpus_diagnostics_v1.json'
  );

  const rows: BroaderDiagnosticsSummary[] = [];

  if (gwbPath) {
    const payload = await readJsonFile<any>(gwbPath);
    rows.push({
      key: 'gwb_broader',
      label: 'GWB broader promotion diagnostics',
      artifactPath: gwbPath,
      summaryLines: [
        { label: 'families', value: Number(payload?.summary?.source_family_count ?? 0) || 0 },
        {
          label: 'families with promoted relations',
          value: Number(payload?.summary?.families_with_promoted_relations ?? 0) || 0
        },
        {
          label: 'diagnostic seed lanes',
          value: Number(payload?.summary?.broader_seed_diagnostic_count ?? 0) || 0
        },
        { label: 'reading', value: String(payload?.summary?.core_reading ?? '') }
      ],
      sections: Array.isArray(payload?.source_family_summaries)
        ? payload.source_family_summaries.map((row: any) => ({
            key: String(row?.source_family ?? ''),
            label: String(row?.source_family ?? ''),
            stats: [
              { label: 'matched seeds', value: Number(row?.matched_seed_count ?? 0) || 0 },
              { label: 'candidate-only seeds', value: Number(row?.candidate_only_seed_count ?? 0) || 0 },
              { label: 'relation candidates', value: Number(row?.relation_candidate_count ?? 0) || 0 },
              { label: 'promoted relations', value: Number(row?.promoted_relation_count ?? 0) || 0 },
              { label: 'unresolved mentions', value: Number(row?.unresolved_mention_count ?? 0) || 0 },
              { label: 'ambiguous events', value: Number(row?.ambiguous_event_count ?? 0) || 0 }
            ]
          }))
        : []
    });
  }

  try {
    await fs.access(auPath);
    const payload = await readJsonFile<any>(auPath);
    rows.push({
      key: 'au_broader',
      label: 'AU broader corpus diagnostics',
      artifactPath: auPath,
      summaryLines: [
        { label: 'source families', value: Number(payload?.summary?.source_family_count ?? 0) || 0 },
        { label: 'workflow kinds', value: Number(payload?.summary?.workflow_kind_count ?? 0) || 0 },
        { label: 'fact count total', value: Number(payload?.summary?.fact_count_total ?? 0) || 0 },
        { label: 'reading', value: String(payload?.summary?.core_reading ?? '') }
      ],
      sections: Array.isArray(payload?.workflow_summaries)
        ? payload.workflow_summaries.map((row: any) => ({
            key: String(row?.workflow_kind ?? ''),
            label: String(row?.workflow_kind ?? ''),
            stats: Object.entries(row ?? {})
              .filter(([key]) => key !== 'workflow_kind')
              .map(([key, value]) => ({ label: key.replace(/_/g, ' '), value: typeof value === 'number' ? value : String(value ?? '') }))
          }))
        : []
    });
  } catch {
    // optional
  }

  return rows;
}

export async function loadBroaderDiagnosticsDetail(key: string): Promise<BroaderDiagnosticsDetail | null> {
  const repoRoot = resolveRepoRoot();
  if (key === 'gwb_broader') {
    const gwbCandidates = [
      '/tmp/gwb_broader_promotion_diagnostics_live/gwb_broader_promotion_diagnostics_v1.json',
      path.join(
        repoRoot,
        'SensibLaw',
        'tests',
        'fixtures',
        'zelph',
        'gwb_broader_promotion_diagnostics_v1',
        'gwb_broader_promotion_diagnostics_v1.json'
      )
    ];
    let artifactPath = '';
    for (const candidate of gwbCandidates) {
      try {
        await fs.access(candidate);
        artifactPath = candidate;
        break;
      } catch {
        // continue
      }
    }
    if (!artifactPath) return null;
    const payload = await readJsonFile<any>(artifactPath);
    return {
      key,
      label: 'GWB broader promotion diagnostics',
      artifactPath,
      headline: [
        { label: 'families', value: Number(payload?.summary?.source_family_count ?? 0) || 0 },
        {
          label: 'families with matched seed support',
          value: Number(payload?.summary?.families_with_matched_seed_support ?? 0) || 0
        },
        {
          label: 'families with promoted relations',
          value: Number(payload?.summary?.families_with_promoted_relations ?? 0) || 0
        },
        {
          label: 'core reading',
          value: String(payload?.summary?.core_reading ?? '')
        }
      ],
      families: Array.isArray(payload?.source_family_summaries)
        ? payload.source_family_summaries.map((row: any) => ({
            key: String(row?.source_family ?? ''),
            label: String(row?.source_family ?? ''),
            stats: [
              { label: 'matched seeds', value: Number(row?.matched_seed_count ?? 0) || 0 },
              { label: 'candidate-only seeds', value: Number(row?.candidate_only_seed_count ?? 0) || 0 },
              { label: 'relation candidates', value: Number(row?.relation_candidate_count ?? 0) || 0 },
              { label: 'promoted relations', value: Number(row?.promoted_relation_count ?? 0) || 0 },
              { label: 'unmatched seeds', value: Number(row?.unmatched_seed_count ?? 0) || 0 },
              { label: 'unresolved mentions', value: Number(row?.unresolved_mention_count ?? 0) || 0 },
              { label: 'ambiguous events', value: Number(row?.ambiguous_event_count ?? 0) || 0 }
            ],
            unresolvedSurfaces: Array.isArray(row?.top_unresolved_surfaces) ? row.top_unresolved_surfaces.map(String) : [],
            mentionHeavyEvents: Array.isArray(row?.mention_heavy_events)
              ? row.mention_heavy_events.map((event: any) => ({
                  eventId: String(event?.event_id ?? ''),
                  mentionCount: Number(event?.mention_count ?? 0) || 0,
                  matchCount: Number(event?.match_count ?? 0) || 0,
                  text: String(event?.text ?? '')
                }))
              : []
          }))
        : [],
      seedDiagnostics: Array.isArray(payload?.seed_diagnostics)
        ? payload.seed_diagnostics.map((row: any) => ({
            seedId: String(row?.seed_id ?? ''),
            linkageKind: String(row?.linkage_kind ?? ''),
            actionSummary: String(row?.action_summary ?? ''),
            families: Array.isArray(row?.families)
              ? row.families.map((family: any) => ({
                  sourceFamily: String(family?.source_family ?? ''),
                  reviewStatus: String(family?.review_status ?? ''),
                  matchedEventCount: Number(family?.matched_event_count ?? 0) || 0,
                  candidateEventCount: Number(family?.candidate_event_count ?? 0) || 0,
                  supportKind: String(family?.support_kind ?? ''),
                  sampleEvents: Array.isArray(family?.sample_events)
                    ? family.sample_events.map((event: any) => ({
                        eventId: String(event?.event_id ?? ''),
                        confidence: String(event?.confidence ?? ''),
                        matched: Boolean(event?.matched),
                        receiptKinds: Array.isArray(event?.receipt_kinds) ? event.receipt_kinds.map(String) : [],
                        text: String(event?.text ?? '')
                      }))
                    : []
                }))
              : []
          }))
        : []
    };
  }

  if (key === 'au_broader') {
    const artifactPath = path.join(
      repoRoot,
      'SensibLaw',
      'tests',
      'fixtures',
      'zelph',
      'au_broader_corpus_diagnostics_v1',
      'au_broader_corpus_diagnostics_v1.json'
    );
    try {
      await fs.access(artifactPath);
    } catch {
      return null;
    }
    const payload = await readJsonFile<any>(artifactPath);
    const backlog = payload?.raw_source_backlog ?? {};
    return {
      key,
      label: 'AU broader corpus diagnostics',
      artifactPath,
      headline: [
        { label: 'source families', value: Number(payload?.summary?.source_family_count ?? 0) || 0 },
        { label: 'workflow kinds', value: Number(payload?.summary?.workflow_kind_count ?? 0) || 0 },
        { label: 'fact count total', value: Number(payload?.summary?.fact_count_total ?? 0) || 0 },
        { label: 'core reading', value: String(payload?.summary?.core_reading ?? '') }
      ],
      workflowSummaries: Array.isArray(payload?.workflow_summaries)
        ? payload.workflow_summaries.map((row: any) => ({
            workflowKind: String(row?.workflow_kind ?? ''),
            stats: Object.entries(row ?? {})
              .filter(([field]) => field !== 'workflow_kind')
              .map(([field, value]) => ({ label: field.replace(/_/g, ' '), value: typeof value === 'number' ? value : String(value ?? '') }))
          }))
        : [],
      bundlePressure: Array.isArray(payload?.bundle_pressure_inventory)
        ? payload.bundle_pressure_inventory.map((row: any) => ({
            sourceLabel: String(row?.source_label ?? ''),
            workflowKind: String(row?.workflow_kind ?? ''),
            bundlePath: String(row?.bundle_path ?? ''),
            pressureScore: Number(row?.pressure_score ?? 0) || 0,
            contestedItemCount: Number(row?.contested_item_count ?? 0) || 0,
            reviewQueueCount: Number(row?.review_queue_count ?? 0) || 0,
            factCount: Number(row?.fact_count ?? 0) || 0,
            eventCount: Number(row?.event_count ?? 0) || 0
          }))
        : [],
      rawSourceBacklog: {
        root: String(backlog?.root ?? ''),
        fileCount: Number(backlog?.file_count ?? 0) || 0,
        filesBySuffix: Object.fromEntries(Object.entries(backlog?.files_by_suffix ?? {}).map(([k, v]) => [k, Number(v ?? 0) || 0])),
        files: Array.isArray(backlog?.files) ? backlog.files.map(String) : []
      }
    };
  }

  return null;
}

export async function loadChatArchiveOverview(): Promise<{
  q: string;
  limit: number;
  offset: number;
  threads: ThreadIndexRow[];
}> {
  const repoRoot = resolveRepoRoot();
  return await listThreads(repoRoot, { limit: 200, offset: 0 });
}

export async function loadMessengerRuns(): Promise<MessengerRun[]> {
  const repoRoot = resolveRepoRoot();
  const dbPath = resolveMessengerDbPath(repoRoot);
  const payload = await runJsonQuery<{ runs: MessengerRun[] }>(
    'python3',
    [messengerQueryScript(repoRoot), '--db-path', dbPath, 'runs', '--limit', '20'],
    repoRoot
  );
  return payload.runs ?? [];
}

export async function loadMessengerSummary(runId?: string | null): Promise<MessengerSummary | null> {
  const repoRoot = resolveRepoRoot();
  const dbPath = resolveMessengerDbPath(repoRoot);
  const args = [messengerQueryScript(repoRoot), '--db-path', dbPath, 'summary'];
  if (runId) args.push('--run-id', runId);
  const payload = await runJsonQuery<{ summary: MessengerSummary | null }>('python3', args, repoRoot);
  return payload.summary ?? null;
}

export async function loadMessengerMessages(opts: {
  runId?: string | null;
  conversationHash?: string | null;
  textQuery?: string | null;
  limit?: number;
}): Promise<{ runId: string | null; messages: MessengerMessage[] }> {
  const repoRoot = resolveRepoRoot();
  const dbPath = resolveMessengerDbPath(repoRoot);
  const args = [messengerQueryScript(repoRoot), '--db-path', dbPath, 'messages', '--limit', String(opts.limit ?? 120)];
  if (opts.runId) args.push('--run-id', opts.runId);
  if (opts.conversationHash) args.push('--conversation-hash', opts.conversationHash);
  if (opts.textQuery) args.push('--text-query', opts.textQuery);
  const payload = await runJsonQuery<{ run_id: string | null; messages: MessengerMessage[] }>('python3', args, repoRoot);
  return { runId: payload.run_id ?? null, messages: payload.messages ?? [] };
}

export async function loadOpenRecallRuns(): Promise<OpenRecallRun[]> {
  const repoRoot = resolveRepoRoot();
  const dbPath = resolveItirDbPath(repoRoot);
  const payload = await runJsonQuery<{ runs: OpenRecallRun[] }>(
    'python3',
    [openRecallQueryScript(repoRoot), '--itir-db-path', dbPath, 'runs', '--limit', '20'],
    repoRoot
  );
  return payload.runs ?? [];
}

export async function loadOpenRecallSummary(opts: {
  importRunId?: string | null;
  date?: string | null;
  appName?: string | null;
} = {}): Promise<OpenRecallSummary | null> {
  const repoRoot = resolveRepoRoot();
  const dbPath = resolveItirDbPath(repoRoot);
  const args = [openRecallQueryScript(repoRoot), '--itir-db-path', dbPath, 'summary'];
  if (opts.importRunId) args.push('--import-run-id', opts.importRunId);
  if (opts.date) args.push('--date', opts.date);
  if (opts.appName) args.push('--app-name', opts.appName);
  const payload = await runJsonQuery<{ summary: OpenRecallSummaryRaw | null }>('python3', args, repoRoot);
  return normalizeOpenRecallSummary(payload.summary ?? null);
}

export async function loadOpenRecallCaptures(opts: {
  importRunId?: string | null;
  date?: string | null;
  appName?: string | null;
  textQuery?: string | null;
  limit?: number;
}): Promise<OpenRecallCapture[]> {
  const repoRoot = resolveRepoRoot();
  const dbPath = resolveItirDbPath(repoRoot);
  const args = [openRecallQueryScript(repoRoot), '--itir-db-path', dbPath, 'captures', '--limit', String(opts.limit ?? 80)];
  if (opts.importRunId) args.push('--import-run-id', opts.importRunId);
  if (opts.date) args.push('--date', opts.date);
  if (opts.appName) args.push('--app-name', opts.appName);
  if (opts.textQuery) args.push('--text-query', opts.textQuery);
  const payload = await runJsonQuery<{ captures: OpenRecallCapture[] }>('python3', args, repoRoot);
  return payload.captures ?? [];
}
