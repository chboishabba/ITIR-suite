export const semanticIntentKinds = Object.freeze([
  'ExplainSpan',
  'ExplainRole',
  'WhyClaim',
  'OpenSource',
  'ExploreEntity',
  'FollowReference',
  'ExpandProofCone',
  'Back',
]);

export const defaultSemanticDisclosure = Object.freeze({
  showQids: false,
  showHashes: false,
  showProofGraph: false,
  showAllResiduals: false,
  showAllSourceRoles: false,
  showTechnicalPnfLabels: false,
});

const requiredString = (value, field) => {
  if (typeof value !== 'string' || value.length === 0) {
    throw new TypeError(`${field} must be a non-empty string`);
  }
  return value;
};

export function createSemanticTarget({
  spanRef,
  targetKind,
  surface,
  semanticRef,
  role = null,
  entityRef = null,
  sourceRef = null,
}) {
  return Object.freeze({
    spanRef: requiredString(spanRef, 'spanRef'),
    targetKind: requiredString(targetKind, 'targetKind'),
    surface: requiredString(surface, 'surface'),
    semanticRef: requiredString(semanticRef, 'semanticRef'),
    role,
    entityRef,
    sourceRef,
  });
}

export function buildElucidatoryCone({ nodes, baseDepth, threshold }) {
  if (!Array.isArray(nodes)) {
    throw new TypeError('nodes must be an array');
  }
  if (!Number.isFinite(baseDepth) || baseDepth < 0) {
    throw new TypeError('baseDepth must be a non-negative number');
  }
  if (!Number.isFinite(threshold)) {
    throw new TypeError('threshold must be a number');
  }

  return Object.freeze(
    nodes.filter((node) => {
      const distance = Number(node?.distance);
      const elucidatoryValue = Number(node?.elucidatoryValue ?? 0);
      return distance <= baseDepth || elucidatoryValue >= threshold;
    }),
  );
}

export function resolveExplainOutcome({
  referenceResolved,
  capabilitySupported,
  disclosurePermitted,
  localProjectionAdequate,
  residual = null,
}) {
  if (!referenceResolved) {
    return Object.freeze({ status: 'reject', defect: 'unresolved-reference' });
  }
  if (!capabilitySupported) {
    return Object.freeze({ status: 'reject', defect: 'unsupported-capability' });
  }
  if (!disclosurePermitted) {
    return Object.freeze({ status: 'reject', defect: 'disclosure-blocked' });
  }
  if (localProjectionAdequate) {
    return Object.freeze({ status: 'execute', acquire: false, residual: null });
  }
  if (typeof residual === 'string' && residual.length > 0) {
    return Object.freeze({ status: 'defer', acquire: true, residual });
  }
  return Object.freeze({ status: 'reject', defect: 'missing-residual' });
}

const targetForIntent = (intent, subject) => {
  switch (intent) {
    case 'ExplainSpan':
    case 'ExplainRole':
      return ['Span', subject?.spanRef];
    case 'WhyClaim':
    case 'ExpandProofCone':
      return ['Semantic', subject?.semanticRef ?? subject?.claimRef];
    case 'OpenSource':
      return ['Source', subject?.sourceRef];
    case 'ExploreEntity':
      return ['Entity', subject?.entityRef];
    case 'FollowReference':
      return ['Reference', subject?.referenceRef];
    case 'Back':
      return ['Trail', subject?.trailRef];
    default:
      throw new TypeError(`unsupported semantic intent: ${intent}`);
  }
};

export function compileSemanticIntent(intent, subject) {
  if (!semanticIntentKinds.includes(intent)) {
    throw new TypeError(`unsupported semantic intent: ${intent}`);
  }
  const [targetKind, target] = targetForIntent(intent, subject);
  return Object.freeze({
    action: intent,
    targetKind,
    target: requiredString(target, `${intent} target`),
  });
}

export function createContextCandidate({
  semanticRef,
  qid = null,
  wikipediaRef = null,
  sourceRefs = [],
}) {
  return Object.freeze({
    semanticRef: requiredString(semanticRef, 'semanticRef'),
    qid,
    wikipediaRef,
    sourceRefs: Object.freeze([...sourceRefs]),
    identityCandidateOnly: true,
    legalAuthority: false,
    evidencePaid: false,
    semanticPromotion: false,
  });
}
