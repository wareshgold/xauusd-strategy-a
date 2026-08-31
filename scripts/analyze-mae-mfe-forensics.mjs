import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const OUT = resolve(ROOT, 'data/reports/strategy-a-mae-mfe-forensics');
const src = (tf) => resolve(ROOT, `data/reports/strategy-a-entry-geometry-forensics/${tf}.json`);
const candleSrc = (tf) => resolve(ROOT, `data/historical/xauusd-${tf}.json`);

function finite(v) { return Number.isFinite(Number(v)); }
function pick(r, keys) { for (const k of keys) if (finite(r[k])) return Number(r[k]); return null; }
function stats(rows) {
  const n = rows.length;
  if (!n) return { n: 0, avgR: 0, totalR: 0, winRate: 0, PF: null };
  const rs = rows.map(r => Number(r.rMultiple)).filter(Number.isFinite);
  const wins = rs.filter(x => x > 0), losses = rs.filter(x => x < 0);
  const gp = wins.reduce((a, b) => a + b, 0), gl = -losses.reduce((a, b) => a + b, 0);
  return { n, avgR: rs.reduce((a, b) => a + b, 0) / rs.length, totalR: rs.reduce((a, b) => a + b, 0), winRate: wins.length / rs.length, PF: gl ? gp / gl : (gp ? null : 0) };
}
function split(rows) {
  const a = [...rows].sort((x, y) => new Date(x.entryTime) - new Date(y.entryTime));
  const c = Math.floor(a.length / 3);
  return { dev: a.slice(0, c), validation: a.slice(c, 2 * c), holdout: a.slice(2 * c) };
}
function bucket(rows, fn) { return rows.filter(fn); }

function exitIndexForTrade(trade, candles) {
  const entryIndex = Number.isInteger(trade.entryIndex) ? trade.entryIndex : Number(trade.entryIndex);
  const entry = pick(trade, ['entry', 'entryPrice', 'fillPrice', 'price']);
  const stop = pick(trade, ['stopLoss', 'stop', 'sl']);
  const tp1 = pick(trade, ['tp1', 'takeProfit', 'target']);
  const tp2 = pick(trade, ['tp2']);
  if (!Number.isInteger(entryIndex) || !finite(entry) || !finite(stop) || !finite(tp1)) return null;
  for (let i = entryIndex + 1; i < candles.length; i++) {
    const c = candles[i];
    const sl = trade.direction === 'BUY' ? c.low <= stop : c.high >= stop;
    const hitTp1 = trade.direction === 'BUY' ? c.high >= tp1 : c.low <= tp1;
    const hitTp2 = tp2 === null ? false : trade.direction === 'BUY' ? c.high >= tp2 : c.low <= tp2;
    if (sl || hitTp1 || hitTp2) return i;
  }
  return null;
}

function derivePathMetrics(trade, candles) {
  const entryIndex = Number.isInteger(trade.entryIndex) ? trade.entryIndex : Number(trade.entryIndex);
  const entry = pick(trade, ['entry', 'entryPrice', 'fillPrice', 'price']);
  const risk = pick(trade, ['riskDistance', 'risk', 'stopDistance']);
  const exitIndex = exitIndexForTrade(trade, candles);
  if (!Number.isInteger(entryIndex) || !finite(entry) || !finite(risk) || risk <= 0 || !Number.isInteger(exitIndex)) return {};

  const buy = trade.direction === 'BUY';
  let worst = 0, best = 0, maeIndex = entryIndex, mfeIndex = entryIndex;
  for (let i = entryIndex + 1; i <= exitIndex; i++) {
    const c = candles[i];
    const lo = Number(c.low), hi = Number(c.high);
    const adverse = buy ? entry - lo : hi - entry;
    const favorable = buy ? hi - entry : entry - lo;
    if (Number.isFinite(adverse) && adverse > worst) { worst = adverse; maeIndex = i; }
    if (Number.isFinite(favorable) && favorable > best) { best = favorable; mfeIndex = i; }
  }
  return {
    maeR: Math.max(0, worst) / risk,
    mfeR: Math.max(0, best) / risk,
    timeToMfeBars: Math.max(0, mfeIndex - entryIndex),
    timeToMaeBars: Math.max(0, maeIndex - entryIndex),
    exitIndex,
    excursionSource: 'backtest_exit_candle_historical_ohlc',
  };
}

