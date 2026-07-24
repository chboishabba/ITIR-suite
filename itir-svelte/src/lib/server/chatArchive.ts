import { spawn } from 'node:child_process';
import path from 'node:path';
import type { RuntimePathCandidate } from '$lib/server/runtime/pathCandidates';
import { gatherChatArchiveCandidates } from '$lib/server/runtime/pathCandidates';

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

export function resolveChatArchiveCandidates(): RuntimePathCandidate[] {
  return gatherChatArchiveCandidates();
}

export function resolveChatArchivePath(): string {
  return resolveChatArchiveCandidates()[0]!.path;
}

export async function fetchThreadTail(
  repoRoot: string,
  canonicalThreadId: string,
  opts: QueryOpts = {}
): Promise<{ title: string | null; total: number; messages: ChatArchiveMessage[] }> {
  const script = path.join(repoRoot, 'itir-svelte', 'scripts', 'query_chat_archive.py');
  const tail = Math.max(1, Math.min(2000, Math.floor(opts.tail ?? 400)));
  let fallback: { title: string | null; total: number; messages: ChatArchiveMessage[] } | null = null;

  for (const candidate of resolveChatArchiveCandidates()) {
    const dbPath = candidate.path;
    const argv = [script, '--db', dbPath, '--thread-id', canonicalThreadId, '--tail', String(tail)];
    if (opts.startIso && isDateText(opts.startIso)) argv.push('--start', opts.startIso);
    if (opts.endIso && isDateText(opts.endIso)) argv.push('--end', opts.endIso);
    const raw = await runQueryScript(argv, repoRoot);
    const parsed = JSON.parse(raw) as any;
    const payload = {
      title: typeof parsed?.title === 'string' ? parsed.title : parsed?.title ?? null,
      total: Number(parsed?.total ?? 0) || 0,
      messages: Array.isArray(parsed?.messages) ? (parsed.messages as ChatArchiveMessage[]) : []
    };
    if (!fallback) fallback = payload;
    if (payload.total > 0 || payload.messages.length > 0) return payload;
  }

  return fallback ?? { title: null, total: 0, messages: [] };
}

export async function fetchThreadTailBySourceThreadId(
  repoRoot: string,
  sourceThreadId: string,
  opts: QueryOpts = {}
): Promise<{ canonicalThreadId: string | null; title: string | null; total: number; messages: ChatArchiveMessage[] }> {
  const script = path.join(repoRoot, 'itir-svelte', 'scripts', 'query_chat_archive.py');
  const tail = Math.max(1, Math.min(2000, Math.floor(opts.tail ?? 400)));
  let fallback: { canonicalThreadId: string | null; title: string | null; total: number; messages: ChatArchiveMessage[] } | null = null;

  for (const candidate of resolveChatArchiveCandidates()) {
    const dbPath = candidate.path;
    const argv = [script, '--db', dbPath, '--source-thread-id', sourceThreadId, '--tail', String(tail)];
    if (opts.startIso && isDateText(opts.startIso)) argv.push('--start', opts.startIso);
    if (opts.endIso && isDateText(opts.endIso)) argv.push('--end', opts.endIso);
    const raw = await runQueryScript(argv, repoRoot);
    const parsed = JSON.parse(raw) as any;
    const payload = {
      canonicalThreadId: typeof parsed?.canonical_thread_id === 'string' ? parsed.canonical_thread_id : null,
      title: typeof parsed?.title === 'string' ? parsed.title : parsed?.title ?? null,
      total: Number(parsed?.total ?? 0) || 0,
      messages: Array.isArray(parsed?.messages) ? (parsed.messages as ChatArchiveMessage[]) : []
    };
    if (!fallback) fallback = payload;
    if (payload.canonicalThreadId || payload.total > 0 || payload.messages.length > 0) return payload;
  }

  return fallback ?? { canonicalThreadId: null, title: null, total: 0, messages: [] };
}

export async function fetchMessageAtTs(
  repoRoot: string,
  canonicalThreadId: string,
  ts: string
): Promise<ChatArchiveMessage | null> {
  const script = path.join(repoRoot, 'itir-svelte', 'scripts', 'query_chat_archive.py');
  for (const candidate of resolveChatArchiveCandidates()) {
    const dbPath = candidate.path;
    const argv = [script, '--db', dbPath, '--thread-id', canonicalThreadId, '--ts', ts];
    const raw = await runQueryScript(argv, repoRoot);
    const parsed = JSON.parse(raw) as any;
    const m = parsed?.message;
    if (m && typeof m === 'object') return m as ChatArchiveMessage;
  }
  return null;
}

export async function fetchLastMessageInRange(
  repoRoot: string,
  canonicalThreadId: string,
  range: { startTs: string | null; endTs: string | null },
  opts: { preferNonEmpty?: boolean } = {}
): Promise<ChatArchiveMessage | null> {
  const script = path.join(repoRoot, 'itir-svelte', 'scripts', 'query_chat_archive.py');
  for (const candidate of resolveChatArchiveCandidates()) {
    const dbPath = candidate.path;
    const argv = [script, '--db', dbPath, '--thread-id', canonicalThreadId];
    if (range.startTs) argv.push('--ts-start', range.startTs);
    if (range.endTs) argv.push('--ts-end', range.endTs);
    if (opts.preferNonEmpty) argv.push('--prefer-non-empty');

    const raw = await runQueryScript(argv, repoRoot);
    const parsed = JSON.parse(raw) as any;
    const m = parsed?.message;
    if (m && typeof m === 'object') return m as ChatArchiveMessage;
  }
  return null;
}
