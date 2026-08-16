/**
 * tools/demo/record.mjs — the product walkthrough, recorded.
 *
 *     make demo-video
 *
 * Drives a real Chromium through the running server, overlays subtitles and title cards, and
 * writes `reports/demo/cdfc-walkthrough.mp4` plus a matching `.srt`.
 *
 * ## Why the browser records itself rather than a screen recorder capturing a desktop
 *
 * A screen recording is a picture of one machine on one afternoon. This drives the SAME server a
 * reviewer would run, at a fixed viewport, and every figure that appears is read live off
 * `/v1` — so a number that moved since the last cut shows up as a different video, not as a
 * caption nobody re-checked. The script is in the repository for the same reason the measurement
 * tools are: a demo whose numbers cannot be re-derived is a memory.
 *
 * ## The overlay is injected through CDP, and that is deliberate
 *
 * The served screens carry `script-src 'self'` with no `unsafe-inline`, so an injected `<script>`
 * would be REFUSED by the browser — correctly. `page.evaluate` runs through the debugging
 * protocol rather than as page script, so the overlay works without the app loosening a policy
 * for a marketing asset. `style-src` permits inline styles, so the overlay's own CSS is a plain
 * `<style>` element.
 *
 * ## What it will not do
 *
 * It does not type a number, draw a chart, or assert a claim of its own. Every figure on screen is
 * whatever the page rendered. The only text this file contributes is the subtitles, and each one
 * is checked against the live API in `verify.mjs` before the encode.
 */

