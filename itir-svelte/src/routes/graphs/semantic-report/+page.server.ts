import path from 'node:path';
import { spawn } from 'node:child_process';
import { fail, redirect } from '@sveltejs/kit';
import { listSemanticCorpora, loadSemanticComparison, loadSemanticReport } from '$lib/server/semanticReport';

type SemanticCorrectionRecord = {
  correction_submission_id: string;
  source: string;
  run_id: string;
  corpus_label: string;
  event_id: string;
  relation_id: string | null;
  anchor_key: string | null;
  action_kind: string;
  proposed_payload: Record<string, unknown>;
  evidence_refs: Array<Record<string, unknown>>;
  operator_provenance: Record<string, unknown>;
  created_at: string;
  note: string;
};

function repoRoot(): string {
  return path.resolve('..');
}

function correctionAdminScriptPath(): string {
  return path.join(repoRoot(), 'SensibLaw', 'scripts', 'semantic_review_admin.py');
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

async function readCorrectionRecords(source: string, runId: string | undefined): Promise<SemanticCorrectionRecord[]> {
  const raw = await readStdout(
    'python3',
    [
      correctionAdminScriptPath(),
      '--db-path',
      path.join(repoRoot(), '.cache_local', 'itir.sqlite'),
      'list-corrections',
      '--source',
      source,
      '--run-id',
      runId || '',
      '--limit',
      '24'
    ],
    repoRoot()
  );
  const parsed = JSON.parse(raw);
  return Array.isArray(parsed) ? (parsed as SemanticCorrectionRecord[]) : [];
}

export async function load({ url }: { url: URL }) {
  const source = (url.searchParams.get('source') || 'gwb').toLowerCase();
  const available = listSemanticCorpora();
  try {
    const [payload, comparison] = await Promise.all([loadSemanticReport(source), loadSemanticComparison()]);
    const corrections = await readCorrectionRecords(source, payload.report?.run_id);
    return {
      ...payload,
      comparison,
      graphGate: comparison.graphGate,
      semanticGraph: comparison.semanticGraph,
      tokenArcDebug: payload.tokenArcDebug,
      corrections,
      available,
      error: null as string | null
    };
  } catch (e) {
    return {
      source,
      label: available.find((item) => item.key === source)?.label ?? source,
      report: null,
      comparison: null,
      graphGate: null,
      semanticGraph: null,
      tokenArcDebug: { events: [], unavailableReason: null },
      corrections: [],
      available,
      error: e instanceof Error ? e.message : String(e)
    };
  }
}

export const actions = {
  submitCorrection: async ({ request, url }: { request: Request; url: URL }) => {
    const form = await request.formData();
    const source = String(form.get('source') ?? '').trim().toLowerCase();
    const runId = String(form.get('runId') ?? '').trim();
    const corpusLabel = String(form.get('corpusLabel') ?? '').trim();
    const eventId = String(form.get('eventId') ?? '').trim();
    const relationId = String(form.get('relationId') ?? '').trim() || null;
    const anchorKey = String(form.get('anchorKey') ?? '').trim() || null;
    const actionKind = String(form.get('actionKind') ?? '').trim();
    const proposedPredicateKey = String(form.get('proposedPredicateKey') ?? '').trim();
    const replacementLabel = String(form.get('replacementLabel') ?? '').trim();
    const note = String(form.get('note') ?? '').trim();
    const evidencePayload = String(form.get('evidencePayload') ?? '').trim();
    if (!source || !runId || !eventId || !actionKind || !evidencePayload) {
      return fail(400, { ok: false, error: 'Missing required correction fields.' });
    }
    let evidenceRefs: Array<Record<string, unknown>> = [];
    try {
      const parsed = JSON.parse(evidencePayload);
      if (Array.isArray(parsed)) evidenceRefs = parsed as Array<Record<string, unknown>>;
    } catch {
      return fail(400, { ok: false, error: 'Correction evidence payload was not valid JSON.' });
    }
    const createdAt = new Date().toISOString();
    const record: SemanticCorrectionRecord = {
      correction_submission_id: `corr:${source}:${Date.now()}`,
      source,
      run_id: runId,
      corpus_label: corpusLabel || source,
      event_id: eventId,
      relation_id: relationId,
      anchor_key: anchorKey,
      action_kind: actionKind,
      proposed_payload: {
        proposed_predicate_key: proposedPredicateKey || null,
        replacement_label: replacementLabel || null,
      },
      evidence_refs: evidenceRefs,
      operator_provenance: {
        source: 'itir-svelte',
        actor: 'operator',
        route: '/graphs/semantic-report',
      },
      created_at: createdAt,
      note,
    };
    await readStdout(
      'python3',
      [
        correctionAdminScriptPath(),
        '--db-path',
        path.join(repoRoot(), '.cache_local', 'itir.sqlite'),
        'submit-correction',
        '--payload-json',
        JSON.stringify(record)
      ],
      repoRoot()
    );
    const next = new URL(url);
    next.searchParams.set('source', source);
    next.searchParams.set('submitted', '1');
    throw redirect(303, next.toString());
  }
};
