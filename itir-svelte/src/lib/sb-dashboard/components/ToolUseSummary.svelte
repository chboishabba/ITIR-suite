<script lang="ts">
  import Section from '$lib/ui/Section.svelte';

  export let toolUse: Record<string, unknown> | undefined;

  type Family = {
    family: string;
    count: number;
    unique_variants?: number;
    variants?: VariantAgg[];
  };

  type VariantAgg = {
    command: string; // normalized label
    count: number;
    example?: string; // one representative raw command (for tooltip)
  };

  function heredocDelimiter(cmd: string): string | null {
    // Collapse "python - <<'PY' ... PY" into a stable variant key.
    const m = cmd.match(/<<\s*(['"]?)([A-Za-z0-9_]+)\1/);
    return m?.[2] ? String(m[2]) : null;
  }

  function normalizeVariant(cmd: string): { key: string; label: string } {
    const delim = heredocDelimiter(cmd);
    if (delim) return { key: `heredoc:${delim}`, label: `'${delim}'` };
    return { key: cmd.trim(), label: cmd.trim() };
  }

  function aggregateVariants(raw: unknown): VariantAgg[] | undefined {
    if (!Array.isArray(raw)) return undefined;
    const agg = new Map<string, VariantAgg>();
    for (const v of raw) {
      const cmd = String((v as any)?.command ?? '');
      const count = Number((v as any)?.count ?? 0) || 0;
      if (!cmd.trim()) continue;
      const n = normalizeVariant(cmd);
      const cur = agg.get(n.key) ?? { command: n.label, count: 0, example: cmd };
      cur.count += count;
      agg.set(n.key, cur);
    }
    return [...agg.values()].sort((a, b) => b.count - a.count);
  }

  function families(): Family[] {
    const raw = toolUse?.['families'];
    if (!Array.isArray(raw)) return [];
    return raw
      .map((f) => ({
        family: String(f?.family ?? ''),
        count: Number(f?.count ?? 0),
        unique_variants: typeof f?.unique_variants === 'number' ? f.unique_variants : undefined,
        variants: aggregateVariants(f?.variants)?.slice(0, 6)
      }))
      .filter((f) => f.family)
      .sort((a, b) => b.count - a.count);
  }
</script>

<Section title="Tool Use" subtitle="Top command families (first pass).">
  {@const fs = families()}
  {#if fs.length}
    <div class="grid gap-3 md:grid-cols-2">
      {#each fs.slice(0, 8) as f (f.family)}
        <div class="rounded-xl bg-paper-100 ring-1 ring-ink-900/10 px-4 py-3">
          <div class="flex items-baseline justify-between gap-4">
            <div class="font-mono text-sm text-ink-950">{f.family}</div>
            <div class="font-mono text-xs text-ink-800/70">{f.count.toLocaleString()} calls</div>
          </div>
          {#if f.variants && f.variants.length}
            <ul class="mt-2 space-y-1">
              {#each f.variants as v (v.command)}
                <li class="flex items-start justify-between gap-4">
                  <div class="font-mono text-[11px] text-ink-800/70 break-all" title={v.example ?? v.command}>{v.command}</div>
                  <div class="shrink-0 font-mono text-[11px] text-ink-900/80">{v.count}</div>
                </li>
              {/each}
            </ul>
          {/if}
        </div>
      {/each}
    </div>
  {:else}
    <div class="text-sm text-ink-800/70">No tool use summary.</div>
  {/if}
</Section>
