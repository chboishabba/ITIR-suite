export type TimeGranularity = 'year' | 'month' | 'day';

export type TimelineFilters = {
  timeGranularity: TimeGranularity;
  limitEvents: number;
  maxSubjects: number;
  maxObjects: number;
  maxNumbers: number;
  maxSources: number;
  maxLenses: number;
  maxEvidence: number;
  includeSources: boolean;
  includeLenses: boolean;
  includeRequesters: boolean;
  includePurpose: boolean;
  includeEvidence: boolean;
  orderByFactDate: boolean;
};

export function defaultFilters(): TimelineFilters {
  return {
    timeGranularity: 'month',
    limitEvents: 80,
    maxSubjects: 120,
    maxObjects: 160,
    maxNumbers: 120,
    maxSources: 80,
    maxLenses: 120,
    maxEvidence: 140,
    includeSources: true,
    includeLenses: true,
    includeRequesters: true,
    includePurpose: false,
    includeEvidence: false,
    orderByFactDate: false,
  };
}

export function viewportKey(source: string | undefined, filters: TimelineFilters, graphEventCount: number): string {
  const f = filters;
  return [
    String(source ?? 'gwb'),
    String(f.timeGranularity),
    String(f.limitEvents),
    String(f.maxSubjects),
    String(f.maxObjects),
    String(f.maxNumbers),
    f.includeSources ? `src:${f.maxSources}` : 'src:off',
    f.includeLenses ? `lens:${f.maxLenses}` : 'lens:off',
    f.includeEvidence ? `evd:${f.maxEvidence}` : 'evd:off',
    f.includeRequesters ? 'req:on' : 'req:off',
    f.includePurpose ? 'purpose:on' : 'purpose:off',
    f.orderByFactDate ? 'fact_date:on' : 'fact_date:off',
    String(graphEventCount),
  ].join('|');
}
