import { writable } from '$lib/ui/simpleStore';

export type WaterfallPaletteName = 'viridis' | 'magma' | 'plasma' | 'inferno' | 'custom';
export type WaterfallAlgoName = 'thread' | 'hour' | 'role' | 'switch';
export type WaterfallModeName = 'linear' | 'waterfall';

export type WaterfallPrefs = {
  palette: WaterfallPaletteName;
  algo: WaterfallAlgoName;
  mode: WaterfallModeName;
  custom: string; // comma-separated CSS colors
};

const PALETTE_KEY = 'sb_dashboard_waterfall_palette';
const ALGO_KEY = 'sb_dashboard_waterfall_color_algo';
const CUSTOM_KEY = 'sb_dashboard_waterfall_custom';
const MODE_KEY = 'sb_dashboard_waterfall_view_mode';

const DEFAULTS = {
  palette: 'viridis',
  algo: 'thread',
  mode: 'waterfall',
  custom: ''
} as const satisfies WaterfallPrefs;

// Compact palettes; can be expanded later.
export const PALETTES: Record<Exclude<WaterfallPaletteName, 'custom'>, string[]> = {
  viridis: ['#440154', '#46327E', '#365C8D', '#277F8E', '#1FA187', '#4AC16D', '#A0DA39', '#FDE725'],
  magma: ['#000004', '#1A1042', '#4B0C6B', '#781C6D', '#A52C60', '#CF4446', '#ED6925', '#FB9B06', '#F7D13D'],
  plasma: ['#0D0887', '#5302A3', '#8B0AA5', '#B83289', '#DB5C68', '#F48849', '#FEBE2A', '#F0F921'],
  inferno: ['#000004', '#160B39', '#420A68', '#6A176E', '#932667', '#BC3754', '#DD513A', '#F2771F', '#FCA50A', '#F6D746', '#FCFFA4']
};

export type ColorableWaterfallItem = {
  hour?: number;
  role?: string;
  switch?: boolean;
  threadIndex?: number;
  threadStartHour?: number;
  defaultColor?: string;
};

function parseCustomColors(value: string): string[] {
  return String(value || '')
    .split(',')
    .map((s) => s.trim())
    .filter((s) => s.length > 0);
}

function resolveColors(prefs: WaterfallPrefs): string[] {
  if (prefs.palette === 'custom') {
    const custom = parseCustomColors(prefs.custom);
    return custom.length ? custom : PALETTES[DEFAULTS.palette];
  }
  const key = prefs.palette as Exclude<WaterfallPaletteName, 'custom'>;
  return PALETTES[key] ?? PALETTES[DEFAULTS.palette];
}

export function colorIndexFor(item: ColorableWaterfallItem, algo: WaterfallAlgoName, paletteSize: number): number {
  const size = Math.max(1, paletteSize);

  if (algo === 'hour') {
    const h = Math.max(0, Math.min(23, Number(item.threadStartHour ?? item.hour ?? 0)));
    return Math.floor((h / 24) * size);
  }

  if (algo === 'role') {
    const r = String(item.role ?? 'unknown').trim().toLowerCase() || 'unknown';
    // Keep stable mapping without needing the full role-index list.
    let hash = 0;
    for (let i = 0; i < r.length; i++) hash = (hash * 31 + r.charCodeAt(i)) >>> 0;
    return hash % size;
  }

  if (algo === 'switch') {
    return item.switch ? Math.max(1, size - 1) : 0;
  }

  // thread
  return Number(item.threadIndex ?? 0) || 0;
}

export function colorFor(item: ColorableWaterfallItem, prefs: WaterfallPrefs): string {
  const colors = resolveColors(prefs);
  const idx = colorIndexFor(item, prefs.algo, colors.length);
  const fallback = item.defaultColor ?? '#6b7280';
  if (!colors.length) return fallback;
  return colors[Math.abs(idx) % colors.length] ?? fallback;
}

function isBrowser(): boolean {
  return typeof window !== 'undefined' && typeof localStorage !== 'undefined';
}

function readPrefsFromStorage(fallback: WaterfallPrefs): WaterfallPrefs {
  if (!isBrowser()) return fallback;

  let palette: WaterfallPaletteName = fallback.palette;
  let algo: WaterfallAlgoName = fallback.algo;
  let mode: WaterfallModeName = fallback.mode;
  let custom = fallback.custom;

  try {
    palette = (localStorage.getItem(PALETTE_KEY) as WaterfallPaletteName | null) ?? palette;
    algo = (localStorage.getItem(ALGO_KEY) as WaterfallAlgoName | null) ?? algo;
    mode = (localStorage.getItem(MODE_KEY) as WaterfallModeName | null) ?? mode;
    custom = localStorage.getItem(CUSTOM_KEY) ?? custom;
  } catch {
    // Some environments throw on storage access (blocked/disabled/quota).
  }

  return {
    palette,
    algo,
    mode: mode === 'linear' ? 'linear' : 'waterfall',
    custom
  };
}

export function hydrateWaterfallPrefs(store: { set: (v: WaterfallPrefs) => void }, fallback: WaterfallPrefs) {
  store.set(readPrefsFromStorage(fallback));
}

export function createWaterfallPrefs(initial?: Partial<WaterfallPrefs>) {
  const start: WaterfallPrefs = { ...DEFAULTS, ...(initial ?? {}) };
  const store = writable<WaterfallPrefs>(start);

  if (isBrowser()) {
    store.subscribe((v) => {
      try {
        localStorage.setItem(PALETTE_KEY, v.palette);
        localStorage.setItem(ALGO_KEY, v.algo);
        localStorage.setItem(MODE_KEY, v.mode);
        localStorage.setItem(CUSTOM_KEY, v.custom);
      } catch {
        // Best-effort persistence only.
      }
    });
  }

  return store;
}
