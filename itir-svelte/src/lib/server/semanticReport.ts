import { resolveRepoRoot, resolveItirDbPath, readStdout } from './utils';
import type { TextDebugPayload, TextDebugSourceDocument } from '$lib/semantic/textDebug';
import path from 'node:path';

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
  source_documents?: TextDebugSourceDocument[];
  text_debug?: TextDebugPayload;
  review_summary?: {
    predicate_counts?: Record<string, Record<string, number>>;
    top_cue_surfaces?: Record<string, Array<[string, number]>>;
    family_counts?: Record<string, number>;
    text_debug?: {
      event_count?: number;
      relation_count?: number;
      excluded_relation_count?: number;
      unavailable_reason?: string | null;
    };
    event_counts?: Record<string, number>;
    focus_candidate_only_note?: string | null;
    summary?: Record<string, number>;
  };
  mission_observer?: {
    summary?: {
      mission_count?: number;
      followup_count?: number;
      linked_followup_count?: number;
      abstained_followup_count?: number;
      overlay_count?: number;
    };
    missions?: Array<{
      missionId: string;
      nodeKind: string;
      topicLabel: string;
      normalizedTopic: string;
      status: string;
      confidence: string;
      sourceId: string;
      sourceEventIds: string[];
      deadline?: string | null;
      owners?: Array<{ entityId?: number; label: string }>;
    }>;
    followups?: Array<{
      eventId: string;
      sourceId: string;
      speaker?: string | null;
      followupTopic: string;
      resolvedMissionId?: string | null;
      resolvedTopicLabel?: string | null;
      targetEventId?: string | null;
      status: string;
      confidence: string;
      deadline?: string | null;
    }>;
    sb_observer_overlays?: Array<Record<string, unknown>>;
    unavailableReason?: string | null;
  };
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

function validateReport(report: any): report is SemanticReportPayload {
  if (!report || typeof report !== 'object') return false;
  if (typeof report.run_id !== 'string') return false;
  if (!report.summary || typeof report.summary !== 'object') return false;
  return true;
}

function parseReport(raw: string): SemanticReportPayload {
  let report: any;
  try {
    report = JSON.parse(raw);
  } catch (e) {
    throw new Error(`Failed to parse semantic report JSON: ${e}\nRaw output: ${raw.slice(0, 500)}`);
  }

  if (!validateReport(report)) {
    throw new Error(`Invalid semantic report payload: missing required 'run_id' or 'summary' fields.`);
  }

  return report;
}

function buildTokenArcDebug(report: SemanticReportPayload): TextDebugPayload {
  return (
    report.text_debug ?? {
      events: [],
      unavailableReason: 'No text-rich semantic events with defensible token anchors are available for this corpus yet.'
    }
  );
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
