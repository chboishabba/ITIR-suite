import path from 'node:path';
import { spawn } from 'node:child_process';
import { resolveChatArchivePath } from '$lib/server/chatArchive';

export type ThreadIndexRow = {
  canonical_thread_id: string;
  title: string;
  message_count: number;
  empty_text_count: number;
  latest_ts: string;
  source_id: string | null;
  platform: string | null;
  account_id: string | null;
  any_source_thread_id: string | null;
};

function runQueryScript(args: string[], cwd: string): Promise<string> {
  return new Promise((resolve, reject) => {
    const child = spawn('python3', args, { cwd, stdio: ['ignore', 'pipe', 'pipe'] });
    let out = '';
    let err = '';
    child.stdout.on('data', (d) => (out += String(d)));
    child.stderr.on('data', (d) => (err += String(d)));
    child.on('error', (e) => reject(e));
    child.on('close', (code) => {
      if (code === 0) return resolve(out);
      reject(new Error(err || out || `list_threads.py failed (exit ${code})`));
    });
  });
}

export async function listThreads(
  repoRoot: string,
  opts: { q?: string; limit?: number; offset?: number } = {}
): Promise<{ threads: ThreadIndexRow[]; q: string; limit: number; offset: number }> {
  const dbPath = resolveChatArchivePath();
  const script = path.join(repoRoot, 'itir-svelte', 'scripts', 'list_threads.py');
  const limit = Math.max(1, Math.min(500, Math.floor(opts.limit ?? 200)));
  const offset = Math.max(0, Math.floor(opts.offset ?? 0));
  const q = (opts.q ?? '').trim();

  const argv = [script, '--db', dbPath, '--limit', String(limit), '--offset', String(offset)];
  if (q) argv.push('--q', q);

  const raw = await runQueryScript(argv, repoRoot);
  const parsed = JSON.parse(raw) as any;
  return {
    threads: Array.isArray(parsed?.threads) ? (parsed.threads as ThreadIndexRow[]) : [],
    q: typeof parsed?.q === 'string' ? parsed.q : q,
    limit: Number(parsed?.limit ?? limit) || limit,
    offset: Number(parsed?.offset ?? offset) || offset
  };
}
