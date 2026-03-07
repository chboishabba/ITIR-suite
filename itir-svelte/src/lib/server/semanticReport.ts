import path from 'node:path';
import { existsSync } from 'node:fs';
import { spawn } from 'node:child_process';
import type {
  TextDebugAnchor,
  TextDebugEvent,
  TextDebugPayload,
  TextDebugRelation,
  TextDebugToken
} from '$lib/semantic/textDebug';

type SemanticCorpusConfig = {
  key: string;
  label: string;
  script: string;
  timelineSuffix?: string;
  importSeed?: boolean;
  reportArgs?: string[];
};

export type SemanticSeedCoverage = {
  seed_id: string;
  matched_count: number;
  candidate_count: number;
};

export type SemanticReviewedLinkage = {
  label: string;
  ambiguous_events: Array<{ event_id: string; matches: unknown[] }>;
  per_seed: SemanticSeedCoverage[];
  unmatched_seeds: string[];
};

export type SemanticEntity = {
  entity_id: number;
  entity_kind: string;
  canonical_key: string;
  canonical_label: string;
};

export type SemanticRelation = {
  candidate_id: number;
  event_id: string;
  predicate_key: string;
  display_label: string;
  promotion_status: string;
  confidence_tier: string;
  subject: SemanticEntity;
  object: SemanticEntity;
  receipts: Array<{ kind: string; value: string }>;
};

export type SemanticPerEventRow = {
  event_id: string;
  text?: string;
  mentions?: Array<{
    surface_text: string;
    resolved_entity?: SemanticEntity | null;
    resolution_status?: string;
    resolution_rule?: string;
  }>;
  promoted_relations?: SemanticRelation[];
  candidate_only_relations?: SemanticRelation[];
};

export type SemanticMention = {
  event_id: string;
  cluster_id: number;
  surface_text: string;
  canonical_key_hint: string;
  resolution_status: string;
  resolution_rule: string;
  source_rule: string;
};

export type SemanticReportPayload = {
  run_id: string;
  summary: {
    entity_count: number;
    relation_candidate_count: number;
    promoted_relation_count: number;
    candidate_only_relation_count: number;
    abstained_relation_candidate_count: number;
    unresolved_mention_count: number;
  };
  promoted_relations: SemanticRelation[];
  candidate_only_relations: SemanticRelation[];
  unresolved_mentions: SemanticMention[];
  per_entity?: Array<{
    entity: SemanticEntity;
    promoted_relation_count: number;
    candidate_relation_count?: number;
  }>;
  per_event?: SemanticPerEventRow[];
  au_linkage?: {
    ambiguous_events: Array<{ event_id: string; matches: unknown[] }>;
    per_seed: Array<{ seed_id: string; matched_count: number; candidate_count: number }>;
    unmatched_seeds: string[];
  };
  gwb_us_law_linkage?: {
    ambiguous_events: Array<{ event_id: string; matches: unknown[] }>;
    per_seed: Array<{ seed_id: string; matched_count: number; candidate_count: number }>;
    unmatched_seed_ids?: string[];
    unmatched_seeds?: string[];
  };
};

export type SemanticPredicateSummary = {
  predicate_key: string;
  display_label: string;
  promoted_count: number;
  candidate_only_count: number;
  total_count: number;
};

export type SemanticComparisonSnapshot = {
  source: string;
  label: string;
  summary: SemanticReportPayload['summary'];
  reviewed?: {
    seed_count: number;
    unmatched_count: number;
    ambiguous_event_count: number;
  };
  top_predicates: SemanticPredicateSummary[];
};

export type SemanticComparisonDeltaRow = {
  predicate_key: string;
  display_label: string;
  gwb_total: number;
  hca_total: number;
  delta_hca_minus_gwb: number;
  gwb_promoted: number;
  hca_promoted: number;
};

export type SemanticGraphGate = {
  enabled: boolean;
  predicateTypeCount: number;
  totalRelationCandidates: number;
  threshold: {
    minPredicateTypes: number;
    minTotalRelationCandidates: number;
  };
};

