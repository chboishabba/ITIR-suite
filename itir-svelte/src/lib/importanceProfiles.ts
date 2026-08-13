export type ImportanceProfileId = 'none' | 'entropy_role_section_v1';

export type FactLike = {
  event_id: string;
  section?: string;
  subjects?: string[];
  objects?: string[];
};

type RoleCounts = {
  subject: number;
  object: number;
  agent: number;
  requester: number;
};

type EntityMetrics = {
  id: string;
  roles: RoleCounts;
  event_ids: Set<string>;
  sections: Map<string, { event_ids: Set<string>; roles: RoleCounts }>;
};

type CorpusMetrics = {
  entities: Map<string, EntityMetrics>;
  section_event_counts: Map<string, number>;
  corpus_event_count: number;
  section_count: number;
};

const EPS = 1e-9;

function emptyRoles(): RoleCounts {
  return { subject: 0, object: 0, agent: 0, requester: 0 };
}

function roleTotal(r: RoleCounts): number {
  return r.subject + r.object + r.agent + r.requester;
}

function safeLog(v: number): number {
  return Math.log(Math.max(EPS, v));
}

function roleEntropy(roles: RoleCounts): number {
  const total = roleTotal(roles);
  if (total <= 0) return 0;
  const probs = [roles.subject, roles.object, roles.agent, roles.requester].map((c) => c / total);
  let h = 0;
  for (const p of probs) {
    if (p <= 0) continue;
    h += -p * safeLog(p);
  }
  return h;
}

function ensureEntity(map: Map<string, EntityMetrics>, id: string): EntityMetrics {
  const k = String(id || '').trim();
  if (!k) {
    return {
      id: '',
      roles: emptyRoles(),
      event_ids: new Set<string>(),
      sections: new Map<string, { event_ids: Set<string>; roles: RoleCounts }>()
    };
  }
  let row = map.get(k);
  if (!row) {
    row = {
      id: k,
      roles: emptyRoles(),
      event_ids: new Set<string>(),
      sections: new Map<string, { event_ids: Set<string>; roles: RoleCounts }>()
    };
    map.set(k, row);
  }
  return row;
}

function ensureSectionBucket(
  sections: Map<string, { event_ids: Set<string>; roles: RoleCounts }>,
  section: string
): { event_ids: Set<string>; roles: RoleCounts } {
  const sec = String(section || '(unknown)').trim() || '(unknown)';
  let row = sections.get(sec);
  if (!row) {
    row = { event_ids: new Set<string>(), roles: emptyRoles() };
    sections.set(sec, row);
  }
  return row;
}

function buildCorpusMetrics(facts: FactLike[]): CorpusMetrics {
  const entities = new Map<string, EntityMetrics>();
  const sectionEvents = new Map<string, Set<string>>();
  const allEvents = new Set<string>();

  for (const f of facts) {
    const eventId = String(f?.event_id || '').trim();
    if (!eventId) continue;
    const section = String(f?.section || '(unknown)').trim() || '(unknown)';
    allEvents.add(eventId);
    (sectionEvents.get(section) ?? sectionEvents.set(section, new Set<string>()).get(section)!).add(eventId);

    for (const s of f.subjects ?? []) {
      const id = String(s || '').trim();
      if (!id) continue;
      const e = ensureEntity(entities, id);
      e.event_ids.add(eventId);
      e.roles.subject += 1;
      const sec = ensureSectionBucket(e.sections, section);
      sec.event_ids.add(eventId);
      sec.roles.subject += 1;
    }
    for (const o of f.objects ?? []) {
      const id = String(o || '').trim();
      if (!id) continue;
      const e = ensureEntity(entities, id);
      e.event_ids.add(eventId);
      e.roles.object += 1;
      const sec = ensureSectionBucket(e.sections, section);
      sec.event_ids.add(eventId);
      sec.roles.object += 1;
    }
  }

  const section_event_counts = new Map<string, number>();
  for (const [sec, ids] of sectionEvents) section_event_counts.set(sec, ids.size);
  return {
    entities,
    section_event_counts,
    corpus_event_count: allEvents.size,
    section_count: section_event_counts.size
  };
}

function scoreEntropyRoleSectionV1(entity: EntityMetrics, corpus: CorpusMetrics): number {
  const total = roleTotal(entity.roles);
  if (total < 2) return 0;

  const hRole = roleEntropy(entity.roles);
  const hMax = safeLog(4);
  const roleFocus = 1 - hRole / Math.max(EPS, hMax);

  let domSection = '';
  let domTf = 0;
  for (const [sec, row] of entity.sections) {
    const tf = row.event_ids.size;
    if (tf > domTf || (tf === domTf && sec < domSection)) {
      domSection = sec;
      domTf = tf;
    }
  }
  if (!domSection || domTf <= 0) return 2.0 * roleFocus;

  const sectionEventCount = Math.max(1, Number(corpus.section_event_counts.get(domSection) ?? 0));
  const pSec = domTf / sectionEventCount;
  const pAll = entity.event_ids.size / Math.max(1, corpus.corpus_event_count);
  const kl = pSec > 0 && pAll > 0 ? pSec * (safeLog(pSec) - safeLog(pAll)) : 0;

  const nSections = Math.max(1, corpus.section_count);
  const dfSections = Math.max(1, entity.sections.size);
  const idf = safeLog((nSections + 1) / (dfSections + 1));
  const tfidf = domTf * idf;

  return 2.0 * roleFocus + 1.0 * kl + 0.2 * Math.log1p(Math.max(0, tfidf));
}

export function computeImportanceScores(
  facts: FactLike[],
  profile: ImportanceProfileId
): Map<string, number> {
  const out = new Map<string, number>();
  if (profile === 'none') return out;

  const corpus = buildCorpusMetrics(facts);
  if (profile === 'entropy_role_section_v1') {
    for (const [id, m] of corpus.entities) out.set(id, scoreEntropyRoleSectionV1(m, corpus));
    return out;
  }
  return out;
}

export function percentileScaleMap(
  ids: string[],
  scoreById: Map<string, number>,
  minScale = 0.9,
  maxScale = 1.8
): Map<string, number> {
  const out = new Map<string, number>();
  const scored = ids
    .map((id) => ({ id, score: Number(scoreById.get(id) ?? 0) }))
    .sort((a, b) => a.score - b.score || a.id.localeCompare(b.id));
  if (!scored.length) return out;
  if (scored.length === 1) {
    const only = scored[0];
    if (only) out.set(only.id, (minScale + maxScale) / 2);
    return out;
  }
  for (let i = 0; i < scored.length; i++) {
    const row = scored[i];
    if (!row) continue;
    const p = i / (scored.length - 1);
    const scale = minScale + (maxScale - minScale) * Math.sqrt(Math.max(0, Math.min(1, p)));
    out.set(row.id, scale);
  }
  return out;
}
