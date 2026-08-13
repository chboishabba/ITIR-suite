import fs from 'node:fs/promises';
import path from 'node:path';
import { loadFactReviewWorkbench } from '$lib/server/factReview';
import { loadTircorderSourceArtifact } from '$lib/server/tircorderSourceArtifact';
import { resolveRepoRoot } from '$lib/server/utils';

export interface NormalizedArtifactRef {
  label: string;
  producer: string;
  source: string;
  artifact: Record<string, unknown> | null;
  inspect_href?: string | null;
  inspect_label?: string | null;
  gate?: {
    decision?: string;
    reason?: string;
    product_ref?: string;
  } | null;
  workflow?: {
    stage?: string;
    title?: string;
    recommended_view?: string;
    recommended_filter?: string | null;
    reason?: string;
  } | null;
  error?: string | null;
}

export interface SuiteNormalizedArtifact {
  schema_version?: string;
  artifact_role?: string;
  artifact_id?: string;
  canonical_identity?: {
    identity_class?: string;
    identity_key?: string;
    aliases?: string[];
  } | null;
  provenance_anchor?: {
    source_system?: string;
    source_artifact_id?: string;
    anchor_kind?: string;
    anchor_ref?: string | null;
  } | null;
  context_envelope_ref?: {
    envelope_id?: string;
    envelope_kind?: string;
  } | null;
  authority?: {
    authority_class?: string;
    derived?: boolean;
    promotion_receipt_ref?: Record<string, unknown> | null;
  } | null;
  lineage?: {
    upstream_artifact_ids?: string[];
    profile_version?: string | null;
  } | null;
  follow_obligation?: {
    trigger?: string;
    scope?: string;
    stop_condition?: string;
  } | null;
  unresolved_pressure_status?: string;
  summary?: Record<string, unknown> | null;
}

function buildFactReviewInspectHref(args: {
  workflowKind: string;
  workflowRunId?: string | null;
  sourceLabel?: string | null;
  recommendedView?: string | null;
  recommendedFilter?: string | null;
}): string {
  const params = new URLSearchParams();
  params.set('workflow', args.workflowKind);
  if (args.workflowRunId) params.set('workflowRunId', args.workflowRunId);
  if (args.sourceLabel) params.set('sourceLabel', args.sourceLabel);
  if (args.recommendedView) params.set('view', args.recommendedView);
  if (args.recommendedFilter && args.recommendedFilter !== 'all') params.set('filter', args.recommendedFilter);
  return `/graphs/fact-review?${params.toString()}`;
}

async function readJsonObject(filePath: string): Promise<Record<string, unknown>> {
  return JSON.parse(await fs.readFile(filePath, 'utf-8')) as Record<string, unknown>;
}

function resolveArtifactPath(repoRoot: string, rawPath: string): string {
  if (path.isAbsolute(rawPath)) return rawPath;
  return path.resolve(repoRoot, rawPath);
}

function resolveSbRunsRoot(repoRoot: string): string {
  const fallback = path.join(repoRoot, 'StatiBaker', 'runs');
  const raw = process.env.SB_RUNS_ROOT?.trim() || fallback;
  return path.resolve(raw);
}

async function findLatestSbBundleArtifact(sbRunsRoot: string): Promise<string | null> {
  try {
    const entries = await fs.readdir(sbRunsRoot, { withFileTypes: true });
    const candidates = entries
      .filter((entry) => entry.isDirectory() && /^\d{4}-\d{2}-\d{2}$/.test(entry.name))
      .map((entry) => entry.name)
      .sort()
      .reverse();
    for (const dateText of candidates) {
      const candidate = path.join(sbRunsRoot, dateText, 'bundle', 'suite_normalized_artifact.json');
      try {
        await fs.access(candidate);
        return candidate;
      } catch {
        continue;
      }
    }
  } catch {
    return null;
  }
  return null;
}

export async function loadSbNormalizedArtifact(date?: string | null): Promise<NormalizedArtifactRef> {
  const repoRoot = resolveRepoRoot();
  const sbRunsRoot = resolveSbRunsRoot(repoRoot);
  const explicit = date ? path.join(sbRunsRoot, date, 'bundle', 'suite_normalized_artifact.json') : null;
  const artifactPath = explicit ?? (await findLatestSbBundleArtifact(sbRunsRoot));
  if (!artifactPath) {
    return {
      label: date ? `StatiBaker ${date}` : 'StatiBaker latest bundle',
      producer: 'StatiBaker',
      source: explicit ?? path.join(sbRunsRoot, '<date>', 'bundle', 'suite_normalized_artifact.json'),
      artifact: null,
      error: 'No compiled-state normalized artifact bundle was found.'
    };
  }
  try {
    const artifact = await readJsonObject(artifactPath);
    return {
      label: path.basename(path.dirname(path.dirname(artifactPath))),
      producer: 'StatiBaker',
      source: artifactPath,
      artifact,
      inspect_href: '/graphs/timeline-ribbon',
      inspect_label: 'Open timeline ribbon'
    };
  } catch (error) {
    return {
      label: date ? `StatiBaker ${date}` : 'StatiBaker latest bundle',
      producer: 'StatiBaker',
      source: artifactPath,
      artifact: null,
      error: error instanceof Error ? error.message : String(error)
    };
  }
}

