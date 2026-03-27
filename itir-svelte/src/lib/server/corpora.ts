import path from 'node:path';
import fs from 'node:fs/promises';
import { readStdout, resolveItirDbPath, resolveRepoRoot } from './utils';
import { listThreads, type ThreadIndexRow } from './threadIndex';
import { resolveChatArchivePath } from './chatArchive';
import { listSemanticCorpora, loadSemanticReport } from './semanticReport';

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
  artifactPath: string;
  origin: 'fixture' | 'live';
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

type OpenRecallSummaryRaw = {
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

function messengerQueryScript(repoRoot: string): string {
  return path.join(repoRoot, 'itir-svelte', 'scripts', 'query_messenger_test_db.py');
}

function openRecallQueryScript(repoRoot: string): string {
  return path.join(repoRoot, 'SensibLaw', 'scripts', 'query_openrecall_import.py');
}

function factReviewQueryScript(repoRoot: string): string {
  return path.join(repoRoot, 'SensibLaw', 'scripts', 'query_fact_review.py');
}

export function resolveMessengerDbPath(repoRoot: string): string {
  const raw = process.env.ITIR_MESSENGER_DB_PATH?.trim() || process.env.MESSENGER_TEST_DB_PATH?.trim();
  return path.resolve(repoRoot, raw || '.cache_local/itir_messenger_test.sqlite');
}

async function runJsonQuery<T>(cmd: string, args: string[], cwd: string): Promise<T> {
  const raw = await readStdout(cmd, args, cwd);
  return JSON.parse(raw) as T;
}

async function readJsonFile<T>(filePath: string): Promise<T> {
  const raw = await fs.readFile(filePath, 'utf8');
  return JSON.parse(raw) as T;
}

function buildFactReviewHref(params: Record<string, string | null | undefined>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value) search.set(key, value);
  }
  return `/graphs/fact-review?${search.toString()}`;
}

function buildRawSourceHref(sourceLabel: string, workflowKind: string): string {
  if (workflowKind === 'au_semantic') {
    return '/corpora/processed/personal';
  }
  if (sourceLabel.includes('transcript')) {
    return '/corpora/processed/personal';
  }
  if (sourceLabel.includes('messenger') || sourceLabel.includes('facebook') || sourceLabel.includes('fb')) {
    return '/corpora/messenger';
  }
  if (sourceLabel.includes('chat')) {
    return '/corpora/chat-archive';
  }
  return '/corpora';
}

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

type FactReviewDemoBundle = {
  selector?: {
    source_label?: string;
  };
  acceptance?: {
    summary?: {
      story_count?: number;
      pass_count?: number;
      partial_count?: number;
      fail_count?: number;
    };
  };
  workbench?: {
    summary?: Record<string, number>;
    operator_views?: Record<string, unknown>;
  };
};

const PERSONAL_DEMO_BUNDLES: Record<string, string> = {
  'wave1:real_transcript_intake_v1': 'itir-svelte/tests/fixtures/fact_review_wave1_real_demo_bundle.json',
  'wave1:real_au_procedural_v1': 'itir-svelte/tests/fixtures/fact_review_wave1_real_au_demo_bundle.json',
  'wave3:real_transcript_fragmented_support_v1':
    'itir-svelte/tests/fixtures/fact_review_wave3_real_fragmented_support_demo_bundle.json',
  'wave5:real_transcript_professional_handoff_v1':
    'itir-svelte/tests/fixtures/fact_review_wave5_real_professional_handoff_demo_bundle.json',
  'wave5:real_transcript_false_coherence_v1':
    'itir-svelte/tests/fixtures/fact_review_wave5_real_false_coherence_demo_bundle.json'
};

