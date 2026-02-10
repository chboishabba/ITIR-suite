import { DashboardPayloadSchema, type DashboardPayload } from './dashboard';

export function parseDashboardPayload(raw: unknown): DashboardPayload {
  const parsed = DashboardPayloadSchema.safeParse(raw);
  if (!parsed.success) {
    const message = parsed.error.issues.map((i) => `${i.path.join('.') || '<root>'}: ${i.message}`).join('\n');
    throw new Error(`Invalid dashboard payload:\n${message}`);
  }
  return parsed.data;
}
