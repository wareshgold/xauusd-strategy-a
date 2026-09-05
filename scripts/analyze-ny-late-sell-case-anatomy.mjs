import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const REPORT = resolve(ROOT, 'data/reports/strategy-a-ny-late-sell-path-geometry-v2/5m.json');
const CANDLES = resolve(ROOT, 'data/historical/xauusd-5min.json');
const OUT = resolve(ROOT, 'data/reports/strategy-a-ny-late-sell-case-anatomy');
const DEV = 6000;
const HORIZONS = [12, 24, 48];

const p = (n) => Number.isFinite(n) ? Number(n.toFixed(6)) : null;

function candleAt(candles, index) {
  const c = candles[index];
  if (!c) return null;
  return { index, timestamp: c.timestamp, open: c.open, high: c.high, low: c.low, close: c.close };
}

function stage(candles, index, priceField = 'close') {
  const c = candleAt(candles, index);
  if (!c) return null;
  return { ...c, price: c[priceField] };
}

function excursion(candles, entryIndex, entry, stopLoss, horizon) {
  const end = Math.min(candles.length - 1, entryIndex + horizon);
  const path = candles.slice(entryIndex + 1, end + 1);
  if (!path.length) return { bars: 0, mfeR: 0, maeR: 0 };
  const risk = Math.abs(entry - stopLoss);
  if (!(risk > 0)) return { bars: path.length, mfeR: null, maeR: null };
  const favorable = Math.max(...path.map((c) => entry - c.low));
  const adverse = Math.max(...path.map((c) => c.high - entry));
  return { bars: path.length, mfeR: p(favorable / risk), maeR: p(adverse / risk) };
}

function outcomeOnPath(candles, row) {
  const risk = Math.abs(row.entry - row.stopLoss);
  if (!(risk > 0)) return { result: 'INVALID', index: null, timestamp: null, rMultiple: null };
  for (let i = row.entryIndex + 1; i < candles.length; i += 1) {
    const c = candles[i];
    const hitSL = c.high >= row.stopLoss;
    const hitTP = c.low <= row.tp1;
    if (hitSL && hitTP) return { result: 'AMBIGUOUS', index: i, timestamp: c.timestamp, rMultiple: null };
    if (hitSL) return { result: 'SL', index: i, timestamp: c.timestamp, rMultiple: -1 };
    if (hitTP) return { result: 'TP1', index: i, timestamp: c.timestamp, rMultiple: Math.abs(row.tp1 - row.entry) / risk };
  }
  return { result: 'OPEN', index: null, timestamp: null, rMultiple: null };
}

function outcomeExcursion(candles, row, outcome) {
  if (!outcome?.index) return null;
  const risk = Math.abs(row.entry - row.stopLoss);
  if (!(risk > 0)) return null;
  const path = candles.slice(row.entryIndex + 1, outcome.index + 1);
  if (!path.length) return { barsToOutcome: 0, mfeR: 0, maeR: 0 };
  const favorable = Math.max(...path.map((c) => row.entry - c.low));
  const adverse = Math.max(...path.map((c) => c.high - row.entry));
  return {
    barsToOutcome: outcome.index - row.entryIndex,
    mfeR: p(favorable / risk),
    maeR: p(adverse / risk),
  };
}

function groupStats(rows) {
  const r = rows.map((x) => Number(x.r)).filter(Number.isFinite);
  const wins = r.filter((x) => x > 0);
  const losses = r.filter((x) => x < 0);
  const gp = wins.reduce((a, b) => a + b, 0);
  const gl = -losses.reduce((a, b) => a + b, 0);
  return {
    n: r.length,
    wins: wins.length,
    losses: losses.length,
    winRate: r.length ? p(wins.length / r.length) : 0,
    avgR: r.length ? p(r.reduce((a, b) => a + b, 0) / r.length) : 0,
    totalR: p(r.reduce((a, b) => a + b, 0)),
    PF: gl ? p(gp / gl) : (gp ? null : 0),
  };
}

function quantiles(values) {
  const a = values.filter(Number.isFinite).sort((x, y) => x - y);
  if (!a.length) return { n: 0 };
  const q = (f) => {
    const pos = (a.length - 1) * f;
    const lo = Math.floor(pos);
    const hi = Math.ceil(pos);
    return p(a[lo] + (a[hi] - a[lo]) * (pos - lo));
  };
  return { n: a.length, min: p(a[0]), p25: q(0.25), median: q(0.5), p75: q(0.75), max: p(a[a.length - 1]) };
}

function pathShape(rows) {
  return {
    breakoutToFollowThroughBars: quantiles(rows.map((x) => x.breakoutToFollowThroughBars)),
    breakoutExtension: quantiles(rows.map((x) => x.breakoutExtension)),
    followThroughDistance: quantiles(rows.map((x) => x.followThroughDistance)),
    spikeSize: quantiles(rows.map((x) => x.spikeSize)),
    spikeSizeToPreRange: quantiles(rows.map((x) => x.spikeSizeToPreRange)),
    correctionDepth: quantiles(rows.map((x) => x.correctionDepth)),
    correctionBars: quantiles(rows.map((x) => x.correctionBars)),
    entryDelayFromCorrection: quantiles(rows.map((x) => x.entryDelayFromCorrection)),
    entryDistanceFromStructuralHighPct: quantiles(rows.map((x) => x.entryDistanceFromStructuralHighPct)),
    entryDistanceFromSpikeEndPct: quantiles(rows.map((x) => x.entryDistanceFromSpikeEndPct)),
    plannedRR: quantiles(rows.map((x) => x.plannedRR)),
  };
}

