import path from 'node:path';
import { resolveRepoRoot, resolveItirDbPath, readStdout } from '../utils';
import type {
  SemanticComparisonPayload,
  SemanticComparisonSnapshot,
  SemanticCorpusConfig,
  SemanticReportPayload
} from './types';
import { normalizeReviewedLinkage, buildTokenArcDebug, topPredicates, buildGraphGate, buildHcaPredicateGraph } from './analytics.ts';
import { parseReport } from './payload.ts';

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

export function listSemanticCorpora(): Array<{ key: string; label: string }> {
  return Object.values(SEMANTIC_CORPORA).map((item) => ({ key: item.key, label: item.label }));
}

export async function loadSemanticReport(source: string): Promise<{
  source: string;
  label: string;
  report: SemanticReportPayload;
  reviewedLinkage: ReturnType<typeof normalizeReviewedLinkage>;
  tokenArcDebug: ReturnType<typeof buildTokenArcDebug>;
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
    .sort(
      (a, b) =>
        Math.abs(b.delta_hca_minus_gwb) - Math.abs(a.delta_hca_minus_gwb) ||
        b.hca_total - a.hca_total ||
        a.predicate_key.localeCompare(b.predicate_key)
    )
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