export type SemanticGraphPayload = {
  layers: Array<{ id: string; title: string; nodes: Array<{ id: string; label: string; color?: string; tooltip?: string; scale?: number }> }>;
  edges: Array<{ from: string; to: string; label?: string; kind?: 'role' | 'sequence' | 'evidence' | 'context' }>;
};

export type SemanticComparisonPayload = {
  corpora: Record<string, SemanticComparisonSnapshot>;
  delta: {
    summary: Record<string, number>;
    predicates: SemanticComparisonDeltaRow[];
  };
  graphGate: SemanticGraphGate;
  semanticGraph: SemanticGraphPayload | null;
};

const SEMANTIC_CORPORA: Record<string, SemanticCorpusConfig> = {
  gwb: {
    key: 'gwb',
    label: 'George W. Bush',
    script: path.join('SensibLaw', 'scripts', 'gwb_semantic.py'),
    timelineSuffix: 'wiki_timeline_gwb.json'
  },
  hca: {
    key: 'hca',
    label: 'Australian HCA',
    script: path.join('SensibLaw', 'scripts', 'au_semantic.py'),
    timelineSuffix: 'wiki_timeline_hca_s942025_aoo.json',
    importSeed: true
  },
  transcript: {
    key: 'transcript',
    label: 'Transcript / freeform',
    script: path.join('SensibLaw', 'scripts', 'transcript_semantic.py'),
    reportArgs: ['report']
  }
};

function resolveRepoRoot(): string {
  const candidates = [path.resolve('.'), path.resolve('..')];
  for (const c of candidates) {
    if (existsSync(path.join(c, 'SensibLaw'))) return c;
  }
  return path.resolve('..');
}

