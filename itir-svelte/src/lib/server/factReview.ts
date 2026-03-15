import path from 'node:path';
import { spawn } from 'node:child_process';

export type FactReviewSelector = {
  runId?: string | null;
  workflowKind?: string | null;
  workflowRunId?: string | null;
  sourceLabel?: string | null;
};

function resolveRepoRoot(): string {
  return path.resolve('..');
}

function resolveItirDbPath(repoRoot: string): string {
  const raw = process.env.ITIR_DB_PATH?.trim() || '.cache_local/itir.sqlite';
  return path.resolve(repoRoot, raw);
}

function queryScriptPath(repoRoot: string): string {
  return path.join(repoRoot, 'SensibLaw', 'scripts', 'query_fact_review.py');
}

async function readStdout(cmd: string, args: string[], cwd: string): Promise<string> {
  return await new Promise<string>((resolve, reject) => {
    const child = spawn(cmd, args, { cwd });
    let stdout = '';
    let stderr = '';
    child.stdout.on('data', (d) => (stdout += d.toString()));
    child.stderr.on('data', (d) => (stderr += d.toString()));
    child.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`${cmd} ${args.join(' ')} failed with ${code}\n${stderr || stdout}`));
      } else {
        resolve(stdout);
      }
    });
  });
}

function selectorArgs(selector: FactReviewSelector): string[] {
  const args: string[] = [];
  if (selector.runId) args.push('--run-id', selector.runId);
  if (selector.workflowKind) args.push('--workflow-kind', selector.workflowKind);
  if (selector.workflowRunId) args.push('--workflow-run-id', selector.workflowRunId);
  if (selector.sourceLabel) args.push('--source-label', selector.sourceLabel);
  return args;
}

async function runQuery(commandArgs: string[]): Promise<any> {
  const repoRoot = resolveRepoRoot();
  const raw = await readStdout(
    'python3',
    [queryScriptPath(repoRoot), '--db-path', resolveItirDbPath(repoRoot), ...commandArgs],
    repoRoot
  );
  return JSON.parse(raw);
}

export async function loadFactReviewWorkbench(selector: FactReviewSelector): Promise<any> {
  const payload = await runQuery([...selectorArgs(selector), 'workbench']);
  return payload.workbench;
}

export async function loadFactReviewAcceptance(
  selector: FactReviewSelector,
  opts: { wave?: string; fixtureKind?: string } = {}
): Promise<any> {
  const payload = await runQuery([
    ...selectorArgs(selector),
    'acceptance',
    '--wave',
    opts.wave ?? 'all',
    '--fixture-kind',
    opts.fixtureKind ?? 'unknown'
  ]);
  return payload.acceptance;
}

export async function listFactReviewSources(workflowKind?: string | null): Promise<any[]> {
  const args = ['sources'];
  if (workflowKind) args.push('--workflow-kind', workflowKind);
  const payload = await runQuery(args);
  return Array.isArray(payload.sources) ? payload.sources : [];
}
