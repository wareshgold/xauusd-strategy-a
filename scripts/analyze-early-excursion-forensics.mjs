import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const OUT = resolve(ROOT, 'data/reports/strategy-a-early-excursion-forensics');
const TIMEFRAMES = ['1min', '5min'];
const HORIZONS = [1, 2, 3, 5, 8, 12, 20];

function finite(v) { return Number.isFinite(Number(v)); }
function pick(r, keys) { for (const k of keys) if (finite(r[k])) return Number(r[k]); return null; }
function stats(rows) {
  const rs = rows.map(r => Number(r.rMultiple)).filter(Number.isFinite);
  const wins = rs.filter(x => x > 0);
  const losses = rs.filter(x => x < 0);
  const gp = wins.reduce((a, b) => a + b, 0);
  const gl = -losses.reduce((a, b) => a + b, 0);
  return {
    n: rs.length,
    winRate: rs.length ? wins.length / rs.length : 0,
    PF: gl ? gp / gl : (gp ? null : 0),
    avgR: rs.length ? rs.reduce((a, b) => a + b, 0) / rs.length : 0,
    totalR: rs.reduce((a, b) => a + b, 0),
  };
}
function split(rows) {
  const a = [...rows].sort((x, y) => new Date(x.entryTime) - new Date(y.entryTime));
  const c = Math.floor(a.length / 3);
  return { dev: a.slice(0, c), validation: a.slice(c, 2 * c), holdout: a.slice(2 * c) };
}
function band(v, edges, labels) {
  if (!Number.isFinite(v)) return 'UNKNOWN';
  for (let i = 0; i < edges.length; i++) if (v < edges[i]) return labels[i];
  return labels[labels.length - 1];
}

function pathAt(trade, candles, horizon) {
  const entryIndex = Number(trade.entryIndex);
  const entry = pick(trade, ['entry', 'entryPrice', 'fillPrice', 'price']);
  const risk = pick(trade, ['riskDistance', 'risk', 'stopDistance']);
  if (!Number.isInteger(entryIndex) || !finite(entry) || !finite(risk) || risk <= 0) return null;
  const end = Math.min(candles.length - 1, entryIndex + horizon);
  if (end <= entryIndex) return null;
  const buy = String(trade.direction).toUpperCase() === 'BUY';
  let mae = 0, mfe = 0;
  for (let i = entryIndex + 1; i <= end; i++) {
    const c = candles[i];
    const lo = Number(c.low), hi = Number(c.high);
    if (!Number.isFinite(lo) || !Number.isFinite(hi)) continue;
    mae = Math.max(mae, buy ? entry - lo : hi - entry);
    mfe = Math.max(mfe, buy ? hi - entry : entry - lo);
  }
  return { maeR: Math.max(0, mae) / risk, mfeR: Math.max(0, mfe) / risk, bars: end - entryIndex };
}

function firstExitIndex(trade, candles) {
  const entryIndex = Number(trade.entryIndex);
  const entry = pick(trade, ['entry', 'entryPrice', 'fillPrice', 'price']);
  const stop = pick(trade, ['stopLoss', 'stop', 'sl']);
  const tp1 = pick(trade, ['tp1', 'takeProfit', 'target']);
  const tp2 = pick(trade, ['tp2']);
  if (!Number.isInteger(entryIndex) || !finite(entry) || !finite(stop) || !finite(tp1)) return null;
  for (let i = entryIndex + 1; i < candles.length; i++) {
    const c = candles[i];
    const sl = trade.direction === 'BUY' ? c.low <= stop : c.high >= stop;
    const tp2Hit = tp2 !== null && (trade.direction === 'BUY' ? c.high >= tp2 : c.low <= tp2);
    const tp1Hit = trade.direction === 'BUY' ? c.high >= tp1 : c.low <= tp1;
    if (sl || tp2Hit || tp1Hit) return i;
  }
  return null;
}

