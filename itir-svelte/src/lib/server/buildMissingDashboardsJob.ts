import fs from 'node:fs/promises';
import path from 'node:path';
import { spawn } from 'node:child_process';
import crypto from 'node:crypto';

type Stage = 'idle' | 'ingest_codex' | 'build_dashboards' | 'done' | 'error';

export type BuildMissingJobStatus = {
  jobId: string;
  stage: Stage;
  percent: number; // 0..100 estimated
  message: string;
  startedAtIso: string;
  updatedAtIso: string;
  missingTotal: number;
  built: number;
  failed: number;
  errors: string[];
  done: boolean;
};

type JobInternal = BuildMissingJobStatus & {
  key: string;
};

const JOBS = new Map<string, JobInternal>();
const JOBS_BY_KEY = new Map<string, string>();

function nowIso(): string {
  return new Date().toISOString();
}

function clamp01(x: number): number {
  if (!Number.isFinite(x)) return 0;
  return Math.max(0, Math.min(1, x));
}

function mkJobId(): string {
  return crypto.randomBytes(12).toString('hex');
}

async function fileExists(p: string): Promise<boolean> {
  try {
    const st = await fs.stat(p);
    return st.isFile();
  } catch {
    return false;
  }
}

async function loadExistsForDate(runsRoot: string, date: string): Promise<boolean> {
  const pAll = path.join(runsRoot, date, 'outputs', 'dashboard_all.json');
  const p = path.join(runsRoot, date, 'outputs', 'dashboard.json');
  return (await fileExists(pAll)) || (await fileExists(p));
}

function resolveRepoRoot(): string {
  // itir-svelte is a sibling of StatiBaker in ITIR-suite.
  return path.resolve('..');
}

function resolvePython(repoRoot: string): string {
  const venv = path.join(repoRoot, '.venv', 'bin', 'python');
  return venv;
}

async function tryIngestCodexChats(repoRoot: string, job: JobInternal): Promise<void> {
  // Best-effort: if Codex history doesn't exist, skip without failing the build step.
  const home = process.env.HOME || '';
  const history = process.env.CODEX_HISTORY_PATH || path.join(home, '.codex', 'history.jsonl');
  const toolLog = process.env.CODEX_LOG_PATH || path.join(home, '.codex', 'log', 'codex-tui.log');
  const snapshotsDir = process.env.CODEX_SHELL_SNAPSHOTS_DIR || path.join(home, '.codex', 'shell_snapshots');
  const dbPath = path.join(repoRoot, 'chat-export-structurer', 'my_archive.sqlite');
  const ingestPy = path.join(repoRoot, 'chat-export-structurer', 'src', 'ingest.py');

  const haveHistory = await fileExists(history);
  if (!haveHistory) {
    job.message = `No Codex history found at ${history}; skipping chat ingest.`;
    job.updatedAtIso = nowIso();
    job.percent = Math.max(job.percent, 40);
    return;
  }

  const py = resolvePython(repoRoot);
  const pythonBin = (await fileExists(py)) ? py : 'python3';

  const args: string[] = [
    ingestPy,
    '--in',
    history,
    '--format',
    'codex',
    '--db',
    dbPath,
    '--tool-log',
    toolLog,
    '--account',
    process.env.CODEX_ACCOUNT_ID || 'local',
    '--source-id',
    'codex_auto_ui',
    '--upsert-empty-text',
    '--commit-every',
    '2000',
    '--debug',
    '--debug-every',
    '2000'
  ];

  if (await fileExists(snapshotsDir)) {
    args.push('--shell-snapshots-dir', snapshotsDir);
  }

  job.stage = 'ingest_codex';
  job.message = 'Ingesting Codex chats into chat archive...';
  job.updatedAtIso = nowIso();
  job.percent = 5;

  await new Promise<void>((resolve, reject) => {
    const child = spawn(pythonBin, args, { cwd: repoRoot, stdio: ['ignore', 'pipe', 'pipe'] });
    let total = 0;
    let processed = 0;
    let stderr = '';

    function bump() {
      const frac = total > 0 ? processed / total : 0;
      const est = Math.floor(40 * clamp01(frac));
      job.percent = Math.max(job.percent, est);
      job.updatedAtIso = nowIso();
    }

    child.stdout.on('data', (d) => {
      const text = String(d);
      for (const line of text.split(/\r?\n/g)) {
        const l = line.trim();
        if (!l) continue;

        // Example: "[+] Parsed 123 messages ..."
        const mParsed = l.match(/\bParsed\s+(\d+)\s+messages\b/i);
        if (mParsed) {
          total = Number(mParsed[1]) || total;
          bump();
          continue;
        }

        // Example: "  [debug] processed=2000/12345 inserted=..."
        const mProc = l.match(/\bprocessed=(\d+)\/(\d+)\b/);
        if (mProc) {
          processed = Number(mProc[1]) || processed;
          total = Number(mProc[2]) || total;
          bump();
        }
      }
    });

    child.stderr.on('data', (d) => {
      stderr += String(d);
      if (stderr.length > 50_000) stderr = stderr.slice(-50_000);
    });

    child.on('error', (err) => reject(err));
    child.on('close', (code) => {
      // Ingest is best-effort. If it fails, we continue but surface an error line.
      if (code !== 0) {
        job.errors.push(`chat ingest failed (exit ${code}). ${stderr.trim() || ''}`.trim());
      }
      job.percent = Math.max(job.percent, 40);
      job.updatedAtIso = nowIso();
      resolve();
    });
  });
}

