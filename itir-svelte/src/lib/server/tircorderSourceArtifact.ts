import fs from 'node:fs/promises';
import path from 'node:path';
import { resolveRepoRoot } from '$lib/server/utils';
import type { NormalizedArtifactRef } from '$lib/server/normalizedArtifacts';

async function readJsonObject(filePath: string): Promise<Record<string, unknown>> {
  return JSON.parse(await fs.readFile(filePath, 'utf-8')) as Record<string, unknown>;
}

function resolveArtifactPath(repoRoot: string, rawPath: string): string {
  if (path.isAbsolute(rawPath)) return rawPath;
  return path.resolve(repoRoot, rawPath);
}

export async function loadTircorderSourceArtifact(
  sidecarPath?: string | null
): Promise<NormalizedArtifactRef | null> {
  if (!sidecarPath) return null;
  const repoRoot = resolveRepoRoot();
  const resolvedPath = resolveArtifactPath(repoRoot, sidecarPath);
  try {
    const artifact = await readJsonObject(resolvedPath);
    return {
      label: path.basename(resolvedPath),
      producer: 'tircorder-JOBBIE',
      source: resolvedPath,
      artifact
    };
  } catch (error) {
    return {
      label: path.basename(sidecarPath),
      producer: 'tircorder-JOBBIE',
      source: resolvedPath,
      artifact: null,
      error: error instanceof Error ? error.message : String(error)
    };
  }
}
