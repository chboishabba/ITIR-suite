import { error } from '@sveltejs/kit';
import { loadThreadArgumentsWorkbench } from '$lib/server/threadArguments';
import { threadReviewState } from '$lib/workbench/reviewState';
import { type ThreadArgumentsWorkbench } from '$lib/arguments/workbench';
import path from 'node:path';
import fs from 'node:fs';

function resolveRepoRoot(): string {
  const candidates = [path.resolve('.'), path.resolve('..')];
  for (const candidate of candidates) {
    if (fs.existsSync(path.join(candidate, 'SensibLaw')) && fs.existsSync(path.join(candidate, 'itir-svelte'))) {
      return candidate;
    }
  }
  return path.resolve('.');
}

function normalizeThreadId(raw: string): string {
  return raw.trim().replace(/[:/]+$/, '');
}

export async function load({ params }: { params: { threadId: string } }) {
  const threadId = normalizeThreadId(params.threadId);
  if (!threadId || threadId.length < 8) throw error(400, 'Invalid thread id.');
  const repoRoot = resolveRepoRoot();
  let workbench: ThreadArgumentsWorkbench;
  let stateReason: ReturnType<typeof threadReviewState> | 'load_error';
  try {
    workbench = await loadThreadArgumentsWorkbench(repoRoot, threadId);
    stateReason = threadReviewState(workbench.unavailableReason);
  } catch (err) {
    workbench = {
      threadId,
      title: null,
      total: 0,
      messages: [],
      unavailableReason: err instanceof Error ? `Failed to load argument workbench: ${err.message}` : 'Failed to load argument workbench.',
      families: [],
      anchors: [],
      badges: [],
      claims: [],
      edges: [],
      defaultSelectedClaimIds: [],
      sourceThreadId: null
    };
    stateReason = 'load_error';
  }
  return {
    workbench,
    stateReason
  };
}
