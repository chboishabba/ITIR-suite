<script lang="ts">
  import Expander from '$lib/ui/Expander.svelte';
  import MarkdownLite from '$lib/ui/MarkdownLite.svelte';

  export let tool = 'tool_call';
  export let payload: Record<string, unknown> | null = null;
  export let rawJson: string | null = null;
  export let parseError: string | null = null;
  export let notebookSourceIndex: Record<string, number> | null = null;

  let copied = '';

  type Tone = 'neutral' | 'warn' | 'danger' | 'teal' | 'indigo';

  function badgeClass(tone: 'neutral' | 'warn' | 'danger'): string {
    if (tone === 'danger') return 'bg-red-600/10 text-red-900 ring-red-900/20';
    if (tone === 'warn') return 'bg-amber-500/10 text-amber-950 ring-amber-900/20';
    return 'bg-paper-100 text-ink-900/80 ring-ink-900/10';
  }

  function toolTone(t: string): Tone {
    const s = (t ?? '').toLowerCase().trim();
    if (s === 'exec_command') return 'teal';
    if (s === 'write_stdin') return 'indigo';
    if (s === 'update_plan') return 'warn';
    if (s === 'request_user_input') return 'warn';
    if (s === 'notebooklm_meta_event') return 'indigo';
    if (s === 'apply_patch') return 'danger';
    return 'neutral';
  }

  function toneBadge(tone: Tone): string {
    if (tone === 'teal') return 'bg-teal-600/10 text-teal-950 ring-teal-900/20';
    if (tone === 'indigo') return 'bg-indigo-600/10 text-indigo-950 ring-indigo-900/20';
    if (tone === 'danger') return badgeClass('danger');
    if (tone === 'warn') return badgeClass('warn');
    return badgeClass('neutral');
  }

  function getString(v: unknown): string {
    return typeof v === 'string' ? v : '';
  }

  function cmdText(): string {
    const c = payload ? payload['cmd'] : null;
    return typeof c === 'string' ? c : '';
  }

  function getNum(v: unknown): number | null {
    return typeof v === 'number' && Number.isFinite(v) ? v : null;
  }

  function getBool(v: unknown): boolean | null {
    return typeof v === 'boolean' ? v : null;
  }

  function getStringArray(v: unknown): string[] {
    if (!Array.isArray(v)) return [];
    return v
      .map((x) => (typeof x === 'string' ? x : ''))
      .filter((x) => x.trim().length > 0);
  }

  function shortHash(v: string): string {
    const clean = (v ?? '').replace(/^sha256:/i, '').trim();
    if (!clean) return '';
    return clean.length > 12 ? `${clean.slice(0, 12)}...` : clean;
  }

  function normalizeSourceType(v: string): string {
    const s = (v ?? '').trim();
    if (!s) return '';
    const noPrefix = s.replace(/^SourceType\./i, '').trim();
    return noPrefix.toUpperCase();
  }

  function sourceTypeBadgeText(v: string): string {
    const s = normalizeSourceType(v);
    if (s === 'GOOGLE_DOCS' || s === 'GOOGLE_DOC') return 'GDoc';
    if (s === 'PASTED_TEXT' || s === 'TEXT') return 'Text';
    if (s === 'PDF') return 'PDF';
    if (s === 'WEB_PAGE' || s === 'WEB') return 'Web';
    if (s === 'YOUTUBE') return 'YT';
    if (s === 'INFOGRAPHIC') return 'Infographic';
    if (!s) return 'Source';
    return s;
  }

  function sortedUniqueNums(values: number[]): number[] {
    return [...new Set(values.filter((n) => Number.isFinite(n) && n > 0))].sort((a, b) => a - b);
  }

  function formatRanges(values: number[]): string {
    const nums = sortedUniqueNums(values);
    if (!nums.length) return '';
    const parts: string[] = [];
    let start: number = nums[0]!;
    let prev: number = nums[0]!;
    for (let i = 1; i < nums.length; i++) {
      const cur = nums[i];
      if (cur === undefined) continue;
      if (cur === prev + 1) {
        prev = cur;
        continue;
      }
      parts.push(start === prev ? `${start}` : `${start}-${prev}`);
      start = cur;
      prev = cur;
    }
    parts.push(start === prev ? `${start}` : `${start}-${prev}`);
    return parts.join(',');
  }

  function isEmptyString(v: unknown): boolean {
    return typeof v === 'string' && v.length === 0;
  }

  function shortText(v: string, max = 140): string {
    const s = v.replace(/\s+/g, ' ').trim();
    if (s.length <= max) return s;
    return s.slice(0, max - 1) + '…';
  }

  function planItems(): Array<{ step: string; status: string }> {
    const p = payload?.plan;
    if (!Array.isArray(p)) return [];
    const out: Array<{ step: string; status: string }> = [];
    for (const it of p) {
      if (!it || typeof it !== 'object' || Array.isArray(it)) continue;
      const rec = it as Record<string, unknown>;
      const step = typeof rec.step === 'string' ? rec.step : '';
      const status = typeof rec.status === 'string' ? rec.status : '';
      if (!step && !status) continue;
      out.push({ step, status });
    }
    return out;
  }

  type ChoiceQuestion = {
    header: string;
    id: string;
    question: string;
    options: Array<{ label: string; description: string }>;
  };

  function choiceQuestions(): ChoiceQuestion[] {
    const raw = payload?.questions;
    if (!Array.isArray(raw)) return [];
    const out: ChoiceQuestion[] = [];
    for (const item of raw) {
      if (!item || typeof item !== 'object' || Array.isArray(item)) continue;
      const rec = item as Record<string, unknown>;
      const header = typeof rec.header === 'string' ? rec.header.trim() : '';
      const id = typeof rec.id === 'string' ? rec.id.trim() : '';
      const question = typeof rec.question === 'string' ? rec.question.trim() : '';
      const optsRaw = Array.isArray(rec.options) ? rec.options : [];
      const options = optsRaw
        .map((opt) => {
          if (!opt || typeof opt !== 'object' || Array.isArray(opt)) return null;
          const o = opt as Record<string, unknown>;
          return {
            label: typeof o.label === 'string' ? o.label.trim() : '',
            description: typeof o.description === 'string' ? o.description.trim() : ''
          };
        })
        .filter((opt): opt is { label: string; description: string } => Boolean(opt && (opt.label || opt.description)));
      if (!header && !id && !question && !options.length) continue;
      out.push({ header, id, question, options });
    }
    return out;
  }

  function statusPill(status: string): { cls: string; label: string } {
    const s = (status ?? '').toLowerCase().trim();
    if (s === 'completed' || s === 'done')
      return { cls: 'bg-emerald-600/10 text-emerald-950 ring-emerald-900/20', label: 'completed' };
    if (s === 'in_progress')
      return { cls: 'bg-sky-600/10 text-sky-950 ring-sky-900/20', label: 'in_progress' };
    if (s === 'pending' || !s) return { cls: 'bg-paper-100 text-ink-900/80 ring-ink-900/10', label: s || 'pending' };
    return { cls: 'bg-paper-100 text-ink-900/80 ring-ink-900/10', label: s };
  }

  async function copyText(label: string, text: string): Promise<void> {
    if (!text.trim()) return;
    try {
      await navigator.clipboard.writeText(text);
      copied = label;
      window.setTimeout(() => (copied = ''), 900);
    } catch {
      // ignore
    }
  }

  $: tone = toolTone(tool);
  $: cmd = cmdText();
  $: justification = getString(payload?.justification);
  $: prefixRule = Array.isArray(payload?.prefix_rule) ? payload?.prefix_rule : null;
  $: sandboxPerm = getString(payload?.sandbox_permissions);
  $: workdir = getString(payload?.workdir);
  $: tty = getBool(payload?.tty);
  $: sessionId = getNum(payload?.session_id);
  $: chars = typeof payload?.chars === 'string' ? (payload?.chars as string) : null;
  $: yieldMs = getNum(payload?.yield_time_ms);
  $: maxOut = getNum(payload?.max_output_tokens);
  $: explanation = getString(payload?.explanation);
  $: plan = planItems();
  $: questions = choiceQuestions();
  $: nbEvent = getString(payload?.event);
  $: nbNotebookHash = getString(payload?.notebook_id_hash);
  $: nbNoteHash = getString(payload?.note_id_hash);
  $: nbSourceCount = getNum(payload?.source_observed_count);
  $: nbUniqueNoteCount = getNum(payload?.unique_note_id_count);
  $: nbNoteHashes = getStringArray(payload?.note_id_hashes);
  $: nbNoteHashesTotal = getNum(payload?.note_id_hashes_total);
  $: nbNoteHashesTruncated = getBool(payload?.note_id_hashes_truncated);
  $: nbNotebookTitle = getString(payload?.notebook_title);
  $: nbSourceTitle = getString(payload?.source_title);
  $: nbSourceType = getString(payload?.source_type);
  $: nbSourceStatus = getString(payload?.source_status);
  $: nbSourceCreatedAt = getString(payload?.source_created_at);
  $: nbSourceUrl = getString(payload?.source_url);
  $: nbSourceSummary = getString(payload?.source_summary);
  $: nbSourceKeywords = getStringArray(payload?.source_keywords);
  $: nbArtifactIdHash = getString(payload?.artifact_id_hash);
  $: nbArtifactTitle = getString(payload?.artifact_title);
  $: nbArtifactType = getString(payload?.artifact_type);
  $: nbArtifactStatus = getString(payload?.artifact_status);
  $: nbArtifactCreatedAt = getString(payload?.artifact_created_at);
  $: nbSourceTitles = getStringArray(payload?.source_titles);
  $: nbSourceTypes = getStringArray(payload?.source_types);
  $: nbSourceStatuses = getStringArray(payload?.source_statuses);
  $: nbSourceSummaryCount = getNum(payload?.source_summary_count);
  $: nbSourceSummaries = getStringArray(payload?.source_summaries);
  $: nbHasContext = getBool(payload?.has_context);
  $: nbProvSource = getString(payload?.provenance_source);
  $: nbSourceTypeNorm = normalizeSourceType(nbSourceType);
  $: nbArtifactTypeNorm = normalizeSourceType(nbArtifactType);
  $: nbSourceTypesNorm = nbSourceTypes.map((v) => normalizeSourceType(v)).filter((v) => v.length > 0);
  $: refNums = (() => {
    if (!notebookSourceIndex) return [] as number[];
    const hashes: string[] = [];
    if (nbNoteHash) hashes.push(nbNoteHash);
    hashes.push(...nbNoteHashes);
    const mapped = hashes
      .map((h) => notebookSourceIndex[h] ?? 0)
      .filter((n) => Number.isFinite(n) && n > 0);
    return sortedUniqueNums(mapped);
  })();
  $: refLabel = formatRanges(refNums);
  $: eventChip =
    nbEvent === 'artifact_observed' && nbArtifactTypeNorm
      ? sourceTypeBadgeText(nbArtifactTypeNorm)
      : nbEvent === 'source_observed' && nbSourceTypeNorm
        ? sourceTypeBadgeText(nbSourceTypeNorm)
        : nbEvent === 'source_observed_batch'
          ? 'Sources'
          : nbEvent || 'event';
  $: eventNarrative =
    nbEvent === 'artifact_observed'
      ? `${sourceTypeBadgeText(nbArtifactTypeNorm || 'artifact')} output ${nbArtifactStatus || 'observed'}.`
      : nbEvent === 'source_observed'
        ? `${sourceTypeBadgeText(nbSourceTypeNorm || 'source')} indexed ${nbSourceStatus ? `(${nbSourceStatus})` : ''}.`.replace(
            /\s+\./g,
            '.'
          )
        : nbEvent === 'source_observed_batch'
          ? `${nbSourceCount ?? 0} sources observed${nbSourceSummaryCount ? `; ${nbSourceSummaryCount} snippet(s)` : ''}.`
          : '';
