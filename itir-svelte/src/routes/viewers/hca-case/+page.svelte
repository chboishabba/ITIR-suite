<script lang="ts">
  import DashboardShell from '$lib/sb-dashboard/components/DashboardShell.svelte';
  import Section from '$lib/ui/Section.svelte';
  import Panel from '$lib/ui/Panel.svelte';
  import TranscriptViewer from '$lib/viewers/TranscriptViewer.svelte';
  import DocumentViewer from '$lib/viewers/DocumentViewer.svelte';
  import FolderListViewer from '$lib/viewers/FolderListViewer.svelte';
  import { cuesFromSegments, cuesFromTranscriptText, type TranscriptCue } from '$lib/viewers/transcript';

  export let data: {
    baseRel: string;
    transcriptFiles: Array<{ id: string; name: string; relPath: string; bytes: number; kind: 'file' | 'dir' }>;
    documentFiles: Array<{ id: string; name: string; relPath: string; bytes: number; kind: 'file' | 'dir' }>;
    selectedTranscriptId: string | null;
    selectedDocumentId: string | null;
    audioSrc: string | null;
    transcriptMarkdown: string;
    transcriptSegments: Array<{ start: string; end: string; text: string }>;
    selectedDocumentText: string;
    selectedDocumentName: string | null;
  };

  type SelectionState = { kind: 'cue' | 'line'; label: string; detail: string } | null;
  type DocumentLineSelectEvent = {
    lineNumber: number;
    text: string;
    charStart: number;
    charEnd: number;
  };
  let selectionState: SelectionState = null;

  $: cueRows = (() => {
    const seg = cuesFromSegments(data.transcriptSegments || []);
    if (seg.length) return seg;
    return cuesFromTranscriptText(data.transcriptMarkdown || '');
  })();

  $: selectedTranscriptName =
    data.transcriptFiles.find((f) => f.id === data.selectedTranscriptId)?.name ??
    data.transcriptFiles[0]?.name ??
    '(none)';
  $: selectedDocumentName = data.selectedDocumentName || '(none)';

  function navigateWithParam(key: 'transcript' | 'doc', value: string): void {
    const u = new URL(window.location.href);
    if (value) u.searchParams.set(key, value);
    else u.searchParams.delete(key);
    window.location.href = `${u.pathname}?${u.searchParams.toString()}`;
  }

  function onCueSelect(ev: CustomEvent<{ cue: TranscriptCue; index: number; timeSec: number }>): void {
    const cue = ev.detail?.cue;
    if (!cue) return;
    selectionState = {
      kind: 'cue',
      label: `[${cue.startLabel} -> ${cue.endLabel}]`,
      detail: cue.text
    };
  }

  function onDocLineSelect(ev: CustomEvent<DocumentLineSelectEvent>): void {
    const row = ev.detail;
    selectionState = {
      kind: 'line',
      label: `line ${row.lineNumber}`,
      detail: row.text
    };
  }
</script>

<DashboardShell title="Viewer Workbench">
  <Section
    title="HCA Transcript + Document Viewer"
    subtitle="Reusable viewer primitives for SB/SL: transcript cues, folder browser, and line-addressable document text."
  >
    <div slot="actions" class="flex items-center gap-2">
      <a
        class="rounded-lg bg-paper-100 ring-1 ring-ink-900/10 px-3 py-2 text-xs uppercase tracking-widest"
        href="/"
      >
        Dashboard
      </a>
      <a
        class="rounded-lg bg-paper-100 ring-1 ring-ink-900/10 px-3 py-2 text-xs uppercase tracking-widest"
        href="/graphs/wiki-timeline-aoo-all?source=hca"
      >
        HCA Graph
      </a>
    </div>

    <div class="grid gap-4 lg:grid-cols-[1.2fr_1fr]">
      <TranscriptViewer
        title={`Transcript (${selectedTranscriptName})`}
        cues={cueRows}
        transcriptText={data.transcriptMarkdown}
        audioSrc={data.audioSrc}
        maxHeightPx={560}
        on:cueSelect={onCueSelect}
      />
      <DocumentViewer
        title={`Document (${selectedDocumentName})`}
        text={data.selectedDocumentText}
        mode="plain"
        maxHeightPx={560}
        on:lineSelect={onDocLineSelect}
      />
    </div>
  </Section>

  <Section title="Artifact Folders" subtitle={`Root: ${data.baseRel}`}>
    <div class="grid gap-4 lg:grid-cols-2">
      <FolderListViewer
        title="Transcript Artifacts"
        entries={data.transcriptFiles}
        selectedId={data.selectedTranscriptId}
        on:select={(ev) => navigateWithParam('transcript', ev.detail.id)}
      />
      <FolderListViewer
        title="Ingested Documents"
        entries={data.documentFiles}
        selectedId={data.selectedDocumentId}
        on:select={(ev) => navigateWithParam('doc', ev.detail.id)}
      />
    </div>
  </Section>

  <Panel>
    <div class="text-xs uppercase tracking-[0.28em] text-ink-800/70">Selection Bridge</div>
    {#if selectionState}
      <div class="mt-2 text-sm text-ink-950">
        <span class="rounded bg-amber-100 px-1.5 py-0.5 font-mono">{selectionState.kind}</span>
        <span class="ml-2 font-mono text-xs text-ink-800/70">{selectionState.label}</span>
      </div>
      <div class="mt-2 whitespace-pre-wrap break-words text-sm text-ink-950">{selectionState.detail}</div>
    {:else}
      <div class="mt-2 text-xs text-ink-800/70">
        Click a transcript cue or document line. This panel is the hook point for future graph/input synchronization.
      </div>
    {/if}
  </Panel>

  <Section title="Raw Transcript Source" subtitle="Same content, rendered as markdown/text for cross-checking parser output.">
    <DocumentViewer
      title={selectedTranscriptName}
      text={data.transcriptMarkdown}
      mode="markdown"
      showLineNumbers={false}
      maxHeightPx={360}
    />
  </Section>
</DashboardShell>
