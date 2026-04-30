import type { TextDebugPayload, TextDebugSourceDocument } from '$lib/semantic/textDebug';
import type path from 'node:path';

export type SemanticCorpusConfig = {
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
