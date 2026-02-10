<script lang="ts">
  import Section from '$lib/ui/Section.svelte';
  import type { DashboardArtifactLink } from '../contracts/dashboard';

  export let links: DashboardArtifactLink[] | undefined;

  async function copy(text: string) {
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      // ignore (clipboard permissions)
    }
  }

  function norm(p: string): string {
    return String(p ?? '').replaceAll('\\', '/');
  }

  function dirname(p: string): string {
    const s = norm(p);
    const idx = s.lastIndexOf('/');
    if (idx <= 0) return '';
    return s.slice(0, idx);
  }

  function basename(p: string): string {
    const s = norm(p);
    const idx = s.lastIndexOf('/');
    return idx === -1 ? s : s.slice(idx + 1);
  }

  function commonDirPrefix(paths: string[]): string {
    if (!paths.length) return '';
    const ss = paths.map(norm);
    let pref = ss[0] ?? '';
    for (let i = 1; i < ss.length; i++) {
      const t = ss[i] ?? '';
      let j = 0;
      const max = Math.min(pref.length, t.length);
      while (j < max && pref[j] === t[j]) j++;
      pref = pref.slice(0, j);
      if (!pref) break;
    }
    const cut = pref.lastIndexOf('/');
    return cut >= 0 ? pref.slice(0, cut + 1) : '';
  }

  $: normalized = (links ?? []).map((l) => ({ ...l, path: norm(l.path) }));
  $: prefix = commonDirPrefix(normalized.map((l) => l.path));
  $: maxSeen = Math.max(1, ...(normalized.map((l) => l.seen_count ?? 1) ?? [1]));

  type Group = { folder: string; items: DashboardArtifactLink[] };
  $: groups = (() => {
    const by = new Map<string, DashboardArtifactLink[]>();
    for (const l of normalized) {
      const p = l.path;
      const short = prefix && p.startsWith(prefix) ? p.slice(prefix.length) : p;
      const folder = dirname(short) || '.';
      const next = by.get(folder) ?? [];
      next.push({ ...l, path: short });
      by.set(folder, next);
    }
    const out: Group[] = [];
    for (const [folder, items] of by.entries()) {
      items.sort((a, b) => (b.seen_count ?? 0) - (a.seen_count ?? 0) || basename(a.path).localeCompare(basename(b.path)));
      out.push({ folder, items });
    }
    out.sort((a, b) => a.folder.localeCompare(b.folder));
    return out;
  })();

  function satBg(seenCount: number | undefined): string {
    const n = Math.max(1, seenCount ?? 1);
    const r = Math.max(0, Math.min(1, n / maxSeen));
    // Orange accent, subtle: used as a "frequency saturation" hint, not a metric claim.
    const a = 0.06 + 0.22 * r;
    return `background: rgba(194, 91, 42, ${a.toFixed(3)});`;
  }
</script>

<Section title="Artifacts" subtitle="Paths are local; this UI does not attempt to open them.">
  {#if normalized.length}
    <div class="max-h-[360px] overflow-auto pr-1">
      <div class="space-y-4">
        {#each groups as g (g.folder)}
          <div>
            <div class="mb-2 flex items-baseline justify-between gap-4">
              <div class="font-mono text-xs text-ink-800/70">{g.folder}</div>
              <div class="text-[11px] text-ink-800/50">{g.items.length} file{g.items.length === 1 ? '' : 's'}</div>
            </div>
            <ul class="space-y-2">
              {#each g.items as l (l.path)}
                {@const file = basename(l.path) || l.label}
                {@const seen = l.seen_count ?? (l.seen_dates?.length ?? 1)}
                <li class="flex items-start justify-between gap-4 rounded-xl ring-1 ring-ink-900/10 px-4 py-2" style={satBg(seen)}>
                  <div class="min-w-0">
                    <div class="text-sm font-medium text-ink-950 truncate" title={l.path}>{file}</div>
                    {#if l.seen_dates && l.seen_dates.length}
                      <div class="mt-1 font-mono text-[11px] text-ink-800/70" title={l.seen_dates.join(', ')}>
                        seen {seen}x: {l.seen_dates[0]}{l.seen_dates.length > 1 ? ` .. ${l.seen_dates[l.seen_dates.length - 1]}` : ''}
                      </div>
                    {/if}
                  </div>
                  <button
                    class="shrink-0 rounded-lg bg-ink-900 text-paper-50 px-3 py-2 text-xs uppercase tracking-widest"
                    on:click={() => copy(prefix ? prefix + l.path : l.path)}
                    type="button"
                    title={prefix ? prefix + l.path : l.path}
                  >
                    Copy
                  </button>
                </li>
              {/each}
            </ul>
          </div>
        {/each}
      </div>
    </div>
  {:else}
    <div class="text-sm text-ink-800/70">No artifact links.</div>
  {/if}
</Section>
