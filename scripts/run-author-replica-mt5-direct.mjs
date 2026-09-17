#!/usr/bin/env node
/**
 * Research-only runner for the author-associated SP2L implementation against
 * an MT5-exported OTET XAUUSD.ecn M1 artifact.
 *
 * No trading API is called. This script only replays committed candle data.
 * It intentionally does not alter canonical geometry or source-resolution state.
 */

import fs from 'node:fs';
import path from 'node:path';

const input = process.argv[2] ?? 'artifacts/mt5_xauusd_m1_10000.json';
const raw = JSON.parse(fs.readFileSync(path.resolve(input), 'utf8'));
const candles = raw.candles ?? raw;

const pGapPrice = Number(process.env.PGAP_PRICE ?? '1');
const spikeMultiplier = Number(process.env.SPIKE_MULTIPLIER ?? '1.5');
const maxSlPrice = Number(process.env.MAX_SL_PRICE ?? '10');
const tpR = Number(process.env.TP_R ?? '1');
const emaPeriod = Number(process.env.EMA_PERIOD ?? '60');
const useEma = (process.env.USE_EMA ?? 'true') === 'true';
const useTrend = (process.env.USE_TREND ?? 'true') === 'true';

function body(c) { return Math.abs(c.close - c.open); }

function emaSeries(values, period) {
  const k = 2 / (period + 1);
  const out = Array(values.length).fill(null);
  let seed = 0;
  for (let i = 0; i < values.length; i += 1) {
    seed += values[i];
    if (i === period - 1) out[i] = seed / period;
    else if (i >= period) out[i] = values[i] * k + out[i - 1] * (1 - k);
  }
  return out;
}

const closes = candles.map(c => Number(c.close));
const ema = emaSeries(closes, emaPeriod);

function evaluateSetup(i) {
  if (i < 4 || ema[i] == null) return null;
  const m1 = candles[i];
  const m2 = candles[i - 1];
  const m3 = candles[i - 2];
  const m4 = candles[i - 3];

  const buy =
    m1.low < m2.low &&
    m2.close > m3.close &&
    m2.open > m3.open &&
    m2.close > m3.close &&
    m3.open > m4.open &&
    m2.close > m2.open &&
    m3.close > m3.open &&
    m4.close > m4.open &&
    m2.low > m4.high + pGapPrice &&
    (m3.close - m3.open) > spikeMultiplier * body(m2) &&
    (m3.close - m3.open) > spikeMultiplier * body(m4) &&
    (m3.close - m3.open) > spikeMultiplier * body(m1) &&
    (!useEma || m1.close > ema[i]) &&
    (!useTrend || ema[i] >= ema[i - 1]);

  const sell =
    m1.high > m2.high &&
    m2.close < m3.close &&
    m2.open < m3.open &&
    m3.close < m4.close &&
    m3.open < m4.open &&
    m2.close < m2.open &&
    m3.close < m3.open &&
    m4.close < m4.open &&
    m2.high < m4.low - pGapPrice &&
    (m3.open - m3.close) > spikeMultiplier * body(m2) &&
    (m3.open - m3.close) > spikeMultiplier * body(m4) &&
    (m3.open - m3.close) > spikeMultiplier * body(m1) &&
    (!useEma || m1.close < ema[i]) &&
    (!useTrend || ema[i] <= ema[i - 1]);

  if (buy) return { direction: 'BUY', index: i, triggerPrice: m1.low, sl: m4.low, time: m1.time_utc ?? m1.time };
  if (sell) return { direction: 'SELL', index: i, triggerPrice: m1.high, sl: m4.high, time: m1.time_utc ?? m1.time };
  return null;
}

const signals = [];
for (let i = 4; i < candles.length; i += 1) {
  const s = evaluateSetup(i);
  if (s) signals.push(s);
}

const trades = [];
for (const s of signals) {
  const risk = Math.abs(s.triggerPrice - s.sl);
  if (!(risk > 0) || risk > maxSlPrice) continue;
  const tp = s.direction === 'BUY' ? s.triggerPrice + tpR * risk : s.triggerPrice - tpR * risk;
  let result = null;
  let exitTime = null;
  let rMultiple = null;
  for (let j = s.index + 1; j < candles.length; j += 1) {
    const c = candles[j];
    const hitSl = s.direction === 'BUY' ? c.low <= s.sl : c.high >= s.sl;
    const hitTp = s.direction === 'BUY' ? c.high >= tp : c.low <= tp;
    if (hitSl && hitTp) { result = 'AMBIGUOUS'; break; }
    if (hitSl) { result = 'LOSS'; rMultiple = -1; exitTime = c.time_utc ?? c.time; break; }
    if (hitTp) { result = 'WIN'; rMultiple = tpR; exitTime = c.time_utc ?? c.time; break; }
  }
  if (result) trades.push({ ...s, risk, tp, result, rMultiple, exitTime });
}

const wins = trades.filter(t => t.result === 'WIN').length;
const losses = trades.filter(t => t.result === 'LOSS').length;
const closed = wins + losses;
const totalR = trades.reduce((a, t) => a + (t.rMultiple ?? 0), 0);
const grossWinR = trades.filter(t => t.rMultiple > 0).reduce((a, t) => a + t.rMultiple, 0);
const grossLossR = -trades.filter(t => t.rMultiple < 0).reduce((a, t) => a + t.rMultiple, 0);

const report = {
  research_only: true,
  source_artifact: input,
  symbol: raw.symbol,
  timeframe: raw.timeframe,
  data_first_utc: raw.first_candle?.time_utc,
  data_last_utc: raw.last_candle?.time_utc,
  requested_count: raw.requested_count,
  returned_count: raw.returned_count,
  config: { pGapPrice, spikeMultiplier, maxSlPrice, tpR, emaPeriod, useEma, useTrend },
  signals_detected: signals.length,
  trades_closed_or_ambiguous: trades.length,
  wins,
  losses,
  ambiguous: trades.filter(t => t.result === 'AMBIGUOUS').length,
  win_rate: closed ? wins / closed : null,
  totalR,
  profit_factor: grossLossR ? grossWinR / grossLossR : null,
  first_signals: signals.slice(0, 20),
  trades: trades.slice(0, 200),
};

console.log(JSON.stringify(report, null, 2));
