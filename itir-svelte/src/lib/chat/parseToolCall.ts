export type ToolCall = {
  tool: string;
  payload: Record<string, unknown> | null;
  rawJson: string | null;
  parseError: string | null;
};

const KNOWN_KEYS = new Set([
  'cmd',
  'chars',
  'session_id',
  'sandbox_permissions',
  'justification',
  'prefix_rule',
  'workdir',
  'tty',
  'yield_time_ms',
  'max_output_tokens',
  // Other common structured tool payloads we want to render nicely.
  'plan',
  'explanation'
]);

// Keep this allowlist tight to avoid accidentally treating random JSON snippets
// in assistant text as a tool call.
const KNOWN_TOOLS = new Set([
  'exec_command',
  'write_stdin',
  'update_plan',
  'notebooklm_meta_event',
  // tool wrappers / variants that may appear in logs
  'parallel',
  'apply_patch'
]);

function toolFromPrefix(prefix: string): string {
  const p = prefix.trim();
  if (!p) return '';
  const left = p.split('<--', 1)[0]?.trim() ?? p;
  const tok = left.split(/\s+/, 1)[0]?.trim() ?? '';
  if (!tok) return '';
  // functions.exec_command -> exec_command
  const lastDot = tok.lastIndexOf('.');
  return lastDot >= 0 ? tok.slice(lastDot + 1) : tok;
}

export function parseToolCallText(text: string): ToolCall | null {
  const t = (text ?? '').trim();
  if (!t) return null;

  const firstBrace = t.indexOf('{');
  const lastBrace = t.lastIndexOf('}');
  if (firstBrace < 0 || lastBrace < 0 || lastBrace <= firstBrace) return null;

  const prefix = t.slice(0, firstBrace);
  const rawJson = t.slice(firstBrace, lastBrace + 1);
  const tool = toolFromPrefix(prefix);
  if (!tool) return null;

  let payload: Record<string, unknown> | null = null;
  let parseError: string | null = null;

  try {
    const v = JSON.parse(rawJson);
    payload = v && typeof v === 'object' && !Array.isArray(v) ? (v as Record<string, unknown>) : null;
  } catch (e) {
    parseError = e instanceof Error ? e.message : String(e);
    payload = null;
  }

  // Heuristic: only treat as a tool call if it looks like one.
  // 1) known tool name (preferred)
  // 2) payload has some known tool-ish keys (fallback)
  if (!KNOWN_TOOLS.has(tool)) {
    const keys = payload ? Object.keys(payload) : [];
    const hits = keys.filter((k) => KNOWN_KEYS.has(k));
    if (!hits.length) return null;
  }

  return { tool: tool || 'tool_call', payload, rawJson, parseError };
}
