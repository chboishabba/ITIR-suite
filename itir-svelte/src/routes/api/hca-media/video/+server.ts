import path from 'node:path';
import { existsSync, createReadStream } from 'node:fs';
import fs from 'node:fs/promises';
import { Readable } from 'node:stream';

function resolveRepoRoot(): string {
  const candidates = [path.resolve('.'), path.resolve('..')];
  for (const c of candidates) {
    if (existsSync(path.join(c, 'SensibLaw'))) return c;
  }
  return path.resolve('..');
}

function parseRange(rangeHeader: string | null, size: number): { start: number; end: number } | null {
  if (!rangeHeader) return null;
  const m = /^bytes=(\d*)-(\d*)$/i.exec(rangeHeader.trim());
  if (!m) return null;
  const startRaw = m[1] ?? '';
  const endRaw = m[2] ?? '';
  let start = startRaw ? Number(startRaw) : 0;
  let end = endRaw ? Number(endRaw) : size - 1;
  if (!Number.isFinite(start) || !Number.isFinite(end)) return null;
  start = Math.max(0, Math.floor(start));
  end = Math.min(size - 1, Math.floor(end));
  if (end < start || start >= size) return null;
  return { start, end };
}

export async function GET({ request }: { request: Request }) {
  const repoRoot = resolveRepoRoot();
  const videoPath = path.join(
    repoRoot,
    'SensibLaw',
    'demo',
    'ingest',
    'hca_case_s942025',
    'media',
    'video',
    'hca_case_s942025.mp4'
  );
  if (!existsSync(videoPath)) {
    return new Response('video_not_found', { status: 404 });
  }

  const st = await fs.stat(videoPath);
  const size = Math.max(0, Number(st.size || 0));
  const range = parseRange(request.headers.get('range'), size);

  if (!range) {
    const stream = createReadStream(videoPath);
    return new Response(Readable.toWeb(stream) as ReadableStream, {
      status: 200,
      headers: {
        'content-type': 'video/mp4',
        'content-length': String(size),
        'accept-ranges': 'bytes',
        'cache-control': 'no-store'
      }
    });
  }

  const { start, end } = range;
  const chunkLen = end - start + 1;
  const stream = createReadStream(videoPath, { start, end });
  return new Response(Readable.toWeb(stream) as ReadableStream, {
    status: 206,
    headers: {
      'content-type': 'video/mp4',
      'content-length': String(chunkLen),
      'content-range': `bytes ${start}-${end}/${size}`,
      'accept-ranges': 'bytes',
      'cache-control': 'no-store'
    }
  });
}

