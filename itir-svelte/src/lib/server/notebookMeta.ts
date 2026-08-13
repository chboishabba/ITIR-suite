import fs from 'node:fs/promises';
import { createReadStream } from 'node:fs';
import path from 'node:path';
import readline from 'node:readline';

export type NotebookMetaMessage = {
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

export type NotebookMetaSummary = {
  notebookIdHash: string | null;
  unscoped: boolean;
  eventCount: number;
  groupedMessageCount: number;
  sourceObservedCount: number;
  artifactObservedCount: number;
  sourceSummaryCount: number;
  uniqueNoteIdCount: number;
  firstTs: string | null;
  lastTs: string | null;
};

export type NotebookMetaSourceRow = {
  noteIdHash: string;
  sourceTitle: string | null;
  sourceType: string | null;
  sourceUrl: string | null;
  mentions: number;
};

type QueryOpts = {
  startDate?: string | null; // YYYY-MM-DD inclusive
  endDate?: string | null; // YYYY-MM-DD inclusive
  tail?: number; // last N rows
  runsRootEnv?: string | undefined;
};

type ParsedNotebookRow = {
  seq: number;
  ts: string;
  event: string;
  notebookHash: string;
  noteHash: string;
  provenanceSource: string;
  notebookTitle: string | null;
  sourceTitle: string | null;
  sourceType: string | null;
  sourceStatus: string | null;
  sourceUrl: string | null;
  sourceCreatedAt: string | null;
  sourceSummary: string | null;
  sourceKeywords: string[];
  artifactIdHash: string | null;
  artifactTitle: string | null;
  artifactType: string | null;
  artifactStatus: string | null;
  artifactCreatedAt: string | null;
  hasContext: boolean | null;
};

type SourceObservedBatchAcc = {
  ts: string;
  seq: number;
  notebookHash: string;
  provenanceSource: string;
  sourceObservedCount: number;
  sourceTitles: Set<string>;
  sourceTypes: Set<string>;
  sourceStatuses: Set<string>;
  sourceSummaries: string[];
  noteHashes: Set<string>;
};

type SummaryAcc = {
  eventCount: number;
  sourceObservedCount: number;
  artifactObservedCount: number;
  sourceSummaryCount: number;
  uniqueNoteHashes: Set<string>;
  firstTs: string | null;
  lastTs: string | null;
};

const PREFIX = 'meta:notebooklm:';

function isDateText(v: string): boolean {
  return /^\d{4}-\d{2}-\d{2}$/.test(v);
}

function shortHash(value: string): string {
  const clean = value.replace(/^sha256:/i, '').trim();
  if (!clean) return '';
  return clean.length > 12 ? `${clean.slice(0, 12)}...` : clean;
}

function resolveRunsRoot(runsRootEnv: string | undefined): string {
  const fallback = path.resolve('..', 'StatiBaker', 'runs');
  const raw = runsRootEnv && runsRootEnv.trim() ? runsRootEnv.trim() : fallback;
  return path.resolve(raw);
}

function dateRangeInclusive(start: string, end: string): string[] {
  const out: string[] = [];
  if (start > end) [start, end] = [end, start];
  const partsA = start.split('-').map((x) => Number(x));
  const partsB = end.split('-').map((x) => Number(x));
  if (partsA.length !== 3 || partsB.length !== 3) return out;
  const [sy, sm, sd] = partsA as [number, number, number];
  const [ey, em, ed] = partsB as [number, number, number];
  if (![sy, sm, sd, ey, em, ed].every((n) => Number.isFinite(n))) return out;
  const startDate = new Date(Date.UTC(sy, sm - 1, sd));
  const endDate = new Date(Date.UTC(ey, em - 1, ed));
  for (let d = startDate; d <= endDate; d = new Date(d.getTime() + 86400_000)) {
    out.push(d.toISOString().slice(0, 10));
  }
  return out;
}

async function listDatesWithNotes(runsRoot: string): Promise<string[]> {
  try {
    const entries = await fs.readdir(runsRoot, { withFileTypes: true });
    const out: string[] = [];
    for (const e of entries) {
      if (!e.isDirectory() || !isDateText(e.name)) continue;
      const notesFile = path.join(runsRoot, e.name, 'logs', 'notes', `${e.name}.jsonl`);
      try {
        await fs.access(notesFile);
        out.push(e.name);
      } catch {
        // ignore missing notes file
      }
    }
    return out.sort();
  } catch {
    return [];
  }
}

function titleFromThreadId(threadId: string): string {
  const id = threadId.startsWith(PREFIX) ? threadId.slice(PREFIX.length) : threadId;
  if (id === 'unscoped') return 'NotebookLM (unscoped metadata)';
  return `NotebookLM ${shortHash(id)}`;
}

function notebookHashFromThreadId(threadId: string): string | null {
  const id = threadId.startsWith(PREFIX) ? threadId.slice(PREFIX.length) : threadId;
  if (!id || id === 'unscoped') return null;
  return id;
}

function matchesThread(threadId: string, record: Record<string, unknown>): boolean {
  const id = threadId.startsWith(PREFIX) ? threadId.slice(PREFIX.length) : threadId;
  const notebookHash = String(record.notebook_id_hash ?? '').trim();
  if (id === 'unscoped') return !notebookHash;
  return notebookHash === id;
}

function buildMessageText(record: Record<string, unknown>): string {
  return `notebooklm_meta_event ${JSON.stringify(record)}`;
}

function toParsedRow(date: string, seq: number, record: Record<string, unknown>): ParsedNotebookRow {
  const event = String(record.event ?? '').trim() || 'unknown';
  const ts = String(record.ts ?? '').trim() || `${date}T00:00:00Z`;
  const notebookHash = String(record.notebook_id_hash ?? '').trim();
  const noteHash = String(record.note_id_hash ?? '').trim();
  const provenance = record.provenance && typeof record.provenance === 'object' ? (record.provenance as Record<string, unknown>) : null;
  const provenanceSource = String(provenance?.source ?? '').trim();
  const sourceKeywords = Array.isArray(record.source_keywords)
    ? record.source_keywords.map((v) => String(v ?? '').trim()).filter((v) => v.length > 0).slice(0, 24)
    : [];
  const hasContextRaw = record.has_context;
  const hasContext =
    typeof hasContextRaw === 'boolean'
      ? hasContextRaw
      : typeof hasContextRaw === 'number'
        ? hasContextRaw !== 0
        : typeof hasContextRaw === 'string'
          ? hasContextRaw.trim().toLowerCase() === 'true'
          : null;
  return {
    seq,
    ts,
    event,
    notebookHash,
    noteHash,
    provenanceSource,
    notebookTitle: String(record.notebook_title ?? '').trim() || null,
    sourceTitle: String(record.source_title ?? '').trim() || null,
    sourceType: String(record.source_type ?? '').trim() || null,
    sourceStatus: String(record.source_status ?? '').trim() || null,
    sourceUrl: String(record.source_url ?? '').trim() || null,
    sourceCreatedAt: String(record.source_created_at ?? '').trim() || null,
    sourceSummary: String(record.source_summary ?? '').trim() || null,
    sourceKeywords,
    artifactIdHash: String(record.artifact_id_hash ?? '').trim() || null,
    artifactTitle: String(record.artifact_title ?? '').trim() || null,
    artifactType: String(record.artifact_type ?? '').trim() || null,
    artifactStatus: String(record.artifact_status ?? '').trim() || null,
    artifactCreatedAt: String(record.artifact_created_at ?? '').trim() || null,
    hasContext
  };
}

function buildSinglePayload(row: ParsedNotebookRow): Record<string, unknown> {
  const SUMMARY_CHAR_LIMIT = 1200;
  const summary =
    row.sourceSummary && row.sourceSummary.length > SUMMARY_CHAR_LIMIT
      ? `${row.sourceSummary.slice(0, SUMMARY_CHAR_LIMIT)}\n…`
      : row.sourceSummary;
  return {
    event: row.event,
    ts: row.ts,
    notebook_id_hash: row.notebookHash || null,
    note_id_hash: row.noteHash || null,
    provenance_source: row.provenanceSource || null,
    notebook_title: row.notebookTitle ?? null,
    source_title: row.sourceTitle ?? null,
    source_type: row.sourceType ?? null,
    source_status: row.sourceStatus ?? null,
    source_url: row.sourceUrl ?? null,
    source_created_at: row.sourceCreatedAt ?? null,
    source_summary: summary ?? null,
    source_summary_truncated: Boolean(row.sourceSummary && summary && row.sourceSummary.length > summary.length),
    source_keywords: row.sourceKeywords,
    artifact_id_hash: row.artifactIdHash ?? null,
    artifact_title: row.artifactTitle ?? null,
    artifact_type: row.artifactType ?? null,
    artifact_status: row.artifactStatus ?? null,
    artifact_created_at: row.artifactCreatedAt ?? null,
    has_context: row.hasContext
  };
}

function buildSourceObservedBatchPayload(batch: SourceObservedBatchAcc): Record<string, unknown> {
  const sourceTitles = [...batch.sourceTitles].sort((a, b) => a.localeCompare(b));
  const sourceTypes = [...batch.sourceTypes].sort((a, b) => a.localeCompare(b));
  const sourceStatuses = [...batch.sourceStatuses].sort((a, b) => a.localeCompare(b));
  const noteHashes = [...batch.noteHashes].sort((a, b) => a.localeCompare(b));
  const summaryItems = batch.sourceSummaries.filter((v) => v.length > 0);
  const NOTE_HASH_LIMIT = 120;
  const SOURCE_SUMMARY_LIMIT = 8;
  const SOURCE_SUMMARY_CHAR_LIMIT = 600;
  const noteHashesLimited = noteHashes.slice(0, NOTE_HASH_LIMIT);
  const summaryLimited = summaryItems.slice(0, SOURCE_SUMMARY_LIMIT).map((v) => (v.length > SOURCE_SUMMARY_CHAR_LIMIT ? `${v.slice(0, SOURCE_SUMMARY_CHAR_LIMIT)}…` : v));
  return {
    event: 'source_observed_batch',
    ts: batch.ts,
    notebook_id_hash: batch.notebookHash || null,
    source_observed_count: batch.sourceObservedCount,
    unique_note_id_count: noteHashes.length,
    source_titles: sourceTitles,
    source_types: sourceTypes,
    source_statuses: sourceStatuses,
    source_summary_count: summaryItems.length,
    source_summaries: summaryLimited,
    source_summaries_truncated: summaryItems.length > summaryLimited.length,
    note_id_hashes: noteHashesLimited,
    note_id_hashes_total: noteHashes.length,
    note_id_hashes_truncated: noteHashes.length > noteHashesLimited.length,
    provenance_source: batch.provenanceSource || null
  };
}

function buildSummary(threadId: string, acc: SummaryAcc, groupedCount: number): NotebookMetaSummary {
  return {
    notebookIdHash: notebookHashFromThreadId(threadId),
    unscoped: notebookHashFromThreadId(threadId) === null,
    eventCount: acc.eventCount,
    groupedMessageCount: groupedCount,
    sourceObservedCount: acc.sourceObservedCount,
    artifactObservedCount: acc.artifactObservedCount,
    sourceSummaryCount: acc.sourceSummaryCount,
    uniqueNoteIdCount: acc.uniqueNoteHashes.size,
    firstTs: acc.firstTs,
    lastTs: acc.lastTs
  };
}

function buildSourceCatalog(byHash: Map<string, NotebookMetaSourceRow>): NotebookMetaSourceRow[] {
  return [...byHash.values()].sort((a, b) => {
    const ta = (a.sourceTitle ?? '').trim();
    const tb = (b.sourceTitle ?? '').trim();
    return ta.localeCompare(tb);
  });
}

export function isNotebookMetaThreadId(threadId: string): boolean {
  return threadId.startsWith(PREFIX);
}

export async function fetchNotebookMetaThreadTail(
  threadId: string,
  opts: QueryOpts = {}
): Promise<{ title: string; total: number; messages: NotebookMetaMessage[]; summary: NotebookMetaSummary; sources: NotebookMetaSourceRow[] }> {
  const emptySummary: NotebookMetaSummary = {
    notebookIdHash: notebookHashFromThreadId(threadId),
    unscoped: notebookHashFromThreadId(threadId) === null,
    eventCount: 0,
    groupedMessageCount: 0,
    sourceObservedCount: 0,
    artifactObservedCount: 0,
    sourceSummaryCount: 0,
    uniqueNoteIdCount: 0,
    firstTs: null,
    lastTs: null
  };
  if (!isNotebookMetaThreadId(threadId)) {
    return { title: titleFromThreadId(threadId), total: 0, messages: [], summary: emptySummary, sources: [] };
  }

  const runsRoot = resolveRunsRoot(opts.runsRootEnv);
  const tail = Math.max(1, Math.min(400, Math.floor(opts.tail ?? 200)));

  let dates: string[] = [];
  if (opts.startDate && opts.endDate && isDateText(opts.startDate) && isDateText(opts.endDate)) {
    dates = dateRangeInclusive(opts.startDate, opts.endDate);
  } else {
    dates = await listDatesWithNotes(runsRoot);
  }

  const summaryAcc: SummaryAcc = {
    eventCount: 0,
    sourceObservedCount: 0,
    artifactObservedCount: 0,
    sourceSummaryCount: 0,
    uniqueNoteHashes: new Set<string>(),
    firstTs: null,
    lastTs: null
  };
  const sourceCatalogByHash = new Map<string, NotebookMetaSourceRow>();
  const sourceBatchByKey = new Map<string, SourceObservedBatchAcc>();
  const passthrough: Array<{ ts: string; seq: number; payload: Record<string, unknown> }> = [];
  let seq = 0;
  for (const date of dates) {
    const file = path.join(runsRoot, date, 'logs', 'notes', `${date}.jsonl`);
    try {
      await fs.access(file);
    } catch {
      continue;
    }
    const stream = createReadStream(file, { encoding: 'utf-8' });
    const rl = readline.createInterface({ input: stream, crlfDelay: Infinity });
    try {
      for await (const rawLine of rl) {
        const line = (rawLine ?? '').trim();
        if (!line) continue;

        let record: Record<string, unknown>;
        try {
          const parsed = JSON.parse(line);
          if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) continue;
          record = parsed as Record<string, unknown>;
        } catch {
          continue;
        }

        if (String(record.signal ?? '').trim().toLowerCase() !== 'notes_meta') continue;
        if (String(record.app ?? '').trim().toLowerCase() !== 'notebooklm') continue;
        if (!matchesThread(threadId, record)) continue;

        const row = toParsedRow(date, seq++, record);
        summaryAcc.eventCount += 1;
        if (!summaryAcc.firstTs || row.ts < summaryAcc.firstTs) summaryAcc.firstTs = row.ts;
        if (!summaryAcc.lastTs || row.ts > summaryAcc.lastTs) summaryAcc.lastTs = row.ts;
        if (row.noteHash) summaryAcc.uniqueNoteHashes.add(row.noteHash);
        if (row.sourceSummary) summaryAcc.sourceSummaryCount += 1;
        if (row.event === 'artifact_observed') summaryAcc.artifactObservedCount += 1;

        if (row.event === 'source_observed') {
          summaryAcc.sourceObservedCount += 1;
          const key = `${row.ts}::${row.notebookHash || ''}`;
          let batch = sourceBatchByKey.get(key);
          if (!batch) {
            batch = {
              ts: row.ts,
              seq: row.seq,
              notebookHash: row.notebookHash,
              provenanceSource: row.provenanceSource,
              sourceObservedCount: 0,
              sourceTitles: new Set<string>(),
              sourceTypes: new Set<string>(),
              sourceStatuses: new Set<string>(),
              sourceSummaries: [],
              noteHashes: new Set<string>()
            };
            sourceBatchByKey.set(key, batch);
          }
          batch.sourceObservedCount += 1;
          if (row.sourceTitle) batch.sourceTitles.add(row.sourceTitle);
          if (row.sourceType) batch.sourceTypes.add(row.sourceType);
          if (row.sourceStatus) batch.sourceStatuses.add(row.sourceStatus);
          if (row.sourceSummary) {
            const maxChars = 1200;
            const compactSummary =
              row.sourceSummary.length > maxChars ? `${row.sourceSummary.slice(0, maxChars)}…` : row.sourceSummary;
            batch.sourceSummaries.push(compactSummary);
          }
          if (row.noteHash) batch.noteHashes.add(row.noteHash);

          if (row.noteHash) {
            const existing = sourceCatalogByHash.get(row.noteHash);
            if (!existing) {
              sourceCatalogByHash.set(row.noteHash, {
                noteIdHash: row.noteHash,
                sourceTitle: row.sourceTitle,
                sourceType: row.sourceType,
                sourceUrl: row.sourceUrl,
                mentions: 1
              });
            } else {
              existing.mentions += 1;
              if (!existing.sourceTitle && row.sourceTitle) existing.sourceTitle = row.sourceTitle;
              if (!existing.sourceType && row.sourceType) existing.sourceType = row.sourceType;
              if (!existing.sourceUrl && row.sourceUrl) existing.sourceUrl = row.sourceUrl;
            }
          }
          continue;
        }

        passthrough.push({ ts: row.ts, seq: row.seq, payload: buildSinglePayload(row) });
      }
    } finally {
      rl.close();
    }
  }

  const batched: Array<{ ts: string; seq: number; payload: Record<string, unknown> }> = [];
  for (const batch of sourceBatchByKey.values()) {
    batched.push({
      ts: batch.ts,
      seq: batch.seq,
      payload: buildSourceObservedBatchPayload(batch)
    });
  }

  const events = [...passthrough, ...batched].sort((a, b) => a.ts.localeCompare(b.ts) || a.seq - b.seq);
  const total = events.length;
  const startIndex = Math.max(0, total - tail);
  const tailEvents = events.slice(startIndex);
  const messages: NotebookMetaMessage[] = tailEvents.map((e, idx) => ({
    message_id: `nbmeta:${startIndex + idx + 1}`,
    canonical_thread_id: threadId,
    platform: 'notebooklm_meta',
    account_id: null,
    ts: e.ts || '',
    role: 'tool',
    text: buildMessageText(e.payload),
    title: titleFromThreadId(threadId),
    source_id: 'notebooklm_meta',
    source_thread_id: null,
    source_message_id: null
  }));

  const summary = buildSummary(threadId, summaryAcc, total);
  const sources = buildSourceCatalog(sourceCatalogByHash);
  return { title: titleFromThreadId(threadId), total, messages, summary, sources };
}
