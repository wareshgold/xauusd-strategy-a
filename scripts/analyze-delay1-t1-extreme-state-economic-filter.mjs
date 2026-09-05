import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { detectBreakout } from '../src/domain/market/BreakoutDetector.js';
import { detectFollowThrough } from '../src/domain/market/FollowThroughDetector.js';
import { detectSpikeCandidates } from '../src/domain/strategy-a/SpikeDetector.js';
import { detectFirstCorrection } from '../src/domain/strategy-a/CorrectionDetector.js';
import { detectEntryTrigger } from '../src/domain/strategy-a/EntryTrigger.js';
import { getInvalidationRule } from '../src/domain/strategy-a/Invalidation.js';
import { projectLeg2 } from '../src/domain/strategy-a/LegProjection.js';
import { buildEMAContext, buildLocationContext, buildSessionContext } from '../src/domain/strategy-a/Context.js';
import { scoreSetup } from '../src/domain/strategy-a/QualityScore.js';

const ROOT = resolve(process.cwd());
const BASE = resolve(ROOT, 'data/reports/strategy-a-baseline');
const OUT = resolve(ROOT, 'data/reports/strategy-a-t1-extreme-state-economic-filter');
const PRE = 10000;
const DEV = 6000;
const FRESH = 5000;
const BINS = [3, 4, 5];
const BO_LOOKBACK = 5;
const CTX = { emaPeriod: 60, roundStep: 50, roundDistance: 5, tradingSessions: [{ name: 'LONDON', startMinutes: 420, endMinutes: 960 }, { name: 'NEW_YORK', startMinutes: 780, endMinutes: 1320 }], avoidWindows: [] };
const finite = Number.isFinite;
const mean = a => a.length ? a.reduce((x, y) => x + y, 0) / a.length : null;
const median = a => { const v = [...a].sort((x, y) => x - y); return v.length ? v[Math.floor(v.length / 2)] : null; };
function edges(a, b) { a = a.filter(finite).sort((x, y) => x - y); if (!a.length) return []; return [...new Set(Array.from({ length: b - 1 }, (_, i) => { const p = (a.length - 1) * (i + 1) / b, l = Math.floor(p), h = Math.ceil(p); return a[l] + (a[h] - a[l]) * (p - l); }).filter(finite))]; }
const bin = (v, e) => finite(v) ? e.reduce((k, x) => k + (v > x ? 1 : 0), 0) : null;
function candidate(candles, index) { const v = candles.slice(0, index + 1); if (v.length < 60) return null; const bo = detectBreakout(v, BO_LOOKBACK), ft = detectFollowThrough(v, bo, { maxBarsAfterBreakout: 2, requireCloseBeyondBrokenLevel: true }), sp = detectSpikeCandidates(v, bo, ft, { maxCandles: 8, minDirectionalFraction: .5, maxOverlapFraction: .8 }); for (const spike of sp.candidates) { if (spike.endIndex >= index) continue; const cor = detectFirstCorrection(v, spike); if (!cor || cor.correctionExtremeIndex >= index || index - cor.correctionExtremeIndex !== 1) continue; const tr = detectEntryTrigger(v, cor); if (!tr || tr.index !== index) continue; const pr = projectLeg2(v, cor); if (!pr) continue; const inv = getInvalidationRule(cor), ema = buildEMAContext(v.map(c => c.close), CTX), loc = buildLocationContext(tr.entryPrice, CTX), ses = buildSessionContext(tr.timestamp, CTX); if (!ema || !scoreSetup(spike, { ema, location: loc, session: ses }).tradeAllowed) continue; const risk = Math.abs(tr.entryPrice - inv.invalidationLevel); if (!(risk > 0 && (tr.direction === 'BUY' ? pr.tp1 > tr.entryPrice : pr.tp1 < tr.entryPrice))) continue; return { entryIndex: index, direction: tr.direction, entry: tr.entryPrice, stopLoss: inv.invalidationLevel, tp1: pr.tp1, risk }; } return null; }
function t1Mae(c) { const j = c.entryIndex + 1; if (j >= c.candles.length) return null; const x = c.candles[j]; const adv = (c.direction === 'BUY' ? c.entry - x.low : x.high - c.entry) / c.risk; return Math.max(0, adv); }
function key(c) { return `${c.entryIndex}|${c.direction}|${Number(c.entry).toPrecision(15)}|${Number(c.stopLoss).toPrecision(15)}|${Number(c.tp1).toPrecision(15)}`; }
function seriesStats(rows) {
  const ys = rows.map(r => r.y).filter(finite);
  const wins = ys.filter(x => x > 0), losses = ys.filter(x => x < 0);
  const grossWin = wins.reduce((a, x) => a + x, 0), grossLoss = Math.abs(losses.reduce((a, x) => a + x, 0));
  let equity = 0, peak = 0, maxDrawdown = 0, currentLosses = 0, maxConsecutiveLosses = 0;
  for (const y of ys) {
    equity += y;
    peak = Math.max(peak, equity);
    maxDrawdown = Math.max(maxDrawdown, peak - equity);
    if (y < 0) { currentLosses++; maxConsecutiveLosses = Math.max(maxConsecutiveLosses, currentLosses); } else if (y > 0) currentLosses = 0;
  }
  return {
    n: ys.length,
    totalR: ys.reduce((a, x) => a + x, 0),
    meanR: mean(ys),
    medianR: median(ys),
    winRate: ys.length ? wins.length / ys.length : null,
    profitFactor: grossLoss > 0 ? grossWin / grossLoss : null,
    maxDrawdownR: maxDrawdown,
    maxConsecutiveLosses,
  };
}
function deltaMetric(base, filtered, field) { return finite(base[field]) && finite(filtered[field]) ? filtered[field] - base[field] : null; }
async function rows(tf) {
  const raw = JSON.parse(await readFile(resolve(ROOT, `data/historical/xauusd-${tf}.json`), 'utf8')), candles = raw.candles ?? raw;
  if (candles.length < PRE + FRESH) throw new Error(`${tf}: expected at least ${PRE + FRESH} candles, found ${candles.length}`);
  const base = JSON.parse(await readFile(resolve(BASE, `${tf}.json`), 'utf8')).trades ?? [];
  const map = new Map(base.filter(t => t.result !== 'AMBIGUOUS' && finite(Number(t.rMultiple))).map(t => [key(t), t]));
  const out = [];
  for (let i = 0; i < candles.length; i++) {
    const c = candidate(candles, i); if (!c) continue;
    const t = map.get(key(c)); if (!t) continue;
    const mae = t1Mae({ ...c, candles });
    if (finite(mae)) out.push({ entryIndex: i, y: Number(t.rMultiple), T1_MAE: mae });
  }
  return out;
}
function evaluate(set, edgesForBins, b) {
  const extreme = r => bin(r.T1_MAE, edgesForBins) === b - 1;
  const base = seriesStats(set);
  const kept = set.filter(r => !extreme(r));
  const filtered = seriesStats(kept);
  return {
    baseline: base,
    filtered,
    removed: { n: set.length - kept.length, pct: set.length ? (set.length - kept.length) / set.length : null },
    improvement: {
      totalR: deltaMetric(base, filtered, 'totalR'),
      meanR: deltaMetric(base, filtered, 'meanR'),
      medianR: deltaMetric(base, filtered, 'medianR'),
      winRate: deltaMetric(base, filtered, 'winRate'),
      profitFactor: deltaMetric(base, filtered, 'profitFactor'),
      maxDrawdownR: deltaMetric(base, filtered, 'maxDrawdownR'),
      maxConsecutiveLosses: deltaMetric(base, filtered, 'maxConsecutiveLosses'),
    },
  };
}
function fmt(v) { return finite(v) ? v.toFixed(4) : 'NA'; }
function compact(x) { return `N ${x.n} | totalR ${fmt(x.totalR)} | meanR ${fmt(x.meanR)} | win ${fmt(x.winRate * 100)}% | PF ${fmt(x.profitFactor)} | DD ${fmt(x.maxDrawdownR)}R | maxCL ${x.maxConsecutiveLosses}`; }
async function run(tf) {
  const all = await rows(tf);
  const dev = all.filter(r => r.entryIndex < DEV);
  const val = all.filter(r => r.entryIndex >= DEV && r.entryIndex < PRE);
  const fresh = all.filter(r => r.entryIndex >= PRE && r.entryIndex < PRE + FRESH);
  const report = {
    strategy: 'Strategy A',
    mode: 'DELAY1_T1_EXTREME_STATE_ECONOMIC_FILTER',
    timeframe: tf,
    scope: { totalCandles: PRE + FRESH, devCandles: DEV, valCandles: PRE - DEV, freshHoldoutCandles: FRESH, delayExactly: 1 },
    methodology: {
      hypothesis: 'Excluding the pre-specified highest T1_MAE quantile improves DELAY1 economic performance.',
      edgesFitOn: 'DEV only',
      edgesFrozenFor: ['VAL', 'FRESH_HOLDOUT'],
      bins: BINS,
      thresholdOptimization: false,
      holdoutOptimization: false,
      diagnosticOnly: true,
      productionUntouched: true,
      baselineDefinition: 'Canonical Strategy A DELAY1 trades reconstructed and joined by exact entry/direction/entry/stop/tp1 key.',
      drawdownDefinition: 'Peak-to-trough cumulative R drawdown over chronological trades within each split.',
    },
  };
  console.log(`\n${tf}: n=${all.length} DEV=${dev.length} VAL=${val.length} FRESH=${fresh.length}`);
  for (const b of BINS) {
    const e = edges(dev.map(r => r.T1_MAE), b);
    report[b] = { edges: e, dev: evaluate(dev, e, b), val: evaluate(val, e, b), freshHoldout: evaluate(fresh, e, b) };
    const x = report[b];
    console.log(`bins=${b}`);
    console.log(`  DEV baseline:  ${compact(x.dev.baseline)}`);
    console.log(`  DEV filtered:  ${compact(x.dev.filtered)} | removed=${x.dev.removed.n} (${fmt(x.dev.removed.pct * 100)}%)`);
    console.log(`  VAL baseline:  ${compact(x.val.baseline)}`);
    console.log(`  VAL filtered:  ${compact(x.val.filtered)} | removed=${x.val.removed.n} (${fmt(x.val.removed.pct * 100)}%)`);
    console.log(`  FRESH baseline:${compact(x.freshHoldout.baseline)}`);
    console.log(`  FRESH filtered:${compact(x.freshHoldout.filtered)} | removed=${x.freshHoldout.removed.n} (${fmt(x.freshHoldout.removed.pct * 100)}%)`);
  }
  await mkdir(OUT, { recursive: true });
  await writeFile(resolve(OUT, `${tf}.json`), JSON.stringify({ ...report, counts: { all: all.length, dev: dev.length, val: val.length, freshHoldout: fresh.length } }, null, 2));
}
for (const tf of ['1min', '5min']) await run(tf);
