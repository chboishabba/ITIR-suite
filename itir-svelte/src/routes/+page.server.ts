import fs from 'node:fs/promises';
import path from 'node:path';
import { spawn } from 'node:child_process';

import { fail, redirect } from '@sveltejs/kit';

import { parseDashboardPayload } from '$lib/sb-dashboard/contracts/parse';
import type {
  DashboardPayload,
  DashboardTimelineEvent,
  DashboardArtifactLink,
  ChatWaterfallItem
} from '$lib/sb-dashboard/contracts/dashboard';

function isDateText(v: string): boolean {
  return /^\d{4}-\d{2}-\d{2}$/.test(v);
}

function resolveRunsRoot(runsRootEnv: string | undefined): string {
  // Normalize to an absolute path so loaders and the Python runner agree even when
  // SB_RUNS_ROOT is set as a relative path.
  const fallback = path.resolve('..', 'StatiBaker', 'runs');
  const raw = runsRootEnv && runsRootEnv.trim() ? runsRootEnv.trim() : fallback;
  return path.resolve(raw);
}

async function tryReadJson(p: string): Promise<unknown | null> {
  try {
    const raw = await fs.readFile(p, 'utf-8');
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

type NotebookMetaRow = {
  threadId: string;
  title: string;
  messageCount: number;
  origin: string;
  sources: string[];
  metaOnly: boolean;
  firstTs?: string;
  lastTs?: string;
};

function shortHash(value: string): string {
  const clean = value.replace(/^sha256:/i, '').trim();
  if (!clean) return '';
  return clean.length > 12 ? `${clean.slice(0, 12)}...` : clean;
}

function minIso(a?: string, b?: string): string | undefined {
  if (!a) return b;
  if (!b) return a;
  return b < a ? b : a;
}

function maxIso(a?: string, b?: string): string | undefined {
  if (!a) return b;
  if (!b) return a;
  return b > a ? b : a;
}

async function loadNotebookMetaRowsForDate(runsRoot: string, date: string): Promise<NotebookMetaRow[]> {
  const file = path.join(runsRoot, date, 'logs', 'notes', `${date}.jsonl`);
  let raw = '';
  try {
    raw = await fs.readFile(file, 'utf-8');
  } catch {
    return [];
  }

  const byId = new Map<string, NotebookMetaRow>();
  for (const line of raw.split(/\r?\n/g)) {
    const text = line.trim();
    if (!text) continue;
    let record: any;
    try {
      record = JSON.parse(text);
    } catch {
      continue;
    }

    if (String(record?.signal ?? '').trim().toLowerCase() !== 'notes_meta') continue;
    if (String(record?.app ?? '').trim().toLowerCase() !== 'notebooklm') continue;

    const notebookHash = String(record?.notebook_id_hash ?? '').trim();
    const isScoped = Boolean(notebookHash);
    const id = isScoped ? `meta:notebooklm:${notebookHash}` : 'meta:notebooklm:unscoped';
    const title = isScoped ? `NotebookLM ${shortHash(notebookHash)}` : 'NotebookLM (unscoped metadata)';
    const ts = String(record?.ts ?? '').trim() || undefined;

    const current = byId.get(id) ?? {
      threadId: id,
      title,
      messageCount: 0,
      origin: 'notebooklm',
      sources: ['notebooklm (meta-only)'],
      metaOnly: true
    };

    current.messageCount += 1;
    current.firstTs = minIso(current.firstTs, ts);
    current.lastTs = maxIso(current.lastTs, ts);
    byId.set(id, current);
  }

  return [...byId.values()].sort((a, b) => b.messageCount - a.messageCount || a.title.localeCompare(b.title));
}

function dateRangeInclusive(start: string, end: string): string[] {
  const out: string[] = [];
  // dates are ISO so lexical order matches chronological order.
  if (start > end) [start, end] = [end, start];
  const partsA = start.split('-').map((x) => Number(x));
  const partsB = end.split('-').map((x) => Number(x));
  if (partsA.length !== 3 || partsB.length !== 3) return [];
  const [sy, sm, sd] = partsA as [number, number, number];
  const [ey, em, ed] = partsB as [number, number, number];
  if (![sy, sm, sd, ey, em, ed].every((n) => Number.isFinite(n))) return [];
  const startDate = new Date(Date.UTC(sy, sm - 1, sd));
  const endDate = new Date(Date.UTC(ey, em - 1, ed));
  for (let d = startDate; d <= endDate; d = new Date(d.getTime() + 86400_000)) {
    out.push(d.toISOString().slice(0, 10));
  }
  return out;
}

async function listAvailableDates(runsRoot: string): Promise<string[]> {
  try {
    const entries = await fs.readdir(runsRoot, { withFileTypes: true });
    const dates = entries
      .filter((e) => e.isDirectory() && isDateText(e.name))
      .map((e) => e.name)
      .sort();
    // Only keep dates that look usable (some output exists).
    const out: string[] = [];
    for (const d of dates) {
      const p = path.join(runsRoot, d, 'outputs', 'dashboard.json');
      const pAll = path.join(runsRoot, d, 'outputs', 'dashboard_all.json');
      const raw = (await tryReadJson(p)) ?? (await tryReadJson(pAll));
      if (raw) out.push(d);
    }
    return out;
  } catch {
    return [];
  }
}

async function loadDashboardForDate(runsRoot: string, date: string): Promise<{ payload: DashboardPayload; source: string } | null> {
  const pAll = path.join(runsRoot, date, 'outputs', 'dashboard_all.json');
  const p = path.join(runsRoot, date, 'outputs', 'dashboard.json');
  const rawAll = await tryReadJson(pAll);
  if (rawAll) return { payload: parseDashboardPayload(rawAll), source: pAll };
  const raw = await tryReadJson(p);
  if (raw) return { payload: parseDashboardPayload(raw), source: p };
  return null;
}

async function isWritableDir(dir: string): Promise<boolean> {
  try {
    await fs.mkdir(dir, { recursive: true });
    const probe = path.join(dir, `.itir_svelte_write_probe_${Date.now()}_${Math.random().toString(16).slice(2)}`);
    await fs.writeFile(probe, 'ok', 'utf-8');
    await fs.unlink(probe);
    return true;
  } catch {
    return false;
  }
}

async function addArtifactMtimes(links: DashboardArtifactLink[] | undefined): Promise<DashboardArtifactLink[] | undefined> {
  if (!links || !links.length) return links;
  const MAX = 200;
  const slice = links.slice(0, MAX);
  const out: DashboardArtifactLink[] = await Promise.all(
    slice.map(async (l) => {
      try {
        const st = await fs.stat(l.path);
        const iso = st.mtime.toISOString();
        const hour = Number(iso.slice(11, 13));
        return { ...l, mtime_iso: iso, mtime_hour: Number.isFinite(hour) ? hour : undefined };
      } catch {
        return l;
      }
    })
  );
  return links.length > MAX ? [...out, ...links.slice(MAX)] : out;
}

function runBuildDashboard(repoRoot: string, runsRoot: string, date: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const script = path.join(repoRoot, 'StatiBaker', 'scripts', 'build_dashboard.py');
    const args = [script, '--date', date, '--runs-root', runsRoot, '--repo-root', repoRoot];
    const child = spawn('python3', args, { cwd: repoRoot, stdio: ['ignore', 'pipe', 'pipe'] });
    let stdout = '';
    let stderr = '';
    child.stdout.on('data', (d) => (stdout += String(d)));
    child.stderr.on('data', (d) => (stderr += String(d)));
    child.on('error', (err) => reject(err));
    child.on('close', (code) => {
      if (code === 0) return resolve();
      reject(new Error(`build_dashboard.py failed for ${date} (exit ${code}).\n${stderr || stdout}`));
    });
  });
}

