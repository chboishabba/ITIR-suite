import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';

const ROOT = new URL('..', import.meta.url);

function read(rel) {
  return readFileSync(join(ROOT.pathname, rel), 'utf8');
}

test('corpus browser routes exist and are linked from the home page', () => {
  const home = read('src/routes/+page.svelte');
  const corpora = read('src/routes/corpora/+page.svelte');
  const chatArchive = read('src/routes/corpora/chat-archive/+page.svelte');
  const messenger = read('src/routes/corpora/messenger/+page.svelte');
  const openrecall = read('src/routes/corpora/openrecall/+page.svelte');
  const processed = read('src/routes/corpora/processed/+page.svelte');
  const personal = read('src/routes/corpora/processed/personal/+page.svelte');
  const broader = read('src/routes/corpora/processed/broader/+page.svelte');
  const broaderDetail = read('src/routes/corpora/processed/broader/[diagnosticKey]/+page.svelte');

  assert.ok(home.includes('href="/corpora"'));
  assert.ok(corpora.includes('Read-only browsing over the main local corpora'));
  assert.ok(chatArchive.includes('Canonical thread index over the local chat archive'));
  assert.ok(messenger.includes('Browse the filtered Messenger ingest DB'));
  assert.ok(openrecall.includes('Browse imported app/window/OCR captures'));
  assert.ok(processed.includes('Browse the extracted semantic/report outputs'));
  assert.ok(processed.includes('href="/corpora/processed/personal"'));
  assert.ok(personal.includes('Personal Processed Results'));
  assert.ok(personal.includes('Open workbench'));
  assert.ok(personal.includes('Affidavit Reviews'));
  assert.ok(personal.includes('Live persisted personal runs'));
  assert.ok(processed.includes('href="/corpora/processed/broader"'));
  assert.ok(broader.includes('public_bios_timeline'));
  assert.ok(broader.includes('Open details'));
  assert.ok(broaderDetail.includes('Seed Diagnostics'));
  assert.ok(broaderDetail.includes('Raw Source Backlog'));
});

test('corpus server helpers expose dedicated Messenger and OpenRecall query paths', () => {
  const corporaServer = read('src/lib/server/corpora.ts');

  assert.ok(corporaServer.includes('query_messenger_test_db.py'));
  assert.ok(corporaServer.includes('query_openrecall_import.py'));
  assert.ok(corporaServer.includes('loadProcessedCorpusSummaries'));
  assert.ok(corporaServer.includes('loadPersonalProcessedOverview'));
  assert.ok(corporaServer.includes('loadBroaderDiagnosticsSummaries'));
  assert.ok(corporaServer.includes('loadBroaderDiagnosticsDetail'));
  assert.ok(corporaServer.includes("href: '/corpora/chat-archive'"));
  assert.ok(corporaServer.includes("href: '/corpora/messenger'"));
  assert.ok(corporaServer.includes("href: '/corpora/openrecall'"));
  assert.ok(corporaServer.includes("href: '/corpora/processed'"));
});
