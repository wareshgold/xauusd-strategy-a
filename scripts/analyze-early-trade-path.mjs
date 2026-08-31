import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const TIMEFRAMES = ['1min', '5min'];
const HORIZONS = [1, 2, 3, 5, 10];
const THRESHOLDS = [0.25, 0.5, 1];

const median = (xs) => {
  const a = xs.filter(Number.isFinite).sort((x, y) => x - y);
  if (!a.length) return null;
  const m = Math.floor(a.length / 2);
  return a.length % 2 ? a[m] : (a[m - 1] + a[m]) / 2;
};

const loadJson = async (p) => JSON.parse(await readFile(p, 'utf8'));

function pathForTrade(trade, candles) {
  const risk = Number(trade.riskDistance);
  if (!(risk > 0)) return null;
  const entryIndex = Number(trade.entryIndex);
  const direction = trade.direction;
  const rows = [];
  let first = Object.fromEntries([...THRESHOLDS, ...THRESHOLDS].map(() => []));
  const firstHit = { plus: Object.fromEntries(THRESHOLDS.map((r) => [r, null])), minus: Object.fromEntries(THRESHOLDS.map((r) => [r, null])) };

  for (let h = 1; h <= 10; h++) {
    const c = candles[entryIndex + h];
    if (!c) break;
    const mfeR = direction === 'BUY' ? (c.high - trade.entry) / risk : (trade.entry - c.low) / risk;
    const maeR = direction === 'BUY' ? (trade.entry - c.low) / risk : (c.high - trade.entry) / risk;
    const signedCloseR = direction === 'BUY' ? (c.close - trade.entry) / risk : (trade.entry - c.close) / risk;
    rows.push({ horizon: h, mfeR, maeR, signedCloseR });
    for (const r of THRESHOLDS) {
      if (firstHit.plus[r] === null && mfeR >= r) firstHit.plus[r] = h;
      if (firstHit.minus[r] === null && maeR >= r) firstHit.minus[r] = h;
    }
  }
  return { result: trade.result, rMultiple: trade.rMultiple, riskDistance: risk, rows, firstHit };
}

function summarize(paths) {
  const closed = paths.filter(Boolean);
  const groups = {
    winners: closed.filter((p) => p.rMultiple > 0),
    losers: closed.filter((p) => p.rMultiple < 0),
  };
  const byHorizon = {};
  for (const h of HORIZONS) {
    byHorizon[h] = {};
    for (const [name, group] of Object.entries(groups)) {
      const at = group.map((p) => p.rows.find((r) => r.horizon === h)).filter(Boolean);
      byHorizon[h][name] = {
        n: at.length,
        medianMFER: median(at.map((x) => x.mfeR)),
        medianMAER: median(at.map((x) => x.maeR)),
        medianCloseR: median(at.map((x) => x.signedCloseR)),
      };
    }
  }
  const firstThresholds = {};
  for (const side of ['plus', 'minus']) {
    firstThresholds[side] = {};
    for (const r of THRESHOLDS) {
      firstThresholds[side][r] = {};
      for (const [name, group] of Object.entries(groups)) {
        const hits = group.map((p) => p.firstHit[side][r]).filter((x) => x !== null);
        firstThresholds[side][r][name] = {
          hitCount: hits.length,
          hitRate: group.length ? hits.length / group.length : 0,
          medianBars: median(hits),
        };
      }
    }
  }
  return { byHorizon, firstThresholds };
}

async function run(timeframe) {
  const baseline = await loadJson(resolve(ROOT, `data/reports/strategy-a-baseline/${timeframe}.json`));
  const dataset = await loadJson(resolve(ROOT, `data/historical/xauusd-${timeframe}.json`));
  const paths = baseline.trades.map((t) => pathForTrade(t, dataset.candles));
  const report = {
    strategy: 'Strategy A / SP2L',
    mode: 'DIAGNOSTIC_ONLY',
    timeframe,
    candles: dataset.candles.length,
    tradeCount: paths.filter(Boolean).length,
    horizons: HORIZONS,
    thresholdsR: THRESHOLDS,
    summary: summarize(paths),
    trades: paths.map((p, i) => p ? { entryIndex: baseline.trades[i].entryIndex, entryTime: baseline.trades[i].entryTime, direction: baseline.trades[i].direction, result: p.result, rMultiple: p.rMultiple, riskDistance: p.riskDistance, path: p.rows, firstHit: p.firstHit } : null).filter(Boolean),
    researchNote: 'Diagnostic only. Uses post-entry candle paths from the existing baseline; no strategy parameters or trading rules changed.'
  };
  const outDir = resolve(ROOT, 'data/reports/strategy-a-early-trade-path');
  await mkdir(outDir, { recursive: true });
  const out = resolve(outDir, `${timeframe}.json`);
  await writeFile(out, JSON.stringify(report, null, 2));
  console.log(`${timeframe}: trades=${report.tradeCount}`);
  for (const h of HORIZONS) {
    const s = report.summary.byHorizon[h];
    console.log(`  h+${h}: MFE W/L=${s.winners.medianMFER?.toFixed(3)}/${s.losers.medianMFER?.toFixed(3)} MAE W/L=${s.winners.medianMAER?.toFixed(3)}/${s.losers.medianMAER?.toFixed(3)} closeR W/L=${s.winners.medianCloseR?.toFixed(3)}/${s.losers.medianCloseR?.toFixed(3)}`);
  }
  console.log(`Report -> ${out}`);
}

for (const tf of TIMEFRAMES) await run(tf);
