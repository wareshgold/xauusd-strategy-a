import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const REPORT_DIR = resolve(ROOT, 'data/reports/strategy-a-baseline');
const TIMEFRAMES = ['1min', '5min'];
const EPSILON = 1e-9;

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function auditTrade(trade, index) {
  const prefix = `trade[${index}]`;
  const closed = Number.isFinite(trade.rMultiple);
  const risk = Number(trade.riskDistance);
  const entry = Number(trade.entry);
  const stop = Number(trade.stopLoss);
  const tp1 = Number(trade.tp1);

  assert(Number.isFinite(entry), `${prefix}: entry is not finite`);
  assert(Number.isFinite(stop), `${prefix}: stopLoss is not finite`);
  assert(Number.isFinite(tp1), `${prefix}: tp1 is not finite`);
  assert(Number.isFinite(risk), `${prefix}: riskDistance is not finite`);
  assert(risk > 0, `${prefix}: riskDistance must be > 0`);

  if (trade.direction === 'BUY') {
    assert(stop < entry - EPSILON, `${prefix}: BUY stop must be below entry`);
    assert(tp1 > entry + EPSILON, `${prefix}: BUY TP1 must be above entry`);
  } else if (trade.direction === 'SELL') {
    assert(stop > entry + EPSILON, `${prefix}: SELL stop must be above entry`);
    assert(tp1 < entry - EPSILON, `${prefix}: SELL TP1 must be below entry`);
  } else {
    throw new Error(`${prefix}: unknown direction ${trade.direction}`);
  }

  const expectedRisk = Math.abs(entry - stop);
  assert(Math.abs(expectedRisk - risk) <= 1e-6, `${prefix}: riskDistance does not match entry/stop`);

  if (closed) {
    assert(trade.result !== 'AMBIGUOUS', `${prefix}: AMBIGUOUS trade cannot have a closed R multiple`);
  }

  return {
    tinyRisk: risk < 0.1,
    veryTinyRisk: risk < 0.05,
    closed,
    rMultiple: closed ? Number(trade.rMultiple) : null,
  };
}

function maxDrawdownR(trades) {
  let equity = 0;
  let peak = 0;
  let maxDrawdown = 0;
  for (const trade of trades) {
    if (!Number.isFinite(trade.rMultiple)) continue;
    equity += trade.rMultiple;
    peak = Math.max(peak, equity);
    maxDrawdown = Math.max(maxDrawdown, peak - equity);
  }
  return maxDrawdown;
}

for (const timeframe of TIMEFRAMES) {
  const report = JSON.parse(await readFile(resolve(REPORT_DIR, `${timeframe}.json`), 'utf8'));
  const trades = report.trades ?? [];
  let closed = 0;
  let tinyRisk = 0;
  let veryTinyRisk = 0;
  let maxR = -Infinity;
  let maxRTrade = null;

  for (let i = 0; i < trades.length; i += 1) {
    const result = auditTrade(trades[i], i);
    if (result.closed) closed += 1;
    if (result.tinyRisk) tinyRisk += 1;
    if (result.veryTinyRisk) veryTinyRisk += 1;
    if (result.closed && result.rMultiple > maxR) {
      maxR = result.rMultiple;
      maxRTrade = trades[i];
    }
  }

  const recomputedDrawdown = maxDrawdownR(trades);
  const reported = Number(report.metrics?.maxDrawdownR);
  assert(!Number.isFinite(reported) || Math.abs(reported - recomputedDrawdown) <= 1e-6,
    `${timeframe}: reported maxDrawdownR differs from recomputed value`);

  console.log(JSON.stringify({
    timeframe,
    candles: report.candles,
    trades: trades.length,
    closedTrades: closed,
    tinyRiskTrades: tinyRisk,
    veryTinyRiskTrades: veryTinyRisk,
    maxR: Number.isFinite(maxR) ? maxR : null,
    maxRTrade: maxRTrade ? {
      entryTime: maxRTrade.entryTime,
      direction: maxRTrade.direction,
      entry: maxRTrade.entry,
      stopLoss: maxRTrade.stopLoss,
      riskDistance: maxRTrade.riskDistance,
      tp1: maxRTrade.tp1,
      rMultiple: maxRTrade.rMultiple,
    } : null,
    recomputedMaxDrawdownR: recomputedDrawdown,
    status: 'PASS: structural and accounting invariants are valid; tiny-risk trades remain diagnostic only',
  }, null, 2));
}