async function loadPersonalDemoBundleMap(repoRoot: string): Promise<Map<string, FactReviewDemoBundle>> {
  const bundles = new Map<string, FactReviewDemoBundle>();
  for (const [sourceLabel, relativePath] of Object.entries(PERSONAL_DEMO_BUNDLES)) {
    const absolutePath = path.join(repoRoot, relativePath);
    try {
      const payload = await readJsonFile<FactReviewDemoBundle>(absolutePath);
      bundles.set(sourceLabel, payload);
    } catch {
      // optional fixture only
    }
  }
  return bundles;
}

async function resolveLatestLiveContestedAffidavitPath(): Promise<string | null> {
  try {
    const entries = await fs.readdir('/tmp', { withFileTypes: true });
    const candidates: Array<{ filePath: string; mtimeMs: number }> = [];
    for (const entry of entries) {
      if (!entry.isDirectory() || !entry.name.startsWith('google_docs_contested')) continue;
      const candidatePath = path.join('/tmp', entry.name, 'affidavit_coverage_review_v1.json');
      try {
        const stat = await fs.stat(candidatePath);
        candidates.push({ filePath: candidatePath, mtimeMs: stat.mtimeMs });
      } catch {
        // optional artifact
      }
    }
    candidates.sort((a, b) => b.mtimeMs - a.mtimeMs);
    return candidates[0]?.filePath ?? null;
  } catch {
    return null;
  }
}

export async function loadPersonalProcessedOverview(): Promise<PersonalProcessedOverview> {
  const repoRoot = resolveRepoRoot();
  const dbPath = resolveItirDbPath(repoRoot);
  const runsPayload = await runJsonQuery<FactReviewRunsPayload>(
    'python3',
    [factReviewQueryScript(repoRoot), '--db-path', dbPath, 'runs', '--limit', '50'],
    repoRoot
  ).catch(() => ({ runs: [] }));
  const demoBundles = await loadPersonalDemoBundleMap(repoRoot);

  const runs = (runsPayload.runs ?? [])
    .filter((row) => String(row.source_label ?? '').includes(':real_'))
    .map((row) => {
      const sourceLabel = String(row.source_label ?? '');
      const workflowKind = String(row.workflow_link?.workflow_kind ?? '');
      const workflowRunId = String(row.workflow_link?.workflow_run_id ?? '');
      const demo = demoBundles.get(sourceLabel);
      const acceptanceSummary = demo?.acceptance?.summary
        ? {
            storyCount: Number(demo.acceptance.summary.story_count ?? 0) || 0,
            passCount: Number(demo.acceptance.summary.pass_count ?? 0) || 0,
            partialCount: Number(demo.acceptance.summary.partial_count ?? 0) || 0,
            failCount: Number(demo.acceptance.summary.fail_count ?? 0) || 0
          }
        : null;
      return {
        sourceLabel,
        runId: String(row.run_id ?? ''),
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
        summary: Object.fromEntries(
          Object.entries(demo?.workbench?.summary ?? {}).map(([key, value]) => [key, Number(value ?? 0) || 0])
        ),
        operatorViews: Object.keys(demo?.workbench?.operator_views ?? {}),
        acceptanceSummary,
        rawSourceHref: buildRawSourceHref(sourceLabel, workflowKind),
        workbenchHref: buildFactReviewHref({
          source_label: sourceLabel,
          workflow_kind: workflowKind,
          workflow_run_id: workflowRunId
        })
      } satisfies PersonalProcessedRun;
    })
    .sort((a, b) => b.createdAt.localeCompare(a.createdAt));

  const affidavitArtifacts: Array<{ key: string; label: string; artifactPath: string; origin: 'fixture' | 'live' }> = [
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

  const affidavits: PersonalAffidavitResult[] = [];
  for (const artifact of affidavitArtifacts) {
    try {
      const payload = await readJsonFile<any>(artifact.artifactPath);
      const summary = payload?.summary ?? {};
      affidavits.push({
        key: artifact.key,
        label: artifact.label,
        artifactPath: artifact.artifactPath,
        origin: artifact.origin,
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

  return { runs, affidavits };
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
  const summary = payload.summary;
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
