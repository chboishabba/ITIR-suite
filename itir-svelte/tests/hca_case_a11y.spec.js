import { test, expect } from '@playwright/test';
import { createRequire } from 'node:module';
import { readFileSync } from 'node:fs';

const require = createRequire(import.meta.url);
const axeSource = readFileSync(require.resolve('axe-core/axe.min.js'), 'utf8');

async function gotoHcaCase(page) {
  await page.goto('/viewers/hca-case');
  await expect(page.getByText('HCA Transcript + Document Viewer')).toBeVisible();
}

async function contrastRatio(locator) {
  return await locator.evaluate((element) => {
    function parseColor(value) {
      const match = String(value).match(/rgba?\(([\d.\s,]+)\)/);
      if (!match) return null;
      const parts = match[1].split(',').map((part) => Number.parseFloat(part.trim()));
      return {
        r: parts[0] ?? 0,
        g: parts[1] ?? 0,
        b: parts[2] ?? 0,
        a: parts[3] ?? 1
      };
    }

    function relativeChannel(channel) {
      const normalized = channel / 255;
      return normalized <= 0.03928 ? normalized / 12.92 : ((normalized + 0.055) / 1.055) ** 2.4;
    }

    function luminance(rgb) {
      return 0.2126 * relativeChannel(rgb.r) + 0.7152 * relativeChannel(rgb.g) + 0.0722 * relativeChannel(rgb.b);
    }

    function blend(foreground, background) {
      const alpha = foreground.a ?? 1;
      return {
        r: foreground.r * alpha + background.r * (1 - alpha),
        g: foreground.g * alpha + background.g * (1 - alpha),
        b: foreground.b * alpha + background.b * (1 - alpha),
        a: 1
      };
    }

    function effectiveBackground(node) {
      let current = node;
      let background = { r: 255, g: 255, b: 255, a: 1 };
      while (current) {
        const parsed = parseColor(getComputedStyle(current).backgroundColor);
        if (parsed && parsed.a > 0) background = blend(parsed, background);
        current = current.parentElement;
      }
      return background;
    }

    const style = getComputedStyle(element);
    const foreground = parseColor(style.color);
    const background = effectiveBackground(element);
    if (!foreground) return 0;
    const light = Math.max(luminance(foreground), luminance(background));
    const dark = Math.min(luminance(foreground), luminance(background));
    return (light + 0.05) / (dark + 0.05);
  });
}

test('HCA viewer route exposes accessible viewer controls after render', async ({ page }) => {
  await gotoHcaCase(page);

  await expect(page.getByRole('region', { name: /Transcript \(/ })).toBeVisible();
  await expect(page.getByRole('region', { name: /Document \(/ })).toBeVisible();
  await expect(page.getByRole('region', { name: 'Transcript Artifacts' })).toBeVisible();
  await expect(page.getByRole('region', { name: 'Ingested Documents' })).toBeVisible();

  await expect(page.getByRole('textbox', { name: 'Search transcript cues' })).toBeVisible();
  const scrubSlider = page.getByRole('slider', { name: 'Manual transcript scrub (seconds)' });
  const audioControl = page.locator('audio[controls]');
  await expect.poll(async () => (await scrubSlider.count()) + (await audioControl.count())).toBeGreaterThan(0);
  const documentSearchInputs = page.getByRole('textbox', { name: 'Search document text' });
  await expect(documentSearchInputs.first()).toBeVisible();
  await expect(documentSearchInputs).toHaveCount(2);
  await expect(page.getByRole('textbox', { name: 'Filter files and folders' }).first()).toBeVisible();
  await expect(page.getByRole('textbox', { name: 'Filter files and folders' }).nth(1)).toBeVisible();
  await expect(page.getByRole('button', { name: /^Select cue / }).first()).toBeVisible();
  await expect(page.getByRole('button', { name: /^Select line / }).first()).toBeVisible();
});

test('HCA viewer route supports keyboard selection across transcript, document, and folder surfaces', async ({ page }) => {
  await gotoHcaCase(page);

  const cueButton = page.getByRole('button', { name: /^Select cue / }).first();
  await cueButton.focus();
  await expect(cueButton).toBeFocused();
  await page.keyboard.press('Space');
  await expect(cueButton).toHaveAttribute('aria-pressed', 'true');
  await expect(cueButton).toBeFocused();

  const lineButton = page.getByRole('button', { name: /^Select line / }).first();
  await lineButton.focus();
  await expect(lineButton).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(lineButton).toHaveAttribute('aria-pressed', 'true');
  await expect(lineButton).toBeFocused();

  const folderButton = page.locator('button[aria-label^="file "]:not([aria-current]), button[aria-label^="dir "]:not([aria-current])').first();
  await expect(folderButton).toBeVisible();
  await folderButton.focus();
  await expect(folderButton).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page).toHaveURL(/(\?|&)(transcript|doc)=/);
});

test('HCA viewer route has no serious or critical axe violations', async ({ page }) => {
  test.setTimeout(90_000);
  await gotoHcaCase(page);

  await page.addScriptTag({ content: axeSource });
  const regionResults = await page.evaluate(async () => {
    const selectors = [
      '[role="region"][aria-label^="Transcript ("]',
      '[role="region"][aria-label^="Document ("]',
      '[role="region"][aria-label="Transcript Artifacts"]',
      '[role="region"][aria-label="Ingested Documents"]'
    ];
    const scans = [];
    for (const selector of selectors) {
      const element = document.querySelector(selector);
      if (!element) continue;
      const result = await window.axe.run(element, {
        rules: {
          'color-contrast': { enabled: false }
        },
        runOnly: {
          type: 'tag',
          values: ['wcag2a', 'wcag2aa']
        }
      });
      scans.push({
        selector,
        violations: result.violations
      });
    }
    return scans;
  });

  const blockingViolations = regionResults.flatMap((scan) =>
    scan.violations
      .filter((entry) => entry.impact === 'serious' || entry.impact === 'critical')
      .map((entry) => ({ selector: scan.selector, ...entry }))
  );
  expect(blockingViolations, JSON.stringify(blockingViolations, null, 2)).toEqual([]);
});

test('HCA viewer route key interactive controls meet a contrast floor', async ({ page }) => {
  await gotoHcaCase(page);

  const cueButton = page.getByRole('button', { name: /^Select cue / }).first();
  await cueButton.focus();
  await page.keyboard.press('Space');

  const lineButton = page.getByRole('button', { name: /^Select line / }).first();
  await lineButton.focus();
  await page.keyboard.press('Enter');

  const selectedFolderButton = page.locator('button[aria-current="true"]').first();

  const transcriptContrast = await contrastRatio(cueButton);
  const documentContrast = await contrastRatio(lineButton);
  const folderContrast = await contrastRatio(selectedFolderButton);

  expect(transcriptContrast).toBeGreaterThanOrEqual(4.5);
  expect(documentContrast).toBeGreaterThanOrEqual(4.5);
  expect(folderContrast).toBeGreaterThanOrEqual(4.5);
});