async function report(tf) {
  const [raw, candleRaw] = await Promise.all([
    readFile(src(tf), 'utf8'),
    readFile(candleSrc(tf), 'utf8'),
  ]);
  const source = JSON.parse(raw);
  const candleData = JSON.parse(candleRaw);
  const candles = candleData.candles ?? candleData;
  const all = (source.tradeRows || []).filter(r => Number.isFinite(r.rMultiple));
  const rows = all.map(r => {
    const derived = derivePathMetrics(r, candles);
    return {
      ...r,
      ...derived,
      mae: derived.maeR ?? pick(r, ['maeR', 'MAE', 'maxAdverseExcursionR', 'maxAdverseR', 'maxLossR']),
      mfe: derived.mfeR ?? pick(r, ['mfeR', 'MFE', 'maxFavorableExcursionR', 'maxFavorableR']),
      timeToMfeBars: derived.timeToMfeBars ?? pick(r, ['timeToMfeBars', 'barsToMfe', 'barsToMaxFavorable']),
      timeToMaeBars: derived.timeToMaeBars ?? pick(r, ['timeToMaeBars', 'barsToMae', 'barsToMaxAdverse']),
    };
  });
  const s = split(rows);
  const buckets = {
    mae: {
      LT_025: r => r.mae !== null && r.mae !== undefined && r.mae < .25,
      '025_050': r => r.mae !== null && r.mae !== undefined && r.mae >= .25 && r.mae < .5,
      '050_075': r => r.mae !== null && r.mae !== undefined && r.mae >= .5 && r.mae < .75,
      '075_100': r => r.mae !== null && r.mae !== undefined && r.mae >= .75 && r.mae < 1,
      GE_100: r => r.mae !== null && r.mae !== undefined && r.mae >= 1,
    },
    mfe: {
      LT_050: r => r.mfe !== null && r.mfe !== undefined && r.mfe < .5,
      '050_100': r => r.mfe !== null && r.mfe !== undefined && r.mfe >= .5 && r.mfe < 1,
      '100_150': r => r.mfe !== null && r.mfe !== undefined && r.mfe >= 1 && r.mfe < 1.5,
      '150_200': r => r.mfe !== null && r.mfe !== undefined && r.mfe >= 1.5 && r.mfe < 2,
      GE_200: r => r.mfe !== null && r.mfe !== undefined && r.mfe >= 2,
    },
    timeToMfeBars: {
      D0_2: r => r.timeToMfeBars !== null && r.timeToMfeBars !== undefined && r.timeToMfeBars <= 2,
      D3_5: r => r.timeToMfeBars !== null && r.timeToMfeBars !== undefined && r.timeToMfeBars >= 3 && r.timeToMfeBars <= 5,
      D6_8: r => r.timeToMfeBars !== null && r.timeToMfeBars !== undefined && r.timeToMfeBars >= 6 && r.timeToMfeBars <= 8,
      D9_12: r => r.timeToMfeBars !== null && r.timeToMfeBars !== undefined && r.timeToMfeBars >= 9 && r.timeToMfeBars <= 12,
      D13_PLUS: r => r.timeToMfeBars !== null && r.timeToMfeBars !== undefined && r.timeToMfeBars >= 13,
    },
  };
  const out = {
    strategy: 'Strategy A / SP2L',
    mode: 'RESEARCH_MAE_MFE_TRADE_PATH_FORENSICS_V3',
    timeframe: tf,
    scope: 'Descriptive trade-path analysis; MAE/MFE derived from historical OHLC from the first post-entry candle through the same first exit candle used by the backtest; no rule selection or holdout optimization',
    methodology: {
      exitReplay: 'Replays the BacktestEngine first-hit order: SL, then TP2, then TP1, using the recorded entry/stop/targets and entryIndex',
      mae: 'Maximum adverse intrabar excursion divided by recorded riskDistance',
      mfe: 'Maximum favorable intrabar excursion divided by recorded riskDistance',
      timing: 'Number of bars from entryIndex to the candle containing the maximum excursion',
      lookahead: 'Only candles from entryIndex + 1 through the backtest exit candle are used',
    },
    globalCounts: { all: rows.length, dev: s.dev.length, validation: s.validation.length, holdout: s.holdout.length },
    coverage: {
      mae: rows.filter(r => Number.isFinite(r.mae)).length,
      mfe: rows.filter(r => Number.isFinite(r.mfe)).length,
      timeToMfeBars: rows.filter(r => Number.isFinite(r.timeToMfeBars)).length,
      timeToMaeBars: rows.filter(r => Number.isFinite(r.timeToMaeBars)).length,
      exitIndex: rows.filter(r => Number.isInteger(r.exitIndex)).length,
    },
    overall: stats(rows),
    by: {},
  };
  for (const [name, defs] of Object.entries(buckets)) {
    out.by[name] = {};
    for (const [label, fn] of Object.entries(defs)) {
      out.by[name][label] = {
        all: stats(bucket(rows, fn)),
        dev: stats(bucket(s.dev, fn)),
        validation: stats(bucket(s.validation, fn)),
        holdout: stats(bucket(s.holdout, fn)),
      };
    }
  }
  out.thresholds = {};
  for (const x of [0.5, 1, 1.5, 2]) {
    out.thresholds[`mfe_ge_${x}R`] = {
      all: stats(rows.filter(r => r.mfe !== null && r.mfe !== undefined && r.mfe >= x)),
      dev: stats(s.dev.filter(r => r.mfe !== null && r.mfe !== undefined && r.mfe >= x)),
      validation: stats(s.validation.filter(r => r.mfe !== null && r.mfe !== undefined && r.mfe >= x)),
      holdout: stats(s.holdout.filter(r => r.mfe !== null && r.mfe !== undefined && r.mfe >= x)),
    };
  }
  return out;
}

await mkdir(OUT, { recursive: true });
for (const tf of ['1min', '5min']) {
  const r = await report(tf);
  const p = resolve(OUT, `${tf}.json`);
  await writeFile(p, JSON.stringify(r, null, 2));
  console.log(`${tf}: trades=${r.globalCounts.all} MAE=${r.coverage.mae} MFE=${r.coverage.mfe} timeToMFE=${r.coverage.timeToMfeBars} exits=${r.coverage.exitIndex}`);
  console.log(`Report -> ${p}`);
}
