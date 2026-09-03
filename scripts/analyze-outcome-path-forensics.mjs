import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const BASE_DIR = resolve(ROOT, 'data/reports/strategy-a-baseline');
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-outcome-path-forensics');
const TOTAL = 15000;
const PRE = 10000;
const DEV = 6000;
const HORIZONS = [1, 2, 3, 5, 10, 20];

function metrics(rows) {
  const rs = rows.map(x => Number(x.r)).filter(Number.isFinite);
  const wins = rs.filter(x => x > 0), losses = rs.filter(x => x < 0);
  const grossProfit = wins.reduce((a, b) => a + b, 0);
  const grossLoss = -losses.reduce((a, b) => a + b, 0);
  return {
    n: rs.length,
    wins: wins.length,
    losses: losses.length,
    winRate: rs.length ? wins.length / rs.length : 0,
    avgR: rs.length ? rs.reduce((a, b) => a + b, 0) / rs.length : 0,
    totalR: rs.reduce((a, b) => a + b, 0),
    PF: grossLoss ? grossProfit / grossLoss : null,
  };
}

function quantiles(values) {
  const v = values.filter(Number.isFinite).sort((a, b) => a - b);
  if (!v.length) return { n: 0, p25: null, median: null, p75: null, mean: null };
  const at = p => {
    const i = (v.length - 1) * p;
    const b = Math.floor(i), f = i - b;
    return v[b] + (v[b + 1] ?? v[b]) * f;
  };
  return {
    n: v.length,
    p25: at(0.25),
    median: at(0.5),
    p75: at(0.75),
    mean: v.reduce((a, b) => a + b, 0) / v.length,
  };
}

function pathAt(candles, trade, horizon) {
  const entryIndex = Number(trade.entryIndex);
  const entry = Number(trade.entry);
  const stopLoss = Number(trade.stopLoss);
  const risk = Math.abs(entry - stopLoss);
  if (!Number.isInteger(entryIndex) || !(risk > 0)) return null;

  const end = Math.min(candles.length - 1, entryIndex + horizon);
  let mfe = 0;
  let mae = 0;
  let firstFav = null;
  let firstAdv = null;

  for (let i = entryIndex + 1; i <= end; i++) {
    const candle = candles[i];
    const favorable = trade.direction === 'BUY'
      ? (candle.high - entry) / risk
      : (entry - candle.low) / risk;
    const adverse = trade.direction === 'BUY'
      ? (entry - candle.low) / risk
      : (candle.high - entry) / risk;

    mfe = Math.max(mfe, favorable);
    mae = Math.max(mae, adverse);
    if (firstFav === null && favorable >= 0.25) firstFav = i - entryIndex;
    if (firstAdv === null && adverse >= 0.25) firstAdv = i - entryIndex;
  }

  return { mfe, mae, firstFav, firstAdv };
}

function enrich(candles, trades) {
  return trades.map(trade => {
    const paths = Object.fromEntries(
      HORIZONS.map(h => [h, pathAt(candles, trade, h)])
    );
    const h20 = paths[20];
    return {
      entryIndex: Number(trade.entryIndex),
      entryTime: trade.entryTime,
      direction: trade.direction,
      session: trade.session ?? null,
      r: Number(trade.rMultiple),
      ...Object.fromEntries(HORIZONS.map(h => [`h${h}`, paths[h]])),
      mfe20: h20?.mfe ?? null,
      mae20: h20?.mae ?? null,
      firstFav20: h20?.firstFav ?? null,
      firstAdv20: h20?.firstAdv ?? null,
    };
  }).filter(x => Number.isFinite(x.r));
}

function thresholdStats(rows, field, threshold, mode) {
  const selected = rows.filter(row => {
    const value = row[field];
    return Number.isFinite(value) && (mode === 'lt' ? value < threshold : value >= threshold);
  });
  return { condition: mode === 'lt' ? `<${threshold}` : `>=${threshold}`, ...metrics(selected) };
}

