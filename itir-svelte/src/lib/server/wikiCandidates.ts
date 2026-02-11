import fs from 'node:fs/promises';
import path from 'node:path';

export type WikiCandidateEvidence = {
  wiki: string | null;
  page_title: string;
  page_revid: number | null;
  source_url: string | null;
  source_path: string | null;
};

export type WikiCandidateRow = {
  title: string;
  score: number;
  evidence_pages: string[];
};

export type WikiCandidatesPayload = {
  pages: Array<{ title: string; revid: number | null; wiki: string | null; source_url: string | null }>;
  candidates: WikiCandidateRow[];
};

function isObj(v: unknown): v is Record<string, unknown> {
  return Boolean(v) && typeof v === 'object';
}

export async function loadWikiCandidates(repoRoot: string, relPath: string): Promise<WikiCandidatesPayload> {
  const p = path.resolve(repoRoot, relPath);
  const raw = await fs.readFile(p, 'utf-8');
  const parsed = JSON.parse(raw) as any;
  const rows = Array.isArray(parsed?.rows) ? (parsed.rows as any[]) : [];

  const pagesByTitle = new Map<
    string,
    { title: string; revid: number | null; wiki: string | null; source_url: string | null }
  >();
  const candidates: WikiCandidateRow[] = [];

  for (const r of rows) {
    if (!isObj(r)) continue;
    const title = String(r.title ?? '').trim();
    if (!title) continue;
    const score = Number(r.score ?? 0) || 0;
    const evidence = Array.isArray(r.evidence) ? (r.evidence as any[]) : [];
    const evidence_pages: string[] = [];

    for (const ev of evidence) {
      if (!isObj(ev)) continue;
      const page_title = String(ev.page_title ?? '').trim();
      if (!page_title) continue;
      if (!evidence_pages.includes(page_title)) evidence_pages.push(page_title);
      if (!pagesByTitle.has(page_title)) {
        const wiki = typeof ev.wiki === 'string' ? ev.wiki : null;
        const revidRaw = ev.page_revid;
        const revid = Number.isFinite(Number(revidRaw)) ? Number(revidRaw) : null;
        const source_url = typeof ev.source_url === 'string' ? ev.source_url : null;
        pagesByTitle.set(page_title, { title: page_title, revid, wiki, source_url });
      }
    }

    candidates.push({ title, score, evidence_pages });
  }

  candidates.sort((a, b) => b.score - a.score || a.title.localeCompare(b.title));
  const pages = Array.from(pagesByTitle.values()).sort((a, b) => a.title.localeCompare(b.title));

  return { pages, candidates };
}

