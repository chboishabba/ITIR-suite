import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { parseFactReviewCliPayload } from '../src/lib/server/factReviewCli.js';

const ROOT = new URL('..', import.meta.url);

test('Zelph-demo output (sl_output.json) is compatible with itir-svelte CLI parser', () => {
  const filePath = join(ROOT.pathname, '../SensibLaw/sl_zelph_demo/sl_output.json');
  const raw = readFileSync(filePath, 'utf8');
  
  // This should not throw if sl_extract.py has been hardened with ok: true
  const facts = parseFactReviewCliPayload(raw, 'facts');
  
  assert.ok(Array.isArray(facts));
  assert.equal(facts.length, 6);
  assert.equal(facts[0].id, 'f1');
  assert.equal(facts[0].event_id, 'slip_event');
});
