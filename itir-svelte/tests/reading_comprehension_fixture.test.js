import assert from 'node:assert/strict';
import test from 'node:test';

import {
  createGoldenSpiderSilkReadingFixture,
  humanRoleLabels,
} from '../src/lib/workbench/readingComprehensionFixture.js';

test('fixture exposes actor predicate patient composite and constituent targets independently', () => {
  const fixture = createGoldenSpiderSilkReadingFixture();

  assert.equal(fixture.text, 'They wove a panel from golden spider silk.');
  assert.deepEqual(
    fixture.targets.map((target) => [target.surface, target.role, target.targetKind]),
    [
      ['They', 'actor', 'role'],
      ['wove', 'predicate', 'role'],
      ['panel', 'patient', 'role'],
      ['golden spider silk', 'material', 'composite'],
      ['silk', 'material', 'constituent'],
    ],
  );
  assert.notEqual(fixture.targets[3].semanticRef, fixture.targets[4].semanticRef);
  assert.notEqual(fixture.targets[3].spanRef, fixture.targets[4].spanRef);
});

test('human-first labels precede technical PNF vocabulary', () => {
  assert.deepEqual(humanRoleLabels, {
    actor: 'who',
    predicate: 'did what',
    patient: 'to what',
    condition: 'under what condition',
  });

  const fixture = createGoldenSpiderSilkReadingFixture();
  assert.equal(fixture.showTechnicalPnfLabelsByDefault, false);
  assert.equal(fixture.userUnderstands, undefined);
  assert.equal(fixture.userBelieves, undefined);
});
