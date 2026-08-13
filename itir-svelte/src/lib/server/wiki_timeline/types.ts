export type AooActor = {
  label: string;
  resolved: string;
  role: string;
  source: string;
};

export type AooObject = {
  title: string;
  source: string;
  resolver_hints?: Array<{
    lane: string;
    kind: string;
    title: string;
    score: number;
  }>;
};

export type AooCitation = {
  text: string;
  kind?: string;
  source?: string;
  targets?: number[];
  follower_order?: string[];
  follow?: Array<Record<string, unknown>>;
};

export type AooSlReference = {
  lane: string;
  authority?: string;
  ref_kind?: string;
  ref_value?: string;
  text?: string;
  source_document_json?: string;
  source_pdf?: string;
  provision_stable_id?: string;
  rule_atom_stable_id?: string;
  follower_order?: string[];
  follow?: Array<Record<string, unknown>>;
};

export type AooNegation = {
  kind: string;
  scope?: string;
  source?: string;
};

export type AooTimelineFact = {
  fact_id: string;
  event_id: string;
  step_index?: number;
  anchor: { year: number; month: number | null; day: number | null; precision: string; text: string; kind: string };
  party?: string;
  subjects?: string[];
  action?: string | null;
  negation?: AooNegation;
  objects?: string[];
  numeric_objects?: string[];
  purpose?: string | null;
  text?: string;
  prev_fact_ids?: string[];
  next_fact_ids?: string[];
  chain_kinds?: string[];
};

export type AooPropositionArgument = {
  role: string;
  value: string;
};

export type AooProposition = {
  proposition_id: string;
  event_id: string;
  proposition_kind: string;
  predicate_key: string;
  negation?: AooNegation;
  source_fact_id?: string;
  source_signal?: string;
  anchor_text?: string;
  arguments?: AooPropositionArgument[];
  receipts?: Array<{ kind: string; value: string }>;
};

export type AooPropositionLink = {
  link_id: string;
  event_id: string;
  source_proposition_id: string;
  target_proposition_id: string;
  link_kind: string;
  receipts?: Array<{ kind: string; value: string }>;
};

export type SpanCandidate = {
  span_id: string;
  event_id: string;
  span: { kind: string; start: number; end: number; revision_id?: string };
  text: string;
  span_type: string;
  recurrence?: { seen_events: number };
  hygiene?: {
    token_count?: number;
    is_time_expression?: boolean;
    overlaps_resolved_entity?: boolean;
    view_score?: number;
  };
};

export type AooEvent = {
  event_id: string;
  anchor: { year: number; month: number | null; day: number | null; precision: string; text: string; kind: string };
  section: string;
  text: string;
  actors: AooActor[];
  action: string | null;
  action_meta?: {
    surface?: string;
    tense?: string | null;
    aspect?: string | null;
    verb_form?: string | null;
    voice?: string | null;
    source?: string;
  };
  action_surface?: string | null;
  negation?: AooNegation;
  steps?: Array<{
    action: string;
    action_meta?: {
      surface?: string;
      tense?: string | null;
      aspect?: string | null;
      verb_form?: string | null;
      voice?: string | null;
      source?: string;
    };
    action_surface?: string | null;
    negation?: AooNegation;
    subjects: string[];
    entity_objects?: string[];
    numeric_objects?: string[];
    modifier_objects?: string[];
    objects: string[];
    purpose: string | null;
  }>;
  chains?: Array<{
    from_step?: number;
    to_step?: number;
    to?: string;
    kind: string;
  }>;
  objects: AooObject[];
  entity_objects?: string[];
  numeric_objects?: string[];
  modifier_objects?: string[];
  citations?: AooCitation[];
  sl_references?: AooSlReference[];
  party?: string;
  party_source?: string;
  party_evidence?: string[];
  toc_context?: Array<{ node_type?: string; identifier?: string; title?: string; path?: string }>;
  legal_section_markers?: {
    citation_prefixes?: string[];
    sl_reference_lanes?: string[];
    provision_stable_ids?: string[];
    rule_atom_stable_ids?: string[];
  };
  timeline_facts?: AooTimelineFact[];
  purpose: string | null;
  span_candidates?: SpanCandidate[];
  warnings: string[];
};

export type WikiTimelineAooPayload = {
  root_actor: { label: string; surname: string };
  events: AooEvent[];
  fact_timeline?: AooTimelineFact[];
  propositions?: AooProposition[];
  proposition_links?: AooPropositionLink[];
  parser?: any;
  source_entity?: unknown;
  extraction_record?: unknown;
  extraction_profile?: unknown;
  requester_coverage?: unknown;
  source_timeline?: unknown;
  generated_at?: string;
  run_id?: string;
  __loaded_from_db?: boolean;
};
