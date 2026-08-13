import path from 'node:path';
import { existsSync } from 'node:fs';
import { spawn } from 'node:child_process';

/**
 * Resolves the repository root by looking for the 'SensibLaw' directory.
 */
export function resolveRepoRoot(): string {
  const candidates = [path.resolve('.'), path.resolve('..')];
  for (const c of candidates) {
    if (existsSync(path.join(c, 'SensibLaw'))) return c;
  }
  return path.resolve('..');
}

/**
 * Resolves the path to the ITIR SQLite database.
 * Defaults to .cache_local/itir.sqlite unless ITIR_DB_PATH is set.
 */
export function resolveItirDbPath(repoRoot: string): string {
  const raw = process.env.ITIR_DB_PATH?.trim() || '.cache_local/itir.sqlite';
  return path.resolve(repoRoot, raw);
}

/**
 * Spawns a process and returns its stdout as a string.
 * Rejects with a descriptive error if the process fails.
 */
export async function readStdout(cmd: string, args: string[], cwd: string): Promise<string> {
  return await new Promise<string>((resolve, reject) => {
    const child = spawn(cmd, args, { cwd });
    let stdout = '';
    let stderr = '';
    child.stdout.on('data', (d) => (stdout += d.toString()));
    child.stderr.on('data', (d) => (stderr += d.toString()));
    child.on('close', (code) => {
      if (code !== 0) {
        const errorDetail = stderr || stdout || 'No output';
        reject(new Error(`${cmd} ${args.join(' ')} failed with exit code ${code}\n\nDetail:\n${errorDetail}`));
      } else {
        resolve(stdout);
      }
    });
    child.on('error', (err) => {
      reject(new Error(`Failed to start ${cmd}: ${err.message}`));
    });
  });
}