async function runBuildDashboard(repoRoot: string, runsRoot: string, date: string): Promise<void> {
  const script = path.join(repoRoot, 'StatiBaker', 'scripts', 'build_dashboard.py');
  const args = [script, '--date', date, '--runs-root', runsRoot, '--repo-root', repoRoot];
  const child = spawn('python3', args, { cwd: repoRoot, stdio: ['ignore', 'pipe', 'pipe'] });
  let stderr = '';
  child.stderr.on('data', (d) => (stderr += String(d)));
  await new Promise<void>((resolve, reject) => {
    child.on('error', (err) => reject(err));
    child.on('close', (code) => {
      if (code === 0) return resolve();
      reject(new Error(`build_dashboard.py failed for ${date} (exit ${code}).\n${stderr}`));
    });
  });
}

async function runJob(job: JobInternal, runsRoot: string, start: string, end: string): Promise<void> {
  const repoRoot = resolveRepoRoot();
  try {
    // Fail fast if we can't write dashboards.
    try {
      await fs.mkdir(runsRoot, { recursive: true });
      const probe = path.join(runsRoot, `.itir_write_probe_${Date.now()}_${Math.random().toString(16).slice(2)}`);
      await fs.writeFile(probe, 'ok', 'utf-8');
      await fs.unlink(probe);
    } catch (err) {
      job.stage = 'error';
      job.message = `SB_RUNS_ROOT is not writable: ${runsRoot}`;
      job.errors.push(err instanceof Error ? err.message : String(err));
      job.done = true;
      job.updatedAtIso = nowIso();
      return;
    }

    await tryIngestCodexChats(repoRoot, job);

    job.stage = 'build_dashboards';
    job.message = 'Building missing dashboards...';
    job.updatedAtIso = nowIso();

    // Missing set is computed once at job start.
    const missingDates: string[] = [];
    // ISO lexical ordering matches chronological ordering.
    const startDate = start <= end ? start : end;
    const endDate = start <= end ? end : start;
    const partsA = startDate.split('-').map((x) => Number(x));
    const partsB = endDate.split('-').map((x) => Number(x));
    const [sy, sm, sd] = partsA as [number, number, number];
    const [ey, em, ed] = partsB as [number, number, number];
    const a = new Date(Date.UTC(sy, sm - 1, sd));
    const b = new Date(Date.UTC(ey, em - 1, ed));
    for (let d = a; d <= b; d = new Date(d.getTime() + 86400_000)) {
      const dateText = d.toISOString().slice(0, 10);
      if (!(await loadExistsForDate(runsRoot, dateText))) missingDates.push(dateText);
    }

    job.missingTotal = missingDates.length;
    job.built = 0;
    job.failed = 0;

    const total = Math.max(1, missingDates.length);
    for (const d of missingDates) {
      job.message = `Building dashboard for ${d}...`;
      job.updatedAtIso = nowIso();
      try {
        await runBuildDashboard(repoRoot, runsRoot, d);
        job.built += 1;
      } catch (err) {
        job.failed += 1;
        job.errors.push(err instanceof Error ? err.message : String(err));
      }
      const frac = (job.built + job.failed) / total;
      job.percent = Math.max(job.percent, 40 + Math.floor(60 * clamp01(frac)));
      job.updatedAtIso = nowIso();
    }

    job.stage = 'done';
    job.message = 'Done.';
    job.percent = 100;
    job.done = true;
    job.updatedAtIso = nowIso();
  } catch (err) {
    job.stage = 'error';
    job.message = 'Failed.';
    job.errors.push(err instanceof Error ? err.message : String(err));
    job.done = true;
    job.updatedAtIso = nowIso();
  }
}

export function startBuildMissingDashboardsJob(opts: {
  runsRoot: string;
  start: string;
  end: string;
}): { jobId: string } {
  const key = `${opts.runsRoot}|${opts.start}|${opts.end}`;
  const existing = JOBS_BY_KEY.get(key);
  if (existing && JOBS.get(existing) && !JOBS.get(existing)!.done) {
    return { jobId: existing };
  }

  const jobId = mkJobId();
  const startedAtIso = nowIso();
  const job: JobInternal = {
    key,
    jobId,
    stage: 'idle',
    percent: 0,
    message: 'Starting...',
    startedAtIso,
    updatedAtIso: startedAtIso,
    missingTotal: 0,
    built: 0,
    failed: 0,
    errors: [],
    done: false
  };

  JOBS.set(jobId, job);
  JOBS_BY_KEY.set(key, jobId);

  void runJob(job, opts.runsRoot, opts.start, opts.end);

  return { jobId };
}

export function getBuildMissingDashboardsJob(jobId: string): BuildMissingJobStatus | null {
  const job = JOBS.get(jobId);
  if (!job) return null;
  const { key: _key, ...publicJob } = job;
  return publicJob;
}
