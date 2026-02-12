export type TranscriptCue = {
  id: string;
  startSec: number;
  endSec: number;
  startLabel: string;
  endLabel: string;
  text: string;
  sourceLine?: string;
};

type RawSegment = {
  start?: unknown;
  end?: unknown;
  text?: unknown;
};

const TIMECODE_RE = /^(\d{2}):(\d{2}):(\d{2})([.,](\d{1,3}))?$/;
const INLINE_CUE_RE = /(\d{2}:\d{2}:\d{2}[.,]\d{1,3})\s*-->\s*(\d{2}:\d{2}:\d{2}[.,]\d{1,3})\s*(.*)$/;
const BULLET_CUE_RE = /^\s*-\s*\[(\d{2}:\d{2}:\d{2}[.,]\d{1,3})\s*-->\s*(\d{2}:\d{2}:\d{2}[.,]\d{1,3})\]\s*(.*)$/;

function normalizeMillis(msPart: string | undefined): number {
  const raw = String(msPart ?? '').replace(/[^\d]/g, '');
  if (!raw) return 0;
  if (raw.length === 1) return Number(raw) * 100;
  if (raw.length === 2) return Number(raw) * 10;
  return Number(raw.slice(0, 3));
}

export function parseTimecode(value: string): number | null {
  const m = TIMECODE_RE.exec(String(value ?? '').trim());
  if (!m) return null;
  const h = Number(m[1] ?? 0);
  const mm = Number(m[2] ?? 0);
  const ss = Number(m[3] ?? 0);
  const ms = normalizeMillis(m[5]);
  if (!Number.isFinite(h) || !Number.isFinite(mm) || !Number.isFinite(ss) || !Number.isFinite(ms)) return null;
  if (mm > 59 || ss > 59) return null;
  return h * 3600 + mm * 60 + ss + ms / 1000;
}

export function formatTimecode(seconds: number): string {
  const total = Math.max(0, Number(seconds || 0));
  const h = Math.floor(total / 3600);
  const m = Math.floor((total % 3600) / 60);
  const s = Math.floor(total % 60);
  const ms = Math.round((total - Math.floor(total)) * 1000);
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}.${String(ms).padStart(3, '0')}`;
}

function cueFromMatch(startLabel: string, endLabel: string, text: string, line: string, idx: number): TranscriptCue | null {
  const startSec = parseTimecode(startLabel);
  const endSec = parseTimecode(endLabel);
  if (startSec === null || endSec === null || endSec < startSec) return null;
  return {
    id: `cue:${idx.toString().padStart(5, '0')}`,
    startSec,
    endSec,
    startLabel,
    endLabel,
    text: String(text ?? '').trim(),
    sourceLine: line
  };
}

export function parseInlineCue(line: string, idx: number): TranscriptCue | null {
  const raw = String(line ?? '');
  const bullet = BULLET_CUE_RE.exec(raw);
  if (bullet) return cueFromMatch(String(bullet[1]), String(bullet[2]), String(bullet[3] ?? ''), raw, idx);
  const inline = INLINE_CUE_RE.exec(raw);
  if (inline) return cueFromMatch(String(inline[1]), String(inline[2]), String(inline[3] ?? ''), raw, idx);
  return null;
}

export function cuesFromTranscriptText(rawText: string): TranscriptCue[] {
  const lines = String(rawText ?? '').split(/\r?\n/);
  const out: TranscriptCue[] = [];
  for (let i = 0; i < lines.length; i += 1) {
    const cue = parseInlineCue(lines[i] ?? '', i + 1);
    if (cue) out.push(cue);
  }
  return out;
}

export function cuesFromSegments(segments: RawSegment[]): TranscriptCue[] {
  const out: TranscriptCue[] = [];
  for (let i = 0; i < (segments ?? []).length; i += 1) {
    const row = segments[i] ?? {};
    const startLabel = String((row as RawSegment).start ?? '').trim();
    const endLabel = String((row as RawSegment).end ?? '').trim();
    const text = String((row as RawSegment).text ?? '').trim();
    if (!startLabel || !endLabel || !text) continue;
    const startSec = parseTimecode(startLabel);
    const endSec = parseTimecode(endLabel);
    if (startSec === null || endSec === null || endSec < startSec) continue;
    out.push({
      id: `seg:${(i + 1).toString().padStart(5, '0')}`,
      startSec,
      endSec,
      startLabel,
      endLabel,
      text
    });
  }
  return out;
}

export function findActiveCueIndex(cues: TranscriptCue[], currentTimeSec: number): number {
  const t = Number(currentTimeSec || 0);
  if (!Number.isFinite(t)) return -1;
  for (let i = 0; i < (cues ?? []).length; i += 1) {
    const cue = cues[i];
    if (!cue) continue;
    if (t >= cue.startSec && t <= cue.endSec) return i;
  }
  return -1;
}

