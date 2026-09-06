import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const SOURCE = resolve(ROOT, 'data/reports/strategy-a-ny-sell-correction-path-geometry-v3/5m.json');
const OUT = resolve(ROOT, 'data/reports/strategy-a-ny-sell-preentry-discriminative-anatomy');
const GROUPS = ['LOSS', 'NORMAL_WIN', 'EXCEPTIONAL_WIN'];
const FEATURES = [
  'correctionBars', 'correctionToSpike', 'pathEfficiency', 'bodyParticipation',
  'upperWickShare', 'lowerWickShare', 'secondHalfProgress',
  'triggerReclaimToRange', 'triggerBodyToRange', 'triggerCloseLocation',
  'triggerReclaimToCorrection',
];
const p = (n) => Number.isFinite(n) ? Number(n.toFixed(6)) : null;

function classifyOutcome(r) {
  if (!Number.isFinite(r)) return null;
  if (r < 0) return 'LOSS';
  if (r >= 5) return 'EXCEPTIONAL_WIN';
  return 'NORMAL_WIN';
}

function quantiles(values) {
  const a = values.filter(Number.isFinite).sort((x, y) => x - y);
  if (!a.length) return { n: 0 };
  const q = (f) => {
    const pos = (a.length - 1) * f;
    const lo = Math.floor(pos), hi = Math.ceil(pos);
    return p(a[lo] + (a[hi] - a[lo]) * (pos - lo));
  };
  return { n: a.length, median: q(.5), p25: q(.25), p75: q(.75), min: p(a[0]), max: p(a.at(-1)) };
}

function values(rows, feature) {
  return rows.map((x) => Number(x[feature])).filter(Number.isFinite);
}

function pair(rowsA, rowsB, feature) {
  const a = values(rowsA, feature), b = values(rowsB, feature);
  const ma = quantiles(a).median, mb = quantiles(b).median;
  return {
    aN: a.length, bN: b.length, aMedian: ma, bMedian: mb,
    medianDelta: Number.isFinite(ma) && Number.isFinite(mb) ? p(ma - mb) : null,
    absMedianDelta: Number.isFinite(ma) && Number.isFinite(mb) ? p(Math.abs(ma - mb)) : null,
  };
}

function outcomeStats(rows) {
  const r = rows.map((x) => Number(x.r)).filter(Number.isFinite);
  const wins = r.filter((x) => x > 0), losses = r.filter((x) => x < 0);
  const grossWin = wins.reduce((s, x) => s + x, 0);
  const grossLoss = -losses.reduce((s, x) => s + x, 0);
  return {
    n: r.length,
    WR: r.length ? p(wins.length / r.length) : null,
    avgR: r.length ? p(r.reduce((s, x) => s + x, 0) / r.length) : null,
    PF: grossLoss ? p(grossWin / grossLoss) : null,
    totalR: p(r.reduce((s, x) => s + x, 0)),
  };
}

function featureComparison(rows, left, right) {
  return Object.fromEntries(FEATURES.map((f) => [f, pair(rows.filter((x) => x.classification === left), rows.filter((x) => x.classification === right), f)]));
}

function splitComparison(rows, split) {
  const scoped = rows.filter((x) => x.split === split);
  const loss = scoped.filter((x) => x.classification === 'LOSS');
  const normal = scoped.filter((x) => x.classification === 'NORMAL_WIN');
  const exceptional = scoped.filter((x) => x.classification === 'EXCEPTIONAL_WIN');
  return {
    n: scoped.length,
    outcome: outcomeStats(scoped),
    classCounts: { LOSS: loss.length, NORMAL_WIN: normal.length, EXCEPTIONAL_WIN: exceptional.length },
    winVsLoss: featureComparison(scoped, 'NORMAL_WIN', 'LOSS'),
    exceptionalVsNormal: featureComparison(scoped, 'EXCEPTIONAL_WIN', 'NORMAL_WIN'),
    exceptionalVsLoss: featureComparison(scoped, 'EXCEPTIONAL_WIN', 'LOSS'),
  };
}

function directionConsistency(rows) {
  return Object.fromEntries(FEATURES.map((f) => {
    const all = pair(rows.filter((x) => x.classification === 'NORMAL_WIN'), rows.filter((x) => x.classification === 'LOSS'), f);
    const dev = pair(rows.filter((x) => x.split === 'DEV' && x.classification === 'NORMAL_WIN'), rows.filter((x) => x.split === 'DEV' && x.classification === 'LOSS'), f);
    const val = pair(rows.filter((x) => x.split === 'VAL' && x.classification === 'NORMAL_WIN'), rows.filter((x) => x.split === 'VAL' && x.classification === 'LOSS'), f);
    return [f, { ALL: all, DEV: dev, VAL: val, signStableDEVVAL: Number.isFinite(dev.medianDelta) && Number.isFinite(val.medianDelta) ? Math.sign(dev.medianDelta) === Math.sign(val.medianDelta) : false }];
  }));
}

