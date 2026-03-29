import fs from 'node:fs/promises';
import path from 'node:path';
import { spawn } from 'node:child_process';

let warnedLegacyAooDbEnv = false;

export function resolveItirDbPath(repoRoot: string): string {
  const modern = process.env.ITIR_DB_PATH?.trim();
  if (modern) return path.resolve(repoRoot, modern);

  const legacy = process.env.SL_WIKI_TIMELINE_AOO_DB?.trim() || process.env.SL_WIKI_TIMELINE_DB?.trim();
  if (legacy) {
    if (!warnedLegacyAooDbEnv) {
      warnedLegacyAooDbEnv = true;
      console.warn('SL_WIKI_TIMELINE_AOO_DB / SL_WIKI_TIMELINE_DB is deprecated; use ITIR_DB_PATH.');
    }
    return path.resolve(repoRoot, legacy);
  }

  return path.resolve(repoRoot, '.cache_local', 'itir.sqlite');
}

export async function fileExists(p: string): Promise<boolean> {
  try {
    await fs.stat(p);
    return true;
  } catch {
    return false;
  }
}

export async function runPythonJson(repoRoot: string, args: string[]): Promise<unknown> {
  return new Promise((resolve, reject) => {
    const script = path.join(repoRoot, 'SensibLaw', 'scripts', 'query_wiki_timeline_aoo_db.py');
    const child = spawn('python3', [script, ...args], { cwd: repoRoot, stdio: ['ignore', 'pipe', 'pipe'] });
    let stdout = '';
    let stderr = '';
    child.stdout.on('data', (d) => (stdout += String(d)));
    child.stderr.on('data', (d) => (stderr += String(d)));
    child.on('error', (err) => reject(err));
    child.on('close', (code) => {
      if (code !== 0) return reject(new Error(`query_wiki_timeline_aoo_db.py failed (exit ${code}).\n${stderr || stdout}`));
      try {
        resolve(JSON.parse(stdout));
      } catch {
        reject(new Error(`query_wiki_timeline_aoo_db.py returned non-JSON output.\n${stderr || ''}\n${stdout.slice(0, 2000)}`));
      }
    });
  });
}

export async function loadFromDbCandidates(
  repoRoot: string,
  dbPath: string,
  timelineSuffixes: string[],
): Promise<unknown | null> {
  for (const timelineSuffix of timelineSuffixes) {
    const raw = await runPythonJson(repoRoot, ['--db-path', dbPath, '--timeline-path-suffix', timelineSuffix]);
    if (raw && typeof raw === 'object') {
      return raw;
    }
  }
  return null;
}
