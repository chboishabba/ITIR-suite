<script>
  import ReadingSurface from '$lib/workbench/ReadingSurface.svelte';
  import { createSourceConditionedMaboSpecimen } from '$lib/workbench/maboSourceProjection.js';

  const specimen = createSourceConditionedMaboSpecimen();
</script>

<ReadingSurface {specimen} />