function resolveItirDbPath(repoRoot: string): string {
  const raw = process.env.ITIR_DB_PATH?.trim() || '.cache_local/itir.sqlite';
  return path.resolve(repoRoot, raw);
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

function parseReport(raw: string): SemanticReportPayload {
  return JSON.parse(raw) as SemanticReportPayload;
}

function tokenizeEventText(text: string): TextDebugToken[] {
  const tokens: TextDebugToken[] = [];
  const re = /[A-Za-z0-9][A-Za-z0-9.'’:/-]*/g;
  let match: RegExpExecArray | null;
  let index = 0;
  while ((match = re.exec(text)) !== null) {
    tokens.push({
      index,
      text: String(match[0]),
      start: Number(match.index),
      end: Number(match.index) + String(match[0]).length
    });
    index += 1;
  }
  return tokens;
}

function escapeRegExp(text: string): string {
  return text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function normalizeSurface(text: string): string {
  return text.trim().replace(/\s+/g, ' ');
}

function findSurfaceRange(text: string, surface: string): { start: number; end: number } | null {
  const trimmed = normalizeSurface(surface);
  if (!trimmed) return null;
  const re = new RegExp(escapeRegExp(trimmed), 'i');
  const match = re.exec(text);
  if (!match || match.index < 0) return null;
  return { start: match.index, end: match.index + match[0].length };
}

function findReceiptRange(text: string, relation: SemanticRelation): { start: number; end: number; source: 'receipt' | 'label_fallback' } | null {
  const preferred = ['cue_surface', 'verb', 'role_marker', 'authority_title', 'provenance_cue'];
  for (const kind of preferred) {
    const receipt = relation.receipts.find((row) => String(row.kind) === kind && String(row.value).trim());
    if (!receipt) continue;
    const range = findSurfaceRange(text, String(receipt.value));
    if (range) return { ...range, source: 'receipt' };
  }
  const fallback = findSurfaceRange(text, String(relation.display_label || relation.predicate_key || '').replaceAll('_', ' '));
  return fallback ? { ...fallback, source: 'label_fallback' } : null;
}

function charRangeToTokenRange(
  tokens: TextDebugToken[],
  start: number,
  end: number
): { tokenStart: number; tokenEnd: number } | null {
  const overlapping = tokens.filter((token) => token.end > start && token.start < end);
  if (!overlapping.length) return null;
  return {
    tokenStart: overlapping[0]?.index ?? 0,
    tokenEnd: overlapping[overlapping.length - 1]?.index ?? 0
  };
}

function entityAnchorRange(
  text: string,
  tokens: TextDebugToken[],
  mentions: Array<{
    surface_text: string;
    resolved_entity?: SemanticEntity | null;
    resolution_status?: string;
  }>,
  entity: SemanticEntity,
  fallbackLabel: string
): { tokenStart: number; tokenEnd: number; source: 'mention' | 'label_fallback' } | null {
  const matchingMention = mentions.find(
    (mention) =>
      mention.resolution_status === 'resolved' &&
      mention.resolved_entity &&
      String(mention.resolved_entity.canonical_key) === String(entity.canonical_key)
  );
  if (matchingMention) {
    const range = findSurfaceRange(text, String(matchingMention.surface_text));
    const tokenRange = range ? charRangeToTokenRange(tokens, range.start, range.end) : null;
    if (tokenRange) return { ...tokenRange, source: 'mention' };
  }
  const fallback = findSurfaceRange(text, fallbackLabel);
  if (fallback) {
    const tokenRange = charRangeToTokenRange(tokens, fallback.start, fallback.end);
    if (tokenRange) return { ...tokenRange, source: 'label_fallback' };
  }
  const keyTail = String(entity.canonical_key).split(':').pop()?.replaceAll('_', ' ') ?? '';
  if (keyTail) {
    const keyRange = findSurfaceRange(text, keyTail);
    if (keyRange) {
      const tokenRange = charRangeToTokenRange(tokens, keyRange.start, keyRange.end);
      if (tokenRange) return { ...tokenRange, source: 'label_fallback' };
    }
  }
  return null;
}

function relationFamily(predicateKey: string): { family: string; color: string } {
  if (['ruled_by', 'challenged_in', 'subject_of_review_by', 'appealed', 'challenged', 'heard_by', 'decided_by'].includes(predicateKey)) {
    return { family: 'review', color: '#2563eb' };
  }
  if (['applied', 'followed', 'distinguished', 'held_that'].includes(predicateKey)) {
    return { family: 'authority', color: '#059669' };
  }
  if (['signed', 'vetoed', 'nominated', 'confirmed_by', 'authorized', 'funded_by', 'sanctioned'].includes(predicateKey)) {
    return { family: 'governance', color: '#d97706' };
  }
  if (['replied_to'].includes(predicateKey)) {
    return { family: 'conversation', color: '#e11d48' };
  }
  if (['felt_state'].includes(predicateKey)) {
    return { family: 'state', color: '#7c3aed' };
  }
  return { family: 'semantic', color: '#475569' };
}

function confidenceOpacity(confidenceTier: string, promotionStatus: string): number {
  const base =
    confidenceTier === 'high' ? 0.92 : confidenceTier === 'medium' ? 0.7 : confidenceTier === 'low' ? 0.42 : 0;
  return promotionStatus === 'promoted' ? base : Math.max(0.18, base * 0.82);
}

function buildTokenArcDebug(report: SemanticReportPayload): TextDebugPayload {
  const perEvent = Array.isArray(report.per_event) ? report.per_event : [];
  const events: TextDebugEvent[] = [];
  for (const event of perEvent) {
    const text = String(event.text ?? '').trim();
    if (!text) continue;
    const tokens = tokenizeEventText(text);
    if (!tokens.length) continue;
    const mentions = Array.isArray(event.mentions) ? event.mentions : [];
    const rows = [
      ...(Array.isArray(event.promoted_relations) ? event.promoted_relations : []),
      ...(Array.isArray(event.candidate_only_relations) ? event.candidate_only_relations : [])
    ];
    const relations: TextDebugRelation[] = [];
    for (const row of rows) {
      const subjectRange = entityAnchorRange(text, tokens, mentions, row.subject, String(row.subject?.canonical_label ?? ''));
      const objectRange = entityAnchorRange(text, tokens, mentions, row.object, String(row.object?.canonical_label ?? ''));
      const predicateCharRange = findReceiptRange(text, row);
      const predicateTokenRange = predicateCharRange ? charRangeToTokenRange(tokens, predicateCharRange.start, predicateCharRange.end) : null;
      const predicateRange =
        predicateCharRange && predicateTokenRange ? { ...predicateTokenRange, source: predicateCharRange.source } : null;
      const anchors: TextDebugAnchor[] = [];
      if (subjectRange) {
        anchors.push({
          key: `${row.candidate_id}:subject`,
          role: 'subject',
          label: String(row.subject?.canonical_label ?? row.subject?.canonical_key ?? 'subject'),
          source: subjectRange.source,
          tokenStart: subjectRange.tokenStart,
          tokenEnd: subjectRange.tokenEnd
        });
      }
      if (predicateRange) {
        anchors.push({
          key: `${row.candidate_id}:predicate`,
          role: 'predicate',
          label: String(row.display_label || row.predicate_key),
          source: predicateRange.source,
          tokenStart: predicateRange.tokenStart,
          tokenEnd: predicateRange.tokenEnd
        });
      }
      if (objectRange) {
        anchors.push({
          key: `${row.candidate_id}:object`,
          role: 'object',
          label: String(row.object?.canonical_label ?? row.object?.canonical_key ?? 'object'),
          source: objectRange.source,
          tokenStart: objectRange.tokenStart,
          tokenEnd: objectRange.tokenEnd
        });
      }
      if (anchors.length < 2) continue;
      const familyMeta = relationFamily(String(row.predicate_key || ''));
      relations.push({
        relationId: `${event.event_id}:${row.candidate_id}`,
        predicateKey: String(row.predicate_key || ''),
        displayLabel: String(row.display_label || row.predicate_key || ''),
        promotionStatus: String(row.promotion_status || 'candidate'),
        confidenceTier: String(row.confidence_tier || 'low'),
        family: familyMeta.family,
        color: familyMeta.color,
        opacity: confidenceOpacity(String(row.confidence_tier || 'low'), String(row.promotion_status || 'candidate')),
        anchors
      });
    }
    if (!relations.length) continue;
    events.push({
      eventId: String(event.event_id),
      text,
      tokenCount: tokens.length,
      relationCount: relations.length,
      promotedCount: relations.filter((row) => row.promotionStatus === 'promoted').length,
      tokens,
      relations
    });
  }
  return {
    events: events.slice(0, 24),
    unavailableReason: events.length ? null : 'No text-rich semantic events with defensible token anchors are available for this corpus yet.'
  };
}

const GRAPH_GATE_THRESHOLD = {
  minPredicateTypes: 2,
  minTotalRelationCandidates: 8,
} as const;

function topPredicates(report: SemanticReportPayload, limit = 8): SemanticPredicateSummary[] {
  const map = new Map<string, SemanticPredicateSummary>();
  for (const row of report.promoted_relations ?? []) {
    const k = String(row.predicate_key);
    const cur = map.get(k) ?? {
      predicate_key: k,
      display_label: String(row.display_label || row.predicate_key || k),
      promoted_count: 0,
      candidate_only_count: 0,
      total_count: 0
    };
    cur.promoted_count += 1;
    cur.total_count += 1;
    map.set(k, cur);
  }
  for (const row of report.candidate_only_relations ?? []) {
    const k = String(row.predicate_key);
    const cur = map.get(k) ?? {
      predicate_key: k,
      display_label: String(row.display_label || row.predicate_key || k),
      promoted_count: 0,
      candidate_only_count: 0,
      total_count: 0
    };
    cur.candidate_only_count += 1;
    cur.total_count += 1;
    map.set(k, cur);
  }
  return Array.from(map.values())
    .sort((a, b) => b.total_count - a.total_count || b.promoted_count - a.promoted_count || a.predicate_key.localeCompare(b.predicate_key))
    .slice(0, Math.max(1, limit));
}

function relationRows(report: SemanticReportPayload): SemanticRelation[] {
  const promoted = Array.isArray(report.promoted_relations) ? report.promoted_relations : [];
  const candidateOnly = Array.isArray(report.candidate_only_relations) ? report.candidate_only_relations : [];
  return [...promoted, ...candidateOnly];
}

function buildGraphGate(report: SemanticReportPayload): SemanticGraphGate {
  const rows = relationRows(report);
  const predicateTypeCount = new Set(rows.map((row) => String(row.predicate_key || ''))).size;
  const totalRelationCandidates = Number(report.summary?.relation_candidate_count ?? rows.length);
  return {
    enabled:
      predicateTypeCount >= GRAPH_GATE_THRESHOLD.minPredicateTypes &&
      totalRelationCandidates >= GRAPH_GATE_THRESHOLD.minTotalRelationCandidates,
    predicateTypeCount,
    totalRelationCandidates,
    threshold: {
      minPredicateTypes: GRAPH_GATE_THRESHOLD.minPredicateTypes,
      minTotalRelationCandidates: GRAPH_GATE_THRESHOLD.minTotalRelationCandidates
    }
  };
}

function buildHcaPredicateGraph(report: SemanticReportPayload): SemanticGraphPayload | null {
  const rows = relationRows(report);
  if (!rows.length) return null;
  type NodeStat = { label: string; count: number };
  type EdgeStat = { from: string; to: string; total: number; promoted: number; candidate: number };
  const subjects = new Map<string, NodeStat>();
  const predicates = new Map<string, NodeStat>();
  const objects = new Map<string, NodeStat>();
  const edges = new Map<string, EdgeStat>();
  const edgeKey = (from: string, to: string) => `${from}->${to}`;

  for (const row of rows) {
    const subjectLabel = String(row.subject?.canonical_label ?? row.subject?.canonical_key ?? 'unknown subject');
    const predicateLabel = String(row.display_label || row.predicate_key || 'unknown predicate');
    const objectLabel = String(row.object?.canonical_label ?? row.object?.canonical_key ?? 'unknown object');
    const subjectId = `sub:${String(row.subject?.canonical_key ?? subjectLabel)}`;
    const predicateId = `pred:${String(row.predicate_key || predicateLabel)}`;
    const objectId = `obj:${String(row.object?.canonical_key ?? objectLabel)}`;
    const promoted = String(row.promotion_status) === 'promoted';
    subjects.set(subjectId, { label: subjectLabel, count: (subjects.get(subjectId)?.count ?? 0) + 1 });
    predicates.set(predicateId, { label: predicateLabel, count: (predicates.get(predicateId)?.count ?? 0) + 1 });
    objects.set(objectId, { label: objectLabel, count: (objects.get(objectId)?.count ?? 0) + 1 });
    for (const [from, to] of [
      [subjectId, predicateId],
      [predicateId, objectId]
    ] as const) {
      const k = edgeKey(from, to);
      const cur = edges.get(k) ?? { from, to, total: 0, promoted: 0, candidate: 0 };
      cur.total += 1;
      if (promoted) cur.promoted += 1;
      else cur.candidate += 1;
      edges.set(k, cur);
    }
  }

  const rank = (a: { count: number }, b: { count: number }) => b.count - a.count;
  const subjectTop = Array.from(subjects.entries()).sort((a, b) => rank(a[1], b[1])).slice(0, 16);
  const predicateTop = Array.from(predicates.entries()).sort((a, b) => rank(a[1], b[1])).slice(0, 10);
  const objectTop = Array.from(objects.entries()).sort((a, b) => rank(a[1], b[1])).slice(0, 16);
  const keep = new Set([...subjectTop.map(([id]) => id), ...predicateTop.map(([id]) => id), ...objectTop.map(([id]) => id)]);
  const scale = (count: number, max: number) => (max <= 0 ? 1 : 0.85 + (count / max) * 0.85);
  const maxS = subjectTop.length ? Math.max(...subjectTop.map(([, v]) => v.count)) : 1;
  const maxP = predicateTop.length ? Math.max(...predicateTop.map(([, v]) => v.count)) : 1;
  const maxO = objectTop.length ? Math.max(...objectTop.map(([, v]) => v.count)) : 1;

  const toNode = (id: string, stat: NodeStat, color: string, max: number) => ({
    id,
    label: `${stat.label} (${stat.count})`,
    color,
    tooltip: stat.label,
    scale: scale(stat.count, max)
  });

  const filteredEdges = Array.from(edges.values())
    .filter((row) => keep.has(row.from) && keep.has(row.to))
    .sort((a, b) => b.total - a.total || a.from.localeCompare(b.from))
    .slice(0, 120)
    .map((row) => ({
      from: row.from,
      to: row.to,
      label: row.promoted && row.candidate ? `${row.promoted}P/${row.candidate}C` : `${row.total}`,
      kind: row.promoted > 0 ? ('role' as const) : ('context' as const)
    }));

  return {
    layers: [
      {
        id: 'subjects',
        title: 'Subjects',
        nodes: subjectTop.map(([id, stat]) => toNode(id, stat, '#eef2ff', maxS))
      },
      {
        id: 'predicates',
        title: 'Predicates',
        nodes: predicateTop.map(([id, stat]) => toNode(id, stat, '#dcfce7', maxP))
      },
      {
        id: 'objects',
        title: 'Objects',
        nodes: objectTop.map(([id, stat]) => toNode(id, stat, '#fef3c7', maxO))
      }
    ],
    edges: filteredEdges
  };
}

function normalizeReviewedLinkage(report: SemanticReportPayload): SemanticReviewedLinkage | null {
  if (report.gwb_us_law_linkage) {
    return {
      label: 'Reviewed U.S.-law seed coverage',
      ambiguous_events: report.gwb_us_law_linkage.ambiguous_events ?? [],
      per_seed: report.gwb_us_law_linkage.per_seed ?? [],
      unmatched_seeds: report.gwb_us_law_linkage.unmatched_seed_ids ?? report.gwb_us_law_linkage.unmatched_seeds ?? []
    };
  }
  if (report.au_linkage) {
    return {
      label: 'Reviewed Australian seed coverage',
      ambiguous_events: report.au_linkage.ambiguous_events ?? [],
      per_seed: report.au_linkage.per_seed ?? [],
      unmatched_seeds: report.au_linkage.unmatched_seeds ?? []
    };
  }
  return null;
}

export function listSemanticCorpora(): Array<{ key: string; label: string }> {
  return Object.values(SEMANTIC_CORPORA).map((item) => ({ key: item.key, label: item.label }));
}

export async function loadSemanticReport(
  source: string
): Promise<{
  source: string;
  label: string;
  report: SemanticReportPayload;
  reviewedLinkage: SemanticReviewedLinkage | null;
  tokenArcDebug: TextDebugPayload;
}> {
  const cfg = SEMANTIC_CORPORA[source] ?? SEMANTIC_CORPORA.gwb;
  if (!cfg) {
    throw new Error('semantic corpus configuration missing');
  }
  const repoRoot = resolveRepoRoot();
  const dbPath = resolveItirDbPath(repoRoot);
  if (cfg.importSeed) {
    await readStdout('python', [path.join(repoRoot, cfg.script), '--db-path', dbPath, 'import-seed'], repoRoot);
  }
  const reportArgs = cfg.reportArgs ?? ['report', '--timeline-suffix', cfg.timelineSuffix ?? ''];
  const raw = await readStdout('python', [path.join(repoRoot, cfg.script), '--db-path', dbPath, ...reportArgs], repoRoot);
  const report = parseReport(raw);
  return {
    source: cfg.key,
    label: cfg.label,
    report,
    reviewedLinkage: normalizeReviewedLinkage(report),
    tokenArcDebug: buildTokenArcDebug(report)
  };
}

export async function loadSemanticComparison(): Promise<SemanticComparisonPayload> {
  const [gwb, hca] = await Promise.all([loadSemanticReport('gwb'), loadSemanticReport('hca')]);
  const corpora: Record<string, SemanticComparisonSnapshot> = {
    gwb: {
      source: gwb.source,
      label: gwb.label,
      summary: gwb.report.summary,
      reviewed: gwb.reviewedLinkage
        ? {
            seed_count: gwb.reviewedLinkage.per_seed.length,
            unmatched_count: gwb.reviewedLinkage.unmatched_seeds.length,
            ambiguous_event_count: gwb.reviewedLinkage.ambiguous_events.length
          }
        : undefined,
      top_predicates: topPredicates(gwb.report)
    },
    hca: {
      source: hca.source,
      label: hca.label,
      summary: hca.report.summary,
      reviewed: hca.reviewedLinkage
        ? {
            seed_count: hca.reviewedLinkage.per_seed.length,
            unmatched_count: hca.reviewedLinkage.unmatched_seeds.length,
            ambiguous_event_count: hca.reviewedLinkage.ambiguous_events.length
          }
        : undefined,
      top_predicates: topPredicates(hca.report)
    }
  };
  const gwbSnapshot = corpora.gwb;
  const hcaSnapshot = corpora.hca;
  if (!gwbSnapshot || !hcaSnapshot) {
    throw new Error('semantic comparison snapshots missing');
  }

  const summaryDelta = {
    entity_count: Number(hca.report.summary.entity_count) - Number(gwb.report.summary.entity_count),
    relation_candidate_count: Number(hca.report.summary.relation_candidate_count) - Number(gwb.report.summary.relation_candidate_count),
    promoted_relation_count: Number(hca.report.summary.promoted_relation_count) - Number(gwb.report.summary.promoted_relation_count),
    candidate_only_relation_count:
      Number(hca.report.summary.candidate_only_relation_count) - Number(gwb.report.summary.candidate_only_relation_count),
    unresolved_mention_count: Number(hca.report.summary.unresolved_mention_count) - Number(gwb.report.summary.unresolved_mention_count)
  };

  const gwbPred = new Map(gwbSnapshot.top_predicates.map((row) => [row.predicate_key, row]));
  const hcaPred = new Map(hcaSnapshot.top_predicates.map((row) => [row.predicate_key, row]));
  const allPredicates = Array.from(new Set([...gwbPred.keys(), ...hcaPred.keys()]));
  const predicateDelta = allPredicates
    .map((key) => {
      const g = gwbPred.get(key);
      const h = hcaPred.get(key);
      return {
        predicate_key: key,
        display_label: h?.display_label ?? g?.display_label ?? key,
        gwb_total: Number(g?.total_count ?? 0),
        hca_total: Number(h?.total_count ?? 0),
        delta_hca_minus_gwb: Number(h?.total_count ?? 0) - Number(g?.total_count ?? 0),
        gwb_promoted: Number(g?.promoted_count ?? 0),
        hca_promoted: Number(h?.promoted_count ?? 0)
      };
    })
    .sort((a, b) => Math.abs(b.delta_hca_minus_gwb) - Math.abs(a.delta_hca_minus_gwb) || b.hca_total - a.hca_total || a.predicate_key.localeCompare(b.predicate_key))
    .slice(0, 12);

  const graphGate = buildGraphGate(hca.report);
  const semanticGraph = graphGate.enabled ? buildHcaPredicateGraph(hca.report) : null;

  return {
    corpora,
    delta: {
      summary: summaryDelta,
      predicates: predicateDelta
    },
    graphGate,
    semanticGraph
  };
}
