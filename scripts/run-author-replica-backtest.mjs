import fs from 'node:fs';

const DATA = 'data/historical/xauusd-1min.json';
const OUT = 'artifacts/sp2l-author-replica-backtest.json';
const cfg = {
  pGapPrice: 1.0,
  spikeMultiplier: 1.5,
  maxSlPrice: 10.0,
  tpR: 1.0,
  emaPeriod: 60,
  useEma: true,
  useTrend: true,
  maxOppositeMoves: 1,
};

const raw = JSON.parse(fs.readFileSync(DATA, 'utf8'));
const candles = (raw.candles ?? raw).map((c) => ({
  time: c.timestamp ?? c.datetime ?? c.time,
  open: Number(c.open), high: Number(c.high), low: Number(c.low), close: Number(c.close),
})).filter(c => [c.open,c.high,c.low,c.close].every(Number.isFinite));

if (candles.length < cfg.emaPeriod + 10) throw new Error(`Not enough candles: ${candles.length}`);

function emaSeries(values, period) {
  const k = 2 / (period + 1);
  const out = Array(values.length).fill(NaN);
  let prev = values[0];
  out[0] = prev;
  for (let i = 1; i < values.length; i++) {
    prev = values[i] * k + prev * (1 - k);
    out[i] = prev;
  }
  return out;
}

const ema = emaSeries(candles.map(c => c.close), cfg.emaPeriod);

function detect(i) {
  if (i < 3) return null;
  const a = candles[i-3], spike = candles[i-2], correction = candles[i-1], trigger = candles[i];
  const sb = spike.close - spike.open;
  const ss = spike.open - spike.close;
  const buy =
    trigger.low < correction.low &&
    correction.close > spike.close && correction.open > spike.open &&
    spike.close > a.close && spike.open > a.open &&
    correction.close > correction.open && spike.close > spike.open && a.close > a.open &&
    correction.low > a.high + cfg.pGapPrice &&
    sb > cfg.spikeMultiplier * (correction.close-correction.open) &&
    sb > cfg.spikeMultiplier * (a.close-a.open) &&
    sb > cfg.spikeMultiplier * (trigger.close-trigger.open);
  const sell =
    trigger.high > correction.high &&
    correction.close < spike.close && correction.open < spike.open &&
    spike.close < a.close && spike.open < a.open &&
    correction.close < correction.open && spike.close < spike.open && a.close < a.open &&
    correction.high < a.low - cfg.pGapPrice &&
    ss > cfg.spikeMultiplier * (correction.open-correction.close) &&
    ss > cfg.spikeMultiplier * (a.open-a.close) &&
    ss > cfg.spikeMultiplier * (trigger.open-trigger.close);
  if (buy === sell) return null;
  const direction = buy ? 'BUY' : 'SELL';
  const entry = buy ? trigger.low : trigger.high;
  const stopLoss = buy ? a.low : a.high;
  const risk = buy ? entry-stopLoss : stopLoss-entry;
  if (!(risk > 0) || risk > cfg.maxSlPrice) return null;
  return { direction, signalIndex:i, entry, stopLoss, risk, takeProfit: buy ? entry+cfg.tpR*risk : entry-cfg.tpR*risk, spikeBody: Math.abs(spike.close-spike.open) };
}

function trendValid(signal) {
  if (!cfg.useTrend) return true;
  let opposite = 0;
  // Mirror the author's trend check from the setup origin through entry.
  const start = signal.signalIndex - 2;
  for (let p = start + 1; p <= signal.signalIndex; p++) {
    if (signal.direction === 'BUY') {
      if (candles[p].high > candles[p-1].high) opposite = 0;
      else { opposite++; if (opposite > cfg.maxOppositeMoves) return false; }
    } else {
      if (candles[p].low < candles[p-1].low) opposite = 0;
      else { opposite++; if (opposite > cfg.maxOppositeMoves) return false; }
    }
  }
  return true;
}

