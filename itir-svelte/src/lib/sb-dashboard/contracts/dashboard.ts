import { z } from 'zod';

export const DashboardArtifactLinkSchema = z.object({
  label: z.string(),
  path: z.string(),
  // Optional range aggregation helpers (Svelte-side), ignored by legacy SB HTML.
  seen_count: z.number().int().nonnegative().optional(),
  seen_dates: z.array(z.string()).optional()
});

export const DashboardTimelineEventSchema = z.object({
  ts: z.string(),
  hour: z.number().int().min(0).max(23),
  kind: z.string(),
  detail: z.string(),
  source_path: z.string().optional(),
  meta: z.record(z.unknown()).optional()
});

export const ChatThreadSchema = z.object({
  thread_id: z.string(),
  title: z.string().optional(),
  title_resolved: z.string().optional(),
  origin: z.string().optional(),
  message_count: z.number().int().nonnegative().optional(),
  first_ts: z.string().optional(),
  last_ts: z.string().optional(),
  first_user_preview: z.string().optional(),
  // In practice these may be arrays or count maps (role->count, source_id->count).
  roles: z.union([z.array(z.string()), z.record(z.number().int().nonnegative())]).optional(),
  source_ids: z.union([z.array(z.string()), z.record(z.number().int().nonnegative())]).optional()
});

export const ChatFlowThreadSchema = z.object({
  thread_id: z.string(),
  thread_key: z.string().optional(),
  thread_title: z.string().optional(),
  message_count: z.number().int().nonnegative().optional(),
  share: z.number().nonnegative().optional(),
  color_hex: z.string().optional(),
  color_index: z.number().int().optional(),
  thread_start_ts: z.string().optional(),
  thread_start_hour: z.number().int().min(0).max(23).optional()
});

export const ChatWaterfallItemSchema = z.object({
  ts: z.string(),
  hour: z.number().int().min(0).max(23),
  role: z.string().optional(),
  thread_id: z.string(),
  thread_key: z.string().optional(),
  thread_title: z.string().optional(),
  thread_start_ts: z.string().optional(),
  thread_start_hour: z.number().int().min(0).max(23).optional(),
  switch: z.boolean().optional(),
  gap_to_next_seconds: z.number().optional(),
  color_hex: z.string().optional(),
  color_index: z.number().int().optional()
});

export const DashboardChatFlowSchema = z.object({
  message_count: z.number().int().nonnegative().optional(),
  thread_count: z.number().int().nonnegative().optional(),
  switch_count: z.number().int().nonnegative().optional(),
  switch_rate: z.number().nonnegative().optional(),
  dominant_thread_share: z.number().nonnegative().optional(),
  active_hours: z.number().int().nonnegative().optional(),
  first_ts: z.string().optional(),
  last_ts: z.string().optional(),
  threads: z.array(ChatFlowThreadSchema).optional(),
  waterfall: z.array(ChatWaterfallItemSchema).optional(),
  waterfall_render_limit: z.number().int().optional(),
  waterfall_truncated: z.boolean().optional(),
  // Observed shape: 24-element int array.
  // Keep permissive because this is a visualization helper, not a stable contract yet.
  hour_bins: z.union([z.array(z.number().int()), z.record(z.unknown())]).optional()
});

export const DashboardPayloadSchema = z
  .object({
    date: z.string(),
    generated_at: z.string().optional(),
    period_start: z.string().optional(),
    period_end: z.string().optional(),
    days: z.number().int().nonnegative().optional(),
    chat_source: z.string().optional(),
    chat_scope_mode: z.string().optional(),
    chat_scope_thread_count: z.number().int().optional(),
    summary: z.record(z.unknown()).optional(),
    frequency_by_hour: z.record(z.array(z.number())).optional(),
    chat_flow: DashboardChatFlowSchema.optional(),
    chat_threads: z.array(ChatThreadSchema).optional(),
    tool_use_summary: z.record(z.unknown()).optional(),
    notes_meta_summary: z.record(z.unknown()).optional(),
    artifact_links: z.array(DashboardArtifactLinkSchema).optional(),
    timeline: z.array(DashboardTimelineEventSchema).optional(),
    warnings: z.array(z.string()).optional()
  })
  .passthrough();

export type DashboardPayload = z.infer<typeof DashboardPayloadSchema>;
export type DashboardTimelineEvent = z.infer<typeof DashboardTimelineEventSchema>;
export type DashboardArtifactLink = z.infer<typeof DashboardArtifactLinkSchema>;
export type ChatWaterfallItem = z.infer<typeof ChatWaterfallItemSchema>;