async function main() {
  const report = JSON.parse(await readFile(REPORT, 'utf8'));
  const candles = JSON.parse(await readFile(CANDLES, 'utf8')).candles ?? [];

  const cases = (report.cases ?? []).map((row) => {
    const entryCandle = candles[row.entryIndex];
    if (!entryCandle) throw new Error(`Missing historical candle at entryIndex ${row.entryIndex} for ${row.entryTime}`);
    if (entryCandle.timestamp !== row.entryTime) {
      throw new Error(`Historical candle lineage mismatch at entryIndex ${row.entryIndex}: report=${row.entryTime} candles=${entryCandle.timestamp}`);
    }

    const outcome = outcomeOnPath(candles, row);
    if (outcome.result === 'AMBIGUOUS') {
      throw new Error(`Ambiguous outcome for ${row.entryTime} at ${outcome.timestamp}`);
    }

    const stages = {
      breakout: stage(candles, row.breakoutIndex),
      followThrough: stage(candles, row.followThroughIndex),
      spikeStart: stage(candles, row.spikeStartIndex),
      spikeEnd: stage(candles, row.spikeEndIndex),
      correctionStart: stage(candles, row.correctionStartIndex),
      structuralExtreme: stage(candles, row.correctionExtremeIndex, row.direction === 'SELL' ? 'high' : 'low'),
      entry: stage(candles, row.entryIndex, 'close'),
    };

    return {
      classification: row.r > 0 ? (row.r >= 5 ? 'EXCEPTIONAL_WIN' : 'NORMAL_WIN') : 'LOSS',
      split: new Date(row.entryTime) < new Date(candles[DEV].timestamp) ? 'DEV' : 'VAL',
      entryTime: row.entryTime,
      entryIndex: row.entryIndex,
      r: row.r,
      recomputedR: outcome.rMultiple,
      result: outcome.result,
      direction: row.direction,
      entry: row.entry,
      stopLoss: row.stopLoss,
      tp1: row.tp1,
      stages,
      outcome: { index: outcome.index, timestamp: outcome.timestamp, type: outcome.result },
      outcomeExcursion: outcomeExcursion(candles, row, outcome),
      fixedHorizonExcursion: Object.fromEntries(HORIZONS.map((h) => [String(h), excursion(candles, row.entryIndex, row.entry, row.stopLoss, h)])),
      geometry: Object.fromEntries(Object.entries(row).filter(([k]) => !['entryTime', 'entryIndex', 'r', 'direction', 'entry', 'stopLoss', 'tp1'].includes(k))),
    };
  });

  const groups = {
    all: cases,
    DEV: cases.filter((x) => x.split === 'DEV'),
    VAL: cases.filter((x) => x.split === 'VAL'),
    EXCEPTIONAL_WIN: cases.filter((x) => x.classification === 'EXCEPTIONAL_WIN'),
    NORMAL_WIN: cases.filter((x) => x.classification === 'NORMAL_WIN'),
    LOSS: cases.filter((x) => x.classification === 'LOSS'),
  };

  const reportOut = {
    strategy: 'Strategy A / SP2L',
    mode: 'RESEARCH_NY_LATE_SELL_CASE_ANATOMY',
    timeframe: '5m',
    scope: { source: 'Path Geometry V2', n: cases.length, dev: groups.DEV.length, val: groups.VAL.length, freshHoldoutExcluded: true, productionUntouched: true },
    methodology: {
      purpose: 'Descriptive case-by-case anatomy before any hypothesis or threshold is frozen.',
      outcome: 'Outcome is recomputed directly from the canonical historical candles using the same first-hit SL/TP semantics as the deterministic backtest. No baseline report join is used.',
      fixedHorizons: HORIZONS.map((h) => `${h} bars after entry`),
      classification: 'EXCEPTIONAL_WIN=r>=5R; NORMAL_WIN=0<r<5R; LOSS=r<0. This classification is descriptive and does not create a trading rule.',
      noOptimization: true,
      noNewThresholds: true,
      holdoutLocked: true,
      lineageCheck: 'entryIndex must resolve to the exact entryTime in the current historical candle file; mismatch fails closed.',
    },
    groupStats: Object.fromEntries(Object.entries(groups).map(([name, rows]) => [name, groupStats(rows)])),
    groupGeometry: Object.fromEntries(Object.entries(groups).map(([name, rows]) => [name, pathShape(rows)])),
    cases,
  };

  await mkdir(OUT, { recursive: true });
  await writeFile(resolve(OUT, '5m.json'), JSON.stringify(reportOut, null, 2));
  console.log(`5m anatomy: cases=${cases.length} DEV=${groups.DEV.length} VAL=${groups.VAL.length}`);
  console.log('Group stats:');
  console.table(Object.fromEntries(Object.entries(reportOut.groupStats).map(([k, v]) => [k, v])));
  console.log('Case classification:');
  console.table(cases.map((x) => ({ split: x.split, time: x.entryTime, class: x.classification, r: x.r, recomputedR: x.recomputedR, result: x.result, barsToOutcome: x.outcomeExcursion?.barsToOutcome ?? null, mfeR: x.outcomeExcursion?.mfeR ?? null, maeR: x.outcomeExcursion?.maeR ?? null })));
}

await main();