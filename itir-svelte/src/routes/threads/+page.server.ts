import { listThreads } from '$lib/server/threadIndex';
import path from 'node:path';

export async function load({ url }: { url: URL }) {
  const q = (url.searchParams.get('q') ?? '').trim();
  const offset = Math.max(0, Number(url.searchParams.get('offset') ?? 0) || 0);

  // SvelteKit dev server runs with cwd at `itir-svelte/`; repo root is parent.
  const repoRoot = path.resolve('..');

  const data = await listThreads(repoRoot, { q, limit: 200, offset });
  return data;
}

