import type { ChatArchiveMessage } from '$lib/server/chatArchive';
import type { ArgumentAnchor, ArgumentClaim } from '$lib/arguments/workbench';
import { familyMeta } from './family';
import { normalizeText } from './text';

type SpanPreview = { start: number; end: number; exact: boolean; preview: string };

export function sentenceChunks(text: string): Array<{ text: string; start: number; end: number }> {
  const chunks: Array<{ text: string; start: number; end: number }> = [];
  const pattern = /[^\n.!?]+(?:[.!?]+|\n+|$)/g;
  let match: RegExpExecArray | null;
  while ((match = pattern.exec(text)) !== null) {
    const raw = match[0];
    const trimmed = raw.trim();
    if (!trimmed) continue;
    const startOffset = raw.indexOf(trimmed);
    const start = match.index + Math.max(0, startOffset);
    const end = start + trimmed.length;
    chunks.push({ text: trimmed, start, end });
  }
  return chunks.length ? chunks : [{ text, start: 0, end: text.length }];
}

export function claimCandidates(claim: ArgumentClaim): string[] {
  const values = [
    claim.surfaceText,
    claim.normalizedText,
    ...claim.receipts.filter((row) => row.kind === 'claim_text').map((row) => row.value),
    ...claim.arguments.filter((row) => row.role === 'content').map((row) => row.value)
  ]
    .map((value) => normalizeText(value))
    .filter((value) => value.length >= 12);
  return Array.from(new Set(values)).sort((a, b) => b.length - a.length);
}

export function findFamilySentenceSpan(message: ChatArchiveMessage, claim: ArgumentClaim): SpanPreview | null {
  const haystack = message.text ?? '';
  const meta = familyMeta(claim.familyId);
  if (!meta.keywords.length) return null;
  const chunks = sentenceChunks(haystack);
  let best: (SpanPreview & { score: number; length: number }) | null = null;
  for (const chunk of chunks) {
    const lowered = chunk.text.toLowerCase();
    const matched = meta.keywords.filter((keyword) => lowered.includes(keyword.toLowerCase()));
    if (matched.length < 2) continue;
    const candidate = {
      start: chunk.start,
      end: chunk.end,
      exact: false,
      preview: chunk.text,
      score: matched.length,
      length: chunk.text.length
    };
    if (!best || candidate.score > best.score || (candidate.score === best.score && candidate.length < best.length)) {
      best = candidate;
    }
  }
  return best ? { start: best.start, end: best.end, exact: false, preview: best.preview } : null;
}

export function findLiteralSpan(message: ChatArchiveMessage, claim: ArgumentClaim): SpanPreview | null {
  const haystack = message.text ?? '';
  const candidates = claimCandidates(claim);
  for (const candidate of candidates) {
    const idx = haystack.toLowerCase().indexOf(candidate.toLowerCase());
    if (idx >= 0) {
      return {
        start: idx,
        end: Math.min(haystack.length, idx + candidate.length),
        exact: candidate === normalizeText(claim.surfaceText) || candidate === normalizeText(claim.normalizedText),
        preview: candidate
      };
    }
  }
  return findFamilySentenceSpan(message, claim);
}

export function buildAnchors(messages: ChatArchiveMessage[], claims: ArgumentClaim[]): ArgumentAnchor[] {
  const anchors: ArgumentAnchor[] = [];
  for (const claim of claims) {
    for (const message of messages) {
      const span = findLiteralSpan(message, claim);
      if (!span) continue;
      anchors.push({
        id: `${claim.id}:${message.message_id}`,
        claimId: claim.id,
        familyId: claim.familyId,
        messageId: message.message_id,
        charStart: span.start,
        charEnd: span.end,
        exact: span.exact,
        preview: span.preview
      });
      if (!claim.messageIds.includes(message.message_id)) claim.messageIds.push(message.message_id);
    }
  }
  return anchors;
}
