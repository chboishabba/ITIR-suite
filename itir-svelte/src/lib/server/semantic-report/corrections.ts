import path from 'node:path';
import { resolveRepoRoot, readStdout } from '../utils.ts';

type EvidenceRef = Record<string, unknown>;

export type SemanticCorrectionRecord = {
  correction_submission_id: string;
  source: string;
  run_id: string;
  corpus_label: string;
  event_id: string;
  relation_id: string | null;
  anchor_key: string | null;
  action_kind: string;
  proposed_payload: {
    proposed_predicate_key: string | null;
    replacement_label: string | null;
  };
  evidence_refs: EvidenceRef[];
  operator_provenance: Record<string, unknown>;
  created_at: string;
  note: string;
};

export type CorrectionFormFields = {
  source: string;
  runId: string;
  corpusLabel: string;
  eventId: string;
  relationId: string | null;
  anchorKey: string | null;
  actionKind: string;
  proposedPredicateKey: string | null;
  replacementLabel: string | null;
  note: string;
  evidenceRefs: EvidenceRef[];
};

export class CorrectionValidationError extends Error {}

const CORRECTION_LIMIT = 24;

function correctionAdminScriptPath(root: string) {
  return path.join(root, 'SensibLaw', 'scripts', 'semantic_review_admin.py');
}

function dbPath(root: string) {
  return path.join(root, '.cache_local', 'itir.sqlite');
}

function parseEvidencePayload(raw: string): EvidenceRef[] {
  if (!raw) {
    throw new CorrectionValidationError('Correction evidence payload was not valid JSON.');
  }
  try {
    const parsed = JSON.parse(raw);
    if (Array.isArray(parsed)) return parsed as EvidenceRef[];
  } catch {
    // fall through to error
  }
  throw new CorrectionValidationError('Correction evidence payload was not valid JSON.');
}

function normalizeFormValue(value: FormDataEntryValue | null): string {
  if (value === null) return '';
  return typeof value === 'string' ? value : value.toString();
}

export function parseCorrectionForm(form: FormData): CorrectionFormFields {
  const rawSource = normalizeFormValue(form.get('source')).trim().toLowerCase();
  const runId = normalizeFormValue(form.get('runId')).trim();
  const corpusLabel = normalizeFormValue(form.get('corpusLabel')).trim();
  const eventId = normalizeFormValue(form.get('eventId')).trim();
  const relationId = normalizeFormValue(form.get('relationId')).trim();
  const anchorKey = normalizeFormValue(form.get('anchorKey')).trim();
  const actionKind = normalizeFormValue(form.get('actionKind')).trim();
  const proposedPredicateKey = normalizeFormValue(form.get('proposedPredicateKey')).trim();
  const replacementLabel = normalizeFormValue(form.get('replacementLabel')).trim();
  const note = normalizeFormValue(form.get('note')).trim();
  const evidencePayload = normalizeFormValue(form.get('evidencePayload')).trim();

  if (!rawSource || !runId || !eventId || !actionKind || !evidencePayload) {
    throw new CorrectionValidationError('Missing required correction fields.');
  }

  return {
    source: rawSource,
    runId,
    corpusLabel,
    eventId,
    relationId: relationId || null,
    anchorKey: anchorKey || null,
    actionKind,
    proposedPredicateKey: proposedPredicateKey || null,
    replacementLabel: replacementLabel || null,
    note,
    evidenceRefs: parseEvidencePayload(evidencePayload)
  };
}

export function buildCorrectionRecord(
  fields: CorrectionFormFields,
  options?: { createdAt?: string; submissionTimestamp?: number }
): SemanticCorrectionRecord {
  const createdAt = options?.createdAt ?? new Date().toISOString();
  const timestamp = options?.submissionTimestamp ?? Date.now();
  return {
    correction_submission_id: `corr:${fields.source}:${timestamp}`,
    source: fields.source,
    run_id: fields.runId,
    corpus_label: fields.corpusLabel || fields.source,
    event_id: fields.eventId,
    relation_id: fields.relationId,
    anchor_key: fields.anchorKey,
    action_kind: fields.actionKind,
    proposed_payload: {
      proposed_predicate_key: fields.proposedPredicateKey,
      replacement_label: fields.replacementLabel
    },
    evidence_refs: fields.evidenceRefs,
    operator_provenance: {
      source: 'itir-svelte',
      actor: 'operator',
      route: '/graphs/semantic-report'
    },
    created_at: createdAt,
    note: fields.note
  };
}

export async function submitCorrectionRecord(record: SemanticCorrectionRecord): Promise<void> {
  const root = resolveRepoRoot();
  await readStdout(
    'python3',
    [
      correctionAdminScriptPath(root),
      '--db-path',
      dbPath(root),
      'submit-correction',
      '--payload-json',
      JSON.stringify(record)
    ],
    root
  );
}

export async function readCorrectionRecords(
  source: string,
  runId: string | undefined
): Promise<SemanticCorrectionRecord[]> {
  const root = resolveRepoRoot();
  const raw = await readStdout(
    'python3',
    [
      correctionAdminScriptPath(root),
      '--db-path',
      dbPath(root),
      'list-corrections',
      '--source',
      source,
      '--run-id',
      runId ?? '',
      '--limit',
      String(CORRECTION_LIMIT)
    ],
    root
  );
  const parsed = JSON.parse(raw);
  return Array.isArray(parsed) ? (parsed as SemanticCorrectionRecord[]) : [];
}
