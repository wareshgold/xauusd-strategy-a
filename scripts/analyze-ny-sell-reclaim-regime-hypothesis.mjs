import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const SOURCE = resolve(ROOT, 'data/reports/strategy-a-ny-sell-preentry-discriminative-anatomy/5m.json');
const OUT = resolve(ROOT, 'data/reports/strategy-a-ny-sell-reclaim-regime-hypothesis');
const FEATURES = ['triggerReclaimToRange', 'triggerReclaimToCorrection'];
const FIXED_BOUNDARY = 0.5;
const p = (n) => Number.isFinite(n) ? Number(n.toFixed(6)) : null;
const classify = (r) => !Number.isFinite(r) ? null : r < 0 ? 'LOSS' : r >= 5 ? 'EXCEPTIONAL_WIN' : 'NORMAL_WIN';
const exceptional = (x) => Number(x.r) >= 5;

function stats(rows) {
  const r = rows.map(x => Number(x.r)).filter(Number.isFinite);
  const wins = r.filter(x => x > 0), losses = r.filter(x => x < 0);
  const gw = wins.reduce((s, x) => s + x, 0), gl = -losses.reduce((s, x) => s + x, 0);
  return { n: r.length, WR: r.length ? p(wins.length / r.length) : null, avgR: r.length ? p(r.reduce((s, x) => s + x, 0) / r.length) : null, PF: gl ? p(gw / gl) : null, totalR: p(r.reduce((s, x) => s + x, 0)) };
}

function regime(x) {
  const a = Number(x.triggerReclaimToRange), b = Number(x.triggerReclaimToCorrection);
  if (!Number.isFinite(a) || !Number.isFinite(b)) return 'UNCLASSIFIED';
  const ar = a >= FIXED_BOUNDARY, br = b >= FIXED_BOUNDARY;
  if (ar && br) return 'STRONG_BOTH';
  if (ar || br) return 'MIXED';
  return 'WEAK_BOTH';
}

function describe(rows, label) {
  const scoped = rows.filter(x => regime(x) === label);
  const noEx = scoped.filter(x => !exceptional(x));
  return { label, boundary: FIXED_BOUNDARY, outcome: stats(scoped), noExceptionalOutcome: stats(noEx), exceptionalN: scoped.length - noEx.length, n: scoped.length };
}

function temporal(rows) {
  const out = [];
  for (const split of ['DEV', 'VAL']) {
    const scoped = rows.filter(x => x.split === split).sort((a, b) => new Date(a.time) - new Date(b.time));
    const mid = Math.ceil(scoped.length / 2);
    for (const [i, w] of [scoped.slice(0, mid), scoped.slice(mid)].entries()) {
      out.push({ id: `${split}_H${i + 1}`, n: w.length, regimes: ['WEAK_BOTH', 'MIXED', 'STRONG_BOTH'].map(r => describe(w, r)) });
    }
  }
  return out;
}

async function main() {
  const source = JSON.parse(await readFile(SOURCE, 'utf8'));
  const rows = (source.cases ?? []).map(x => ({ ...x, ...x.geometry, classification: classify(Number(x.r)) })).filter(x => x.split === 'DEV' || x.split === 'VAL');
  if (!rows.length) throw new Error('No DEV/VAL cases found');

  const result = {
    strategy: 'Strategy A / SP2L',
    mode: 'RESEARCH_NY_SELL_RECLAIM_REGIME_HYPOTHESIS',
    timeframe: '5m',
    scope: { n: rows.length, dev: rows.filter(x => x.split === 'DEV').length, val: rows.filter(x => x.split === 'VAL').length, exceptional: rows.filter(exceptional).length, freshHoldoutExcluded: true, productionUntouched: true },
    hypothesis: {
      purpose: 'Predefined structural regime audit for reclaim strength; descriptive candidate only.',
      features: FEATURES,
      fixedBoundary: FIXED_BOUNDARY,
      boundaryMeaning: 'A reclaim ratio >= 0.5 means the trigger reclaim spans at least half of the referenced range/correction magnitude.',
      regimes: { STRONG_BOTH: 'both reclaim ratios >= 0.5', MIXED: 'exactly one reclaim ratio >= 0.5', WEAK_BOTH: 'both reclaim ratios < 0.5' },
      noOptimization: true,
      noThresholdSearch: true,
      noNewTradingRule: true,
      holdoutLocked: true,
      rationale: '0.5 is a fixed geometric half-span boundary chosen before evaluating outcomes; it is not fitted to this sample.'
    },
    overall: { all: stats(rows), noExceptional: stats(rows.filter(x => !exceptional(x))) },
    regimes: ['WEAK_BOTH', 'MIXED', 'STRONG_BOTH'].map(r => describe(rows, r)),
    temporal: temporal(rows),
    cases: rows.map(x => ({ split: x.split, time: x.time ?? x.entryTime, r: x.r, classification: x.classification, regime: regime(x), triggerReclaimToRange: Number.isFinite(Number(x.triggerReclaimToRange)) ? Number(x.triggerReclaimToRange) : null, triggerReclaimToCorrection: Number.isFinite(Number(x.triggerReclaimToCorrection)) ? Number(x.triggerReclaimToCorrection) : null }))
  };

  await mkdir(OUT, { recursive: true });
  await writeFile(resolve(OUT, '5m.json'), JSON.stringify(result, null, 2));

  console.log(`RECLAIM_REGIME_HYPOTHESIS N=${rows.length} DEV=${result.scope.dev} VAL=${result.scope.val} FRESH=LOCKED`);
  console.log(`BOUNDARY=0.5 | ALL avgR=${result.overall.all.avgR} PF=${result.overall.all.PF} | NO_EXCEPTIONAL avgR=${result.overall.noExceptional.avgR} PF=${result.overall.noExceptional.PF}`);
  for (const z of result.regimes) console.log(`${z.label}: N=${z.n} WR=${z.outcome.WR} avgR=${z.outcome.avgR} PF=${z.outcome.PF} exceptional=${z.exceptionalN} | noExceptionalAvgR=${z.noExceptionalOutcome.avgR} PF=${z.noExceptionalOutcome.PF}`);
  for (const w of result.temporal) console.log(`${w.id}: ${w.regimes.map(z => `${z.label}=${z.n}/${z.outcome.WR ?? '-'}/${z.outcome.avgR ?? '-'}/${z.outcome.PF ?? '-'}`).join(' | ')}`);
  console.log(`REPORT=${resolve(OUT, '5m.json')}`);
  console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_RULE NO_FRESH');
}

await main();
