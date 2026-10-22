/* Exporte les PNG du kit logo à partir des SVG de brand/out (fond transparent, sauf fonds explicites). */
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const d = path.join(__dirname, 'out'); const f = n => fs.readFileSync(path.join(d, n), 'utf8');
const dims = JSON.parse(fs.readFileSync(path.join(__dirname, 'mark.json'), 'utf8')).dims;
const jobs = [
  ['marque-color', 'marque-couleur-1024.png', 1024, 1024], ['marque-color', 'marque-couleur-512.png', 512, 512], ['marque-color', 'marque-couleur-256.png', 256, 256],
  ['marque-white', 'marque-blanche-1024.png', 1024, 1024], ['marque-black', 'marque-noire-1024.png', 1024, 1024],
  ['logo-horizontal-color', 'logo-horizontal-couleur-2400.png', 2400, Math.round(2400 * dims.horizontal[1] / dims.horizontal[0])],
  ['logo-horizontal-color', 'logo-horizontal-couleur-1200.png', 1200, Math.round(1200 * dims.horizontal[1] / dims.horizontal[0])],
  ['logo-horizontal-white', 'logo-horizontal-blanc-2400.png', 2400, Math.round(2400 * dims.horizontal[1] / dims.horizontal[0])],
  ['logo-horizontal-black', 'logo-horizontal-noir-2400.png', 2400, Math.round(2400 * dims.horizontal[1] / dims.horizontal[0])],
  ['logo-empile-color', 'logo-empile-couleur-1200.png', 1200, Math.round(1200 * dims.empile[1] / dims.empile[0])],
  ['logo-empile-white', 'logo-empile-blanc-1200.png', 1200, Math.round(1200 * dims.empile[1] / dims.empile[0])],
  ['icone-app', 'icone-app-1024.png', 1024, 1024], ['icone-app', 'icone-app-512.png', 512, 512], ['icone-app', 'icone-app-192.png', 192, 192], ['icone-app', 'icone-app-180.png', 180, 180],
  ['favicon', 'favicon-32.png', 32, 32], ['favicon', 'favicon-16.png', 16, 16],
];
(async () => {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--no-sandbox'] });
  const page = await browser.newPage();
  for (const [svg, out, w, h] of jobs) {
    await page.setViewportSize({ width: w, height: h });
    await page.setContent(`<html><body style="margin:0;background:transparent">${f(svg + '.svg').replace('<svg ', `<svg width="${w}" height="${h}" `)}</body></html>`);
    await page.screenshot({ path: path.join(d, out), omitBackground: true });
  }
  // avatar réseaux (carré vert, logo empilé blanc) et bannière (vert, logo horizontal blanc + signature)
  await page.setViewportSize({ width: 1024, height: 1024 });
  await page.setContent(`<html><body style="margin:0;width:1024px;height:1024px;background:#1F6B4A;display:grid;place-items:center"><div style="width:720px">${f('logo-empile-white.svg')}</div></body></html>`);
  await page.screenshot({ path: path.join(d, 'avatar-reseaux-1024.png') });
  await page.setViewportSize({ width: 1024, height: 1024 });
  await page.setContent(`<html><body style="margin:0;width:1024px;height:1024px;background:#F5F7F2;display:grid;place-items:center"><div style="width:720px">${f('logo-empile-color.svg')}</div></body></html>`);
  await page.screenshot({ path: path.join(d, 'avatar-reseaux-creme-1024.png') });
  await page.setViewportSize({ width: 1640, height: 624 });
  await page.setContent(`<html><head><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Nunito+Sans:wght@600&display=swap"></head><body style="margin:0;width:1640px;height:624px;background:#1F6B4A;display:grid;place-items:center;position:relative;overflow:hidden"><div style="position:absolute;width:700px;height:700px;border-radius:50%;background:rgba(255,255,255,.06);right:-220px;top:-300px"></div><div style="display:grid;gap:26px;justify-items:center"><div style="width:900px">${f('logo-horizontal-white.svg')}</div><div style="font-family:'Nunito Sans',Arial,sans-serif;font-size:34px;font-weight:600;color:#F2A93B;letter-spacing:.01em">Des racines solides dès le premier jour.</div></div></body></html>`);
  await page.waitForTimeout(500);
  await page.screenshot({ path: path.join(d, 'banniere-1640x624.png') });
  await browser.close();
  console.log('PNG exportés :', fs.readdirSync(d).filter(n => n.endsWith('.png')).length);
})();
