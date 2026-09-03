import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const BASE_DIR = resolve(ROOT, 'data/reports/strategy-a-baseline');
const OUT_DIR = resolve(ROOT, 'data/reports/strategy-a-outcome-path-forensics');
const TOTAL = 15000;
const PRE = 10000;
const DEV = 6000;
const HORIZONS = [1, 2, 3, 5, 10, 20];
const THRESHOLDS = [0.25, 0.5, 1];

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

function pathToHorizon(candles, trade, horizon) {
  const entryIndex = Number(trade.entryIndex);
  const entry = Number(trade.entry);
  const stopLoss = Number(trade.stopLoss);
  const risk = Math.abs(entry - stopLoss);
  if (!Number.isInteger(entryIndex) || !(risk > 0)) return null;

  const end = Math.min(candles.length - 1, entryIndex + horizon);
  let mfe = 0, mae = 0;
  const firstFav = {}, firstAdv = {};
  const maxFavBeforeAdv = {}, maxAdvBeforeFav = {};

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
    for (const t of THRESHOLDS) {
      const k = String(t);
      if (firstFav[k] == null && favorable >= t) firstFav[k] = i - entryIndex;
      if (firstAdv[k] == null && adverse >= t) firstAdv[k] = i - entryIndex;
    }
  }

  for (const t of THRESHOLDS) {
    const k = String(t);
    const favDelay = firstFav[k];
    const advDelay = firstAdv[k];
    maxFavBeforeAdv[k] = advDelay == null ? null : pathToThreshold(candles, trade, advDelay, 'fav', t);
    maxAdvBeforeFav[k] = favDelay == null ? null : pathToThreshold(candles, trade, favDelay, 'adv', t);
  }

  return { horizon, mfe, mae, firstFav, firstAdv, maxFavBeforeAdv, maxAdvBeforeFav };
}

function pathToThreshold(candles, trade, bars, mode, threshold) {
  const entryIndex = Number(trade.entryIndex);
  const entry = Number(trade.entry);
  const stopLoss = Number(trade.stopLoss);
  const risk = Math.abs(entry - stopLoss);
  let extreme = 0;
  const end = Math.min(candles.length - 1, entryIndex + bars);
  for (let i = entryIndex + 1; i <= end; i++) {
    const candle = candles[i];
    const value = trade.direction === 'BUY'
      ? (mode === 'fav' ? (candle.high - entry) / risk : (entry - candle.low) / risk)
      : (mode === 'fav' ? (entry - candle.low) / risk : (candle.high - entry) / risk);
    extreme = Math.max(extreme, value);
  }
  return extreme;
}

function enrich(candles, trades) {
  return trades.map(trade => {
    const paths = Object.fromEntries(HORIZONS.map(h => [h, pathToHorizon(candles, trade, h)]));
    const h20 = paths[20];
    return {
      entryIndex: Number(trade.entryIndex),
      entryTime: trade.entryTime,
      direction: trade.direction,
      session: trade.session ?? null,
      r: Number(trade.rMultiple),
      paths,
      mfe20: h20?.mfe ?? null,
      mae20: h20?.mae ?? null,
    };
  }).filter(x => Number.isFinite(x.r));
}

function eventRows(rows, horizon) {
  return rows.map(row => {
    const p = row.paths[horizon];
    const result = {};
    for (const t of THRESHOLDS) {
      const k = String(t);
      const f = p?.firstFav?.[k] ?? null;
      const a = p?.firstAdv?.[k] ?? null;
      result[`fav${k}`] = f;
      result[`adv${k}`] = a;
      result[`first${k}`] = f != null && a != null ? (f < a ? 'FAVORABLE_FIRST' : a < f ? 'ADVERSE_FIRST' : 'SAME_BAR') : f != null ? 'FAVORABLE_ONLY' : a != null ? 'ADVERSE_ONLY' : 'NEITHER';
      result[`favBeforeAdv${k}`] = f != null && a != null && f < a;
      result[`advBeforeFav${k}`] = f != null && a != null && a < f;
    }
    return { row, ...result };
  });
}