async function main() {
  const source = JSON.parse(await readFile(SOURCE, 'utf8'));
  const rows = (source.cases ?? [])
    .map((x) => ({ ...x, ...x.geometry, classification: classifyOutcome(Number(x.r)) }))
    .filter((x) => x.split === 'DEV' || x.split === 'VAL');
  if (!rows.length) throw new Error('No DEV/VAL cases found');
  if (rows.some((x) => !GROUPS.includes(x.classification))) throw new Error('Unexpected outcome classification');

  const result = {
    strategy: 'Strategy A / SP2L',
    mode: 'RESEARCH_NY_SELL_PREENTRY_DISCRIMINATIVE_ANATOMY',
    timeframe: '5m',
    scope: { source: 'NY SELL correction path geometry v3', n: rows.length, dev: rows.filter((x) => x.split === 'DEV').length, val: rows.filter((x) => x.split === 'VAL').length, freshHoldoutExcluded: true, productionUntouched: true },
    methodology: {
      purpose: 'Pre-entry-only discriminative anatomy of canonical NY SELL cases, comparing losses with normal and exceptional wins.',
      featuresObservableAtEntryOnly: true,
      noPostEntryFeaturesUsedForDiscrimination: true,
      noOptimization: true,
      noThresholdSearch: true,
      noNewTradingRules: true,
      holdoutLocked: true,
      classification: 'LOSS=r<0; NORMAL_WIN=0<=r<5R; EXCEPTIONAL_WIN=r>=5R. Descriptive grouping only.',
      interpretation: 'A feature is interesting only if its direction is materially separated and remains directionally consistent between DEV and VAL. No feature is promoted by this report.',
    },
    groupStats: Object.fromEntries(GROUPS.map((g) => [g, outcomeStats(rows.filter((x) => x.classification === g))])),
    allComparison: {
      normalWinVsLoss: featureComparison(rows, 'NORMAL_WIN', 'LOSS'),
      exceptionalWinVsNormal: featureComparison(rows, 'EXCEPTIONAL_WIN', 'NORMAL_WIN'),
      exceptionalWinVsLoss: featureComparison(rows, 'EXCEPTIONAL_WIN', 'LOSS'),
    },
    splitComparison: { DEV: splitComparison(rows, 'DEV'), VAL: splitComparison(rows, 'VAL') },
    devValConsistency: directionConsistency(rows),
    featureDistributions: Object.fromEntries(FEATURES.map((f) => [f, Object.fromEntries(GROUPS.map((g) => [g, quantiles(values(rows.filter((x) => x.classification === g), f))]))])),
    cases: rows.map((x) => ({ split: x.split, time: x.time ?? x.entryTime, classification: x.classification, r: x.r, ...Object.fromEntries(FEATURES.map((f) => [f, Number.isFinite(Number(x[f])) ? Number(x[f]) : null])) })),
  };

  await mkdir(OUT, { recursive: true });
  await writeFile(resolve(OUT, '5m.json'), JSON.stringify(result, null, 2));

  console.log(`PREENTRY_DISCRIMINATIVE N=${result.scope.n} DEV=${result.scope.dev} VAL=${result.scope.val} FRESH=LOCKED`);
  console.log(`GROUPS LOSS=${result.groupStats.LOSS.n} NORMAL=${result.groupStats.NORMAL_WIN.n} EXCEPTIONAL=${result.groupStats.EXCEPTIONAL_WIN.n}`);
  console.log('NORMAL_WIN vs LOSS — median delta (NORMAL - LOSS):');
  console.table(Object.fromEntries(FEATURES.map((f) => [f, { ALL: result.allComparison.normalWinVsLoss[f].medianDelta, DEV: result.devValConsistency[f].DEV.medianDelta, VAL: result.devValConsistency[f].VAL.medianDelta, stable: result.devValConsistency[f].signStableDEVVAL }])));
  console.log('EXCEPTIONAL_WIN vs NORMAL_WIN — median delta:');
  console.table(Object.fromEntries(FEATURES.map((f) => [f, { ALL: result.allComparison.exceptionalWinVsNormal[f].medianDelta, DEV: result.splitComparison.DEV.exceptionalVsNormal[f].medianDelta, VAL: result.splitComparison.VAL.exceptionalVsNormal[f].medianDelta }])));
  console.log(`REPORT=${resolve(OUT, '5m.json')}`);
  console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_RULE NO_FRESH');
}

await main();
