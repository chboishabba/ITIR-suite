import { spawn } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

export type ChatArchiveMessage = {
  message_id: string;
  canonical_thread_id: string;
  platform: string | null;
  account_id: string | null;
  ts: string;
  role: string;
  text: string;
  title: string | null;
  source_id: string | null;
  source_thread_id: string | null;
  source_message_id: string | null;
};

type QueryOpts = {
  startIso?: string | null; // inclusive; ISO date "YYYY-MM-DD"
  endIso?: string | null; // inclusive; ISO date "YYYY-MM-DD"
  tail?: number; // last N messages
};

function isDateText(v: string): boolean {
  return /^\d{4}-\d{2}-\d{2}$/.test(v);
}

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
      reject(new Error(err || out || `query_chat_archive.py failed (exit ${code})`));
    });
  });
}

export function resolveChatArchivePath(): string {
  const envPath = process.env.ITIR_CHAT_ARCHIVE_DB_PATH?.trim() || process.env.CHAT_ARCHIVE_DB_PATH?.trim();
  if (envPath) return path.resolve(envPath);

  const candidates = [path.join(os.homedir(), '.chat_archive.sqlite'), path.join(os.homedir(), 'chat_archive.sqlite')];
  for (const candidate of candidates) {
    if (fs.existsSync(candidate)) return candidate;
  }
  return candidates[0]!;
}

export async function fetchThreadTail(
  repoRoot: string,
  canonicalThreadId: string,
  opts: QueryOpts = {}
): Promise<{ title: string | null; total: number; messages: ChatArchiveMessage[] }> {
  const dbPath = resolveChatArchivePath();
  const script = path.join(repoRoot, 'itir-svelte', 'scripts', 'query_chat_archive.py');
  const tail = Math.max(1, Math.min(2000, Math.floor(opts.tail ?? 400)));

  const argv = [
    script,
    '--db',
    dbPath,
    '--thread-id',
    canonicalThreadId,
    '--tail',
    String(tail)
  ];
  if (opts.startIso && isDateText(opts.startIso)) argv.push('--start', opts.startIso);
  if (opts.endIso && isDateText(opts.endIso)) argv.push('--end', opts.endIso);

  const raw = await runQueryScript(argv, repoRoot);
  const parsed = JSON.parse(raw) as any;
  return {
    title: typeof parsed?.title === 'string' ? parsed.title : parsed?.title ?? null,
    total: Number(parsed?.total ?? 0) || 0,
    messages: Array.isArray(parsed?.messages) ? (parsed.messages as ChatArchiveMessage[]) : []
  };
}

export async function fetchThreadTailBySourceThreadId(
  repoRoot: string,
  sourceThreadId: string,
  opts: QueryOpts = {}
): Promise<{ canonicalThreadId: string | null; title: string | null; total: number; messages: ChatArchiveMessage[] }> {
  const dbPath = resolveChatArchivePath();
  const script = path.join(repoRoot, 'itir-svelte', 'scripts', 'query_chat_archive.py');
  const tail = Math.max(1, Math.min(2000, Math.floor(opts.tail ?? 400)));

  const argv = [script, '--db', dbPath, '--source-thread-id', sourceThreadId, '--tail', String(tail)];
  if (opts.startIso && isDateText(opts.startIso)) argv.push('--start', opts.startIso);
  if (opts.endIso && isDateText(opts.endIso)) argv.push('--end', opts.endIso);

  const raw = await runQueryScript(argv, repoRoot);
  const parsed = JSON.parse(raw) as any;
  return {
    canonicalThreadId: typeof parsed?.canonical_thread_id === 'string' ? parsed.canonical_thread_id : null,
    title: typeof parsed?.title === 'string' ? parsed.title : parsed?.title ?? null,
    total: Number(parsed?.total ?? 0) || 0,
    messages: Array.isArray(parsed?.messages) ? (parsed.messages as ChatArchiveMessage[]) : []
  };
}

export async function fetchMessageAtTs(
  repoRoot: string,
  canonicalThreadId: string,
  ts: string
): Promise<ChatArchiveMessage | null> {
  const dbPath = resolveChatArchivePath();
  const script = path.join(repoRoot, 'itir-svelte', 'scripts', 'query_chat_archive.py');

  const argv = [script, '--db', dbPath, '--thread-id', canonicalThreadId, '--ts', ts];
  const raw = await runQueryScript(argv, repoRoot);
  const parsed = JSON.parse(raw) as any;
  const m = parsed?.message;
  if (!m || typeof m !== 'object') return null;
  return m as ChatArchiveMessage;
}

export async function fetchLastMessageInRange(
  repoRoot: string,
  canonicalThreadId: string,
  range: { startTs: string | null; endTs: string | null },
  opts: { preferNonEmpty?: boolean } = {}
): Promise<ChatArchiveMessage | null> {
  const dbPath = resolveChatArchivePath();
  const script = path.join(repoRoot, 'itir-svelte', 'scripts', 'query_chat_archive.py');

  const argv = [script, '--db', dbPath, '--thread-id', canonicalThreadId];
  if (range.startTs) argv.push('--ts-start', range.startTs);
  if (range.endTs) argv.push('--ts-end', range.endTs);
  if (opts.preferNonEmpty) argv.push('--prefer-non-empty');

  const raw = await runQueryScript(argv, repoRoot);
  const parsed = JSON.parse(raw) as any;
  const m = parsed?.message;
  if (!m || typeof m !== 'object') return null;
  return m as ChatArchiveMessage;
}
