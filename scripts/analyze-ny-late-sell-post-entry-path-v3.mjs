import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const ANATOMY = resolve(ROOT, 'data/reports/strategy-a-ny-late-sell-case-anatomy/5m.json');
const CANDLES = resolve(ROOT, 'data/historical/xauusd-5min.json');
const OUT = resolve(ROOT, 'data/reports/strategy-a-ny-late-sell-post-entry-path-v3');
const HORIZONS = [1, 2, 3, 6, 12];
const GROUPS = ['EXCEPTIONAL_WIN', 'NORMAL_WIN', 'LOSS'];

const p = (n) => Number.isFinite(n) ? Number(n.toFixed(6)) : null;

function quantiles(values) {
  const a = values.filter(Number.isFinite).sort((x, y) => x - y);
  if (!a.length) return { n: 0 };
  const q = (f) => {
    const pos = (a.length - 1) * f;
    const lo = Math.floor(pos);
    const hi = Math.ceil(pos);
    return p(a[lo] + (a[hi] - a[lo]) * (pos - lo));
  };
  return { n: a.length, min: p(a[0]), p25: q(.25), median: q(.5), p75: q(.75), max: p(a[a.length - 1]), mean: p(a.reduce((s, x) => s + x, 0) / a.length) };
}

function pathAt(candles, row, horizon) {
  const entryIndex = Number(row.entryIndex);
  const entry = Number(row.entry);
  const stop = Number(row.stopLoss);
  const risk = Math.abs(entry - stop);
  if (!(risk > 0) || !Number.isInteger(entryIndex)) return null;
  const end = Math.min(candles.length - 1, entryIndex + horizon);
  const path = candles.slice(entryIndex + 1, end + 1);
  if (!path.length) return null;
  const lows = path.map((c) => (entry - c.low) / risk);
  const highs = path.map((c) => (c.high - entry) / risk);
  const closes = path.map((c) => (entry - c.close) / risk);
  const first = path[0];
  const firstFavorable = (entry - first.low) / risk;
  const firstAdverse = (first.high - entry) / risk;
  const firstCloseR = (entry - first.close) / risk;
  const firstRangeR = (first.high - first.low) / risk;
  const firstBodyR = Math.abs(first.close - first.open) / risk;
  const firstAligned = first.close < first.open;
  const favorableFirst = firstFavorable > firstAdverse;
  const adverseFirst = firstAdverse > firstFavorable;
  const conflictFirst = first.low <= entry - risk && first.high >= stop;
  return {
    barsObserved: path.length,
    mfeR: p(Math.max(0, ...lows)),
    maeR: p(Math.max(0, ...highs)),
    closeExcursionR: p(closes[closes.length - 1]),
    minCloseExcursionR: p(Math.min(...closes)),
    maxCloseExcursionR: p(Math.max(...closes)),
    firstBar: {
      favorableR: p(Math.max(0, firstFavorable)),
      adverseR: p(Math.max(0, firstAdverse)),
      closeR: p(firstCloseR),
      rangeR: p(firstRangeR),
      bodyR: p(firstBodyR),
      alignedBearish: firstAligned,
      favorableDominant: favorableFirst,
      adverseDominant: adverseFirst,
      intrabarOneRConflict: conflictFirst,
    },
  };
}

function summarize(rows, horizon) {
  const xs = rows.map((x) => x.path[String(horizon)]).filter(Boolean);
  const first = xs.map((x) => x.firstBar);
  return {
    n: xs.length,
    mfeR: quantiles(xs.map((x) => x.mfeR)),
    maeR: quantiles(xs.map((x) => x.maeR)),
    closeExcursionR: quantiles(xs.map((x) => x.closeExcursionR)),
    firstBar: {
      favorableR: quantiles(first.map((x) => x.favorableR)),
      adverseR: quantiles(first.map((x) => x.adverseR)),
      closeR: quantiles(first.map((x) => x.closeR)),
      rangeR: quantiles(first.map((x) => x.rangeR)),
      bodyR: quantiles(first.map((x) => x.bodyR)),
      favorableDominantRate: first.length ? p(first.filter((x) => x.favorableDominant).length / first.length) : null,
      adverseDominantRate: first.length ? p(first.filter((x) => x.adverseDominant).length / first.length) : null,
      oneRConflictRate: first.length ? p(first.filter((x) => x.intrabarOneRConflict).length / first.length) : null,
    },
  };
}

