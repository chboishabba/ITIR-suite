export const UNIFIED_WORKBENCH_STAGE_KEYS = [
  'journal',
  'timeline',
  'handoff',
  'matter_proof',
  'research',
];

function selectedFact(workbench, selectedFactId) {
  const facts = Array.isArray(workbench?.facts) ? workbench.facts : [];
  return facts.find((fact) => fact?.fact_id === selectedFactId) ?? facts[0] ?? null;
}

function hasItems(view) {
  return Array.isArray(view?.items) && view.items.length > 0;
}

function stage(key, label, status, reason, payload = {}) {
  return { key, label, status, reason, ...payload };
}

export function buildUnifiedWorkbenchProjection(workbench, options = {}) {
  const fact = selectedFact(workbench, options.selectedFactId);
  const operatorViews = workbench?.operator_views ?? {};
  const chronology = workbench?.chronology_groups ?? {};
  const legalGraph = workbench?.legal_follow_graph ?? null;

  const selectedSourceIds = Array.isArray(fact?.source_ids) ? fact.source_ids : [];
  const selectedStatementIds = Array.isArray(fact?.statement_ids) ? fact.statement_ids : [];

  const journalStage = fact
    ? stage(
        'journal',
        'Journal',
        'available',
        'Selected fact remains anchored to its persisted source/statement lineage.',
        {
          fact_id: fact.fact_id,
          label: fact.label ?? null,
          source_ids: selectedSourceIds,
          statement_ids: selectedStatementIds,
          review_status: fact.latest_review_status ?? null,
          needs_review: Boolean(fact.needs_review),
        }
      )
    : stage('journal', 'Journal', 'unavailable', 'No fact is available in the current workbench.');

  const dated = Array.isArray(chronology.dated_events) ? chronology.dated_events : [];
  const approximate = Array.isArray(chronology.approximate_events) ? chronology.approximate_events : [];
  const undated = Array.isArray(chronology.undated_events) ? chronology.undated_events : [];
  const contested = Array.isArray(chronology.contested_chronology_items)
    ? chronology.contested_chronology_items
    : [];
  const noEvent = Array.isArray(chronology.facts_with_no_event) ? chronology.facts_with_no_event : [];
  const selectedChronologyRow = [...dated, ...approximate, ...undated, ...contested, ...noEvent].find(
    (row) => row?.fact_id === fact?.fact_id
  );

  const timelineStage = selectedChronologyRow
    ? stage(
        'timeline',
        'Timeline',
        selectedChronologyRow?.chronology_bucket === 'no_event' ? 'blocked' : 'available',
        selectedChronologyRow?.chronology_bucket === 'no_event'
          ? 'The selected fact has no assembled event yet; chronology remains unresolved rather than inferred.'
          : 'The selected fact has an explicit chronology projection.',
        {
          fact_id: fact?.fact_id ?? null,
          chronology_bucket: selectedChronologyRow?.chronology_bucket ?? null,
          chronology_label: selectedChronologyRow?.chronology_label ?? null,
          event_ids: selectedChronologyRow?.event_ids ?? [],
        }
      )
    : stage(
        'timeline',
        'Timeline',
        fact ? 'blocked' : 'unavailable',
        fact
          ? 'No chronology row exists for the selected fact; the workbench does not fabricate one.'
          : 'No selected fact is available.'
      );

  const handoffView = operatorViews.professional_handoff ?? null;
  const handoffItems = Array.isArray(handoffView?.items) ? handoffView.items : [];
  const selectedHandoff = handoffItems.find((item) => item?.fact_id === fact?.fact_id) ?? null;
  const handoffStage = handoffView
    ? stage(
        'handoff',
        'Handoff',
        selectedHandoff ? 'available' : 'blocked',
        selectedHandoff
          ? 'The selected fact participates in the persisted professional-handoff projection.'
          : 'A handoff view exists, but this selected fact is not currently included in it.',
        {
          fact_id: fact?.fact_id ?? null,
          item: selectedHandoff,
          scope_receipt: options.scopeReceipt ?? null,
        }
      )
    : stage(
        'handoff',
        'Handoff',
        'unavailable',
        'The current workbench has no professional-handoff projection.'
      );

  const graphNodes = Array.isArray(legalGraph?.nodes) ? legalGraph.nodes : [];
  const graphEdges = Array.isArray(legalGraph?.edges) ? legalGraph.edges : [];
  const matterProofStage = legalGraph && (graphNodes.length > 0 || graphEdges.length > 0)
    ? stage(
        'matter_proof',
        'Matter / Proof',
        'available',
        'A persisted legal-follow graph is available for proof inspection.',
        {
          graph_summary: legalGraph.summary ?? null,
          node_count: graphNodes.length,
          edge_count: graphEdges.length,
        }
      )
    : stage(
        'matter_proof',
        'Matter / Proof',
        'unavailable',
        'No legal proof graph is attached to this workbench; personal/handoff state is not promoted into legal applicability.'
      );

  const authorityFollow = operatorViews.authority_follow ?? null;
  const contestedItems = operatorViews.contested_items ?? null;
  const reviewQueue = Array.isArray(workbench?.review_queue) ? workbench.review_queue : [];
  const researchPressureCount =
    (Array.isArray(authorityFollow?.queue) ? authorityFollow.queue.length : 0) +
    (hasItems(contestedItems) ? contestedItems.items.length : 0) +
    reviewQueue.length;

  const researchStage = researchPressureCount > 0
    ? stage(
        'research',
        'Research',
        'available',
        'The persisted workbench exposes unresolved review/follow pressure.',
        {
          pressure_count: researchPressureCount,
          authority_follow_count: Array.isArray(authorityFollow?.queue) ? authorityFollow.queue.length : 0,
          contested_count: hasItems(contestedItems) ? contestedItems.items.length : 0,
          review_queue_count: reviewQueue.length,
        }
      )
    : stage(
        'research',
        'Research',
        'unavailable',
        'No unresolved review/follow pressure is exposed by the current workbench.'
      );

  const stages = [
    journalStage,
    timelineStage,
    handoffStage,
    matterProofStage,
    researchStage,
  ];

  return {
    version: 'itir.unified_workbench.v0_1',
    selected_fact_id: fact?.fact_id ?? null,
    stages,
    stage_by_key: Object.fromEntries(stages.map((item) => [item.key, item])),
    invariant: {
      shared_world_only: true,
      derived_projection_only: true,
      creates_semantic_authority: false,
      creates_claim_truth: false,
    },
  };
}

export function nextUnifiedWorkbenchStage(projection, currentKey) {
  const stages = Array.isArray(projection?.stages) ? projection.stages : [];
  const index = stages.findIndex((item) => item?.key === currentKey);
  if (index < 0) return stages[0] ?? null;
  return stages[index + 1] ?? null;
}