function weekdayIndex(dateText: string): number {
  // Monday=0..Sunday=6
  const parts = dateText.split('-').map((x) => Number(x));
  if (parts.length !== 3) return 0;
  const [y, m, d] = parts as [number, number, number];
  const dt = new Date(Date.UTC(y, m - 1, d));
  // JS: Sunday=0..Saturday=6 => map to Monday=0..Sunday=6
  const js = dt.getUTCDay();
  return js === 0 ? 6 : js - 1;
}

type Heatmaps = {
  weekday_names: string[];
  weekday_day_counts: number[];
  lanes: string[];
  lane_labels: Record<string, string>;
  lane_totals: Record<string, number>;
  default_selected: string[];
  series: Record<string, number[][]>;
};

function emptyMatrix(): number[][] {
  return Array.from({ length: 7 }, () => Array.from({ length: 24 }, () => 0));
}

function buildHeatmaps(dailyPayloads: Array<{ date: string; payload: DashboardPayload }>): Heatmaps {
  const weekday_day_counts = Array.from({ length: 7 }, () => 0);
  const lanes = ['chat', 'shell', 'git', 'pr', 'git_branch', 'input', 'window', 'activity', 'media', 'calendar'];
  const lane_labels: Record<string, string> = {
    chat: 'Chat',
    shell: 'Shell',
    git: 'Git commits',
    pr: 'PR events',
    git_branch: 'Git branch events',
    input: 'Input',
    window: 'Window focus',
    activity: 'Activity sessions',
    media: 'Media',
    calendar: 'Calendar'
  };
  const matrices: Record<string, number[][]> = Object.fromEntries(lanes.map((l) => [l, emptyMatrix()]));

  for (const { date, payload } of dailyPayloads) {
    const freq = payload.frequency_by_hour ?? {};
    const weekday = weekdayIndex(date);
    weekday_day_counts[weekday] = (weekday_day_counts[weekday] ?? 0) + 1;
    for (const lane of lanes) {
      const bins = (freq as any)[lane];
      if (!Array.isArray(bins) || bins.length !== 24) continue;
      const row = matrices[lane]?.[weekday];
      if (!row) continue;
      for (let hour = 0; hour < 24; hour++) row[hour] = (row[hour] ?? 0) + (Number(bins[hour] ?? 0) || 0);
    }
  }

  const lane_totals: Record<string, number> = {};
  for (const lane of lanes) {
    let t = 0;
    for (const row of matrices[lane] ?? []) for (const v of row) t += Number(v) || 0;
    lane_totals[lane] = t;
  }
  const default_selected = lanes.filter((l) => (lane_totals[l] ?? 0) > 0);

  return {
    weekday_names: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    weekday_day_counts,
    lanes,
    lane_labels,
    lane_totals,
    default_selected,
    series: matrices
  };
}

