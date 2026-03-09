import { error } from '@sveltejs/kit';
import { loadThreadArgumentsWorkbench } from '$lib/server/threadArguments';
import path from 'node:path';

export async function load({ params }: { params: { threadId: string } }) {
  const threadId = params.threadId;
  if (!threadId || threadId.length < 8) throw error(400, 'Invalid thread id.');
  const repoRoot = path.resolve('..');
  const workbench = await loadThreadArgumentsWorkbench(repoRoot, threadId);
  return { workbench };
}
