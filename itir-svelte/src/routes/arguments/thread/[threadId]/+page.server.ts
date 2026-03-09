import { error } from '@sveltejs/kit';
import { loadThreadArgumentsWorkbench } from '$lib/server/threadArguments';
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
  const workbench = await loadThreadArgumentsWorkbench(repoRoot, threadId);
  return { workbench };
}
