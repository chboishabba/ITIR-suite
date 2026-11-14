import { createSemanticTarget } from './semanticTrail.js';

export const humanRoleLabels = Object.freeze({
  actor: 'who',
  predicate: 'did what',
  patient: 'to what',
  condition: 'under what condition',
});

const target = ({ start, end, targetKind, surface, semanticRef, role }) =>
  createSemanticTarget({
    spanRef: `span:golden-spider-silk:${start}:${end}`,
    targetKind,
    surface,
    semanticRef,
    role,
  });

export function createGoldenSpiderSilkReadingFixture() {
  return Object.freeze({
    id: 'reading:golden-spider-silk:fixture:v1',
    text: 'They wove a panel from golden spider silk.',
    showTechnicalPnfLabelsByDefault: false,
    targets: Object.freeze([
      target({
        start: 0,
        end: 4,
        targetKind: 'role',
        surface: 'They',
        semanticRef: 'semantic:golden-spider-silk:actor',
        role: 'actor',
      }),
      target({
        start: 5,
        end: 9,
        targetKind: 'role',
        surface: 'wove',
        semanticRef: 'semantic:golden-spider-silk:predicate',
        role: 'predicate',
      }),
      target({
        start: 12,
        end: 17,
        targetKind: 'role',
        surface: 'panel',
        semanticRef: 'semantic:golden-spider-silk:patient',
        role: 'patient',
      }),
      target({
        start: 23,
        end: 41,
        targetKind: 'composite',
        surface: 'golden spider silk',
        semanticRef: 'semantic:golden-spider-silk:material-composite',
        role: 'material',
      }),
      target({
        start: 37,
        end: 41,
        targetKind: 'constituent',
        surface: 'silk',
        semanticRef: 'semantic:golden-spider-silk:material-silk',
        role: 'material',
      }),
    ]),
  });
}
