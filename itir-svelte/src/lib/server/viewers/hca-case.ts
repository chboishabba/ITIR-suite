import fs from 'node:fs/promises';
import path from 'node:path';
import { existsSync } from 'node:fs';

import { resolveRepoRoot } from '$lib/server/utils';

export type FileEntry = {
  id: string;
  name: string;
  relPath: string;
  bytes: number;
  kind: 'file';
};

export type TranscriptSegment = {
  start: string;
  end: string;
  text: string;
};

type RawSegment = {
  start?: string;
  end?: string;
  text?: string;
};

export interface HcaCaseModel {
  baseRel: string;
  transcriptFiles: FileEntry[];
  documentFiles: FileEntry[];
  selectedTranscriptId: string | null;
  selectedDocumentId: string | null;
  audioSrc: string | null;
  transcriptMarkdown: string;
  transcriptSegments: TranscriptSegment[];
  selectedDocumentText: string;
  selectedDocumentName: string | null;
}

async function listFilesAbs(dirAbs: string, relBase: string): Promise<FileEntry[]> {
  const rows: FileEntry[] = [];
  const entries = await fs.readdir(dirAbs, { withFileTypes: true });
  for (const entry of entries) {
    if (!entry.isFile()) continue;
    const abs = path.join(dirAbs, entry.name);
    const st = await fs.stat(abs);
    rows.push({
      id: `${relBase}/${entry.name}`,
      name: entry.name,
      relPath: `${relBase}/${entry.name}`,
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
        .map((item: any) => (typeof item?.text === 'string' ? item.text : typeof item === 'string' ? item : ''))
        .filter(Boolean);
      if (parts.length) return parts.join('\n');
    }
    return raw;
  } catch {
    return await fs.readFile(absPath, 'utf-8');
  }
}

export async function loadHcaCaseModel(url: URL): Promise<HcaCaseModel> {
  const repoRoot = resolveRepoRoot();
  const baseRel = path.join('SensibLaw', 'demo', 'ingest', 'hca_case_s942025');
  const transcriptDirRel = path.join(baseRel, 'media', 'transcripts');
  const transcriptDirAbs = path.join(repoRoot, transcriptDirRel);
  const videoFileRel = path.join(baseRel, 'media', 'video', 'hca_case_s942025.mp4');
  const videoFileAbs = path.join(repoRoot, videoFileRel);
  const ingestDirRel = path.join(baseRel, 'ingest');
  const ingestDirAbs = path.join(repoRoot, ingestDirRel);

  const transcriptFiles = existsSync(transcriptDirAbs) ? await listFilesAbs(transcriptDirAbs, transcriptDirRel) : [];
  const documentFilesRaw = existsSync(ingestDirAbs) ? await listFilesAbs(ingestDirAbs, ingestDirRel) : [];
  const documentFiles = documentFilesRaw.filter((row) => row.name.endsWith('.document.json'));

  const transcriptQuery = url.searchParams.get('transcript');
  const docQuery = url.searchParams.get('doc');

  const defaultTranscript =
    transcriptFiles.find((file) => file.name.endsWith('.segments.json')) ??
    transcriptFiles.find((file) => file.name.endsWith('.md')) ??
    transcriptFiles[0] ??
    null;
  const selectedTranscript = transcriptFiles.find((file) => file.id === transcriptQuery || file.name === transcriptQuery) ?? defaultTranscript;

  const defaultDoc = documentFiles[0] ?? null;
  const selectedDocument = documentFiles.find((file) => file.id === docQuery || file.name === docQuery) ?? defaultDoc;

  let transcriptMarkdown = '';
  let transcriptSegments: TranscriptSegment[] = [];
  if (selectedTranscript) {
    const abs = path.join(repoRoot, selectedTranscript.relPath);
    if (selectedTranscript.name.endsWith('.segments.json')) {
      try {
        const parsed = JSON.parse(await fs.readFile(abs, 'utf-8')) as any;
        const rows = Array.isArray(parsed?.segments) ? (parsed.segments as RawSegment[]) : [];
        transcriptSegments = rows
          .map((row) => ({
            start: String(row?.start ?? ''),
            end: String(row?.end ?? ''),
            text: String(row?.text ?? '')
          }))
          .filter((row) => row.start && row.end && row.text);
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
    const markdownCandidate = transcriptFiles.find((file) => file.name.endsWith('.md'));
    if (markdownCandidate) {
      transcriptMarkdown = await fs.readFile(path.join(repoRoot, markdownCandidate.relPath), 'utf-8');
    }
  }

  let selectedDocumentText = '';
  if (selectedDocument) {
    selectedDocumentText = await loadDocumentBody(path.join(repoRoot, selectedDocument.relPath));
  }

  return {
    baseRel,
    transcriptFiles,
    documentFiles,
    selectedTranscriptId: selectedTranscript?.id ?? null,
    selectedDocumentId: selectedDocument?.id ?? null,
    audioSrc: existsSync(videoFileAbs) ? '/api/hca-media/video' : null,
    transcriptMarkdown,
    transcriptSegments,
    selectedDocumentText,
    selectedDocumentName: selectedDocument?.name ?? null
  };
}
