import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const PATH_DIR = resolve(ROOT, 'data/reports/strategy-a-entry-path-forensics');
const BASE_DIR = resolve(ROOT, 'data/reports/strategy-a-baseline');
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-entry-trigger-failure-ordering-v2');
const PRE = 10000;
const HORIZONS = [1, 2, 3, 5, 10];

function metrics(rows) {
  const rs = rows.map(x => Number(x.r)).filter(Number.isFinite);
  const wins = rs.filter(x => x > 0), losses = rs.filter(x => x < 0);
  const gp = wins.reduce((a, b) => a + b, 0), gl = -losses.reduce((a, b) => a + b, 0);
  return {
    n: rs.length,
    wins: wins.length,
    losses: losses.length,
    winRate: rs.length ? wins.length / rs.length : 0,
    avgR: rs.length ? rs.reduce((a, b) => a + b, 0) / rs.length : 0,
    totalR: rs.reduce((a, b) => a + b, 0),
    PF: gl ? gp / gl : null,
  };
}

function key(c) {
  return `${c.index}|${c.direction}|${Number(c.entry).toPrecision(15)}|${Number(c.stopLoss).toPrecision(15)}|${Number(c.tp1).toPrecision(15)}`;
}

function firstEvents(row, candles, horizon) {
  const i = Number(row.index), dir = row.direction;
  const entry = Number(row.entry), sl = Number(row.stopLoss), level = Number(row.triggerLevel);
  const risk = Math.abs(entry - sl);
  const end = Math.min(i + horizon, candles.length - 1);
  let stopIndex = null, invalidationCloseIndex = null, invalidationWickIndex = null;
  let stopBars = null, invalidationCloseBars = null, invalidationWickBars = null;

  for (let j = i + 1; j <= end; j++) {
    const c = candles[j], high = Number(c.high), low = Number(c.low), close = Number(c.close);
    const stop = dir === 'BUY' ? low <= sl : high >= sl;
    const invalidationClose = dir === 'BUY' ? close < level : close > level;
    const invalidationWick = dir === 'BUY' ? low < level : high > level;
    if (stop && stopIndex === null) { stopIndex = j; stopBars = j - i; }
    if (invalidationClose && invalidationCloseIndex === null) { invalidationCloseIndex = j; invalidationCloseBars = j - i; }
    if (invalidationWick && invalidationWickIndex === null) { invalidationWickIndex = j; invalidationWickBars = j - i; }
  }

  const classify = (a, b) => {
    if (a === null && b === null) return 'NONE';
    if (a !== null && b === null) return 'STOP_FIRST';
    if (a === null && b !== null) return 'INVALIDATION_FIRST';
    if (a < b) return 'STOP_FIRST';
    if (b < a) return 'INVALIDATION_FIRST';
    return 'SAME_CANDLE';
  };

  return {
    stopIndex,
    stopBars,
    invalidationCloseIndex,
    invalidationCloseBars,
    invalidationWickIndex,
    invalidationWickBars,
    closeOrder: classify(stopIndex, invalidationCloseIndex),
    wickOrder: classify(stopIndex, invalidationWickIndex),
    riskToImpulse: risk / Math.max(Number(row.spikeSize), 1e-9),
    triggerToStopDistance: Math.abs(entry - sl) / Math.max(Number(row.spikeSize), 1e-9),
    triggerLevelToStopDistance: Math.abs(level - sl) / Math.max(Number(row.spikeSize), 1e-9),
  };
}

function bucket(rows, fn) {
  return {
    all: metrics(rows),
    winners: metrics(rows.filter(r => r.r > 0)),
    losers: metrics(rows.filter(r => r.r < 0)),
    ...fn(rows),
  };
}

