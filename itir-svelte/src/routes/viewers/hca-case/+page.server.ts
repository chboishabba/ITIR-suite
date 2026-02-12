import path from 'node:path';
import { existsSync } from 'node:fs';
import fs from 'node:fs/promises';

type FileEntry = {
  id: string;
  name: string;
  relPath: string;
  bytes: number;
  kind: 'file' | 'dir';
};

function resolveRepoRoot(): string {
  const candidates = [path.resolve('.'), path.resolve('..')];
  for (const c of candidates) {
    if (existsSync(path.join(c, 'SensibLaw'))) return c;
  }
  return path.resolve('..');
}

async function listFilesAbs(dirAbs: string, relBase: string): Promise<FileEntry[]> {
  const rows: FileEntry[] = [];
  const entries = await fs.readdir(dirAbs, { withFileTypes: true });
  for (const e of entries) {
    if (!e.isFile()) continue;
    const abs = path.join(dirAbs, e.name);
    const st = await fs.stat(abs);
    rows.push({
      id: `${relBase}/${e.name}`,
      name: e.name,
      relPath: `${relBase}/${e.name}`,
      bytes: st.size,
      kind: 'file'
    });
  }
  rows.sort((a, b) => a.name.localeCompare(b.name));
  return rows;
}

async function loadDocumentBody(absPath: string): Promise<string> {
  try {
    const raw = await fs.readFile(absPath, 'utf-8');
    const parsed = JSON.parse(raw) as any;
    if (typeof parsed?.body === 'string' && parsed.body.trim()) return parsed.body;
    if (Array.isArray(parsed?.sentences) && parsed.sentences.length) {
      const parts = parsed.sentences
        .map((s: any) => (typeof s?.text === 'string' ? s.text : typeof s === 'string' ? s : ''))
        .filter(Boolean);
      if (parts.length) return parts.join('\n');
    }
    return raw;
  } catch {
    return await fs.readFile(absPath, 'utf-8');
  }
}

export async function load({ url }: { url: URL }) {
  const repoRoot = resolveRepoRoot();
  const baseRel = path.join('SensibLaw', 'demo', 'ingest', 'hca_case_s942025');
  const baseAbs = path.join(repoRoot, baseRel);
  const transcriptDirRel = path.join(baseRel, 'media', 'transcripts');
  const transcriptDirAbs = path.join(repoRoot, transcriptDirRel);
  const videoFileRel = path.join(baseRel, 'media', 'video', 'hca_case_s942025.mp4');
  const videoFileAbs = path.join(repoRoot, videoFileRel);
  const ingestDirRel = path.join(baseRel, 'ingest');
  const ingestDirAbs = path.join(repoRoot, ingestDirRel);

  const transcriptFiles = existsSync(transcriptDirAbs) ? await listFilesAbs(transcriptDirAbs, transcriptDirRel) : [];
  const documentFilesRaw = existsSync(ingestDirAbs) ? await listFilesAbs(ingestDirAbs, ingestDirRel) : [];
  const documentFiles = documentFilesRaw.filter((r) => r.name.endsWith('.document.json'));

  const transcriptQuery = url.searchParams.get('transcript');
  const docQuery = url.searchParams.get('doc');

  const defaultTranscript =
    transcriptFiles.find((f) => f.name.endsWith('.segments.json')) ??
    transcriptFiles.find((f) => f.name.endsWith('.md')) ??
    transcriptFiles[0] ??
    null;
  const selectedTranscript =
    transcriptFiles.find((f) => f.id === transcriptQuery || f.name === transcriptQuery) ?? defaultTranscript;

  const defaultDoc = documentFiles[0] ?? null;
  const selectedDoc = documentFiles.find((f) => f.id === docQuery || f.name === docQuery) ?? defaultDoc;

  let transcriptMarkdown = '';
  let transcriptSegments: Array<{ start: string; end: string; text: string }> = [];
  if (selectedTranscript) {
    const abs = path.join(repoRoot, selectedTranscript.relPath);
    if (selectedTranscript.name.endsWith('.segments.json')) {
      try {
        const parsed = JSON.parse(await fs.readFile(abs, 'utf-8')) as any;
        const rows = Array.isArray(parsed?.segments) ? parsed.segments : [];
        transcriptSegments = rows
          .map((r: any) => ({
            start: String(r?.start ?? ''),
            end: String(r?.end ?? ''),
            text: String(r?.text ?? '')
          }))
          .filter((r: any) => r.start && r.end && r.text);
      } catch {
        transcriptSegments = [];
      }
    } else if (selectedTranscript.name.endsWith('.md') || selectedTranscript.name.endsWith('.txt')) {
      transcriptMarkdown = await fs.readFile(abs, 'utf-8');
    } else {
      transcriptMarkdown = await fs.readFile(abs, 'utf-8');
    }
  }

  if (!transcriptMarkdown) {
    const md = transcriptFiles.find((f) => f.name.endsWith('.md'));
    if (md) transcriptMarkdown = await fs.readFile(path.join(repoRoot, md.relPath), 'utf-8');
  }

  let selectedDocumentText = '';
  if (selectedDoc) {
    selectedDocumentText = await loadDocumentBody(path.join(repoRoot, selectedDoc.relPath));
  }

  return {
    baseRel,
    transcriptFiles,
    documentFiles,
    selectedTranscriptId: selectedTranscript?.id ?? null,
    selectedDocumentId: selectedDoc?.id ?? null,
    audioSrc: existsSync(videoFileAbs) ? '/api/hca-media/video' : null,
    transcriptMarkdown,
    transcriptSegments,
    selectedDocumentText,
    selectedDocumentName: selectedDoc?.name ?? null
  };
}
