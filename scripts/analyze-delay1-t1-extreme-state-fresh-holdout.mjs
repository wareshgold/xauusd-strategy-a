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
const OUT = resolve(ROOT, 'data/reports/strategy-a-t1-extreme-state-fresh-holdout');
const PRE = 10000;
const DEV = 6000;
const FRESH = 5000;
const BINS = [3, 4, 5];
const PERMUTATIONS = 499;
const SEED = 20260905;
const BO_LOOKBACK = 5;
const CONTEXT = {
  emaPeriod: 60,
  roundStep: 50,
  roundDistance: 5,
  tradingSessions: [
    { name: 'LONDON', startMinutes: 420, endMinutes: 960 },
    { name: 'NEW_YORK', startMinutes: 780, endMinutes: 1320 },
  ],
  avoidWindows: [],
};
const finite = Number.isFinite;
const mean = a => a.length ? a.reduce((x, y) => x + y, 0) / a.length : null;
const median = a => { const v = [...a].sort((x, y) => x - y); return v.length ? v[Math.floor(v.length / 2)] : null; };
const key = c => `${c.entryIndex}|${c.direction}|${Number(c.entry).toPrecision(15)}|${Number(c.stopLoss).toPrecision(15)}|${Number(c.tp1).toPrecision(15)}`;
function edges(a, b) { a = a.filter(finite).sort((x, y) => x - y); if (!a.length) return []; return [...new Set(Array.from({ length: b - 1 }, (_, i) => { const p = (a.length - 1) * (i + 1) / b, l = Math.floor(p), h = Math.ceil(p); return a[l] + (a[h] - a[l]) * (p - l); }).filter(finite))]; }
const bin = (v, e) => finite(v) ? e.reduce((k, x) => k + (v > x ? 1 : 0), 0) : null;
function candidate(candles, index) {
  const v = candles.slice(0, index + 1);
  if (v.length < CONTEXT.emaPeriod) return null;
  const bo = detectBreakout(v, BO_LOOKBACK);
  const ft = detectFollowThrough(v, bo, { maxBarsAfterBreakout: 2, requireCloseBeyondBrokenLevel: true });
  const sp = detectSpikeCandidates(v, bo, ft, { maxCandles: 8, minDirectionalFraction: .5, maxOverlapFraction: .8 });
  for (const spike of sp.candidates) {
    if (spike.endIndex >= index) continue;
    const cor = detectFirstCorrection(v, spike);
    if (!cor || cor.correctionExtremeIndex >= index || index - cor.correctionExtremeIndex !== 1) continue;
    const tr = detectEntryTrigger(v, cor);
    if (!tr || tr.index !== index) continue;
    const pr = projectLeg2(v, cor);
    if (!pr) continue;
    const inv = getInvalidationRule(cor);
    const ema = buildEMAContext(v.map(c => c.close), CONTEXT);
    if (!ema) continue;
    const loc = buildLocationContext(tr.entryPrice, CONTEXT);
    const ses = buildSessionContext(tr.timestamp, CONTEXT);
    if (!scoreSetup(spike, { ema, location: loc, session: ses }).tradeAllowed) continue;
    const risk = Math.abs(tr.entryPrice - inv.invalidationLevel);
    if (!(risk > 0 && (tr.direction === 'BUY' ? pr.tp1 > tr.entryPrice : pr.tp1 < tr.entryPrice))) continue;
    return { entryIndex: index, entryTime: tr.timestamp, direction: tr.direction, entry: tr.entryPrice, stopLoss: inv.invalidationLevel, tp1: pr.tp1, risk };
  }
  return null;
}
function path(candles, c) {
  let mae = 0, t1Mae = null;
  for (let j = c.entryIndex + 1; j <= Math.min(c.entryIndex + 20, candles.length - 1); j++) {
    const x = candles[j];
    const adv = (c.direction === 'BUY' ? c.entry - x.low : x.high - c.entry) / c.risk;
    if (j === c.entryIndex + 1) t1Mae = Math.max(0, adv);
    mae = Math.max(mae, adv, 0);
  }
  return { t1Mae, mae20: mae };
}
function stats(set) {
  const ys = set.map(r => r.y).filter(finite);
  const wins = ys.filter(x => x > 0), losses = ys.filter(x => x < 0);
  const grossWin = wins.reduce((a, x) => a + x, 0), grossLoss = Math.abs(losses.reduce((a, x) => a + x, 0));
  return { n: ys.length, meanR: mean(ys), medianR: median(ys), winRate: ys.length ? wins.length / ys.length : null, profitFactor: grossLoss > 0 ? grossWin / grossLoss : null, meanMAE20: mean(set.map(r => r.MAE20)) };
}
function rng(seed) { let s = seed >>> 0; return () => { s = (1664525 * s + 1013904223) >>> 0; return s / 4294967296; }; }
function permutationP(set, extreme) {
  const a = set.filter(extreme), b = set.filter(r => !extreme);
  if (a.length < 2 || b.length < 2) return null;
  const observed = mean(a.map(r => r.y)) - mean(b.map(r => r.y));
  const values = set.map(r => r.y), labels = set.map(extreme), random = rng(SEED);
  let ge = 0;
  for (let k = 0; k < PERMUTATIONS; k++) {
    const shuffled = [...values];
    for (let i = shuffled.length - 1; i > 0; i--) { const j = Math.floor(random() * (i + 1)); [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]]; }
    const x = [], c = [];
    for (let i = 0; i < shuffled.length; i++) (labels[i] ? x : c).push(shuffled[i]);
    if (Math.abs(mean(x) - mean(c)) >= Math.abs(observed)) ge++;
  }
  return { observedDifferenceR: observed, p: (ge + 1) / (PERMUTATIONS + 1) };
}
function bootstrapCI(set, extreme) {
  const a = set.filter(extreme), b = set.filter(r => !extreme);
  if (a.length < 2 || b.length < 2) return null;
  const random = rng(SEED + 17), diffs = [];
  for (let k = 0; k < 1000; k++) {
    const sa = Array.from({ length: a.length }, () => a[Math.floor(random() * a.length)]);
    const sb = Array.from({ length: b.length }, () => b[Math.floor(random() * b.length)]);
    diffs.push(mean(sa.map(r => r.y)) - mean(sb.map(r => r.y)));
  }
  diffs.sort((x, y) => x - y);
  return { low95: diffs[Math.floor(diffs.length * .025)], high95: diffs[Math.floor(diffs.length * .975)] };
}
async function rows(tf) {
  const raw = JSON.parse(await readFile(resolve(ROOT, `data/historical/xauusd-${tf}.json`), 'utf8'));
  const candles = raw.candles ?? raw;
  if (candles.length < PRE + FRESH) throw new Error(`${tf}: expected at least ${PRE + FRESH} candles, found ${candles.length}`);
  const base = JSON.parse(await readFile(resolve(BASE, `${tf}.json`), 'utf8')).trades ?? [];
  const map = new Map(base.filter(t => t.result !== 'AMBIGUOUS' && finite(Number(t.rMultiple))).map(t => [key(t), t]));
  const out = [];
  for (let i = 0; i < candles.length; i++) {
    const c = candidate(candles, i);
    if (!c) continue;
    const t = map.get(key(c));
    if (!t) continue;
    const p = path(candles, c);
    if (finite(p.t1Mae)) out.push({ entryIndex: i, y: Number(t.rMultiple), T1_MAE: p.t1Mae, MAE20: p.mae20 });
  }
  return out;
}
async function run(tf) {
  const all = await rows(tf);
  const dev = all.filter(r => r.entryIndex < DEV);
  const val = all.filter(r => r.entryIndex >= DEV && r.entryIndex < PRE);
  const fresh = all.filter(r => r.entryIndex >= PRE && r.entryIndex < PRE + FRESH);
  const report = { strategy: 'Strategy A', mode: 'DELAY1_T1_EXTREME_STATE_FRESH_HOLDOUT', timeframe: tf, scope: { totalCandles: PRE + FRESH, devCandles: DEV, valCandles: PRE - DEV, freshHoldoutCandles: FRESH, delayExactly: 1 }, methodology: { hypothesis: 'The highest T1_MAE quantile is economically worse than all lower T1_MAE states.', edgesFitOn: 'DEV only', edgesFrozenFor: ['VAL', 'FRESH_HOLDOUT'], bins: BINS, permutations: PERMUTATIONS, seed: SEED, bootstrapReplicates: 1000, noThresholdOptimization: true, noHoldoutOptimization: true, diagnosticOnly: true, productionUntouched: true } };
  for (const b of BINS) {
    const e = edges(dev.map(r => r.T1_MAE), b), extreme = r => bin(r.T1_MAE, e) === b - 1;
    report[b] = { edges: e, dev: { extreme: stats(dev.filter(extreme)), control: stats(dev.filter(r => !extreme(r))), test: permutationP(dev, extreme), bootstrapCI: bootstrapCI(dev, extreme) }, val: { extreme: stats(val.filter(extreme)), control: stats(val.filter(r => !extreme(r))), test: permutationP(val, extreme), bootstrapCI: bootstrapCI(val, extreme) }, freshHoldout: { extreme: stats(fresh.filter(extreme)), control: stats(fresh.filter(r => !extreme(r))), test: permutationP(fresh, extreme), bootstrapCI: bootstrapCI(fresh, extreme) } };
  }
  await mkdir(OUT, { recursive: true });
  await writeFile(resolve(OUT, `${tf}.json`), JSON.stringify({ ...report, counts: { all: all.length, dev: dev.length, val: val.length, freshHoldout: fresh.length } }, null, 2));
  console.log(`\n${tf}: n=${all.length} DEV=${dev.length} VAL=${val.length} FRESH=${fresh.length}`);
  for (const b of BINS) { const x = report[b]; console.log(`bins=${b} DEV diff=${x.dev.test?.observedDifferenceR?.toFixed(4)} p=${x.dev.test?.p?.toFixed(4)} | VAL diff=${x.val.test?.observedDifferenceR?.toFixed(4)} p=${x.val.test?.p?.toFixed(4)} | FRESH extreme=${x.freshHoldout.extreme.meanR?.toFixed(4)} control=${x.freshHoldout.control.meanR?.toFixed(4)} diff=${x.freshHoldout.test?.observedDifferenceR?.toFixed(4)} p=${x.freshHoldout.test?.p?.toFixed(4)} CI=[${x.freshHoldout.bootstrapCI?.low95?.toFixed(4)},${x.freshHoldout.bootstrapCI?.high95?.toFixed(4)}]`); }
}
for (const tf of ['1min', '5min']) await run(tf);
