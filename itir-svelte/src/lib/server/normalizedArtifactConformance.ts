import type { SuiteNormalizedArtifact } from './normalizedArtifacts';

const SCHEMA_VERSION = 'itir.normalized.artifact.v1';
const DERIVED_ROLES = new Set(['derived_product', 'bounded_union_surface']);
const FOLLOW_STATUS_WITH_PRESSURE = new Set(['follow_needed', 'hold', 'abstain']);
const ENUM_UNRESOLVED_STATUS = new Set(['none', ...FOLLOW_STATUS_WITH_PRESSURE]);

const REQUIRED_FIELD_PATHS = [
  'schema_version',
  'artifact_role',
  'artifact_id',
  'canonical_identity',
  'canonical_identity.identity_class',
  'canonical_identity.identity_key',
  'provenance_anchor',
  'provenance_anchor.source_system',
  'provenance_anchor.source_artifact_id',
  'provenance_anchor.anchor_kind',
  'context_envelope_ref',
  'context_envelope_ref.envelope_id',
  'context_envelope_ref.envelope_kind',
  'authority',
  'authority.authority_class',
  'authority.derived',
  'lineage',
  'lineage.upstream_artifact_ids',
  'unresolved_pressure_status'
] as const;

const REQUIRED_FOLLOW_FIELDS = ['trigger', 'scope', 'stop_condition'] as const;

export type NormalizedArtifactConformanceStatus = {
  artifactPresent: boolean;
  schemaVersion: string | null;
  schemaVersionMatches: boolean;
  artifactRole: string | null;
  requiredFieldCoverage: {
    total: number;
    satisfied: number;
    missing: string[];
  };
  authorityConsistency: {
    authorityClass: string | null;
    derived: boolean | null;
    hints: string[];
  };
  followObligationConsistency: {
    hasFollowObligation: boolean;
    unresolvedPressureStatus: string | null;
    hints: string[];
  };
  issues: string[];
};

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null;
}

function getPathValue(root: unknown, path: string): unknown {
  let current = root;
  for (const part of path.split('.')) {
    if (!isObject(current)) {
      return undefined;
    }
    if (!(part in current)) {
      return undefined;
    }
    current = current[part];
  }
  return current;
}

function hasPathValue(root: unknown, path: string): boolean {
  const value = getPathValue(root, path);
  return value !== undefined && value !== null;
}

function isNonEmptyString(value: unknown): value is string {
  return typeof value === 'string' && value.trim().length > 0;
}