function filtersValid(signal) {
  if (cfg.useEma) {
    const e = ema[signal.signalIndex];
    if (!Number.isFinite(e)) return false;
    if (signal.direction === 'BUY' && candles[signal.signalIndex].close <= e) return false;
    if (signal.direction === 'SELL' && candles[signal.signalIndex].close >= e) return false;
  }
  return trendValid(signal);
}

function run({filters}) {
  const trades = [];
  let open = null;
  let detected = 0;
  for (let i = 3; i < candles.length; i++) {
    if (open) {
      const c = candles[i];
      let result = null;
      if (open.direction === 'BUY') {
        const hitSL = c.low <= open.stopLoss;
        const hitTP = c.high >= open.takeProfit;
        if (hitSL && hitTP) result = { r: -1, reason: 'SL_and_TP_same_bar_SL_first' };
        else if (hitSL) result = { r: -1, reason: 'SL' };
        else if (hitTP) result = { r: 1, reason: 'TP' };
      } else {
        const hitSL = c.high >= open.stopLoss;
        const hitTP = c.low <= open.takeProfit;
        if (hitSL && hitTP) result = { r: -1, reason: 'SL_and_TP_same_bar_SL_first' };
        else if (hitSL) result = { r: -1, reason: 'SL' };
        else if (hitTP) result = { r: 1, reason: 'TP' };
      }
      if (result) {
        trades.push({...open, exitIndex:i, exitTime:c.time, ...result});
        open = null;
      }
      continue;
    }
    const s = detect(i);
    if (!s) continue;
    detected++;
    if (filters && !filtersValid(s)) continue;
    open = {...s, entryTime:candles[i].time};
  }
  const wins = trades.filter(t=>t.r>0).length;
  const losses = trades.filter(t=>t.r<0).length;
  const totalR = trades.reduce((a,t)=>a+t.r,0);
  const grossWin = trades.filter(t=>t.r>0).reduce((a,t)=>a+t.r,0);
  const grossLoss = -trades.filter(t=>t.r<0).reduce((a,t)=>a+t.r,0);
  let equity=0, peak=0, maxDD=0;
  for (const t of trades) { equity += t.r; peak=Math.max(peak,equity); maxDD=Math.max(maxDD,peak-equity); }
  return { detected, trades:trades.length, wins, losses, winRate: trades.length ? wins/trades.length : null, totalR, expectancy: trades.length ? totalR/trades.length : null, profitFactor: grossLoss ? grossWin/grossLoss : null, maxDrawdownR:maxDD, byDirection:{BUY:trades.filter(t=>t.direction==='BUY').length,SELL:trades.filter(t=>t.direction==='SELL').length}, exitReasons:Object.fromEntries([...new Set(trades.map(t=>t.reason))].map(k=>[k,trades.filter(t=>t.reason===k).length])), firstTrade:trades[0]?.entryTime??null,lastTrade:trades.at(-1)?.entryTime??null};
}

const result = {
  methodology: 'RESEARCH-ONLY author implementation replica; not canonical Strategy A. Bar-level entry at trigger low/high and next-bar-forward exit evaluation.',
  data: { source: raw.source, symbol: raw.symbol, timeframe: raw.timeframe, timezone: raw.timezone, candles: candles.length, from: candles[0].time, to: candles.at(-1).time },
  config: cfg,
  noFilters: run({filters:false}),
  reportedConfigFilters: run({filters:true}),
  externalReference: { signals:93, trades:92, wins:66, losses:26, winRate:0.7174, totalR:40, profitFactor:2.538, maxDrawdownCash:-300, secondEntry:false, ema:true, emaPeriod:60, trend:true, maxOppositeMoves:1, range:false, session:false },
};
fs.mkdirSync('artifacts', {recursive:true});
fs.writeFileSync(OUT, JSON.stringify(result, null, 2));
console.log(JSON.stringify(result, null, 2));
