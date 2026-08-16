/**
 * tools/demo/verify.mjs — **every figure a caption quotes, checked against the live API.**
 *
 * Run before the encode. A walkthrough is the one artifact in a project like this that nobody
 * re-derives: it is watched once, believed, and never checked again. So the numbers in it are
 * checked here, mechanically, against the same `/v1` endpoints the screens read — and a mismatch
 * fails the build rather than shipping a video that quotes a figure the product no longer produces.
 *
 * This is the same rule the repository applies to its own measurement documents. A number in a
 * caption is a published number.
 */

const BASE = process.env.CDFC_DEMO_BASE ?? 'http://127.0.0.1:8765';
const RUN = process.env.CDFC_DEMO_RUN ?? 'f5eb385a8888c55b';

const get = async (p) => {
  const r = await fetch(BASE + p);
  if (!r.ok) throw new Error(`${p} -> ${r.status}`);
  return r.json();
};

/* Each claim names the caption it appears in, so a failure points at the line to edit rather
   than at a number in the abstract. */
const failures = [];
const claim = (caption, label, actual, expected) => {
  if (String(actual) !== String(expected)) {
    failures.push(`  ${label}: caption says ${expected}, API says ${actual}\n     in: "${caption}"`);
  }
};

const run = await get(`/v1/runs/${RUN}`);
const f = run.settledFraction;
const ex = run.surfaceExclusions;
const unchecked = await get(`/v1/runs/${RUN}/unchecked`);
const rej = await get('/v1/rejections?limit=1');
const preds = await get('/v1/predicates');
const funnel = await get('/v1/funnel');
const history = await get('/v1/settled-fraction/history');
const churn = await get('/v1/churn');

claim('Two numbers, the same size', 'settled', f.settled, 1898);
claim('Two numbers, the same size', 'inScope', f.inScope, 3747);
claim('Two numbers, the same size', 'notChecked', f.notChecked, 1849);

claim('Is 3,747 the whole form?', 'recorded', ex?.recorded, 6757);
claim('505 the template computes', 'formula excluded', ex?.formula, 505);
claim('2,505 a filer cannot write', 'locked excluded', ex?.locked, 2505);
claim('3,747 left', 'field surface', ex?.field_surface, 3747);

const byCode = Object.fromEntries((unchecked.groups ?? []).map((g) => [g.reasonCode, g.count]));
claim('422 have a check the kill gate refused',
  'failed_qualification', byCode['no_predicate.failed_qualification'], 422);
claim('1,427 have no candidate at all',
  'not_yet_synthesised', byCode['no_predicate.not_yet_synthesised'], 1427);

claim('348 candidate checks refused', 'refusals', rej.totalUnfiltered, 348);
claim('0 are admitted through the five gates', 'admitted', preds.admittedCount, 0);
claim('29 predicates produced the settled count',
  'predicates in runs', preds.predicatesThatProducedRuns, 29);

const g2 = funnel.stages.find((s) => s.name === 'G2');
claim('Everything dies at G2', 'G2 rejected', g2?.rejected, 348);
for (const name of ['G3e', 'G4']) {
  const st = funnel.stages.find((s) => s.name === name);
  if (st?.ran !== false) failures.push(`  ${name}: caption says NOT RUN, API says ran=${st?.ran}`);
}
claim('0 of 348 predicates implement a statutory clause',
  'statute obligations', funnel.obligationCoverage.withStatuteObligation, 0);
claim('0 of 348 predicates implement a statutory clause',
  'obligation total', funnel.obligationCoverage.total, 348);

claim('1,898 to 1,862', 'first point', history[0]?.settled, 1898);
claim('1,898 to 1,862', 'last point', history[history.length - 1]?.settled, 1862);
if (!history.some((p) => p.steppedDown && (p.cause ?? '').trim())) {
  failures.push('  history: caption says the number fell with a cause; no labelled step-down found');
}

claim('Nine predicates stopped settling', 'moved', churn.movedToProvisional.length, 9);
if (churn.stillRunning.length !== churn.movedToProvisional.length) {
  failures.push('  churn: caption says detection was not lost; stillRunning != movedToProvisional');
}

if (failures.length) {
  console.error('DEMO CAPTIONS ARE STALE — the product moved and the script did not:\n');
  console.error(failures.join('\n'));
  console.error('\nEdit tools/demo/record.mjs, or re-run `make history attrition` if the run is old.');
  process.exit(1);
}
console.log(`demo-verify: OK — 20 figures across 7 endpoints match the captions`);
