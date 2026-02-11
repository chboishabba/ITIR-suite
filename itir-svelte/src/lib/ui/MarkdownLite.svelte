<script lang="ts">
  export let text = '';

  type InlineTok =
    | { t: 'text'; s: string }
    | { t: 'bold'; s: string }
    | { t: 'code'; s: string };

  type Block =
    | { k: 'code'; lang: string; code: string }
    | { k: 'h'; level: 1 | 2 | 3; inl: InlineTok[] }
    | { k: 'p'; lines: InlineTok[][] }
    | { k: 'ul'; items: InlineTok[][] };

  function parseInline(line: string): InlineTok[] {
    const s = line ?? '';
    const out: InlineTok[] = [];
    let i = 0;
    while (i < s.length) {
      // Inline code: `...`
      if (s[i] === '`') {
        const j = s.indexOf('`', i + 1);
        if (j > i + 1) {
          out.push({ t: 'code', s: s.slice(i + 1, j) });
          i = j + 1;
          continue;
        }
      }
      // Bold: **...**
      if (s[i] === '*' && s[i + 1] === '*') {
        const j = s.indexOf('**', i + 2);
        if (j > i + 2) {
          out.push({ t: 'bold', s: s.slice(i + 2, j) });
          i = j + 2;
          continue;
        }
      }
      // Plain text until next marker.
      const nextCode = s.indexOf('`', i);
      const nextBold = s.indexOf('**', i);
      let next = -1;
      if (nextCode !== -1) next = next === -1 ? nextCode : Math.min(next, nextCode);
      if (nextBold !== -1) next = next === -1 ? nextBold : Math.min(next, nextBold);
      if (next === -1) next = s.length;
      out.push({ t: 'text', s: s.slice(i, next) });
      i = next;
    }
    return out.filter((t) => t.s.length > 0);
  }

  function parseBlocks(input: string): Block[] {
    const lines = String(input ?? '').replace(/\r\n/g, '\n').split('\n');
    const blocks: Block[] = [];

    function tryParseJsonBlock(startIdx: number): { block: Block; nextIdx: number } | null {
      const first = (lines[startIdx] ?? '').trim();
      if (!(first.startsWith('{') || first.startsWith('['))) return null;

      // Heuristic: consume until a plausible end line and validate with JSON.parse.
      const buf: string[] = [];
      for (let j = startIdx; j < Math.min(lines.length, startIdx + 80); j++) {
        buf.push(lines[j] ?? '');
        const joined = buf.join('\n').trim();
        if (joined.length > 20_000) return null;
        const last = joined[joined.length - 1];
        if (!(last === '}' || last === ']')) continue;
        try {
          const v = JSON.parse(joined);
          const code = JSON.stringify(v, null, 2);
          return { block: { k: 'code', lang: 'json', code }, nextIdx: j + 1 };
        } catch {
          // Keep consuming; it might be incomplete JSON.
        }
      }
      return null;
    }

    let i = 0;
    while (i < lines.length) {
      const line = lines[i] ?? '';

      // Fence code blocks.
      const fence = line.match(/^```(\S+)?\s*$/);
      if (fence) {
        const lang = (fence[1] ?? '').trim();
        i++;
        const buf: string[] = [];
        while (i < lines.length && !/^```\s*$/.test(lines[i] ?? '')) {
          buf.push(lines[i] ?? '');
          i++;
        }
        // Skip closing fence if present.
        if (i < lines.length && /^```\s*$/.test(lines[i] ?? '')) i++;
        blocks.push({ k: 'code', lang, code: buf.join('\n') });
        continue;
      }

      // Skip repeated blank lines.
      if (!line.trim()) {
        i++;
        continue;
      }

      // JSON snippet blocks (common in chat guidance): render as a code block.
      const jsonBlock = tryParseJsonBlock(i);
      if (jsonBlock) {
        blocks.push(jsonBlock.block);
        i = jsonBlock.nextIdx;
        continue;
      }

      // Headings (H1-H3).
      const h = line.match(/^(#{1,3})\s+(.*)$/);
      if (h) {
        const marks = h[1] ?? '#';
        const level = Math.min(3, marks.length) as 1 | 2 | 3;
        blocks.push({ k: 'h', level, inl: parseInline(h[2] ?? '') });
        i++;
        continue;
      }

      // Unordered list.
      if (/^[-*]\s+/.test(line)) {
        const items: InlineTok[][] = [];
        while (i < lines.length && /^[-*]\s+/.test(lines[i] ?? '')) {
          const item = (lines[i] ?? '').replace(/^[-*]\s+/, '');
          items.push(parseInline(item));
          i++;
        }
        blocks.push({ k: 'ul', items });
        continue;
      }

      // Paragraph: gather until blank line / next structural marker.
      const paraLines: InlineTok[][] = [];
      while (i < lines.length) {
        const l = lines[i] ?? '';
        if (!l.trim()) break;
        if (/^```/.test(l)) break;
        if (/^(#{1,3})\s+/.test(l)) break;
        if (/^[-*]\s+/.test(l)) break;
        paraLines.push(parseInline(l));
        i++;
      }
      blocks.push({ k: 'p', lines: paraLines });
    }

    return blocks;
  }

  $: blocks = parseBlocks(text);
</script>

<div class="text-[12px] leading-relaxed text-ink-950/90">
  {#each blocks as b, idx (idx)}
    {#if b.k === 'h'}
      {#if b.level === 1}
        <h1 class="text-[15px] font-mono tracking-tight mt-2 mb-2">
          {#each b.inl as t, j (j)}
            {#if t.t === 'bold'}<strong>{t.s}</strong>{:else if t.t === 'code'}<code class="font-mono">{t.s}</code>{:else}{t.s}{/if}
          {/each}
        </h1>
      {:else if b.level === 2}
        <h2 class="text-[14px] font-mono tracking-tight mt-2 mb-1">
          {#each b.inl as t, j (j)}
            {#if t.t === 'bold'}<strong>{t.s}</strong>{:else if t.t === 'code'}<code class="font-mono">{t.s}</code>{:else}{t.s}{/if}
          {/each}
        </h2>
      {:else}
        <h3 class="text-[13px] font-mono tracking-tight mt-2 mb-1">
          {#each b.inl as t, j (j)}
            {#if t.t === 'bold'}<strong>{t.s}</strong>{:else if t.t === 'code'}<code class="font-mono">{t.s}</code>{:else}{t.s}{/if}
          {/each}
        </h3>
      {/if}
    {:else if b.k === 'code'}
      <pre class="max-h-[320px] overflow-auto overscroll-contain whitespace-pre rounded-lg bg-paper-100 ring-1 ring-ink-900/10 px-3 py-2 font-mono text-[11px] leading-relaxed text-ink-950/90"><code>{b.code}</code></pre>
    {:else if b.k === 'ul'}
      <ul class="my-2 list-disc pl-5">
        {#each b.items as item, j (j)}
          <li>
            {#each item as t, k (k)}
              {#if t.t === 'bold'}<strong>{t.s}</strong>{:else if t.t === 'code'}<code class="font-mono">{t.s}</code>{:else}{t.s}{/if}
            {/each}
          </li>
        {/each}
      </ul>
    {:else}
      <p class="my-2 whitespace-pre-wrap break-words">
        {#each b.lines as line, j (j)}
          {#each line as t, k (k)}
            {#if t.t === 'bold'}<strong>{t.s}</strong>{:else if t.t === 'code'}<code class="font-mono">{t.s}</code>{:else}{t.s}{/if}
          {/each}
          {#if j < b.lines.length - 1}<br />{/if}
        {/each}
      </p>
    {/if}
  {/each}
</div>
