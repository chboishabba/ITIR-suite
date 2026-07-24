import { compactLower } from './text';

type FamilyMeta = { label: string; color: string; keywords: string[] };

const THEME_ORDER = ['cprs_blocking', 'woolworths_price', 'government_capacity', 'ets_delay_authority', 'fallacies'] as const;

const OTHER_FAMILY_META: FamilyMeta = {
  label: 'Other argument family',
  color: '#6b7280',
  keywords: []
};

const FAMILY_META: Record<string, FamilyMeta> = {
  cprs_blocking: {
    label: 'CPRS blocking',
    color: '#b54747',
    keywords: ['cprs', 'greens', 'blocked', 'instability', 'momentum']
  },
  woolworths_price: {
    label: 'Woolworths / price effects',
    color: '#8d6a1a',
    keywords: ['woolworths', 'grocery', 'direct cost pass-through', 'direct grocery impacts', 'cpi']
  },
  government_capacity: {
    label: 'Majority vs minority government',
    color: '#2e6f53',
    keywords: ['majority government', 'minority government', 'germany', 'green parties']
  },
  ets_delay_authority: {
    label: 'ETS authority wrappers',
    color: '#4f46e5',
    keywords: ['ross garnaut', 'imperfect ets', 'better than delay', 'kevin rudd']
  },
  fallacies: {
    label: 'Fallacies / framing',
    color: '#0f5b99',
    keywords: ['logical fallacies', 'post hoc', 'false dilemma', 'counterfactual']
  },
  other: OTHER_FAMILY_META
};

export function familyMeta(familyId: string): FamilyMeta {
  const fallback = FAMILY_META.other;
  if (Object.prototype.hasOwnProperty.call(FAMILY_META, familyId)) {
    return FAMILY_META[familyId] ?? OTHER_FAMILY_META;
  }
  return fallback ?? OTHER_FAMILY_META;
}

export function deriveFamilyId(predicateKey: string, surfaceText: string): string {
  const normalized = compactLower(`${predicateKey} ${surfaceText}`);
  if (normalized.includes('ross garnaut') || normalized.includes('imperfect ets') || normalized.includes('better than delay') || normalized.includes('kevin rudd')) {
    return 'ets_delay_authority';
  }
  if (normalized.includes('woolworths') || normalized.includes('grocery') || normalized.includes('pass-through') || normalized.includes('cpi')) {
    return 'woolworths_price';
  }
  if (normalized.includes('majority government') || normalized.includes('minority government') || normalized.includes('germany')) {
    return 'government_capacity';
  }
  if (normalized.includes('fallacies') || normalized.includes('post hoc') || normalized.includes('false dilemma')) {
    return 'fallacies';
  }
  if (normalized.includes('cprs') || normalized.includes('greens blocked') || normalized.includes('climate policy instability') || normalized.includes('climate policy momentum')) {
    return 'cprs_blocking';
  }
  return 'other';
}

export { THEME_ORDER };
