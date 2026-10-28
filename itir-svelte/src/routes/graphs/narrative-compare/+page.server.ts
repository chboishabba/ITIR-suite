import { loadNarrativeComparison } from '$lib/server/narrativeCompare';
import { narrativeCompareReviewState } from '$lib/workbench/reviewState';

const MACROSCOPIC_EIGEN_MOTIF_PROPERTIES = [
  'property:chboishabba:NominalModifier',
  'property:repos:NominalModifier',
  'property:dashi_agda:NominalModifier'
] as const;

const DEFAULT_MACROSCOPIC_EIGEN_MOTIF_SELECTOR = MACROSCOPIC_EIGEN_MOTIF_PROPERTIES.join('|');

type EigenMotifProperty = {
  id: string;
  namespace: string;
  property: string;
  modifier: 'NominalModifier';
};

type EigenMotifEdge = {
  id: string;
  source: string;
  target: string;
  relation: 'noTypedMeet';
};

function parseEigenMotifProperty(id: string): EigenMotifProperty {
  const parts = id.split(':');
  if (parts.length !== 3 || parts[0] !== 'property' || parts[2] !== 'NominalModifier' || !parts[1]) {
    throw new Error(`unsupported macroscopic eigen-motif property: ${id}`);
  }
  return {
    id,
    namespace: parts[1],
    property: parts[1],
    modifier: 'NominalModifier'
  };
}

function buildMacroscopicEigenMotif(selector: string) {
  const ids = selector
    .split('|')
    .map((value) => value.trim())
    .filter(Boolean);

  const uniqueIds = Array.from(new Set(ids));
  const expectedIds = [...MACROSCOPIC_EIGEN_MOTIF_PROPERTIES];
  if (
    uniqueIds.length !== expectedIds.length
    || expectedIds.some((propertyId) => !uniqueIds.includes(propertyId))
  ) {
    throw new Error('macroscopic eigen-motif selector is outside this lane typed support');
  }

  const properties = expectedIds.map(parseEigenMotifProperty);
  const edges: EigenMotifEdge[] = [];
  for (let left = 0; left < properties.length; left += 1) {
    for (let right = left + 1; right < properties.length; right += 1) {
      const source = properties[left];
      const target = properties[right];
      if (!source || !target) continue;
      edges.push({
        id: `noTypedMeet:${source.id}:${target.id}`,
        source: source.id,
        target: target.id,
        relation: 'noTypedMeet'
      });
    }
  }

  return {
    motif_id: `macroscopic-eigen-motif:${properties.map((row) => row.namespace).join('+')}:NominalModifier`,
    label: 'Macroscopic Eigen-Motif',
    selector: expectedIds.join('|'),
    properties,
    edges,
    invariants: {
      property_count: properties.length,
      pairwise_no_typed_meet_count: edges.length,
      pairwise_no_typed_meet_complete: edges.length === 3
    },
    authority: {
      candidate_only: true,
      diagnostic_only: true,
      truth: false,
      support: false,
      admissibility: false,
      runtime: false,
      promoted: false,
      routing: false,
      vector: false
    }
  };
}

export async function load({ url }: { url: URL }) {
  const selectedFixture = (url.searchParams.get('fixture') || 'friendlyjordies_demo').trim() || 'friendlyjordies_demo';
  const selectedMotif = (url.searchParams.get('motif') || DEFAULT_MACROSCOPIC_EIGEN_MOTIF_SELECTOR).trim()
    || DEFAULT_MACROSCOPIC_EIGEN_MOTIF_SELECTOR;
  const threadId = (url.searchParams.get('threadId') || '').trim() || null;
  const threadTitle = (url.searchParams.get('threadTitle') || '').trim() || null;
  const macroscopicEigenMotif = buildMacroscopicEigenMotif(selectedMotif);

  try {
    const payload = await loadNarrativeComparison(selectedFixture, { threadId, threadTitle });
    const comparisonRowCount = (payload.comparison?.shared_propositions?.length ?? 0)
      + (payload.comparison?.disputed_propositions?.length ?? 0)
      + Object.values(payload.comparison?.source_only_propositions ?? {}).reduce(
        (acc: number, rows: any) => acc + ((rows as any[])?.length ?? 0),
        0
      );
    return {
      selectedFixture,
      selectedMotif,
      macroscopicEigenMotif,
      threadId,
      threadTitle,
      fixtureMeta: payload.fixture,
      comparison: payload.comparison,
      availableFixtures: payload.availableFixtures,
      stateReason: macroscopicEigenMotif.invariants.pairwise_no_typed_meet_complete
        ? 'ready'
        : narrativeCompareReviewState(null, comparisonRowCount),
      comparisonStateReason: narrativeCompareReviewState(null, comparisonRowCount),
      error: null as string | null
    };
  } catch (e) {
    return {
      selectedFixture,
      selectedMotif,
      macroscopicEigenMotif,
      threadId,
      threadTitle,
      fixtureMeta: null,
      comparison: null,
      availableFixtures: [{ key: 'friendlyjordies_demo', label: 'FriendlyJordies public-media demo' }],
      stateReason: macroscopicEigenMotif.invariants.pairwise_no_typed_meet_complete ? 'ready' : 'load_error',
      comparisonStateReason: narrativeCompareReviewState(e instanceof Error ? e.message : String(e), 0),
      error: e instanceof Error ? e.message : String(e)
    };
  }
}