function sumLane(a: number[] | undefined, b: number[] | undefined): number[] {
  const out = Array.from({ length: 24 }, () => 0);
  const aa = a ?? [];
  const bb = b ?? [];
  for (let i = 0; i < 24; i++) {
    out[i] = (aa[i] ?? 0) + (bb[i] ?? 0);
  }
  return out;
}

function mergeCountMaps(a: unknown, b: unknown): Record<string, number> {
  const out: Record<string, number> = {};
  const add = (v: unknown) => {
    if (!v) return;
    if (Array.isArray(v)) {
      for (const k of v) {
        const kk = String(k);
        out[kk] = (out[kk] ?? 0) + 1;
      }
      return;
    }
    if (typeof v === 'object') {
      for (const [k, val] of Object.entries(v as Record<string, unknown>)) {
        const n = typeof val === 'number' && Number.isFinite(val) ? val : Number(String(val)) || 0;
        out[k] = (out[k] ?? 0) + n;
      }
    }
  };
  add(a);
  add(b);
  return out;
}

function viridisColor(index: number): string {
  const palette = ['#440154', '#46327E', '#365C8D', '#277F8E', '#1FA187', '#4AC16D', '#A0DA39', '#FDE725'];
  return palette[Math.abs(index) % palette.length] ?? '#6b7280';
}