async function run(timeframe) {
  const candles = JSON.parse(
    await readFile(resolve(ROOT, `data/historical/xauusd-${timeframe}.json`), 'utf8')
  ).candles;
  if (candles.length < TOTAL) throw new Error(`${timeframe}: expected ${TOTAL}+ candles, got ${candles.length}`);

  const baseline = JSON.parse(
    await readFile(resolve(BASE_DIR, `${timeframe}.json`), 'utf8')
  );
  const cutoff = new Date(candles[PRE].timestamp);
  const trades = (baseline.trades ?? []).filter(trade =>
    trade.result !== 'AMBIGUOUS' &&
    Number.isFinite(Number(trade.rMultiple)) &&
    new Date(trade.entryTime) < cutoff
  );

  const rows = enrich(candles, trades);
  const dev = rows.filter(row => row.entryIndex < DEV);
  const val = rows.filter(row => row.entryIndex >= DEV && row.entryIndex < PRE);

  const horizonReport = set => Object.fromEntries(HORIZONS.map(h => [h, {
    MFE: quantiles(set.map(row => row[`h${h}`]?.mfe)),
    MAE: quantiles(set.map(row => row[`h${h}`]?.mae)),
    firstFavorableDelay: quantiles(set.map(row => row[`h${h}`]?.firstFav)),
    firstAdverseDelay: quantiles(set.map(row => row[`h${h}`]?.firstAdv)),
  }]));

  const report = {
    strategy: 'Strategy A',
    mode: 'OUTCOME_PATH_FORENSICS_PREHOLDOUT',
    timeframe,
    scope: {
      totalCandles: TOTAL,
      preHoldoutCandles: PRE,
      devCandles: DEV,
      valCandles: PRE - DEV,
      freshHoldoutCandles: TOTAL - PRE,
      freshHoldoutExcluded: true,
    },
    methodology: {
      purpose: 'Diagnose post-entry path: immediate adverse movement, favorable opportunity before failure, and MAE/MFE timing.',
      source: 'Canonical baseline trades only; AMBIGUOUS outcomes excluded; candles after the recorded entry are used for path measurements.',
      horizons: HORIZONS,
      favorableThreshold: '+0.25R',
      adverseThreshold: '-0.25R',
      noOptimization: true,
    },
    counts: { joined: rows.length, DEV: dev.length, VAL: val.length },
    baseline: { DEV: metrics(dev), VAL: metrics(val) },
    mfeMae: { DEV: horizonReport(dev), VAL: horizonReport(val) },
    winnerLoser: {
      DEV: {
        winners: { n: dev.filter(x => x.r > 0).length, mfe20: quantiles(dev.filter(x => x.r > 0).map(x => x.mfe20)), mae20: quantiles(dev.filter(x => x.r > 0).map(x => x.mae20)) },
        losers: { n: dev.filter(x => x.r < 0).length, mfe20: quantiles(dev.filter(x => x.r < 0).map(x => x.mfe20)), mae20: quantiles(dev.filter(x => x.r < 0).map(x => x.mae20)) },
      },
      VAL: {
        winners: { n: val.filter(x => x.r > 0).length, mfe20: quantiles(val.filter(x => x.r > 0).map(x => x.mfe20)), mae20: quantiles(val.filter(x => x.r > 0).map(x => x.mae20)) },
        losers: { n: val.filter(x => x.r < 0).length, mfe20: quantiles(val.filter(x => x.r < 0).map(x => x.mfe20)), mae20: quantiles(val.filter(x => x < 0).map(x => x.mae20)) },
      },
    },
    thresholdDiagnostics: {
      DEV: {
        MFE20_ge_025: thresholdStats(dev, 'mfe20', 0.25, 'ge'),
        MFE20_ge_050: thresholdStats(dev, 'mfe20', 0.5, 'ge'),
        MFE20_ge_100: thresholdStats(dev, 'mfe20', 1, 'ge'),
        MAE20_lt_025: thresholdStats(dev, 'mae20', 0.25, 'lt'),
        MAE20_lt_050: thresholdStats(dev, 'mae20', 0.5, 'lt'),
      },
      VAL: {
        MFE20_ge_025: thresholdStats(val, 'mfe20', 0.25, 'ge'),
        MFE20_ge_050: thresholdStats(val, 'mfe20', 0.5, 'ge'),
        MFE20_ge_100: thresholdStats(val, 'mfe20', 1, 'ge'),
        MAE20_lt_025: thresholdStats(val, 'mae20', 0.25, 'lt'),
        MAE20_lt_050: thresholdStats(val, 'mae20', 0.5, 'lt'),
      },
    },
  };

  await mkdir(OUT_DIR, { recursive: true });
  const out = resolve(OUT_DIR, `${timeframe}.json`);
  await writeFile(out, JSON.stringify(report, null, 2));

  console.log(`${timeframe}: joined=${rows.length} DEV=${dev.length} VAL=${val.length} baselineDEV=${report.baseline.DEV.avgR.toFixed(4)} baselineVAL=${report.baseline.VAL.avgR.toFixed(4)}`);
  for (const h of HORIZONS) {
    console.log(` h${h}: MFE DEV=${report.mfeMae.DEV[h].MFE.median?.toFixed(4) ?? 'n/a'} VAL=${report.mfeMae.VAL[h].MFE.median?.toFixed(4) ?? 'n/a'} | MAE DEV=${report.mfeMae.DEV[h].MAE.median?.toFixed(4) ?? 'n/a'} VAL=${report.mfeMae.VAL[h].MAE.median?.toFixed(4) ?? 'n/a'}`);
  }
  console.log(`Report -> ${out}`);
}

await run('1min');
await run('5min');
