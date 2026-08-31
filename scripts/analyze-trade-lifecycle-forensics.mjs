import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { resolve } from 'node:path';

const ROOT = resolve(process.cwd());
const OUT = resolve(ROOT, 'data/reports/strategy-a-trade-lifecycle-forensics');
const src = tf => resolve(ROOT, `data/reports/strategy-a-entry-geometry-forensics/${tf}.json`);
const candleSrc = tf => resolve(ROOT, `data/historical/xauusd-${tf}.json`);

const MAE_LEVELS = [0.25, 0.5, 0.75, 1];
const MFE_LEVELS = [0.5, 1, 1.5, 2];

function finite(v) { return Number.isFinite(Number(v)); }
function num(r, ...keys) { for (const k of keys) if (finite(r[k])) return Number(r[k]); return null; }
function stats(rows) {
  const rs = rows.map(r => Number(r.rMultiple)).filter(Number.isFinite);
  const n = rs.length;
  if (!n) return { n: 0, avgR: 0, totalR: 0, winRate: 0, PF: null };
  const wins = rs.filter(x => x > 0), losses = rs.filter(x => x < 0);
  const gp = wins.reduce((a, b) => a + b, 0), gl = -losses.reduce((a, b) => a + b, 0);
  return { n, avgR: rs.reduce((a, b) => a + b, 0) / n, totalR: rs.reduce((a, b) => a + b, 0), winRate: wins.length / n, PF: gl ? gp / gl : (gp ? null : 0) };
}
function split(rows) {
  const a = [...rows].sort((x, y) => new Date(x.entryTime) - new Date(y.entryTime));
  const c = Math.floor(a.length / 3);
  return { dev: a.slice(0, c), validation: a.slice(c, 2 * c), holdout: a.slice(2 * c) };
}
function q(values) {
  const vals = values.filter(Number.isFinite).sort((a, b) => a - b);
  if (!vals.length) return null;
  const at = p => vals[Math.min(vals.length - 1, Math.floor((vals.length - 1) * p))];
  return { p25: at(.25), median: at(.5), p75: at(.75), mean: vals.reduce((a,b)=>a+b,0)/vals.length };
}
function descriptive(rows) {
  const winners = rows.filter(r => r.lifecycle.outcome === 'WIN');
  const losers = rows.filter(r => r.lifecycle.outcome === 'LOSS');
  const metrics = xs => ({
    n: xs.length,
    exitBars: q(xs.map(r => r.lifecycle.exitBars)),
    maeR: q(xs.map(r => r.lifecycle.maeR)),
    mfeR: q(xs.map(r => r.lifecycle.mfeR)),
    timeToMfeBars: q(xs.map(r => r.lifecycle.timeToMfeBars)),
    timeToMaeBars: q(xs.map(r => r.lifecycle.timeToMaeBars)),
  });
  return { all: metrics(rows), winners: metrics(winners), losers: metrics(losers) };
}
function exitIndexForTrade(trade, candles) {
  const entryIndex = Number(trade.entryIndex);
  const entry = num(trade, 'entry', 'entryPrice', 'fillPrice', 'price');
  const stop = num(trade, 'stopLoss', 'stop', 'sl');
  const tp1 = num(trade, 'tp1', 'takeProfit', 'target');
  const tp2 = num(trade, 'tp2');
  if (!Number.isInteger(entryIndex) || !finite(entry) || !finite(stop) || !finite(tp1)) return null;
  for (let i = entryIndex + 1; i < candles.length; i++) {
    const c = candles[i];
    const sl = trade.direction === 'BUY' ? c.low <= stop : c.high >= stop;
    const hitTp1 = trade.direction === 'BUY' ? c.high >= tp1 : c.low <= tp1;
    const hitTp2 = tp2 === null ? false : trade.direction === 'BUY' ? c.high >= tp2 : c.low <= tp2;
    if (sl || hitTp2 || hitTp1) return i;
  }
  return null;
}
function enrich(row, candles) {
  const entryIndex = Number(row.entryIndex);
  const entry = num(row, 'entry', 'entryPrice', 'fillPrice', 'price');
  const risk = num(row, 'riskDistance', 'risk', 'stopDistance');
  const exitIndex = exitIndexForTrade(row, candles);
  let maeR = num(row, 'maeR', 'mae', 'MAE');
  let mfeR = num(row, 'mfeR', 'mfe', 'MFE');
  let timeToMfeBars = num(row, 'timeToMfeBars', 'barsToMfe', 'barsToMaxFavorable');
  let timeToMaeBars = num(row, 'timeToMaeBars', 'barsToMae', 'barsToMaxAdverse');
  if (Number.isInteger(entryIndex) && finite(entry) && finite(risk) && risk > 0 && Number.isInteger(exitIndex)) {
    const buy = row.direction === 'BUY';
    let worst = 0, best = 0, maeIndex = entryIndex, mfeIndex = entryIndex;
    for (let i = entryIndex + 1; i <= exitIndex; i++) {
      const c = candles[i];
      const lo = Number(c.low), hi = Number(c.high);
      const adverse = buy ? entry - lo : hi - entry;
      const favorable = buy ? hi - entry : entry - lo;
      if (Number.isFinite(adverse) && adverse > worst) { worst = adverse; maeIndex = i; }
      if (Number.isFinite(favorable) && favorable > best) { best = favorable; mfeIndex = i; }
    }
    maeR = Math.max(0, worst) / risk;
    mfeR = Math.max(0, best) / risk;
    timeToMfeBars = Math.max(0, mfeIndex - entryIndex);
    timeToMaeBars = Math.max(0, maeIndex - entryIndex);
  }
  const exitBars = Number.isInteger(exitIndex) && Number.isInteger(entryIndex) ? Math.max(0, exitIndex - entryIndex) : num(row, 'exitBar', 'barsToExit', 'timeToExitBars', 'holdingBars', 'barsHeld');
  const r = Number(row.rMultiple);
  return { ...row, lifecycle: { outcome: r > 0 ? 'WIN' : r < 0 ? 'LOSS' : 'FLAT', exitBars, maeR, mfeR, timeToMfeBars, timeToMaeBars, mfeBeforeExit: finite(mfeR) && finite(exitBars) && finite(timeToMfeBars) ? timeToMfeBars <= exitBars : null, maeBeforeExit: finite(maeR) && finite(exitBars) && finite(timeToMaeBars) ? timeToMaeBars <= exitBars : null, excursionEfficiency: finite(mfeR) && finite(maeR) ? mfeR / Math.max(1, maeR) : null } };
}
async function run(tf) {
  const [raw, candleRaw] = await Promise.all([readFile(src(tf), 'utf8'), readFile(candleSrc(tf), 'utf8')]);
  const source = JSON.parse(raw), candleData = JSON.parse(candleRaw), candles = candleData.candles ?? candleData;
  const rows = (source.tradeRows || []).filter(r => finite(r.rMultiple)).map(r => enrich(r, candles));
  const s = split(rows);
  const out = {
    strategy: 'Strategy A / SP2L', mode: 'RESEARCH_TRADE_LIFECYCLE_FORENSICS_V2', timeframe: tf,
    scope: 'Descriptive lifecycle analysis only. Metrics are replayed from the same recorded trade rows and historical OHLC used by the MAE/MFE forensic engine; no rule selection or holdout optimization.',
    methodology: { source: 'strategy-a-entry-geometry-forensics tradeRows + historical OHLC', dimensions: ['exit timing','MAE','MFE','time-to-MAE','time-to-MFE','winner/loser lifecycle separation'], split: 'single chronological thirds: DEV / VALIDATION / HOLDOUT; holdout is descriptive only', exitReplay: 'first post-entry candle hitting SL, TP2, or TP1', excursionWindow: 'entryIndex + 1 through replayed exit candle', note: 'No missing lifecycle fields are imputed from outcome.' },
    counts: { all: rows.length, dev: s.dev.length, validation: s.validation.length, holdout: s.holdout.length },
    lifecycle: { all: descriptive(rows), dev: descriptive(s.dev), validation: descriptive(s.validation), holdout: descriptive(s.holdout) },
    outcomeByDirection: {}, outcomeBySession: {}, thresholds: {}, pathClasses: {}
  };
  for (const direction of ['BUY','SELL']) out.outcomeByDirection[direction] = { all: stats(rows.filter(r=>r.direction===direction)), dev: stats(s.dev.filter(r=>r.direction===direction)), validation: stats(s.validation.filter(r=>r.direction===direction)), holdout: stats(s.holdout.filter(r=>r.direction===direction)) };
  for (const session of ['LONDON','NEW_YORK','OUTSIDE']) out.outcomeBySession[session] = { all: stats(rows.filter(r=>r.session===session)), dev: stats(s.dev.filter(r=>r.session===session)), validation: stats(s.validation.filter(r=>r.session===session)), holdout: stats(s.holdout.filter(r=>r.session===session)) };
  for (const x of MAE_LEVELS) out.thresholds[`mae_ge_${x}R`] = { all: stats(rows.filter(r=>finite(r.lifecycle.maeR)&&r.lifecycle.maeR>=x)), dev: stats(s.dev.filter(r=>finite(r.lifecycle.maeR)&&r.lifecycle.maeR>=x)), validation: stats(s.validation.filter(r=>finite(r.lifecycle.maeR)&&r.lifecycle.maeR>=x)), holdout: stats(s.holdout.filter(r=>finite(r.lifecycle.maeR)&&r.lifecycle.maeR>=x)) };
  for (const x of MFE_LEVELS) out.thresholds[`mfe_ge_${x}R`] = { all: stats(rows.filter(r=>finite(r.lifecycle.mfeR)&&r.lifecycle.mfeR>=x)), dev: stats(s.dev.filter(r=>finite(r.lifecycle.mfeR)&&r.lifecycle.mfeR>=x)), validation: stats(s.validation.filter(r=>finite(r.lifecycle.mfeR)&&r.lifecycle.mfeR>=x)), holdout: stats(s.holdout.filter(r=>finite(r.lifecycle.mfeR)&&r.lifecycle.mfeR>=x)) };
  const classes = [
    ['fast_winner', r=>r.lifecycle.outcome==='WIN'&&finite(r.lifecycle.timeToMfeBars)&&r.lifecycle.timeToMfeBars<=3],
    ['slow_winner', r=>r.lifecycle.outcome==='WIN'&&finite(r.lifecycle.timeToMfeBars)&&r.lifecycle.timeToMfeBars>3],
    ['fast_loser', r=>r.lifecycle.outcome==='LOSS'&&finite(r.lifecycle.exitBars)&&r.lifecycle.exitBars<=3],
    ['slow_loser', r=>r.lifecycle.outcome==='LOSS'&&finite(r.lifecycle.exitBars)&&r.lifecycle.exitBars>3],
    ['low_adverse_winner', r=>r.lifecycle.outcome==='WIN'&&finite(r.lifecycle.maeR)&&r.lifecycle.maeR<0.5],
    ['high_adverse_winner', r=>r.lifecycle.outcome==='WIN'&&finite(r.lifecycle.maeR)&&r.lifecycle.maeR>=0.5]
  ];
  for (const [name, fn] of classes) out.pathClasses[name] = { all: stats(rows.filter(fn)), dev: stats(s.dev.filter(fn)), validation: stats(s.validation.filter(fn)), holdout: stats(s.holdout.filter(fn)) };
  await mkdir(OUT,{recursive:true}); const path=resolve(OUT,`${tf}.json`); await writeFile(path,JSON.stringify(out,null,2));
  console.log(`${tf}: trades=${rows.length} winners=${rows.filter(r=>r.lifecycle.outcome==='WIN').length} losers=${rows.filter(r=>r.lifecycle.outcome==='LOSS').length} lifecycle=${rows.filter(r=>finite(r.lifecycle.exitBars)&&finite(r.lifecycle.maeR)&&finite(r.lifecycle.mfeR)).length}`);
  console.log(`Report -> ${path}`);
}
for (const tf of ['1min','5min']) await run(tf);
