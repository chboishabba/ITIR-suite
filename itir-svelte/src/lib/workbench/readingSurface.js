import { createContextCandidate } from './semanticTrail.js';

export const readingViews = Object.freeze([
  'explain',
  'why',
  'source',
  'context',
  'graph',
  'guide',
]);

export const cardKinds = Object.freeze(['identity', 'source', 'proof']);

export const guideCues = Object.freeze([
  'actor',
  'predicate',
  'patient',
  'negation',
  'modality',
  'condition',
  'temporal',
  'coreference',
]);

const makeStage = ({
  role,
  eyebrow,
  heading,
  summary,
  semanticRef,
  proofRef,
  sourceRef,
  sourceSpanRef,
  sourceRevisionRef,
  contextLabel,
}) => Object.freeze({
  role,
  eyebrow,
  heading,
  summary,
  semanticRef,
  proofRef,
  sourceRef,
  sourceSpanRef,
  sourceRevisionRef,
  contextLabel,
  exactAuthorityReady: Boolean(sourceRef && sourceSpanRef && sourceRevisionRef),
});

export function createMaboReadingSpecimen() {
  return Object.freeze({
    id: 'reading:mabo:flagship:v1',
    title: 'Why was Mabo such a big deal?',
    lead:
      'Mabo changed a foundational legal assumption about Crown title and the survival of pre-existing native title. This view shows one bounded chain; open the source or proof detail only when you want it.',
    defaultView: 'explain',
    graphVisibleByDefault: false,
    contextVisibleByDefault: false,
    guideVisibleByDefault: false,
    showQidsByDefault: false,
    showHashesByDefault: false,
    showAllResidualsByDefault: false,
    showAllSourceRolesByDefault: false,
    context: Object.freeze({
      ...createContextCandidate({
        semanticRef: 'mabo:case:1992:hca:23',
        qid: 'Q1501525',
        wikipediaRef: 'wiki:en:Mabo_v_Queensland_(No_2)',
        sourceRefs: ['source:mabo:1992:hca:23'],
      }),
      wikidataQid: 'Q1501525',
    }),
    stages: Object.freeze([
      makeStage({
        role: 'challenged-premise',
        eyebrow: 'Before',
        heading: 'The starting assumption',
        summary:
          'The argument starts from a premise about what Crown sovereignty did to pre-existing interests in land. Mabo is important because the Court did not leave that premise untouched.',
        semanticRef: 'mabo:premise:prior-crown-title-treatment',
        proofRef: 'proof:mabo:challenged-premise',
        sourceRef: 'source:mabo:1992:hca:23',
        sourceSpanRef: 'span:mabo:challenged-premise',
        sourceRevisionRef: 'revision:mabo:1992:hca:23',
        contextLabel: 'Crown title and pre-existing rights',
      }),
      makeStage({
        role: 'historical-input',
        eyebrow: 'Context',
        heading: 'The legal materials the Court had to work through',
        summary:
          'The proposition sits inside a longer common-law and historical genealogy. Those inputs matter, but this reading view keeps them folded until you ask for them.',
        semanticRef: 'mabo:input:historical-common-law',
        proofRef: 'proof:mabo:historical-input',
        sourceRef: 'source:mabo:1992:hca:23',
        sourceSpanRef: 'span:mabo:historical-input',
        sourceRevisionRef: 'revision:mabo:1992:hca:23',
        contextLabel: 'Historical and common-law inputs',
      }),
      makeStage({
        role: 'authority-proposition',
        eyebrow: 'What changed',
        heading: 'Radical title did not itself answer every question of beneficial ownership',
        summary:
          'The selected Mabo proposition separates the Crown’s radical title from an automatic conclusion that every pre-existing native interest vanished. That distinction changes what must be proved next.',
        semanticRef: 'mabo:proposition:radical-title-native-title',
        proofRef: 'proof:mabo:authority-proposition',
        sourceRef: 'source:mabo:1992:hca:23',
        sourceSpanRef: 'span:mabo:authority-proposition',
        sourceRevisionRef: 'revision:mabo:1992:hca:23',
        contextLabel: 'Mabo proposition',
      }),
      makeStage({
        role: 'immediate-implication',
        eyebrow: 'Immediate effect',
        heading: 'Native title became a question that could survive into the legal analysis',
        summary:
          'Once the automatic-extinguishment premise is rejected, native title can be analysed as a surviving interest subject to its own proof, continuity, recognition and extinguishment questions.',
        semanticRef: 'mabo:implication:native-title-survival',
        proofRef: 'proof:mabo:immediate-implication',
        sourceRef: 'source:mabo:1992:hca:23',
        sourceSpanRef: 'span:mabo:immediate-implication',
        sourceRevisionRef: 'revision:mabo:1992:hca:23',
        contextLabel: 'Native-title implication',
      }),
      makeStage({
        role: 'downstream-application',
        eyebrow: 'After Mabo',
        heading: 'Later law had to operate in the space Mabo opened',
        summary:
          'Later legislation and cases did not simply repeat Mabo. They developed rules for recognition, proof, extinguishment and application. Open this stage when you want one concrete downstream path.',
        semanticRef: 'mabo:application:downstream-law',
        proofRef: 'proof:mabo:downstream-application',
        sourceRef: 'source:mabo:downstream-application',
        sourceSpanRef: 'span:mabo:downstream-application',
        sourceRevisionRef: 'revision:mabo:downstream-application',
        contextLabel: 'Later-law application',
      }),
    ]),
  });
}

export function projectReadingStage(stage, view) {
  if (!readingViews.includes(view)) {
    throw new TypeError(`unsupported reading view: ${view}`);
  }

  return Object.freeze({ ...stage, view });
}

export function projectContextInspection(specimen, stage) {
  return Object.freeze({
    semanticRef: stage.semanticRef,
    wikidataQid: specimen.context.wikidataQid,
    wikipediaRef: specimen.context.wikipediaRef,
    exactSourceRef: stage.sourceRef,
    identityCandidateOnly: specimen.context.identityCandidateOnly,
    legalAuthority: false,
    evidencePaid: false,
  });
}

export function compileReadingIntent(stage, intent) {
  const availability = stage?.actionAvailability?.[intent];
  if (availability && availability.status !== 'execute') {
    return Object.freeze({
      action: 'Defer',
      targetKind: 'Residual',
      target: availability.residual,
      requestedIntent: intent,
    });
  }

  switch (intent) {
    case 'why':
      return Object.freeze({
        action: 'Expand',
        targetKind: 'Semantic',
        target: stage.semanticRef,
      });
    case 'source':
      return Object.freeze({
        action: 'OpenSource',
        targetKind: 'Source',
        target: stage.sourceRef,
      });
    case 'context':
      return Object.freeze({
        action: 'Follow',
        targetKind: 'Semantic',
        target: stage.semanticRef,
      });
    case 'graph':
      return Object.freeze({
        action: 'Zoom',
        targetKind: 'Semantic',
        target: stage.semanticRef,
        detail: 'Fit',
      });
    default:
      throw new TypeError(`unsupported reading intent: ${intent}`);
  }
}