</script>

<div class="space-y-2">
  <div class="flex flex-wrap items-center justify-between gap-2">
    <div class="flex items-center gap-2">
      <div class="font-mono text-xs text-ink-900/80">
        <span class="inline-block rounded-md bg-paper-100 px-2 py-1 ring-1 ring-ink-900/10">>_</span>
        <span class={`ml-2 inline-flex items-center rounded-full px-2 py-1 text-[10px] font-mono uppercase tracking-widest ring-1 ${toneBadge(tone)}`}>
          {tool}
        </span>
      </div>
    </div>
    <div class="flex flex-wrap items-center gap-2">
      {#if sandboxPerm === 'require_escalated'}
        <span class={`rounded-full px-2 py-1 text-[10px] font-mono uppercase tracking-widest ring-1 ${badgeClass('danger')}`}>escalated</span>
      {/if}
      {#if justification}
        <span class={`rounded-full px-2 py-1 text-[10px] font-mono uppercase tracking-widest ring-1 ${badgeClass('warn')}`}>justification</span>
      {/if}
      {#if prefixRule}
        <span class={`rounded-full px-2 py-1 text-[10px] font-mono uppercase tracking-widest ring-1 ${badgeClass('neutral')}`}>prefix rule</span>
      {/if}
    </div>
  </div>

  {#if tool === 'exec_command' && cmd}
    <div class="rounded-xl bg-paper-50 ring-1 ring-ink-900/10">
      <div class="flex items-center justify-between gap-3 px-3 py-2">
        <div class="text-[10px] font-mono uppercase tracking-widest text-ink-800/60">cmd</div>
        <button
          type="button"
          class="rounded-md bg-paper-100 px-2 py-1 text-[10px] font-mono uppercase tracking-widest ring-1 ring-ink-900/10"
          on:click={() => copyText('cmd', cmd)}
        >
          {copied === 'cmd' ? 'copied' : 'copy'}
        </button>
      </div>
      <pre class="max-h-[220px] overflow-auto overscroll-contain whitespace-pre-wrap break-words font-mono text-[12px] leading-relaxed px-3 pb-3">{cmd}</pre>
      {#if workdir || tty !== null || yieldMs !== null || maxOut !== null}
        <div class="border-t border-ink-900/10 px-3 py-2 text-[11px] text-ink-800/70">
          <div class="flex flex-wrap items-center gap-x-4 gap-y-1 font-mono">
            {#if workdir}<span>workdir={workdir}</span>{/if}
            {#if tty !== null}<span>tty={tty ? 'true' : 'false'}</span>{/if}
            {#if yieldMs !== null}<span>yield_ms={yieldMs}</span>{/if}
            {#if maxOut !== null}<span>max_output_tokens={maxOut}</span>{/if}
          </div>
        </div>
      {/if}
    </div>
  {/if}

  {#if tool === 'write_stdin'}
    <div class="rounded-xl bg-paper-50 ring-1 ring-ink-900/10 px-3 py-2">
      <div class="text-[10px] font-mono uppercase tracking-widest text-ink-800/60">stdin</div>
      <div class="mt-1 flex flex-wrap items-center gap-x-4 gap-y-1 font-mono text-[11px] text-ink-800/70">
        {#if sessionId !== null}<span>session_id={sessionId}</span>{/if}
        {#if yieldMs !== null}<span>yield_ms={yieldMs}</span>{/if}
        {#if maxOut !== null}<span>max_output_tokens={maxOut}</span>{/if}
        {#if chars !== null}
          <span>
            chars=
            {#if isEmptyString(chars)}
              (empty)
            {:else}
              {chars.length}
            {/if}
          </span>
        {/if}
      </div>
      {#if chars && chars.trim()}
        <pre class="mt-2 whitespace-pre-wrap break-words font-mono text-[12px] leading-relaxed text-ink-900/80">{shortText(chars, 500)}</pre>
      {/if}
    </div>
  {/if}

  {#if tool === 'update_plan'}
    <div class="rounded-xl bg-paper-50 ring-1 ring-ink-900/10 px-3 py-2">
      <div class="flex flex-wrap items-center justify-between gap-2">
        <div class="text-[10px] font-mono uppercase tracking-widest text-ink-800/60">plan</div>
        <div class="text-[11px] font-mono text-ink-800/60">{plan.length.toLocaleString()} item(s)</div>
      </div>
      {#if explanation}
        <div class="mt-2 text-[12px] text-ink-900/80 whitespace-pre-wrap">{explanation}</div>
      {/if}
      {#if plan.length}
        <div class="mt-2 space-y-2">
          {#each plan as p, idx (idx)}
            {@const pill = statusPill(p.status)}
            <div class="flex items-start gap-2">
              <span class={`mt-[2px] inline-flex items-center rounded-full px-2 py-[2px] text-[10px] font-mono uppercase tracking-widest ring-1 ${pill.cls}`}>{pill.label}</span>
              <div class="min-w-0 text-[12px] text-ink-950/90 leading-snug">{p.step}</div>
            </div>
          {/each}
        </div>
      {:else}
        <div class="mt-2 text-[12px] text-ink-800/60">No plan items found in payload.</div>
      {/if}
    </div>
  {/if}

  {#if tool === 'request_user_input'}
    <div class="rounded-xl bg-paper-50 ring-1 ring-ink-900/10 px-3 py-2">
      <div class="flex flex-wrap items-center justify-between gap-2">
        <div class="text-[10px] font-mono uppercase tracking-widest text-ink-800/60">user input request</div>
        <div class="text-[11px] font-mono text-ink-800/60">{questions.length.toLocaleString()} question(s)</div>
      </div>
      {#if questions.length}
        <div class="mt-3 space-y-3">
          {#each questions as q, idx (`q_${idx}_${q.id}`)}
            <div class="rounded-lg bg-paper-100 ring-1 ring-ink-900/10 px-3 py-3">
              <div class="flex flex-wrap items-center gap-2">
                {#if q.header}
                  <span class="inline-flex items-center rounded-full bg-amber-500/10 text-amber-950 ring-1 ring-amber-900/20 px-2 py-[2px] text-[10px] font-mono uppercase tracking-widest">
                    {q.header}
                  </span>
                {/if}
                {#if q.id}
                  <span class="font-mono text-[10px] uppercase tracking-widest text-ink-800/55">{q.id}</span>
                {/if}
              </div>
              {#if q.question}
                <div class="mt-2 text-[13px] leading-snug text-ink-950/90">{q.question}</div>
              {/if}
              {#if q.options.length}
                <div class="mt-3 space-y-2">
                  {#each q.options as opt, j (`opt_${j}_${opt.label}`)}
                    <div class="rounded-md bg-paper-50 ring-1 ring-ink-900/10 px-3 py-2">
                      <div class="text-[12px] font-semibold leading-snug text-ink-950/90">{opt.label}</div>
                      {#if opt.description}
                        <div class="mt-1 text-[12px] leading-snug text-ink-800/75">{opt.description}</div>
                      {/if}
                    </div>
                  {/each}
                </div>
              {/if}
            </div>
          {/each}
        </div>
      {:else}
        <div class="mt-2 text-[12px] text-ink-800/60">No structured questions found in payload.</div>
      {/if}
    </div>
  {/if}

  {#if tool === 'notebooklm_meta_event'}
    <div class="rounded-xl bg-paper-50 ring-1 ring-ink-900/10 px-3 py-2">
      <div class="flex flex-wrap items-center justify-between gap-2">
        <div class="text-[10px] font-mono uppercase tracking-widest text-ink-800/60">notebooklm</div>
        {#if eventChip}
          <span class="rounded-full bg-indigo-600/10 text-indigo-950 ring-1 ring-indigo-900/20 px-2 py-1 text-[10px] font-mono uppercase tracking-widest">
            {eventChip}
          </span>
        {/if}
      </div>
      {#if nbNotebookTitle}
        <div class="mt-2 text-[13px] text-ink-950/90 font-semibold leading-snug">{nbNotebookTitle}</div>
      {/if}
      {#if eventNarrative}
        <div class="mt-1 text-[11px] text-ink-900/75">{eventNarrative}</div>
      {/if}
      <div class="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 font-mono text-[11px] text-ink-800/70">
        {#if refLabel}
          <span class="rounded-md bg-paper-100 ring-1 ring-ink-900/10 px-2 py-[1px]">refs={refLabel}</span>
        {/if}
        {#if nbNotebookHash}<span>notebook={shortHash(nbNotebookHash)}</span>{/if}
        {#if nbNoteHash}<span>note={shortHash(nbNoteHash)}</span>{/if}
        {#if nbSourceCount !== null}<span>sources_observed={nbSourceCount}</span>{/if}
        {#if nbUniqueNoteCount !== null}<span>unique_notes={nbUniqueNoteCount}</span>{/if}
        {#if nbSourceSummaryCount !== null}<span>summary_count={nbSourceSummaryCount}</span>{/if}
        {#if nbHasContext !== null}<span>has_context={nbHasContext ? 'true' : 'false'}</span>{/if}
        {#if nbProvSource}<span>src={nbProvSource}</span>{/if}
      </div>
      {#if nbSourceTitle || nbSourceType || nbSourceStatus || nbSourceCreatedAt || nbSourceUrl}
        <div class="mt-2 rounded-lg bg-paper-100 ring-1 ring-ink-900/10 px-2 py-2">
          <div class="text-[10px] font-mono uppercase tracking-widest text-ink-800/60">source</div>
          <div class="mt-1 flex flex-wrap items-center gap-x-4 gap-y-1 font-mono text-[11px] text-ink-800/75">
            {#if nbSourceTitle}<span>title={shortText(nbSourceTitle, 120)}</span>{/if}
            {#if nbSourceTypeNorm}
              <span class="inline-flex items-center rounded-full bg-paper-50 ring-1 ring-ink-900/10 px-2 py-[1px]">{sourceTypeBadgeText(nbSourceTypeNorm)}</span>
            {/if}
            {#if nbSourceStatus}<span>status={nbSourceStatus}</span>{/if}
            {#if nbSourceCreatedAt}<span>created={nbSourceCreatedAt}</span>{/if}
          </div>
          {#if nbSourceUrl}
            <a class="mt-1 block break-all font-mono text-[11px] text-sky-900 underline decoration-sky-900/30 underline-offset-2" href={nbSourceUrl} target="_blank" rel="noreferrer">{nbSourceUrl}</a>
          {/if}
        </div>
      {/if}
      {#if nbSourceSummary}
        <div class="mt-2 rounded-lg bg-paper-100 ring-1 ring-ink-900/10 px-2 py-2">
          <div class="text-[10px] font-mono uppercase tracking-widest text-ink-800/60">source snippet</div>
          <div class="mt-1 max-h-[260px] overflow-auto overscroll-contain pr-1">
            <MarkdownLite text={nbSourceSummary} />
          </div>
        </div>
      {/if}
      {#if nbSourceKeywords.length}
        <div class="mt-2 flex flex-wrap items-center gap-1">
          {#each nbSourceKeywords as kw (kw)}
            <span class="inline-flex items-center rounded-full bg-indigo-600/10 text-indigo-950 ring-1 ring-indigo-900/20 px-2 py-[2px] text-[10px] font-mono">{kw}</span>
          {/each}
        </div>
      {/if}
      {#if nbArtifactTitle || nbArtifactType || nbArtifactStatus || nbArtifactCreatedAt || nbArtifactIdHash}
        <div class="mt-2 rounded-lg bg-paper-100 ring-1 ring-ink-900/10 px-2 py-2">
          <div class="text-[10px] font-mono uppercase tracking-widest text-ink-800/60">artifact</div>
          <div class="mt-1 flex flex-wrap items-center gap-x-4 gap-y-1 font-mono text-[11px] text-ink-800/75">
            {#if nbArtifactTitle}<span>title={shortText(nbArtifactTitle, 120)}</span>{/if}
            {#if nbArtifactTypeNorm}
              <span class="inline-flex items-center rounded-full bg-paper-50 ring-1 ring-ink-900/10 px-2 py-[1px]">{sourceTypeBadgeText(nbArtifactTypeNorm)}</span>
            {/if}
            {#if nbArtifactStatus}<span>status={nbArtifactStatus}</span>{/if}
            {#if nbArtifactCreatedAt}<span>created={nbArtifactCreatedAt}</span>{/if}
            {#if nbArtifactIdHash}<span>id={shortHash(nbArtifactIdHash)}</span>{/if}
          </div>
        </div>
      {/if}
      {#if nbSourceTitles.length || nbSourceTypes.length || nbSourceStatuses.length || nbSourceSummaries.length}
        <Expander title="batched source details" collapsedHeight={0} collapsedLabel="Show" expandedLabel="Hide" showFade={false} lazy={true}>
          <div class="mt-2 space-y-2">
            {#if nbSourceTitles.length}
              <div>
                <div class="text-[10px] font-mono uppercase tracking-widest text-ink-800/60">titles</div>
                <pre class="mt-1 max-h-[160px] overflow-auto overscroll-contain whitespace-pre-wrap break-words font-mono text-[11px] leading-relaxed text-ink-900/80">{nbSourceTitles.join('\n')}</pre>
              </div>
            {/if}
            {#if nbSourceTypesNorm.length}
              <div class="font-mono text-[11px] text-ink-800/75">types: {nbSourceTypesNorm.map((v) => sourceTypeBadgeText(v)).join(', ')}</div>
            {/if}
            {#if nbSourceStatuses.length}
              <div class="font-mono text-[11px] text-ink-800/75">statuses: {nbSourceStatuses.join(', ')}</div>
            {/if}
            {#if nbSourceSummaries.length}
              <div>
                <div class="text-[10px] font-mono uppercase tracking-widest text-ink-800/60">summary snippets</div>
                <div class="mt-1 max-h-[260px] overflow-auto overscroll-contain space-y-3 pr-1">
                  {#each nbSourceSummaries as summary, i (`sum_${i}`)}
                    <div class="rounded-md bg-paper-50 ring-1 ring-ink-900/10 px-2 py-1">
                      <MarkdownLite text={summary} />
                    </div>
                  {/each}
                </div>
              </div>
            {/if}
          </div>
        </Expander>
      {/if}
      {#if nbNoteHashes.length}
        <Expander title="source ids" collapsedHeight={0} collapsedLabel="Show" expandedLabel="Hide" showFade={false} lazy={true}>
          {#if nbNoteHashesTotal !== null}
            <div class="mb-1 font-mono text-[10px] text-ink-800/60">
              showing {nbNoteHashes.length} of {nbNoteHashesTotal}{#if nbNoteHashesTruncated} (truncated){/if}
            </div>
          {/if}
          <pre class="mt-2 max-h-[220px] overflow-auto overscroll-contain whitespace-pre-wrap break-words font-mono text-[11px] leading-relaxed text-ink-900/80">{nbNoteHashes.join('\n')}</pre>
        </Expander>
      {/if}
    </div>
  {/if}

  {#if justification}
    <div class="rounded-xl bg-amber-500/10 ring-1 ring-amber-900/20 px-3 py-2 text-[12px] text-amber-950">
      <div class="text-[10px] font-mono uppercase tracking-widest text-amber-950/70">justification</div>
      <div class="mt-1 whitespace-pre-wrap">{justification}</div>
    </div>
  {/if}

  {#if prefixRule}
    <div class="rounded-xl bg-paper-50 ring-1 ring-ink-900/10 px-3 py-2">
      <div class="text-[10px] font-mono uppercase tracking-widest text-ink-800/60">prefix_rule</div>
      <pre class="mt-1 whitespace-pre-wrap break-words font-mono text-[12px] leading-relaxed">{JSON.stringify(prefixRule, null, 2)}</pre>
    </div>
  {/if}

  <Expander title="raw payload" collapsedHeight={0} collapsedLabel="Show" expandedLabel="Hide" showFade={false} lazy={true}>
    {#if parseError}
      <div class="text-[11px] text-red-900/80">parse error: {parseError}</div>
    {/if}
    <div class="mt-2 flex items-center justify-between gap-3">
      <div class="text-[10px] font-mono uppercase tracking-widest text-ink-800/40">json</div>
      <button
        type="button"
        class="rounded-md bg-paper-100 px-2 py-1 text-[10px] font-mono uppercase tracking-widest ring-1 ring-ink-900/10"
        on:click={() => copyText('json', rawJson ?? '')}
      >
        {copied === 'json' ? 'copied' : 'copy'}
      </button>
    </div>
    <pre class="mt-2 max-h-[260px] overflow-auto overscroll-contain whitespace-pre-wrap break-words font-mono text-[11px] leading-relaxed text-ink-900/80">{rawJson ?? ''}</pre>
  </Expander>
</div>
