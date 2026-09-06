import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const SOURCE = resolve(ROOT, 'data/reports/strategy-a-ny-sell-preentry-discriminative-anatomy/5m.json');
const OUT = resolve(ROOT, 'data/reports/strategy-a-ny-sell-preentry-outcome-attribution');
const FEATURES = [
  'pathEfficiency',
  'upperWickShare',
  'triggerReclaimToRange',
  'triggerBodyToRange',
  'triggerReclaimToCorrection',
];
const p = (n) => Number.isFinite(n) ? Number(n.toFixed(6)) : null;

function mean(xs) {
  const a = xs.filter(Number.isFinite);
  return a.length ? a.reduce((s, x) => s + x, 0) / a.length : null;
}
function median(xs) {
  const a = xs.filter(Number.isFinite).sort((a, b) => a - b);
  if (!a.length) return null;
  const m = Math.floor(a.length / 2);
  return a.length % 2 ? a[m] : (a[m - 1] + a[m]) / 2;
}
function pearson(xs, ys) {
  const pairs = xs.map((x, i) => [x, ys[i]]).filter(([x, y]) => Number.isFinite(x) && Number.isFinite(y));
  if (pairs.length < 3) return null;
  const xm = mean(pairs.map(([x]) => x));
  const ym = mean(pairs.map(([, y]) => y));
  let num = 0, dx = 0, dy = 0;
  for (const [x, y] of pairs) {
    num += (x - xm) * (y - ym);
    dx += (x - xm) ** 2;
    dy += (y - ym) ** 2;
  }
  return dx && dy ? p(num / Math.sqrt(dx * dy)) : null;
}
function rank(values) {
  const indexed = values.map((v, i) => ({ v, i })).sort((a, b) => a.v - b.v);
  const out = Array(values.length);
  let i = 0;
  while (i < indexed.length) {
    let j = i + 1;
    while (j < indexed.length && indexed[j].v === indexed[i].v) j++;
    const r = (i + j - 1) / 2 + 1;
    for (let k = i; k < j; k++) out[indexed[k].i] = r;
    i = j;
  }
  return out;
}
function spearman(rows, feature, outcomeKey = 'r') {
  const pairs = rows.map((x) => [Number(x[feature]), Number(x[outcomeKey])]).filter(([x, y]) => Number.isFinite(x) && Number.isFinite(y));
  if (pairs.length < 3) return null;
  const rx = rank(pairs.map(([x]) => x));
  const ry = rank(pairs.map(([, y]) => y));
  return pearson(rx, ry);
}
function stats(rows) {
  const r = rows.map((x) => Number(x.r)).filter(Number.isFinite);
  const wins = r.filter((x) => x > 0), losses = r.filter((x) => x < 0);
  const gw = wins.reduce((s, x) => s + x, 0);
  const gl = -losses.reduce((s, x) => s + x, 0);
  return { n: r.length, WR: r.length ? p(wins.length / r.length) : null, avgR: mean(r), PF: gl ? p(gw / gl) : null, totalR: p(r.reduce((s, x) => s + x, 0)) };
}
function featureSummary(rows, feature) {
  const normalLoss = rows.filter((x) => x.classification === 'NORMAL_WIN' || x.classification === 'LOSS');
  const noExceptional = rows.filter((x) => x.classification !== 'EXCEPTIONAL_WIN');
  const normal = rows.filter((x) => x.classification === 'NORMAL_WIN');
  const loss = rows.filter((x) => x.classification === 'LOSS');
  const values = (rs) => rs.map((x) => Number(x[feature])).filter(Number.isFinite);
  const nVals = values(normal), lVals = values(loss), allVals = values(rows), neVals = values(noExceptional);
  const delta = Number.isFinite(median(nVals)) && Number.isFinite(median(lVals)) ? median(nVals) - median(lVals) : null;
  const deltaNoExceptional = Number.isFinite(median(nVals)) && Number.isFinite(median(lVals)) ? delta : null;
  return {
    normalN: nVals.length,
    lossN: lVals.length,
    normalMedian: p(median(nVals)),
    lossMedian: p(median(lVals)),
    normalMinusLossMedian: p(delta),
    allSpearmanR: spearman(rows, feature),
    nonExceptionalSpearmanR: spearman(noExceptional, feature),
    allFeatureMedian: p(median(allVals)),
    nonExceptionalFeatureMedian: p(median(neVals)),
    normalVsLossUnchangedAfterExceptionalRemoval: deltaNoExceptional === delta,
  };
}
function temporal(rows) {
  return ['DEV', 'VAL'].flatMap((split) => {
    const scoped = rows.filter((x) => x.split === split).sort((a, b) => new Date(a.time) - new Date(b.time));
    const mid = Math.ceil(scoped.length / 2);
    return [scoped.slice(0, mid), scoped.slice(mid)].map((windowRows, i) => ({
      id: `${split}_H${i + 1}`,
      n: windowRows.length,
      outcome: stats(windowRows),
      nonExceptionalOutcome: stats(windowRows.filter((x) => x.classification !== 'EXCEPTIONAL_WIN')),
      features: Object.fromEntries(FEATURES.map((f) => [f, featureSummary(windowRows, f)])),
    }));
  });
}

