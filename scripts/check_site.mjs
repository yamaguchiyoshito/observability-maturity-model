// ビルド済みサイト（docs/.vitepress/dist）を base パス付きで配信し、Playwright で主要機能を検証する。
// 検証: トップ、深いリンクとアンカー、全量マトリクス、個人評価の保存と集計、目次の標準/コンパクト切替、日本語検索、ダウンロード、モバイル表示。
import { chromium, expect } from '@playwright/test';
import { createServer } from 'node:http';
import { readFile, stat, mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';

const directory = path.resolve('docs/.vitepress/dist');
const homeHtml = await readFile(path.join(directory, 'index.html'), 'utf8');
const base = homeHtml.match(/href="([^"]*)favicon\.svg"/)[1];
const mime = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml', '.md': 'text/markdown; charset=utf-8', '.csv': 'text/csv; charset=utf-8', '.pdf': 'application/pdf', '.woff2': 'font/woff2' };
const server = createServer(async (req, res) => {
  try {
    const pathname = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
    if (!pathname.startsWith(base)) { res.writeHead(404); res.end(); return; }
    let file = path.resolve(directory, pathname.slice(base.length) || 'index.html');
    if (!file.startsWith(directory + path.sep)) { res.writeHead(404); res.end(); return; }
    if (pathname.endsWith('/')) file = path.join(file === path.join(directory, 'index.html') ? directory : file, 'index.html');
    const info = await stat(file);
    if (!info.isFile()) throw Error('Not a file');
    res.writeHead(200, { 'Content-Type': mime[path.extname(file)] || 'application/octet-stream' }); res.end(await readFile(file));
  } catch { res.writeHead(404); res.end('Not found'); }
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
const origin = `http://127.0.0.1:${server.address().port}`;
const url = origin + base;
const results = { base, axes: 6, levels: 5, checks: [] };
let browser;
try {
  browser = await chromium.launch({ headless: true, ...(process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH ? { executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH, args: JSON.parse(process.env.PLAYWRIGHT_CHROMIUM_ARGS || '["--no-sandbox","--disable-dev-shm-usage"]') } : {}) });
  results.browser = browser.version();
  const page = await browser.newPage({ viewport: { width: 1440, height: 1050 } });
  const errors = []; const networkErrors = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('response', response => { if (response.url().startsWith(origin) && response.status() >= 400) networkErrors.push(response.url()); });

  await page.goto(url);
  await expect(page.locator('h1')).toHaveText('オブザーバビリティ成熟度モデル');
  await expect(page.getByRole('link', { name: '全量マトリクス', exact: true }).first()).toBeVisible();
  await mkdir('artifacts', { recursive: true });
  await page.screenshot({ path: 'artifacts/home-desktop.png', fullPage: true });
  results.checks.push('desktop home and navigation');

  for (const [route, heading, anchor] of [
    ['model/alert-optimization-and-incident-response.html#level-2', 'A4. アラート最適化と障害対応', 'level-2'],
    ['model/data-collection-and-visualization.html#transition-3-4', 'A1. データ収集と可視化', 'transition-3-4'],
    ['levels/level-3.html', 'レベル3: 組織標準化', null]
  ]) {
    await page.goto(url + route); await page.reload();
    await expect(page.locator('h1')).toHaveText(heading);
    if (anchor) await expect(page.locator(`[id="${anchor}"]`)).toHaveCount(1);
  }
  results.checks.push('deep links, anchor navigation and refresh');

  await page.goto(url + 'model/data-collection-and-visualization.html');
  for (const [kind, count] of [['desc', 5], ['example', 5], ['required', 4], ['recommended', 4], ['note', 4]]) {
    await expect(page.locator(`.omm-block.omm-${kind}`)).toHaveCount(count); // 5 レベル分の説明・具体例と 4 遷移分の改善・活用・注意点
  }
  await page.screenshot({ path: 'artifacts/axis-page.png', fullPage: true });
  results.checks.push('axis page: description, example, required, recommended and note blocks');

  await page.goto(url + 'matrix.html');
  await expect(page.locator('h1')).toHaveText('全量マトリクス');
  await expect(page.locator('.omm-matrix-levels tbody tr')).toHaveCount(6);
  await expect(page.locator('.omm-matrix-levels tbody tr').first().locator('td')).toHaveCount(5);
  await expect(page.locator('.omm-matrix-actions tbody tr')).toHaveCount(6);
  await expect(page.locator('.omm-matrix-actions tbody tr').first().locator('td')).toHaveCount(4);
  await page.getByRole('button', { name: '具体例をすべて開く' }).click();
  await expect(page.locator('.omm-matrix-levels details[open]')).toHaveCount(30);
  results.checks.push('full matrix: 6 axes by 5 levels and 4 transitions, expand all');

  await page.goto(url + 'self-assessment.html');
  await expect(page.locator('h1')).toHaveText('個人評価');
  const a1l2 = page.locator('tr[data-axis="A1"] td.omm-sa-cell[data-level="2"]');
  await expect(a1l2).toHaveAttribute('aria-checked', 'false');
  await a1l2.click();
  await expect(a1l2).toHaveAttribute('aria-checked', 'true');
  await page.locator('tr[data-axis="A5"] td.omm-sa-cell[data-level="0"]').click();
  await expect(page.locator('.omm-sa-stats .stat-primary strong')).toContainText('1');
  await page.locator('#omm-sa-target').fill('サンプルチーム'); await page.locator('#omm-sa-target').blur();
  await page.reload();
  await expect(page.locator('tr[data-axis="A1"] td.omm-sa-cell[data-level="2"]')).toHaveAttribute('aria-checked', 'true'); // localStorage に保持
  await expect(page.locator('#omm-sa-target')).toHaveValue('サンプルチーム');
  await expect(page.locator('.omm-sa-summary a[href*="transition-2-3"]')).toHaveCount(1);
  await expect(page.locator('.omm-sa-markdown pre')).toContainText('| A1. データ収集と可視化 | レベル2 | プロセス確立 |');
  await a1l2.click(); // 同じセルの再クリックで解除
  await expect(a1l2).toHaveAttribute('aria-checked', 'false');
  results.checks.push('self-assessment persists across reloads, summary and markdown');

  const sidebar = page.locator('.VPSidebar');
  const fullWidth = (await sidebar.boundingBox()).width;
  await page.getByRole('button', { name: '目次をコンパクト表示' }).click();
  await expect(page.locator('html')).toHaveAttribute('data-sidebar', 'compact');
  await page.reload();
  await expect(page.locator('html')).toHaveAttribute('data-sidebar', 'compact'); // 描画前に適用
  const compactWidth = (await sidebar.boundingBox()).width;
  if (!(compactWidth < fullWidth - 150)) throw Error(`Compact sidebar not narrower: ${compactWidth} vs ${fullWidth}`);
  await page.screenshot({ path: 'artifacts/self-assessment-compact.png' });
  await page.getByRole('button', { name: '目次を表示' }).click();
  await expect(page.locator('html')).toHaveAttribute('data-sidebar', 'full');
  results.checks.push('sidebar full / compact toggle persists');

  for (const [query, target] of [['ポストモーテム', 'system-reliability-management'], ['動的しきい値', 'alert-optimization'], ['SLO', 'data-collection'], ['CMMI', 'model']]) {
    await page.locator('button.DocSearch-Button').click();
    const input = page.locator('#localsearch-input');
    await expect(input).toBeVisible(); await input.fill(query);
    const result = page.locator(`.VPLocalSearchBox a[href*="${target}"]`).first();
    try { await expect(result).toBeVisible({ timeout: 15000 }); } catch (e) { console.error('Search diagnostics', query, await page.locator('.VPLocalSearchBox').innerText(), errors, networkErrors); await page.screenshot({ path: 'artifacts/search-failure.png' }); throw e; }
    await result.click();
    await expect(input).toBeHidden();
    results.checks.push(`search ${query}`);
  }
  await page.locator('button.DocSearch-Button').click();
  await page.locator('#localsearch-input').fill('存在しない検索語zzzzzzzz');
  await expect(page.getByText('結果が見つかりません')).toBeVisible();
  await page.keyboard.press('Escape');
  results.checks.push('empty search and keyboard close');

  await page.goto(url + 'downloads.html');
  await expect(page.locator('.downloads-list a')).toHaveCount(5);
  for (const anchor of await page.locator('.downloads-list a').all()) {
    const [download] = await Promise.all([page.waitForEvent('download'), anchor.click()]);
    if (await download.failure()) throw Error('Download failed');
  }
  results.checks.push('five browser downloads');

  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(url + 'model/system-reliability-management.html');
  await expect(page.locator('h1')).toHaveText('A2. システムの信頼性管理');
  await page.getByRole('button', { name: '目次', exact: true }).click();
  await expect(page.locator('.VPSidebar')).toBeVisible();
  await page.locator('.VPBackdrop').click({ position: { x: 370, y: 300 } });
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
  if (overflow) throw Error('Horizontal page overflow on mobile');
  await page.screenshot({ path: 'artifacts/axis-mobile.png', fullPage: true });
  results.checks.push('mobile sidebar and no page overflow');

  if (errors.length || networkErrors.length) throw Error(JSON.stringify({ errors, networkErrors }));
  results.checks.push('no browser exceptions or failed local requests');
  await writeFile('artifacts/site-check-results.json', JSON.stringify(results, null, 2) + '\n');
  console.log(`Browser OK: ${results.checks.length} checks; base=${base}`);
} finally {
  if (browser) await browser.close();
  await new Promise(resolve => server.close(resolve));
}
