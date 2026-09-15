<script>
  import ReadingSurface from '$lib/workbench/ReadingSurface.svelte';
  import { createMaboReadingSpecimen } from '$lib/workbench/readingSurface.js';

  const specimen = createMaboReadingSpecimen();
</script>

<ReadingSurface {specimen} />
