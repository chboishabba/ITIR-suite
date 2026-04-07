import type { SemanticReportPayload, SemanticGraphGate, SemanticGraphPayload, SemanticPredicateSummary, SemanticRelation, SemanticReviewedLinkage } from './types.ts';

export function buildTokenArcDebug(report: SemanticReportPayload) {
  return (
    report.text_debug ?? {
      events: [],
      unavailableReason: 'No text-rich semantic events with defensible token anchors are available for this corpus yet.'
    }
  );
}

const GRAPH_GATE_THRESHOLD = {
  minPredicateTypes: 2,
  minTotalRelationCandidates: 8
} as const;

export function relationRows(report: SemanticReportPayload): SemanticRelation[] {
  const promoted = Array.isArray(report.promoted_relations) ? report.promoted_relations : [];
  const candidateOnly = Array.isArray(report.candidate_only_relations) ? report.candidate_only_relations : [];
  return [...promoted, ...candidateOnly];
}

export function topPredicates(report: SemanticReportPayload, limit = 8): SemanticPredicateSummary[] {
  const map = new Map<string, SemanticPredicateSummary>();
  for (const row of report.promoted_relations ?? []) {
    const key = String(row.predicate_key);
    const current = map.get(key) ?? {
      predicate_key: key,
      display_label: String(row.display_label || row.predicate_key || key),
      promoted_count: 0,
      candidate_only_count: 0,
      total_count: 0
    };
    current.promoted_count += 1;
    current.total_count += 1;
    map.set(key, current);
  }
  for (const row of report.candidate_only_relations ?? []) {
    const key = String(row.predicate_key);
    const current = map.get(key) ?? {
      predicate_key: key,
      display_label: String(row.display_label || row.predicate_key || key),
      promoted_count: 0,
      candidate_only_count: 0,
      total_count: 0
    };
    current.candidate_only_count += 1;
    current.total_count += 1;
    map.set(key, current);
  }
  return Array.from(map.values())
    .sort(
      (a, b) =>
        b.total_count - a.total_count ||
        b.promoted_count - a.promoted_count ||
        a.predicate_key.localeCompare(b.predicate_key)
    )
    .slice(0, Math.max(1, limit));
}

export function buildGraphGate(report: SemanticReportPayload): SemanticGraphGate {
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

export function buildHcaPredicateGraph(report: SemanticReportPayload): SemanticGraphPayload | null {
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
      const key = edgeKey(from, to);
      const current = edges.get(key) ?? { from, to, total: 0, promoted: 0, candidate: 0 };
      current.total += 1;
      if (promoted) current.promoted += 1;
      else current.candidate += 1;
      edges.set(key, current);
    }
  }

  const rank = (a: { count: number }, b: { count: number }) => b.count - a.count;
  const subjectTop = Array.from(subjects.entries()).sort((a, b) => rank(a[1], b[1])).slice(0, 16);
  const predicateTop = Array.from(predicates.entries()).sort((a, b) => rank(a[1], b[1])).slice(0, 10);
  const objectTop = Array.from(objects.entries()).sort((a, b) => rank(a[1], b[1])).slice(0, 16);
  const keep = new Set([...subjectTop.map(([id]) => id), ...predicateTop.map(([id]) => id), ...objectTop.map(([id]) => id)]);
  const scale = (count: number, max: number) => (max <= 0 ? 1 : 0.85 + (count / max) * 0.85);
  const maxS = subjectTop.length ? Math.max(...subjectTop.map(([, stat]) => stat.count)) : 1;
  const maxP = predicateTop.length ? Math.max(...predicateTop.map(([, stat]) => stat.count)) : 1;
  const maxO = objectTop.length ? Math.max(...objectTop.map(([, stat]) => stat.count)) : 1;

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

export function normalizeReviewedLinkage(report: SemanticReportPayload): SemanticReviewedLinkage | null {
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