export function summarizeNormalizedArtifactConformance(
  artifact: SuiteNormalizedArtifact | null
): NormalizedArtifactConformanceStatus {
  const issues: string[] = [];
  if (!artifact) {
    const missing = REQUIRED_FIELD_PATHS.map((path) => String(path));
    return {
      artifactPresent: false,
      schemaVersion: null,
      schemaVersionMatches: false,
      artifactRole: null,
      requiredFieldCoverage: { total: missing.length, satisfied: 0, missing },
      authorityConsistency: { authorityClass: null, derived: null, hints: [] },
      followObligationConsistency: { hasFollowObligation: false, unresolvedPressureStatus: null, hints: [] },
      issues: ['Artifact payload missing', 'Required normalized artifact fields could not be evaluated']
    };
  }

  const schemaVersion = isNonEmptyString(artifact.schema_version) ? artifact.schema_version : null;
  const schemaVersionMatches = schemaVersion === SCHEMA_VERSION;
  if (!schemaVersionMatches) {
    const got = schemaVersion ?? 'missing';
    issues.push(`Expected schema_version '${SCHEMA_VERSION}', found '${got}'`);
  }

  const artifactRole = isNonEmptyString(artifact.artifact_role) ? artifact.artifact_role : null;
  if (!artifactRole) {
    issues.push('artifact_role is missing or empty');
  }

  const missing: string[] = [];
  for (const path of REQUIRED_FIELD_PATHS) {
    if (path === 'lineage.upstream_artifact_ids') {
      const value = getPathValue(artifact, path);
      if (!Array.isArray(value)) {
        missing.push(path);
        issues.push('lineage.upstream_artifact_ids must be an array of strings');
        continue;
      }
      const badEntry = value.find((entry) => !isNonEmptyString(entry));
      if (badEntry !== undefined) {
        missing.push(path);
        issues.push('lineage.upstream_artifact_ids must contain non-empty strings');
        continue;
      }
    }
    if (!hasPathValue(artifact, path)) {
      missing.push(path);
      issues.push(`Missing required field ${path}`);
    }
  }

  const authorityRecord = isObject(artifact.authority) ? artifact.authority : null;
  const authorityClass = isNonEmptyString(authorityRecord?.authority_class) ? authorityRecord?.authority_class : null;
  const derived = typeof authorityRecord?.derived === 'boolean' ? authorityRecord.derived : null;
  const authorityHints: string[] = [];

  if (artifactRole === 'promoted_record') {
    if (authorityClass !== 'promoted_truth') {
      const hint = 'promoted_record must carry authority_class promoted_truth';
      authorityHints.push(hint);
      issues.push(hint);
    }
    if (derived !== false) {
      const hint = 'promoted_record should mark authority.derived as false';
      authorityHints.push(hint);
      issues.push(hint);
    }
    const receipt = isObject(authorityRecord?.promotion_receipt_ref)
      ? authorityRecord?.promotion_receipt_ref
      : null;
    if (!isNonEmptyString(receipt?.receipt_id)) {
      const hint = 'promoted_record requires authority.promotion_receipt_ref.receipt_id';
      authorityHints.push(hint);
      issues.push(hint);
    }
  }

  if (artifactRole && DERIVED_ROLES.has(artifactRole)) {
    if (derived !== true) {
      const hint = `${artifactRole} should mark authority.derived true`;
      authorityHints.push(hint);
      issues.push(hint);
    }
  } else if (derived === true) {
    const hint = 'authority.derived true without a derived-product or union role';
    authorityHints.push(hint);
    issues.push(hint);
  }

  const unresolvedPressureStatus = isNonEmptyString(artifact.unresolved_pressure_status)
    ? artifact.unresolved_pressure_status
    : null;
  if (unresolvedPressureStatus && !ENUM_UNRESOLVED_STATUS.has(unresolvedPressureStatus)) {
    const hint = `unresolved_pressure_status has unexpected value '${unresolvedPressureStatus}'`;
    issues.push(hint);
  }

  const followRecord = isObject(artifact.follow_obligation) ? artifact.follow_obligation : null;
  const hasFollow = Boolean(followRecord);
  const followHints: string[] = [];

  if (followRecord) {
    for (const key of REQUIRED_FOLLOW_FIELDS) {
      const value = followRecord[key];
      if (!isNonEmptyString(value)) {
        const hint = `follow_obligation.${key} must be a non-empty string`;
        followHints.push(hint);
        issues.push(hint);
      }
    }
    if (!FOLLOW_STATUS_WITH_PRESSURE.has(unresolvedPressureStatus ?? '')) {
      const hint = 'Follow obligations should surface a follow-needed or hold pressure status';
      followHints.push(hint);
      issues.push(hint);
    }
  } else if (unresolvedPressureStatus && FOLLOW_STATUS_WITH_PRESSURE.has(unresolvedPressureStatus)) {
    const hint = `unresolved_pressure_status ${unresolvedPressureStatus} suggests follow_obligation but none is present`;
    followHints.push(hint);
    issues.push(hint);
  }

  return {
    artifactPresent: true,
    schemaVersion,
    schemaVersionMatches,
    artifactRole,
    requiredFieldCoverage: {
      total: REQUIRED_FIELD_PATHS.length,
      satisfied: REQUIRED_FIELD_PATHS.length - missing.length,
      missing
    },
    authorityConsistency: {
      authorityClass,
      derived,
      hints: authorityHints
    },
    followObligationConsistency: {
      hasFollowObligation: hasFollow,
      unresolvedPressureStatus,
      hints: followHints
    },
    issues
  };
}
