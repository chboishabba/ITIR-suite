<script lang="ts">
  import Panel from '$lib/ui/Panel.svelte';

  export let corpusDocs: Array<{ relPath: string; name: string; bytes: number; ext: string }> = [];
  export let events: Array<any> = [];
  export let corpusRoot = 'SensibLaw/demo/ingest/gwb';

  function fmtBytes(n: number): string {
    const v = Number(n);
    if (!Number.isFinite(v) || v <= 0) return '0 B';
    const units = ['B', 'KB', 'MB', 'GB'];
    let u = 0;
    let x = v;
    while (x >= 1024 && u < units.length - 1) {
      x /= 1024;
      u += 1;
    }
    const digits = u === 0 ? 0 : u === 1 ? 1 : 2;
    return `${x.toFixed(digits)} ${units[u]}`;
  }

  function referencedCorpusPaths(eventsAll: Array<any>): Set<string> {
    const out = new Set<string>();
    for (const e of eventsAll ?? []) {
      const cits = Array.isArray(e?.citations) ? e.citations : [];
      for (const c of cits) {
        const follow = Array.isArray(c?.follow) ? c.follow : [];
        for (const f of follow) {
          const p = String(f?.path ?? '').trim();
          const u = String(f?.url ?? '').trim();
          if (p) out.add(p);
          if (u) out.add(u);
        }
      }
      const refs = Array.isArray(e?.sl_references) ? e.sl_references : [];
      for (const r of refs) {
        const follow = Array.isArray(r?.follow) ? r.follow : [];
        for (const f of follow) {
          const p = String(f?.path ?? '').trim();
          const u = String(f?.url ?? '').trim();
          if (p) out.add(p);
          if (u) out.add(u);
        }
      }
    }
    return out;
  }

  function refHasDoc(ref: Set<string>, relPath: string, name: string): boolean {
    const relNorm = String(relPath || '').replaceAll('\\', '/');
    const nameNorm = String(name || '').trim();
    if (!relNorm && !nameNorm) return false;
    for (const raw of ref) {
      const x = String(raw || '').replaceAll('\\', '/');
      if (!x) continue;
      if (relNorm && (x === relNorm || x.endsWith('/' + relNorm))) return true;
      if (nameNorm && (x === nameNorm || x.endsWith('/' + nameNorm))) return true;
    }
    return false;
  }

  $: referenced = referencedCorpusPaths(events);
  $: referencedCount = referenced.size;
</script>

{#if corpusDocs.length}
  <Panel>
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Corpus docs</div>
        <div class="mt-1 text-xs text-ink-800/60">
          root: <span class="font-mono">{corpusRoot}</span> | files:{' '}
          <span class="font-mono">{corpusDocs.length}</span>
          <span class="mx-2">|</span>
          follow_hints_in_run: <span class="font-mono">{referencedCount}</span>
        </div>
      </div>
    </div>
    {#if referencedCount === 0}
      <div class="mt-2 text-xs text-ink-800/70">
        This selected dataset/run emitted no citation/sl_ref follow hints, so everything below will show as <span class="font-mono">unreferenced</span>.
        If you want the corpus files to appear as sources, switch Dataset to <span class="font-mono">gwb_corpus_v1</span>.
      </div>
    {/if}
    <div class="mt-3 flex flex-wrap gap-2 text-[11px]">
      {#each corpusDocs as d (d.relPath)}
        {@const isRef = refHasDoc(referenced, d.relPath, d.name)}
        <span
          class={`inline-flex items-center gap-2 rounded ring-1 ring-ink-900/10 px-2 py-1 ${
            isRef ? 'bg-emerald-50' : 'bg-paper-100'
          }`}
        >
          <span class="font-mono text-ink-900">{d.name}</span>
          <span class="font-mono text-ink-800/60">{d.ext}</span>
          <span class="font-mono text-ink-800/60">{fmtBytes(d.bytes)}</span>
          <span
            class={`rounded px-1.5 py-0.5 font-mono ${
              isRef ? 'bg-emerald-200/60 text-emerald-900' : 'bg-ink-950/5 text-ink-800/70'
            }`}
            title={d.relPath}
          >
            {isRef ? 'referenced' : 'unreferenced'}
          </span>
        </span>
      {/each}
    </div>
    <div class="mt-2 text-xs text-ink-800/60">
      "Referenced" means the current AAO run emitted a citation/sl_ref follow hint pointing at that file path/URL. It does not guarantee we extracted semantic events from the doc content.
    </div>
  </Panel>
{/if}
