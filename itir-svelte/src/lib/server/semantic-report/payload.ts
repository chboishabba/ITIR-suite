import type { SemanticReportPayload } from './types.ts';

export function validateReport(report: unknown): report is SemanticReportPayload {
  if (!report || typeof report !== 'object') return false;
  if (typeof (report as Partial<SemanticReportPayload>).run_id !== 'string') return false;
  if (!('summary' in (report as SemanticReportPayload)) || typeof (report as SemanticReportPayload).summary !== 'object') return false;
  return true;
}

export function parseReport(raw: string): SemanticReportPayload {
  let report: unknown;
  try {
    report = JSON.parse(raw);
  } catch (e) {
    throw new Error(`Failed to parse semantic report JSON: ${e}\nRaw output: ${raw.slice(0, 500)}`);
  }

  if (!validateReport(report)) {
    throw new Error(`Invalid semantic report payload: missing required 'run_id' or 'summary' fields.`);
  }

  return report;
}
