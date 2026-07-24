import { existsSync } from 'node:fs';
import os from 'node:os';
import path from 'node:path';

export type PathProvenance =
  | { type: 'env'; envVar: string }
  | { type: 'static'; label: string }
  | { type: 'override'; label: string };

export type RuntimePathCandidate = {
  path: string;
  provenance: PathProvenance;
};

function resolveCandidatePath(value: string, base?: string): string {
  if (base) return path.resolve(base, value);
  return path.resolve(value);
}

export function createEnvCandidate(
  envVar: string,
  repoRoot?: string,
  env: NodeJS.ProcessEnv = process.env
): RuntimePathCandidate | null {
  const raw = env[envVar]?.trim();
  if (!raw) return null;
  return {
    path: resolveCandidatePath(raw, repoRoot),
    provenance: { type: 'env', envVar }
  };
}

export function createStaticCandidate(value: string, label: string, base?: string): RuntimePathCandidate {
  return {
    path: resolveCandidatePath(value, base),
    provenance: { type: 'static', label }
  };
}

export function createOverrideCandidate(value: string, label: string, base?: string): RuntimePathCandidate {
  return {
    path: resolveCandidatePath(value, base),
    provenance: { type: 'override', label }
  };
}

export function dedupeRuntimePathCandidates(candidates: RuntimePathCandidate[]): RuntimePathCandidate[] {
  const seen = new Set<string>();
  const deduped: RuntimePathCandidate[] = [];
  for (const candidate of candidates) {
    const resolved = path.resolve(candidate.path);
    if (seen.has(resolved)) continue;
    seen.add(resolved);
    deduped.push({ ...candidate, path: resolved });
  }
  return deduped;
}

export function gatherChatArchiveCandidates(env: NodeJS.ProcessEnv = process.env): RuntimePathCandidate[] {
  const override = createEnvCandidate('ITIR_CHAT_ARCHIVE_DB_PATH', undefined, env);
  if (override) return [override];

  const fallbackEnv = createEnvCandidate('CHAT_ARCHIVE_DB_PATH', undefined, env);
  if (fallbackEnv) return [fallbackEnv];

  const staticCandidates = [
    createStaticCandidate(path.join(os.homedir(), 'chat_archive.sqlite'), 'home chat archive'),
    createStaticCandidate('/tmp/dashig_chat_archive_latest.sqlite', 'tmp dashig archive'),
    createStaticCandidate(path.join(os.homedir(), '.chat_archive.sqlite'), 'home dot chat archive')
  ];

  const resolved: RuntimePathCandidate[] = [];
  const seen = new Set<string>();
  for (const candidate of staticCandidates) {
    if (!existsSync(candidate.path)) continue;
    if (seen.has(candidate.path)) continue;
    seen.add(candidate.path);
    resolved.push(candidate);
  }

  if (!resolved.length) {
    const fallbackCandidate = staticCandidates[0];
    if (fallbackCandidate) {
      resolved.push(fallbackCandidate);
    }
  }

  return dedupeRuntimePathCandidates(resolved);
}

export function gatherWikiDbCandidates(
  repoRoot: string,
  explicitDbEnv?: string | null,
  env: NodeJS.ProcessEnv = process.env
): RuntimePathCandidate[] {
  const candidates: RuntimePathCandidate[] = [];
  const normalized = explicitDbEnv?.trim();
  if (normalized) {
    candidates.push(createOverrideCandidate(normalized, 'explicit timeline override', repoRoot));
  }

  const modern = createEnvCandidate('ITIR_DB_PATH', repoRoot, env);
  if (modern) {
    candidates.push(modern);
  }

  const legacyCandidates = [
    { envVar: 'SL_WIKI_TIMELINE_DB' },
    { envVar: 'SL_WIKI_TIMELINE_AOO_DB' }
  ];
  for (const legacy of legacyCandidates) {
    const value = env[legacy.envVar]?.trim();
    if (!value) continue;
    candidates.push({
      path: resolveCandidatePath(value, repoRoot),
      provenance: { type: 'env', envVar: legacy.envVar }
    });
    break;
  }

  const deduped = dedupeRuntimePathCandidates(candidates);
  if (!deduped.length) {
    return [createStaticCandidate('.cache_local/itir.sqlite', 'local cache default', repoRoot)];
  }
  return deduped;
}