async function run(tf) {
  const [raw, candleRaw] = await Promise.all([
    readFile(resolve(ROOT, `data/reports/strategy-a-entry-geometry-forensics/${tf}.json`), 'utf8'),
    readFile(resolve(ROOT, `data/historical/xauusd-${tf}.json`), 'utf8'),
  ]);
  const source = JSON.parse(raw);
  const candleData = JSON.parse(candleRaw);
  const candles = candleData.candles ?? candleData;
  const base = (source.tradeRows || []).filter(r => Number.isFinite(r.rMultiple));

  const rows = [];
  for (const trade of base) {
    const exitIndex = firstExitIndex(trade, candles);
    const early = {};
    for (const h of HORIZONS) early[h] = pathAt(trade, candles, h);
    rows.push({ ...trade, exitIndex, early });
  }
  const s = split(rows);

  const byHorizon = {};
  for (const h of HORIZONS) {
    const valid = rows.filter(r => r.early[h]);
    const maeBuckets = {
      LT_025: r => r.early[h]?.maeR < .25,
      '025_050': r => r.early[h]?.maeR >= .25 && r.early[h]?.maeR < .5,
      '050_075': r => r.early[h]?.maeR >= .5 && r.early[h]?.maeR < .75,
      '075_100': r => r.early[h]?.maeR >= .75 && r.early[h]?.maeR < 1,
      GE_100: r => r.early[h]?.maeR >= 1,
    };
    const mfeBuckets = {
      LT_050: r => r.early[h]?.mfeR < .5,
      '050_100': r => r.early[h]?.mfeR >= .5 && r.early[h]?.mfeR < 1,
      '100_150': r => r.early[h]?.mfeR >= 1 && r.early[h]?.mfeR < 1.5,
      '150_200': r => r.early[h]?.mfeR >= 1.5 && r.early[h]?.mfeR < 2,
      GE_200: r => r.early[h]?.mfeR >= 2,
    };
    const summarizeBuckets = defs => Object.fromEntries(Object.entries(defs).map(([name, fn]) => [name, {
      all: stats(valid.filter(fn)),
      dev: stats(s.dev.filter(r => r.early[h] && fn(r))),
      validation: stats(s.validation.filter(r => r.early[h] && fn(r))),
      holdout: stats(s.holdout.filter(r => r.early[h] && fn(r))),
    }]));
    byHorizon[`H${h}`] = {
      coverage: valid.length,
      overall: stats(valid),
      mae: summarizeBuckets(maeBuckets),
      mfe: summarizeBuckets(mfeBuckets),
      joint: {
        lowMAE_highMFE: {
          all: stats(valid.filter(r => r.early[h].maeR < .5 && r.early[h].mfeR >= 1)),
          dev: stats(s.dev.filter(r => r.early[h] && r.early[h].maeR < .5 && r.early[h].mfeR >= 1)),
          validation: stats(s.validation.filter(r => r.early[h] && r.early[h].maeR < .5 && r.early[h].mfeR >= 1)),
          holdout: stats(s.holdout.filter(r => r.early[h] && r.early[h].maeR < .5 && r.early[h].mfeR >= 1)),
        },
        highMAE_lowMFE: {
          all: stats(valid.filter(r => r.early[h].maeR >= 1 && r.early[h].mfeR < .5)),
          dev: stats(s.dev.filter(r => r.early[h] && r.early[h].maeR >= 1 && r.early[h].mfeR < .5)),
          validation: stats(s.validation.filter(r => r.early[h] && r.early[h].maeR >= 1 && r.early[h].mfeR < .5)),
          holdout: stats(s.holdout.filter(r => r.early[h] && r.early[h].maeR >= 1 && r.early[h].mfeR < .5)),
        },
      },
    };
  }

  const report = {
    strategy: 'Strategy A / SP2L',
    mode: 'RESEARCH_EARLY_EXCURSION_PATH_FORENSICS_V1',
    timeframe: tf,
    scope: 'Descriptive post-entry path analysis intended to identify exit-management hypotheses; it must not be used as an entry filter because the measurements occur after entry.',
    methodology: {
      horizonsBars: HORIZONS,
      mae: 'Maximum adverse intrabar excursion from entry through the specified post-entry horizon, divided by recorded riskDistance',
      mfe: 'Maximum favorable intrabar excursion from entry through the specified post-entry horizon, divided by recorded riskDistance',
      split: 'One shared chronological DEV/VALIDATION/HOLDOUT partition',
      antiLookahead: 'Early excursion is measured only after entry. No future excursion is used to classify an entry before it occurs.',
      importantWarning: 'These results are descriptive. A positive subgroup does not authorize a rule change. Any exit rule must be simulated prospectively and validated on untouched data.',
    },
    globalCounts: { all: rows.length, dev: s.dev.length, validation: s.validation.length, holdout: s.holdout.length },
    byHorizon,
  };

  await mkdir(OUT, { recursive: true });
  const out = resolve(OUT, `${tf}.json`);
  await writeFile(out, JSON.stringify(report, null, 2));
  console.log(`${tf}: trades=${rows.length} horizons=${HORIZONS.join(',')}`);
  for (const h of HORIZONS) {
    const x = byHorizon[`H${h}`];
    const j = x.joint.lowMAE_highMFE;
    console.log(`  H${h}: coverage=${x.coverage} lowMAE+highMFE HOLDOUT n=${j.holdout.n} PF=${j.holdout.PF?.toFixed(4) ?? 'n/a'} avgR=${j.holdout.avgR.toFixed(4)} | highMAE+lowMFE HOLDOUT n=${x.joint.highMAE_lowMFE.holdout.n} PF=${x.joint.highMAE_lowMFE.holdout.PF?.toFixed(4) ?? 'n/a'} avgR=${x.joint.highMAE_lowMFE.holdout.avgR.toFixed(4)}`);
  }
  console.log(`Report -> ${out}`);
}

for (const tf of TIMEFRAMES) await run(tf);
