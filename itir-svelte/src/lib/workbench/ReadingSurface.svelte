<script>
  import { createEventDispatcher } from 'svelte';
  import { cardKinds, compileReadingIntent, guideCues } from './readingSurface.js';

  export let specimen;

  const dispatch = createEventDispatcher();
  let selectedIndex = 2;
  let openCard = null;

  $: selected = specimen.stages[selectedIndex];

  function chooseStage(index) {
    selectedIndex = index;
    openCard = null;
  }

  function toggleCard(kind) {
    openCard = openCard === kind ? null : kind;
  }

  function explore(kind, intent) {
    toggleCard(kind);
    if (openCard === kind && intent) {
      dispatch('intent', compileReadingIntent(selected, intent));
    }
  }
</script>

<svelte:head>
  <title>{specimen.title}</title>
</svelte:head>

<main class="reading-shell" aria-labelledby="reading-title">
  <header class="hero">
    <p class="kicker">Reading workbench · bounded explanation</p>
    <h1 id="reading-title">{specimen.title}</h1>
    <p class="lead">{specimen.lead}</p>
    <p class="scope-note">
      This view is deliberately small. Hidden source, proof and context detail remains available on demand.
    </p>
  </header>

  <section class="chain" aria-label="Mabo explanation chain">
    <ol>
      {#each specimen.stages as stage, index}
        <li class:active={index === selectedIndex}>
          <button
            type="button"
            class="stage-button"
            aria-current={index === selectedIndex ? 'step' : undefined}
            on:click={() => chooseStage(index)}
          >
            <span class="eyebrow">{stage.eyebrow}</span>
            <span class="stage-heading">{stage.heading}</span>
          </button>
        </li>
      {/each}
    </ol>
  </section>

  <article class="focus" aria-live="polite">
    <header>
      <p class="eyebrow">{selected.eyebrow}</p>
      <h2>{selected.heading}</h2>
    </header>
    <p class="summary">{selected.summary}</p>

    <nav class="actions" aria-label="Explore this step">
      <button type="button" class:pressed={openCard === 'proof'} on:click={() => explore('proof', 'why')}>
        Why?
      </button>
      <button type="button" class:pressed={openCard === 'source'} on:click={() => explore('source', 'source')}>
        Source
      </button>
      <button type="button" class:pressed={openCard === 'identity'} on:click={() => explore('identity', 'context')}>
        Context
      </button>
      <button type="button" class:pressed={openCard === 'guide'} on:click={() => toggleCard('guide')}>
        Reading guide
      </button>
      <button type="button" class:pressed={openCard === 'graph'} on:click={() => explore('graph', 'graph')}>
        Show structure
      </button>
    </nav>

    {#if openCard === 'proof'}
      <aside class="drawer" aria-label="Proof role">
        <p class="drawer-label">Proof</p>
        <h3>What is this step doing here?</h3>
        <p>
          This step is linked to the canonical proof object. Support, qualifiers, defeaters and residuals stay folded until the proof read model supplies them.
        </p>
        <details>
          <summary>Technical reference</summary>
          <code>{selected.proofRef}</code>
        </details>
      </aside>
    {:else if openCard === 'source'}
      <aside class="drawer" aria-label="Source inspection">
        <p class="drawer-label">Source</p>
        <h3>{selected.exactAuthorityReady ? 'Exact-source coordinates are available' : 'Source needs richer coordinates'}</h3>
        <p>
          Source identity is kept separate from proof role. Opening a source does not make it applicable authority or pay an evidence obligation.
        </p>
        <details>
          <summary>Show source references</summary>
          <dl class="refs">
            <div><dt>Source</dt><dd><code>{selected.sourceRef}</code></dd></div>
            <div><dt>Span</dt><dd><code>{selected.sourceSpanRef}</code></dd></div>
            <div><dt>Revision</dt><dd><code>{selected.sourceRevisionRef}</code></dd></div>
          </dl>
        </details>
      </aside>
    {:else if openCard === 'identity'}
      <aside class="drawer" aria-label="Identity and context">
        <p class="drawer-label">Identity / context</p>
        <h3>{selected.contextLabel}</h3>
        <p>
          This is where Wikipedia, Wikidata and public-ontology navigation can appear progressively. Identity helps you follow the rabbit hole; it does not create legal authority or applicability.
        </p>
        <details>
          <summary>Semantic reference</summary>
          <code>{selected.semanticRef}</code>
        </details>
      </aside>
    {:else if openCard === 'guide'}
      <aside class="drawer" aria-label="Reading guide">
        <p class="drawer-label">Guide mode</p>
        <h3>Who did what, to what — and with what qualification?</h3>
        <p>
          The parser can reveal a small grammar overlay when useful. These cues are reading aids, not a score of what you understand.
        </p>
        <div class="cue-list" aria-label="PNF reading cues">
          {#each guideCues as cue}
            <span>{cue}</span>
          {/each}
        </div>
      </aside>
    {:else if openCard === 'graph'}
      <aside class="drawer" aria-label="Structure view">
        <p class="drawer-label">Structure</p>
        <h3>The graph is a power view, not the landing page.</h3>
        <p>
          The first specimen keeps the bounded chain visible and leaves the wider proof graph unloaded until a canonical graph read model is connected.
        </p>
      </aside>
    {/if}
  </article>

  <footer class="boundary">
    <strong>What this page is not claiming:</strong>
    navigation, source discovery and parser cues do not themselves establish authority, applicability, evidence payment, belief or understanding.
    <span class="sr-only">Card kinds: {cardKinds.join(', ')}</span>
  </footer>
</main>

<style>
  :global(body) {
    margin: 0;
    background: #f6f3ec;
    color: #26241f;
    font-family: ui-serif, Georgia, Cambria, "Times New Roman", serif;
  }

  .reading-shell {
    width: min(980px, calc(100% - 2rem));
    margin: 0 auto;
    padding: 4rem 0 6rem;
  }

  .hero {
    max-width: 760px;
    margin-bottom: 2.5rem;
  }

  .kicker,
  .eyebrow,
  .drawer-label {
    margin: 0 0 0.5rem;
    font-family: ui-sans-serif, system-ui, sans-serif;
    font-size: 0.76rem;
    font-weight: 700;
    letter-spacing: 0.09em;
    text-transform: uppercase;
  }

  h1 {
    margin: 0;
    max-width: 14ch;
    font-size: clamp(2.5rem, 7vw, 5.6rem);
    line-height: 0.95;
    letter-spacing: -0.04em;
  }

  .lead {
    max-width: 68ch;
    margin: 1.5rem 0 0;
    font-size: 1.2rem;
    line-height: 1.65;
  }

  .scope-note {
    max-width: 66ch;
    margin-top: 1rem;
    color: #666056;
    font-family: ui-sans-serif, system-ui, sans-serif;
    font-size: 0.9rem;
  }

  .chain ol {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 0;
    padding: 0;
    margin: 0 0 2.5rem;
    list-style: none;
    border-top: 1px solid #b9b1a3;
    border-bottom: 1px solid #b9b1a3;
  }

  .chain li + li {
    border-left: 1px solid #d9d2c6;
  }

  .chain li.active {
    background: #ece6d9;
  }

  .stage-button {
    width: 100%;
    min-height: 9rem;
    padding: 1rem;
    border: 0;
    background: transparent;
    color: inherit;
    text-align: left;
    cursor: pointer;
  }

  .stage-button:focus-visible,
  .actions button:focus-visible {
    outline: 3px solid #3c5d75;
    outline-offset: 3px;
  }

  .stage-heading {
    display: block;
    font-size: 1rem;
    line-height: 1.35;
  }

  .focus {
    max-width: 760px;
    min-height: 26rem;
  }

  .focus h2 {
    margin: 0;
    font-size: clamp(1.8rem, 4vw, 3.1rem);
    line-height: 1.05;
    letter-spacing: -0.025em;
  }

  .summary {
    font-size: 1.16rem;
    line-height: 1.7;
  }

  .actions {
    display: flex;
    flex-wrap: wrap;
    gap: 0.55rem;
    margin: 1.7rem 0;
  }

  .actions button {
    border: 1px solid #9d9588;
    border-radius: 999px;
    padding: 0.55rem 0.9rem;
    background: #fffdf8;
    color: #292720;
    cursor: pointer;
    font: 600 0.86rem ui-sans-serif, system-ui, sans-serif;
  }

  .actions button.pressed {
    background: #28261f;
    color: #fffdf8;
  }

  .drawer {
    margin-top: 1.2rem;
    padding: 1.25rem 1.4rem;
    border-left: 4px solid #817663;
    background: #fffdf8;
  }

  .drawer h3 {
    margin: 0 0 0.6rem;
    font-size: 1.2rem;
  }

  .drawer p {
    line-height: 1.6;
  }

  details {
    margin-top: 1rem;
    font-family: ui-sans-serif, system-ui, sans-serif;
    font-size: 0.82rem;
  }

  summary {
    cursor: pointer;
    font-weight: 700;
  }

  code {
    overflow-wrap: anywhere;
  }

  .refs div {
    display: grid;
    grid-template-columns: 5rem 1fr;
    gap: 0.5rem;
    margin: 0.45rem 0;
  }

  .refs dt {
    font-weight: 700;
  }

  .refs dd {
    margin: 0;
  }

  .cue-list {
    display: flex;
    flex-wrap: wrap;
    gap: 0.45rem;
  }

  .cue-list span {
    border-bottom: 2px solid #b8a673;
    padding: 0.2rem 0.35rem;
    font: 600 0.82rem ui-sans-serif, system-ui, sans-serif;
  }

  .boundary {
    max-width: 760px;
    margin-top: 3rem;
    padding-top: 1rem;
    border-top: 1px solid #c9c1b4;
    color: #625d54;
    font: 0.82rem/1.55 ui-sans-serif, system-ui, sans-serif;
  }

  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
  }

  @media (max-width: 760px) {
    .reading-shell {
      padding-top: 2rem;
    }

    .chain ol {
      grid-template-columns: 1fr;
    }

    .chain li + li {
      border-left: 0;
      border-top: 1px solid #d9d2c6;
    }

    .stage-button {
      min-height: auto;
    }
  }
</style>