function eventSummary(rows, horizon) {
  const er = eventRows(rows, horizon);
  const out = {};
  for (const t of THRESHOLDS) {
    const k = String(t);
    const both = er.filter(x => x[`fav${k}`] != null && x[`adv${k}`] != null);
    const favFirst = both.filter(x => x[`favBeforeAdv${k}`]);
    const advFirst = both.filter(x => x[`advBeforeFav${k}`]);
    const sameBar = both.filter(x => x[`first${k}`] === 'SAME_BAR');
    const favOnly = er.filter(x => x[`first${k}`] === 'FAVORABLE_ONLY');
    const advOnly = er.filter(x => x[`first${k}`] === 'ADVERSE_ONLY');
    const neither = er.filter(x => x[`first${k}`] === 'NEITHER');
    out[k] = {
      thresholdR: t,
      n: er.length,
      favorableFirst: { n: favFirst.length, rate: er.length ? favFirst.length / er.length : 0, metrics: metrics(favFirst.map(x => x.row)) },
      adverseFirst: { n: advFirst.length, rate: er.length ? advFirst.length / er.length : 0, metrics: metrics(advFirst.map(x => x.row)) },
      sameBar: { n: sameBar.length, rate: er.length ? sameBar.length / er.length : 0, metrics: metrics(sameBar.map(x => x.row)) },
      favorableOnly: { n: favOnly.length, rate: er.length ? favOnly.length / er.length : 0, metrics: metrics(favOnly.map(x => x.row)) },
      adverseOnly: { n: advOnly.length, rate: er.length ? advOnly.length / er.length : 0, metrics: metrics(advOnly.map(x => x.row)) },
      neither: { n: neither.length, rate: er.length ? neither.length / er.length : 0, metrics: metrics(neither.map(x => x.row)) },
      bothThresholdsReached: { n: both.length, rate: er.length ? both.length / er.length : 0 },
      timeToFavorable: quantiles(er.map(x => x[`fav${k}`])),
      timeToAdverse: quantiles(er.map(x => x[`adv${k}`])),
    };
  }
  return out;
}

function winnerLoser(rows) {
  const groups = {
    winners: rows.filter(x => x.r > 0),
    losers: rows.filter(x => x.r < 0),
  };
  const out = {};
  for (const [name, group] of Object.entries(groups)) {
    out[name] = {
      n: group.length,
      mfe20: quantiles(group.map(x => x.mfe20)),
      mae20: quantiles(group.map(x => x.mae20)),
      firstFavorableDelay25: quantiles(group.map(x => x.paths[20]?.firstFav?.['0.25'])),
      firstAdverseDelay25: quantiles(group.map(x => x.paths[20]?.firstAdv?.['0.25'])),
      firstFavorableDelay50: quantiles(group.map(x => x.paths[20]?.firstFav?.['0.5'])),
      firstAdverseDelay50: quantiles(group.map(x => x.paths[20]?.firstAdv?.['0.5'])),
      firstFavorableDelay100: quantiles(group.map(x => x.paths[20]?.firstFav?.['1'])),
      firstAdverseDelay100: quantiles(group.map(x => x.paths[20]?.firstAdv?.['1'])),
    };
  }
  return out;
}

function thresholdOutcome(rows, threshold, field) {
  const selected = rows.filter(row => Number.isFinite(row[field]) && row[field] >= threshold);
  return { threshold, ...metrics(selected) };
}

