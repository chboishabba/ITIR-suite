import type { DashboardTimelineEvent } from '../contracts/dashboard';

export type RibbonLensId = 'chat_chars' | 'chat_events' | 'events';

export type RibbonLayoutMode = 'time' | 'mass';

export type RibbonContributor = {
  id: string;
  label: string;
  mass: number;
  eventCount: number;
  share: number;
};

export type RibbonThreadCallout = {
  id: string;
  anchor_t: number;
  segment_id: string;
  kind: 'annotation';
  label: string;
  mass: number;
  event_count: number;
  visibility_scope: 'public';
};

export type RibbonSegment = {
  id: string;
  label: string;
  hour: number;
  t_start: number;
  t_end: number;
  mass: number;
  width_norm: number;
  event_count: number;
  contributors: RibbonContributor[];
  threads: RibbonThreadCallout[];
  top_detail: string[];
};

export type TimelineRibbonModel = {
  spine: {
    domain: {
      type: 'discrete';
      start: number;
      end: number;
    };
  };
  lens: {
    id: RibbonLensId;
    name: string;
    units: string;
    definition: string;
    normalization_basis: string;
    total_mass: number;
  };
  segments: RibbonSegment[];
  threads: RibbonThreadCallout[];
  zero_mass: boolean;
};

const LENS_META: Record<
  RibbonLensId,
  {
    name: string;
    units: string;
    definition: string;
    normalizationBasis: string;
  }
> = {
  chat_chars: {
    name: 'Chat chars',
    units: 'chars',
    definition: 'Sum of estimated chat character counts per timeline hour.',
    normalizationBasis: 'Normalized over total chat chars in the selected timeline payload.'
  },
  chat_events: {
    name: 'Chat events',
    units: 'events',
    definition: 'Count of chat timeline events per hour.',
    normalizationBasis: 'Normalized over total chat event count in the selected timeline payload.'
  },
  events: {
    name: 'All events',
    units: 'events',
    definition: 'Count of all timeline events per hour.',
    normalizationBasis: 'Normalized over total event count in the selected timeline payload.'
  }
};

const ROLE_LABELS: Record<string, string> = {
  user: 'User',
  assistant: 'Assistant',
  tool: 'Tool',
  system: 'System',
  unknown: 'Unknown'
};

function eventRole(event: DashboardTimelineEvent): string {
  const role = (event.meta as any)?.role;
  if (typeof role !== 'string') return 'unknown';
  const clean = role.trim().toLowerCase();
  return clean || 'unknown';
}

function eventMass(event: DashboardTimelineEvent, lensId: RibbonLensId): number {
  if (lensId === 'events') return 1;
  if (lensId === 'chat_events') return event.kind === 'chat' ? 1 : 0;
  if (event.kind !== 'chat') return 0;
  const chars = (event.meta as any)?.chars;
  return typeof chars === 'number' && Number.isFinite(chars) ? Math.max(0, chars) : 0;
}

function threadKey(event: DashboardTimelineEvent): { key: string; label: string } | null {
  const meta = (event.meta as any) ?? {};
  const id = typeof meta.thread_id === 'string' ? meta.thread_id.trim() : '';
  const title = typeof meta.thread_title === 'string' ? meta.thread_title.trim() : '';
  if (id) return { key: id, label: title || id };
  const source = typeof meta.source_id === 'string' ? meta.source_id.trim() : typeof meta.source === 'string' ? meta.source.trim() : '';
  if (!source) return null;
  return { key: `src:${source}`, label: source };
}

function hourLabel(hour: number): string {
  return String(hour).padStart(2, '0');
}

function topDetails(eventCount: number, contributors: RibbonContributor[], threads: RibbonThreadCallout[]): string[] {
  const lines: string[] = [];
  lines.push(`${eventCount} events`);
  if (contributors.length) {
    lines.push(
      contributors
        .slice(0, 3)
        .map((row) => `${row.label} ${row.share.toFixed(1)}%`)
        .join(' | ')
    );
  }
  if (threads.length) {
    lines.push(
      threads
        .slice(0, 2)
        .map((row) => `${row.label} (${row.event_count})`)
        .join(' | ')
    );
  }
  return lines;
}

export function buildTimelineRibbonModel(events: DashboardTimelineEvent[] | undefined, lensId: RibbonLensId): TimelineRibbonModel {
  const meta = LENS_META[lensId];
  const byHour = Array.from({ length: 24 }, (_, hour) => ({
    hour,
    mass: 0,
    eventCount: 0,
    roles: new Map<string, { mass: number; eventCount: number }>(),
    threads: new Map<string, { label: string; mass: number; eventCount: number }>()
  }));

  for (const event of events ?? []) {
    const hour = typeof event.hour === 'number' ? event.hour : Number(String(event.ts ?? '').slice(11, 13));
    if (!Number.isFinite(hour) || hour < 0 || hour > 23) continue;
    const bucket = byHour[hour];
    if (!bucket) continue;
    const mass = eventMass(event, lensId);
    const role = eventRole(event);
    const roleRow = bucket.roles.get(role) ?? { mass: 0, eventCount: 0 };
    roleRow.mass += mass;
    roleRow.eventCount += 1;
    bucket.roles.set(role, roleRow);
    const thread = threadKey(event);
    if (thread) {
      const row = bucket.threads.get(thread.key) ?? { label: thread.label, mass: 0, eventCount: 0 };
      row.mass += mass;
      row.eventCount += 1;
      bucket.threads.set(thread.key, row);
    }
    bucket.mass += mass;
    bucket.eventCount += 1;
  }

  const totalMass = byHour.reduce((sum, row) => sum + row.mass, 0);
  const segments: RibbonSegment[] = byHour.map((row) => {
    const contributors = [...row.roles.entries()]
      .map(([id, value]) => ({
        id,
        label: ROLE_LABELS[id] ?? id,
        mass: value.mass,
        eventCount: value.eventCount,
        share: totalMass > 0 ? (value.mass / totalMass) * 100 : 0
      }))
      .sort((a, b) => b.mass - a.mass || b.eventCount - a.eventCount || a.label.localeCompare(b.label));

    const threads = [...row.threads.entries()]
      .map(([id, value]) => ({
        id,
        anchor_t: row.hour,
        segment_id: `hour-${row.hour}`,
        kind: 'annotation' as const,
        label: value.label,
        mass: value.mass,
        event_count: value.eventCount,
        visibility_scope: 'public' as const
      }))
      .sort((a, b) => b.mass - a.mass || b.event_count - a.event_count || a.label.localeCompare(b.label))
      .slice(0, 3);

    return {
      id: `hour-${row.hour}`,
      label: `${hourLabel(row.hour)}:00 - ${hourLabel(row.hour)}:59`,
      hour: row.hour,
      t_start: row.hour,
      t_end: row.hour + 1,
      mass: row.mass,
      width_norm: totalMass > 0 ? row.mass / totalMass : 0,
      event_count: row.eventCount,
      contributors,
      threads,
      top_detail: topDetails(row.eventCount, contributors, threads)
    };
  });

  return {
    spine: {
      domain: {
        type: 'discrete',
        start: 0,
        end: 24
      }
    },
    lens: {
      id: lensId,
      name: meta.name,
      units: meta.units,
      definition: meta.definition,
      normalization_basis: meta.normalizationBasis,
      total_mass: totalMass
    },
    segments,
    threads: segments.flatMap((segment) => segment.threads),
    zero_mass: totalMass <= 0
  };
}
