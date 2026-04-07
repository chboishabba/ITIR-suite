import path from 'node:path';
import { describe, test } from 'node:test';
import { strictEqual, deepStrictEqual } from 'node:assert/strict';

import {
  autoBuildMissingEnabled,
  dateRangeInclusive,
  resolveRunsRoot,
  resolveSbDbPath
} from '../src/lib/server/dashboard-home/index.ts';

describe('dashboard-home helpers', () => {
  test('enumerates inclusive date ranges', () => {
    deepStrictEqual(dateRangeInclusive('2026-04-01', '2026-04-03'), ['2026-04-01', '2026-04-02', '2026-04-03']);
    deepStrictEqual(dateRangeInclusive('2026-04-03', '2026-04-01'), ['2026-04-01', '2026-04-02', '2026-04-03']);
  });

  test('autoBuildMissingEnabled defaults on and honors off', () => {
    strictEqual(autoBuildMissingEnabled(), true);
    strictEqual(autoBuildMissingEnabled('off'), false);
    strictEqual(autoBuildMissingEnabled(' DISABLE '), false);
    strictEqual(autoBuildMissingEnabled('yes'), true);
  });

  test('resolveRunsRoot respects explicitly provided paths', () => {
    const input = './tmp/test-runs';
    strictEqual(resolveRunsRoot(input), path.resolve(input));
  });

  test('resolveSbDbPath prefers explicit path over runs root', () => {
    const explicit = './tmp/force.db';
    strictEqual(resolveSbDbPath(explicit, '/tmp/runs'), path.resolve(explicit));
  });

  test('resolveSbDbPath falls back to runs root', () => {
    const runsRoot = '/tmp/runs-root';
    strictEqual(resolveSbDbPath('', runsRoot), path.join(runsRoot, 'dashboard.sqlite'));
  });
});
