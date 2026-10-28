import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

// Browser-level WCAG smoke.  Only the HCA viewer and its primary graph routes
// belong to this leaf; no shared UI or ESD surface is modified.
const routes = [
  { path: '/viewers/hca-case', marker: 'HCA Transcript + Document Viewer' },
  { path: '/graphs/wiki-timeline-aoo', marker: null },
  { path: '/graphs/wiki-timeline-aoo-all', marker: null },
  { path: '/graphs/mission-lens', marker: null }
];

test('HCA viewer and primary graph routes have no serious or critical axe violations', async ({ page }) => {
  for (const { path, marker } of routes) {
    const response = await page.goto(path, { waitUntil: 'domcontentloaded' });
    expect(response, path + ' should answer HTTP').not.toBeNull();
    expect(response.status(), path + ' should not fail').toBeLessThan(400);

    await expect(page.locator('body')).toBeVisible();
    if (marker) await expect(page.getByText(marker)).toBeVisible();

    // axe runs in the rendered browser rather than inspecting source markup.
    // Limit severity to serious/critical for a stable smoke gate.  Other
    // findings remain available in the full axe results when this fails.
    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();
    const blocking = results.violations.filter(({ impact }) =>
      impact === 'critical' || impact === 'serious'
    );
    expect(
      blocking.map(({ id, impact, nodes }) => ({
        id,
        impact,
        targets: nodes.map(({ target }) => target)
      })),
      path + ': serious/critical axe violations'
    ).toEqual([]);
  }
});
