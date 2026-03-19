import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';

const ROOT = new URL('..', import.meta.url);

function read(rel) {
  return readFileSync(join(ROOT.pathname, rel), 'utf8');
}

test('semantic report uses supported DocumentViewer accessibility props', () => {
  const page = read('src/routes/graphs/semantic-report/+page.svelte');

  assert.ok(page.includes('ariaLabel="Search selected event text"'));
  assert.ok(page.includes('ariaLabel="Search source document text"'));
  assert.ok(page.includes('searchAriaLabel="Search selected event text"'));
  assert.ok(page.includes('searchAriaLabel="Search source document text"'));
});