import { chromium } from 'playwright-core';
import { mkdirSync, writeFileSync, readdirSync, renameSync, rmSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const REPO = join(HERE, '..', '..');
const OUT = join(REPO, 'reports', 'demo');
const RAW = join(OUT, 'raw');

const BASE = process.env.CDFC_DEMO_BASE ?? 'http://127.0.0.1:8765';
const RUN = process.env.CDFC_DEMO_RUN ?? 'f5eb385a8888c55b';
const W = 1280, H = 720;

/* ============================ THE STORYBOARD ==============================================
 *
 * `hold` is milliseconds the frame rests AFTER the caption appears — reading time, not padding.
 * A caption of ~90 characters needs about 4.5s at a comfortable pace; the holds below are set
 * from the caption lengths rather than round-numbered.
 *
 * `scroll` is a target in CSS pixels, animated smoothly by the page itself, so the motion in the
 * video is the browser's own scrolling rather than a pan applied afterwards.
 */
const BEATS = [
  { kind: 'card', hold: 3400,
    title: 'cdfc',
    sub: 'coverage declaration for filed compliance',
    note: 'Every checker tells you what it found.\nThis one tells you what it never looked at.' },

  { kind: 'screen', path: '/', hold: 4200,
    cap: 'One control. No strict mode, no sheet selector, no skip-empty-rows box.' },
  { kind: 'screen', path: '/', hold: 5200, reuse: true,
    cap: 'Every setting here would change what gets checked — without changing what the report says was checked.' },

  { kind: 'screen', path: `/runs/${RUN}`, hold: 5600,
    cap: 'The declaration. Two numbers, the same size, the same weight, the same ink.' },
  { kind: 'screen', path: `/runs/${RUN}`, hold: 5200, reuse: true,
    cap: 'The moment one is bigger, the reader has been told which matters — and it would be the one nobody checked.' },
  { kind: 'screen', path: `/runs/${RUN}`, hold: 4600, reuse: true, scroll: 780,
    cap: 'The coverage band never fills. The two hatched terms carry no digit, because neither has been measured.' },
  { kind: 'screen', path: `/runs/${RUN}`, hold: 5800, reuse: true, scroll: 1130,
    cap: 'Is 3,747 the whole form? No — and a denominator that will not say what it excluded is a coverage lie.' },
  { kind: 'graphic', hold: 6400, art: 'denominator',
    cap: '505 cells the template computes. 2,505 a filer cannot write. 3,747 left, and that is the denominator.' },

  { kind: 'screen', path: `/runs/${RUN}/unchecked`, hold: 5000,
    cap: 'This page is the product. It is not an appendix and it does not live behind a tab.' },
  { kind: 'screen', path: `/runs/${RUN}/unchecked`, hold: 6000, reuse: true, scroll: 175,
    cap: '422 cells have a check that the kill gate refused. 1,427 have no candidate at all. Different gaps.' },
  { kind: 'screen', path: `/runs/${RUN}/unchecked`, hold: 5200, reuse: true, scroll: 175,
    cap: 'Each group carries its own remedy naming the gate that would move it. There is no fallback string.' },

  { kind: 'screen', path: '/rejections', hold: 5400, scroll: 300,
    cap: '348 candidate checks refused, every row carrying the number that refused it.' },
  { kind: 'screen', path: '/rejections', hold: 5000, reuse: true, scroll: 520,
    cap: 'A rejection without the number that decided it is an opinion with a gate name on it.' },

  { kind: 'screen', path: '/funnel', hold: 5200, scroll: 120,
    cap: 'Gate order. Everything survives G0, G1 and G3-proof. Everything dies at G2, the kill gate.' },
  { kind: 'screen', path: '/funnel', hold: 5600, reuse: true, scroll: 330,
    cap: 'The last two stages say NOT RUN — not "passed everyone". A gate that never ran decided nothing.' },

  { kind: 'screen', path: '/predicates', hold: 5800, scroll: 150,
    cap: '29 predicates produced the settled count. 0 are admitted through the five gates.' },
  { kind: 'screen', path: '/predicates', hold: 5000, reuse: true, scroll: 150,
    cap: 'Disjoint populations — so the screen says so, rather than leaving a reader to assume.' },

  { kind: 'screen', path: '/history', hold: 5200, scroll: 180,
    cap: 'A coverage number that can only rise is a marketing chart. This one fell.' },
  { kind: 'screen', path: '/history', hold: 5600, reuse: true, scroll: 560,
    cap: '1,898 to 1,862 after a template change, and the cause travels with the fall.' },

  { kind: 'screen', path: '/churn', hold: 5800, scroll: 60,
    cap: 'Nine predicates stopped settling. They did not stop running — detection was not lost.' },

  { kind: 'graphic', hold: 7000, art: 'detection',
    cap: 'Five seeded defects. All five detected — but only one surfaces as a finding.' },

  { kind: 'card', hold: 5000,
    title: 'What it does not claim',
    sub: 'three sentences that must not be said',
    note: 'It does not read the regulation — 0 of 348 predicates implement a statutory clause.\nIt is not an audit opinion.\nNothing here is admitted under G4.' },

  { kind: 'card', hold: 4200,
    title: 'It tells you what it did not check.',
    sub: 'in writing · with the reason',
    note: 'This states what was checked and what was not.\nIt does not state that a filing is correct.' },
];

/* ---- palette, lifted from src/cdfc/surface/design.py so the chrome matches the product ---- */
const C = {
  ink: '#111827', ink2: '#4B5563', slate: '#53617A', accent: '#ED7B46',
  accentInk: '#B45D35', bg: '#FFFFFF', rule: '#D8DADF',
};
const SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif";
const MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace";

const OVERLAY_CSS = `
#cdfc-demo-sub {
  position: fixed; left: 0; right: 0; bottom: 0; z-index: 2147483000;
  padding: 26px 56px 30px; pointer-events: none;
  background: linear-gradient(to top, rgba(17,24,39,.93) 0%, rgba(17,24,39,.80) 62%, rgba(17,24,39,0) 100%);
  opacity: 0; transition: opacity 320ms cubic-bezier(.22,.61,.36,1);
  font-family: ${SANS};
}
#cdfc-demo-sub.on { opacity: 1; }
#cdfc-demo-sub p {
  margin: 0 auto; max-width: 62ch; text-align: center;
  color: #fff; font-size: 21px; line-height: 1.42; font-weight: 500;
  text-wrap: balance; text-shadow: 0 1px 3px rgba(0,0,0,.5);
}
#cdfc-demo-fade {
  position: fixed; inset: 0; z-index: 2147483001; background: ${C.bg};
  opacity: 0; pointer-events: none; transition: opacity 300ms linear;
}
#cdfc-demo-fade.on { opacity: 1; }
/* The rail's own hover transitions would flicker under a scripted scroll. */
* { scroll-behavior: smooth; }
`;

async function installOverlay(page) {
  await page.evaluate((css) => {
    if (document.getElementById('cdfc-demo-style')) return;
    const s = document.createElement('style');
    s.id = 'cdfc-demo-style';
    s.textContent = css;
    document.head.appendChild(s);
    const sub = document.createElement('div');
    sub.id = 'cdfc-demo-sub';
    sub.innerHTML = '<p></p>';
    document.body.appendChild(sub);
    const fade = document.createElement('div');
    fade.id = 'cdfc-demo-fade';
    document.body.appendChild(fade);
  }, OVERLAY_CSS);
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function caption(page, text) {
  await page.evaluate((t) => {
    const el = document.getElementById('cdfc-demo-sub');
    el.querySelector('p').textContent = t;
    el.classList.add('on');
  }, text);
}
async function clearCaption(page) {
  await page.evaluate(() => document.getElementById('cdfc-demo-sub')?.classList.remove('on'));
}
async function fadeOut(page) {
  await page.evaluate(() => document.getElementById('cdfc-demo-fade')?.classList.add('on'));
  await sleep(340);
}
async function fadeIn(page) {
  await page.evaluate(() => document.getElementById('cdfc-demo-fade')?.classList.remove('on'));
  await sleep(340);
}

function cardHtml(b) {
  const lines = b.note.split('\n').map((l) => `<p class="n">${l}</p>`).join('');
  return `<!doctype html><meta charset="utf-8"><style>
    html,body{margin:0;height:100%;background:${C.bg};color:${C.ink};font-family:${SANS};}
    .w{height:100%;display:flex;flex-direction:column;justify-content:center;padding:0 92px;
       max-width:1100px;margin:0 auto;}
    .eyebrow{font-family:${MONO};font-size:12px;letter-spacing:.16em;text-transform:uppercase;
       color:${C.ink2};margin:0 0 18px;display:flex;align-items:center;gap:14px;}
    .eyebrow::after{content:"";flex:1;height:1px;background:${C.rule};}
    h1{font-size:58px;line-height:1.03;letter-spacing:-.03em;font-weight:500;margin:0 0 26px;
       max-width:20ch;text-wrap:balance;}
    .n{font-size:20px;line-height:1.55;color:${C.ink2};margin:0 0 8px;max-width:60ch;
       border-left:3px solid ${C.accent};padding-left:16px;}
    .anim{opacity:0;transform:translateY(10px);animation:r 620ms cubic-bezier(.16,1,.30,1) forwards;}
    @keyframes r{to{opacity:1;transform:none;}}
  </style><div class="w">
    <p class="eyebrow anim" style="animation-delay:60ms">${b.sub}</p>
    <h1 class="anim" style="animation-delay:180ms">${b.title}</h1>
    <div class="anim" style="animation-delay:340ms">${lines}</div>
  </div>`;
}

/* ============================ THE TWO GRAPHIC CARDS ========================================
 *
 * Both show something NO SCREEN SHOWS, which is the bar a graphic has to clear here: a diagram
 * that restates a table the viewer just watched is a slower version of the table.
 *
 *   `denominator` — the decomposition as one proportional bar. On the screen it is three rows of
 *                   a table; the relative SIZE of what was excluded is the thing a table cannot
 *                   say, and it is the answer to "is 3,747 the whole form?".
 *   `detection`   — the five seeded defects and how each one surfaces. This is measured in
 *                   `docs/DEMO-SCRIPT.md` and deliberately appears on no product screen, because
 *                   the product reports on ONE filing and this is a claim about five.
 *
 * The bars grow from zero on a CSS transform. That is the one animation in this file, and it is
 * animating a WIDTH, never a figure: `design.py` fixes `FIGURES_ANIMATE = False` because a count
 * that ticks up from zero renders every intermediate value, and each one understates the truth.
 */
const GRAPHIC_CSS = `
  html,body{margin:0;height:100%;background:${C.bg};color:${C.ink};font-family:${SANS};}
  .w{height:100%;display:flex;flex-direction:column;justify-content:center;padding:0 92px;
     max-width:1140px;margin:0 auto;}
  .eyebrow{font-family:${MONO};font-size:12px;letter-spacing:.16em;text-transform:uppercase;
     color:${C.ink2};margin:0 0 14px;display:flex;align-items:center;gap:14px;}
  .eyebrow::after{content:"";flex:1;height:1px;background:${C.rule};}
  h1{font-size:40px;line-height:1.08;letter-spacing:-.025em;font-weight:500;margin:0 0 34px;
     max-width:24ch;text-wrap:balance;}
  .fig{font-family:${MONO};font-variant-numeric:tabular-nums;}

  .bar{display:flex;height:64px;border:1px solid #868E9C;border-radius:6px;overflow:hidden;}
  .seg{transform:scaleX(0);transform-origin:left;animation:grow 900ms cubic-bezier(.16,1,.30,1) forwards;}
  @keyframes grow{to{transform:scaleX(1);}}
  .hatch{background-image:repeating-linear-gradient(45deg,#868E9C 0,#868E9C 3px,#fff 3px,#fff 9px);}
  .solid{background:${C.slate};}
  /* Fixed thirds, NOT flex proportional to the value. Sizing a key by its own number makes the
     smallest bucket's label the hardest to read, which inverts what the card is for. */
  .keys{display:grid;grid-template-columns:repeat(3,1fr);gap:22px;margin-top:16px;}
  .key{padding-right:8px;}
  .key .n{font-family:${MONO};font-size:26px;font-weight:500;display:block;letter-spacing:-.02em;}
  .key .l{font-size:13.5px;color:${C.ink2};display:block;max-width:24ch;line-height:1.35;}

  table{border-collapse:collapse;width:100%;}
  th,td{text-align:left;padding:11px 14px;border-bottom:1px solid ${C.rule};font-size:15px;}
  thead th{font-family:${MONO};font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:${C.ink2};}
  td.n{font-family:${MONO};font-variant-numeric:tabular-nums;text-align:right;}
  .tag{display:inline-block;font-family:${MONO};font-size:11px;letter-spacing:.08em;
     text-transform:uppercase;border-radius:999px;padding:3px 11px;border:1px solid #868E9C;color:${C.ink2};}
  .tag.hit{background:${C.accent};color:${C.ink};border-color:${C.accentInk};}
  tbody tr{opacity:0;animation:fade 480ms ease forwards;}
  @keyframes fade{to{opacity:1;}}
  .foot{margin-top:26px;font-size:16px;color:${C.ink2};max-width:70ch;line-height:1.5;
     border-left:3px solid ${C.accent};padding-left:16px;}
`;

const ART = {
  denominator: `
    <p class="eyebrow">the denominator, decomposed</p>
    <h1>Is 3,747 the whole form?</h1>
    <div class="bar">
      <div class="seg hatch" style="flex:505;animation-delay:120ms"></div>
      <div class="seg hatch" style="flex:2505;animation-delay:260ms"></div>
      <div class="seg solid" style="flex:3747;animation-delay:400ms"></div>
    </div>
    <div class="keys">
      <div class="key"><span class="n">505</span>
        <span class="l">formula cells — the template computes them</span></div>
      <div class="key"><span class="n">2,505</span>
        <span class="l">locked cells — a filer cannot write them</span></div>
      <div class="key"><span class="n">3,747</span>
        <span class="l">THE FIELD SURFACE — the denominator of every count</span></div>
    </div>
    <p class="foot">6,757 cells recorded. Three disjoint buckets, asserted in code to sum to that
      total — so an exclusion added without a tally fails the build.</p>`,

  detection: `
    <p class="eyebrow">five seeded defects, measured</p>
    <h1>All five detected. One is a finding.</h1>
    <table>
      <thead><tr><th>seeded defect</th><th>how it surfaces</th><th class="n">settled</th></tr></thead>
      <tbody>
        <tr style="animation-delay:200ms"><td class="fig">mutant__f11-formula-override</td>
          <td><span class="tag hit">1 finding</span></td><td class="n">1,898</td></tr>
        <tr style="animation-delay:340ms"><td class="fig">formula-overwritten__portfolio-O7</td>
          <td><span class="tag">coverage collapse</span></td><td class="n">1,557</td></tr>
        <tr style="animation-delay:480ms"><td class="fig">formula-overwritten__pair-O7-C182</td>
          <td><span class="tag">coverage collapse</span></td><td class="n">1,557</td></tr>
        <tr style="animation-delay:620ms"><td class="fig">values-written__50-cells</td>
          <td><span class="tag">coverage collapse</span></td><td class="n">1,579</td></tr>
        <tr style="animation-delay:760ms"><td class="fig">row-inserted__portfolio-r7</td>
          <td><span class="tag">run refuses</span></td><td class="n">—</td></tr>
      </tbody>
    </table>
    <p class="foot">Catching a problem as loss of coverage is not the same as catching it as
      "this is wrong", and we do not describe it as if it were.</p>`,
};

const graphicHtml = (art) =>
  `<!doctype html><meta charset="utf-8"><style>${GRAPHIC_CSS}</style><div class="w">${ART[art]}</div>`;

/* ---- SRT, emitted alongside. Burned-in subtitles cannot be turned off or translated; the
       sidecar is what makes the recording accessible and editable. ---- */
const srt = [];
let clock = 0;
const stamp = (ms) => {
  const h = String(Math.floor(ms / 3600000)).padStart(2, '0');
  const m = String(Math.floor(ms / 60000) % 60).padStart(2, '0');
  const s = String(Math.floor(ms / 1000) % 60).padStart(2, '0');
  const x = String(ms % 1000).padStart(3, '0');
  return `${h}:${m}:${s},${x}`;
};

async function main() {
  rmSync(RAW, { recursive: true, force: true });
  mkdirSync(RAW, { recursive: true });

  const browser = await chromium.launch({ args: ['--force-color-profile=srgb', '--font-render-hinting=none'] });
  const ctx = await browser.newContext({
    viewport: { width: W, height: H },
    deviceScaleFactor: 2,
    recordVideo: { dir: RAW, size: { width: W, height: H } },
    colorScheme: 'light',
    reducedMotion: 'no-preference',
  });
  const page = await ctx.newPage();

  let lastPath = null;
  for (const b of BEATS) {
    const start = clock;

    if (b.kind === 'card' || b.kind === 'graphic') {
      if (lastPath !== null) { await fadeOut(page); clock += 340; }
      await page.setContent(
        b.kind === 'card' ? cardHtml(b) : graphicHtml(b.art), { waitUntil: 'load' },
      );
      await installOverlay(page);
      if (lastPath !== null) { await fadeIn(page); clock += 340; }
      lastPath = null;

      if (b.kind === 'graphic') {
        // The bars and rows finish arriving before the caption does, so the eye reads the shape
        // first and the sentence second rather than competing for the same beat.
        await sleep(1100); clock += 1100;
        await caption(page, b.cap);
        await sleep(b.hold);
        srt.push({ from: clock, to: clock + b.hold, text: b.cap });
        clock += b.hold;
        await clearCaption(page);
        await sleep(200); clock += 200;
        continue;
      }

      await sleep(b.hold);
      clock += b.hold;
      srt.push({ from: start, to: clock, text: `${b.title} — ${b.note.split('\n')[0]}` });
      continue;
    }

    const fresh = !b.reuse || lastPath !== b.path;
    if (fresh) {
      if (lastPath !== null) { await fadeOut(page); clock += 340; }
      await page.goto(BASE + b.path, { waitUntil: 'networkidle' });
      await installOverlay(page);
      await page.evaluate(() => window.scrollTo(0, 0));
      if (lastPath !== null) { await fadeIn(page); clock += 340; }
      lastPath = b.path;
      await sleep(260); clock += 260;
    }

    if (typeof b.scroll === 'number') {
      await page.evaluate((y) => window.scrollTo({ top: y, behavior: 'smooth' }), b.scroll);
      await sleep(760); clock += 760;
    }

    await caption(page, b.cap);
    await sleep(b.hold);
    srt.push({ from: clock, to: clock + b.hold, text: b.cap });
    clock += b.hold;
    await clearCaption(page);
    await sleep(200); clock += 200;
  }

  await page.close();
  await ctx.close();
  await browser.close();

  const webm = readdirSync(RAW).filter((f) => f.endsWith('.webm'))[0];
  if (!webm) throw new Error('playwright produced no video file');
  renameSync(join(RAW, webm), join(OUT, 'walkthrough.webm'));

  writeFileSync(
    join(OUT, 'cdfc-walkthrough.srt'),
    srt.map((c, i) => `${i + 1}\n${stamp(c.from)} --> ${stamp(c.to)}\n${c.text}\n`).join('\n'),
    'utf-8',
  );

  console.log(`captured ${Math.round(clock / 1000)}s across ${BEATS.length} beats`);
  console.log(`  ${join(OUT, 'walkthrough.webm')}`);
  console.log(`  ${join(OUT, 'cdfc-walkthrough.srt')}`);
}

main().catch((e) => { console.error(e); process.exit(1); });