async function main() {
  const source = JSON.parse(await readFile(SOURCE, 'utf8'));
  const rows = (source.cases ?? []).filter((x) => x.split === 'DEV' || x.split === 'VAL');
  if (!rows.length) throw new Error('No DEV/VAL cases found');
  const noExceptional = rows.filter((x) => x.classification !== 'EXCEPTIONAL_WIN');
  const report = {
    strategy: 'Strategy A / SP2L',
    mode: 'RESEARCH_NY_SELL_PREENTRY_OUTCOME_ATTRIBUTION',
    timeframe: '5m',
    scope: { n: rows.length, dev: rows.filter((x) => x.split === 'DEV').length, val: rows.filter((x) => x.split === 'VAL').length, freshHoldoutExcluded: true, productionUntouched: true },
    methodology: {
      purpose: 'Test whether temporally stable pre-entry descriptors retain outcome association when exceptional winners are removed from the outcome association analysis.',
      features: FEATURES,
      exceptionalDefinition: 'r >= 5R',
      noOptimization: true,
      noThresholdSearch: true,
      noNewTradingRules: true,
      holdoutLocked: true,
      interpretation: 'This is attribution only. Exceptional wins are removed only for sensitivity analysis; no predictive rule is created.',
    },
    overall: { all: stats(rows), nonExceptional: stats(noExceptional), exceptionalCount: rows.length - noExceptional.length },
    features: Object.fromEntries(FEATURES.map((f) => [f, featureSummary(rows, f)])),
    temporalWindows: temporal(rows),
    decisionGuide: {
      retainOnlyIf: 'directional association persists in non-exceptional data and is not confined to one temporal window',
      rejectIf: 'association disappears after exceptional removal or changes sign repeatedly across temporal windows',
    },
  };
  await mkdir(OUT, { recursive: true });
  const out = resolve(OUT, '5m.json');
  await writeFile(out, JSON.stringify(report, null, 2));
  console.log(`PREENTRY_OUTCOME_ATTRIBUTION N=${rows.length} DEV=${report.scope.dev} VAL=${report.scope.val} FRESH=LOCKED`);
  console.log(`ALL avgR=${report.overall.all.avgR} PF=${report.overall.all.PF} | NON_EXCEPTIONAL N=${noExceptional.length} avgR=${report.overall.nonExceptional.avgR} PF=${report.overall.nonExceptional.PF} | EXCEPTIONAL=${report.overall.exceptionalCount}`);
  for (const f of FEATURES) {
    const x = report.features[f];
    console.log(`${f}: medianDelta=${x.normalMinusLossMedian} spearmanAll=${x.allSpearmanR} spearmanNoExceptional=${x.nonExceptionalSpearmanR}`);
  }
  for (const w of report.temporalWindows) console.log(`${w.id}: N=${w.n} avgR=${w.outcome.avgR} PF=${w.outcome.PF} | noExceptionalAvgR=${w.nonExceptionalOutcome.avgR} PF=${w.nonExceptionalOutcome.PF}`);
  console.log(`REPORT=${out}`);
  console.log('STATUS=DESCRIPTIVE_ONLY NO_OPT NO_RULE NO_FRESH');
}
await main();
