import type { DashboardPayload } from '../contracts/dashboard';

export type ThreadRow = {
  threadId: string;
  title: string;
  messageCount: number;
  share?: number;
  colorHex?: string;
  origin?: string;
  firstTs?: string;
  lastTs?: string;
};

export function buildThreadRows(payload: DashboardPayload): ThreadRow[] {
  const byId = new Map<string, ThreadRow>();

  for (const t of payload.chat_threads ?? []) {
    const threadId = t.thread_id;
    const title = (t.title_resolved || t.title || '(no title)').trim() || '(no title)';
    const row: ThreadRow = {
      threadId,
      title,
      messageCount: t.message_count ?? 0,
      origin: t.origin,
      firstTs: t.first_ts,
      lastTs: t.last_ts
    };
    byId.set(threadId, row);
  }

  for (const t of payload.chat_flow?.threads ?? []) {
    const threadId = t.thread_id;
    const existing = byId.get(threadId);
    const title = (t.thread_title || existing?.title || '(no title)').trim() || '(no title)';
    const next: ThreadRow = {
      threadId,
      title,
      messageCount: t.message_count ?? existing?.messageCount ?? 0,
      share: t.share,
      colorHex: t.color_hex,
      origin: existing?.origin,
      firstTs: existing?.firstTs,
      lastTs: existing?.lastTs
    };
    byId.set(threadId, next);
  }

  return [...byId.values()].sort((a, b) => (b.share ?? 0) - (a.share ?? 0) || b.messageCount - a.messageCount);
}

export type WaterfallSegment = {
  hour: number;
  threadId: string;
  threadTitle?: string;
  colorHex?: string;
  threadIndex?: number;
  role?: string;
  switch?: boolean;
  threadStartHour?: number;
  messageCount: number;
  durationSeconds: number;
};

export function buildWaterfallSegments(payload: DashboardPayload): WaterfallSegment[] {
  const items = payload.chat_flow?.waterfall ?? [];
  const segs: WaterfallSegment[] = [];

  const parsedTs: number[] = items.map((it) => {
    const ms = Date.parse(String((it as any)?.ts ?? ''));
    return Number.isFinite(ms) ? ms : NaN;
  });

  function endOfHourMs(ms: number): number {
    const d = new Date(ms);
    d.setUTCMinutes(0, 0, 0);
    return d.getTime() + 3600_000;
  }

  // Group consecutive items within the same hour+thread, and compute a "time weight"
  // (gap to next message within hour; otherwise to hour boundary).
  let cur: WaterfallSegment | null = null;
  for (let i = 0; i < items.length; i++) {
    const it = items[i]!;
    const hour = it.hour;
    const threadId = it.thread_id;
    const threadTitle = it.thread_title;
    const colorHex = it.color_hex;
    const threadIndex = it.color_index;
    const role = it.role;
    const sw = it.switch;
    const threadStartHour = it.thread_start_hour;

    let gap = typeof it.gap_to_next_seconds === 'number' && Number.isFinite(it.gap_to_next_seconds) ? it.gap_to_next_seconds : NaN;
    if (!Number.isFinite(gap) || gap <= 0) {
      const ms = parsedTs[i]!;
      if (Number.isFinite(ms)) {
        const nextMs = parsedTs[i + 1]!;
        const sameHourAsNext = Number.isFinite(nextMs) && items[i + 1]?.hour === hour;
        const endMs = endOfHourMs(ms);
        const target = sameHourAsNext ? nextMs : endMs;
        gap = Math.max(1, Math.round((target - ms) / 1000));
      } else {
        gap = 60;
      }
    }
    // Clamp extreme gaps so a single block can't dominate rendering.
    gap = Math.max(1, Math.min(3600, gap));

    if (cur && cur.hour === hour && cur.threadId === threadId) {
      cur.messageCount += 1;
      cur.durationSeconds += gap;
      continue;
    }
    cur = {
      hour,
      threadId,
      threadTitle,
      colorHex,
      threadIndex,
      role,
      switch: sw,
      threadStartHour,
      messageCount: 1,
      durationSeconds: gap
    };
    segs.push(cur);
  }
  return segs;
}
