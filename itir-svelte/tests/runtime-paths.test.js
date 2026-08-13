import 'ts-node/register';
import test from 'node:test';
import assert from 'node:assert/strict';
import path from 'node:path';
import { gatherChatArchiveCandidates, gatherWikiDbCandidates } from '../src/lib/server/runtime/pathCandidates.ts';

test('chat archive candidates honor ITIR env override with provenance', () => {
  const env = { ITIR_CHAT_ARCHIVE_DB_PATH: '/tmp/override-archive.sqlite' };
  const candidates = gatherChatArchiveCandidates(env);
  assert.equal(candidates.length, 1);
  assert.equal(candidates[0].path, path.resolve('/tmp/override-archive.sqlite'));
  assert.equal(candidates[0].provenance.type, 'env');
  assert.equal(candidates[0].provenance.envVar, 'ITIR_CHAT_ARCHIVE_DB_PATH');
});

test('wiki timeline candidates prefer explicit overrides even when ITIR env exists', () => {
  const repoRoot = '/tmp/repo-root';
  const env = { ITIR_DB_PATH: 'ignored.db' };
  const candidates = gatherWikiDbCandidates(repoRoot, 'explicit.timeline.sqlite', env);
  assert.equal(candidates[0].path, path.resolve(repoRoot, 'explicit.timeline.sqlite'));
  assert.equal(candidates[0].provenance.type, 'override');
  assert.equal(candidates[0].provenance.label, 'explicit timeline override');
});

test('wiki timeline candidates expose legacy env vars when modern ITIR path is absent', () => {
  const repoRoot = '/tmp/repo-root';
  const env = { SL_WIKI_TIMELINE_DB: 'legacy.sqlite' };
  const candidates = gatherWikiDbCandidates(repoRoot, null, env);
  assert.equal(candidates[0].path, path.resolve(repoRoot, 'legacy.sqlite'));
  assert.equal(candidates[0].provenance.type, 'env');
  assert.equal(candidates[0].provenance.envVar, 'SL_WIKI_TIMELINE_DB');
});
