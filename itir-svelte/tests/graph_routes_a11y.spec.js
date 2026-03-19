import { test, expect } from '@playwright/test';

async function gotoPath(page, path, textHint) {
  await page.goto(path);
  if (textHint) {
    await expect(page.getByText(textHint, { exact: false }).first()).toBeVisible();
  }
}

test.describe('graph route accessibility', () => {
  test('wiki candidates exposes labeled inputs and keyboard-adjustable Top N', async ({ page }) => {
    await gotoPath(page, '/graphs/wiki-candidates', 'Wiki candidates');

    const modeSelect = page.getByLabel('Mode');
    await expect(modeSelect).toBeVisible();
    const firstNode = page.getByRole('button', { name: /Select node/ }).first();
    await expect(firstNode).toBeVisible();
    await firstNode.focus();
    await expect(firstNode).toBeFocused();
    await page.keyboard.press('Enter');
    await expect(firstNode).toBeFocused();
  });

  test('wiki fact timeline renders labeled filters and responds to keyboard', async ({ page }) => {
    await gotoPath(page, '/graphs/wiki-fact-timeline', 'Fact timeline');

    await expect(page.getByLabel('Dataset')).toBeVisible();
    await expect(page.getByLabel('Time')).toBeVisible();
    const maxFacts = page.getByRole('spinbutton', { name: 'Max facts' });
    await expect(maxFacts).toBeVisible();

    const initial = Number(await maxFacts.inputValue());
    await maxFacts.focus();
    await page.keyboard.press('ArrowDown');
    const after = Number(await maxFacts.inputValue());
    expect(after).toBeLessThan(initial);
  });

  test('wiki timeline AAO-all exposes labeled selectors and toggles', async ({ page }) => {
    await gotoPath(page, '/graphs/wiki-timeline-aoo-all', 'Wiki timeline AAO');

    await expect(page.getByLabel('Dataset source')).toBeVisible();
    await expect(page.getByLabel('Time granularity')).toBeVisible();
    await expect(page.getByLabel('Max events')).toBeVisible();
    await expect(page.getByLabel('Max subjects')).toBeVisible();
    await expect(page.getByLabel('Max objects')).toBeVisible();

    const sourceLane = page.getByRole('checkbox', { name: 'Show source lane' });
    await sourceLane.focus();
    const before = await sourceLane.isChecked();
    await page.keyboard.press('Space');
    await expect(sourceLane).toBeChecked({ checked: !before });
  });

  test('wiki revision contested keeps selects labeled and state visible', async ({ page }) => {
    await gotoPath(page, '/graphs/wiki-revision-contested', 'Selected article state');

    await expect(page.getByLabel('Contested graph pack')).toBeVisible();
    await expect(page.getByLabel('Contested graph run')).toBeVisible();
    await expect(page.getByLabel('Contested article')).toBeVisible();
    await expect(page.getByText('Selected graph node')).toBeVisible();
  });

  test('timeline ribbon date range inputs are labeled and keyboard-writable', async ({ page }) => {
    await gotoPath(page, '/graphs/timeline-ribbon', 'Timeline Ribbon Workbench');

    const start = page.getByLabel('Timeline start date');
    const end = page.getByLabel('Timeline end date');
    await expect(start).toBeVisible();
    await expect(end).toBeVisible();

    await start.fill('2020-01-01');
    await end.fill('2020-12-31');

    await expect(start).toHaveValue(/2020-01-01|2020-01-0?1/);
    await expect(end).toHaveValue(/2020-12-31|2020-12-3?1/);
  });
});
