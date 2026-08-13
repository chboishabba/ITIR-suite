export function normalizeText(value: string | null | undefined): string {
  return String(value ?? '').replace(/\s+/g, ' ').trim();
}

export function compactLower(value: string | null | undefined): string {
  return normalizeText(value).toLowerCase();
}
