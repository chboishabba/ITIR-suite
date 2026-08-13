import path from 'node:path';
import fs from 'node:fs/promises';
import { readStdout } from '../utils';

export function messengerQueryScript(repoRoot: string): string {
  return path.join(repoRoot, 'itir-svelte', 'scripts', 'query_messenger_test_db.py');
}

export function openRecallQueryScript(repoRoot: string): string {
  return path.join(repoRoot, 'SensibLaw', 'scripts', 'query_openrecall_import.py');
}

export function factReviewQueryScript(repoRoot: string): string {
  return path.join(repoRoot, 'SensibLaw', 'scripts', 'query_fact_review.py');
}

export function resolveMessengerDbPath(repoRoot: string): string {
  const raw = process.env.ITIR_MESSENGER_DB_PATH?.trim() || process.env.MESSENGER_TEST_DB_PATH?.trim();
  return path.resolve(repoRoot, raw || '.cache_local/itir_messenger_test.sqlite');
}

export async function runJsonQuery<T>(cmd: string, args: string[], cwd: string): Promise<T> {
  const raw = await readStdout(cmd, args, cwd);
  return JSON.parse(raw) as T;
}

export async function readJsonFile<T>(filePath: string): Promise<T> {
  const raw = await fs.readFile(filePath, 'utf8');
  return JSON.parse(raw) as T;
}

export async function resolveLatestLiveContestedAffidavitPath(): Promise<string | null> {
  try {
    const entries = await fs.readdir('/tmp', { withFileTypes: true });
    const candidates: Array<{ filePath: string; mtimeMs: number }> = [];
    for (const entry of entries) {
      if (!entry.isDirectory() || !entry.name.startsWith('google_docs_contested')) continue;
      const candidatePath = path.join('/tmp', entry.name, 'affidavit_coverage_review_v1.json');
      try {
        const stat = await fs.stat(candidatePath);
        candidates.push({ filePath: candidatePath, mtimeMs: stat.mtimeMs });
      } catch {
        // optional artifact
      }
    }
    candidates.sort((a, b) => b.mtimeMs - a.mtimeMs);
    return candidates[0]?.filePath ?? null;
  } catch {
    return null;
  }
}