async function main() {
  const anatomy = JSON.parse(await readFile(ANATOMY, 'utf8'));
  const candles = JSON.parse(await readFile(CANDLES, 'utf8')).candles ?? [];
  const sourceCases = anatomy.cases ?? [];
  if (sourceCases.length !== 15) throw new Error(`Expected 15 anatomy cases, got ${sourceCases.length}`);

  const cases = sourceCases.map((row) => {
    const enriched = { ...row, entryIndex: Number(row.entryIndex), entry: Number(row.entry), stopLoss: Number(row.stopLoss) };
    const path = Object.fromEntries(HORIZONS.map((h) => [String(h), pathAt(candles, enriched, h)]));
    return { split: row.split, time: row.entryTime, class: row.classification, r: Number(row.r), plannedRR: Number(row.plannedRR), path };
  });

  const report = {
    strategy: 'Strategy A / SP2L',
    mode: 'RESEARCH_NY_LATE_SELL_POST_ENTRY_PATH_V3',
    timeframe: '5m',
    scope: { source: 'NY late SELL case anatomy V2', n: cases.length, dev: cases.filter((x) => x.split === 'DEV').length, val: cases.filter((x) => x.split === 'VAL').length, freshHoldoutExcluded: true, productionUntouched: true },
    methodology: {
      purpose: 'Descriptive post-entry path anatomy for the already identified NY late SELL cases. No candidate selection, entry, stop, target, or management rule is changed.',
      horizonsBars: HORIZONS,
      firstBar: 'Measures favorable excursion, adverse excursion, close displacement, range, body, and whether favorable/adverse excursion dominates on the first post-entry candle.',
      intrabar: 'A first-bar one-R conflict means both +1R favorable price and the stop were touched in the same OHLC candle; intrabar order is unknowable.',
      noOptimization: true,
      noThresholdSearch: true,
      noNewTradingRules: true,
      holdoutLocked: true,
      interpretationGuard: 'This is hypothesis-generation evidence only. Any future rule must be frozen on DEV, validated on VAL, then tested once on the locked fresh holdout.',
    },
    groupStats: Object.fromEntries(GROUPS.map((group) => [group, Object.fromEntries(HORIZONS.map((h) => [String(h), summarize(cases.filter((x) => x.class === group), h)]))])),
    splitStats: Object.fromEntries(['DEV', 'VAL'].map((split) => [split, Object.fromEntries(HORIZONS.map((h) => [String(h), summarize(cases.filter((x) => x.split === split), h)]))])),
    cases,
  };

  await mkdir(OUT, { recursive: true });
  await writeFile(resolve(OUT, '5m.json'), JSON.stringify(report, null, 2));

  console.log(`5m post-entry V3: cases=${cases.length} DEV=${report.scope.dev} VAL=${report.scope.val}`);
  for (const group of GROUPS) {
    console.log(`\n${group}`);
    for (const h of HORIZONS) {
      const s = report.groupStats[group][String(h)];
      console.log(` ${h}b: N=${s.n} firstFavMed=${s.firstBar.favorableR.median ?? '—'} firstAdvMed=${s.firstBar.adverseR.median ?? '—'} firstCloseMed=${s.firstBar.closeR.median ?? '—'} MFE=${s.mfeR.median ?? '—'} MAE=${s.maeR.median ?? '—'} favDom=${s.firstBar.favorableDominantRate ?? '—'}`);
    }
  }
  console.log(`Report -> ${resolve(OUT, '5m.json')}`);
}

await main();
