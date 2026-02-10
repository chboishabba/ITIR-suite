<script lang="ts">
  import Section from '$lib/ui/Section.svelte';

  export let toolUse: Record<string, unknown> | undefined;

  type VariantLeaf = {
    key: string;
    label: string;
    count: number;
    example?: string; // one representative raw command (tooltip)
  };

  type TrunkGroup = {
    trunk: string; // e.g. "'PY'"
    count: number;
    leaves: VariantLeaf[];
  };

  type Family = {
    family: string;
    count: number;
    unique_variants?: number;
    trunks?: TrunkGroup[];
    plain?: VariantLeaf[];
  };

  function heredocDelimiter(cmd: string): string | null {
    const m = cmd.match(/<<\s*(['"]?)([A-Za-z0-9_]+)\1/);
    return m?.[2] ? String(m[2]) : null;
  }

  function fnv1a(text: string): string {
    let h = 2166136261;
    for (let i = 0; i < text.length; i++) {
      h ^= text.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    // short, stable id for grouping identical scripts
    return (h >>> 0).toString(16).padStart(8, '0');
  }

  type ShellSplit = { segments: string[]; ops: string[] };

  function splitShellTopLevel(line: string): ShellSplit {
    // Conservative shell splitter for "pretty grouping" only.
    // Splits on &&, ||, ;, | when not inside single/double quotes.
    const segments: string[] = [];
    const ops: string[] = [];
    let cur = '';
    let inS = false;
    let inD = false;
    let esc = false;

    const flush = () => {
      const t = cur.trim();
      if (t) segments.push(t);
      cur = '';
    };

    for (let i = 0; i < line.length; i++) {
      const ch = line[i]!;
      if (esc) {
        cur += ch;
        esc = false;
        continue;
      }
      if (ch === '\\') {
        cur += ch;
        esc = true;
        continue;
      }
      if (!inD && ch === "'") {
        inS = !inS;
        cur += ch;
        continue;
      }
      if (!inS && ch === '"') {
        inD = !inD;
        cur += ch;
        continue;
      }

      if (!inS && !inD) {
        const two = line.slice(i, i + 2);
        if (two === '&&' || two === '||') {
          flush();
          ops.push(two);
          i++;
          continue;
        }
        if (ch === ';' || ch === '|') {
          flush();
          ops.push(ch);
          continue;
        }
      }

      cur += ch;
    }
    flush();
    return { segments, ops };
  }

  function stripEnvPrefix(seg: string): string {
    // Drop leading VAR=... assignments for operator detection/labels.
    let s = seg.trim();
    for (let i = 0; i < 6; i++) {
      const m = s.match(/^([A-Za-z_][A-Za-z0-9_]*)=([^\s]+)\s+(.*)$/);
      if (!m) break;
      s = (m[3] ?? '').trim();
    }
    return s;
  }

  function firstToken(seg: string): string {
    const s = stripEnvPrefix(seg);
    const tok = s.split(/\s+/, 1)[0] ?? '';
    return tok.trim();
  }

  function opWordForFamily(family: string, word: string): boolean {
    const w = word.trim();
    if (!w) return false;
    const base = w.includes('/') ? w.slice(w.lastIndexOf('/') + 1) : w;
    if (family === 'python') return base === 'python' || base === 'python3' || base === 'python2';
    if (family === 'bash') return base === 'bash' || base === 'sh' || base === 'zsh';
    return base === family;
  }

  function focusSegmentIndex(family: string, segments: string[]): number {
    for (let i = 0; i < segments.length; i++) {
      const seg = stripEnvPrefix(segments[i] ?? '');
      const tok = seg.split(/\s+/, 1)[0] ?? '';
      if (opWordForFamily(family, tok)) return i;
    }
    return Math.max(0, segments.length - 1);
  }

  function suffixKeyAndLabel(segments: string[], ops: string[], focus: number): { key: string; label: string } {
    if (focus >= segments.length - 1) return { key: '', label: '' };
    const partsKey: string[] = [];
    const partsLabel: string[] = [];
    const maxParts = 2;
    for (let j = focus; j < Math.min(segments.length - 1, focus + maxParts); j++) {
      const op = ops[j] ?? '';
      const next = segments[j + 1] ?? '';
      const tok = firstToken(next);
      if (!op || !tok) continue;
      partsKey.push(`${op}${tok}`);
      partsLabel.push(`${op} ${truncate(next, 32)}`);
    }
    const key = partsKey.join(' ');
    const label = partsLabel.length ? ` ${partsLabel.join(' ')}` : '';
    return { key, label };
  }

  function splitLines(cmd: string): string[] {
    return cmd.replaceAll('\r\n', '\n').replaceAll('\r', '\n').split('\n');
  }

  function isPatchBlock(cmd: string): boolean {
    const s = cmd.trimStart();
    if (s.startsWith('*** Begin Patch')) return true;
    // Sometimes the patch is nested in a larger string; still treat as patch-like.
    return cmd.includes('\n*** Begin Patch') || cmd.includes('*** Begin Patch\n');
  }

  function parsePatchSummary(cmd: string): { label: string; key: string } {
    const lines = splitLines(cmd);
    const hits: Array<{ op: string; path: string }> = [];

    for (const ln of lines) {
      const s = ln.trim();
      if (s.startsWith('*** Update File: ')) hits.push({ op: 'Update', path: s.slice('*** Update File: '.length).trim() });
      else if (s.startsWith('*** Add File: ')) hits.push({ op: 'Add', path: s.slice('*** Add File: '.length).trim() });
      else if (s.startsWith('*** Delete File: ')) hits.push({ op: 'Delete', path: s.slice('*** Delete File: '.length).trim() });
      else if (s.startsWith('*** Move to: ')) hits.push({ op: 'Move', path: s.slice('*** Move to: '.length).trim() });
      if (hits.length >= 8) break;
    }

    if (!hits.length) {
      const key = `patch:${fnv1a(cmd)}`;
      return { label: 'Patch (unparsed)', key };
    }

    const uniq = new Map<string, { op: string; path: string }>();
    for (const h of hits) {
      const k = `${h.op}:${h.path}`;
      if (!uniq.has(k)) uniq.set(k, h);
    }
    const items = [...uniq.values()];

    const opCounts = new Map<string, number>();
    for (const h of items) opCounts.set(h.op, (opCounts.get(h.op) ?? 0) + 1);
    const opSummary = [...opCounts.entries()]
      .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
      .map(([op, n]) => `${op}${n > 1 ? `×${n}` : ''}`)
      .join(', ');

    const first = items[0]!;
    const extra = items.length > 1 ? ` (+${items.length - 1})` : '';
    const label = `${opSummary}: ${truncate(first.path, 56)}${extra}`;
    const key = `patch:${fnv1a(items.map((h) => `${h.op}:${h.path}`).join('|'))}`;
    return { label, key };
  }

  function extractHeredocBody(cmd: string, delim: string): string {
    const lines = splitLines(cmd);
    // Identify the line that starts the heredoc and the delimiter terminator line.
    const start = lines.findIndex((ln) => ln.includes('<<') && ln.includes(delim));
    let end = -1;
    for (let i = lines.length - 1; i >= 0; i--) {
      if (lines[i]?.trim() === delim) {
        end = i;
        break;
      }
    }
    if (start >= 0 && end > start) return lines.slice(start + 1, end).join('\n');
    // Fallback: best-effort, still groupable by hash.
    return cmd;
  }

  function firstMeaningfulLine(body: string): string {
    for (const ln of splitLines(body)) {
      const s = ln.trim();
      if (!s) continue;
      if (s.startsWith('#')) continue;
      return s;
    }
    return '';
  }

  function firstNonImportLine(body: string): string {
    for (const ln of splitLines(body)) {
      const s = ln.trim();
      if (!s) continue;
      if (s.startsWith('#')) continue;
      if (s.startsWith('import ') || s.startsWith('from ')) continue;
      return s;
    }
    return '';
  }

  function truncate(s: string, n: number): string {
    const t = s.replace(/\s+/g, ' ').trim();
    if (t.length <= n) return t;
    return t.slice(0, Math.max(0, n - 1)) + '…';
  }

  function heredocSubLabel(family: string, cmd: string, delim: string): { label: string; key: string } {
    const firstLine = splitLines(cmd)[0] ?? '';
    const split = splitShellTopLevel(firstLine);
    const focus = focusSegmentIndex(family, split.segments);
    const suffix = suffixKeyAndLabel(split.segments, split.ops, focus);

    const body = extractHeredocBody(cmd, delim);
    const a = firstMeaningfulLine(body);
    const b = firstNonImportLine(body);
    const head = a && b && b !== a && (a.startsWith('import ') || a.startsWith('from ')) ? `${a} | ${b}` : a || b || '(empty)';
    const key = `heredoc:${delim}:${fnv1a(body)}:${suffix.key}`;
    return { label: truncate(head, 64) + suffix.label, key };
  }

  function aggregateVariants(
    family: string,
    raw: unknown
  ): { trunks: TrunkGroup[]; plain: VariantLeaf[] } | null {
    if (!Array.isArray(raw)) return null;

    const plain = new Map<string, VariantLeaf>();
    const trunks = new Map<string, Map<string, VariantLeaf>>();
    const trunkCounts = new Map<string, number>();

    for (const v of raw) {
      const cmd = String((v as any)?.command ?? '');
      const count = Number((v as any)?.count ?? 0) || 0;
      if (!cmd.trim() || count <= 0) continue;

      if (isPatchBlock(cmd)) {
        const trunk = "'PATCH'";
        const sub = parsePatchSummary(cmd);
        const leafMap = trunks.get(trunk) ?? new Map<string, VariantLeaf>();
        const cur = leafMap.get(sub.key) ?? { key: sub.key, label: sub.label, count: 0, example: cmd };
        cur.count += count;
        leafMap.set(sub.key, cur);
        trunks.set(trunk, leafMap);
        trunkCounts.set(trunk, (trunkCounts.get(trunk) ?? 0) + count);
        continue;
      }

      const firstLine = splitLines(cmd)[0] ?? cmd;
      const split = splitShellTopLevel(firstLine);
      const focus = focusSegmentIndex(family, split.segments);
      const suffix = suffixKeyAndLabel(split.segments, split.ops, focus);

      const delim = heredocDelimiter(cmd);
      if (delim) {
        const trunk = `'${delim}'`;
        const sub = heredocSubLabel(family, cmd, delim);
        const leafMap = trunks.get(trunk) ?? new Map<string, VariantLeaf>();
        const cur = leafMap.get(sub.key) ?? { key: sub.key, label: sub.label, count: 0, example: cmd };
        cur.count += count;
        leafMap.set(sub.key, cur);
        trunks.set(trunk, leafMap);
        trunkCounts.set(trunk, (trunkCounts.get(trunk) ?? 0) + count);
        continue;
      }

      // Prefer displaying/grouping by the family-relevant segment (plus a compact suffix showing pipes/&&).
      const focusSeg = split.segments[focus] ?? firstLine;
      const norm = stripEnvPrefix(focusSeg);
      const k = `${norm}::${suffix.key}`.trim();
      const label = truncate(norm, 84) + suffix.label;
      const cur = plain.get(k) ?? { key: k, label, count: 0, example: cmd };
      cur.count += count;
      plain.set(k, cur);
    }

    const trunkGroups: TrunkGroup[] = [...trunks.entries()]
      .map(([trunk, leafMap]) => ({
        trunk,
        count: trunkCounts.get(trunk) ?? 0,
        leaves: [...leafMap.values()].sort((a, b) => b.count - a.count)
      }))
      .sort((a, b) => b.count - a.count);

    const plainLeaves = [...plain.values()].sort((a, b) => b.count - a.count);
    return { trunks: trunkGroups, plain: plainLeaves };
  }

  function families(): Family[] {
    const raw = toolUse?.['families'];
    if (!Array.isArray(raw)) return [];
    return raw
      .map((f) => ({
        family: String(f?.family ?? ''),
        count: Number(f?.count ?? 0),
        unique_variants: typeof f?.unique_variants === 'number' ? f.unique_variants : undefined,
        ...(() => {
          const family = String(f?.family ?? '');
          const agg = aggregateVariants(family, f?.variants);
          if (!agg) return {};
          return {
            trunks: agg.trunks.slice(0, 2).map((t) => ({ ...t, leaves: t.leaves.slice(0, 4) })),
            plain: agg.plain.slice(0, 6)
          };
        })()
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
          {#if f.trunks && f.trunks.length}
            <div class="mt-3 space-y-2">
              {#each f.trunks as t (t.trunk)}
                <div class="rounded-lg bg-paper-50 ring-1 ring-ink-900/10 px-3 py-2">
                  <div class="flex items-baseline justify-between gap-4">
                    <div class="font-mono text-xs text-ink-900/80">{t.trunk}</div>
                    <div class="font-mono text-[11px] text-ink-800/70">{t.count}</div>
                  </div>
                  <ul class="mt-2 space-y-1">
                    {#each t.leaves as v (v.key)}
                      <li class="flex items-start justify-between gap-4">
                        <div class="font-mono text-[11px] text-ink-800/70 break-words" title={v.example ?? v.label}>{v.label}</div>
                        <div class="shrink-0 font-mono text-[11px] text-ink-900/80">{v.count}</div>
                      </li>
                    {/each}
                  </ul>
                </div>
              {/each}
            </div>
          {/if}

          {#if f.plain && f.plain.length}
            <ul class="mt-3 space-y-1">
              {#each f.plain as v (v.key)}
                <li class="flex items-start justify-between gap-4">
                  <div class="font-mono text-[11px] text-ink-800/70 break-words" title={v.example ?? v.label}>{v.label}</div>
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