export async function loadFactReviewNormalizedArtifact(
  workflowKind: string,
  workflowRunId?: string | null,
  sourceLabel?: string | null
): Promise<NormalizedArtifactRef> {
  try {
    const workbench = await loadFactReviewWorkbench({
      workflowKind,
      workflowRunId: workflowRunId ?? null,
      sourceLabel: sourceLabel ?? null
    });
    const artifact = (workbench.semantic_context?.suite_normalized_artifact ?? null) as Record<string, unknown> | null;
    const workflowSummary = (workbench.workflow_summary ?? null) as {
      stage?: string;
      title?: string;
      recommended_view?: string;
      recommended_filter?: string | null;
      reason?: string;
      promotion_gate?: {
        decision?: string;
        reason?: string;
        product_ref?: string;
      } | null;
    } | null;
    return {
      label: workbench.run.run_id,
      producer: 'SensibLaw',
      source: `${workflowKind}:${workbench.run.run_id}`,
      artifact,
      inspect_href: buildFactReviewInspectHref({
        workflowKind,
        workflowRunId: workflowRunId ?? workbench.run.workflow_link?.workflow_run_id ?? null,
        sourceLabel,
        recommendedView: workflowSummary?.recommended_view ?? null,
        recommendedFilter: workflowSummary?.recommended_filter ?? null
      }),
      inspect_label: workflowSummary?.recommended_view ? 'Open recommended review view' : 'Open fact review workbench',
      gate: workflowSummary?.promotion_gate ?? null,
      workflow: workflowSummary
        ? {
            stage: workflowSummary.stage,
            title: workflowSummary.title,
            recommended_view: workflowSummary.recommended_view,
            recommended_filter: workflowSummary.recommended_filter ?? null,
            reason: workflowSummary.reason
          }
        : null,
      error: artifact ? null : 'No suite_normalized_artifact was present in the selected review payload.'
    };
  } catch (error) {
    return {
      label: workflowRunId ?? workflowKind,
      producer: 'SensibLaw',
      source: workflowKind,
      artifact: null,
      error: error instanceof Error ? error.message : String(error)
    };
  }
}

export async function loadArchiveNormalizedArtifact(
  artifactPath?: string | null
): Promise<NormalizedArtifactRef | null> {
  if (!artifactPath) return null;
  const repoRoot = resolveRepoRoot();
  const resolvedPath = resolveArtifactPath(repoRoot, artifactPath);
  try {
    const artifact = await readJsonObject(resolvedPath);
    return {
      label: path.basename(resolvedPath),
      producer: 'chat-export-structurer',
      source: resolvedPath,
      artifact,
      inspect_href: '/corpora/chat-archive',
      inspect_label: 'Open chat archive corpus'
    };
  } catch (error) {
    return {
      label: path.basename(artifactPath),
      producer: 'chat-export-structurer',
      source: resolvedPath,
      artifact: null,
      inspect_href: '/corpora/chat-archive',
      inspect_label: 'Open chat archive corpus',
      error: error instanceof Error ? error.message : String(error)
    };
  }
}

export async function loadCaptureNormalizedArtifact(
  artifactPath?: string | null
): Promise<NormalizedArtifactRef | null> {
  return loadTircorderSourceArtifact(artifactPath);
}

export async function loadResearchNormalizedArtifact(
  artifactPath?: string | null
): Promise<NormalizedArtifactRef | null> {
  if (!artifactPath) return null;
  const repoRoot = resolveRepoRoot();
  const resolvedPath = resolveArtifactPath(repoRoot, artifactPath);
  try {
    const artifact = await readJsonObject(resolvedPath);
    return {
      label: path.basename(resolvedPath),
      producer: 'notebooklm-py',
      source: resolvedPath,
      artifact,
      inspect_href: '/graphs/normalized-artifacts',
      inspect_label: 'Inspect retrieval artifact'
    };
  } catch (error) {
    return {
      label: path.basename(artifactPath),
      producer: 'notebooklm-py',
      source: resolvedPath,
      artifact: null,
      inspect_href: '/graphs/normalized-artifacts',
      inspect_label: 'Inspect retrieval artifact',
      error: error instanceof Error ? error.message : String(error)
    };
  }
}

export async function loadConversationNormalizedArtifact(
  artifactPath?: string | null
): Promise<NormalizedArtifactRef | null> {
  if (!artifactPath) return null;
  const repoRoot = resolveRepoRoot();
  const resolvedPath = resolveArtifactPath(repoRoot, artifactPath);
  try {
    const artifact = await readJsonObject(resolvedPath);
    return {
      label: path.basename(resolvedPath),
      producer: 'reverse-engineered-chatgpt',
      source: resolvedPath,
      artifact,
      inspect_href: '/corpora/chat-archive',
      inspect_label: 'Open chat archive corpus'
    };
  } catch (error) {
    return {
      label: path.basename(artifactPath),
      producer: 'reverse-engineered-chatgpt',
      source: resolvedPath,
      artifact: null,
      inspect_href: '/corpora/chat-archive',
      inspect_label: 'Open chat archive corpus',
      error: error instanceof Error ? error.message : String(error)
    };
  }
}