async function run(timeframe) {
  const candles = JSON.parse(await readFile(resolve(ROOT, `data/historical/xauusd-${timeframe}.json`), 'utf8')).candles;
  if (candles.length < TOTAL) throw new Error(`${timeframe}: expected ${TOTAL}+ candles, got ${candles.length}`);

  const baseline = JSON.parse(await readFile(resolve(BASE_DIR, `${timeframe}.json`), 'utf8'));
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
    MFE: quantiles(set.map(row => row.paths[h]?.mfe)),
    MAE: quantiles(set.map(row => row.paths[h]?.mae)),
    firstFavorableDelay25: quantiles(set.map(row => row.paths[h]?.firstFav?.['0.25'])),
    firstAdverseDelay25: quantiles(set.map(row => row.paths[h]?.firstAdv?.['0.25'])),
  }]));

  const report = {
    strategy: 'Strategy A',
    mode: 'OUTCOME_PATH_ORDERING_FORENSICS_PREHOLDOUT',
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
      purpose: 'Post-entry path ordering diagnostics to distinguish bad entry from stop/path friction.',
      source: 'Canonical baseline trades only; AMBIGUOUS outcomes excluded; future candles are used only for descriptive path measurements.',
      horizons: HORIZONS,
      thresholds: THRESHOLDS.map(t => `+/-${t}R`),
      sameBar: 'A favorable and adverse threshold reached on the same candle is classified as SAME_BAR; intrabar ordering is unknown.',
      noOptimization: true,
      noProductionChange: true,
    },
    counts: { joined: rows.length, DEV: dev.length, VAL: val.length },
    baseline: { DEV: metrics(dev), VAL: metrics(val) },
    mfeMae: { DEV: horizonReport(dev), VAL: horizonReport(val) },
    ordering: {
      DEV: Object.fromEntries(HORIZONS.map(h => [h, eventSummary(dev, h)])),
      VAL: Object.fromEntries(HORIZONS.map(h => [h, eventSummary(val, h)])),
    },
    winnerLoser: { DEV: winnerLoser(dev), VAL: winnerLoser(val) },
    managementOpportunity: {
      DEV: {
        beforeAdverse25: {
          mfeBeforeAdv25_ge_025: thresholdOutcome(dev.map(row => ({ ...row, value: row.paths[20]?.maxFavBeforeAdv?.['0.25'] })), 0.25, 'value'),
          mfeBeforeAdv25_ge_050: thresholdOutcome(dev.map(row => ({ ...row, value: row.paths[20]?.maxFavBeforeAdv?.['0.25'] })), 0.5, 'value'),
        },
        adverseBeforeFavorable25: {
          maeBeforeFav25_ge_025: thresholdOutcome(dev.map(row => ({ ...row, value: row.paths[20]?.maxAdvBeforeFav?.['0.25'] })), 0.25, 'value'),
          maeBeforeFav25_ge_050: thresholdOutcome(dev.map(row => ({ ...row, value: row.paths[20]?.maxAdvBeforeFav?.['0.25'] })), 0.5, 'value'),
        },
      },
      VAL: {
        beforeAdverse25: {
          mfeBeforeAdv25_ge_025: thresholdOutcome(val.map(row => ({ ...row, value: row.paths[20]?.maxFavBeforeAdv?.['0.25'] })), 0.25, 'value'),
          mfeBeforeAdv25_ge_050: thresholdOutcome(val.map(row => ({ ...row, value: row.paths[20]?.maxFavBeforeAdv?.['0.25'] })), 0.5, 'value'),
        },
        adverseBeforeFavorable25: {
          maeBeforeFav25_ge_025: thresholdOutcome(val.map(row => ({ ...row, value: row.paths[20]?.maxAdvBeforeFav?.['0.25'] })), 0.25, 'value'),
          maeBeforeFav25_ge_050: thresholdOutcome(val.map(row => ({ ...row, value: row.paths[20]?.maxAdvBeforeFav?.['0.25'] })), 0.5, 'value'),
        },
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
  for (const t of THRESHOLDS) {
    const k = String(t);
    const d = report.ordering.DEV[20][k], v = report.ordering.VAL[20][k];
    console.log(` h20 +/-${t}R: DEV favorableFirst=${d.favorableFirst.rate.toFixed(3)} adverseFirst=${d.adverseFirst.rate.toFixed(3)} sameBar=${d.sameBar.rate.toFixed(3)} | VAL favorableFirst=${v.favorableFirst.rate.toFixed(3)} adverseFirst=${v.adverseFirst.rate.toFixed(3)} sameBar=${v.sameBar.rate.toFixed(3)}`);
  }
  console.log(`Report -> ${out}`);
}

await run('1min');
await run('5min');
