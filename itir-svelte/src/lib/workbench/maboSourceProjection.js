import { createMaboReadingSpecimen } from './readingSurface.js';

export const MABO_CANONICAL_CORPUS_REF = 'sensiblaw:data/corpus/mabo_v_queensland_no2.json';
export const MABO_CANONICAL_CITATION = 'Mabo v Queensland (No 2) [1992] HCA 23';
export const MABO_CANONICAL_BODY =
  'The High Court recognised native title in Australia and rejected the doctrine of terra nullius.';

export const MABO_CANONICAL_CORPUS_EVIDENCE = Object.freeze({
  corpusRef: MABO_CANONICAL_CORPUS_REF,
  citation: MABO_CANONICAL_CITATION,
  court: 'High Court of Australia',
  date: '1992-06-03',
  body: MABO_CANONICAL_BODY,
});

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

function validateReaderPayment(payment) {
  if (!payment || typeof payment.semanticRef !== 'string' || payment.semanticRef.length === 0) {
    throw new TypeError('reader source payment requires semanticRef');
  }
  if (payment.claimTruthPaid === true || payment.applicabilityPaid === true) {
    throw new TypeError('reader source payment cannot carry claim truth or applicability');
  }
  if (payment.exactAuthoritySpanPaid === true) {
    if (typeof payment.sourceRevisionRef !== 'string' || payment.sourceRevisionRef.length === 0) {
      throw new TypeError('paid reader source payment requires sourceRevisionRef');
    }
    if (typeof payment.spanRef !== 'string' || payment.spanRef.length === 0) {
      throw new TypeError('paid reader source payment requires spanRef');
    }
  }
  return payment;
}

function paymentBySemanticRef(readerPayments) {
  const payments = new Map();
  for (const rawPayment of readerPayments) {
    const payment = validateReaderPayment(rawPayment);
    if (payments.has(payment.semanticRef)) {
      throw new TypeError(`duplicate reader source payment: ${payment.semanticRef}`);
    }
    payments.set(payment.semanticRef, payment);
  }
  return payments;
}

export function createSourceConditionedMaboSpecimen({
  corpusEvidence = MABO_CANONICAL_CORPUS_EVIDENCE,
  readerPayments = [],
} = {}) {
  validateCanonicalCorpus(corpusEvidence);
  const base = createMaboReadingSpecimen();
  const payments = paymentBySemanticRef(readerPayments);

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
    base.stages.map((stage) => {
      const residual = detailedResidualByRole[stage.role];
      const payment = payments.get(stage.semanticRef);
      const exactAuthorityReady = payment?.exactAuthoritySpanPaid === true;
      const proofPaid = payment?.propositionChainPaid === true;
      return Object.freeze({
        ...stage,
        sourceSpanRef: exactAuthorityReady ? payment.spanRef : null,
        sourceRevisionRef: exactAuthorityReady ? payment.sourceRevisionRef : null,
        exactAuthorityReady,
        proofPaid,
        sourceCondition: exactAuthorityReady
          ? 'exact-authority-span-paid'
          : 'detailed-proposition-unpaid',
        residual: exactAuthorityReady ? null : residual,
        actionAvailability: Object.freeze({
          source: exactAuthorityReady
            ? Object.freeze({ status: 'execute' })
            : Object.freeze({ status: 'defer', residual }),
          why: proofPaid
            ? Object.freeze({ status: 'execute' })
            : Object.freeze({
                status: 'defer',
                residual: 'mabo:residual:detailed-proposition-chain',
              }),
        }),
      });
    }),
  );

  return Object.freeze({
    ...base,
    id: 'reading:mabo:source-conditioned:v3',
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
