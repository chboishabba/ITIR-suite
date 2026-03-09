import path from 'node:path';
import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';

export type WikiRevisionMonitorPayload = {
  db_path: string;
  packs: Array<{ pack_id: string; version: number; scope: string; manifest_path: string; updated_at: string }>;
  selected_pack_id: string | null;
  runs: Array<{ run_id: string; pack_id: string; started_at: string; completed_at: string | null; status: string; out_dir: string }>;
  selected_run_id: string | null;
  summary: any;
  selected_article_id: string | null;
  selected_graph: any;
};

function resolveRepoRoot(): string {
  const candidates = [path.resolve('.'), path.resolve('..')];
  for (const c of candidates) {
    if (existsSync(path.join(c, 'SensibLaw'))) return c;
  }
  return path.resolve('..');
}

function resolveRevisionMonitorDb(repoRoot: string): string {
  const raw = process.env.SL_WIKI_REVISION_MONITOR_DB?.trim() || 'SensibLaw/.cache_local/wiki_revision_harness.sqlite';
  return path.resolve(repoRoot, raw);
}

async function readStdout(cmd: string, args: string[], cwd: string): Promise<string> {
  return await new Promise<string>((resolve, reject) => {
    const child = spawn(cmd, args, { cwd });
    let stdout = '';
    let stderr = '';
    child.stdout.on('data', (d) => (stdout += d.toString()));
    child.stderr.on('data', (d) => (stderr += d.toString()));
    child.on('close', (code) => {
      if (code !== 0) reject(new Error(`${cmd} ${args.join(' ')} failed with ${code}\n${stderr || stdout}`));
      else resolve(stdout);
    });
  });
}

export async function loadWikiRevisionMonitor(opts: {
  packId?: string | null;
  runId?: string | null;
  articleId?: string | null;
}): Promise<WikiRevisionMonitorPayload> {
  const repoRoot = resolveRepoRoot();
  const dbPath = resolveRevisionMonitorDb(repoRoot);
  const script = path.join(repoRoot, 'SensibLaw', 'scripts', 'query_wiki_revision_monitor.py');
  const args = [script, '--db-path', dbPath];
  if (opts.packId) args.push('--pack-id', opts.packId);
  if (opts.runId) args.push('--run-id', opts.runId);
  if (opts.articleId) args.push('--article-id', opts.articleId);
  const stdout = await readStdout('python', args, repoRoot);
  return JSON.parse(stdout) as WikiRevisionMonitorPayload;
}
