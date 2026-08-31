import fs from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const TIMEFRAMES = ['1min', '5min'];
const HORIZONS = [2, 3, 5];
const THRESHOLDS_R = [0.25, 0.5, 0.75, 1];

async function loadJson(file) {
  return JSON.parse(await fs.readFile(resolve(ROOT, file), 'utf8'));
}

function stats(rows) {
  const closed = rows.filter(r => Number.isFinite(r.rMultiple));
  const wins = closed.filter(r => r.rMultiple > 0);
  const losses = closed.filter(r => r.rMultiple < 0);
  const grossWin = wins.reduce((s, r) => s + r.rMultiple, 0);
  const grossLoss = Math.abs(losses.reduce((s, r) => s + r.rMultiple, 0));
  let equity = 0, peak = 0, maxDD = 0, streak = 0, maxStreak = 0;
  for (const r of closed) {
    equity += r.rMultiple;
    peak = Math.max(peak, equity);
    maxDD = Math.max(maxDD, peak - equity);
    streak = r.rMultiple < 0 ? streak + 1 : 0;
    maxStreak = Math.max(maxStreak, streak);
  }
  return {
    trades: closed.length,
    wins: wins.length,
    losses: losses.length,
    winRate: closed.length ? wins.length / closed.length : 0,
    averageR: closed.length ? equity / closed.length : 0,
    totalR: equity,
    profitFactor: grossLoss ? grossWin / grossLoss : (grossWin ? Infinity : 0),
    maxDrawdownR: maxDD,
    consecutiveLosses: maxStreak,
  };
}

function pathAt(trade, candles, horizon) {
  const risk = Number(trade.riskDistance);
  if (!(risk > 0)) return null;
  const entry = Number(trade.entry);
  let adverse = 0;
  for (let h = 1; h <= horizon; h++) {
    const c = candles[trade.entryIndex + h];
    if (!c) break;
    const excursion = trade.direction === 'BUY'
      ? (entry - c.low) / risk
      : (c.high - entry) / risk;
    adverse = Math.max(adverse, Math.max(0, excursion));
  }
  return adverse;
}

function evaluateRule(closed, paths, horizon, threshold) {
  const kept = [];
  const removed = [];
  for (let i = 0; i < closed.length; i++) {
    const trade = closed[i];
    if (paths[i] !== null && paths[i] >= threshold) removed.push(trade);
    else kept.push(trade);
  }
  const baseline = stats(closed);
  const result = stats(kept);
  const winners = closed.filter(r => r.rMultiple > 0);
  const losers = closed.filter(r => r.rMultiple < 0);
  const removedWinners = removed.filter(r => r.rMultiple > 0).length;
  const removedLosers = removed.filter(r => r.rMultiple < 0).length;
  return {
    horizon,
    thresholdR: threshold,
    baseline,
    afterRule: result,
    removedTrades: removed.length,
    removedWinners,
    removedLosers,
    winnerRemovalRate: winners.length ? removedWinners / winners.length : 0,
    loserRemovalRate: losers.length ? removedLosers / losers.length : 0,
    loserToWinnerRemovalRatio: removedWinners ? removedLosers / removedWinners : null,
    researchOnly: true,
  };
}

async function run(timeframe) {
  const forensic = await loadJson(`data/reports/strategy-a-trade-forensics/${timeframe}.json`);
  const dataset = await loadJson(`data/historical/xauusd-${timeframe}.json`);
  const closed = forensic.trades.filter(t => Number.isFinite(t.rMultiple));
  const rows = [];
  for (const horizon of HORIZONS) {
    const paths = closed.map(t => pathAt(t, dataset.candles, horizon));
    for (const threshold of THRESHOLDS_R) rows.push(evaluateRule(closed, paths, horizon, threshold));
  }
  const report = {
    strategy: 'Strategy A / SP2L',
    mode: 'DIAGNOSTIC_ONLY',
    timeframe,
    baseline: stats(closed),
    horizons: HORIZONS,
    thresholdsR: THRESHOLDS_R,
    rules: rows,
    methodology: 'Research grid only. A trade is marked removed if its post-entry adverse excursion reaches the threshold by the selected horizon. No replacement exit price is assumed; this is a selection/invalidation diagnostic, not a backtest of execution mechanics.',
    researchNote: 'No strategy parameters or live trading rules changed. Thresholds are predeclared and must be validated out-of-sample before any rule consideration.'
  };
  const outDir = resolve(ROOT, 'data/reports/strategy-a-early-invalidation-grid');
  await fs.mkdir(outDir, { recursive: true });
  const out = resolve(outDir, `${timeframe}.json`);
  await fs.writeFile(out, JSON.stringify(report, null, 2));
  console.log(`${timeframe}: baseline trades=${closed.length} PF=${report.baseline.profitFactor.toFixed(4)} avgR=${report.baseline.averageR.toFixed(4)} totalR=${report.baseline.totalR.toFixed(4)}`);
  for (const row of rows) {
    console.log(`  h+${row.horizon} adverse>=${row.thresholdR}R: kept=${row.afterRule.trades} PF=${row.afterRule.profitFactor.toFixed(4)} avgR=${row.afterRule.averageR.toFixed(4)} totalR=${row.afterRule.totalR.toFixed(4)} DD=${row.afterRule.maxDrawdownR.toFixed(4)} removed=${row.removedTrades} W/L=${row.removedWinners}/${row.removedLosers}`);
  }
  console.log(`Report -> ${out}`);
}

for (const tf of TIMEFRAMES) await run(tf);
