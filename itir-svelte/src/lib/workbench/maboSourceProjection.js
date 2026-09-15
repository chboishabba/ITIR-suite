import { createMaboReadingSpecimen } from './readingSurface.js';

export const MABO_CANONICAL_CORPUS_REF = 'sensiblaw:data/corpus/mabo_v_queensland_no2.json';
export const MABO_CANONICAL_CITATION = 'Mabo v Queensland (No 2) [1992] HCA 23';
export const MABO_CANONICAL_BODY =
  'The High Court recognised native title in Australia and rejected the doctrine of terra nullius.';

const detailedResidualByRole = Object.freeze({
  'challenged-premise': 'mabo:residual:challenged-premise-span',
  'historical-input': 'mabo:residual:historical-input-span',
  'authority-proposition': 'mabo:residual:exact-authority-span',
  'immediate-implication': 'mabo:residual:immediate-implication-span',
  'downstream-application': 'mabo:residual:downstream-application-source',
});

function validateCanonicalCorpus(corpusEvidence) {
  if (!corpusEvidence || corpusEvidence.corpusRef !== MABO_CANONICAL_CORPUS_REF) {
    throw new TypeError('canonical Mabo corpus ref required');
  }
  if (corpusEvidence.citation !== MABO_CANONICAL_CITATION) {
    throw new TypeError('canonical Mabo citation required');
  }
  if (corpusEvidence.body !== MABO_CANONICAL_BODY) {
    throw new TypeError('canonical Mabo corpus body required');
  }
}

export function createSourceConditionedMaboSpecimen({ corpusEvidence }) {
  validateCanonicalCorpus(corpusEvidence);
  const base = createMaboReadingSpecimen();

  const sourceBasis = Object.freeze({
    corpusRef: corpusEvidence.corpusRef,
    citation: corpusEvidence.citation,
    court: corpusEvidence.court,
    date: corpusEvidence.date,
    recognisedNativeTitle: true,
    rejectedTerraNullius: true,
    paysExactRadicalTitleSpan: false,
    paysDetailedFiveStageChain: false,
    corpusStatementIsAuthoritySpan: false,
  });

  const stages = Object.freeze(
    base.stages.map((stage) =>
      Object.freeze({
        ...stage,
        sourceSpanRef: null,
        sourceRevisionRef: null,
        exactAuthorityReady: false,
        proofPaid: false,
        sourceCondition: 'detailed-proposition-unpaid',
        residual: detailedResidualByRole[stage.role],
      }),
    ),
  );

  return Object.freeze({
    ...base,
    id: 'reading:mabo:source-conditioned:v2',
    sourceBasis,
    stages,
  });
}

export function resolveMaboStageAction(stage, action) {
  if (action === 'source') {
    if (stage.exactAuthorityReady && stage.sourceSpanRef && stage.sourceRevisionRef) {
      return Object.freeze({
        status: 'execute',
        requestedSourceRef: stage.sourceRef,
        sourceSpanRef: stage.sourceSpanRef,
        sourceRevisionRef: stage.sourceRevisionRef,
      });
    }

    return Object.freeze({
      status: 'defer',
      residual: stage.residual,
      requestedSourceRef: stage.sourceRef,
    });
  }

  if (action === 'why' && !stage.proofPaid) {
    return Object.freeze({
      status: 'defer',
      residual: 'mabo:residual:detailed-proposition-chain',
      requestedProofRef: stage.proofRef,
    });
  }

  return Object.freeze({
    status: 'execute',
    action,
    semanticRef: stage.semanticRef,
  });
}