async function run(timeframe) {
  const candles = JSON.parse(await readFile(resolve(ROOT, `data/historical/xauusd-${timeframe}.json`), 'utf8')).candles;
  const pathData = JSON.parse(await readFile(resolve(PATH_DIR, `${timeframe}.json`), 'utf8'));
  const base = JSON.parse(await readFile(resolve(BASE_DIR, `${timeframe}.json`), 'utf8'));
  const cutoff = candles[PRE]?.timestamp;
  const trades = (base.trades ?? []).filter(t => t.result !== 'AMBIGUOUS' && Number.isFinite(Number(t.rMultiple)) && new Date(t.entryTime) < new Date(cutoff));
  const tradeMap = new Map(trades.map(t => [key({ index: t.entryIndex, direction: t.direction, entry: t.entry, stopLoss: t.stopLoss, tp1: t.tp1 }), t]));
  const rows = [];
  for (const c of (pathData.baselineSelected ?? []).filter(c => Number(c.index) < PRE)) {
    const t = tradeMap.get(key(c));
    if (t) rows.push({ ...c, r: Number(t.rMultiple), result: t.result });
  }

  const horizon = {};
  for (const h of HORIZONS) {
    const enriched = rows.map(r => ({ ...r, event: firstEvents(r, candles, h) }));
    const groups = {};
    for (const mode of ['closeOrder', 'wickOrder']) {
      groups[mode] = {};
      for (const value of ['STOP_FIRST', 'INVALIDATION_FIRST', 'SAME_CANDLE', 'NONE']) {
        const subset = enriched.filter(r => r.event[mode] === value);
        groups[mode][value] = metrics(subset);
      }
    }
    groups.eventTiming = {
      stopWithin1: metrics(enriched.filter(r => r.event.stopBars === 1)),
      invalidationCloseWithin1: metrics(enriched.filter(r => r.event.invalidationCloseBars === 1)),
      invalidationWickWithin1: metrics(enriched.filter(r => r.event.invalidationWickBars === 1)),
      invalidationCloseBeforeStop: metrics(enriched.filter(r => r.event.invalidationCloseBars !== null && (r.event.stopBars === null || r.event.invalidationCloseBars < r.event.stopBars))),
      invalidationWickBeforeStop: metrics(enriched.filter(r => r.event.invalidationWickBars !== null && (r.event.stopBars === null || r.event.invalidationWickBars < r.event.stopBars))),
    };
    horizon[`h${h}`] = groups;
  }

  const riskBins = {
    '<0.25': rows.filter(r => Number(r.riskToImpulse ?? firstEvents(r, candles, 1).riskToImpulse) < 0.25),
    '0.25-0.5': rows.filter(r => { const x = Number(r.riskToImpulse ?? firstEvents(r, candles, 1).riskToImpulse); return x >= 0.25 && x < 0.5; }),
    '0.5-1': rows.filter(r => { const x = Number(r.riskToImpulse ?? firstEvents(r, candles, 1).riskToImpulse); return x >= 0.5 && x < 1; }),
    '>=1': rows.filter(r => Number(r.riskToImpulse ?? firstEvents(r, candles, 1).riskToImpulse) >= 1),
  };

  const report = {
    strategy: 'Strategy A',
    mode: 'ENTRY_TRIGGER_FAILURE_ORDERING_V2_PREHOLDOUT',
    timeframe,
    scope: { preHoldoutCandles: PRE, freshHoldoutExcluded: true },
    baseline: metrics(rows),
    methodology: {
      stop: 'canonical SL touched by wick',
      closeInvalidation: 'post-entry candle close crosses back through trigger level',
      wickInvalidation: 'post-entry candle wick crosses back through trigger level',
      ordering: 'first event by post-entry candle index; SAME_CANDLE when both first occur on the same candle',
      purpose: 'diagnostic mechanism attribution only; no threshold optimization; no production change',
    },
    horizon,
    riskToImpulse: Object.fromEntries(Object.entries(riskBins).map(([k, v]) => [k, metrics(v)])),
  };

  await mkdir(OUT_DIR, { recursive: true });
  const out = resolve(OUT_DIR, `${timeframe}.json`);
  await writeFile(out, JSON.stringify(report, null, 2));
  console.log(`${timeframe}: n=${rows.length} avgR=${report.baseline.avgR.toFixed(4)} PF=${report.baseline.PF?.toFixed(4) ?? 'n/a'}`);
  for (const h of HORIZONS) {
    const x = horizon[`h${h}`];
    console.log(` h${h} close=${JSON.stringify(x.closeOrder)} wick=${JSON.stringify(x.wickOrder)}`);
    console.log(`  timing closeBeforeStop=${x.eventTiming.invalidationCloseBeforeStop.avgR.toFixed(4)} n=${x.eventTiming.invalidationCloseBeforeStop.n} | wickBeforeStop=${x.eventTiming.invalidationWickBeforeStop.avgR.toFixed(4)} n=${x.eventTiming.invalidationWickBeforeStop.n}`);
  }
  console.log(`Report -> ${out}`);
}

await run('1min');
await run('5min');
