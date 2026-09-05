import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const REPORT = resolve(ROOT, 'data/reports/strategy-a-ny-late-sell-path-geometry-v2/5m.json');
const BASE = resolve(ROOT, 'data/reports/strategy-a-baseline/5min.json');
const CANDLES = resolve(ROOT, 'data/historical/xauusd-5min.json');
const OUT = resolve(ROOT, 'data/reports/strategy-a-ny-late-sell-case-anatomy');
const PRE = 10000;
const DEV = 6000;
const HORIZONS = [12, 24, 48];

const p = (n) => Number.isFinite(n) ? Number(n.toFixed(6)) : null;

function key(c) {
  return `${c.entryIndex}|${c.direction}|${Number(c.entry).toPrecision(15)}|${Number(c.stopLoss).toPrecision(15)}|${Number(c.tp1).toPrecision(15)}`;
}

function candleAt(candles, index) {
  const c = candles[index];
  if (!c) return null;
  return {
    index,
    timestamp: c.timestamp,
    open: c.open,
    high: c.high,
    low: c.low,
    close: c.close,
  };
}

function stage(candles, index, priceField = 'close') {
  const c = candleAt(candles, index);
  if (!c) return null;
  return { ...c, price: c[priceField] };
}

function excursion(candles, entryIndex, entry, stopLoss, tp1, horizon) {
  const end = Math.min(candles.length - 1, entryIndex + horizon);
  const path = candles.slice(entryIndex + 1, end + 1);
  if (!path.length) return { bars: 0, mfeR: 0, maeR: 0 };
  const risk = Math.abs(entry - stopLoss);
  if (!(risk > 0)) return { bars: path.length, mfeR: null, maeR: null };
  const favorable = Math.max(...path.map((c) => entry - c.low));
  const adverse = Math.max(...path.map((c) => c.high - entry));
  return { bars: path.length, mfeR: p(favorable / risk), maeR: p(adverse / risk) };
}

function firstBaselineOutcome(candles, row) {
  const result = row.result;
  if (result !== 'TP1' && result !== 'SL') return null;
  const start = row.entryIndex + 1;
  for (let i = start; i < candles.length; i += 1) {
    const c = candles[i];
    const hitTP = c.low <= row.tp1;
    const hitSL = c.high >= row.stopLoss;
    if (result === 'TP1' && hitTP) return { index: i, timestamp: c.timestamp, type: 'TP1' };
    if (result === 'SL' && hitSL) return { index: i, timestamp: c.timestamp, type: 'SL' };
  }
  return null;
}

function outcomeExcursion(candles, row, outcome) {
  if (!outcome) return null;
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
  const baseline = JSON.parse(await readFile(BASE, 'utf8'));
  const candles = JSON.parse(await readFile(CANDLES, 'utf8')).candles ?? [];
  const outcomes = new Map((baseline.trades ?? [])
    .filter((t) => t.result !== 'AMBIGUOUS' && Number.isFinite(Number(t.rMultiple)))
    .map((t) => [key(t), t]));

  const cases = (report.cases ?? []).map((row) => {
    const base = outcomes.get(key(row));
    if (!base) throw new Error(`Missing baseline outcome for ${row.entryTime}`);
    const stages = {
      breakout: stage(candles, row.breakoutIndex),
      followThrough: stage(candles, row.followThroughIndex),
      spikeStart: stage(candles, row.spikeStartIndex),
      spikeEnd: stage(candles, row.spikeEndIndex),
      correctionStart: stage(candles, row.correctionStartIndex),
      structuralExtreme: stage(candles, row.correctionExtremeIndex, row.direction === 'SELL' ? 'high' : 'low'),
      entry: stage(candles, row.entryIndex, 'close'),
    };
    const outcome = firstBaselineOutcome(candles, base);
    return {
      classification: row.r > 0 ? (row.r >= 5 ? 'EXCEPTIONAL_WIN' : 'NORMAL_WIN') : 'LOSS',
      split: new Date(row.entryTime) < new Date(candles[DEV].timestamp) ? 'DEV' : 'VAL',
      entryTime: row.entryTime,
      entryIndex: row.entryIndex,
      r: row.r,
      result: base.result,
      direction: row.direction,
      entry: row.entry,
      stopLoss: row.stopLoss,
      tp1: row.tp1,
      stages,
      outcome,
      outcomeExcursion: outcomeExcursion(candles, base, outcome),
      fixedHorizonExcursion: Object.fromEntries(HORIZONS.map((h) => [String(h), excursion(candles, row.entryIndex, row.entry, row.stopLoss, row.tp1, h)])),
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
      outcome: 'Baseline TP1/SL result is retained; first candle touching the realized baseline outcome level is used only to measure path excursion to outcome.',
      fixedHorizons: HORIZONS.map((h) => `${h} bars after entry`),
      classification: 'EXCEPTIONAL_WIN=r>=5R; NORMAL_WIN=0<r<5R; LOSS=r<0. This classification is descriptive and does not create a trading rule.',
      noOptimization: true,
      noNewThresholds: true,
      holdoutLocked: true,
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
  console.table(cases.map((x) => ({ split: x.split, time: x.entryTime, class: x.classification, r: x.r, result: x.result, barsToOutcome: x.outcomeExcursion?.barsToOutcome ?? null, mfeR: x.outcomeExcursion?.mfeR ?? null, maeR: x.outcomeExcursion?.maeR ?? null })));
}

await main();