function stableHash(text: string): number {
  // Deterministic, cheap hash for stable color assignment.
  let h = 2166136261;
  for (let i = 0; i < text.length; i++) {
    h ^= text.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

function hourFromIso(iso: unknown): number | null {
  if (typeof iso !== 'string') return null;
  if (iso.length < 13) return null;
  const h = Number(iso.slice(11, 13));
  if (!Number.isFinite(h)) return null;
  if (h < 0 || h > 23) return null;
  return h;
}

function buildRangePayload(dailies: DashboardPayload[], { start, end }: { start: string; end: string }): DashboardPayload {
  const warnings: string[] = [];
  const daysInRange = dateRangeInclusive(start, end).length || dailies.length || 1;

  // Aggregate frequency_by_hour
  const freq: Record<string, number[]> = {};
  for (const p of dailies) {
    const by = p.frequency_by_hour ?? {};
    for (const [lane, vals] of Object.entries(by)) {
      freq[lane] = sumLane(freq[lane], Array.isArray(vals) ? vals : undefined);
    }
  }

  // Merge timelines and keep newest N.
  const timeline: DashboardTimelineEvent[] = [];
  for (const p of dailies) {
    for (const e of p.timeline ?? []) timeline.push(e);
  }
  timeline.sort((a, b) => String(a.ts).localeCompare(String(b.ts)));
  const maxTimeline = 2000;
  const trimmed = timeline.length > maxTimeline ? timeline.slice(-maxTimeline) : timeline;
  if (timeline.length > maxTimeline) warnings.push(`Timeline truncated to ${maxTimeline} events (newest retained).`);

  // Artifacts: group by path and remember which days referenced them.
  // This avoids repeating identical absolute paths with date-prefixed labels.
  const artifactByPath = new Map<
    string,
    { path: string; label: string; seen_count: number; seen_dates: Set<string>; seen_hour_bins: number[] }
  >();
  for (const p of dailies) {
    const date = p.date;
    const genHour = hourFromIso((p as any).generated_at);
    for (const a of p.artifact_links ?? []) {
      const absPath = String(a.path ?? '');
      if (!absPath) continue;
      const base = path.basename(absPath) || absPath;
      const cur =
        artifactByPath.get(absPath) ??
        ({
          path: absPath,
          label: base,
          seen_count: 0,
          seen_dates: new Set<string>(),
          seen_hour_bins: Array.from({ length: 24 }, () => 0)
        } as {
          path: string;
          label: string;
          seen_count: number;
          seen_dates: Set<string>;
          seen_hour_bins: number[];
        });
      cur.seen_count += 1;
      if (date) cur.seen_dates.add(date);
      if (genHour !== null) cur.seen_hour_bins[genHour] = (cur.seen_hour_bins[genHour] ?? 0) + 1;
      artifactByPath.set(absPath, cur);
    }
  }
  const artifacts: DashboardArtifactLink[] = [...artifactByPath.values()]
    .map((a) => ({
      label: a.label,
      path: a.path,
      seen_count: a.seen_count,
      seen_dates: [...a.seen_dates].sort(),
      seen_hour_bins: a.seen_hour_bins
    }))
    .sort((a, b) => (b.seen_count ?? 0) - (a.seen_count ?? 0) || String(a.label).localeCompare(String(b.label)));

  // Summary: compute only what UI needs today.
  let chatMessages = 0;
  let chatSwitches = 0;
  let shellCommands = 0;
  let gitCommits = 0;
  let mediaEvents = 0;
  const uniqueThreads = new Set<string>();

  for (const p of dailies) {
    const s = p.summary ?? {};
    const n = (k: string) => (typeof s[k] === 'number' && Number.isFinite(s[k] as number) ? (s[k] as number) : 0);
    chatMessages += n('chat_messages');
    chatSwitches += n('chat_switches');
    shellCommands += n('shell_commands');
    gitCommits += n('git_commits');
    mediaEvents += n('media_events');
    for (const t of p.chat_threads ?? []) uniqueThreads.add(t.thread_id);
  }

  const summary: Record<string, unknown> = {
    chat_messages: chatMessages,
    chat_switches: chatSwitches,
    chat_switch_rate: chatMessages ? chatSwitches / chatMessages : 0,
    shell_commands: shellCommands,
    git_commits: gitCommits,
    media_events: mediaEvents,
    chat_threads: uniqueThreads.size
  };

  // NotebookLM/notes metadata: aggregate nested counters.
  const notesTotals: any = { total_events: 0, notebooklm_events: 0, app_counts: {}, lifecycle: {}, warnings: [] as string[] };
  const addBucket = (dst: any, src: any) => {
    if (!src || typeof src !== 'object') return;
    for (const k of ['created', 'modified', 'moved', 'deleted', 'seen', 'other']) {
      const v = (src as any)[k];
      if (typeof v === 'number' && Number.isFinite(v)) dst[k] = (dst[k] ?? 0) + v;
    }
  };
  for (const p of dailies) {
    const ns = (p as any).notes_meta_summary;
    if (!ns || typeof ns !== 'object') continue;
    notesTotals.total_events += typeof (ns as any).total_events === 'number' ? (ns as any).total_events : 0;
    notesTotals.notebooklm_events += typeof (ns as any).notebooklm_events === 'number' ? (ns as any).notebooklm_events : 0;
    const lc = (ns as any).lifecycle;
    if (lc && typeof lc === 'object') {
      for (const [bucket, vals] of Object.entries(lc as Record<string, unknown>)) {
        const dst = notesTotals.lifecycle[bucket] ?? {};
        addBucket(dst, vals);
        notesTotals.lifecycle[bucket] = dst;
      }
    }
    const app = (ns as any).app_counts;
    if (app && typeof app === 'object') {
      for (const [k, v] of Object.entries(app as Record<string, unknown>)) {
        const n = typeof v === 'number' && Number.isFinite(v) ? v : Number(String(v)) || 0;
        notesTotals.app_counts[k] = (notesTotals.app_counts[k] ?? 0) + n;
      }
    }
  }

  const notesMetaSummary =
    notesTotals.total_events || notesTotals.notebooklm_events
      ? notesTotals
      : undefined;

  const notesMetaAveragesPerDay =
    notesMetaSummary
      ? {
          total_events: notesTotals.total_events / daysInRange,
          notebooklm_events: notesTotals.notebooklm_events / daysInRange
        }
      : undefined;

  // Chat threads: merge across days.
  type ThreadAgg = {
    thread_id: string;
    title?: string;
    title_resolved?: string;
    origin?: string;
    first_ts?: string;
    last_ts?: string;
    first_user_preview?: string;
    message_count: number;
    roles?: Record<string, number>;
    source_ids?: Record<string, number>;
  };
  const threads = new Map<string, ThreadAgg>();
  for (const p of dailies) {
    for (const t of p.chat_threads ?? []) {
      const id = t.thread_id;
      const cur = threads.get(id) ?? { thread_id: id, message_count: 0 };
      cur.message_count += t.message_count ?? 0;
      cur.title = cur.title ?? t.title;
      cur.title_resolved = cur.title_resolved ?? t.title_resolved;
      cur.origin = cur.origin ?? t.origin;
      cur.first_user_preview = cur.first_user_preview ?? t.first_user_preview;
      cur.first_ts = !cur.first_ts || (t.first_ts && t.first_ts < cur.first_ts) ? (t.first_ts ?? cur.first_ts) : cur.first_ts;
      cur.last_ts = !cur.last_ts || (t.last_ts && t.last_ts > cur.last_ts) ? (t.last_ts ?? cur.last_ts) : cur.last_ts;
      cur.roles = mergeCountMaps(cur.roles, (t as any).roles);
      cur.source_ids = mergeCountMaps(cur.source_ids, (t as any).source_ids);
      threads.set(id, cur);
    }
  }
  const chat_threads = [...threads.values()].sort((a, b) => b.message_count - a.message_count);

  // Chat flow: synthesize a stable per-thread color assignment and (optionally) a combined waterfall.
  const totalMsgs = chat_threads.reduce((acc, t) => acc + (t.message_count ?? 0), 0) || 1;
  const threadOrder = new Map<string, number>();
  for (let i = 0; i < chat_threads.length; i++) threadOrder.set(chat_threads[i]!.thread_id, i);

  const chat_flow_threads = chat_threads.map((t) => {
    const idx = threadOrder.get(t.thread_id) ?? 0;
    const color_index = idx;
    const color_hex = viridisColor(idx);
    return {
      thread_id: t.thread_id,
      thread_key: t.thread_id,
      thread_title: (t.title_resolved || t.title || '(no title)')?.trim?.() || '(no title)',
      message_count: t.message_count,
      share: (t.message_count ?? 0) / totalMsgs,
      color_index,
      color_hex,
      thread_start_ts: t.first_ts,
      thread_start_hour: t.first_ts ? Number(String(t.first_ts).slice(11, 13)) : undefined
    };
  });

  const waterfall: ChatWaterfallItem[] = [];
  for (const p of dailies) {
    for (const it of p.chat_flow?.waterfall ?? []) {
      const idx = threadOrder.get(it.thread_id) ?? (stableHash(it.thread_id) % 64);
      waterfall.push({
        ts: it.ts,
        hour: it.hour,
        role: it.role,
        switch: it.switch,
        thread_id: it.thread_id,
        thread_key: it.thread_key ?? it.thread_id,
        thread_title: (threads.get(it.thread_id)?.title_resolved || threads.get(it.thread_id)?.title || it.thread_title || '(no title)'),
        thread_start_ts: threads.get(it.thread_id)?.first_ts ?? it.thread_start_ts,
        thread_start_hour: threads.get(it.thread_id)?.first_ts ? Number(String(threads.get(it.thread_id)!.first_ts).slice(11, 13)) : it.thread_start_hour,
        gap_to_next_seconds: it.gap_to_next_seconds,
        color_index: idx,
        color_hex: viridisColor(idx)
      });
    }
  }
  waterfall.sort((a, b) => String(a.ts).localeCompare(String(b.ts)));
  const maxWaterfall = 6000;
  const waterfallTrimmed = waterfall.length > maxWaterfall ? waterfall.slice(-maxWaterfall) : waterfall;
  if (waterfall.length > maxWaterfall) warnings.push(`Chat waterfall truncated to ${maxWaterfall} items (newest retained).`);

  const chat_flow = {
    message_count: totalMsgs,
    thread_count: chat_threads.length,
    switch_count: chatSwitches,
    switch_rate: totalMsgs ? chatSwitches / totalMsgs : 0,
    dominant_thread_share: chat_flow_threads.length ? (chat_flow_threads[0]?.share ?? 0) : 0,
    active_hours: dailies.reduce((acc, p) => acc + (typeof p.summary?.['chat_active_hours'] === 'number' ? (p.summary['chat_active_hours'] as number) : 0), 0),
    first_ts: chat_threads.length ? chat_threads.reduce((m, t) => (!m || (t.first_ts && t.first_ts < m) ? (t.first_ts ?? m) : m), '') : undefined,
    last_ts: chat_threads.length ? chat_threads.reduce((m, t) => (!m || (t.last_ts && t.last_ts > m) ? (t.last_ts ?? m) : m), '') : undefined,
    threads: chat_flow_threads,
    waterfall: waterfallTrimmed,
    waterfall_render_limit: maxWaterfall,
    waterfall_truncated: waterfall.length > maxWaterfall,
    hour_bins: []
  };

  // Tool use: coarse aggregation of families.
  const familyAgg = new Map<string, { family: string; count: number; variants: Map<string, number> }>();
  let exec_command_count = 0;
  let unique_commands = 0;
  for (const p of dailies) {
    const tu = p.tool_use_summary as any;
    if (!tu || typeof tu !== 'object') continue;
    exec_command_count += typeof tu.exec_command_count === 'number' ? tu.exec_command_count : 0;
    unique_commands += typeof tu.unique_commands === 'number' ? tu.unique_commands : 0;
    const fams = Array.isArray(tu.families) ? tu.families : [];
    for (const f of fams) {
      const name = String(f?.family ?? '').trim();
      if (!name) continue;
      const cur = familyAgg.get(name) ?? { family: name, count: 0, variants: new Map<string, number>() };
      cur.count += Number(f?.count ?? 0) || 0;
      const variants = Array.isArray(f?.variants) ? f.variants : [];
      for (const v of variants) {
        const cmd = String(v?.command ?? '').trim();
        if (!cmd) continue;
        cur.variants.set(cmd, (cur.variants.get(cmd) ?? 0) + (Number(v?.count ?? 0) || 0));
      }
      familyAgg.set(name, cur);
    }
  }
  const families = [...familyAgg.values()]
    .sort((a, b) => b.count - a.count)
    .slice(0, 30)
    .map((f) => ({
      family: f.family,
      count: f.count,
      unique_variants: f.variants.size,
      variants: [...f.variants.entries()]
        .sort((a, b) => b[1] - a[1])
        .slice(0, 12)
        .map(([command, count]) => ({ command, count }))
    }));
  const tool_use_summary = families.length
    ? {
        source: 'range',
        exec_command_count,
        unique_commands,
        families
      }
    : undefined;

  return {
    date: end,
    period_start: start,
    period_end: end,
    days: dailies.length,
    generated_at: new Date().toISOString(),
    chat_scope_mode: 'range',
    chat_scope_thread_count: uniqueThreads.size,
    summary,
    frequency_by_hour: freq,
    chat_threads,
    chat_flow,
    tool_use_summary,
    notes_meta_summary: notesMetaSummary,
    notes_meta_averages_per_day: notesMetaAveragesPerDay,
    artifact_links: artifacts,
    timeline: trimmed,
    warnings
  } as DashboardPayload;
}

export async function load({ url }: { url: URL }) {
  const envPath = process.env.SB_DASHBOARD_JSON;
  const runsRootEnv = process.env.SB_RUNS_ROOT;
  const dateEnv = process.env.SB_DATE;

  if (envPath) {
    const raw = await tryReadJson(envPath);
    if (!raw) throw new Error(`SB_DASHBOARD_JSON not readable: ${envPath}`);
    try {
      return {
        payload: parseDashboardPayload(raw),
        source: envPath,
        parseError: null as string | null,
        availableDates: [] as string[],
        selected: { start: '', end: '' },
        notebookMetaRows: [] as NotebookMetaRow[]
      };
    } catch (err) {
      return {
        payload: raw,
        source: envPath,
        parseError: err instanceof Error ? err.message : String(err),
        availableDates: [] as string[],
        selected: { start: '', end: '' },
        notebookMetaRows: [] as NotebookMetaRow[]
      };
    }
  }

  const runsRoot = resolveRunsRoot(runsRootEnv);
  const availableDates = await listAvailableDates(runsRoot);

  const endCandidate = url.searchParams.get('end') ?? dateEnv ?? availableDates[availableDates.length - 1] ?? '2026-02-03';
  const startCandidate = url.searchParams.get('start') ?? endCandidate;
  const explicitSelection = url.searchParams.has('start') || url.searchParams.has('end') || Boolean(dateEnv) || Boolean(runsRootEnv);

  const end = isDateText(endCandidate) ? endCandidate : (dateEnv ?? '2026-02-03');
  const start = isDateText(startCandidate) ? startCandidate : end;

  // Cap range to avoid accidental massive reads.
  const dates = dateRangeInclusive(start, end);
  const MAX_DAYS = 31;
  const selectedDates = dates.slice(0, MAX_DAYS);
  const truncated = dates.length > MAX_DAYS;

  const dailies: DashboardPayload[] = [];
  const dailyTuples: Array<{ date: string; payload: DashboardPayload }> = [];
  const notebookMetaById = new Map<string, NotebookMetaRow>();
  const sources: string[] = [];
  const warnings: string[] = [];
  const missingDates: string[] = [];
  for (const d of selectedDates) {
    const loaded = await loadDashboardForDate(runsRoot, d);
    if (!loaded) {
      warnings.push(`Missing dashboard for ${d}`);
      missingDates.push(d);
      continue;
    }
    dailies.push(loaded.payload);
    dailyTuples.push({ date: d, payload: loaded.payload });
    sources.push(loaded.source);
    for (const row of await loadNotebookMetaRowsForDate(runsRoot, d)) {
      const current = notebookMetaById.get(row.threadId) ?? {
        ...row,
        messageCount: 0,
        firstTs: undefined,
        lastTs: undefined
      };
      current.messageCount += row.messageCount;
      current.firstTs = minIso(current.firstTs, row.firstTs);
      current.lastTs = maxIso(current.lastTs, row.lastTs);
      notebookMetaById.set(row.threadId, current);
    }
  }
  const notebookMetaRows = [...notebookMetaById.values()].sort(
    (a, b) => b.messageCount - a.messageCount || a.title.localeCompare(b.title)
  );

  if (!dailies.length) {
    if (explicitSelection) {
      return {
        payload: { date: end, generated_at: new Date().toISOString(), warnings } as DashboardPayload,
        source: `range:${start}..${end}`,
        parseError: null as string | null,
        availableDates,
        selected: { start, end },
        missingDates,
        heatmaps: buildHeatmaps([]),
        notebookMetaRows: [] as NotebookMetaRow[]
      };
    }

    // Repo-local fallback for first render (no env + no query params).
    const fallback = path.resolve('..', 'StatiBaker', 'runs', '2026-02-03', 'outputs', 'dashboard_all.json');
    const raw = await tryReadJson(fallback);
    if (!raw) throw new Error(`No dashboard JSON found. Set SB_DASHBOARD_JSON or SB_RUNS_ROOT+SB_DATE. Tried: ${fallback}`);
    try {
      const payload = parseDashboardPayload(raw);
      return {
        payload,
        source: fallback,
        parseError: null as string | null,
        availableDates,
        selected: { start: payload.date, end: payload.date },
        missingDates: [] as string[],
        heatmaps: buildHeatmaps([{ date: payload.date, payload }]),
        notebookMetaRows: [] as NotebookMetaRow[]
      };
    } catch (err) {
      return {
        payload: raw,
        source: fallback,
        parseError: err instanceof Error ? err.message : String(err),
        availableDates,
        selected: { start: end, end: end },
        missingDates: [] as string[],
        heatmaps: buildHeatmaps([]),
        notebookMetaRows: [] as NotebookMetaRow[]
      };
    }
  }

  if (truncated) warnings.push(`Range truncated to ${MAX_DAYS} days (start..end too large).`);

  let payload: DashboardPayload;
  if (start === end) {
    payload = dailies[dailies.length - 1]!;
  } else {
    payload = buildRangePayload(dailies, { start, end });
    payload.warnings = [...(payload.warnings ?? []), ...warnings];
  }

  // Enrich artifacts with filesystem mtime (best-effort local convenience).
  if (payload.artifact_links) payload.artifact_links = await addArtifactMtimes(payload.artifact_links);

  const builtCount = Number(url.searchParams.get('built') ?? 0) || 0;
  const failedCount = Number(url.searchParams.get('failed') ?? 0) || 0;

  return {
    payload,
    source: sources.length === 1 ? sources[0] : `range:${start}..${end}`,
    parseError: null as string | null,
    availableDates,
    selected: { start, end },
    missingDates,
    heatmaps: buildHeatmaps(dailyTuples),
    runsRoot,
    buildSummary: builtCount || failedCount ? { built: builtCount, failed: failedCount } : null,
    notebookMetaRows
  };
}

export const actions = {
  buildMissing: async ({ request, url }: { request: Request; url: URL }) => {
    const form = await request.formData();
    const start = String(form.get('start') ?? '');
    const end = String(form.get('end') ?? '');
    if (!isDateText(start) || !isDateText(end)) {
      return fail(400, { ok: false, error: 'Invalid start/end date.' });
    }

    const runsRoot = resolveRunsRoot(process.env.SB_RUNS_ROOT);
    const repoRoot = path.resolve('..');
    if (!(await isWritableDir(runsRoot))) {
      return fail(400, {
        ok: false,
        error:
          `SB_RUNS_ROOT is not writable: ${runsRoot}\n` +
          `Fix by pointing SB_RUNS_ROOT at a writable directory (recommended: ../StatiBaker/runs_local after chown), then restart dev server.`
      });
    }

    const wanted = dateRangeInclusive(start, end);
    const max = 31;
    const dates = wanted.slice(0, max);

    const built: string[] = [];
    const failed: Array<{ date: string; error: string }> = [];
    for (const d of dates) {
      const exists = await loadDashboardForDate(runsRoot, d);
      if (exists) continue;
      try {
        await runBuildDashboard(repoRoot, runsRoot, d);
        built.push(d);
      } catch (err) {
        failed.push({ date: d, error: err instanceof Error ? err.message : String(err) });
      }
    }

    // Redirect back to GET so load() picks up new files.
    const next = new URL(url);
    next.searchParams.set('start', start);
    next.searchParams.set('end', end);
    if (built.length) next.searchParams.set('built', String(built.length));
    if (failed.length) next.searchParams.set('failed', String(failed.length));
    throw redirect(303, next.toString());
  }
};
